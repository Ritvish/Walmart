"""
Sample data insertion script for BuddyCart
Run this after starting the server to populate with sample data
"""

import requests
import json
from decimal import Decimal

BASE_URL = "http://localhost:8000"

# Sample products data
sample_products = [
    {
        "name": "Fresh Bananas (1kg)",
        "price": 40.0,
        "weight_grams": 1000,
        "stock": 100,
        "image_url": "https://example.com/banana.jpg"
    },
    {
        "name": "Bread - Whole Wheat",
        "price": 35.0,
        "weight_grams": 400,
        "stock": 50,
        "image_url": "https://example.com/bread.jpg"
    },
    {
        "name": "Milk - Full Cream (1L)",
        "price": 55.0,
        "weight_grams": 1000,
        "stock": 30,
        "image_url": "https://example.com/milk.jpg"
    },
    {
        "name": "Eggs - Free Range (12 pcs)",
        "price": 90.0,
        "weight_grams": 600,
        "stock": 25,
        "image_url": "https://example.com/eggs.jpg"
    },
    {
        "name": "Rice - Basmati (1kg)",
        "price": 120.0,
        "weight_grams": 1000,
        "stock": 40,
        "image_url": "https://example.com/rice.jpg"
    },
    {
        "name": "Tomatoes (500g)",
        "price": 30.0,
        "weight_grams": 500,
        "stock": 60,
        "image_url": "https://example.com/tomatoes.jpg"
    },
    {
        "name": "Chicken Breast (500g)",
        "price": 180.0,
        "weight_grams": 500,
        "stock": 20,
        "image_url": "https://example.com/chicken.jpg"
    },
    {
        "name": "Yogurt - Greek Style",
        "price": 65.0,
        "weight_grams": 200,
        "stock": 35,
        "image_url": "https://example.com/yogurt.jpg"
    }
]

# Sample users
sample_users = [
    {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "password": "password123",
        "phone": "+91-9876543210",
        "address": "123 Park Street, Mumbai"
    },
    {
        "name": "Bob Smith",
        "email": "bob@example.com",
        "password": "password123",
        "phone": "+91-9876543211",
        "address": "456 Garden Road, Mumbai"
    },
    {
        "name": "Carol Brown",
        "email": "carol@example.com",
        "password": "password123",
        "phone": "+91-9876543212",
        "address": "789 Lake View, Mumbai"
    }
]

# Sample drivers
sample_drivers = [
    {
        "name": "Raj Kumar",
        "max_capacity": 5.0
    },
    {
        "name": "Suresh Patel",
        "max_capacity": 7.0
    },
    {
        "name": "Mohan Singh",
        "max_capacity": 4.5
    }
]

def register_user(user_data):
    """Register a new user"""
    response = requests.post(f"{BASE_URL}/auth/register", json=user_data)
    return response.json() if response.status_code == 200 else None

def login_user(email, password):
    """Login user and get token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "email": email,
        "password": password
    })
    return response.json() if response.status_code == 200 else None

def create_product(product_data, token):
    """Create a new product"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/products/", json=product_data, headers=headers)
    return response.json() if response.status_code == 200 else None

def main():
    print("🚀 Setting up BuddyCart with sample data...")
    
    # Register first user (admin)
    print("\n📝 Registering users...")
    admin_user = register_user(sample_users[0])
    if admin_user:
        print(f"✅ Registered admin user: {admin_user['email']}")
        
        # Login to get token
        login_response = login_user(sample_users[0]['email'], sample_users[0]['password'])
        if login_response:
            token = login_response['access_token']
            print("✅ Admin logged in successfully")
            
            # Create products
            print("\n🛍️  Creating sample products...")
            for product in sample_products:
                created_product = create_product(product, token)
                if created_product:
                    print(f"✅ Created product: {created_product['name']}")
                else:
                    print(f"❌ Failed to create product: {product['name']}")
        else:
            print("❌ Failed to login admin user")
    else:
        print("❌ Failed to register admin user")
    
    # Register other users
    for user in sample_users[1:]:
        registered_user = register_user(user)
        if registered_user:
            print(f"✅ Registered user: {registered_user['email']}")
        else:
            print(f"❌ Failed to register user: {user['email']}")
    
    print("\n🎉 Sample data setup complete!")
    print("\nNext steps:")
    print("1. Start your React frontend")
    print("2. Use the following test accounts:")
    for user in sample_users:
        print(f"   - Email: {user['email']}, Password: {user['password']}")
    print("3. Visit http://localhost:8000/docs for API documentation")

if __name__ == "__main__":
    main()
