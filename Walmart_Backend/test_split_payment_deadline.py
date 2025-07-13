#!/usr/bin/env python3
"""
Test script for split payment deadline functionality
"""
import sys
import os
sys.path.append(os.getcwd())

from app.database import get_db
from app.crud import (
    create_user_orders_for_clubbed_order,
    get_split_payment_summary
)
from app.models import ClubbedOrder, ClubbedOrderUser, User, Cart, CartItem
from datetime import datetime, timedelta

def test_split_payment_deadline():
    print("🧪 Testing Split Payment Deadline")
    print("=" * 50)
    
    db = next(get_db())
    
    # Find or create a test clubbed order
    clubbed_order = db.query(ClubbedOrder).first()
    
    if not clubbed_order:
        print("❌ No clubbed order found in database")
        return
    
    print(f"📋 Using clubbed order: {clubbed_order.id}")
    print(f"📋 Status: {clubbed_order.status}")
    
    # Check if user orders already exist
    from app.models import UserOrder
    existing_user_orders = db.query(UserOrder).filter(
        UserOrder.clubbed_order_id == clubbed_order.id
    ).all()
    
    print(f"📋 Existing user orders: {len(existing_user_orders)}")
    
    if not existing_user_orders:
        print("🔄 Creating user orders...")
        user_orders = create_user_orders_for_clubbed_order(db, clubbed_order.id)
        print(f"✅ Created {len(user_orders)} user orders")
        
        for order in user_orders:
            print(f"   - User {order.user_id}: deadline {order.commitment_deadline}")
            current_time = datetime.utcnow()
            time_diff = (order.commitment_deadline - current_time).total_seconds()
            print(f"     Time remaining: {time_diff} seconds ({time_diff/60:.1f} minutes)")
    else:
        print("📋 User orders already exist:")
        for order in existing_user_orders:
            print(f"   - User {order.user_id}: deadline {order.commitment_deadline}")
            current_time = datetime.utcnow()
            time_diff = (order.commitment_deadline - current_time).total_seconds()
            print(f"     Time remaining: {time_diff} seconds ({time_diff/60:.1f} minutes)")
            print(f"     Is committed: {order.is_committed}")
            print(f"     Payment status: {order.payment_status}")
    
    # Test the payment summary for each user
    club_users = db.query(ClubbedOrderUser).filter(
        ClubbedOrderUser.clubbed_order_id == clubbed_order.id
    ).all()
    
    for club_user in club_users:
        print(f"\n💰 Testing payment summary for user {club_user.user_id}")
        summary = get_split_payment_summary(db, clubbed_order.id, club_user.user_id)
        
        if summary:
            print(f"   ✅ Summary found:")
            print(f"     - Your portion: ₹{summary['your_portion']}")
            print(f"     - Payment deadline: {summary['payment_deadline']}")
            
            current_time = datetime.utcnow()
            if isinstance(summary['payment_deadline'], str):
                # Parse the ISO string with Z suffix
                deadline_str = summary['payment_deadline']
                if deadline_str.endswith('Z'):
                    deadline_str = deadline_str[:-1] + '+00:00'  # Replace Z with +00:00
                from datetime import timezone
                deadline = datetime.fromisoformat(deadline_str).replace(tzinfo=None)
            else:
                deadline = summary['payment_deadline']
            
            time_diff = (deadline - current_time).total_seconds()
            print(f"     - Time remaining: {time_diff} seconds ({time_diff/60:.1f} minutes)")
            print(f"     - Is deadline passed: {time_diff <= 0}")
        else:
            print(f"   ❌ No payment summary found")

if __name__ == "__main__":
    test_split_payment_deadline()
