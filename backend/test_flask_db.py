from app import create_app
from database import db
from models import Users
import traceback

def test_flask_database():
    print("🧪 Testing Flask Database Connection")
    print("=" * 50)
    
    try:
        app = create_app()
        
        with app.app_context():
            print("✅ Flask app context created")
            
            # Test database connection
            print(f"📁 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
            
            # Try to query users
            try:
                users = Users.query.all()
                print(f"✅ Users query successful: Found {len(users)} users")
                
                for user in users:
                    print(f"   - ID: {user.id}, Email: {user.email}, Name: {user.name}")
                    print(f"     fs_uniquifier: {user.fs_uniquifier}")
                    
            except Exception as e:
                print(f"❌ Users query failed: {e}")
                print("🔍 Full traceback:")
                traceback.print_exc()
            
            # Test database tables
            try:
                tables = db.engine.table_names()
                print(f"✅ SQLAlchemy can see {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table}")
            except Exception as e:
                print(f"❌ Cannot list tables: {e}")
    
    except Exception as e:
        print(f"❌ Flask app creation failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_flask_database() 