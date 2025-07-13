import uuid
import hashlib
import logging
from typing import List, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, text
from geopy.distance import geodesic
from app.models import (
    User, Product, Cart, CartItem, BuddyQueue, ClubbedOrder, ClubbedOrderUser,
    Driver, Delivery, UserOrder, PaymentTransaction, OrderCancellation
)
from app.enums import BuddyStatus, OrderStatus, DriverStatus
from app.schemas import (
    UserCreate, ProductCreate, CartItemCreate, BuddyQueueCreate,
    DriverCreate, ClubReadinessResponse
)
from app.auth import get_password_hash, verify_password
import os
from math import radians, sin, cos, sqrt, atan2

logger = logging.getLogger(__name__)

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
    print(f"DEBUG: Finding compatible buddies for {buddy_id}")
    current_buddy = db.query(BuddyQueue).filter(BuddyQueue.id == buddy_id).first()
    if not current_buddy or current_buddy.status != BuddyStatus.WAITING.value:
        print(f"DEBUG: Current buddy not found or not waiting. Status: {current_buddy.status if current_buddy else 'None'}")
        return []

    # Timeout for the current user
    timeout_threshold = current_buddy.created_at + timedelta(minutes=current_buddy.timeout_minutes)
    if datetime.utcnow() > timeout_threshold:
        print(f"DEBUG: Current buddy {buddy_id} has timed out")
        current_buddy.status = BuddyStatus.TIMED_OUT.value
        db.commit()
        return []

    # Find other waiting buddies (check timeout in Python instead of SQL)
    potential_buddies = db.query(BuddyQueue).filter(
        BuddyQueue.status == BuddyStatus.WAITING.value,
        BuddyQueue.id != current_buddy.id
    ).all()
    
    print(f"DEBUG: Found {len(potential_buddies)} potential buddies")
    
    # Filter out expired buddies in Python
    current_time = datetime.utcnow()
    valid_buddies = []
    for buddy in potential_buddies:
        timeout_threshold = buddy.created_at + timedelta(minutes=buddy.timeout_minutes)
        if current_time <= timeout_threshold:
            valid_buddies.append(buddy)
        else:
            print(f"DEBUG: Buddy {buddy.id} has timed out")
    
    print(f"DEBUG: {len(valid_buddies)} valid (non-expired) buddies found")
    potential_buddies = valid_buddies

    compatible_group = [current_buddy]
    
    # Max group size can be configured, e.g., 4
    MAX_GROUP_SIZE = int(os.getenv("MAX_CLUB_GROUP_SIZE", 4))

    for potential_buddy in potential_buddies:
        distance = haversine(current_buddy.lat, current_buddy.lng, potential_buddy.lat, potential_buddy.lng)
        print(f"DEBUG: Distance between buddy {current_buddy.id} and {potential_buddy.id}: {distance} meters")
        if distance <= 5000:  # Temporarily increased to 5km for easier testing
            compatible_group.append(potential_buddy)
            print(f"DEBUG: Added buddy {potential_buddy.id} to compatible group")
            if len(compatible_group) >= MAX_GROUP_SIZE:
                break
    
    # We need at least one other person to form a club
    if len(compatible_group) > 1:
        print(f"DEBUG: Returning {len(compatible_group)} compatible buddies for matching")
        return compatible_group
    
    print(f"DEBUG: Not enough buddies for club (only {len(compatible_group)})")
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
        # Check if the existing entry has timed out
        timeout_threshold = existing_entry.created_at + timedelta(minutes=existing_entry.timeout_minutes)
        if datetime.utcnow() > timeout_threshold:
            # Entry has timed out, mark it as timed out
            existing_entry.status = BuddyStatus.TIMED_OUT.value
            db.commit()
            
            # Create a new entry since the old one timed out
            new_buddy = BuddyQueue(
                id=generate_uuid(),
                user_id=user_id,
                cart_id=active_cart.id,
                value_total=cart_value,
                weight_total=cart_weight,
                lat=buddy_data.lat,
                lng=buddy_data.lng,
                location_hash=location_hash,
                timeout_minutes=buddy_data.timeout_minutes,
                status=BuddyStatus.WAITING.value
            )
            db.add(new_buddy)
            db.commit()
            db.refresh(new_buddy)
            return new_buddy
        else:
            # Update existing entry without resetting the timer
            existing_entry.lat = buddy_data.lat
            existing_entry.lng = buddy_data.lng
            existing_entry.location_hash = location_hash
            existing_entry.value_total = cart_value
            existing_entry.weight_total = cart_weight
            existing_entry.cart_id = active_cart.id # Update cart_id in case it changed
            existing_entry.timeout_minutes = buddy_data.timeout_minutes  # Update timeout
            # DO NOT reset created_at - keep the original timestamp
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

        # Explicitly load cart items with product relationships to ensure accurate calculation
        cart_items = db.query(CartItem).filter(CartItem.cart_id == cart.id).all()
        cart_total = sum(item.product.price * item.quantity for item in cart_items)
        cart_weight = sum(item.quantity * item.product.weight_grams for item in cart_items) / 1000  # Convert to kg
        
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
    
    # Automatically initialize split payment process
    try:
        print(f"DEBUG: Auto-initializing split payment for clubbed order {new_clubbed_order.id}")
        user_orders = create_user_orders_for_clubbed_order(db, new_clubbed_order.id)
        if user_orders:
            print(f"DEBUG: Created {len(user_orders)} user orders with payment deadline")
        else:
            print(f"DEBUG: Failed to create user orders")
    except Exception as e:
        print(f"DEBUG: Error auto-initializing split payment: {str(e)}")
        # Don't fail the entire clubbed order creation if split payment fails
        pass
    
    return new_clubbed_order


