from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.schemas import (
    ClubReadinessResponse, BuddyQueueCreate, BuddyQueueResponse,
    ClubbedOrderDetailResponse, LocationUpdate
)
from app.crud import (
    check_club_readiness, join_buddy_queue, find_compatible_buddies,
    create_clubbed_order, assign_driver_to_order, timeout_expired_buddies
)
from app.auth import get_current_user
from app.models import BuddyQueue, ClubbedOrderUser
from app.enums import BuddyStatus

router = APIRouter(prefix="/club", tags=["Club & Save"])

@router.post("/check-readiness", response_model=ClubReadinessResponse)
def check_readiness(
    location: LocationUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user can club orders in their location"""
    return check_club_readiness(db, current_user.id, float(location.lat), float(location.lng))

@router.post("/join-queue", response_model=BuddyQueueResponse)
def join_queue(
    buddy_data: BuddyQueueCreate,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Join the buddy queue for order clubbing"""
    buddy_entry = join_buddy_queue(db, current_user.id, buddy_data)
    
    # Schedule background task to handle matching
    background_tasks.add_task(process_buddy_matching, buddy_entry.id)
    
    return buddy_entry

@router.get("/status/{buddy_queue_id}")
def get_club_status(
    buddy_queue_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the status of user's club request"""
    buddy = db.query(BuddyQueue).filter(BuddyQueue.id == buddy_queue_id).first()
    if not buddy:
        raise HTTPException(status_code=404, detail="Buddy queue entry not found")
    
    if buddy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if entry has timed out and update status if needed
    if buddy.status == BuddyStatus.WAITING.value:
        from datetime import datetime, timedelta
        timeout_threshold = buddy.created_at + timedelta(minutes=buddy.timeout_minutes)
        if datetime.utcnow() > timeout_threshold:
            buddy.status = BuddyStatus.TIMED_OUT.value
            db.commit()
    
    if buddy.status == BuddyStatus.MATCHED.value:
        # Find the clubbed order
        clubbed_user = db.query(ClubbedOrderUser).filter(
            ClubbedOrderUser.user_id == current_user.id,
            ClubbedOrderUser.cart_id == buddy.cart_id
        ).first()
        
        if clubbed_user:
            return {
                "status": "matched",
                "clubbed_order_id": clubbed_user.clubbed_order_id,
                "discount_given": clubbed_user.discount_given
            }
    
    return {
        "status": buddy.status.value,
        "created_at": buddy.created_at
    }

@router.get("/detailed-status/{buddy_queue_id}")
def get_detailed_club_status(
    buddy_queue_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed status of user's club request with nearby users and match potential"""
    from app.models import BuddyQueue, ClubbedOrderUser
    from app.enums import BuddyStatus
    from sqlalchemy import and_, func
    from datetime import datetime, timedelta
    import os
    
    buddy = db.query(BuddyQueue).filter(BuddyQueue.id == buddy_queue_id).first()
    if not buddy:
        raise HTTPException(status_code=404, detail="Buddy queue entry not found")
    
    if buddy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if entry has timed out and update status if needed
    if buddy.status == BuddyStatus.WAITING.value:
        timeout_threshold = buddy.created_at + timedelta(minutes=buddy.timeout_minutes)
        if datetime.utcnow() > timeout_threshold:
            buddy.status = BuddyStatus.TIMED_OUT.value
            db.commit()
    
    # Base response
    response = {
        "status": buddy.status.value,
        "created_at": buddy.created_at.isoformat() if buddy.created_at else None
    }
    
    if buddy.status == BuddyStatus.WAITING.value:
        # Count nearby users within 5km radius
        RADIUS_KM = 5.0
        nearby_users = db.query(BuddyQueue).filter(
            and_(
                BuddyQueue.status == BuddyStatus.WAITING.value,
                BuddyQueue.id != buddy_queue_id,
                func.sqrt(
                    func.pow(BuddyQueue.lat - buddy.lat, 2) + 
                    func.pow(BuddyQueue.lng - buddy.lng, 2)
                ) * 111 <= RADIUS_KM
            )
        ).count()
        
        # Find potential compatible matches
        compatible_buddies = find_compatible_buddies(db, buddy_queue_id)
        potential_matches = len(compatible_buddies) - 1 if len(compatible_buddies) > 0 else 0
        
        # Estimate match time based on the buddy's individual timeout
        elapsed_minutes = (datetime.utcnow() - buddy.created_at).total_seconds() / 60
        remaining_minutes = max(0, buddy.timeout_minutes - elapsed_minutes)
        
        # Adjust estimate based on nearby activity
        if nearby_users > 2:
            estimated_match_time = max(30, remaining_minutes * 60 * 0.7)  # Faster with more users
        elif nearby_users > 0:
            estimated_match_time = remaining_minutes * 60
        else:
            estimated_match_time = remaining_minutes * 60 * 1.5  # Slower with no users
        
        response.update({
            "nearby_users": nearby_users,
            "estimated_match_time": int(estimated_match_time) if estimated_match_time > 0 else None,
            "potential_matches": potential_matches
        })
        
    elif buddy.status == BuddyStatus.MATCHED.value:
        # Find clubbed order details
        clubbed_user = db.query(ClubbedOrderUser).filter(
            ClubbedOrderUser.user_id == current_user.id,
            ClubbedOrderUser.cart_id == buddy.cart_id
        ).first()
        
        if clubbed_user:
            response.update({
                "clubbed_order_id": clubbed_user.clubbed_order_id,
                "discount_given": float(clubbed_user.discount_given) if clubbed_user.discount_given else 0.0
            })
        
        # Still show nearby users for context
        RADIUS_KM = 5.0
        nearby_users = db.query(BuddyQueue).filter(
            and_(
                BuddyQueue.status.in_([BuddyStatus.WAITING.value, BuddyStatus.MATCHED.value]),
                BuddyQueue.id != buddy_queue_id,
                func.sqrt(
                    func.pow(BuddyQueue.lat - buddy.lat, 2) + 
                    func.pow(BuddyQueue.lng - buddy.lng, 2)
                ) * 111 <= RADIUS_KM
            )
        ).count()
        
        response["nearby_users"] = nearby_users
    
    return response

def process_buddy_matching(buddy_queue_id: str):
    """Background task to process buddy matching"""
    db = SessionLocal()
    try:
        # Timeout expired buddies first
        timeout_expired_buddies(db)
        
        # Find compatible buddies for the new user
        compatible_buddies = find_compatible_buddies(db, buddy_queue_id)
        
        if len(compatible_buddies) > 1:
            # Create clubbed order
            clubbed_order = create_clubbed_order(db, compatible_buddies)
            
            if clubbed_order:
                # Try to assign driver, but don't fail if it doesn't work
                try:
                    assign_driver_to_order(db, clubbed_order.id)
                except Exception as e:
                    print(f"Warning: Could not assign driver to order {clubbed_order.id}: {e}")
                    # Continue without driver assignment for now
    finally:
        db.close()

@router.post("/queue-stats")
def get_queue_statistics(
    location: LocationUpdate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get queue statistics for a specific location"""
    from app.models import BuddyQueue
    from app.enums import BuddyStatus
    from sqlalchemy import and_, func
    from datetime import datetime, timedelta
    
    user_lat = float(location.lat)
    user_lng = float(location.lng)
    RADIUS_KM = 5.0
    
    # Count nearby users currently waiting
    nearby_users = db.query(BuddyQueue).filter(
        and_(
            BuddyQueue.status == BuddyStatus.WAITING.value,
            func.sqrt(
                func.pow(BuddyQueue.lat - user_lat, 2) + 
                func.pow(BuddyQueue.lng - user_lng, 2)
            ) * 111 <= RADIUS_KM
        )
    ).count()
    
    # Calculate average wait time from historical data (last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    # Get completed entries (matched or timed out) in the area
    completed_entries = db.query(BuddyQueue).filter(
        and_(
            BuddyQueue.status.in_([BuddyStatus.MATCHED.value, BuddyStatus.TIMED_OUT.value]),
            BuddyQueue.created_at >= seven_days_ago,
            func.sqrt(
                func.pow(BuddyQueue.lat - user_lat, 2) + 
                func.pow(BuddyQueue.lng - user_lng, 2)
            ) * 111 <= RADIUS_KM
        )
    ).all()
    
    # Calculate metrics
    if completed_entries:
        # Assume average completion time (this could be improved with actual completion timestamps)
        avg_wait_time = 180  # Default 3 minutes for matches
        
        # Calculate success rate
        matched_count = len([e for e in completed_entries if e.status == BuddyStatus.MATCHED.value])
        success_rate = (matched_count / len(completed_entries)) * 100
    else:
        # Default values when no historical data
        avg_wait_time = 240  # 4 minutes default
        success_rate = 75  # 75% default success rate
    
    # Determine peak hours based on historical activity
    peak_hours = []
    if completed_entries:
        # Count entries by hour
        hour_counts = {}
        for entry in completed_entries:
            hour = entry.created_at.hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Find peak hours (hours with above average activity)
        if hour_counts:
            avg_activity = sum(hour_counts.values()) / len(hour_counts)
            peak_hour_numbers = [hour for hour, count in hour_counts.items() if count > avg_activity]
            
            # Convert to time ranges
            peak_hours = []
            for hour in sorted(peak_hour_numbers):
                if hour == 12:
                    peak_hours.append("12:00-14:00")  # Lunch time
                elif hour >= 18 and hour <= 20:
                    peak_hours.append("18:00-20:00")  # Dinner time
                elif hour >= 8 and hour <= 10:
                    peak_hours.append("08:00-10:00")  # Morning
    
    # Default peak hours if no data
    if not peak_hours:
        peak_hours = ["12:00-14:00", "18:00-20:00"]
    
    return {
        "nearby_users": nearby_users,
        "avg_wait_time": avg_wait_time,
        "success_rate": round(success_rate, 1),
        "peak_hours": peak_hours[:2]  # Limit to top 2 peak times
    }

@router.post("/leave-queue/{buddy_queue_id}")
def leave_queue(
    buddy_queue_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Leave the buddy queue"""
    buddy = db.query(BuddyQueue).filter(BuddyQueue.id == buddy_queue_id).first()
    if not buddy:
        raise HTTPException(status_code=404, detail="Buddy queue entry not found")
    
    if buddy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Remove from queue
    db.delete(buddy)
    db.commit()
    
    return {"success": True, "message": "Left buddy queue successfully"}

@router.post("/extend-timeout/{buddy_queue_id}")
def extend_timeout(
    buddy_queue_id: str,
    additional_minutes: int,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Extend the timeout for a buddy queue entry"""
    buddy = db.query(BuddyQueue).filter(BuddyQueue.id == buddy_queue_id).first()
    if not buddy:
        raise HTTPException(status_code=404, detail="Buddy queue entry not found")
    
    if buddy.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    if buddy.status != BuddyStatus.WAITING.value:
        raise HTTPException(status_code=400, detail="Cannot extend timeout for non-waiting entry")
    
    # Extend the timeout
    buddy.timeout_minutes += additional_minutes
    db.commit()
    
    return {
        "success": True, 
        "message": f"Timeout extended by {additional_minutes} minutes",
        "new_timeout_minutes": buddy.timeout_minutes
    }
