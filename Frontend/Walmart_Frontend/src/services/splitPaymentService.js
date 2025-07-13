import api from './api';

const splitPaymentService = {
  // Create user orders for a clubbed order
  createUserOrders: async (clubbedOrderId) => {
    try {
      const response = await api.post(`/split-payment/create-user-orders/${clubbedOrderId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to create user orders:', error);
      throw error;
    }
  },

  // Commit to payment with delivery details
  commitToPayment: async (userOrderId, paymentMethod, deliveryAddress, deliveryPhone, specialInstructions = null) => {
    try {
      const response = await api.post('/split-payment/commit', {
        user_order_id: userOrderId,
        payment_method: paymentMethod,
        delivery_address: deliveryAddress,
        delivery_phone: deliveryPhone,
        special_instructions: specialInstructions
      });
      return response.data;
    } catch (error) {
      console.error('Failed to commit to payment:', error);
      throw error;
    }
  },

  // Confirm payment
  confirmPayment: async (userOrderId, externalTransactionId = null, paymentGateway = null) => {
    try {
      const response = await api.post('/split-payment/confirm', {
        user_order_id: userOrderId,
        external_transaction_id: externalTransactionId,
        payment_gateway: paymentGateway
      });
      return response.data;
    } catch (error) {
      console.error('Failed to confirm payment:', error);
      throw error;
    }
  },

  // Cancel order
  cancelOrder: async (userOrderId, cancellationReason = 'USER_WITHDREW') => {
    try {
      const response = await api.post('/split-payment/cancel', {
        user_order_id: userOrderId,
        cancellation_reason: cancellationReason
      });
      return response.data;
    } catch (error) {
      console.error('Failed to cancel order:', error);
      throw error;
    }
  },

  // Get payment summary
  getPaymentSummary: async (clubbedOrderId) => {
    try {
      const response = await api.get(`/split-payment/summary/${clubbedOrderId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get payment summary:', error);
      throw error;
    }
  },

  // Get commitment status
  getCommitmentStatus: async (clubbedOrderId) => {
    try {
      const response = await api.get(`/split-payment/status/${clubbedOrderId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get commitment status:', error);
      throw error;
    }
  },

  // Get user transactions
  getUserTransactions: async (userOrderId) => {
    try {
      const response = await api.get(`/split-payment/transactions/${userOrderId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get transactions:', error);
      throw error;
    }
  },

  // Get user's orders
  getMyOrders: async () => {
    try {
      const response = await api.get('/split-payment/my-orders');
      return response.data;
    } catch (error) {
      console.error('Failed to get user orders:', error);
      throw error;
    }
  }
};

export default splitPaymentService;
