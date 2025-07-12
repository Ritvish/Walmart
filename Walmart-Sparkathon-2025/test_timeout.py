#!/usr/bin/env python3
"""
Test script to verify timeout_minutes is being sent correctly
"""
import requests
import json

# Test data
test_data = {
    "cart_id": "test-cart-123",
    "lat": 37.7749,
    "lng": -122.4194,
    "timeout_minutes": 3  # Test with 3 minutes
}

# API endpoint
url = "http://localhost:8000/club/join-queue"

# You'll need to replace this with a valid JWT token
# For testing, you can get one by logging in first
headers = {
    "Content-Type": "application/json",
    # "Authorization": "Bearer YOUR_JWT_TOKEN_HERE"
}

print("Testing timeout_minutes parameter...")
print(f"Sending data: {json.dumps(test_data, indent=2)}")

try:
    response = requests.post(url, json=test_data, headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
except Exception as e:
    print(f"Error: {e}")
    
print("\nNote: This will fail without a valid JWT token, but it shows the request structure")
