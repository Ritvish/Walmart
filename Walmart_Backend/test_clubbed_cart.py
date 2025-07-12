#!/usr/bin/env python3
"""
Test script for clubbed cart functionality
"""
import sys
import os
sys.path.append(os.getcwd())

from app.database import get_db
from app.crud import (
    get_user_by_email, 
    get_active_cart, 
    create_clubbed_order, 
    get_clubbed_order_details,
    add_item_to_clubbed_cart
)
from app.models import BuddyQueue, ClubbedOrder, ClubbedOrderUser
from app.enums import BuddyStatus, OrderStatus
from app.schemas import CartItemCreate
from datetime import datetime

def test_clubbed_cart():
    print("🧪 Testing Clubbed Cart Functionality")
    print("=" * 50)
    
    db = next(get_db())
    
    # Check if we have any users
    from app.models import User
    users = db.query(User).limit(2).all()
    print(f"👥 Found {len(users)} users")
    
    if len(users) < 2:
        print("❌ Need at least 2 users to test clubbed cart")
        return
    
    # Create fake buddy queue entries for testing
    buddy1 = BuddyQueue(
        id="test-buddy-1",
        user_id=users[0].id,
        cart_id="test-cart-1",
        value_total=100.0,
        weight_total=2.0,
        lat=40.7128,
        lng=-74.0060,
        location_hash="test-hash",
        status=BuddyStatus.WAITING.value,
        timeout_minutes=5,
        created_at=datetime.utcnow()
    )
    
    buddy2 = BuddyQueue(
        id="test-buddy-2",
        user_id=users[1].id,
        cart_id="test-cart-2",
        value_total=150.0,
        weight_total=3.0,
        lat=40.7129,
        lng=-74.0061,
        location_hash="test-hash",
        status=BuddyStatus.WAITING.value,
        timeout_minutes=5,
        created_at=datetime.utcnow()
    )
    
    # Clean up any existing test data
    db.query(BuddyQueue).filter(BuddyQueue.id.in_(["test-buddy-1", "test-buddy-2"])).delete()
    db.query(ClubbedOrder).filter(ClubbedOrder.id.like("test-%")).delete()
    db.commit()
    
    # Add test buddies
    db.add(buddy1)
    db.add(buddy2)
    db.commit()
    
    print(f"✅ Created test buddy entries")
    
    # Test creating a clubbed order
    try:
        clubbed_order = create_clubbed_order(db, [buddy1, buddy2])
        print(f"✅ Created clubbed order: {clubbed_order.id}")
        print(f"   Status: {clubbed_order.status}")
        print(f"   Combined Value: {clubbed_order.combined_value}")
        print(f"   Combined Weight: {clubbed_order.combined_weight}")
        print(f"   Total Discount: {clubbed_order.total_discount}")
        
        # Test getting clubbed order details
        order_details, users_in_order, items = get_clubbed_order_details(
            db, clubbed_order.id, users[0].id
        )
        
        if order_details:
            print(f"✅ Retrieved clubbed order details")
            print(f"   Users in order: {len(users_in_order)}")
            print(f"   Items in order: {len(items)}")
        else:
            print("❌ Could not retrieve clubbed order details")
            
    except Exception as e:
        print(f"❌ Error creating clubbed order: {e}")
        import traceback
        traceback.print_exc()
    
    # Clean up
    db.query(BuddyQueue).filter(BuddyQueue.id.in_(["test-buddy-1", "test-buddy-2"])).delete()
    db.query(ClubbedOrderUser).filter(ClubbedOrderUser.clubbed_order_id.like("test-%")).delete()
    db.query(ClubbedOrder).filter(ClubbedOrder.id.like("test-%")).delete()
    db.commit()
    
    print("\n✅ Clubbed cart test completed!")

if __name__ == "__main__":
    test_clubbed_cart()
