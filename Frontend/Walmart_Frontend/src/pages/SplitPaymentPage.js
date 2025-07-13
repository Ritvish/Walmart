import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import splitPaymentService from '../services/splitPaymentService';
import toast from 'react-hot-toast';

const SplitPaymentPage = () => {
  const { clubbedOrderId } = useParams();
  const navigate = useNavigate();
  
  const [paymentSummary, setPaymentSummary] = useState(null);
  const [commitmentStatus, setCommitmentStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [committing, setCommitting] = useState(false);
  const [confirming, setConfirming] = useState(false);
  
  // Form state
  const [paymentMethod, setPaymentMethod] = useState('ONLINE');
  const [deliveryAddress, setDeliveryAddress] = useState('');
  const [deliveryPhone, setDeliveryPhone] = useState('');
  const [specialInstructions, setSpecialInstructions] = useState('');
  
  // User order state
  const [userOrderId, setUserOrderId] = useState(null);
  const [isCommitted, setIsCommitted] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState('PENDING');

  useEffect(() => {
    fetchData();
    
    // Poll for status updates every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, [clubbedOrderId]);

  const fetchData = async () => {
    try {
      // First, ensure user orders are created for this clubbed order
      let summary, status;
      try {
        [summary, status] = await Promise.all([
          splitPaymentService.getPaymentSummary(clubbedOrderId),
          splitPaymentService.getCommitmentStatus(clubbedOrderId)
        ]);
      } catch (error) {
        // If payment summary doesn't exist, create user orders first
        if (error.response?.status === 404) {
          console.log('User orders not found, creating them...');
          await splitPaymentService.createUserOrders(clubbedOrderId);
          
          // Now try again
          [summary, status] = await Promise.all([
            splitPaymentService.getPaymentSummary(clubbedOrderId),
            splitPaymentService.getCommitmentStatus(clubbedOrderId)
          ]);
        } else {
          throw error;
        }
      }
      
      setPaymentSummary(summary);
      setCommitmentStatus(status);
      
      // Get user orders to find current user's order
      const userOrders = await splitPaymentService.getMyOrders();
      const currentUserOrder = userOrders.find(order => order.clubbed_order_id === clubbedOrderId);
      
      if (currentUserOrder) {
        setUserOrderId(currentUserOrder.id);
        setIsCommitted(currentUserOrder.is_committed);
        setPaymentStatus(currentUserOrder.payment_status);
        
        // Pre-fill form if already committed
        if (currentUserOrder.is_committed) {
          setPaymentMethod(currentUserOrder.payment_method);
          setDeliveryAddress(currentUserOrder.delivery_address);
          setDeliveryPhone(currentUserOrder.delivery_phone);
          setSpecialInstructions(currentUserOrder.special_instructions || '');
        }
      }
      
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch data:', error);
      toast.error('Failed to load payment details');
      setLoading(false);
    }
  };

  const handleCommitToPayment = async () => {
    if (!deliveryAddress || !deliveryPhone) {
      toast.error('Please fill in all required fields');
      return;
    }

    setCommitting(true);
    try {
      await splitPaymentService.commitToPayment(
        userOrderId,
        paymentMethod,
        deliveryAddress,
        deliveryPhone,
        specialInstructions
      );
      
      toast.success('Payment commitment successful!');
      setIsCommitted(true);
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Failed to commit to payment:', error);
      toast.error('Failed to commit to payment');
    } finally {
      setCommitting(false);
    }
  };

  const handleConfirmPayment = async () => {
    setConfirming(true);
    try {
      if (paymentMethod === 'ONLINE') {
        // Simulate online payment gateway
        const mockTransactionId = 'TXN_' + Date.now();
        await splitPaymentService.confirmPayment(userOrderId, mockTransactionId, 'mock_gateway');
      } else {
        // COD payment
        await splitPaymentService.confirmPayment(userOrderId);
      }
      
      toast.success('Payment confirmed successfully!');
      setPaymentStatus('CONFIRMED');
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Failed to confirm payment:', error);
      toast.error('Failed to confirm payment');
    } finally {
      setConfirming(false);
    }
  };

  const handleCancelOrder = async () => {
    if (!window.confirm('Are you sure you want to cancel? A cancellation fee will be charged.')) {
      return;
    }

    try {
      const cancellation = await splitPaymentService.cancelOrder(userOrderId);
      toast.error(`Order cancelled. Cancellation fee: ₹${cancellation.cancellation_fee}`);
      navigate('/cart');
    } catch (error) {
      console.error('Failed to cancel order:', error);
      toast.error('Failed to cancel order');
    }
  };

  const isDeadlinePassed = () => {
    if (!paymentSummary?.payment_deadline) return false;
    return new Date() > new Date(paymentSummary.payment_deadline);
  };

  const getTimeRemaining = () => {
    if (!paymentSummary?.payment_deadline) return '';
    const deadline = new Date(paymentSummary.payment_deadline);
    const now = new Date();
    const diff = deadline - now;
    
    if (diff <= 0) return 'Deadline passed';
    
    const minutes = Math.floor(diff / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  if (loading) {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <div className="card-body">
            <div className="loading">
              <div className="spinner"></div>
            </div>
            <h2>Loading Split Payment Details...</h2>
          </div>
        </div>
      </div>
    );
  }

  if (!paymentSummary) {
    return (
      <div className="container" style={{ padding: '20px' }}>
        <div className="card text-center">
          <div className="card-body">
            <h2>Payment Details Not Found</h2>
            <p>Could not load payment details for this order.</p>
            <button className="btn btn-primary" onClick={() => navigate('/cart')}>
              Back to Cart
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container" style={{ padding: '20px' }}>
      <h1>💰 Split Payment - Clubbed Order</h1>
      
      {/* Payment Summary */}
      <div className="card mb-4">
        <div className="card-header">
          <h5>Payment Summary</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-6">
              <p><strong>Your Portion:</strong> ₹{paymentSummary.your_portion.toFixed(2)}</p>
              <p><strong>Delivery Fee:</strong> ₹{paymentSummary.delivery_fee.toFixed(2)}</p>
              <p><strong>Discount Applied:</strong> -₹{paymentSummary.discount_applied.toFixed(2)}</p>
              <hr />
              <p><strong>Final Amount to Pay:</strong> ₹{paymentSummary.final_amount_to_pay.toFixed(2)}</p>
            </div>
            <div className="col-md-6">
              <p><strong>Total Order Value:</strong> ₹{paymentSummary.total_order_value.toFixed(2)}</p>
              <p><strong>Other Users' Portion:</strong> ₹{paymentSummary.other_users_portion.toFixed(2)}</p>
              <p><strong>Payment Deadline:</strong> {getTimeRemaining()}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Commitment Status */}
      <div className="card mb-4">
        <div className="card-header">
          <h5>Order Status</h5>
        </div>
        <div className="card-body">
          <div className="row">
            <div className="col-md-6">
              <p><strong>Confirmed Payments:</strong> {paymentSummary.confirmed_payments}</p>
              <p><strong>Pending Payments:</strong> {paymentSummary.pending_payments}</p>
            </div>
            <div className="col-md-6">
              <p><strong>All Users Committed:</strong> 
                <span className={`badge ${paymentSummary.all_users_committed ? 'bg-success' : 'bg-warning'} ms-2`}>
                  {paymentSummary.all_users_committed ? 'Yes' : 'No'}
                </span>
              </p>
              <p><strong>Order Confirmed:</strong> 
                <span className={`badge ${commitmentStatus?.order_confirmed ? 'bg-success' : 'bg-secondary'} ms-2`}>
                  {commitmentStatus?.order_confirmed ? 'Yes' : 'No'}
                </span>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Payment Form */}
      {!isCommitted && !isDeadlinePassed() && (
        <div className="card mb-4">
          <div className="card-header">
            <h5>Commit to Payment</h5>
          </div>
          <div className="card-body">
            <div className="row">
              <div className="col-md-6">
                <div className="form-group mb-3">
                  <label className="form-label">Payment Method *</label>
                  <select 
                    className="form-control"
                    value={paymentMethod}
                    onChange={(e) => setPaymentMethod(e.target.value)}
                  >
                    <option value="ONLINE">Online Payment</option>
                    <option value="COD">Cash on Delivery</option>
                  </select>
                </div>
                
                <div className="form-group mb-3">
                  <label className="form-label">Phone Number *</label>
                  <input
                    type="tel"
                    className="form-control"
                    value={deliveryPhone}
                    onChange={(e) => setDeliveryPhone(e.target.value)}
                    placeholder="Enter your phone number"
                    required
                  />
                </div>
              </div>
              
              <div className="col-md-6">
                <div className="form-group mb-3">
                  <label className="form-label">Delivery Address *</label>
                  <textarea
                    className="form-control"
                    value={deliveryAddress}
                    onChange={(e) => setDeliveryAddress(e.target.value)}
                    placeholder="Enter your complete delivery address"
                    rows="3"
                    required
                  />
                </div>
                
                <div className="form-group mb-3">
                  <label className="form-label">Special Instructions</label>
                  <textarea
                    className="form-control"
                    value={specialInstructions}
                    onChange={(e) => setSpecialInstructions(e.target.value)}
                    placeholder="Any special delivery instructions"
                    rows="2"
                  />
                </div>
              </div>
            </div>
            
            <div className="d-flex justify-content-between">
              <button 
                className="btn btn-primary"
                onClick={handleCommitToPayment}
                disabled={committing || !deliveryAddress || !deliveryPhone}
              >
                {committing ? 'Committing...' : 'Commit to Payment'}
              </button>
              
              <button 
                className="btn btn-danger"
                onClick={handleCancelOrder}
              >
                Cancel Order
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Payment Confirmation */}
      {isCommitted && paymentStatus === 'PENDING' && (
        <div className="card mb-4">
          <div className="card-header">
            <h5>Confirm Payment</h5>
          </div>
          <div className="card-body">
            <div className="alert alert-info">
              <strong>Payment Method:</strong> {paymentMethod}<br />
              <strong>Amount to Pay:</strong> ₹{paymentSummary.final_amount_to_pay.toFixed(2)}
            </div>
            
            {paymentMethod === 'ONLINE' && (
              <div className="alert alert-warning">
                <strong>Online Payment:</strong> You will be redirected to the payment gateway after clicking confirm.
              </div>
            )}
            
            {paymentMethod === 'COD' && (
              <div className="alert alert-info">
                <strong>Cash on Delivery:</strong> You will pay ₹{paymentSummary.final_amount_to_pay.toFixed(2)} when the order is delivered.
              </div>
            )}
            
            <button 
              className="btn btn-success"
              onClick={handleConfirmPayment}
              disabled={confirming}
            >
              {confirming ? 'Confirming...' : `Confirm Payment - ₹${paymentSummary.final_amount_to_pay.toFixed(2)}`}
            </button>
          </div>
        </div>
      )}

      {/* Payment Confirmed */}
      {paymentStatus === 'CONFIRMED' && (
        <div className="card mb-4">
          <div className="card-body text-center">
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>✅</div>
            <h3>Payment Confirmed!</h3>
            <p>Your payment has been confirmed. Waiting for other users to complete their payments.</p>
            
            {commitmentStatus?.order_confirmed && (
              <div className="alert alert-success">
                <strong>🎉 Order Confirmed!</strong> All payments received. Your order is being prepared.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Deadline Passed */}
      {isDeadlinePassed() && !isCommitted && (
        <div className="card mb-4">
          <div className="card-body text-center">
            <div style={{ fontSize: '48px', marginBottom: '20px' }}>⏰</div>
            <h3>Payment Deadline Passed</h3>
            <p>The payment commitment deadline has passed. This order has been cancelled.</p>
            <button 
              className="btn btn-primary"
              onClick={() => navigate('/cart')}
            >
              Back to Cart
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SplitPaymentPage;
