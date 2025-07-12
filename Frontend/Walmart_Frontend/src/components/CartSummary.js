import React from 'react';
import { cartService } from '../services/cartService';
import { useCart } from '../context/CartContext';

const CartSummary = ({ cart, onClubAndSave, onCheckout, clubReadiness, clubTimeout, onTimeoutChange }) => {
  const { loadCart } = useCart();
  
  // Use cart_items from the API response
  const cartItems = cart?.cart_items || [];
  
  const handleRemoveItem = async (itemId) => {
    try {
      await cartService.removeFromCart(itemId);
      console.log('Item removed from cart');
      loadCart(); // Refresh the cart to update the UI
    } catch (error) {
      console.error('Error removing item:', error);
      alert('Failed to remove item from cart');
    }
  };

  const handleUpdateQuantity = async (itemId, newQuantity) => {
    try {
      await cartService.updateCartItemQuantity(itemId, newQuantity);
      console.log('Quantity updated');
      loadCart(); // Refresh the cart to update the UI
    } catch (error) {
      console.error('Error updating quantity:', error);
      alert('Failed to update quantity');
    }
  };

  const handleClearCart = async () => {
    if (window.confirm('Are you sure you want to clear your entire cart? This action cannot be undone.')) {
      try {
        const response = await cartService.clearCart();
        console.log('Cart cleared:', response.message);
        loadCart(); // Refresh the cart to update the UI
      } catch (error) {
        console.error('Error clearing cart:', error);
        alert('Failed to clear cart');
      }
    }
  };
  
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
      <div className="d-flex justify-content-between align-items-center" style={{ marginBottom: '20px' }}>
        <h3 style={{ margin: 0 }}>Cart Summary</h3>
        <button
          onClick={handleClearCart}
          className="btn btn-sm btn-outline-danger"
          style={{ fontSize: '12px' }}
        >
          Clear Cart
        </button>
      </div>
      
      <div style={{ marginBottom: '20px' }}>
        {cartItems.map((item) => (
          <div key={item.id} className="cart-item" style={{ marginBottom: '16px', padding: '12px', border: '1px solid #eee', borderRadius: '8px' }}>
            <div className="d-flex justify-content-between align-items-start">
              <div style={{ flex: 1 }}>
                <div style={{ fontWeight: '600', marginBottom: '4px' }}>{item.product.name}</div>
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '8px' }}>
                  ₹{parseFloat(item.product.price).toFixed(2)} each
                </div>
                <div className="d-flex align-items-center gap-2">
                  <button
                    onClick={() => handleUpdateQuantity(item.id, Math.max(1, item.quantity - 1))}
                    className="btn btn-sm btn-outline-secondary"
                    style={{ width: '30px', height: '30px', padding: '0' }}
                  >
                    -
                  </button>
                  <span style={{ minWidth: '30px', textAlign: 'center' }}>{item.quantity}</span>
                  <button
                    onClick={() => handleUpdateQuantity(item.id, item.quantity + 1)}
                    className="btn btn-sm btn-outline-secondary"
                    style={{ width: '30px', height: '30px', padding: '0' }}
                  >
                    +
                  </button>
                </div>
              </div>
              <div className="text-right">
                <div style={{ fontWeight: '600', marginBottom: '8px' }}>
                  ₹{parseFloat(item.total_price || 0).toFixed(2)}
                </div>
                <button
                  onClick={() => handleRemoveItem(item.id)}
                  className="btn btn-sm btn-danger"
                  style={{ fontSize: '12px' }}
                >
                  Remove
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
      
      <div style={{ borderTop: '1px solid #eee', paddingTop: '16px', marginBottom: '20px' }}>
        <div className="d-flex justify-content-between" style={{ marginBottom: '8px' }}>
          <span>Total Items:</span>
          <span>{cartItems.reduce((sum, item) => sum + item.quantity, 0)}</span>
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
