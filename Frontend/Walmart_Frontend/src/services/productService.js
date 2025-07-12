import api from './api';

export const productService = {
  // Get all products
  getProducts: async () => {
    try {
      const response = await api.get('/products/');
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Get product by ID
  getProductById: async (id) => {
    try {
      const response = await api.get(`/products/${id}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },

  // Create new product (admin only)
  createProduct: async (productData) => {
    try {
      const response = await api.post('/products/', productData);
      return response.data;
    } catch (error) {
      throw error.response?.data || error.message;
    }
  },
};
