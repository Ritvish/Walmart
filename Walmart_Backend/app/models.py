from sqlalchemy import create_engine, Column, String, Integer, DECIMAL, Boolean, TIMESTAMP, Enum, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from .enums import BuddyStatus, OrderStatus, DriverStatus, DeliveryStatus

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    carts = relationship("Cart", back_populates="user")
    buddy_queue_entries = relationship("BuddyQueue", back_populates="user")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    weight_grams = Column(Integer, nullable=False)
    stock = Column(Integer, default=0)
    image_url = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    cart_items = relationship("CartItem", back_populates="product")

class Cart(Base):
    __tablename__ = "carts"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    is_active = Column(Boolean, default=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="carts")
    cart_items = relationship("CartItem", back_populates="cart")
    buddy_queue_entries = relationship("BuddyQueue", back_populates="cart")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(String(36), primary_key=True)
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"))
    product_id = Column(String(36), ForeignKey("products.id"))
    quantity = Column(Integer, nullable=False)
    total_price = Column(DECIMAL(10, 2))
    
    # Relationships
    cart = relationship("Cart", back_populates="cart_items")
    product = relationship("Product", back_populates="cart_items")

class BuddyQueue(Base):
    __tablename__ = "buddy_queue"
    
    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"))
    cart_id = Column(String(36), ForeignKey("carts.id", ondelete="CASCADE"))
    value_total = Column(DECIMAL(10, 2), nullable=False)
    weight_total = Column(DECIMAL(10, 2), nullable=False)
    lat = Column(DECIMAL(9, 6), nullable=False)
    lng = Column(DECIMAL(9, 6), nullable=False)
    location_hash = Column(String(20))
    status = Column(Enum(BuddyStatus, validate_strings=True, native_enum=False), default=BuddyStatus.WAITING)
    timeout_minutes = Column(Integer, nullable=False, default=5)  # Dynamic timeout per user
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="buddy_queue_entries")
    cart = relationship("Cart", back_populates="buddy_queue_entries")

class ClubbedOrder(Base):
    __tablename__ = "clubbed_orders"
    
    id = Column(String(36), primary_key=True)
    combined_value = Column(DECIMAL(10, 2))
    combined_weight = Column(DECIMAL(10, 2))
    total_discount = Column(DECIMAL(10, 2))
    status = Column(Enum(OrderStatus, validate_strings=True, native_enum=False), default=OrderStatus.CREATED)
    
    # Payment and commitment tracking
    all_payments_confirmed = Column(Boolean, default=False)
    payment_confirmation_deadline = Column(TIMESTAMP)
    order_confirmed_at = Column(TIMESTAMP)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    clubbed_order_users = relationship("ClubbedOrderUser", back_populates="clubbed_order")
    user_orders = relationship("UserOrder", back_populates="clubbed_order")

class ClubbedOrderUser(Base):
    __tablename__ = "clubbed_order_users"
    
    id = Column(String(36), primary_key=True)
    clubbed_order_id = Column(String(36), ForeignKey("clubbed_orders.id", ondelete="CASCADE"))
    user_id = Column(String(36), ForeignKey("users.id"))
    cart_id = Column(String(36), ForeignKey("carts.id"))
    discount_given = Column(DECIMAL(5, 4), default=0.0)  # e.g., 0.05 for 5%
    
    # Relationships
    clubbed_order = relationship("ClubbedOrder", back_populates="clubbed_order_users")
    user = relationship("User")
    cart = relationship("Cart")

class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    status = Column(Enum(DriverStatus, validate_strings=True, native_enum=False), default=DriverStatus.INACTIVE)
    lat = Column(DECIMAL(9, 6))
    lng = Column(DECIMAL(9, 6))
    current_load = Column(DECIMAL(10, 2), default=0.0)  # Current load in kg
    max_capacity = Column(DECIMAL(10, 2), default=20.0)  # Maximum capacity in kg
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    deliveries = relationship("Delivery", back_populates="driver")

