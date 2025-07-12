import React from 'react';

const ProductCard = ({ product, onAddToCart, loading }) => {
  const handleAddToCart = () => {
    onAddToCart({
      product_id: product.id,
      quantity: 1,
      total_price: product.price,
    });
  };

  return (
    <div className="card">
      <div style={{ position: 'relative' }}>
        {product.image_url && (
          <img
            src={product.image_url}
            alt={product.name}
            style={{
              width: '100%',
              height: '200px',
              objectFit: 'cover',
              borderRadius: '8px',
              marginBottom: '12px',
            }}
          />
        )}
        {product.stock <= 0 && (
          <div style={{
            position: 'absolute',
            top: '10px',
            right: '10px',
            background: '#dc3545',
            color: 'white',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '12px',
          }}>
            Out of Stock
          </div>
        )}
      </div>
      
      <div>
        <h3 style={{ fontSize: '16px', margin: '0 0 8px 0' }}>
          {product.name}
        </h3>
        
        <div className="d-flex justify-content-between align-items-center mb-2">
          <span style={{ fontSize: '18px', fontWeight: 'bold', color: '#28a745' }}>
            ₹{product.price}
          </span>
          <span style={{ fontSize: '12px', color: '#666' }}>
            {product.weight_grams}g
          </span>
        </div>
        
        <div className="d-flex justify-content-between align-items-center">
          <span style={{ fontSize: '12px', color: product.stock > 0 ? '#28a745' : '#dc3545' }}>
            {product.stock > 0 ? `${product.stock} in stock` : 'Out of stock'}
          </span>
          
          <button
            onClick={handleAddToCart}
            disabled={product.stock <= 0 || loading}
            className={`btn ${product.stock > 0 ? 'btn-primary' : 'btn-secondary'}`}
            style={{ padding: '6px 12px', fontSize: '12px' }}
          >
            {loading ? 'Adding...' : 'Add to Cart'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
