from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')

def get_db_connection():
    try:
        connection = sqlite3.connect('items_monitoring.db')
        connection.row_factory = sqlite3.Row
        return connection
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

def ensure_database_exists():
    """Create database and tables if they don't exist"""
    try:
        connection = sqlite3.connect('items_monitoring.db')
        cursor = connection.cursor()
        
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            # Create users table
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            
            # Create admin user
            hashed_password = generate_password_hash('admin123')
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                         ('admin', hashed_password))
            connection.commit()
            print("Users table and admin user created successfully")
        
        # Check if stock_items table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='stock_items'")
        if not cursor.fetchone():
            # Create stock_items table
            cursor.execute("""
                CREATE TABLE stock_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insert sample data
            sample_items = [
                ('Laptop Dell XPS', 5, 999.99, 'High-performance laptop for professionals'),
                ('Wireless Mouse', 15, 29.99, 'Ergonomic wireless mouse'),
                ('USB-C Hub', 8, 49.99, '7-in-1 USB-C hub with HDMI'),
                ('Mechanical Keyboard', 3, 129.99, 'RGB mechanical keyboard'),
                ('Monitor Stand', 12, 39.99, 'Adjustable monitor stand')
            ]
            cursor.executemany("INSERT INTO stock_items (name, quantity, price, description) VALUES (?, ?, ?, ?)", 
                             sample_items)
            connection.commit()
            print("Stock items table and sample data created successfully")
        
        connection.close()
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")

def init_db():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL
                )
            """)
            conn.commit()
            
            # Check if admin user exists, if not create one
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                hashed_password = generate_password_hash('admin123')
                cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", 
                             ('admin', hashed_password))
                conn.commit()
                print("Default admin user created: username=admin, password=admin123")
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")
        finally:
            conn.close()

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/auth/login', methods=['POST'])
def auth_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Please enter both username and password', 'error')
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
            
            if user and check_password_hash(user['password'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password', 'error')
        except sqlite3.Error as e:
            flash('Database error occurred', 'error')
            print(f"Login error: {e}")
        finally:
            conn.close()
    else:
        flash('Database connection failed', 'error')
    
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    username = session.get('username', 'User')
    
    # Get stock summary
    conn = get_db_connection()
    total_items = 0
    total_value = 0
    low_stock_items = 0
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM stock_items")
            total_items = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(quantity * price) FROM stock_items")
            result = cursor.fetchone()[0]
            total_value = result if result else 0
            
            cursor.execute("SELECT COUNT(*) FROM stock_items WHERE quantity < 10")
            low_stock_items = cursor.fetchone()[0]
            
            conn.close()
        except sqlite3.Error as e:
            print(f"Dashboard error: {e}")
    
    return render_template('dashboard.html', username=username, 
                         total_items=total_items, total_value=total_value, 
                         low_stock_items=low_stock_items)

# Stock Management Routes
@app.route('/items')
def items_list():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    items = []
    
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM stock_items ORDER BY created_at DESC")
            items = cursor.fetchall()
            conn.close()
        except sqlite3.Error as e:
            print(f"Items list error: {e}")
            flash('Error loading items', 'error')
    
    return render_template('items.html', items=items)

@app.route('/items/add', methods=['GET', 'POST'])
def add_item():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        description = request.form.get('description')
        
        if not name or not quantity or not price:
            flash('Please fill in all required fields', 'error')
            return render_template('add_item.html')
        
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            flash('Invalid quantity or price', 'error')
            return render_template('add_item.html')
        
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("INSERT INTO stock_items (name, quantity, price, description) VALUES (?, ?, ?, ?)",
                             (name, quantity, price, description))
                conn.commit()
                conn.close()
                flash('Item added successfully!', 'success')
                return redirect(url_for('items_list'))
            except sqlite3.Error as e:
                print(f"Add item error: {e}")
                flash('Error adding item', 'error')
    
    return render_template('add_item.html')

@app.route('/items/edit/<int:item_id>', methods=['GET', 'POST'])
def edit_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if not conn:
        flash('Database connection error', 'error')
        return redirect(url_for('items_list'))
    
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        price = request.form.get('price')
        description = request.form.get('description')
        
        if not name or not quantity or not price:
            flash('Please fill in all required fields', 'error')
            return redirect(url_for('edit_item', item_id=item_id))
        
        try:
            quantity = int(quantity)
            price = float(price)
        except ValueError:
            flash('Invalid quantity or price', 'error')
            return redirect(url_for('edit_item', item_id=item_id))
        
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE stock_items SET name=?, quantity=?, price=?, description=? WHERE id=?",
                         (name, quantity, price, description, item_id))
            conn.commit()
            conn.close()
            flash('Item updated successfully!', 'success')
            return redirect(url_for('items_list'))
        except sqlite3.Error as e:
            print(f"Edit item error: {e}")
            flash('Error updating item', 'error')
    
    # GET request - show edit form
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stock_items WHERE id=?", (item_id,))
        item = cursor.fetchone()
        conn.close()
        
        if not item:
            flash('Item not found', 'error')
            return redirect(url_for('items_list'))
        
        return render_template('edit_item.html', item=item)
    except sqlite3.Error as e:
        print(f"Edit item error: {e}")
        flash('Error loading item', 'error')
        return redirect(url_for('items_list'))

@app.route('/items/delete/<int:item_id>')
def delete_item(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM stock_items WHERE id=?", (item_id,))
            conn.commit()
            conn.close()
            flash('Item deleted successfully!', 'success')
        except sqlite3.Error as e:
            print(f"Delete item error: {e}")
            flash('Error deleting item', 'error')
    
    return redirect(url_for('items_list'))

@app.before_request
def check_database():
    if request.endpoint and request.endpoint != 'static':
        ensure_database_exists()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
