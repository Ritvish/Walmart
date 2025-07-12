import React from 'react';

const CartSummary = ({ cart, onClubAndSave, onCheckout, clubReadiness, clubTimeout, onTimeoutChange }) => {
  // Use cart_items from the API response
  const cartItems = cart?.cart_items || [];
  
  if (!cart || !cartItems || cartItems.length === 0) {
    return (
      <div className="card text-center">
        <h3>Your Cart is Empty</h3>
        <p>Add some items to get started!</p>
      </div>
    );
  }

  const total = cartItems.reduce((sum, item) => sum + parseFloat(item.total_price || 0), 0);
  const weight = cartItems.reduce((sum, item) => sum + (item.product.weight_grams * item.quantity), 0);

  return (
    <div className="card">
      <h3 style={{ marginBottom: '20px' }}>Cart Summary</h3>
      
      <div style={{ marginBottom: '20px' }}>
        {cartItems.map((item) => (
          <div key={item.id} className="d-flex justify-content-between align-items-center" style={{ marginBottom: '12px' }}>
            <div>
              <div style={{ fontWeight: '600' }}>{item.product.name}</div>
              <div style={{ fontSize: '14px', color: '#666' }}>
                Qty: {item.quantity} × ₹{item.product.price}
              </div>
            </div>
            <div style={{ fontWeight: '600' }}>
              ₹{parseFloat(item.total_price || 0).toFixed(2)}
            </div>
          </div>
        ))}
      </div>
      
      <div style={{ borderTop: '1px solid #eee', paddingTop: '16px', marginBottom: '20px' }}>
        <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
          <span>Total Items:</span>
          <span>{cartItems.length}</span>
        </div>
        <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
          <span>Total Weight:</span>
          <span>{weight}g</span>
        </div>
        <div className="d-flex justify-content-between" style={{ fontSize: '18px', fontWeight: 'bold' }}>
          <span>Total Amount:</span>
          <span>₹{total.toFixed(2)}</span>
        </div>
      </div>
      
      {clubReadiness && clubReadiness.can_club && (
        <div className="alert alert-info" style={{ marginBottom: '20px' }}>
          <h4 style={{ margin: '0 0 8px 0' }}>🎉 Club & Save Available!</h4>
          <p style={{ margin: '0 0 8px 0' }}>
            Join with nearby users and save on delivery fees.
          </p>
          <div style={{ marginTop: '16px' }}>
            <label htmlFor="timeout-slider" style={{ display: 'block', marginBottom: '8px' }}>
              Wait time: <strong>{clubTimeout / 60} minutes</strong>
            </label>
            <input
              type="range"
              id="timeout-slider"
              min="120" // 2 minutes
              max="600" // 10 minutes
              step="60"
              value={clubTimeout}
              onChange={(e) => onTimeoutChange(parseInt(e.target.value, 10))}
              style={{ width: '100%' }}
            />
          </div>
        </div>
      )}
      
      <div className="d-flex gap-2">
        {clubReadiness && clubReadiness.can_club ? (
          <>
            <button 
              onClick={onClubAndSave}
              className="btn btn-warning"
              style={{ flex: 1 }}
            >
              Find Clubbing Buddy
            </button>
            <button 
              onClick={onCheckout}
              className="btn btn-primary"
              style={{ flex: 1 }}
            >
              Skip & Checkout
            </button>
          </>
        ) : (
          <button 
            onClick={onCheckout}
            className="btn btn-primary"
            style={{ flex: 1 }}
          >
            Checkout Now
          </button>
        )}
      </div>
    </div>
  );
};

export default CartSummary;
