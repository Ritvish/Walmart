# BuddyCart FastAPI Server

A FastAPI backend server for the BuddyCart smart order clubbing system.

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Copy the `.env` file and update with your database credentials:

```bash
cp .env .env.local
```

Update the following variables in `.env`:

- `DATABASE_URL`: Your MySQL connection string
- `SECRET_KEY`: A secure secret key for JWT tokens
- Other configuration values as needed

### 3. Database Setup

Make sure you have MySQL installed and create a database named `buddycart`:

```sql
CREATE DATABASE buddycart;
```

The tables will be created automatically when you start the server.

### 4. Run the Server

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

### Authentication

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login and get access token
- `GET /auth/me` - Get current user info

### Products

- `GET /products/` - Get all products
- `GET /products/{product_id}` - Get specific product
- `POST /products/` - Create new product (admin)

### Cart

- `GET /cart/` - Get user's active cart
- `POST /cart/items` - Add item to cart
- `GET /cart/{cart_id}` - Get cart by ID

### Club & Save

- `POST /club/check-readiness` - Check if clubbing is available
- `POST /club/join-queue` - Join the buddy queue
- `GET /club/status/{buddy_queue_id}` - Get club status

### Orders

- `GET /orders/` - Get user's order history
- `GET /orders/{order_id}` - Get order details
- `GET /orders/{order_id}/delivery` - Get delivery status

## Features Implemented

1. **User Authentication** - JWT-based auth with registration/login
2. **Product Management** - CRUD operations for products
3. **Shopping Cart** - Add items, manage cart
4. **Smart Clubbing** - Location-based order matching
5. **Order Management** - Track clubbed orders and deliveries
6. **Driver Assignment** - Automatic driver allocation based on capacity

## Architecture

- **FastAPI** for the web framework
- **SQLAlchemy** for database ORM
- **MySQL** for data storage
- **JWT** for authentication
- **Pydantic** for data validation
- **Background tasks** for order matching

## Database Schema

The server implements the complete MySQL schema defined in the README, including:

- Users and authentication
- Products and inventory
- Shopping carts and items
- Buddy queue for order matching
- Clubbed orders and user associations
- Drivers and delivery management

## Development

The server includes:

- Automatic table creation on startup
- CORS middleware for frontend integration
- Background tasks for order processing
- Comprehensive error handling
- Input validation with Pydantic models
