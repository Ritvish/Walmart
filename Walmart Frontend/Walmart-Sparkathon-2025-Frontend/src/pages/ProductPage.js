import React, { useState, useEffect } from 'react';
import { productService } from '../services/productService';
import { useCart } from '../context/CartContext';
import ProductCard from '../components/ProductCard';
import toast from 'react-hot-toast';

const ProductPage = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [addingToCart, setAddingToCart] = useState(null);
  
  const { addToCart, items, total } = useCart();

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const data = await productService.getProducts();
      setProducts(data);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = async (item) => {
    try {
      setAddingToCart(item.product_id);
      await addToCart(item);
      // Optimistically update the product stock in the UI
      setProducts((prevProducts) =>
        prevProducts.map((p) =>
          p.id === item.product_id && p.stock > 0
            ? { ...p, stock: p.stock - 1 }
            : p
        )
      );
      toast.success('Item added to cart!');
    } catch (error) {
      toast.error(error.detail || 'Failed to add item to cart');
    } finally {
      setAddingToCart(null);
    }
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>Products</h1>
        <div className="d-flex align-items-center gap-3">
          <div style={{ width: '300px' }}>
            <input
              type="text"
              placeholder="Search products..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="form-control"
            />
          </div>
          <a href="/cart" className="btn btn-primary">
            🛒 View Cart
          </a>
        </div>
      </div>

      {filteredProducts.length === 0 ? (
        <div className="text-center">
          <h3>No products found</h3>
          <p>Try adjusting your search term</p>
        </div>
      ) : (
        <div className="grid grid-4">
          {filteredProducts.map((product) => (
            <ProductCard
              key={product.id}
              product={product}
              onAddToCart={handleAddToCart}
              loading={addingToCart === product.id}
            />
          ))}
        </div>
      )}
      
      {/* Floating Cart Button */}
      {items && items.length > 0 && (
        <div style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          zIndex: 1000,
        }}>
          <a
            href="/cart"
            className="btn btn-primary"
            style={{
              borderRadius: '50px',
              padding: '12px 20px',
              fontSize: '16px',
              fontWeight: 'bold',
              boxShadow: '0 4px 12px rgba(0, 123, 255, 0.4)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            🛒 {items.length} items - ₹{(total || 0).toFixed(2)}
          </a>
        </div>
      )}
    </div>
  );
};

export default ProductPage;