def get_clubbed_order_details(db: Session, clubbed_order_id: str, requesting_user_id: str):
    """
    Get details of a clubbed order, ensuring the requesting user is part of it.
    Returns anonymized data to protect privacy.
    """
    # First, check if the user is part of this clubbed order
    user_in_club = db.query(ClubbedOrderUser).filter(
        ClubbedOrderUser.clubbed_order_id == clubbed_order_id,
        ClubbedOrderUser.user_id == requesting_user_id
    ).first()

    if not user_in_club:
        return None, [], [], 0.0

    clubbed_order = db.query(ClubbedOrder).filter(ClubbedOrder.id == clubbed_order_id).first()
    
    # Get all users in this clubbed order
    club_users_assoc = db.query(ClubbedOrderUser).filter(ClubbedOrderUser.clubbed_order_id == clubbed_order_id).all()
    user_ids = [cua.user_id for cua in club_users_assoc]
    users = db.query(User).filter(User.id.in_(user_ids)).all()

    # Get current user's items only (for privacy)
    current_user_cart_id = user_in_club.cart_id
    current_user_items_query = db.query(CartItem, User.name.label("added_by_user")).join(
        Cart, CartItem.cart_id == Cart.id
    ).join(
        User, Cart.user_id == User.id
    ).filter(CartItem.cart_id == current_user_cart_id)
    
    current_user_items = current_user_items_query.all()

    # Format current user's items for the response
    formatted_items = [
        {
            "product_name": item.product.name,
            "quantity": item.quantity,
            "price": float(item.product.price),  # Convert Decimal to float
            "added_by_user": "You"
        }
        for item, added_by_user in current_user_items
    ]

    # Calculate anonymized user data
    anonymized_users = []
    other_users_total = 0.0
    
    for i, cua in enumerate(club_users_assoc):
        # Get cart total for this user - using same calculation method as create_clubbed_order
        cart_items = db.query(CartItem).filter(CartItem.cart_id == cua.cart_id).all()
        cart_total = float(sum(item.product.price * item.quantity for item in cart_items))
        item_count = len(cart_items)
        
        is_current_user = cua.user_id == requesting_user_id
        
        anonymized_users.append({
            "user_id": "You" if is_current_user else f"User {i + 1}",
            "cart_total": cart_total,
            "item_count": item_count,
            "is_current_user": is_current_user
        })
        
        if not is_current_user:
            other_users_total += cart_total

    return clubbed_order, anonymized_users, formatted_items, other_users_total


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
    """Mark expired buddy queue entries as TIMED_OUT based on their individual timeout."""
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
            entry.status = BuddyStatus.TIMED_OUT.value
            expired_entries.append(entry.id)
    
    # Commit the status changes
    if expired_entries:
        db.commit()
        return len(expired_entries)
    
    return 0

