class Config:
    SECRET_KEY = "super-secret-key"
    SQLALCHEMY_DATABASE_URI = "sqlite:///synergysphere.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-Security settings
    SECURITY_PASSWORD_HASH = "pbkdf2_sha512"
    SECURITY_PASSWORD_SALT = "saltystring"

    SECURITY_REGISTERABLE = True
    SECURITY_SEND_REGISTER_EMAIL = False



    # ✅ Add this:
    SECURITY_CSRF_PROTECT = False
