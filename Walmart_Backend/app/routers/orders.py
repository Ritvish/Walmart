from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ClubbedOrderDetailResponse, DeliveryResponse
from app.crud import get_user_orders
from app.auth import get_current_user
from app.models import ClubbedOrder, ClubbedOrderUser, Delivery

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.get("/", response_model=List[ClubbedOrderDetailResponse])
def get_my_orders(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's order history"""
    user_orders = get_user_orders(db, current_user.id)
    return [order.clubbed_order for order in user_orders]

@router.get("/{order_id}", response_model=ClubbedOrderDetailResponse)
def get_order_details(
    order_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific order"""
    
    # Check if user is part of this order
    user_order = db.query(ClubbedOrderUser).filter(
        ClubbedOrderUser.clubbed_order_id == order_id,
        ClubbedOrderUser.user_id == current_user.id
    ).first()
    
    if not user_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    order = db.query(ClubbedOrder).filter(ClubbedOrder.id == order_id).first()
    return order

@router.get("/{order_id}/delivery", response_model=DeliveryResponse)
def get_delivery_status(
    order_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get delivery status for an order"""
    
    # Check if user is part of this order
    user_order = db.query(ClubbedOrderUser).filter(
        ClubbedOrderUser.clubbed_order_id == order_id,
        ClubbedOrderUser.user_id == current_user.id
    ).first()
    
    if not user_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    delivery = db.query(Delivery).filter(Delivery.clubbed_order_id == order_id).first()
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    
    return delivery
