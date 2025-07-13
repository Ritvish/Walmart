import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { clubService } from '../services/clubService';
import PrivacyNotice from '../components/PrivacyNotice';
import toast from 'react-hot-toast';

const CheckoutPage = () => {
  const { cart, clearCart } = useCart();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [processing, setProcessing] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('card');
  const [orderDetails, setOrderDetails] = useState({
    address: '',
    phone: '',
    notes: '',
  });
  
  // Clubbed cart state
  const [clubbedCart, setClubbedCart] = useState(null);
  const [isClubbed, setIsClubbed] = useState(false);
  const [clubbedOrderId, setClubbedOrderId] = useState(null);
  
  useEffect(() => {
    const clubbedOrderIdParam = searchParams.get('clubbedOrderId');
    if (clubbedOrderIdParam) {
      setIsClubbed(true);
      setClubbedOrderId(clubbedOrderIdParam);
      fetchClubbedCart(clubbedOrderIdParam);
    }
  }, [searchParams]);
  
  const fetchClubbedCart = async (clubbedOrderId) => {
    try {
      const data = await clubService.getClubbedCart(clubbedOrderId);
      setClubbedCart(data);
    } catch (error) {
      console.error('Failed to fetch clubbed cart:', error);
      toast.error('Failed to fetch clubbed cart details.');
    }
  };

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
      
      if (isClubbed) {
        // For clubbed orders, navigate with clubbed order data
        navigate('/order-success', {
          state: {
            id: clubbedOrderId,
            total: clubbedCart?.total_amount || 0,
            items: clubbedCart?.items?.length || 0,
            estimatedDelivery: '20-30 minutes',
            savings: 35.00, // You may want to calculate this dynamically
            clubbed: true,
            buddyCount: clubbedCart?.users?.length || 1,
          },
        });
      } else {
        // For regular orders
        clearCart();
        navigate('/order-success', {
          state: {
            id: 'ORDER-' + Date.now(),
            total: total,
            items: cart.cart_items.length,
            estimatedDelivery: '20-30 minutes',
            savings: 35.00, // You may want to calculate this dynamically
            clubbed: false,
            buddyCount: 1,
          },
        });
      }
    } catch (error) {
      toast.error('Failed to place order');
      setProcessing(false);
    }
  };

  // Determine which cart data to use
  const currentCart = isClubbed ? clubbedCart : cart;
  const cartItems = isClubbed ? clubbedCart?.items || [] : cart?.cart_items || [];
  
  if (!currentCart || cartItems.length === 0) {
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

  // Calculate totals based on cart type
  let subtotal, total;
  if (isClubbed && clubbedCart) {
    subtotal = parseFloat(clubbedCart.total_amount || 0);
    const deliveryFee = 40;
    total = subtotal + deliveryFee;
  } else {
    subtotal = cart.cart_items.reduce((sum, item) => sum + parseFloat(item.total_price || 0), 0);
    const deliveryFee = 40;
    total = subtotal + deliveryFee;
  }

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
            {isClubbed && clubbedCart && (
              <>
                <PrivacyNotice type="checkout" />
                <div className="alert alert-info mb-3">
                  <strong>🎉 Clubbed Order</strong> - Shopping with {clubbedCart.users?.filter(u => !u.is_current_user).length || 0} other user(s)
                  <br />
                  <small>Other users' items are hidden for privacy</small>
                </div>
              </>
            )}
            
            <div style={{ marginBottom: '20px' }}>
              {isClubbed && clubbedCart ? (
                // Show current user's items only
                <>
                  <h6 style={{ marginBottom: '12px', color: '#666' }}>Your Items:</h6>
                  {clubbedCart.items.length === 0 ? (
                    <p style={{ color: '#666', fontStyle: 'italic' }}>You haven't added any items yet</p>
                  ) : (
                    clubbedCart.items.map((item, index) => (
                      <div key={index} className="d-flex justify-content-between align-items-center" style={{ marginBottom: '12px' }}>
                        <div>
                          <div style={{ fontWeight: '600' }}>{item.product_name}</div>
                          <div style={{ fontSize: '14px', color: '#666' }}>
                            Qty: {item.quantity}
                          </div>
                        </div>
                        <div style={{ fontWeight: '600' }}>
                          ₹{(parseFloat(item.price || 0) * item.quantity).toFixed(2)}
                        </div>
                      </div>
                    ))
                  )}
                  
                  {clubbedCart.other_users_total > 0 && (
                    <>
                      <hr style={{ margin: '16px 0' }} />
                      <h6 style={{ marginBottom: '12px', color: '#666' }}>Other Users:</h6>
                      <div className="d-flex justify-content-between align-items-center" style={{ marginBottom: '12px' }}>
                        <div>
                          <div style={{ fontWeight: '600', color: '#666' }}>
                            {clubbedCart.users?.filter(u => !u.is_current_user).length || 0} other user(s)
                          </div>
                          <div style={{ fontSize: '14px', color: '#666' }}>
                            Items hidden for privacy
                          </div>
                        </div>
                        <div style={{ fontWeight: '600', color: '#666' }}>
                          ₹{parseFloat(clubbedCart.other_users_total || 0).toFixed(2)}
                        </div>
                      </div>
                    </>
                  )}
                </>
              ) : (
                // Render regular cart items
                cart.cart_items.map((item) => (
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
                ))
              )}
            </div>
            
            <div style={{ borderTop: '1px solid #eee', paddingTop: '16px' }}>
              {isClubbed && clubbedCart ? (
                // Clubbed cart totals
                <>
                  <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                    <span>Your Cart:</span>
                    <span>₹{clubbedCart.users?.find(u => u.is_current_user)?.cart_total.toFixed(2) || '0.00'}</span>
                  </div>
                  <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                    <span>Other Users:</span>
                    <span>₹{parseFloat(clubbedCart.other_users_total || 0).toFixed(2)}</span>
                  </div>
                  <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                    <span>Combined Subtotal:</span>
                    <span>₹{parseFloat(clubbedCart.total_amount || 0).toFixed(2)}</span>
                  </div>
                  <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                    <span>Delivery Fee:</span>
                    <span>₹{(40).toFixed(2)}</span>
                  </div>
                  <div className="d-flex justify-content-between" style={{ marginBottom: '8px', color: '#28a745' }}>
                    <span>Club Discount:</span>
                    <span>-₹{(35).toFixed(2)}</span>
                  </div>
                  <div className="d-flex justify-content-between" style={{ fontSize: '18px', fontWeight: 'bold' }}>
                    <span>Total:</span>
                    <span>₹{(parseFloat(clubbedCart.total_amount || 0) + 40 - 35).toFixed(2)}</span>
                  </div>
                </>
              ) : (
                // Regular cart totals
                <>
                  <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                    <span>Subtotal:</span>
                    <span>₹{subtotal.toFixed(2)}</span>
                  </div>
                  <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
                    <span>Delivery Fee:</span>
                    <span>₹{(40).toFixed(2)}</span>
                  </div>
                  <div className="d-flex justify-content-between" style={{ fontSize: '18px', fontWeight: 'bold' }}>
                    <span>Total:</span>
                    <span>₹{total.toFixed(2)}</span>
                  </div>
                </>
              )}
            </div>
            
            <button
              onClick={handlePlaceOrder}
              disabled={processing}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '20px' }}
            >
              {processing ? 'Processing...' : `Place Order - ₹${
                isClubbed && clubbedCart 
                  ? (parseFloat(clubbedCart.total_amount || 0) + 40 - 35).toFixed(2)
                  : total.toFixed(2)
              }`}
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
