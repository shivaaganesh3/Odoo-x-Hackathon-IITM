from app import create_app
from database import db
from flask_security import SQLAlchemyUserDatastore
from models import Users, Roles
from flask_security.utils import hash_password
import uuid

def create_flask_user():
    """Create a user using Flask-Security's proper methods"""
    
    app = create_app()
    
    with app.app_context():
        # Initialize user datastore
        user_datastore = SQLAlchemyUserDatastore(db, Users, Roles)
        
        # Clear existing users
        Users.query.delete()
        db.session.commit()
        print("🧹 Cleared existing users")
        
        # Create user using Flask-Security
        email = 'abc@gmail.com'
        password = 'test123'
        name = 'abc'
        
        user = user_datastore.create_user(
            email=email,
            password=hash_password(password),
            name=name,
            fs_uniquifier=str(uuid.uuid4()),
            active=True
        )
        
        db.session.commit()
        
        print(f"✅ Created Flask-Security user:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Name: {name}")
        print(f"   ID: {user.id}")
        print(f"   Hash format: {user.password[:50]}...")
        
        return user

if __name__ == "__main__":
    create_flask_user() 