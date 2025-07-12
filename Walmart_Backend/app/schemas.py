from pydantic import BaseModel, EmailStr
from typing import Optional, List
from decimal import Decimal
from datetime import datetime
from .enums import BuddyStatus, OrderStatus, DriverStatus, DeliveryStatus

# User schemas
class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Product schemas
class ProductBase(BaseModel):
    name: str
    price: Decimal
    weight_grams: int
    stock: int = 0
    image_url: Optional[str] = None

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Cart schemas
class CartItemBase(BaseModel):
    product_id: str
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItemResponse(CartItemBase):
    id: str
    total_price: Decimal
    product: ProductResponse
    
    class Config:
        from_attributes = True

class CartItemUpdateQuantity(BaseModel):
    quantity: int

class CartItemRemove(BaseModel):
    success: bool
    message: str

class CartClearResponse(BaseModel):
    success: bool
    message: str
    items_removed: int

class CartResponse(BaseModel):
    id: str
    user_id: str
    is_active: bool
    created_at: datetime
    cart_items: List[CartItemResponse] = []
    
    class Config:
        from_attributes = True

# Buddy Queue schemas
class BuddyQueueCreate(BaseModel):
    cart_id: str
    lat: Decimal
    lng: Decimal
    timeout_minutes: int = 5  # Dynamic timeout with default of 5 minutes

class BuddyQueueResponse(BaseModel):
    id: str
    user_id: str
    status: BuddyStatus
    created_at: datetime
    timeout_minutes: int

    class Config:
        from_attributes = True

class ClubbedCartItem(BaseModel):
    product_name: str
    quantity: int
    price: float  # Changed from Decimal to float for frontend compatibility
    added_by_user: str

class ClubbedCartResponse(BaseModel):
    clubbed_order_id: str
    status: OrderStatus
    total_amount: float  # Changed from Decimal to float for frontend compatibility
    users: List[str]
    items: List[ClubbedCartItem]

    class Config:
        from_attributes = True

# Clubbed Order schemas
class ClubbedOrderResponse(BaseModel):
    id: str
    combined_value: Decimal
    combined_weight: Decimal
    total_discount: Decimal
    status: OrderStatus
    created_at: datetime
    
    class Config:
        from_attributes = True

class ClubbedOrderUserResponse(BaseModel):
    id: str
    clubbed_order_id: str
    user_id: str
    cart_id: str
    share_value: Decimal
    discount_given: Decimal
    
    class Config:
        from_attributes = True

class ClubbedOrderDetailResponse(BaseModel):
    id: str
    status: str
    clubbed_order_users: List[ClubbedOrderUserResponse] = []

# Driver schemas
class DriverBase(BaseModel):
    name: str
    max_capacity: Decimal = Decimal('5.0')

class DriverCreate(DriverBase):
    pass

class DriverResponse(DriverBase):
    id: str
    current_load: Decimal
    status: DriverStatus
    
    class Config:
        from_attributes = True

# Delivery schemas
class DeliveryResponse(BaseModel):
    id: str
    driver_id: str
    clubbed_order_id: str
    estimated_time_minutes: Optional[int] = None
    status: DeliveryStatus
    created_at: datetime
    driver: Optional[DriverResponse] = None
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Club readiness check
class ClubReadinessResponse(BaseModel):
    can_club: bool
    estimated_wait_time: int
    potential_discount: Decimal
    nearby_users_count: int

# Location schema
class LocationUpdate(BaseModel):
    lat: Decimal
    lng: Decimal
