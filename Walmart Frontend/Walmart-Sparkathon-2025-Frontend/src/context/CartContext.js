import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { cartService } from '../services/cartService';
import { useAuth } from './AuthContext';

// Initial state
const initialState = {
  cart: null,
  items: [],
  total: 0,
  weight: 0,
  loading: false,
  error: null,
};

// Cart context
const CartContext = createContext();

// Cart reducer
const cartReducer = (state, action) => {
  switch (action.type) {
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload,
      };
    case 'SET_CART':
      return {
        ...state,
        cart: action.payload,
        items: action.payload.cart_items || [],
        total: action.payload.cart_items ? cartService.calculateCartTotal(action.payload.cart_items) : 0,
        weight: action.payload.cart_items ? cartService.calculateCartWeight(action.payload.cart_items) : 0,
        loading: false,
        error: null,
      };
    case 'ADD_ITEM':
      const newItems = [...state.items, action.payload];
      return {
        ...state,
        items: newItems,
        total: cartService.calculateCartTotal(newItems),
        weight: cartService.calculateCartWeight(newItems),
        loading: false,
        error: null,
      };
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false,
      };
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    case 'CLEAR_CART':
      return initialState;
    default:
      return state;
  }
};

// Cart provider component
export const CartProvider = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, initialState);
  const { isAuthenticated } = useAuth();

  // Load cart when user is authenticated
  useEffect(() => {
    if (isAuthenticated) {
      loadCart();
    } else {
      dispatch({ type: 'CLEAR_CART' });
    }
  }, [isAuthenticated]);

  // Load cart function
  const loadCart = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const cart = await cartService.getCart();
      console.log('🛒 Cart API Response:', cart);
      console.log('📦 Cart Items:', cart.cart_items);
      console.log('💰 Cart Total:', cartService.calculateCartTotal(cart.cart_items));
      dispatch({ type: 'SET_CART', payload: cart });
    } catch (error) {
      console.error('❌ Cart API Error:', error);
      dispatch({ type: 'SET_ERROR', payload: error.detail || 'Failed to load cart' });
    }
  };

  // Add item to cart function
  const addToCart = async (item) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const cartItem = await cartService.addToCart(item);
      console.log('➕ Add to Cart Response:', cartItem);
      dispatch({ type: 'ADD_ITEM', payload: cartItem });
      // Reload cart to get updated data
      await loadCart();
      return cartItem;
    } catch (error) {
      console.error('❌ Add to Cart Error:', error);
      dispatch({ type: 'SET_ERROR', payload: error.detail || 'Failed to add item to cart' });
      throw error;
    }
  };


  // Clear cart function
  const clearCart = () => {
    dispatch({ type: 'CLEAR_CART' });
  };

  // Clear error function
  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value = {
    ...state,
    loadCart,
    addToCart,
    clearCart,
    clearError,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

// Custom hook to use cart context
export const useCart = () => {
  const context = useContext(CartContext);
  if (!context) {
    throw new Error('useCart must be used within a CartProvider');
  }
  return context;
};
