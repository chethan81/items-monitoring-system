#!/usr/bin/env python3
"""
Database initialization script for Items Monitoring System
This script creates the database and default admin user.
"""

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
import os

def create_database_and_user():
    """Create database and tables with default admin user"""
    
    # Database connection parameters
    config = {
        'host': os.environ.get('MYSQL_HOST', 'localhost'),
        'user': os.environ.get('MYSQL_USER', 'root'),
        'password': os.environ.get('MYSQL_PASSWORD', ''),
        'charset': 'utf8mb4',
        'collation': 'utf8mb4_unicode_ci'
    }
    
    try:
        # Connect to MySQL server (without specifying database)
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS items_monitoring")
        cursor.execute("USE items_monitoring")
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create index for username
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_username ON users(username)")
        
        # Check if admin user exists
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        admin_exists = cursor.fetchone()
        
        if not admin_exists:
            # Create default admin user with hashed password
            hashed_password = generate_password_hash('admin123')
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", 
                         ('admin', hashed_password))
            print("✓ Default admin user created:")
            print("  Username: admin")
            print("  Password: admin123")
        else:
            print("✓ Admin user already exists")
        
        # Commit changes
        connection.commit()
        
        # Show table info
        cursor.execute("DESCRIBE users")
        print("\n✓ Users table structure:")
        for row in cursor:
            print(f"  {row[0]}: {row[1]}")
        
        # Show all users
        cursor.execute("SELECT id, username, created_at FROM users")
        users = cursor.fetchall()
        print(f"\n✓ Total users: {len(users)}")
        for user in users:
            print(f"  ID: {user[0]}, Username: {user[1]}, Created: {user[2]}")
        
        print("\n✅ Database initialization completed successfully!")
        
    except Error as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

if __name__ == "__main__":
    print("🚀 Initializing Items Monitoring System Database...")
    create_database_and_user()
