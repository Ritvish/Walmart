import api from './api';

export const orderService = {
  // Get user's orders
  getUserOrders: async () => {
    try {
      const response = await api.get('/orders/');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get order by ID
  getOrderById: async (orderId) => {
    try {
      const response = await api.get(`/orders/${orderId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get delivery status
  getDeliveryStatus: async (orderId) => {
    try {
      const response = await api.get(`/orders/${orderId}/delivery`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};
