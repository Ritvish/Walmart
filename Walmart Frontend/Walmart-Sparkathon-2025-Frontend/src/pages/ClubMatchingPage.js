import React, { useState, useEffect, useCallback } from 'react';
import { useCart } from '../context/CartContext';
import { clubService } from '../services/clubService';
import toast from 'react-hot-toast';

const ClubMatchingPage = () => {
  const { cart, loading } = useCart();
  const [buddyQueue, setBuddyQueue] = useState(null);
  const [status, setStatus] = useState('LOADING');
  const [timerDuration, setTimerDuration] = useState(300); // Default 5 minutes

  const [timeLeft, setTimeLeft] = useState(() => {
    const savedStart = localStorage.getItem('buddyQueueTimerStart');
    const savedDuration = localStorage.getItem('buddyQueueTimerDuration');
    const duration = savedDuration ? parseInt(savedDuration, 10) : timerDuration;

    if (savedStart) {
      const elapsed = Math.floor((Date.now() - parseInt(savedStart, 10)) / 1000);
      return Math.max(duration - elapsed, 0);
    }
    return duration;
  });
  const [location, setLocation] = useState(null);
  const [hasTriedJoining, setHasTriedJoining] = useState(false); // Prevent duplicate calls
  const [queueStats, setQueueStats] = useState(null);
  const [nearbyUsers, setNearbyUsers] = useState(0);
  const [estimatedSavings, setEstimatedSavings] = useState(0);

  // Function to get queue information
  const getQueueInformation = useCallback(async (userLocation) => {
    try {
      const stats = await clubService.getQueueStats(userLocation);
      setQueueStats(stats);
      setNearbyUsers(stats.nearby_users || 0);
      
      // Calculate estimated savings based on cart total
      if (cart && cart.cart_items) {
        const total = cart.cart_items.reduce((sum, item) => sum + parseFloat(item.total_price || 0), 0);
        setEstimatedSavings(Math.round(total * 0.15)); // 15% estimated savings
      }
    } catch (error) {
      console.warn('Could not get queue stats:', error);
      setNearbyUsers(0);
    }
  }, [cart]);

  // Get location and timeout from sessionStorage on mount
  useEffect(() => {
    // Get location from sessionStorage
    const savedLocation = sessionStorage.getItem('clubLocation');
    const savedTimeout = sessionStorage.getItem('clubTimeout');

    if (savedTimeout) {
      const duration = parseInt(savedTimeout, 10);
      console.log(`[ClubMatchingPage] 📥 Initializing with timeout from sessionStorage: ${duration} seconds`);
      setTimerDuration(duration);
      setTimeLeft(duration); // Initialize timeLeft with the new duration
    }
    
    if (savedLocation) {
      const userLocation = JSON.parse(savedLocation);
      setLocation(userLocation);
      
      // Get queue statistics for this location
      getQueueInformation(userLocation);
    } else {
      toast.error('Location required for clubbing');
      setTimeout(() => {
        window.location.href = '/cart';
      }, 2000);
    }
  }, [getQueueInformation]); // Added getQueueInformation to dependencies

  // Define joinBuddyQueue function with useCallback
  const joinBuddyQueue = useCallback(async (userLocation) => {
    try {
      console.log('🚀 Starting joinBuddyQueue with location:', userLocation);
      setStatus('JOINING');
      // Safety check for cart data
      if (!cart || !cart.cart_items || cart.cart_items.length === 0) {
        console.error('❌ Cart validation failed:', { cart, hasItems: cart?.cart_items?.length });
        toast.error('Cart is empty or not loaded');
        setTimeout(() => {
          window.location.href = '/cart';
        }, 2000);
        return;
      }
      const total = cart.cart_items.reduce((sum, item) => sum + parseFloat(item.total_price || 0), 0);
      const weight = cart.cart_items.reduce((sum, item) => sum + (item.product.weight_grams * item.quantity), 0);
      const buddyData = {
        cart_id: cart.id,
        value_total: total,
        weight_total: weight / 1000, // Convert to kg
        lat: userLocation.lat,
        lng: userLocation.lng,
        timeout_minutes: timerDuration / 60, // Send timeout to backend in minutes
      };
      console.log('🤝 Joining buddy queue with data:', buddyData);
      console.log(`[ClubMatchingPage] 🚀 Sending timeout to backend API: ${timerDuration / 60} minutes (${timerDuration} seconds)`);
      const result = await clubService.joinQueue(buddyData);
      console.log('✅ Join queue result:', result);
      // Ensure the result has the correct ID field
      const queueId = result.buddyQueueId || result.id;
      if (queueId) {
        result.buddyQueueId = queueId;
        result.id = queueId;
      }
      setBuddyQueue(result);
      // Set timer start in localStorage if joining a new queue
      if (!result.alreadyInQueue) {
        localStorage.setItem('buddyQueueTimerStart', Date.now().toString());
        localStorage.setItem('buddyQueueTimerDuration', timerDuration.toString());
      }
      
      // Store buddy_queue_id as specified by backend
      localStorage.setItem('buddy_queue_id', queueId);
      
      setStatus('WAITING');
      if (result.alreadyInQueue) {
        toast.success('Reconnected to existing buddy queue! Looking for matches...');
      } else {
        toast.success('Joined buddy queue! Looking for matches...');
      }
    } catch (error) {
      console.error('❌ Failed to join buddy queue:', error);
      console.error('❌ Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
        url: error.config?.url
      });
      if (error.message === 'Network Error') {
        toast.error('Cannot connect to server. Please check if backend is running.');
      } else if (error.response?.status === 401) {
        toast.error('Please login again');
        setTimeout(() => {
          window.location.href = '/login';
        }, 2000);
      } else {
        const errorMessage = error.response?.data?.detail || error.detail || 'Failed to join buddy queue';
        toast.error(errorMessage);
      }
      setStatus('ERROR');
    }
  }, [cart, timerDuration]); // Added timerDuration to dependency array

  // Define checkStatus function with useCallback - Updated to match backend specs
  const checkStatus = useCallback(async () => {
    const queueId = buddyQueue?.buddyQueueId || buddyQueue?.id;
    if (!buddyQueue || !queueId) {
      console.warn('⚠️ Cannot check status: no buddy queue or ID');
      return;
    }
    try {
      console.log('📊 Checking status for buddy queue:', queueId);
      // Use the exact endpoint specified by backend
      const statusResult = await clubService.getClubStatus(queueId);
      console.log('📊 Status check result:', statusResult);
      if (!statusResult || !statusResult.status) {
        console.warn('⚠️ Invalid status result:', statusResult);
        return;
      }
      
      // Update nearby users count if available
      if (statusResult.nearby_users !== undefined) {
        setNearbyUsers(statusResult.nearby_users);
      }
      
      // Handle status as specified by backend
      if (statusResult.status === 'matched') {
        setStatus('MATCHED');
        toast.success('Match found! Redirecting to your clubbed cart...');
        
        // Store the IDs as specified by backend
        const clubbedOrderId = statusResult.clubbed_order_id;
        const discountAmount = statusResult.discount_given;
        
        console.log('🔍 Clubbed Order ID:', clubbedOrderId);
        console.log('🔍 Discount Amount:', discountAmount);
        
        if (clubbedOrderId) {
          // Store in localStorage as per backend specs
          localStorage.setItem('clubbed_order_id', clubbedOrderId);
          localStorage.setItem('is_in_clubbed_cart', 'true');
          localStorage.setItem('discount_amount', discountAmount?.toString() || '0');
          
          console.log('✅ Redirecting to clubbed cart:', `/clubbed-cart/${clubbedOrderId}`);
          setTimeout(() => {
            window.location.href = `/clubbed-cart/${clubbedOrderId}`;
          }, 2000);
        } else {
          console.error('❌ No clubbed_order_id found in statusResult:', statusResult);
          toast.error("Match found, but couldn't get the clubbed order ID.");
        }
      } else if (statusResult.status === 'WAITING') {
        setStatus('WAITING');
        // Continue waiting
      } else if (statusResult.status === 'TIMED_OUT') {
        setStatus('TIMED_OUT');
        toast.info('No matches found in the time limit');
        // Clean up localStorage
        localStorage.removeItem('buddy_queue_id');
        localStorage.removeItem('clubbed_order_id');
        localStorage.removeItem('is_in_clubbed_cart');
      }
    } catch (error) {
      console.error('❌ Failed to check status:', error);
      // Don't show error toast for status checks as they happen in background
    }
  }, [buddyQueue]);

  // Handle cart loading and joining queue, with duplicate prevention
  useEffect(() => {
    if (!location || hasTriedJoining) return; // Prevent duplicate calls
    if (loading) {
      setStatus('LOADING');
      return;
    }
    if (!cart || !cart.cart_items || cart.cart_items.length === 0) {
      toast.error('Your cart is empty');
      setTimeout(() => {
        window.location.href = '/cart';
      }, 2000);
      return;
    }
    // Check for existing buddyQueueId in localStorage
    const existingId = localStorage.getItem('buddyQueueId');
    console.log('🔍 ClubMatchingPage checking for existing buddyQueueId:', existingId);
    setHasTriedJoining(true); // Set immediately to prevent duplicate join calls
    if (existingId) {
      // Check backend for status
      console.log('🔍 Checking backend status for existing queue:', existingId);
      clubService.getClubStatus(existingId)
        .then((statusResult) => {
          console.log('📊 Backend status result:', statusResult);
          const statusValue = statusResult?.status?.toUpperCase();
          if (statusResult && statusResult.status && statusValue !== 'EXPIRED' && statusValue !== 'MATCHED' && statusValue !== 'TIMED_OUT') {
            // Already in a valid queue, set state and skip join
            console.log('✅ Already in valid queue, setting state and skipping join');
            setBuddyQueue({ id: existingId, buddyQueueId: existingId, ...statusResult });
            // Do not reset timer if reconnecting to existing queue
            setStatus('WAITING');
          } else {
            // Invalid/expired, remove and join new queue
            console.log('🧹 Invalid/expired queue, removing and joining new');
            localStorage.removeItem('buddyQueueId');
            joinBuddyQueue(location);
          }
        })
        .catch(() => {
          // If backend check fails, remove and join new queue
          console.log('❌ Backend check failed, removing and joining new');
          localStorage.removeItem('buddyQueueId');
          joinBuddyQueue(location);
        });
    } else {
      // No existing queue, join new
      console.log('🚀 No existing queue, joining new');
      joinBuddyQueue(location);
    }
  }, [cart, loading, location, hasTriedJoining, joinBuddyQueue]);

  // Timer and status checking for waiting state
  useEffect(() => {
    if (buddyQueue && status === 'WAITING') {
      console.log(`[ClubMatchingPage] ⏳ Starting countdown timer with duration: ${timerDuration} seconds`);
      // Set timer start if not already set
      let timerStart = localStorage.getItem('buddyQueueTimerStart');
      if (!timerStart) {
        timerStart = Date.now().toString();
        localStorage.setItem('buddyQueueTimerStart', timerStart);
      }
      // Countdown timer
      const timer = setInterval(() => {
        const elapsed = Math.floor((Date.now() - parseInt(timerStart, 10)) / 1000);
        const remaining = Math.max(timerDuration - elapsed, 0);
        setTimeLeft(remaining);
        if (remaining <= 0) {
          setStatus('TIMED_OUT');
          localStorage.removeItem('buddyQueueId');
          localStorage.removeItem('buddyQueueTimerStart');
          localStorage.removeItem('buddyQueueTimerDuration');
        }
      }, 1000);
      // Status checker - Poll every 5 seconds as per backend specs
      const statusChecker = setInterval(() => {
        checkStatus();
      }, 5000);
      // Cleanup function
      return () => {
        clearInterval(timer);
        clearInterval(statusChecker);
      };
    }
  }, [buddyQueue, status, checkStatus, timerDuration]);

  // Clean up buddyQueueId on match or timeout
  useEffect(() => {
    if (status === 'MATCHED' || status === 'TIMED_OUT' || status === 'ERROR') {
      localStorage.removeItem('buddyQueueId');
      localStorage.removeItem('buddyQueueTimerStart');
      localStorage.removeItem('buddyQueueTimerDuration');
    }
  }, [status]);

  const handleContinueAlone = () => {
    window.location.href = '/checkout';
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  // Show loading state while cart is being fetched or location is being processed
  if (loading || status === 'LOADING' || (!cart && !loading)) {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <div className="loading">
            <div className="spinner"></div>
          </div>
          <h2>Loading...</h2>
          <p>Please wait while we prepare your buddy matching</p>
        </div>
      </div>
    );
  }

  if (status === 'JOINING') {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <div className="loading">
            <div className="spinner"></div>
          </div>
          <h2>Joining Buddy Queue...</h2>
          <p>Please wait while we add you to the queue</p>
        </div>
      </div>
    );
  }

  if (status === 'ERROR') {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <h2>Something went wrong</h2>
          <p>We couldn't add you to the buddy queue. Please try again.</p>
          <button onClick={() => window.location.href = '/cart'} className="btn btn-primary">
            Back to Cart
          </button>
        </div>
      </div>
    );
  }

  if (status === 'WAITING') {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏰</div>
          <h2>Looking for Buddy Matches...</h2>
          
          <div style={{ 
            fontSize: '36px', 
            color: '#007bff', 
            fontWeight: 'bold', 
            marginBottom: '20px' 
          }}>
            {formatTime(timeLeft)}
          </div>
          
          {/* Queue Information */}
          <div className="row" style={{ marginBottom: '20px' }}>
            <div className="col-md-4">
              <div className="card bg-light">
                <div className="card-body text-center">
                  <h5 className="card-title">👥 Nearby Users</h5>
                  <h3 className="text-primary">{nearbyUsers}</h3>
                  <small className="text-muted">Looking to club</small>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card bg-light">
                <div className="card-body text-center">
                  <h5 className="card-title">💰 Potential Savings</h5>
                  <h3 className="text-success">₹{estimatedSavings}</h3>
                  <small className="text-muted">On delivery fee</small>
                </div>
              </div>
            </div>
            <div className="col-md-4">
              <div className="card bg-light">
                <div className="card-body text-center">
                  <h5 className="card-title">🎯 Success Rate</h5>
                  <h3 className="text-info">{queueStats?.success_rate || 75}%</h3>
                  <small className="text-muted">In this area</small>
                </div>
              </div>
            </div>
          </div>
          
          <p>We're searching for nearby users to club your order with.</p>
          <p>This usually takes 2-5 minutes.</p>
          
          <div className="alert alert-info">
            <h4>What's happening?</h4>
            <ul style={{ textAlign: 'left', margin: 0 }}>
              <li>🔍 Scanning for nearby users with similar orders</li>
              <li>🎯 Matching cart values and delivery locations</li>
              <li>🚚 Calculating optimal delivery routes</li>
              {nearbyUsers > 0 && <li>✨ Found {nearbyUsers} potential matches nearby!</li>}
            </ul>
          </div>
          
          <div className="d-flex justify-content-center gap-3 mt-4">
            <button 
              onClick={handleContinueAlone}
              className="btn btn-secondary"
            >
              Continue Alone
            </button>
            <button 
              onClick={() => window.location.href = '/cart'}
              className="btn btn-primary"
            >
              Back to Cart
            </button>
            {/* Temporary button to simulate match for testing */}
            {nearbyUsers > 0 && (
              <button 
                onClick={() => {
                  setStatus('MATCHED');
                  toast.success('Match found! Redirecting to your clubbed cart...');
                  setTimeout(() => {
                    window.location.href = `/clubbed-cart/test-clubbed-order-id`;
                  }, 2000);
                }}
                className="btn btn-success"
              >
                (Test) Force Match
              </button>
            )}
          </div>
        </div>
      </div>
    );
  }

  if (status === 'MATCHED') {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>🎉</div>
          <h2>Match Found!</h2>
          <p>Great news! We found compatible users to club your order with.</p>
          
          <div className="alert alert-success">
            <h4>Your savings are confirmed!</h4>
            <p>You'll be redirected to the order confirmation page shortly.</p>
          </div>
          
          <div className="loading">
            <div className="spinner"></div>
          </div>
        </div>
      </div>
    );
  }

  if (status === 'TIMED_OUT') {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏱️</div>
          <h2>No Matches Found</h2>
          <p>We couldn't find any compatible users to club your order with in the time limit.</p>
          
          <div className="alert alert-info">
            <h4>What now?</h4>
            <p>Don't worry! You can still proceed with regular checkout or try clubbing again later.</p>
          </div>
          
          <div className="d-flex justify-content-center gap-3">
            <button 
              onClick={() => window.location.href = '/cart'}
              className="btn btn-secondary"
            >
              Try Again
            </button>
            <button 
              onClick={handleContinueAlone}
              className="btn btn-primary"
            >
              Proceed to Checkout
            </button>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default ClubMatchingPage;
