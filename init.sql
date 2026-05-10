-- PostgreSQL initialization script
-- Creates tables for the e-commerce application

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    email       VARCHAR(150) UNIQUE NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Create orders table
-- References user by user_id (denormalized for simplicity)
CREATE TABLE IF NOT EXISTS orders (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    product_id  VARCHAR(50) NOT NULL,       -- Product ID from MongoDB
    quantity    INTEGER NOT NULL CHECK (quantity > 0),
    total_price NUMERIC(10, 2) NOT NULL,
    status      VARCHAR(20) DEFAULT 'pending',
    created_at  TIMESTAMP DEFAULT NOW()
);

-- Insert sample users
INSERT INTO users (name, email) VALUES
    ('Alice Johnson', 'alice@example.com'),
    ('Bob Smith', 'bob@example.com'),
    ('Carol White', 'carol@example.com')
ON CONFLICT DO NOTHING;

-- Index for faster order lookups by user
CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
