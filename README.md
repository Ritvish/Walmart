# 🛒 BuddyCart - Smart Group Shopping Platform

**BuddyCart** is an innovative e-commerce platform that enables users to combine their shopping carts with nearby shoppers to unlock group discounts and optimize delivery costs. Built for the Walmart Sparkathon 2025.

## 🌟 Features

### 🤝 Smart Cart Clubbing
- **Location-based Matching**: Find nearby shoppers in your area (within 5km radius)
- **Real-time Queue System**: Join a buddy queue and get matched instantly
- **Dynamic Timeouts**: Configurable wait times for optimal matching
- **Compatibility Algorithm**: Smart matching based on location, cart value, and delivery preferences

### 💰 Group Benefits
- **Automatic Discounts**: 5% discount when carts are successfully clubbed
- **Shared Delivery**: Reduced delivery costs through optimized routing
- **Flexible Shopping**: Add more items to your cart even after matching

### 📱 User Experience
- **Seamless Authentication**: Secure JWT-based login system
- **Real-time Updates**: Live status updates on matching progress
- **Intuitive Interface**: Clean, responsive React frontend
- **Progress Tracking**: Visual feedback on nearby users and estimated match time

### 🔒 Privacy & Security
- **Anonymized User Data**: Other users are identified only as "User 1", "User 2", etc.
- **Hidden Shopping Details**: Individual items from other users' carts are never displayed
- **Aggregated Totals**: Only combined cart values and item counts are shared
- **Secure Data Handling**: Personal information and shopping patterns remain private
- **Privacy-First Design**: Users can collaborate without compromising individual privacy

## 🏗️ Architecture

### Backend (FastAPI + Python)
- **Framework**: FastAPI with async support
- **Database**: MySQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with secure password hashing
- **Background Tasks**: Celery-style background processing for matching
- **API Documentation**: Auto-generated OpenAPI/Swagger docs

### Frontend (React)
- **Framework**: React 18 with modern hooks
- **Routing**: React Router v6
- **State Management**: Context API for auth and cart management
- **Styling**: Bootstrap 5 for responsive design
- **Notifications**: React Hot Toast for user feedback

## 📁 Project Structure

```
walmart/
├── 📁 Walmart-Sparkathon-2025/          # Backend (FastAPI)
│   ├── 📁 app/
│   │   ├── __init__.py
│   │   ├── main.py                       # FastAPI app entry point
│   │   ├── database.py                   # Database configuration
│   │   ├── models.py                     # SQLAlchemy models
│   │   ├── schemas.py                    # Pydantic schemas
│   │   ├── auth.py                       # Authentication logic
│   │   ├── crud.py                       # Database operations
│   │   ├── enums.py                      # Status enums
│   │   └── 📁 routers/
│   │       ├── auth.py                   # Authentication routes
│   │       ├── products.py               # Product management
│   │       ├── cart.py                   # Cart operations
│   │       ├── club.py                   # Buddy clubbing logic
│   │       ├── clubbed_cart.py           # Combined cart management
│   │       └── orders.py                 # Order processing
│   ├── requirements.txt                  # Python dependencies
│   ├── database_setup.sql               # Database schema
│   └── .env                             # Environment variables
│
├── 📁 Walmart Frontend/
│   └── 📁 Walmart-Sparkathon-2025-Frontend/  # Frontend (React)
│       ├── 📁 public/
│       ├── 📁 src/
│       │   ├── App.js                    # Main app component
│       │   ├── index.js                  # React entry point
│       │   ├── 📁 components/
│       │   │   ├── Header.js
│       │   │   ├── ProductCard.js
│       │   │   └── CartSummary.js
│       │   ├── 📁 pages/
│       │   │   ├── HomePage.js
│       │   │   ├── LoginPage.js
│       │   │   ├── RegisterPage.js
│       │   │   ├── ProductPage.js
│       │   │   ├── CartPage.js
│       │   │   ├── ClubMatchingPage.js
│       │   │   ├── ClubbedCartPage.js
│       │   │   └── CheckoutPage.js
│       │   ├── 📁 context/
│       │   │   ├── AuthContext.js
│       │   │   └── CartContext.js
│       │   └── 📁 services/
│       │       ├── api.js
│       │       ├── authService.js
│       │       ├── cartService.js
│       │       ├── clubService.js
│       │       └── productService.js
│       ├── package.json
│       └── .env
│
├── .gitignore                           # Git ignore rules
└── README.md                           # This file
```

