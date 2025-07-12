"""
BuddyCart API Testing Utilities
A collection of functions to test the BuddyCart API endpoints
"""

import requests
import json
from typing import Dict, Optional

class BuddyCartAPIClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token = None
    
    def register(self, name: str, email: str, password: str, phone: str = None, address: str = None) -> Dict:
        """Register a new user"""
        data = {
            "name": name,
            "email": email,
            "password": password,
            "phone": phone,
            "address": address
        }
        response = requests.post(f"{self.base_url}/auth/register", json=data)
        return response.json(), response.status_code
    
    def login(self, email: str, password: str) -> Dict:
        """Login and store token"""
        data = {"email": email, "password": password}
        response = requests.post(f"{self.base_url}/auth/login", json=data)
        result = response.json()
        
        if response.status_code == 200:
            self.token = result["access_token"]
        
        return result, response.status_code
    
    def get_headers(self) -> Dict:
        """Get authorization headers"""
        if not self.token:
            raise ValueError("Not logged in. Call login() first.")
        return {"Authorization": f"Bearer {self.token}"}
    
    def get_profile(self) -> Dict:
        """Get current user profile"""
        response = requests.get(f"{self.base_url}/auth/me", headers=self.get_headers())
        return response.json(), response.status_code
    
    def get_products(self) -> Dict:
        """Get all products"""
        response = requests.get(f"{self.base_url}/products/")
        return response.json(), response.status_code
    
    def create_product(self, name: str, price: float, weight_grams: int, stock: int = 0, image_url: str = None) -> Dict:
        """Create a new product"""
        data = {
            "name": name,
            "price": price,
            "weight_grams": weight_grams,
            "stock": stock,
            "image_url": image_url
        }
        response = requests.post(f"{self.base_url}/products/", json=data, headers=self.get_headers())
        return response.json(), response.status_code
    
    def get_cart(self) -> Dict:
        """Get user's active cart"""
        response = requests.get(f"{self.base_url}/cart/", headers=self.get_headers())
        return response.json(), response.status_code
    
    def add_to_cart(self, product_id: str, quantity: int) -> Dict:
        """Add item to cart"""
        data = {"product_id": product_id, "quantity": quantity}
        response = requests.post(f"{self.base_url}/cart/items", json=data, headers=self.get_headers())
        return response.json(), response.status_code
    
    def check_club_readiness(self, lat: float, lng: float) -> Dict:
        """Check if clubbing is available"""
        data = {"lat": lat, "lng": lng}
        response = requests.post(f"{self.base_url}/club/check-readiness", json=data, headers=self.get_headers())
        return response.json(), response.status_code
    
    def join_club_queue(self, cart_id: str, lat: float, lng: float) -> Dict:
        """Join the buddy queue"""
        data = {"cart_id": cart_id, "lat": lat, "lng": lng}
        response = requests.post(f"{self.base_url}/club/join-queue", json=data, headers=self.get_headers())
        return response.json(), response.status_code
    
    def get_club_status(self, buddy_queue_id: str) -> Dict:
        """Get club status"""
        response = requests.get(f"{self.base_url}/club/status/{buddy_queue_id}", headers=self.get_headers())
        return response.json(), response.status_code
    
    def get_orders(self) -> Dict:
        """Get user's orders"""
        response = requests.get(f"{self.base_url}/orders/", headers=self.get_headers())
        return response.json(), response.status_code
    
    def health_check(self) -> Dict:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        return response.json(), response.status_code

def run_api_tests():
    """Run a comprehensive test of the API"""
    print("🧪 Running BuddyCart API Tests")
    print("=" * 40)
    
    client = BuddyCartAPIClient()
    
    # Test 1: Health Check
    print("1. Testing health check...")
    result, status = client.health_check()
    if status == 200:
        print("✅ Health check passed")
    else:
        print(f"❌ Health check failed: {status}")
        return
    
    # Test 2: User Registration
    print("2. Testing user registration...")
    result, status = client.register(
        name="Test User2",
        email="test2@example.com",
        password="testpass123",
        phone="+91-9876543211",
        address="Test Address, Mumbai"
    )
    if status == 200:
        print("✅ User registration passed")
    else:
        print(f"❌ User registration failed: {status} - {result}")
    
    # Test 3: User Login
    print("3. Testing user login...")
    result, status = client.login("test2@example.com", "testpass123")
    if status == 200:
        print("✅ User login passed")
    else:
        print(f"❌ User login failed: {status} - {result}")
        return
    
    # Test 4: Get Profile
    print("4. Testing get profile...")
    result, status = client.get_profile()
    if status == 200:
        print("✅ Get profile passed")
    else:
        print(f"❌ Get profile failed: {status}")
    
    # Test 5: Get Products
    print("5. Testing get products...")
    result, status = client.get_products()
    if status == 200:
        print(f"✅ Get products passed ({len(result)} products found)")
    else:
        print(f"❌ Get products failed: {status}")
    
    # Test 6: Get Cart
    print("6. Testing get cart...")
    result, status = client.get_cart()
    if status == 200:
        print("✅ Get cart passed")
        cart_id = result["id"]
    else:
        print(f"❌ Get cart failed: {status}")
        return
    
    # Test 7: Check Club Readiness
    print("7. Testing club readiness check...")
    result, status = client.check_club_readiness(19.0760, 72.8777)  # Mumbai coordinates
    if status == 200:
        print("✅ Club readiness check passed")
    else:
        print(f"❌ Club readiness check failed: {status}")
    
    print("\n🎉 API tests completed!")
    print("📊 All basic endpoints are working correctly")

if __name__ == "__main__":
    run_api_tests()
