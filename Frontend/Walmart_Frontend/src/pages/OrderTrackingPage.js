import React, { useState, useEffect } from 'react';
import { orderService } from '../services/orderService';

const OrderTrackingPage = () => {
  const [orderStatus, setOrderStatus] = useState({
    id: 'ORDER-' + Date.now(),
    status: 'preparing',
    items: [
      { name: 'Onion 450-500g', quantity: 1, price: 9 },
      { name: 'Cucumber Local 2 Units', quantity: 1, price: 9 },
      { name: 'Amul Milk 1L', quantity: 1, price: 65 },
    ],
    total: 157.50,
    clubbed: true,
    buddyCount: 2,
    driver: {
      name: 'Raj Kumar',
      phone: '+91 98765 43210',
      vehicle: 'Bike - MH12AB1234',
    },
    timeline: [
      { status: 'Order Placed', time: '10:30 AM', completed: true },
      { status: 'Being Prepared', time: '10:35 AM', completed: true },
      { status: 'Out for Delivery', time: '10:50 AM', completed: false },
      { status: 'Delivered', time: 'Expected by 11:15 AM', completed: false },
    ],
  });

  const [currentStep, setCurrentStep] = useState(1);

  useEffect(() => {
    // Simulate real-time updates
    const interval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev < 3) {
          const newStep = prev + 1;
          setOrderStatus(prevStatus => ({
            ...prevStatus,
            status: newStep === 2 ? 'dispatched' : newStep === 3 ? 'delivered' : 'preparing',
            timeline: prevStatus.timeline.map((item, index) => ({
              ...item,
              completed: index <= newStep,
            })),
          }));
          return newStep;
        }
        return prev;
      });
    }, 30000); // Update every 30 seconds

    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status) => {
    switch (status) {
      case 'preparing':
        return '#ffc107';
      case 'dispatched':
        return '#007bff';
      case 'delivered':
        return '#28a745';
      default:
        return '#6c757d';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'preparing':
        return 'Being Prepared';
      case 'dispatched':
        return 'Out for Delivery';
      case 'delivered':
        return 'Delivered';
      default:
        return 'Processing';
    }
  };

  return (
    <div className="container" style={{ padding: '20px' }}>
      <h1 style={{ marginBottom: '20px' }}>Track Your Order</h1>
      
      <div className="grid grid-2">
        <div>
          <div className="card">
            <h3>Order Status</h3>
            <div className="d-flex align-items-center" style={{ marginBottom: '20px' }}>
              <div style={{
                width: '20px',
                height: '20px',
                borderRadius: '50%',
                backgroundColor: getStatusColor(orderStatus.status),
                marginRight: '12px',
              }}></div>
              <div>
                <div style={{ fontWeight: 'bold', fontSize: '18px' }}>
                  {getStatusText(orderStatus.status)}
                </div>
                <div style={{ fontSize: '14px', color: '#666' }}>
                  Order #{orderStatus.id}
                </div>
              </div>
            </div>
            
            {orderStatus.clubbed && (
              <div className="alert alert-info" style={{ marginBottom: '20px' }}>
                <h4>🤝 Clubbed Delivery</h4>
                <p>Your order is being delivered with {orderStatus.buddyCount} other club members</p>
              </div>
            )}
            
            <div>
              <h4>Timeline</h4>
              {orderStatus.timeline.map((item, index) => (
                <div key={index} className="d-flex align-items-center" style={{ marginBottom: '12px' }}>
                  <div style={{
                    width: '12px',
                    height: '12px',
                    borderRadius: '50%',
                    backgroundColor: item.completed ? '#28a745' : '#dee2e6',
                    marginRight: '12px',
                  }}></div>
                  <div style={{ flex: 1 }}>
                    <div style={{ 
                      fontWeight: item.completed ? 'bold' : 'normal',
                      color: item.completed ? '#000' : '#666',
                    }}>
                      {item.status}
                    </div>
                    <div style={{ fontSize: '12px', color: '#666' }}>
                      {item.time}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
          
          {orderStatus.driver && orderStatus.status === 'dispatched' && (
            <div className="card">
              <h3>Delivery Partner</h3>
              <div className="d-flex align-items-center" style={{ marginBottom: '12px' }}>
                <div style={{
                  width: '50px',
                  height: '50px',
                  borderRadius: '50%',
                  backgroundColor: '#007bff',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontSize: '20px',
                  fontWeight: 'bold',
                  marginRight: '12px',
                }}>
                  {orderStatus.driver.name.charAt(0)}
                </div>
                <div>
                  <div style={{ fontWeight: 'bold' }}>
                    {orderStatus.driver.name}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>
                    {orderStatus.driver.vehicle}
                  </div>
                </div>
              </div>
              
              <div className="d-flex gap-2">
                <button className="btn btn-success" style={{ flex: 1 }}>
                  📞 Call Driver
                </button>
                <button className="btn btn-primary" style={{ flex: 1 }}>
                  💬 Chat
                </button>
              </div>
            </div>
          )}
        </div>
        
        <div>
          <div className="card">
            <h3>Order Details</h3>
            <div style={{ marginBottom: '20px' }}>
              {orderStatus.items.map((item, index) => (
                <div key={index} className="d-flex justify-content-between align-items-center" style={{ marginBottom: '8px' }}>
                  <div>
                    <div>{item.name}</div>
                    <div style={{ fontSize: '14px', color: '#666' }}>
                      Qty: {item.quantity}
                    </div>
                  </div>
                  <div style={{ fontWeight: 'bold' }}>
                    ₹{item.price}
                  </div>
                </div>
              ))}
            </div>
            
            <div style={{ borderTop: '1px solid #eee', paddingTop: '16px' }}>
              <div className="d-flex justify-content-between" style={{ fontSize: '18px', fontWeight: 'bold' }}>
                <span>Total:</span>
                <span>₹{orderStatus.total}</span>
              </div>
            </div>
          </div>
          
          <div className="card">
            <h3>Delivery Information</h3>
            <p>
              <strong>Estimated Delivery:</strong> 11:15 AM
            </p>
            <p>
              <strong>Delivery Address:</strong><br />
              Block B, Jaypee Greens, Meerut Division<br />
              Uttar Pradesh, India
            </p>
            <p style={{ fontSize: '14px', color: '#666' }}>
              You'll receive SMS updates when your order status changes
            </p>
          </div>
          
          <div className="card">
            <h3>Need Help?</h3>
            <div className="d-flex gap-2">
              <button className="btn btn-secondary" style={{ flex: 1 }}>
                Contact Support
              </button>
              <button className="btn btn-primary" style={{ flex: 1 }}>
                Report Issue
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OrderTrackingPage;
