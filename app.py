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
            print("Database and admin user created successfully")
        
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
    return render_template('dashboard.html', username=username)

@app.before_request
def check_database():
    if request.endpoint and request.endpoint != 'static':
        ensure_database_exists()

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
