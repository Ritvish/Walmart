import React, { useState, useEffect } from 'react';
import { useCart } from '../context/CartContext';
import { clubService } from '../services/clubService';
import CartSummary from '../components/CartSummary';
import toast from 'react-hot-toast';

const CartPage = () => {
  const { cart, loading, error } = useCart();
  const [clubReadiness, setClubReadiness] = useState(null);
  const [location, setLocation] = useState(null);
  const [clubTimeout, setClubTimeout] = useState(180); // Default 3 minutes
  // Removed unused setCheckingReadiness

  useEffect(() => {
    // Get user location and check club readiness
    const getUserLocation = async () => {
      try {
        console.log('📍 Requesting user location...');
        const userLocation = await clubService.getCurrentLocation();
        console.log('✅ Location obtained:', userLocation);
        setLocation(userLocation);
        
        // Always enable club & save when location is available and cart has items
        if (cart && cart.cart_items && cart.cart_items.length > 0) {
          console.log('🛒 Cart has items, enabling Club & Save');
          setClubReadiness({
            can_club: true,
            nearby_count: 0, // Will be determined in real-time
            potential_savings: 15, // Estimated savings
            estimated_wait_minutes: 3,
            reason: 'Location detected, ready to find matches!'
          });
        } else {
          console.log('🛒 Cart is empty or not loaded yet');
        }
      } catch (error) {
        console.error('❌ Failed to get location:', error);
        toast.error('Location access required for club features');
        // Set club readiness to false when location fails
        setClubReadiness({
          can_club: false,
          reason: 'Location access required for Club & Save feature'
        });
      }
    };

    getUserLocation();
  }, [cart]); // Now getUserLocation is defined inside useEffect

  const handleTimeoutChange = (newTimeout) => {
    console.log('⏰ Timeout changed to:', newTimeout);
    setClubTimeout(newTimeout);
  };

  const handleClubAndSave = () => {
    console.log('🚀 Club & Save clicked with timeout:', clubTimeout);
    console.log('📍 Current location:', location);
    console.log('🛒 Current cart:', cart);
    
    if (!location) {
      console.error('❌ No location available');
      toast.error('Location required for clubbing');
      return;
    }
    
    if (!cart || !cart.cart_items || cart.cart_items.length === 0) {
      console.error('❌ Cart is empty');
      toast.error('Your cart is empty');
      return;
    }
    
    // Store data in sessionStorage instead of URL parameters
    sessionStorage.setItem('clubLocation', JSON.stringify(location));
    sessionStorage.setItem('clubTimeout', clubTimeout.toString());
    
    console.log('🔗 Navigating to club page with data stored in sessionStorage');
    
    // Navigate to club matching page without URL parameters
    window.location.href = '/club';
  };

  const handleCheckout = () => {
    // Navigate to checkout page
    window.location.href = '/checkout';
  };

  if (loading) {
    return (
      <div className="container">
        <div className="loading">
          <div className="spinner"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container">
        <div className="alert alert-danger">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '20px' }}>
      <h1 style={{ marginBottom: '20px' }}>Your Cart</h1>
      
      <div className="grid grid-2">
        <div>
          <CartSummary
            cart={cart}
            onClubAndSave={handleClubAndSave}
            onCheckout={handleCheckout}
            clubReadiness={clubReadiness}
            clubTimeout={clubTimeout}
            onTimeoutChange={handleTimeoutChange}
          />
        </div>
        
        <div>
          {clubReadiness && (
            <div className="card">
              <h3>Club & Save Status</h3>
              
              {clubReadiness.can_club ? (
                <div className="alert alert-success">
                  <h4>🎉 Great news!</h4>
                  <p>You can club with nearby users and save money!</p>
                  <ul>
                    <li>Nearby users: {clubReadiness.nearby_count}</li>
                    <li>Potential savings: ₹{clubReadiness.potential_savings}</li>
                    <li>Estimated wait time: {clubReadiness.estimated_wait_minutes} minutes</li>
                  </ul>
                </div>
              ) : (
                <div className="alert alert-info">
                  <h4>Club & Save Not Available</h4>
                  <p>{clubReadiness.reason}</p>
                  <p>You can still proceed with regular checkout.</p>
                </div>
              )}
            </div>
          )}
          
          <div className="card">
            <h3>Delivery Information</h3>
            <p>
              <strong>Delivery Address:</strong><br />
              {location ? `Lat: ${location.lat.toFixed(4)}, Lng: ${location.lng.toFixed(4)}` : 'Getting location...'}
            </p>
            <p>
              <strong>Estimated Delivery Time:</strong> 15-30 minutes
            </p>
            <p>
              <strong>Delivery Fee:</strong> ₹40 (or save with Club & Save!)
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CartPage;
