import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import toast from 'react-hot-toast';

const CheckoutPage = () => {
  const { cart, clearCart } = useCart();
  const navigate = useNavigate();
  const [processing, setProcessing] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [orderDetails, setOrderDetails] = useState({
    address: '',
    phone: '',
    notes: '',
  });

  const handleInputChange = (e) => {
    setOrderDetails({
      ...orderDetails,
      [e.target.name]: e.target.value,
    });
  };

  const handlePlaceOrder = async () => {
    if (!orderDetails.address || !orderDetails.phone) {
      toast.error('Please fill in all required fields');
      return;
    }

    setProcessing(true);
    try {
      // Simulate order processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      toast.success('Order placed successfully!');
      clearCart();
      // Pass order details (including total) to order-success page
      navigate('/order-success', {
        state: {
          id: 'ORDER-' + Date.now(),
          total: total,
          items: cart.cart_items.length,
          estimatedDelivery: '20-30 minutes',
          savings: 35.00, // You may want to calculate this dynamically
          clubbed: true, // You may want to set this based on logic
          buddyCount: 2, // You may want to set this based on logic
        },
      });
    } catch (error) {
      toast.error('Failed to place order');
      setProcessing(false);
    }
  };

  if (!cart || !cart.cart_items || cart.cart_items.length === 0) {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <h2>Your cart is empty</h2>
          <p>Add some items to proceed with checkout</p>
          <a href="/products" className="btn btn-primary">
            Continue Shopping
          </a>
        </div>
      </div>
    );
  }

  const subtotal = cart.cart_items.reduce((sum, item) => sum + parseFloat(item.total_price || 0), 0);
  const deliveryFee = 40;
  const total = subtotal + deliveryFee;

  return (
    <div className="container" style={{ padding: '20px' }}>
      <h1 style={{ marginBottom: '20px' }}>Checkout</h1>
      
      <div className="grid grid-2">
        <div>
          <div className="card">
            <h3>Delivery Information</h3>
            
            <div className="form-group">
              <label className="form-label">Delivery Address *</label>
              <textarea
                name="address"
                value={orderDetails.address}
                onChange={handleInputChange}
                className="form-control"
                placeholder="Enter your complete delivery address"
                rows="3"
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Phone Number *</label>
              <input
                type="tel"
                name="phone"
                value={orderDetails.phone}
                onChange={handleInputChange}
                className="form-control"
                placeholder="Enter your phone number"
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label">Special Instructions</label>
              <textarea
                name="notes"
                value={orderDetails.notes}
                onChange={handleInputChange}
                className="form-control"
                placeholder="Any special delivery instructions"
                rows="2"
              />
            </div>
          </div>
          
          <div className="card">
            <h3>Payment Method</h3>
            
            <div style={{ marginBottom: '16px' }}>
              <label className="d-flex align-items-center">
                <input
                  type="radio"
                  name="paymentMethod"
                  value="card"
                  checked={paymentMethod === 'card'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  style={{ marginRight: '8px' }}
                />
                Credit/Debit Card
              </label>
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <label className="d-flex align-items-center">
                <input
                  type="radio"
                  name="paymentMethod"
                  value="upi"
                  checked={paymentMethod === 'upi'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  style={{ marginRight: '8px' }}
                />
                UPI Payment
              </label>
            </div>
            
            <div style={{ marginBottom: '16px' }}>
              <label className="d-flex align-items-center">
                <input
                  type="radio"
                  name="paymentMethod"
                  value="cod"
                  checked={paymentMethod === 'cod'}
                  onChange={(e) => setPaymentMethod(e.target.value)}
                  style={{ marginRight: '8px' }}
                />
                Cash on Delivery
              </label>
            </div>
          </div>
        </div>
        
        <div>
          <div className="card">
            <h3>Order Summary</h3>
            
            <div style={{ marginBottom: '20px' }}>
              {cart.cart_items.map((item) => (
                <div key={item.id} className="d-flex justify-content-between align-items-center" style={{ marginBottom: '12px' }}>
                  <div>
                    <div style={{ fontWeight: '600' }}>{item.product.name}</div>
                    <div style={{ fontSize: '14px', color: '#666' }}>
                      Qty: {item.quantity}
                    </div>
                  </div>
                  <div style={{ fontWeight: '600' }}>
                    ₹{parseFloat(item.total_price || 0).toFixed(2)}
                  </div>
                </div>
              ))}
            </div>
            
            <div style={{ borderTop: '1px solid #eee', paddingTop: '16px' }}>
              <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                <span>Subtotal:</span>
                <span>₹{subtotal.toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                <span>Delivery Fee:</span>
                <span>₹{deliveryFee.toFixed(2)}</span>
              </div>
              <div className="d-flex justify-content-between" style={{ fontSize: '18px', fontWeight: 'bold' }}>
                <span>Total:</span>
                <span>₹{total.toFixed(2)}</span>
              </div>
            </div>
            
            <button
              onClick={handlePlaceOrder}
              disabled={processing}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '20px' }}
            >
              {processing ? 'Processing...' : `Place Order - ₹${total.toFixed(2)}`}
            </button>
          </div>
          
          <div className="card">
            <h3>Delivery Information</h3>
            <p>
              <strong>Estimated Delivery Time:</strong> 15-30 minutes
            </p>
            <p>
              <strong>Delivery Partner:</strong> Will be assigned after order confirmation
            </p>
            <p style={{ fontSize: '14px', color: '#666' }}>
              You'll receive SMS and email updates about your order status
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutPage;
