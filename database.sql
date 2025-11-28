-- MySQL Database Setup Script for Items Monitoring System
-- Run this script to create the database and user table

-- Create database (if not exists)
CREATE DATABASE IF NOT EXISTS items_monitoring;

-- Use the database
USE items_monitoring;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default admin user (password: admin123)
-- The password is hashed using werkzeug.security.generate_password_hash
INSERT INTO users (username, password) VALUES 
('admin', 'pbkdf2:sha256:260000$8g4Z9J2Q3L7M5P8R$KdFmNqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVwXyZaBcDeFgHiJkLmNoPqRsTuVw')
ON DUPLICATE KEY UPDATE username=username;

-- Create index for faster username lookup
CREATE INDEX IF NOT EXISTS idx_username ON users(username);

-- Show table structure
DESCRIBE users;

-- Show all users
SELECT * FROM users;
