import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { clubService } from '../services/clubService';
import { productService } from '../services/productService';
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
        
        // Add test data for development - remove when backend is ready
        if (clubbedOrderId === 'test-clubbed-order-id') {
          console.log('🧪 Using test data for clubbed cart');
          const testData = {
            clubbed_order_id: 'test-clubbed-order-id',
            status: 'ACTIVE',
            total_amount: 1700.00,
            users: ['You', 'Buddy User'],
            items: [
              { product_name: 'Organic Bananas', quantity: 2, price: 120.00, added_by_user: 'You' },
              { product_name: 'Almond Milk', quantity: 1, price: 250.00, added_by_user: 'You' },
              { product_name: 'Whole Wheat Bread', quantity: 1, price: 85.00, added_by_user: 'You' },
              { product_name: 'Avocado (Pack of 4)', quantity: 1, price: 480.00, added_by_user: 'Buddy User' },
              { product_name: 'Greek Yogurt', quantity: 2, price: 340.00, added_by_user: 'Buddy User' },
              { product_name: 'Quinoa', quantity: 1, price: 425.00, added_by_user: 'Buddy User' }
            ]
          };
          setClubbedCart(testData);
          setLoading(false);
          return;
        }
        
        const data = await clubService.getClubbedCart(clubbedOrderId);
        console.log('✅ Clubbed cart data received:', data);
        setClubbedCart(data);
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

  const { users, items, total_amount, status } = clubbedCart;
  const currentUser = JSON.parse(localStorage.getItem('user'));

  // Ensure total_amount is a number before using toFixed
  const numericTotalAmount = parseFloat(total_amount) || 0.0;

  return (
    <div className="container mt-4">
      <h1>🎉 Clubbed Cart</h1>
      
      {/* Status Banner */}
      <div className="alert alert-success mb-4">
        <h4>Order Combined Successfully!</h4>
        <p>Matched with {users.length - 1} other shopper(s)</p>
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
              <strong>Total Items:</strong> {items.length}
            </div>
            <div className="col-md-3">
              <strong>Total Amount:</strong> ₹{numericTotalAmount.toFixed(2)}
            </div>
            <div className="col-md-3">
              <strong>Status:</strong> <span className="badge bg-success">{status}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Combined Items List */}
      <div className="card mb-4">
        <div className="card-header">
          <h5>All Items ({items.length} items)</h5>
        </div>
        <div className="card-body">
          {items.map((item, index) => (
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
          ))}
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
          onClick={() => navigate(`/checkout?clubbedOrderId=${clubbedOrderId}`)}
        >
          Proceed to Checkout - ₹{numericTotalAmount.toFixed(2)}
        </button>
      </div>
    </div>
  );
};

export default ClubbedCartPage;