def cleanup_old_buddy_entries(db: Session, hours_old: int = 24):
    """Delete buddy queue entries that are older than specified hours and not WAITING"""
    cutoff_time = datetime.utcnow() - timedelta(hours=hours_old)
    
    # Delete old entries that are not in WAITING status
    num_deleted = db.query(BuddyQueue).filter(
        and_(
            BuddyQueue.created_at < cutoff_time,
            BuddyQueue.status != BuddyStatus.WAITING.value
        )
    ).delete(synchronize_session=False)
    
    db.commit()
    return num_deleted

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

# Split Payment and Commitment System CRUD Functions

def create_user_orders_for_clubbed_order(db: Session, clubbed_order_id: str) -> List[UserOrder]:
    """
    Create individual user orders for each user in a clubbed order
    """
    
    try:
        # Get clubbed order
        clubbed_order = db.query(ClubbedOrder).filter(ClubbedOrder.id == clubbed_order_id).first()
        if not clubbed_order:
            return []
        
        # Get all users in this clubbed order
        clubbed_users = db.query(ClubbedOrderUser).filter(
            ClubbedOrderUser.clubbed_order_id == clubbed_order_id
        ).all()
        
        user_orders = []
        commitment_deadline = datetime.utcnow() + timedelta(minutes=10)  # 10 minutes to commit
        print(f"DEBUG: Setting commitment deadline to: {commitment_deadline}")
        print(f"DEBUG: Current time: {datetime.utcnow()}")
        
        for clubbed_user in clubbed_users:
            # Calculate individual total for this user
            cart_items = db.query(CartItem).filter(CartItem.cart_id == clubbed_user.cart_id).all()
            individual_total = sum(float(item.product.price) * item.quantity for item in cart_items)
            
            # Create user order
            user_order = UserOrder(
                id=generate_uuid(),
                clubbed_order_id=clubbed_order_id,
                user_id=clubbed_user.user_id,
                cart_id=clubbed_user.cart_id,
                individual_total=individual_total,
                payment_method='ONLINE',  # Default, user can change
                commitment_deadline=commitment_deadline,
                delivery_address="",  # User must provide
                delivery_phone=""  # User must provide
            )
            
            db.add(user_order)
            user_orders.append(user_order)
        
        # Update clubbed order status and deadline
        clubbed_order.status = OrderStatus.PAYMENT_PENDING
        clubbed_order.payment_confirmation_deadline = commitment_deadline
        
        db.commit()
        return user_orders
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to create user orders: {str(e)}")
        return []

def commit_to_payment(db: Session, user_order_id: str, payment_method: str, 
                     delivery_address: str, delivery_phone: str, 
                     special_instructions: str = None) -> bool:
    """
    User commits to payment and provides delivery details
    """
    
    try:
        user_order = db.query(UserOrder).filter(UserOrder.id == user_order_id).first()
        if not user_order:
            return False
        
        # Check if commitment deadline has passed
        if datetime.utcnow() > user_order.commitment_deadline:
            return False
        
        # Update user order with commitment
        user_order.payment_method = payment_method
        user_order.delivery_address = delivery_address
        user_order.delivery_phone = delivery_phone
        user_order.special_instructions = special_instructions
        user_order.is_committed = True
        user_order.committed_at = datetime.utcnow()
        
        db.commit()
        
        # Check if all users have committed
        check_all_commitments(db, user_order.clubbed_order_id)
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to commit to payment: {str(e)}")
        return False

