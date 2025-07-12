import uuid
import hashlib
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from geopy.distance import geodesic
from app.models import (
    User, Product, Cart, CartItem, BuddyQueue, ClubbedOrder, ClubbedOrderUser,
    Driver, Delivery
)
from app.enums import BuddyStatus, OrderStatus, DriverStatus
from app.schemas import (
    UserCreate, ProductCreate, CartItemCreate, BuddyQueueCreate,
    DriverCreate, ClubReadinessResponse
)
from app.auth import get_password_hash, verify_password
import os
from math import radians, sin, cos, sqrt, atan2

CLUB_WAIT_TIME_MINUTES = int(os.getenv("CLUB_WAIT_TIME_MINUTES", "5"))
MAX_DELIVERY_WEIGHT_KG = float(os.getenv("MAX_DELIVERY_WEIGHT_KG", "5.0"))
LOCATION_CLUSTER_RADIUS_KM = float(os.getenv("LOCATION_CLUSTER_RADIUS_KM", "2.0"))

def generate_uuid():
    return str(uuid.uuid4())

def generate_location_hash(lat: float, lng: float, precision: int = 3) -> str:
    """Generate a hash for location clustering"""
    location_string = f"{round(lat, precision)},{round(lng, precision)}"
    return hashlib.md5(location_string.encode()).hexdigest()[:8]

