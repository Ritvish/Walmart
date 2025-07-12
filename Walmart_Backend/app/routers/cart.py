from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import CartResponse, CartItemCreate, CartItemResponse, CartItemUpdateQuantity, CartClearResponse
from app.crud import get_active_cart, create_cart, add_item_to_cart, get_cart_details, remove_item_from_cart, update_cart_item_quantity, clear_cart, delete_cart
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

@router.delete("/items/{item_id}", response_model=dict)
def remove_from_cart(
    item_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove item from cart"""
    cart = get_active_cart(db, current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    result = remove_item_from_cart(db, cart.id, item_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Item not found in cart")
    
    return {"success": True, "message": "Item removed from cart"}

@router.put("/items/{item_id}/quantity", response_model=dict)
def update_cart_item(
    item_id: str,
    quantity_update: CartItemUpdateQuantity,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update quantity of item in cart"""
    cart = get_active_cart(db, current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    try:
        result = update_cart_item_quantity(db, cart.id, item_id, quantity_update.quantity)
        if result is None:
            raise HTTPException(status_code=404, detail="Item not found in cart")
        if result is True:  # Item was removed (quantity was 0)
            return {"success": True, "message": "Item removed from cart"}
        return {"success": True, "message": "Quantity updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/clear", response_model=CartClearResponse)
def clear_user_cart(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all items from user's cart"""
    cart = get_active_cart(db, current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    items_removed = clear_cart(db, cart.id)
    
    return CartClearResponse(
        success=True, 
        message=f"Cart cleared successfully. {items_removed} items removed.",
        items_removed=items_removed
    )

@router.delete("/", response_model=dict)
def delete_user_cart(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete the entire cart"""
    cart = get_active_cart(db, current_user.id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    
    result = delete_cart(db, cart.id)
    
    if not result:
        raise HTTPException(status_code=400, detail="Failed to delete cart")
    
    return {"success": True, "message": "Cart deleted successfully"}
