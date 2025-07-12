import api from './api';

export const clubService = {
  // Check if user can club orders
  checkReadiness: async (location) => {
    try {
      const response = await api.post('/club/check-readiness', location);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Join buddy queue
  joinQueue: async (buddyData) => {
    try {
      // Prevent duplicate joinQueue calls by checking localStorage for an active buddyQueueId
      const existingId = localStorage.getItem('buddyQueueId');
      console.log('🔍 Checking for existing buddyQueueId:', existingId);
      
      if (existingId) {
        // Check with backend if this queue is still valid (not matched or expired)
        try {
          console.log('🔍 Checking status of existing queue:', existingId);
          const status = await clubService.getClubStatus(existingId);
          console.log('📊 Existing queue status:', status);
          
          if (status && status.status && status.status !== 'expired' && status.status !== 'matched' && status.status !== 'timed_out') {
            // Already in a valid queue, return the status
            console.log('✅ Already in valid queue, skipping join');
            return { buddyQueueId: existingId, ...status, alreadyInQueue: true };
          } else {
            // Clean up invalid/expired buddyQueueId
            console.log('🧹 Cleaning up invalid/expired buddyQueueId');
            localStorage.removeItem('buddyQueueId');
          }
        } catch (e) {
          // If backend check fails, remove the id and proceed
          console.log('❌ Backend check failed, removing buddyQueueId:', e.message);
          localStorage.removeItem('buddyQueueId');
        }
      }
      
      // No valid queue, proceed to join
      console.log('🚀 Proceeding to join new queue');
      const response = await api.post('/club/join-queue', buddyData);
      console.log('✅ Join queue response:', response.data);
      
      // Handle both id and buddyQueueId field names from backend
      const queueId = response.data.buddyQueueId || response.data.id;
      if (queueId) {
        console.log('💾 Storing buddyQueueId in localStorage:', queueId);
        localStorage.setItem('buddyQueueId', queueId);
        // Ensure the response has the expected buddyQueueId field
        response.data.buddyQueueId = queueId;
      }
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get club status
  getClubStatus: async (buddyQueueId) => {
    try {
      const response = await api.get(`/club/status/${buddyQueueId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get user's current location
  getCurrentLocation: () => {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by this browser'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
        },
        (error) => {
          reject(error);
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0,
        }
      );
    });
  },

  // Get queue statistics (if backend supports it)
  getQueueStats: async (location) => {
    try {
      const response = await api.post('/club/queue-stats', location);
      return response.data;
    } catch (error) {
      // Fallback if endpoint doesn't exist
      console.warn('Queue stats endpoint not available:', error.message);
      return {
        nearby_users: 0,
        avg_wait_time: 300,
        success_rate: 75,
      };
    }
  },

  // Get detailed status with additional info
  getDetailedStatus: async (buddyQueueId) => {
    try {
      const response = await api.get(`/club/detailed-status/${buddyQueueId}`);
      return response.data;
    } catch (error) {
      // Fallback to basic status
      console.warn('Detailed status endpoint not available, using basic status');
      return await clubService.getClubStatus(buddyQueueId);
    }
  },

  // Get clubbed cart details
  getClubbedCart: async (clubbedOrderId) => {
    try {
      const response = await api.get(`/clubbed-cart/${clubbedOrderId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Add item to a user's cart within a clubbed order
  addItemToClubbedCart: async (clubbedOrderId, itemData) => {
    try {
      const response = await api.post(`/clubbed-cart/${clubbedOrderId}/items`, itemData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};

export const joinClubQueue = async (cartId, lat, lng, timeout = 5) => {
  try {
    const token = localStorage.getItem('token');
    const res = await api.post('/club/join-queue', {
      cart_id: cartId,
      lat,
      lng,
      timeout_minutes: timeout
    }, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.data;
  } catch (error) {
    console.error('Error joining club queue:', error.response ? error.response.data : error.message);
    throw error;
  }
};

export const checkClubStatus = async (buddyQueueId) => {
  try {
    const token = localStorage.getItem('token');
    const res = await api.get(`/club/status/${buddyQueueId}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return res.data;
  } catch (error) {
    console.error('Error checking club status:', error.response ? error.response.data : error.message);
    throw error;
  }
};
