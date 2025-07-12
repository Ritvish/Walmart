import requests
import time
from api_tester import BuddyCartAPIClient

def run_clubbing_test():
    print("🧪 Running Clubbing Test")
    print("=" * 40)

    # Create two clients for two users
    client1 = BuddyCartAPIClient()
    client2 = BuddyCartAPIClient()

    # --- User 1 ---
    print("\n--- User 1 Operations ---")
    # Register User 1
    print("1. Registering User 1...")
    result, status = client1.register("ClubUser1", "clubuser1@example.com", "password123")
    if status != 200 and status != 400: # 400 for already exists
        print(f"❌ User 1 registration failed: {status} - {result}")
        return
    print("✅ User 1 registered or already exists.")

    # Login User 1
    print("2. Logging in User 1...")
    result, status = client1.login("clubuser1@example.com", "password123")
    if status != 200:
        print(f"❌ User 1 login failed: {status} - {result}")
        return
    print("✅ User 1 logged in.")

    # Get products to add to cart
    products, status = client1.get_products()
    if status != 200 or not products:
        print("❌ Could not get products.")
        return
    product_id = products[0]['id']

    # Add item to cart for User 1
    print(f"3. Adding product {product_id} to User 1's cart...")
    result, status = client1.add_to_cart(product_id, 1)
    if status != 200:
        print(f"❌ Failed to add item to cart for User 1: {status} - {result}")
        return
    print("✅ Item added to User 1's cart.")
    cart1, status = client1.get_cart()
    cart1_id = cart1['id']
    cart1_total_price = sum(float(item['total_price']) for item in cart1['cart_items'])
    print(f"User 1 Cart ID: {cart1_id}, Total Price: {cart1_total_price}")


    # --- User 2 ---
    print("\n--- User 2 Operations ---")
    # Register User 2
    print("1. Registering User 2...")
    result, status = client2.register("ClubUser2", "clubuser2@example.com", "password123")
    if status != 200 and status != 400:
        print(f"❌ User 2 registration failed: {status} - {result}")
        return
    print("✅ User 2 registered or already exists.")

    # Login User 2
    print("2. Logging in User 2...")
    result, status = client2.login("clubuser2@example.com", "password123")
    if status != 200:
        print(f"❌ User 2 login failed: {status} - {result}")
        return
    print("✅ User 2 logged in.")

    # Add item to cart for User 2
    print(f"3. Adding product {product_id} to User 2's cart...")
    result, status = client2.add_to_cart(product_id, 1)
    if status != 200:
        print(f"❌ Failed to add item to cart for User 2: {status} - {result}")
        return
    print("✅ Item added to User 2's cart.")
    cart2, status = client2.get_cart()
    cart2_id = cart2['id']
    cart2_total_price = sum(float(item['total_price']) for item in cart2['cart_items'])
    print(f"User 2 Cart ID: {cart2_id}, Total Price: {cart2_total_price}")


    # --- Clubbing ---
    print("\n--- Clubbing Operations ---")
    # User 1 joins queue
    print("1. User 1 joining club queue...")
    # Coordinates for Mumbai
    lat1, lng1 = 19.0760, 72.8777
    join_data1 = {
        "cart_id": cart1_id,
        "lat": lat1,
        "lng": lng1,
        "timeout_minutes": 5
    }
    response = requests.post(f"{client1.base_url}/club/join-queue", json=join_data1, headers=client1.get_headers())
    result1, status1 = response.json(), response.status_code

    if status1 != 200:
        print(f"❌ User 1 failed to join queue: {status1} - {result1}")
        return
    buddy_queue_id1 = result1['id']
    print(f"✅ User 1 joined queue with BuddyQueue ID: {buddy_queue_id1}")


    # User 2 joins queue
    print("2. User 2 joining club queue...")
    # Slightly different coordinates, but still close
    lat2, lng2 = 19.0765, 72.8780
    join_data2 = {
        "cart_id": cart2_id,
        "lat": lat2,
        "lng": lng2,
        "timeout_minutes": 5
    }
    response = requests.post(f"{client2.base_url}/club/join-queue", json=join_data2, headers=client2.get_headers())
    result2, status2 = response.json(), response.status_code

    if status2 != 200:
        print(f"❌ User 2 failed to join queue: {status2} - {result2}")
        return
    buddy_queue_id2 = result2['id']
    print(f"✅ User 2 joined queue with BuddyQueue ID: {buddy_queue_id2}")

    # --- Check Status ---
    print("\n--- Checking Club Status ---")
    print("Waiting for 10 seconds for backend processing...")
    time.sleep(10)

    print(f"Checking status for User 1 (BuddyQueue ID: {buddy_queue_id1})...")
    status_result1, status_code1 = client1.get_club_status(buddy_queue_id1)
    print(f"User 1 Status: {status_result1} (HTTP {status_code1})")

    print(f"Checking status for User 2 (BuddyQueue ID: {buddy_queue_id2})...")
    status_result2, status_code2 = client2.get_club_status(buddy_queue_id2)
    print(f"User 2 Status: {status_result2} (HTTP {status_code2})")

    if status_result1.get('status') == 'matched' and status_result2.get('status') == 'matched':
        print("\n🎉🎉🎉 SUCCESS: Both users were matched!")
        print(f"User 1 Clubbed Order ID: {status_result1.get('clubbed_order_id')}")
        print(f"User 2 Clubbed Order ID: {status_result2.get('clubbed_order_id')}")
    else:
        print("\n❌❌❌ FAILURE: Users were not matched.")

if __name__ == "__main__":
    run_clubbing_test()