class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(String(36), primary_key=True)
    clubbed_order_id = Column(String(36), ForeignKey("clubbed_orders.id"))
    driver_id = Column(String(36), ForeignKey("drivers.id"))
    status = Column(Enum(DeliveryStatus, validate_strings=True, native_enum=False), default=DeliveryStatus.ASSIGNED)
    estimated_delivery = Column(TIMESTAMP)
    actual_delivery = Column(TIMESTAMP)
    
    # Relationships
    clubbed_order = relationship("ClubbedOrder")
    driver = relationship("Driver", back_populates="deliveries")

# New models for split payment and commitment system

class UserOrder(Base):
    """Individual user's portion of a clubbed order"""
    __tablename__ = "user_orders"
    
    id = Column(String(36), primary_key=True)
    clubbed_order_id = Column(String(36), ForeignKey("clubbed_orders.id", ondelete="CASCADE"))
    user_id = Column(String(36), ForeignKey("users.id"))
    cart_id = Column(String(36), ForeignKey("carts.id"))
    
    # Payment details
    individual_total = Column(DECIMAL(10, 2), nullable=False)  # User's portion
    payment_method = Column(Enum('ONLINE', 'COD', name='payment_method_enum'), nullable=False)
    payment_status = Column(Enum('PENDING', 'CONFIRMED', 'FAILED', 'CANCELLED', name='payment_status_enum'), default='PENDING')
    payment_confirmed_at = Column(TIMESTAMP)
    
    # Commitment tracking
    commitment_deadline = Column(TIMESTAMP, nullable=False)  # When user must confirm payment
    is_committed = Column(Boolean, default=False)
    committed_at = Column(TIMESTAMP)
    
    # Delivery details for this user
    delivery_address = Column(Text, nullable=False)
    delivery_phone = Column(String(20), nullable=False)
    special_instructions = Column(Text)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    clubbed_order = relationship("ClubbedOrder", back_populates="user_orders")
    user = relationship("User")
    cart = relationship("Cart")
    cancellation = relationship("OrderCancellation", back_populates="user_order", uselist=False)

class OrderCancellation(Base):
    """Tracks order cancellations and penalties"""
    __tablename__ = "order_cancellations"
    
    id = Column(String(36), primary_key=True)
    user_order_id = Column(String(36), ForeignKey("user_orders.id", ondelete="CASCADE"))
    clubbed_order_id = Column(String(36), ForeignKey("clubbed_orders.id"))
    cancelled_by_user_id = Column(String(36), ForeignKey("users.id"))
    
    # Cancellation details
    cancellation_reason = Column(Enum('PAYMENT_FAILED', 'USER_WITHDREW', 'TIMEOUT', 'SYSTEM_ERROR', name='cancellation_reason_enum'))
    cancelled_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Financial impact
    cancellation_fee = Column(DECIMAL(10, 2), default=0.0)  # Fee charged to cancelling user
    compensation_amount = Column(DECIMAL(10, 2), default=0.0)  # Amount given to other users
    company_penalty_share = Column(DECIMAL(10, 2), default=0.0)  # Company's share of penalty
    
    # Processing status
    penalty_processed = Column(Boolean, default=False)
    compensation_processed = Column(Boolean, default=False)
    
    # Relationships
    user_order = relationship("UserOrder", back_populates="cancellation")
    clubbed_order = relationship("ClubbedOrder")
    cancelled_by_user = relationship("User")

class PaymentTransaction(Base):
    """Tracks all payment transactions"""
    __tablename__ = "payment_transactions"
    
    id = Column(String(36), primary_key=True)
    user_order_id = Column(String(36), ForeignKey("user_orders.id"))
    user_id = Column(String(36), ForeignKey("users.id"))
    
    # Transaction details
    transaction_type = Column(Enum('PAYMENT', 'REFUND', 'PENALTY', 'COMPENSATION', name='transaction_type_enum'))
    amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(Enum('ONLINE', 'COD', 'WALLET', name='payment_method_enum'))
    
    # External payment details (for online payments)
    external_transaction_id = Column(String(100))  # Payment gateway transaction ID
    payment_gateway = Column(String(50))  # 'razorpay', 'stripe', etc.
    
    # Status tracking
    status = Column(Enum('PENDING', 'SUCCESS', 'FAILED', 'CANCELLED', name='transaction_status_enum'), default='PENDING')
    processed_at = Column(TIMESTAMP)
    failure_reason = Column(Text)
    
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    user_order = relationship("UserOrder")
    user = relationship("User")
