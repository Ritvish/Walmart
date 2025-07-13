from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (
    UserOrderCreate, UserOrderResponse, PaymentCommitRequest, 
    PaymentConfirmationRequest, OrderCancellationRequest, OrderCancellationResponse,
    PaymentTransactionResponse, SplitPaymentSummary, OrderCommitmentStatus
)
from app.crud import (
    create_user_orders_for_clubbed_order, commit_to_payment, confirm_payment,
    cancel_user_order, get_split_payment_summary, check_all_commitments,
    check_all_payments_confirmed
)
from app.auth import get_current_user
from app.models import User, UserOrder, PaymentTransaction, OrderCancellation
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/split-payment", tags=["Split Payment"])

@router.post("/create-user-orders/{clubbed_order_id}")
def create_user_orders(
    clubbed_order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create individual user orders for a clubbed order
    This is called when a clubbed order is successfully matched
    """
    try:
        user_orders = create_user_orders_for_clubbed_order(db, clubbed_order_id)
        
        if not user_orders:
            raise HTTPException(status_code=404, detail="Clubbed order not found or no users")
        
        return {
            "success": True,
            "clubbed_order_id": clubbed_order_id,
            "user_orders_created": len(user_orders),
            "commitment_deadline": user_orders[0].commitment_deadline.isoformat() + 'Z',
            "message": "Individual user orders created. Users have 10 minutes to commit."
        }
        
    except Exception as e:
        logger.error(f"Failed to create user orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create user orders")

@router.post("/commit")
def commit_payment(
    request: PaymentCommitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    User commits to payment and provides delivery details
    """
    try:
        # Verify that the user order belongs to the current user
        user_order = db.query(UserOrder).filter(
            UserOrder.id == request.user_order_id,
            UserOrder.user_id == current_user.id
        ).first()
        
        if not user_order:
            raise HTTPException(status_code=404, detail="User order not found")
        
        success = commit_to_payment(
            db,
            request.user_order_id,
            request.payment_method,
            request.delivery_address,
            request.delivery_phone,
            request.special_instructions
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to commit to payment or deadline passed")
        
        # Check if all users have committed
        all_committed = check_all_commitments(db, user_order.clubbed_order_id)
        
        return {
            "success": True,
            "message": "Payment commitment successful",
            "all_users_committed": all_committed,
            "next_step": "Wait for all users to commit, then proceed with payment" if not all_committed else "All users committed. Proceed with payment confirmation."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to commit payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to commit to payment")

@router.post("/confirm")
def confirm_payment_endpoint(
    request: PaymentConfirmationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Confirm payment for a user order
    """
    try:
        # Verify that the user order belongs to the current user
        user_order = db.query(UserOrder).filter(
            UserOrder.id == request.user_order_id,
            UserOrder.user_id == current_user.id
        ).first()
        
        if not user_order:
            raise HTTPException(status_code=404, detail="User order not found")
        
        if not user_order.is_committed:
            raise HTTPException(status_code=400, detail="Must commit to payment first")
        
        success = confirm_payment(
            db,
            request.user_order_id,
            request.external_transaction_id,
            request.payment_gateway
        )
        
        if not success:
            raise HTTPException(status_code=400, detail="Failed to confirm payment")
        
        # Check if all payments are confirmed
        all_confirmed = check_all_payments_confirmed(db, user_order.clubbed_order_id)
        
        return {
            "success": True,
            "message": "Payment confirmed successfully",
            "all_payments_confirmed": all_confirmed,
            "next_step": "Waiting for other users' payments" if not all_confirmed else "All payments confirmed! Order is being prepared."
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to confirm payment: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to confirm payment")

@router.post("/cancel", response_model=OrderCancellationResponse)
def cancel_order(
    request: OrderCancellationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Cancel a user order and apply penalties/compensation
    """
    try:
        # Verify that the user order belongs to the current user
        user_order = db.query(UserOrder).filter(
            UserOrder.id == request.user_order_id,
            UserOrder.user_id == current_user.id
        ).first()
        
        if not user_order:
            raise HTTPException(status_code=404, detail="User order not found")
        
        if user_order.payment_status == 'CANCELLED':
            raise HTTPException(status_code=400, detail="Order already cancelled")
        
        cancellation = cancel_user_order(
            db,
            request.user_order_id,
            current_user.id,
            request.cancellation_reason
        )
        
        if not cancellation:
            raise HTTPException(status_code=400, detail="Failed to cancel order")
        
        return OrderCancellationResponse(
            id=cancellation.id,
            user_order_id=cancellation.user_order_id,
            clubbed_order_id=cancellation.clubbed_order_id,
            cancelled_by_user_id=cancellation.cancelled_by_user_id,
            cancellation_reason=cancellation.cancellation_reason,
            cancellation_fee=float(cancellation.cancellation_fee),
            compensation_amount=float(cancellation.compensation_amount),
            cancelled_at=cancellation.cancelled_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to cancel order")

@router.get("/summary/{clubbed_order_id}", response_model=SplitPaymentSummary)
def get_payment_summary(
    clubbed_order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get payment summary for the current user in a clubbed order
    """
    try:
        summary = get_split_payment_summary(db, clubbed_order_id, current_user.id)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Payment summary not found")
        
        return SplitPaymentSummary(**summary)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get payment summary: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get payment summary")

@router.get("/status/{clubbed_order_id}")
def get_commitment_status(
    clubbed_order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get commitment and payment status for a clubbed order
    """
    try:
        # Get all user orders for this clubbed order
        user_orders = db.query(UserOrder).filter(
            UserOrder.clubbed_order_id == clubbed_order_id
        ).all()
        
        if not user_orders:
            raise HTTPException(status_code=404, detail="Clubbed order not found")
        
        # Check if current user is part of this order
        user_in_order = any(order.user_id == current_user.id for order in user_orders)
        if not user_in_order:
            raise HTTPException(status_code=403, detail="You are not part of this order")
        
        committed_users = [order.user_id for order in user_orders if order.is_committed]
        pending_users = [order.user_id for order in user_orders if not order.is_committed]
        
        all_committed = len(pending_users) == 0
        
        # Check if order is confirmed (all payments confirmed)
        order_confirmed = all(order.payment_status == 'CONFIRMED' for order in user_orders)
        
        return OrderCommitmentStatus(
            clubbed_order_id=clubbed_order_id,
            commitment_deadline=user_orders[0].commitment_deadline,
            committed_users=committed_users,
            pending_users=pending_users,
            all_committed=all_committed,
            order_confirmed=order_confirmed
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get commitment status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get commitment status")

@router.get("/transactions/{user_order_id}")
def get_user_transactions(
    user_order_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all transactions for a user order
    """
    try:
        # Verify that the user order belongs to the current user
        user_order = db.query(UserOrder).filter(
            UserOrder.id == user_order_id,
            UserOrder.user_id == current_user.id
        ).first()
        
        if not user_order:
            raise HTTPException(status_code=404, detail="User order not found")
        
        transactions = db.query(PaymentTransaction).filter(
            PaymentTransaction.user_order_id == user_order_id
        ).all()
        
        return [
            PaymentTransactionResponse(
                id=txn.id,
                user_order_id=txn.user_order_id,
                user_id=txn.user_id,
                transaction_type=txn.transaction_type,
                amount=float(txn.amount),
                payment_method=txn.payment_method,
                status=txn.status,
                external_transaction_id=txn.external_transaction_id,
                payment_gateway=txn.payment_gateway,
                created_at=txn.created_at
            )
            for txn in transactions
        ]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get transactions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get transactions")

@router.get("/my-orders")
def get_my_user_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get all user orders for the current user
    """
    try:
        user_orders = db.query(UserOrder).filter(
            UserOrder.user_id == current_user.id
        ).order_by(UserOrder.created_at.desc()).all()
        
        return [
            UserOrderResponse(
                id=order.id,
                clubbed_order_id=order.clubbed_order_id,
                user_id=order.user_id,
                individual_total=float(order.individual_total),
                payment_method=order.payment_method,
                payment_status=order.payment_status,
                commitment_deadline=order.commitment_deadline,
                is_committed=order.is_committed,
                delivery_address=order.delivery_address,
                delivery_phone=order.delivery_phone,
                special_instructions=order.special_instructions,
                created_at=order.created_at
            )
            for order in user_orders
        ]
        
    except Exception as e:
        logger.error(f"Failed to get user orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get user orders")
