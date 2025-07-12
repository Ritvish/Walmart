import api from './api';

export const cartService = {
  // Get user's active cart
  getCart: async () => {
    try {
      const response = await api.get('/cart/');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Add item to cart
  addToCart: async (item) => {
    try {
      const response = await api.post('/cart/items', item);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get cart by ID
  getCartById: async (cartId) => {
    try {
      const response = await api.get(`/cart/${cartId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Calculate cart total
  calculateCartTotal: (cartItems) => {
    if (!cartItems || !Array.isArray(cartItems)) return 0;
    return cartItems.reduce((total, item) => {
      const itemTotal = parseFloat(item.total_price) || 0;
      return total + itemTotal;
    }, 0);
  },

  // Calculate cart weight
  calculateCartWeight: (cartItems) => {
    if (!cartItems || !Array.isArray(cartItems)) return 0;
    return cartItems.reduce((total, item) => {
      const weight = typeof item.product?.weight_grams === 'number' ? item.product.weight_grams : 0;
      const quantity = typeof item.quantity === 'number' ? item.quantity : 0;
      return total + (weight * quantity);
    }, 0);
  },

  // Remove item from cart
  removeFromCart: async (itemId) => {
    try {
      const response = await api.delete(`/cart/items/${itemId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Update item quantity in cart
  updateCartItemQuantity: async (itemId, quantity) => {
    try {
      const response = await api.put(`/cart/items/${itemId}/quantity`, { quantity });
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Clear all items from cart
  clearCart: async () => {
    try {
      const response = await api.delete('/cart/clear');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Delete the entire cart
  deleteCart: async () => {
    try {
      const response = await api.delete('/cart/');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};
