from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CartResponse, CartItemCreate, CartItemResponse
from app.crud import get_active_cart, create_cart, add_item_to_cart, get_cart_details
from app.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.get("/", response_model=CartResponse)
def get_user_cart(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's active cart"""
    cart = get_active_cart(db, current_user.id)
    if not cart:
        cart = create_cart(db, current_user.id)
    return cart

@router.post("/items", response_model=CartItemResponse)
def add_to_cart(
    item: CartItemCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add item to cart"""
    cart = get_active_cart(db, current_user.id)
    if not cart:
        cart = create_cart(db, current_user.id)
    
    cart_item = add_item_to_cart(db, cart.id, item)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Product not found")
    
    return cart_item

@router.get("/{cart_id}", response_model=CartResponse)
def get_cart_by_id(
    cart_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get cart details by ID"""
    cart = get_cart_details(db, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    # Ensure user owns the cart
    if cart.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return cart
