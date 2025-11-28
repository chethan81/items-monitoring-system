# Items Monitoring System

A complete, hosting-ready web application with user authentication built with Flask and MySQL. This system is fully configured for deployment on Render.com.

## Features

- ✅ User authentication with session management
- ✅ Secure password hashing using Werkzeug
- ✅ MySQL database integration
- ✅ Clean, responsive UI with CSS
- ✅ Ready for cloud deployment
- ✅ Environment variable configuration
- ✅ Gunicorn production server setup

## Project Structure

```
items-monitoring-system/
├── app.py                 # Main Flask application
├── init_db.py            # Database initialization script
├── database.sql          # SQL database setup script
├── requirements.txt      # Python dependencies
├── render.yaml          # Render.com deployment config
├── .env.example         # Environment variables template
├── README.md            # This file
├── templates/
│   ├── login.html       # Login page template
│   └── dashboard.html   # Dashboard page template
└── static/
    └── css/
        └── style.css    # Application styles
```

## Quick Start (Local Development)

### Prerequisites
- Python 3.8+
- MySQL Server
- Git

### Installation

1. **Clone or download the project**
   ```bash
   git clone <your-repo-url>
   cd items-monitoring-system
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your MySQL credentials
   ```

5. **Initialize database**
   ```bash
   python init_db.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open http://localhost:5000
   - Login with: username `admin`, password `admin123`

## Deployment on Render.com

### Step 1: Push to GitHub

1. Create a new repository on GitHub
2. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

### Step 2: Deploy on Render

1. **Create Render Account**
   - Sign up at [render.com](https://render.com)
   - Connect your GitHub account

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration
   - Click "Create Web Service"

3. **Create MySQL Database**
   - Click "New +" → "PostgreSQL" (or MySQL if available)
   - Choose the free plan
   - Name it `items-monitoring-db`

4. **Set Environment Variables**
   In your web service settings, add these environment variables:
   
   ```
   MYSQL_HOST=your-database-host
   MYSQL_USER=your-database-user
   MYSQL_PASSWORD=your-database-password
   MYSQL_DATABASE=items_monitoring
   SECRET_KEY=your-random-secret-key
   ```

5. **Deploy**
   - Render will automatically build and deploy your application
   - Your app will be available at `https://your-app-name.onrender.com`

### Environment Variables for Render

Get these values from your Render database dashboard:

- **MYSQL_HOST**: Found in your database connection string
- **MYSQL_USER**: Database username (usually auto-generated)
- **MYSQL_PASSWORD**: Database password (auto-generated)
- **MYSQL_DATABASE**: Database name (set to `items_monitoring`)
- **SECRET_KEY**: Generate a random string for security

## Default Credentials

- **Username**: `admin`
- **Password**: `admin123`

⚠️ **Important**: Change the default password after first login for production use.

## Database Schema

The application uses a single `users` table:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Security Features

- Passwords are hashed using Werkzeug's PBKDF2 algorithm
- Session-based authentication
- CSRF protection ready
- Environment variable configuration for sensitive data

## Customization

### Adding New Features

The system is designed to be easily extensible:

1. **Add new routes** in `app.py`
2. **Create new templates** in the `templates/` folder
3. **Add new styles** in `static/css/style.css`
4. **Extend the database** by modifying the database schema

### Changing the UI

- Edit `static/css/style.css` for styling changes
- Modify `templates/login.html` and `templates/dashboard.html` for layout changes

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check MySQL service is running
   - Verify environment variables
   - Ensure database credentials are correct

2. **Import Errors**
   - Make sure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

3. **Render Deployment Issues**
   - Check build logs for errors
   - Verify environment variables are set correctly
   - Ensure `render.yaml` is properly formatted

### Getting Help

- Check the Render documentation: https://render.com/docs
- Review Flask documentation: https://flask.palletsprojects.com/
- MySQL connector docs: https://dev.mysql.com/doc/connector-python/en/

## License

This project is open source and available under the MIT License.

---

**Ready to deploy!** Follow the deployment steps above to get your application running on Render.com in minutes.