def confirm_payment(db: Session, user_order_id: str, external_transaction_id: str = None,
                   payment_gateway: str = None) -> bool:
    """
    Confirm payment for a user order
    """
    try:
        user_order = db.query(UserOrder).filter(UserOrder.id == user_order_id).first()
        if not user_order:
            return False
        
        # Update payment status
        user_order.payment_status = 'CONFIRMED'
        user_order.payment_confirmed_at = datetime.utcnow()
        
        # Create payment transaction record
        transaction = PaymentTransaction(
            id=generate_uuid(),
            user_order_id=user_order_id,
            user_id=user_order.user_id,
            transaction_type='PAYMENT',
            amount=user_order.individual_total,
            payment_method=user_order.payment_method,
            external_transaction_id=external_transaction_id,
            payment_gateway=payment_gateway,
            status='SUCCESS',
            processed_at=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        
        # Check if all payments are confirmed
        check_all_payments_confirmed(db, user_order.clubbed_order_id)
        
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to confirm payment: {str(e)}")
        return False

def check_all_commitments(db: Session, clubbed_order_id: str) -> bool:
    """
    Check if all users have committed to their payments
    """
    try:
        user_orders = db.query(UserOrder).filter(
            UserOrder.clubbed_order_id == clubbed_order_id
        ).all()
        
        all_committed = all(order.is_committed for order in user_orders)
        
        if all_committed:
            # Update clubbed order status
            clubbed_order = db.query(ClubbedOrder).filter(
                ClubbedOrder.id == clubbed_order_id
            ).first()
            
            if clubbed_order and clubbed_order.status == OrderStatus.PAYMENT_PENDING:
                # Extend deadline for payment confirmation
                from datetime import timedelta
                clubbed_order.payment_confirmation_deadline = datetime.utcnow() + timedelta(minutes=30)
                db.commit()
        
        return all_committed
        
    except Exception as e:
        logger.error(f"Failed to check commitments: {str(e)}")
        return False

def check_all_payments_confirmed(db: Session, clubbed_order_id: str) -> bool:
    """
    Check if all users have confirmed their payments
    """
    try:
        user_orders = db.query(UserOrder).filter(
            UserOrder.clubbed_order_id == clubbed_order_id
        ).all()
        
        all_confirmed = all(order.payment_status == 'CONFIRMED' for order in user_orders)
        
        if all_confirmed:
            # Update clubbed order
            clubbed_order = db.query(ClubbedOrder).filter(
                ClubbedOrder.id == clubbed_order_id
            ).first()
            
            if clubbed_order:
                clubbed_order.status = OrderStatus.PAYMENT_CONFIRMED
                clubbed_order.all_payments_confirmed = True
                clubbed_order.order_confirmed_at = datetime.utcnow()
                
                # Assign delivery driver (placeholder for now)
                # assign_delivery_driver(db, clubbed_order_id)
                
                db.commit()
        
        return all_confirmed
        
    except Exception as e:
        logger.error(f"Failed to check payment confirmations: {str(e)}")
        return False

def cancel_user_order(db: Session, user_order_id: str, cancelled_by_user_id: str, 
                     reason: str = 'USER_WITHDREW') -> Optional[OrderCancellation]:
    """
    Cancel a user order and handle penalties/compensation
    """
    try:
        user_order = db.query(UserOrder).filter(UserOrder.id == user_order_id).first()
        if not user_order:
            return None
        
        # Calculate cancellation fee (10% of order value, minimum ₹50, maximum ₹200)
        cancellation_fee = max(50.0, min(200.0, float(user_order.individual_total) * 0.1))
        
        # Calculate compensation (60% of cancellation fee goes to other users)
        compensation_amount = cancellation_fee * 0.6
        company_penalty_share = cancellation_fee * 0.4
        
        # Create cancellation record
        cancellation = OrderCancellation(
            id=generate_uuid(),
            user_order_id=user_order_id,
            clubbed_order_id=user_order.clubbed_order_id,
            cancelled_by_user_id=cancelled_by_user_id,
            cancellation_reason=reason,
            cancellation_fee=cancellation_fee,
            compensation_amount=compensation_amount,
            company_penalty_share=company_penalty_share
        )
        
        db.add(cancellation)
        
        # Update user order status
        user_order.payment_status = 'CANCELLED'
        
        # Cancel the entire clubbed order
        cancel_entire_clubbed_order(db, user_order.clubbed_order_id, cancellation.id)
        
        db.commit()
        return cancellation
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to cancel user order: {str(e)}")
        return None

def cancel_entire_clubbed_order(db: Session, clubbed_order_id: str, cancellation_id: str):
    """
    Cancel the entire clubbed order when one user withdraws
    """
    try:
        # Get all user orders for this clubbed order
        user_orders = db.query(UserOrder).filter(
            UserOrder.clubbed_order_id == clubbed_order_id
        ).all()
        
        # Cancel all other user orders
        for user_order in user_orders:
            if user_order.payment_status != 'CANCELLED':
                user_order.payment_status = 'CANCELLED'
        
        # Update clubbed order status
        clubbed_order = db.query(ClubbedOrder).filter(
            ClubbedOrder.id == clubbed_order_id
        ).first()
        
        if clubbed_order:
            clubbed_order.status = OrderStatus.CANCELLED
        
        # Process compensation to other users
        process_cancellation_compensation(db, clubbed_order_id, cancellation_id)
        
    except Exception as e:
        logger.error(f"Failed to cancel clubbed order: {str(e)}")

def process_cancellation_compensation(db: Session, clubbed_order_id: str, cancellation_id: str):
    """
    Process compensation payments to users affected by cancellation
    """
    try:
        cancellation = db.query(OrderCancellation).filter(
            OrderCancellation.id == cancellation_id
        ).first()
        
        if not cancellation or cancellation.compensation_processed:
            return
        
        # Get all other user orders (excluding the one that was cancelled)
        other_user_orders = db.query(UserOrder).filter(
            UserOrder.clubbed_order_id == clubbed_order_id,
            UserOrder.id != cancellation.user_order_id
        ).all()
        
        if other_user_orders:
            # Divide compensation equally among other users
            compensation_per_user = cancellation.compensation_amount / len(other_user_orders)
            
            for user_order in other_user_orders:
                # Create compensation transaction
                compensation_transaction = PaymentTransaction(
                    id=generate_uuid(),
                    user_order_id=user_order.id,
                    user_id=user_order.user_id,
                    transaction_type='COMPENSATION',
                    amount=compensation_per_user,
                    payment_method='WALLET',  # Credit to wallet
                    status='SUCCESS',
                    processed_at=datetime.utcnow()
                )
                
                db.add(compensation_transaction)
        
        # Create penalty transaction for cancelling user
        penalty_transaction = PaymentTransaction(
            id=generate_uuid(),
            user_order_id=cancellation.user_order_id,
            user_id=cancellation.cancelled_by_user_id,
            transaction_type='PENALTY',
            amount=cancellation.cancellation_fee,
            payment_method='ONLINE',  # Charge to user
            status='PENDING',  # Will be processed by payment system
            processed_at=datetime.utcnow()
        )
        
        db.add(penalty_transaction)
        
        # Mark compensation as processed
        cancellation.compensation_processed = True
        cancellation.penalty_processed = True
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to process compensation: {str(e)}")

def get_split_payment_summary(db: Session, clubbed_order_id: str, user_id: str) -> Optional[dict]:
    """
    Get payment summary for a user in a clubbed order
    """
    try:
        # Get user's order
        user_order = db.query(UserOrder).filter(
            UserOrder.clubbed_order_id == clubbed_order_id,
            UserOrder.user_id == user_id
        ).first()
        
        if not user_order:
            return None
        
        # Get clubbed order
        clubbed_order = db.query(ClubbedOrder).filter(
            ClubbedOrder.id == clubbed_order_id
        ).first()
        
        # Get all user orders for this clubbed order
        all_user_orders = db.query(UserOrder).filter(
            UserOrder.clubbed_order_id == clubbed_order_id
        ).all()
        
        # Calculate totals
        total_order_value = float(clubbed_order.combined_value)
        your_portion = float(user_order.individual_total)
        other_users_portion = total_order_value - your_portion
        
        # Calculate delivery fee (shared equally)
        delivery_fee = 40.0  # Base delivery fee
        delivery_fee_per_user = delivery_fee / len(all_user_orders)
        
        # Calculate discount (5% for clubbed orders)
        discount_applied = your_portion * 0.05
        
        # Final amount to pay
        final_amount = your_portion + delivery_fee_per_user - discount_applied
        
        # Check commitment status
        confirmed_payments = sum(1 for order in all_user_orders if order.payment_status == 'CONFIRMED')
        pending_payments = len(all_user_orders) - confirmed_payments
        all_users_committed = all(order.is_committed for order in all_user_orders)
        
        return {
            'clubbed_order_id': clubbed_order_id,
            'total_order_value': total_order_value,
            'your_portion': your_portion,
            'other_users_portion': other_users_portion,
            'delivery_fee': delivery_fee_per_user,
            'discount_applied': discount_applied,
            'final_amount_to_pay': final_amount,
            'payment_deadline': user_order.commitment_deadline.isoformat() + 'Z' if user_order.commitment_deadline else None,
            'all_users_committed': all_users_committed,
            'confirmed_payments': confirmed_payments,
            'pending_payments': pending_payments
        }
        
    except Exception as e:
        logger.error(f"Failed to get payment summary: {str(e)}")
        return None
