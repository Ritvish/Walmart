# BuddyCart Frontend

A React.js frontend for the BuddyCart smart order clubbing system that helps users save delivery fees by joining with nearby users.

## 🚀 Features

- **User Authentication** - Login and registration system
- **Product Catalog** - Browse and search products
- **Smart Cart Management** - Add items and view cart summary
- **Club & Save** - Join with nearby users to save delivery fees
- **Real-time Matching** - Live status updates during club matching
- **Order Tracking** - Track your orders with real-time updates
- **Responsive Design** - Works on all devices

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd Walmart-Sparkathon-2025-Frontend
   ```

2. **Install dependencies**

   ```bash
   npm install
   ```

3. **Setup environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your API URL (default: http://localhost:8000)
   ```

4. **Start the development server**
   ```bash
   npm start
   ```

The app will be available at `http://localhost:3000`

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Header.js
│   ├── ProductCard.js
│   └── CartSummary.js
├── context/             # React Context for state management
│   ├── AuthContext.js
│   └── CartContext.js
├── pages/               # Page components
│   ├── HomePage.js
│   ├── LoginPage.js
│   ├── RegisterPage.js
│   ├── ProductPage.js
│   ├── CartPage.js
│   ├── ClubMatchingPage.js
│   ├── CheckoutPage.js
│   ├── OrderSuccessPage.js
│   └── OrderTrackingPage.js
├── services/            # API service layers
│   ├── api.js
│   ├── authService.js
│   ├── productService.js
│   ├── cartService.js
│   ├── clubService.js
│   └── orderService.js
├── App.js               # Main app component with routing
├── index.js             # App entry point
└── index.css           # Global styles
```

## 🔧 API Configuration

The frontend communicates with the FastAPI backend through the services layer:

- **Base URL**: Configured in `.env` file
- **Authentication**: JWT tokens stored in localStorage
- **Error Handling**: Global error interceptors
- **Request/Response**: Axios for HTTP requests

## 🌟 Key Features

### 1. Authentication System

- JWT-based authentication
- Persistent login state
- Protected routes
- Auto-redirect on token expiry

### 2. Smart Cart Management

- Add items to cart
- Real-time cart updates
- Cart persistence across sessions
- Weight and price calculations

### 3. Club & Save Flow

- Location-based matching
- Real-time status updates
- Countdown timers
- Savings calculations

### 4. Order Management

- Order confirmation
- Real-time tracking
- Delivery partner details
- Status timeline

## 📱 Pages Overview

1. **Landing Page** - Welcome and feature overview
2. **Login/Register** - User authentication
3. **Product Catalog** - Browse and search products
4. **Cart** - View cart and initiate Club & Save
5. **Club Matching** - Real-time buddy matching
6. **Checkout** - Order placement and payment
7. **Order Success** - Confirmation and details
8. **Order Tracking** - Real-time delivery tracking

## 🛠️ Development

### Available Scripts

- `npm start` - Start development server
- `npm build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

### Code Organization

- **Services**: API calls and business logic
- **Context**: Global state management
- **Components**: Reusable UI elements
- **Pages**: Route-based page components

## 🔧 Configuration

### Environment Variables

```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=BuddyCart
REACT_APP_VERSION=1.0.0
```

### Dependencies

- **React Router** - Client-side routing
- **Axios** - HTTP client
- **React Hot Toast** - Toast notifications
- **React Icons** - Icon library
- **Lucide React** - Modern icons

## 🚀 Production Deployment

1. **Build the app**

   ```bash
   npm run build
   ```

2. **Deploy to your hosting service**
   - Vercel: `vercel --prod`
   - Netlify: Drag & drop `build` folder
   - AWS S3: Upload `build` folder contents

## 🔗 API Integration

The frontend expects the following API endpoints:

- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `GET /auth/me` - Get current user
- `GET /products/` - Get all products
- `GET /cart/` - Get user's cart
- `POST /cart/items` - Add item to cart
- `POST /club/check-readiness` - Check club availability
- `POST /club/join-queue` - Join buddy queue
- `GET /club/status/{id}` - Get club status

## 📝 Notes

- Make sure the FastAPI backend is running on port 8000
- Location permission is required for Club & Save features
- The app uses localStorage for authentication persistence
- All API calls include proper error handling and user feedback

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
