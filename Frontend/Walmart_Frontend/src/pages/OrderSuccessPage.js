import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const OrderSuccessPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [orderDetails, setOrderDetails] = useState(location.state || null);
  const [loading, setLoading] = useState(!location.state);

  useEffect(() => {
    // If no state is passed (e.g. on refresh), redirect to home or show fallback
    if (!location.state) {
      // Optionally, you can fetch order details from backend here if you have an order ID
      setTimeout(() => {
        navigate('/', { replace: true });
      }, 1500);
    }
  }, [location.state, navigate]);

  const handleTrackOrder = () => {
    // Navigate to order tracking page
    window.location.href = '/order-tracking';
  };

  const handleContinueShopping = () => {
    window.location.href = '/products';
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="loading">
          <div className="spinner"></div>
          <div style={{ marginTop: 20, color: '#888' }}>Loading order details...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '20px' }}>
      <div className="card text-center">
        <div style={{ fontSize: '72px', marginBottom: '20px' }}>✅</div>
        <h1 style={{ color: '#28a745', marginBottom: '10px' }}>Order Confirmed!</h1>
        <p style={{ fontSize: '18px', color: '#666', marginBottom: '30px' }}>
          Thank you for your order. We're preparing it for delivery.
        </p>
        
        {orderDetails && (
          <>
            <div className="card" style={{ textAlign: 'left', marginBottom: '20px' }}>
              <h3>Order Details</h3>
              <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                <span>Order ID:</span>
                <span style={{ fontWeight: 'bold' }}>{orderDetails.id}</span>
              </div>
              <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                <span>Total Items:</span>
                <span>{orderDetails.items}</span>
              </div>
              <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                <span>Total Amount:</span>
                <span style={{ fontWeight: 'bold' }}>₹{orderDetails.total}</span>
              </div>
              <div className="d-flex justify-content-between">
                <span>Estimated Delivery:</span>
                <span style={{ color: '#007bff' }}>{orderDetails.estimatedDelivery}</span>
              </div>
            </div>

            {orderDetails.clubbed && (
              <div className="alert alert-success" style={{ textAlign: 'left' }}>
                <h4>🎉 Club & Save Success!</h4>
                <p>Your order was successfully clubbed with {orderDetails.buddyCount} other users!</p>
                <p><strong>You saved ₹{orderDetails.savings} on delivery fees!</strong></p>
                <p style={{ fontSize: '14px', margin: 0 }}>
                  Your order will be delivered together with other club members' orders.
                </p>
              </div>
            )}

            <div className="card" style={{ textAlign: 'left', marginBottom: '20px' }}>
              <h3>What's Next?</h3>
              <ul style={{ margin: 0, paddingLeft: '20px' }}>
                <li>Your order is being prepared</li>
                <li>You'll receive SMS updates on your order status</li>
                <li>A delivery partner will be assigned shortly</li>
                <li>You can track your order in real-time</li>
              </ul>
            </div>

            <div className="d-flex justify-content-center gap-3">
              <button onClick={handleTrackOrder} className="btn btn-primary">
                Track Order
              </button>
              <button onClick={handleContinueShopping} className="btn btn-secondary">
                Continue Shopping
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default OrderSuccessPage;