## 🚀 Getting Started

### Prerequisites
- **Python 3.9+**
- **Node.js 16+**
- **MySQL 8.0+**
- **npm or yarn**

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd Walmart-Sparkathon-2025
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup database**
   ```bash
   # Create MySQL database
   mysql -u root -p
   CREATE DATABASE buddycart;
   
   # Import schema
   mysql -u root -p buddycart < database_setup.sql
   
   # Add sample data
   python setup_sample_data.py
   ```

5. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials
   ```

6. **Start the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd "Walmart Frontend/Walmart-Sparkathon-2025-Frontend"
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API endpoint
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

## 🔧 Configuration

### Backend Environment Variables (.env)
```env
DATABASE_URL=mysql+mysqlconnector://root:password@localhost:3307/buddycart
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
CLUB_WAIT_TIME_MINUTES=5
MAX_DELIVERY_WEIGHT_KG=5.0
LOCATION_CLUSTER_RADIUS_KM=2.0
```

### Frontend Environment Variables (.env)
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=BuddyCart
```

## 📊 Database Schema

### Core Tables
- **users**: User authentication and profile data
- **products**: Product catalog with pricing and inventory
- **carts**: Individual user shopping carts
- **cart_items**: Items within each cart
- **buddy_queue**: Users waiting for cart matching
- **clubbed_orders**: Combined orders from matched users
- **clubbed_order_users**: User associations with clubbed orders
- **drivers**: Delivery driver information
- **deliveries**: Delivery assignments and tracking

## 🔄 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user profile

### Products
- `GET /products` - List all products
- `GET /products/{product_id}` - Get product details

### Cart Management
- `GET /cart` - Get user's cart
- `POST /cart/items` - Add item to cart
- `PUT /cart/items/{item_id}` - Update cart item
- `DELETE /cart/items/{item_id}` - Remove cart item

### Club & Save
- `POST /club/check-readiness` - Check if location supports clubbing
- `POST /club/join-queue` - Join buddy matching queue
- `GET /club/status/{buddy_queue_id}` - Check matching status
- `GET /club/detailed-status/{buddy_queue_id}` - Get detailed status with metrics

### Clubbed Cart
- `GET /clubbed-cart/{clubbed_order_id}` - Get combined cart details
- `POST /clubbed-cart/{clubbed_order_id}/items` - Add items to clubbed cart

## 🧪 Testing

### Backend Tests
```bash
# Run all tests
python -m pytest

# Run specific test files
python test_clubbing.py
python test_mysql_connection.py
```

### Frontend Tests
```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage
```

## 🔒 Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **CORS Protection**: Configurable CORS origins
- **Input Validation**: Pydantic schemas for request validation
- **SQL Injection Prevention**: SQLAlchemy ORM with parameterized queries

## 📈 Performance Optimizations

- **Database Indexing**: Optimized queries for location-based searches
- **Connection Pooling**: Efficient database connection management
- **Caching**: Strategic caching for frequently accessed data
- **Async Processing**: Non-blocking background tasks for matching
- **Lazy Loading**: Efficient React component loading

## 🚀 Deployment

### Backend Deployment
```bash
# Using Docker
docker build -t buddycart-backend .
docker run -p 8000:8000 buddycart-backend

# Using Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment
```bash
# Build for production
npm run build

# Deploy to static hosting
# (Netlify, Vercel, AWS S3, etc.)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Backend API Documentation](http://localhost:8000/docs)
- [Frontend Application](http://localhost:3000)
- [GitHub Repository](https://github.com/Ritvish/Walmart)

