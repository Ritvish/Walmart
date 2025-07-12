import React from 'react';
import { useAuth } from '../context/AuthContext';

const HomePage = () => {
  const { isAuthenticated } = useAuth();

  return (
    <div className="container" style={{ padding: '40px 20px' }}>
      <div className="text-center mb-5">
        <h1 style={{ fontSize: '48px', marginBottom: '20px' }}>
          Welcome to BuddyCart
        </h1>
        <p style={{ fontSize: '20px', color: '#666', maxWidth: '600px', margin: '0 auto' }}>
          Smart order clubbing system to help you save delivery fees by joining with nearby users
        </p>
      </div>

      <div className="grid grid-3 mb-5">
        <div className="card text-center">
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🛒</div>
          <h3>Shop Together</h3>
          <p>Add items to your cart and get matched with nearby users</p>
        </div>
        
        <div className="card text-center">
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>💰</div>
          <h3>Save Money</h3>
          <p>Split delivery fees and unlock bulk discounts</p>
        </div>
        
        <div className="card text-center">
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🚚</div>
          <h3>Fast Delivery</h3>
          <p>Optimized delivery routes for quicker service</p>
        </div>
      </div>

      <div className="text-center">
        {!isAuthenticated ? (
          <div>
            <h2 style={{ marginBottom: '20px' }}>Get Started Today!</h2>
            <div className="d-flex justify-content-center gap-3">
              <a href="/login" className="btn btn-primary">
                Login
              </a>
              <a href="/register" className="btn btn-secondary">
                Register
              </a>
            </div>
          </div>
        ) : (
          <div>
            <h2 style={{ marginBottom: '20px' }}>Ready to Shop?</h2>
            <a href="/products" className="btn btn-primary">
              Browse Products
            </a>
          </div>
        )}
      </div>

      <div className="card mt-5">
        <h2 style={{ marginBottom: '20px' }}>How It Works</h2>
        <div className="grid grid-4">
          <div className="text-center">
            <div style={{ 
              background: '#007bff', 
              color: 'white', 
              borderRadius: '50%', 
              width: '40px', 
              height: '40px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              margin: '0 auto 12px' 
            }}>
              1
            </div>
            <h4>Add to Cart</h4>
            <p>Browse and add items to your cart</p>
          </div>
          
          <div className="text-center">
            <div style={{ 
              background: '#007bff', 
              color: 'white', 
              borderRadius: '50%', 
              width: '40px', 
              height: '40px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              margin: '0 auto 12px' 
            }}>
              2
            </div>
            <h4>Club & Save</h4>
            <p>Join with nearby users to share delivery costs</p>
          </div>
          
          <div className="text-center">
            <div style={{ 
              background: '#007bff', 
              color: 'white', 
              borderRadius: '50%', 
              width: '40px', 
              height: '40px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              margin: '0 auto 12px' 
            }}>
              3
            </div>
            <h4>Get Matched</h4>
            <p>Wait for nearby users to join your club</p>
          </div>
          
          <div className="text-center">
            <div style={{ 
              background: '#007bff', 
              color: 'white', 
              borderRadius: '50%', 
              width: '40px', 
              height: '40px', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              margin: '0 auto 12px' 
            }}>
              4
            </div>
            <h4>Enjoy Savings</h4>
            <p>Receive your order with reduced delivery fees</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage;
