BuddyCart is a smart order clubbing system designed to help users with low-value carts save delivery fees by anonymously merging their orders with others nearby. It enables real-time user matching, combined cart summaries, and load-aware delivery agent assignment—offering better savings for customers and greater efficiency for delivery platforms.

## 🚀 Quick Start

### Setup Instructions

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Walmart-Sparkathon-2025

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment variables
cp .env.example .env
# Edit .env with your database credentials

# 4. Start the server
python main.py

# 5. Optional: Load sample data
python setup_sample_data.py
```

### Testing Your Setup

```bash
# Run the test suite
python test_setup.py

# Run API tests
python api_tester.py

# Start the server manually
./start_server.sh
```

## 📁 Project Structure

```
├── app/
│   ├── __init__.py
│   ├── models.py          # SQLAlchemy database models
│   ├── schemas.py         # Pydantic data models
│   ├── database.py        # Database configuration
│   ├── auth.py           # Authentication utilities
│   ├── crud.py           # Database operations
│   └── routers/
│       ├── __init__.py
│       ├── auth.py       # Authentication endpoints
│       ├── products.py   # Product management
│       ├── cart.py       # Shopping cart operations
│       ├── club.py       # Club & Save functionality
│       └── orders.py     # Order management
├── main.py               # FastAPI application entry point
├── requirements.txt      # Python dependencies
├── .env                 # Environment variables
├── .env.example         # Environment variables template
├── setup_sample_data.py # Sample data loader
├── api_tester.py        # API testing utilities
├── test_setup.py        # Setup validation script
└── start_server.sh      # Server startup script
```

## 🛠️ API Endpoints

### Authentication

- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile

### Products

- `GET /products/` - List all products
- `GET /products/{id}` - Get product details
- `POST /products/` - Create new product

### Cart Management

- `GET /cart/` - Get user's active cart
- `POST /cart/items` - Add item to cart
- `GET /cart/{cart_id}` - Get cart details

### Club & Save

- `POST /club/check-readiness` - Check club availability
- `POST /club/join-queue` - Join buddy queue
- `GET /club/status/{id}` - Get club status

### Orders

- `GET /orders/` - Get user's order history
- `GET /orders/{id}` - Get order details
- `GET /orders/{id}/delivery` - Get delivery status

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

---

—

✅ Key Features (Without ML):

Real-Time Club Readiness Heuristics

When a user has a low cart value, the system checks if others nearby have also started shopping recently (based on time slots and location).

If conditions are favorable, the user is prompted to “Club & Save” instead of paying full delivery charges.

Anonymous BuddyCart Opt-In Flow

Users can choose to wait briefly and club their orders with nearby users.

No cart contents or identities are revealed—only the combined cart value and applicable discount are shown.

Dynamic Cart Matching Engine

Aggregates opt-in users from the same location cluster within a short time window (e.g., 5 minutes).

Combines carts if the total weight remains under a predefined threshold (e.g., 5 kg).

Ensures user pairing maintains delivery feasibility and fairness.

Combined Cart Summary

After clubbing, each user sees:

Combined cart value (e.g., ₹420)

Total discount unlocked (e.g., ₹60)

Their individual contribution and saved amount

Delivery Agent Assignment Based on Load Capacity

Delivery agents are assigned orders based on their maximum carrying capacity.

If the combined order nearly fills the capacity, the driver is assigned only those orders.

If capacity remains, the system continues adding smaller nearby orders until fully optimized.

Simple Rule-Based Discount Logic

Based on combined cart value thresholds:

₹300+ → ₹30 discount

₹500+ → ₹60 discount

These thresholds encourage users to join in and increase total order size collaboratively.

FastAPI + React (or Flutter) Integration

Backend handles cart submission, readiness check, cart pooling, and driver dispatch.

Frontend provides a simple UI with a “Club & Save” prompt, a short wait timer, and confirmation screens.

—

📈 Impact & Outcomes:

Significant savings on delivery for users with small orders

Increased average order value without forcing users to add unnecessary items

Reduced number of delivery trips by grouping nearby orders

Improved last-mile efficiency for platforms like Flipkart Quick or Instamart-type models

—

1.⁠ ⁠Landing Page
2.⁠ ⁠Login / Register Page
3.⁠ ⁠Product Page / Add to Cart
4.⁠ ⁠Club Matchmaking Page
5.⁠ ⁠Clubbed Cart Page (combined wala)
6.⁠ ⁠Checkout Page
7.⁠ ⁠Order Success / Tracking Page

🚀 BuddyCart MySQL Schema:

CREATE TABLE users (
id VARCHAR(36) PRIMARY KEY,
name VARCHAR(100) NOT NULL,
email VARCHAR(100) UNIQUE NOT NULL,
password_hash TEXT NOT NULL,
phone VARCHAR(20),
address TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
id VARCHAR(36) PRIMARY KEY,
name VARCHAR(100) NOT NULL,
price DECIMAL(10,2) NOT NULL,
weight_grams INT NOT NULL,
stock INT DEFAULT 0,
image_url TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE carts (
id VARCHAR(36) PRIMARY KEY,
user_id VARCHAR(36),
is_active BOOLEAN DEFAULT TRUE,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE cart_items (
id VARCHAR(36) PRIMARY KEY,
cart_id VARCHAR(36),
product_id VARCHAR(36),
quantity INT NOT NULL,
total_price DECIMAL(10,2),
FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE TABLE buddy_queue (
id VARCHAR(36) PRIMARY KEY,
user_id VARCHAR(36),
cart_id VARCHAR(36),
value_total DECIMAL(10,2) NOT NULL,
weight_total DECIMAL(10,2) NOT NULL,
lat DECIMAL(9,6) NOT NULL,
lng DECIMAL(9,6) NOT NULL,
location_hash VARCHAR(20),
status ENUM('waiting', 'matched', 'timed_out') DEFAULT 'waiting',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE
);

CREATE TABLE clubbed_orders (
id VARCHAR(36) PRIMARY KEY,
combined_value DECIMAL(10,2),
combined_weight DECIMAL(10,2),
total_discount DECIMAL(10,2),
status ENUM('created', 'preparing', 'dispatched', 'delivered') DEFAULT 'created',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE clubbed_order_users (
id VARCHAR(36) PRIMARY KEY,
clubbed_order_id VARCHAR(36),
user_id VARCHAR(36),
cart_id VARCHAR(36),
share_value DECIMAL(10,2),
discount_given DECIMAL(10,2),
FOREIGN KEY (clubbed_order_id) REFERENCES clubbed_orders(id) ON DELETE CASCADE,
FOREIGN KEY (user_id) REFERENCES users(id),
FOREIGN KEY (cart_id) REFERENCES carts(id)
);

CREATE TABLE drivers (
id VARCHAR(36) PRIMARY KEY,
name VARCHAR(100),
max_capacity DECIMAL(10,2) DEFAULT 5.0,
current_load DECIMAL(10,2) DEFAULT 0.0,
status ENUM('available', 'busy', 'inactive') DEFAULT 'available'
);

CREATE TABLE deliveries (
id VARCHAR(36) PRIMARY KEY,
driver_id VARCHAR(36),
clubbed_order_id VARCHAR(36),
estimated_time_minutes INT,
status ENUM('assigned', 'in_transit', 'delivered') DEFAULT 'assigned',
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
FOREIGN KEY (driver_id) REFERENCES drivers(id),
FOREIGN KEY (clubbed_order_id) REFERENCES clubbed_orders(id)
);

Optional Indexes for Location-Based Matching:

CREATE INDEX idx_buddy_location ON buddy_queue (lat, lng);

Let me know if you'd like:

INSERT statements for sample users/products

SQL dump file (.sql) ready for import

Diagram of the schema (ERD)

ORM version (e.g., Sequelize or Prisma schema)
