from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ClubbedCartResponse, ClubbedCartItem, CartItemCreate
from app.crud import get_clubbed_order_details, add_item_to_clubbed_cart
from app.auth import get_current_user
from app.models import User

router = APIRouter(prefix="/clubbed-cart", tags=["Clubbed Cart"])

@router.get("/{clubbed_order_id}", response_model=ClubbedCartResponse)
def get_clubbed_cart(
    clubbed_order_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the details of a clubbed cart, including all items from all users.
    """
    clubbed_order, users, items = get_clubbed_order_details(db, clubbed_order_id, current_user.id)

    if not clubbed_order:
        raise HTTPException(status_code=404, detail="Clubbed order not found or you are not part of it.")

    return ClubbedCartResponse(
        clubbed_order_id=clubbed_order.id,
        status=clubbed_order.status,
        total_amount=float(clubbed_order.combined_value),  # Convert Decimal to float
        users=[user.name for user in users],
        items=items
    )

@router.post("/{clubbed_order_id}/items", response_model=ClubbedCartItem)
def add_to_clubbed_cart(
    clubbed_order_id: str,
    item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add an item to a user's cart within a clubbed order.
    """
    new_item = add_item_to_clubbed_cart(db, clubbed_order_id, current_user.id, item)

    if not new_item:
        raise HTTPException(status_code=400, detail="Could not add item. Ensure the clubbed order exists and you are a part of it.")

    return new_item
