import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';

const Header = () => {
  const { user, logout } = useAuth();
  const { items, total } = useCart();

  const handleLogout = () => {
    logout();
    window.location.href = '/';
  };

  return (
    <header style={{ 
      background: '#fff', 
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)', 
      position: 'sticky', 
      top: 0, 
      zIndex: 100 
    }}>
      <div className="container">
        <div className="d-flex justify-content-between align-items-center" style={{ padding: '12px 0' }}>
          <div>
            <h1 style={{ margin: 0, color: '#007bff', fontSize: '24px' }}>
              🛒 BuddyCart
            </h1>
            <p style={{ margin: 0, fontSize: '12px', color: '#666' }}>
              Smart order clubbing to save delivery fees
            </p>
          </div>
          
          <div className="d-flex align-items-center gap-3">
            {user && (
              <>
                <div className="d-flex align-items-center gap-2">
                  <span style={{ fontSize: '14px', color: '#666' }}>
                    Cart: {(items || []).length} items
                  </span>
                  <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#28a745' }}>
                    ₹{(total || 0).toFixed(2)}
                  </span>
                </div>
                
                <div className="d-flex align-items-center gap-2">
                  <span style={{ fontSize: '14px' }}>
                    Hello, {user.name}
                  </span>
                  <button 
                    onClick={handleLogout}
                    className="btn btn-secondary"
                    style={{ padding: '6px 12px', fontSize: '12px' }}
                  >
                    Logout
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
