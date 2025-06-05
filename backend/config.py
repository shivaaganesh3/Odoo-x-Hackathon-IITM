import os

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
