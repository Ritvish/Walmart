-- BuddyCart Database Setup Script
-- Run this script in phpMyAdmin to create the database and tables

-- Create database
CREATE DATABASE IF NOT EXISTS buddycart;
USE buddycart;

-- Users table
CREATE TABLE users (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table
CREATE TABLE products (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    weight_grams INT NOT NULL,
    stock INT DEFAULT 0,
    image_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Carts table
CREATE TABLE carts (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Cart items table
CREATE TABLE cart_items (
    id VARCHAR(36) PRIMARY KEY,
    cart_id VARCHAR(36),
    product_id VARCHAR(36),
    quantity INT NOT NULL,
    total_price DECIMAL(10,2),
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Buddy queue table
CREATE TABLE buddy_queue (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    cart_id VARCHAR(36),
    value_total DECIMAL(10,2) NOT NULL,
    weight_total DECIMAL(10,2) NOT NULL,
    lat DECIMAL(9,6) NOT NULL,
    lng DECIMAL(9,6) NOT NULL,
    location_hash VARCHAR(20),
    status ENUM('waiting', 'matched', 'timed_out') DEFAULT 'waiting',
    timeout_minutes INT NOT NULL DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (cart_id) REFERENCES carts(id) ON DELETE CASCADE
);

-- Clubbed orders table
CREATE TABLE clubbed_orders (
    id VARCHAR(36) PRIMARY KEY,
    combined_value DECIMAL(10,2),
    combined_weight DECIMAL(10,2),
    total_discount DECIMAL(10,2),
    status ENUM('created', 'preparing', 'dispatched', 'delivered') DEFAULT 'created',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Clubbed order users table
CREATE TABLE clubbed_order_users (
    id VARCHAR(36) PRIMARY KEY,
    clubbed_order_id VARCHAR(36),
    user_id VARCHAR(36),
    cart_id VARCHAR(36),
    share_value DECIMAL(10,2),
    discount_given DECIMAL(10,2),
    FOREIGN KEY (clubbed_order_id) REFERENCES clubbed_orders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (cart_id) REFERENCES carts(id)
);

-- Drivers table
CREATE TABLE drivers (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) UNIQUE NOT NULL,
    status ENUM('available', 'busy', 'inactive') DEFAULT 'available',
    lat DECIMAL(9,6),
    lng DECIMAL(9,6),
    current_load DECIMAL(10,2) DEFAULT 0.0,
    max_capacity DECIMAL(10,2) DEFAULT 20.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Deliveries table
CREATE TABLE deliveries (
    id VARCHAR(36) PRIMARY KEY,
    driver_id VARCHAR(36),
    clubbed_order_id VARCHAR(36),
    estimated_time_minutes INT,
    status ENUM('assigned', 'in_transit', 'delivered') DEFAULT 'assigned',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES drivers(id),
    FOREIGN KEY (clubbed_order_id) REFERENCES clubbed_orders(id)
);

-- Indexes for better performance
CREATE INDEX idx_buddy_location ON buddy_queue (lat, lng);
CREATE INDEX idx_buddy_location_hash ON buddy_queue (location_hash);
CREATE INDEX idx_buddy_status ON buddy_queue (status);
CREATE INDEX idx_cart_user ON carts (user_id);
CREATE INDEX idx_cart_items_cart ON cart_items (cart_id);
CREATE INDEX idx_cart_items_product ON cart_items (product_id);

-- Insert sample data
INSERT INTO users (id, name, email, password_hash, phone, address) VALUES
('user-1', 'Test User', 'test@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '+91-9876543210', '123 Test Street, Mumbai'),
('user-2', 'Demo User', 'demo@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW', '+91-9876543211', '456 Demo Lane, Mumbai');

INSERT INTO products (id, name, price, weight_grams, stock, image_url) VALUES
('prod-1', 'Fresh Bananas (1kg)', 40.00, 1000, 100, 'https://example.com/banana.jpg'),
('prod-2', 'Bread - Whole Wheat', 35.00, 400, 50, 'https://example.com/bread.jpg'),
('prod-3', 'Milk - Full Cream (1L)', 55.00, 1000, 30, 'https://example.com/milk.jpg'),
('prod-4', 'Eggs - Free Range (12 pcs)', 90.00, 600, 25, 'https://example.com/eggs.jpg'),
('prod-5', 'Rice - Basmati (1kg)', 120.00, 1000, 40, 'https://example.com/rice.jpg'),
('prod-6', 'Tomatoes (500g)', 30.00, 500, 60, 'https://example.com/tomatoes.jpg'),
('prod-7', 'Chicken Breast (500g)', 180.00, 500, 20, 'https://example.com/chicken.jpg'),
('prod-8', 'Yogurt - Greek Style', 65.00, 200, 35, 'https://example.com/yogurt.jpg');

INSERT INTO drivers (id, name, max_capacity, current_load, status) VALUES
('driver-1', 'Raj Kumar', 5.0, 0.0, 'available'),
('driver-2', 'Suresh Patel', 7.0, 0.0, 'available'),
('driver-3', 'Mohan Singh', 4.5, 0.0, 'available');

-- Success message
SELECT 'BuddyCart database setup completed successfully!' as message;
