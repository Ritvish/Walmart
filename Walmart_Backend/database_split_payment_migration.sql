-- Migration script for Split Payment System
-- This script is now idempotent and can be run multiple times safely.

-- Stored procedure to add a column if it doesn't exist
DROP PROCEDURE IF EXISTS AddColumnIfNotExists;
DELIMITER //
CREATE PROCEDURE AddColumnIfNotExists(
    IN db_name VARCHAR(255),
    IN tbl_name VARCHAR(255),
    IN col_name VARCHAR(255),
    IN col_spec VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (
        SELECT * FROM information_schema.columns 
        WHERE table_schema = db_name AND table_name = tbl_name AND column_name = col_name
    )
    THEN
        SET @ddl = CONCAT('ALTER TABLE ', tbl_name, ' ADD COLUMN ', col_name, ' ', col_spec);
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //
DELIMITER ;

-- Use the procedure to add columns to clubbed_orders
CALL AddColumnIfNotExists(DATABASE(), 'clubbed_orders', 'all_payments_confirmed', 'BOOLEAN DEFAULT FALSE');
CALL AddColumnIfNotExists(DATABASE(), 'clubbed_orders', 'payment_confirmation_deadline', 'TIMESTAMP NULL');
CALL AddColumnIfNotExists(DATABASE(), 'clubbed_orders', 'order_confirmed_at', 'TIMESTAMP NULL');

-- Drop the procedure as it's no longer needed
DROP PROCEDURE AddColumnIfNotExists;


-- Create user_orders table if it doesn't exist
CREATE TABLE IF NOT EXISTS user_orders (
    id VARCHAR(36) PRIMARY KEY,
    clubbed_order_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    cart_id VARCHAR(36) NOT NULL,
    individual_total DECIMAL(10,2) NOT NULL,
    payment_method ENUM('ONLINE', 'COD') NOT NULL,
    payment_status ENUM('PENDING', 'CONFIRMED', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    payment_confirmed_at TIMESTAMP NULL,
    commitment_deadline TIMESTAMP NOT NULL,
    is_committed BOOLEAN DEFAULT FALSE,
    committed_at TIMESTAMP NULL,
    delivery_address TEXT NOT NULL,
    delivery_phone VARCHAR(20) NOT NULL,
    special_instructions TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (clubbed_order_id) REFERENCES clubbed_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (cart_id) REFERENCES carts(id)
);

-- Create order_cancellations table if it doesn't exist
CREATE TABLE IF NOT EXISTS order_cancellations (
    id VARCHAR(36) PRIMARY KEY,
    user_order_id VARCHAR(36) NOT NULL,
    clubbed_order_id VARCHAR(36) NOT NULL,
    cancelled_by_user_id VARCHAR(36) NOT NULL,
    cancellation_reason ENUM('PAYMENT_FAILED', 'USER_WITHDREW', 'TIMEOUT', 'SYSTEM_ERROR'),
    cancelled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    cancellation_fee DECIMAL(10,2) DEFAULT 0.0,
    compensation_amount DECIMAL(10,2) DEFAULT 0.0,
    company_penalty_share DECIMAL(10,2) DEFAULT 0.0,
    penalty_processed BOOLEAN DEFAULT FALSE,
    compensation_processed BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_order_id) REFERENCES user_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (clubbed_order_id) REFERENCES clubbed_orders(id),
    FOREIGN KEY (cancelled_by_user_id) REFERENCES users(id)
);

-- Create payment_transactions table if it doesn't exist
CREATE TABLE IF NOT EXISTS payment_transactions (
    id VARCHAR(36) PRIMARY KEY,
    user_order_id VARCHAR(36) NOT NULL,
    user_id VARCHAR(36) NOT NULL,
    transaction_type ENUM('PAYMENT', 'REFUND', 'PENALTY', 'COMPENSATION'),
    amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('ONLINE', 'COD', 'WALLET'),
    external_transaction_id VARCHAR(100),
    payment_gateway VARCHAR(50),
    status ENUM('PENDING', 'SUCCESS', 'FAILED', 'CANCELLED') DEFAULT 'PENDING',
    processed_at TIMESTAMP NULL,
    failure_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_order_id) REFERENCES user_orders(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Stored procedure to add an index if it doesn't exist
DROP PROCEDURE IF EXISTS AddIndexIfNotExists;
DELIMITER //
CREATE PROCEDURE AddIndexIfNotExists(
    IN db_name VARCHAR(255),
    IN tbl_name VARCHAR(255),
    IN idx_name VARCHAR(255),
    IN idx_cols VARCHAR(255)
)
BEGIN
    IF NOT EXISTS (
        SELECT * FROM information_schema.statistics 
        WHERE table_schema = db_name AND table_name = tbl_name AND index_name = idx_name
    )
    THEN
        SET @ddl = CONCAT('CREATE INDEX ', idx_name, ' ON ', tbl_name, ' (', idx_cols, ')');
        PREPARE stmt FROM @ddl;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
    END IF;
END //
DELIMITER ;

-- Use the procedure to add indexes
CALL AddIndexIfNotExists(DATABASE(), 'user_orders', 'idx_user_orders_clubbed_order', 'clubbed_order_id');
CALL AddIndexIfNotExists(DATABASE(), 'user_orders', 'idx_user_orders_user', 'user_id');
CALL AddIndexIfNotExists(DATABASE(), 'user_orders', 'idx_user_orders_payment_status', 'payment_status');
CALL AddIndexIfNotExists(DATABASE(), 'order_cancellations', 'idx_order_cancellations_clubbed_order', 'clubbed_order_id');
CALL AddIndexIfNotExists(DATABASE(), 'payment_transactions', 'idx_payment_transactions_user_order', 'user_order_id');
CALL AddIndexIfNotExists(DATABASE(), 'payment_transactions', 'idx_payment_transactions_user', 'user_id');
CALL AddIndexIfNotExists(DATABASE(), 'payment_transactions', 'idx_payment_transactions_status', 'status');

-- Drop the procedure as it's no longer needed
DROP PROCEDURE AddIndexIfNotExists;

-- Sample data for testing (optional)
-- You can uncomment this if you want to test with sample data

/*
-- Insert sample user orders (make sure you have existing clubbed orders and users)
INSERT INTO user_orders (id, clubbed_order_id, user_id, cart_id, individual_total, payment_method, commitment_deadline, delivery_address, delivery_phone) 
VALUES 
('test-user-order-1', 'existing-clubbed-order-id', 'existing-user-id-1', 'existing-cart-id-1', 455.00, 'ONLINE', DATE_ADD(NOW(), INTERVAL 15 MINUTE), '123 Test Street, Mumbai', '+91-9876543210'),
('test-user-order-2', 'existing-clubbed-order-id', 'existing-user-id-2', 'existing-cart-id-2', 1245.00, 'COD', DATE_ADD(NOW(), INTERVAL 15 MINUTE), '456 Another Street, Mumbai', '+91-9876543211');
*/
