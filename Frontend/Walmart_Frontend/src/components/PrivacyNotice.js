import React from 'react';

const PrivacyNotice = ({ type = 'clubbed' }) => {
  if (type === 'clubbed') {
    return (
      <div className="alert alert-info d-flex align-items-center mb-3" style={{ fontSize: '14px' }}>
        <div style={{ marginRight: '8px' }}>🔒</div>
        <div>
          <strong>Privacy Protected:</strong> For your security, other users' personal information and individual items are hidden. 
          Only combined totals and anonymized user counts are displayed.
        </div>
      </div>
    );
  }

  if (type === 'checkout') {
    return (
      <div className="alert alert-secondary d-flex align-items-center mb-3" style={{ fontSize: '12px' }}>
        <div style={{ marginRight: '8px' }}>🔒</div>
        <div>
          <strong>Privacy Note:</strong> Other users' items and personal details are kept private. 
          You can only see combined order totals.
        </div>
      </div>
    );
  }

  return null;
};

export default PrivacyNotice;
