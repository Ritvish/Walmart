import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { clubService } from '../services/clubService';
import { productService } from '../services/productService';
import splitPaymentService from '../services/splitPaymentService';
import PrivacyNotice from '../components/PrivacyNotice';
import toast from 'react-hot-toast';

const ClubbedCartPage = () => {
  const { clubbedOrderId } = useParams();
  const navigate = useNavigate();
  const [clubbedCart, setClubbedCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [isAddingItem, setIsAddingItem] = useState(false);
  const [discountAmount, setDiscountAmount] = useState(0);

  useEffect(() => {
    console.log('🔍 ClubbedCartPage - clubbedOrderId:', clubbedOrderId);
    
    // Get discount amount from localStorage if available
    const savedDiscount = localStorage.getItem('discount_amount');
    if (savedDiscount) {
      setDiscountAmount(parseFloat(savedDiscount));
    }
    
    const fetchClubbedCart = async () => {
      try {
        console.log('🔍 Fetching clubbed cart for ID:', clubbedOrderId);
        
        const data = await clubService.getClubbedCart(clubbedOrderId);
        console.log('✅ Clubbed cart data received:', data);
        setClubbedCart(data);
        
        // Initialize split payment process if this is a newly created clubbed order
        if (data && data.status === 'CREATED') {
          console.log('🔄 Initializing split payment for clubbed order:', clubbedOrderId);
          try {
            const splitPaymentResult = await splitPaymentService.createUserOrders(clubbedOrderId);
            console.log('✅ Split payment initialized:', splitPaymentResult);
            toast.success('Payment process initialized! You have 10 minutes to commit.');
            
            // Redirect to split payment page
            setTimeout(() => {
              navigate(`/split-payment/${clubbedOrderId}`);
            }, 2000);
          } catch (splitError) {
            console.error('❌ Failed to initialize split payment:', splitError);
            toast.error('Failed to initialize payment process. Please try again.');
          }
        }
      } catch (error) {
        console.error('❌ Failed to fetch clubbed cart:', error);
        console.error('❌ Error details:', {
          message: error.message,
          response: error.response?.data,
          status: error.response?.status
        });
        toast.error('Failed to fetch clubbed cart details.');
      } finally {
        setLoading(false);
      }
    };

    const fetchProducts = async () => {
      try {
        const data = await productService.getProducts();
        setProducts(data);
      } catch (error) {
        console.error('❌ Failed to fetch products:', error);
        toast.error('Failed to fetch products.');
      }
    };

    fetchClubbedCart();
    fetchProducts();
  }, [clubbedOrderId]);

  const handleAddItem = async (e) => {
    e.preventDefault();
    if (!selectedProduct || quantity <= 0) {
      toast.error('Please select a product and quantity.');
      return;
    }
    
    setIsAddingItem(true);
    try {
      const itemData = {
        product_id: selectedProduct,
        quantity: quantity,
      };
      
      // Call the backend API to add item
      await clubService.addItemToClubbedCart(clubbedOrderId, itemData);
      
      // Refetch the clubbed cart data to get updated information
      const updatedData = await clubService.getClubbedCart(clubbedOrderId);
      setClubbedCart(updatedData);
      
      toast.success('Item added to your cart.');
      setSelectedProduct('');
      setQuantity(1);
    } catch (error) {
      console.error('❌ Failed to add item:', error);
      toast.error('Failed to add item.');
    } finally {
      setIsAddingItem(false);
    }
  };

  if (loading) {
    return (
      <div className="container mt-4">
        <div className="card text-center">
          <div className="card-body">
            <div className="loading">
              <div className="spinner"></div>
            </div>
            <h2>Loading Clubbed Cart...</h2>
            <p>Please wait while we fetch your clubbed cart details</p>
          </div>
        </div>
      </div>
    );
  }

  if (!clubbedCart) {
    return (
      <div className="container mt-4">
        <div className="card text-center">
          <div className="card-body">
            <h2>Could not load clubbed cart</h2>
            <p>There was an issue loading your clubbed cart details.</p>
            <p className="text-muted">Clubbed Order ID: {clubbedOrderId}</p>
            <button 
              className="btn btn-primary"
              onClick={() => window.location.href = '/cart'}
            >
              Back to Cart
            </button>
          </div>
        </div>
      </div>
    );
  }

  const { users, items, total_amount, status, other_users_total } = clubbedCart;
  const currentUser = JSON.parse(localStorage.getItem('user'));

  // Ensure total_amount is a number before using toFixed
  const numericTotalAmount = parseFloat(total_amount) || 0.0;
  const numericOtherUsersTotal = parseFloat(other_users_total) || 0.0;
  
  // Calculate current user's cart total
  const currentUserData = users.find(user => user.is_current_user);
  const currentUserTotal = currentUserData ? currentUserData.cart_total : 0.0;

  return (
    <div className="container mt-4">
      <h1>🎉 Clubbed Cart</h1>
      
      <PrivacyNotice type="clubbed" />
      
      {/* Status Banner */}
      <div className="alert alert-success mb-4">
        <h4>🎉 Order Combined Successfully!</h4>
        <p>Matched with {users.filter(u => !u.is_current_user).length} other shopper(s)</p>
        {discountAmount > 0 && <p>💰 Discount Applied: ₹{discountAmount.toFixed(2)}</p>}
      </div>
      
      {/* Cart Summary */}
      <div className="card mb-4">
        <div className="card-body">
          <h5 className="card-title">Combined Cart Summary</h5>
          <div className="row">
            <div className="col-md-3">
              <strong>Total Shoppers:</strong> {users.length}
            </div>
            <div className="col-md-3">
              <strong>Your Items:</strong> {items.length}
            </div>
            <div className="col-md-3">
              <strong>Your Cart Total:</strong> ₹{currentUserTotal.toFixed(2)}
            </div>
            <div className="col-md-3">
              <strong>Status:</strong> <span className="badge bg-success">{status}</span>
            </div>
          </div>
          <div className="row mt-2">
            <div className="col-md-6">
              <strong>Other Users' Total:</strong> ₹{numericOtherUsersTotal.toFixed(2)}
            </div>
            <div className="col-md-6">
              <strong>Combined Total:</strong> ₹{numericTotalAmount.toFixed(2)}
            </div>
          </div>
        </div>
      </div>

      {/* Users Summary */}
      <div className="card mb-4">
        <div className="card-header">
          <h5>👥 Users in this Order</h5>
        </div>
        <div className="card-body">
          {users.map((user, index) => (
            <div key={index} className="d-flex justify-content-between align-items-center border-bottom py-2">
              <div>
                <strong>{user.user_id}</strong>
                {user.is_current_user && <span className="badge bg-primary ms-2">You</span>}
              </div>
              <div className="text-end">
                <span className="badge bg-secondary me-2">{user.item_count} items</span>
                <span className="fw-bold">₹{user.cart_total.toFixed(2)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Your Items List */}
      <div className="card mb-4">
        <div className="card-header">
          <h5>🛒 Your Items ({items.length} items)</h5>
          <small className="text-muted">For privacy, other users' items are not displayed</small>
        </div>
        <div className="card-body">
          {items.length === 0 ? (
            <p className="text-muted">You haven't added any items yet.</p>
          ) : (
            items.map((item, index) => (
              <div key={index} className="d-flex justify-content-between align-items-center border-bottom py-2">
                <div>
                  <strong>{item.product_name}</strong>
                  <br />
                  <small className="text-muted">Added by: {item.added_by_user}</small>
                </div>
                <div className="text-end">
                  <span className="badge bg-primary me-2">Qty: {item.quantity}</span>
                  <span className="fw-bold">₹{item.price.toFixed(2)}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Add Item Section */}
      <div className="card mb-4" style={{ border: '2px dashed #28a745' }}>
        <div className="card-body">
          <h5 className="card-title text-success">Add More Items to Your Cart</h5>
          <form onSubmit={handleAddItem}>
            <div className="row">
              <div className="col-md-6 mb-3">
                <select 
                  className="form-control"
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                  required
                >
                  <option value="">Select a product</option>
                  {products.map(p => (
                    <option key={p.id} value={p.id}>{p.name} - ₹{p.price}</option>
                  ))}
                </select>
              </div>
              <div className="col-md-3 mb-3">
                <input 
                  type="number"
                  className="form-control"
                  value={quantity}
                  onChange={(e) => setQuantity(parseInt(e.target.value, 10))}
                  min="1"
                  required
                />
              </div>
              <div className="col-md-3 mb-3">
                <button 
                  type="submit" 
                  className="btn btn-success w-100"
                  disabled={isAddingItem}
                >
                  {isAddingItem ? 'Adding...' : 'Add to Combined Cart'}
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>

      {/* Checkout Button */}
      <div className="text-center">
        <button 
          className="btn btn-primary btn-lg"
          onClick={() => navigate(`/split-payment/${clubbedOrderId}`)}
        >
          Proceed to Split Payment - ₹{numericTotalAmount.toFixed(2)}
        </button>
      </div>
    </div>
  );
};

export default ClubbedCartPage;