# User operations
def create_user(db: Session, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(
        id=generate_uuid(),
        name=user.name,
        email=user.email,
        password_hash=hashed_password,
        phone=user.phone,
        address=user.address
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user

# Product operations
def create_product(db: Session, product: ProductCreate):
    db_product = Product(
        id=generate_uuid(),
        **product.dict()
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()

def get_product(db: Session, product_id: str):
    return db.query(Product).filter(Product.id == product_id).first()

# Cart operations
def get_active_cart(db: Session, user_id: str):
    return db.query(Cart).filter(
        and_(Cart.user_id == user_id, Cart.is_active == True)
    ).first()

def create_cart(db: Session, user_id: str):
    db_cart = Cart(
        id=generate_uuid(),
        user_id=user_id,
        is_active=True
    )
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

def add_item_to_cart(db: Session, cart_id: str, item: CartItemCreate):
    product = get_product(db, item.product_id)
    if not product:
        return None

    # Check stock before adding
    if product.stock < item.quantity:
        raise Exception("Not enough stock available")

    # Check if item already exists in cart
    existing_item = db.query(CartItem).filter(
        and_(CartItem.cart_id == cart_id, CartItem.product_id == item.product_id)
    ).first()

    if existing_item:
        # Decrement stock by the additional quantity
        product.stock -= item.quantity
        existing_item.quantity += item.quantity
        existing_item.total_price = existing_item.quantity * product.price
        db.commit()
        db.refresh(existing_item)
        db.refresh(product)
        return existing_item
    else:
        # Decrement stock by the quantity being added
        product.stock -= item.quantity
        db_item = CartItem(
            id=generate_uuid(),
            cart_id=cart_id,
            product_id=item.product_id,
            quantity=item.quantity,
            total_price=item.quantity * product.price
        )
        db.add(db_item)
        db.commit()
        db.refresh(db_item)
        db.refresh(product)
        return db_item
def remove_item_from_cart(db: Session, cart_id: str, item_id: str):
    """Remove an item from the cart"""
    cart_item = db.query(CartItem).filter(
        and_(CartItem.id == item_id, CartItem.cart_id == cart_id)
    ).first()
    
    if not cart_item:
        return None
    
    # Restore stock
    product = get_product(db, cart_item.product_id)
    if product:
        product.stock += cart_item.quantity
        db.refresh(product)
    
    # Remove the item
    db.delete(cart_item)
    db.commit()
    return True

def update_cart_item_quantity(db: Session, cart_id: str, item_id: str, new_quantity: int):
    """Update quantity of an item in the cart"""
    if new_quantity <= 0:
        return remove_item_from_cart(db, cart_id, item_id)
    
    cart_item = db.query(CartItem).filter(
        and_(CartItem.id == item_id, CartItem.cart_id == cart_id)
    ).first()
    
    if not cart_item:
        return None
    
    product = get_product(db, cart_item.product_id)
    if not product:
        return None
    
    # Calculate quantity difference
    quantity_diff = new_quantity - cart_item.quantity
    
    # Check if we have enough stock for increase
    if quantity_diff > 0 and product.stock < quantity_diff:
        raise Exception("Not enough stock available")
    
    # Update stock
    product.stock -= quantity_diff
    
    # Update cart item
    cart_item.quantity = new_quantity
    cart_item.total_price = new_quantity * product.price
    
    db.commit()
    db.refresh(cart_item)
    db.refresh(product)
    
    return cart_item

def get_cart_details(db: Session, cart_id: str):
    return db.query(Cart).filter(Cart.id == cart_id).first()

def calculate_cart_totals(db: Session, cart_id: str):
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    if not cart_items:
        return 0, 0  # Return 0 for empty cart
    
    total_value = sum(item.total_price for item in cart_items)
    total_weight = sum(item.quantity * item.product.weight_grams for item in cart_items) / 1000  # Convert to kg
    return total_value, total_weight

# Club readiness operations
def check_club_readiness(db: Session, user_id: str, lat: float, lng: float):
    location_hash = generate_location_hash(lat, lng)
    current_time = datetime.utcnow()
    
    # Get all nearby waiting users and check if they're still within their timeout
    nearby_entries = db.query(BuddyQueue).filter(
        and_(
            BuddyQueue.location_hash == location_hash,
            BuddyQueue.status == BuddyStatus.WAITING,
            BuddyQueue.user_id != user_id
        )
    ).all()
    
    # Count only those users who haven't timed out yet
    nearby_waiting = 0
    for entry in nearby_entries:
        timeout_threshold = entry.created_at + timedelta(minutes=entry.timeout_minutes)
        if current_time <= timeout_threshold:
            nearby_waiting += 1
    
    # Calculate potential discount based on typical cart values
    potential_discount = Decimal('30.0') if nearby_waiting > 0 else Decimal('0.0')
    
    return ClubReadinessResponse(
        can_club=nearby_waiting > 0,
        estimated_wait_time=5,  # Default estimate - could be made dynamic too
        potential_discount=potential_discount,
        nearby_users_count=nearby_waiting
    )

def haversine(lat1, lon1, lat2, lon2):
    """
    Calculate the distance between two points on Earth in meters.
    """
    R = 6371000  # Radius of Earth in meters
    lat1_rad, lon1_rad, lat2_rad, lon2_rad = map(radians, [lat1, lon1, lat2, lon2])

    dlon = lon2_rad - lon1_rad
    dlat = lat2_rad - lat1_rad

    a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return distance

def find_compatible_buddies(db: Session, buddy_id: str) -> List[BuddyQueue]:
    """
    Find compatible buddies for a user based on location and timeout.
    """
    current_buddy = db.query(BuddyQueue).filter(BuddyQueue.id == buddy_id).first()
    if not current_buddy or current_buddy.status != BuddyStatus.WAITING.value:
        return []

    # Timeout for the current user
    timeout_threshold = current_buddy.created_at + timedelta(minutes=current_buddy.timeout_minutes)
    if datetime.utcnow() > timeout_threshold:
        current_buddy.status = BuddyStatus.TIMED_OUT.value
        db.commit()
        return []

    # Find other waiting buddies (check timeout in Python instead of SQL)
    potential_buddies = db.query(BuddyQueue).filter(
        BuddyQueue.status == BuddyStatus.WAITING.value,
        BuddyQueue.id != current_buddy.id
    ).all()
    
    # Filter out expired buddies in Python
    current_time = datetime.utcnow()
    valid_buddies = []
    for buddy in potential_buddies:
        timeout_threshold = buddy.created_at + timedelta(minutes=buddy.timeout_minutes)
        if current_time <= timeout_threshold:
            valid_buddies.append(buddy)
    
    potential_buddies = valid_buddies

    compatible_group = [current_buddy]
    
    # Max group size can be configured, e.g., 4
    MAX_GROUP_SIZE = int(os.getenv("MAX_CLUB_GROUP_SIZE", 4))

    for potential_buddy in potential_buddies:
        distance = haversine(current_buddy.lat, current_buddy.lng, potential_buddy.lat, potential_buddy.lng)
        if distance <= 300:  # 300 meters radius
            compatible_group.append(potential_buddy)
            if len(compatible_group) >= MAX_GROUP_SIZE:
                break
    
    # We need at least one other person to form a club
    if len(compatible_group) > 1:
        return compatible_group
    
    return []

def join_buddy_queue(db: Session, user_id: int, buddy_data: BuddyQueueCreate) -> BuddyQueue:
    # Debug: Log the received timeout_minutes value
    print(f"DEBUG: Received timeout_minutes = {buddy_data.timeout_minutes}")
    
    # Check for existing active entry for the user
    existing_entry = db.query(BuddyQueue).filter(
        and_(
            BuddyQueue.user_id == user_id,
            BuddyQueue.status == BuddyStatus.WAITING.value
        )
    ).first()

    active_cart = get_active_cart(db, user_id)
    if not active_cart:
        return {"ready": False, "message": "Please add items to your cart before joining the queue."}

    cart_value, cart_weight = calculate_cart_totals(db, active_cart.id)
    location_hash = generate_location_hash(float(buddy_data.lat), float(buddy_data.lng))

    if existing_entry:
        # Update existing entry
        existing_entry.lat = buddy_data.lat
        existing_entry.lng = buddy_data.lng
        existing_entry.location_hash = location_hash
        existing_entry.value_total = cart_value
        existing_entry.weight_total = cart_weight
        existing_entry.cart_id = active_cart.id # Update cart_id in case it changed
        existing_entry.timeout_minutes = buddy_data.timeout_minutes  # Update timeout
        existing_entry.created_at = datetime.utcnow() # Reset timer on refresh
        db.commit()
        db.refresh(existing_entry)
        return existing_entry
    else:
        # Create new entry
        new_buddy = BuddyQueue(
            id=generate_uuid(),
            user_id=user_id,
            cart_id=active_cart.id,
            value_total=cart_value,
            weight_total=cart_weight,
            lat=buddy_data.lat,
            lng=buddy_data.lng,
            location_hash=location_hash,
            timeout_minutes=buddy_data.timeout_minutes,  # Use dynamic timeout
            status=BuddyStatus.WAITING.value
        )
        db.add(new_buddy)
        db.commit()
        db.refresh(new_buddy)
        return new_buddy

def create_clubbed_order(db: Session, buddies: List[BuddyQueue]) -> ClubbedOrder:
    """
    Creates a clubbed order from a list of matched buddies.
    """
    # Create the main clubbed order
    new_clubbed_order = ClubbedOrder(
        id=generate_uuid(),
        status=OrderStatus.CREATED.value,
        combined_value=0,  # Will be calculated later
        combined_weight=0,  # Will be calculated later
        total_discount=0
    )
    db.add(new_clubbed_order)
    db.flush()  # To get the ID for the new_clubbed_order

    total_amount = 0
    total_weight = 0
    
    for buddy in buddies:
        # Link user to the clubbed order
        cart = db.query(Cart).filter(Cart.id == buddy.cart_id).first()
        if not cart:
            # This should ideally not happen
            continue

        cart_total = sum(item.product.price * item.quantity for item in cart.cart_items)
        cart_weight = sum(item.quantity * item.product.weight_grams for item in cart.cart_items) / 1000  # Convert to kg
        
        total_amount += cart_total
        total_weight += cart_weight

        club_user = ClubbedOrderUser(
            id=generate_uuid(),
            clubbed_order_id=new_clubbed_order.id,
            user_id=buddy.user_id,
            cart_id=buddy.cart_id,
            discount_given=0.05  # Example: 5% discount
        )
        db.add(club_user)

        # Update buddy status
        buddy.status = BuddyStatus.MATCHED.value
        
        # Deactivate the user's cart - This should happen after checkout, not here.
        # cart.is_active = False

    new_clubbed_order.combined_value = total_amount
    new_clubbed_order.combined_weight = total_weight
    new_clubbed_order.total_discount = total_amount * Decimal('0.05')  # 5% discount
    db.commit()
    db.refresh(new_clubbed_order)
    
    return new_clubbed_order


def get_clubbed_order_details(db: Session, clubbed_order_id: str, requesting_user_id: str):
    """
    Get details of a clubbed order, ensuring the requesting user is part of it.
    """
    # First, check if the user is part of this clubbed order
    user_in_club = db.query(ClubbedOrderUser).filter(
        ClubbedOrderUser.clubbed_order_id == clubbed_order_id,
        ClubbedOrderUser.user_id == requesting_user_id
    ).first()

    if not user_in_club:
        return None, [], []

    clubbed_order = db.query(ClubbedOrder).filter(ClubbedOrder.id == clubbed_order_id).first()
    
    # Get all users in this clubbed order
    club_users_assoc = db.query(ClubbedOrderUser).filter(ClubbedOrderUser.clubbed_order_id == clubbed_order_id).all()
    user_ids = [cua.user_id for cua in club_users_assoc]
    users = db.query(User).filter(User.id.in_(user_ids)).all()

    # Get all items from all carts in this clubbed order
    cart_ids = [cua.cart_id for cua in club_users_assoc]
    all_items_query = db.query(CartItem, User.name.label("added_by_user")).join(
        Cart, CartItem.cart_id == Cart.id
    ).join(
        User, Cart.user_id == User.id
    ).filter(CartItem.cart_id.in_(cart_ids))
    
    all_items = all_items_query.all()

    # Format items for the response
    formatted_items = [
        {
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": float(item.product.price),  # Convert Decimal to float
            "added_by_user": added_by_user
        }
        for item, added_by_user in all_items
    ]

    return clubbed_order, users, formatted_items


def add_item_to_clubbed_cart(db: Session, clubbed_order_id: str, user_id: str, item: CartItemCreate):
    """
    Adds an item to a user's original cart that is part of a clubbed order.
    """
    # Find the user's association to the clubbed order to get their cart_id
    club_user_assoc = db.query(ClubbedOrderUser).filter(
        ClubbedOrderUser.clubbed_order_id == clubbed_order_id,
        ClubbedOrderUser.user_id == user_id
    ).first()

    if not club_user_assoc:
        return None # User is not part of this clubbed order

    # Add item to the user's original cart
    cart_item = add_item_to_cart(db, club_user_assoc.cart_id, item)
    if not cart_item:
        return None

    # Recalculate the total amount for the clubbed order
    clubbed_order = db.query(ClubbedOrder).filter(ClubbedOrder.id == clubbed_order_id).first()
    
    # Get all carts in this clubbed order
    club_users_assoc = db.query(ClubbedOrderUser).filter(ClubbedOrderUser.clubbed_order_id == clubbed_order_id).all()
    cart_ids = [cua.cart_id for cua in club_users_assoc]
    
    total_amount = 0
    total_weight = 0
    for cart_id in cart_ids:
        cart_total, cart_weight = calculate_cart_totals(db, cart_id)
        total_amount += cart_total
        total_weight += cart_weight
        
    clubbed_order.combined_value = total_amount
    clubbed_order.combined_weight = total_weight
    clubbed_order.total_discount = total_amount * Decimal('0.05')  # Recalculate 5% discount
    db.commit()
    db.refresh(clubbed_order)

    return {
        "product_name": cart_item.product.name,
        "quantity": cart_item.quantity,
        "price": cart_item.product.price,
        "added_by_user": db.query(User).filter(User.id == user_id).first().name
    }


def assign_driver_to_order(db: Session, clubbed_order_id: str, driver_id: int = None):
    """Assign the best available driver to a clubbed order"""
    clubbed_order = db.query(ClubbedOrder).filter(ClubbedOrder.id == clubbed_order_id).first()
    if not clubbed_order:
        return None
    
    # Find driver with sufficient capacity
    available_drivers = db.query(Driver).filter(
        and_(
            Driver.status == DriverStatus.AVAILABLE.value,
            Driver.current_load + (clubbed_order.combined_weight or 0) <= Driver.max_capacity
        )
    ).order_by(Driver.current_load).all()
    
    if not available_drivers:
        return None
    
    driver = available_drivers[0]
    
    # Create delivery
    delivery = Delivery(
        id=generate_uuid(),
        driver_id=driver.id,
        clubbed_order_id=clubbed_order_id,
        estimated_delivery=datetime.utcnow() + timedelta(minutes=30)  # 30 minutes from now
    )
    db.add(delivery)
    
    # Update driver status and load
    driver.current_load += (clubbed_order.combined_weight or 0)
    if driver.current_load >= driver.max_capacity * 0.9:  # 90% capacity threshold
        driver.status = DriverStatus.BUSY.value
    
    # Update order status
    clubbed_order.status = OrderStatus.PREPARING.value
    
    db.commit()
    db.refresh(delivery)
    return delivery

# Get user orders
def get_user_orders(db: Session, user_id: str):
    return db.query(ClubbedOrderUser).filter(ClubbedOrderUser.user_id == user_id).all()

# Timeout management
def timeout_expired_buddies(db: Session):
    """Remove expired buddy queue entries based on their individual timeout."""
    current_time = datetime.utcnow()
    
    # Find all waiting entries and check each one's individual timeout
    waiting_entries = db.query(BuddyQueue).filter(
        BuddyQueue.status == BuddyStatus.WAITING.value
    ).all()
    
    expired_entries = []
    for entry in waiting_entries:
        # Calculate timeout for this specific entry
        timeout_threshold = entry.created_at + timedelta(minutes=entry.timeout_minutes)
        if current_time > timeout_threshold:
            expired_entries.append(entry.id)
    
    # Delete expired entries
    if expired_entries:
        num_deleted = db.query(BuddyQueue).filter(
            BuddyQueue.id.in_(expired_entries)
        ).delete(synchronize_session=False)
        db.commit()
        return num_deleted
    
    return 0

def clear_cart(db: Session, cart_id: str):
    """Clear all items from a cart and restore stock"""
    cart_items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    
    # Restore stock for all items
    for cart_item in cart_items:
        product = get_product(db, cart_item.product_id)
        if product:
            product.stock += cart_item.quantity
            db.refresh(product)
    
    # Delete all cart items
    db.query(CartItem).filter(CartItem.cart_id == cart_id).delete()
    db.commit()
    
    return len(cart_items)  # Return number of items removed

def delete_cart(db: Session, cart_id: str):
    """Delete the entire cart and all its items"""
    # First clear all items (this restores stock)
    clear_cart(db, cart_id)
    
    # Then delete the cart itself
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if cart:
        db.delete(cart)
        db.commit()
        return True
    return False
