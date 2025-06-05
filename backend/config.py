import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(os.path.dirname(os.path.abspath(__file__)), "taskmanager.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security settings
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = "saltystring"

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False

    # Session configuration for cross-origin requests
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Disable CSRF for API endpoints
    SECURITY_CSRF_PROTECT = False
    SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS = True
    
    # Natural Language Processing (Gemini API)
    # Set GEMINI_API_KEY in .env file for natural language task parsing
    # Get your API key from: https://makersuite.google.com/app/apikey
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Email Configuration for Scheduled Jobs
    # Set these in your .env file for email functionality
    SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
    SMTP_USERNAME = os.getenv('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
    FROM_EMAIL = os.getenv('FROM_EMAIL', SMTP_USERNAME)
    
    # Redis Configuration for Celery
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
