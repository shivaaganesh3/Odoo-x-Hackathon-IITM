from app import create_app
from database import db
from models import Users, Roles, UserRoles, Projects, CustomStatus, Tasks, TeamMembers, Discussions
from flask_security import hash_password
import uuid
import os

def recreate_database():
    print("🔥 Nuclear Database Recreation")
    print("=" * 50)
    
    app = create_app()
    
    with app.app_context():
        print(f"📁 Database URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # Get the actual database file path
        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        print(f"📁 Database file path: {db_path}")
        
        # Backup existing database if it exists
        if os.path.exists(db_path):
            backup_path = f"{db_path}.backup"
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"📦 Backed up existing database to: {backup_path}")
        
        # Drop all tables
        print("🗑️ Dropping all tables...")
        db.drop_all()
        
        # Create all tables
        print("🏗️ Creating all tables...")
        db.create_all()
        
        # Verify tables were created
        inspector = db.inspect(db.engine)
        table_names = inspector.get_table_names()
        print(f"✅ Created {len(table_names)} tables:")
        for table in table_names:
            print(f"   - {table}")
        
        # Create default statuses for testing
        print("\n🎯 Creating default statuses...")
        default_statuses = [
            {"name": "To Do", "color": "#ef4444", "position": 1, "is_default": True},
            {"name": "In Progress", "color": "#f59e0b", "position": 2, "is_default": False},
            {"name": "Done", "color": "#10b981", "position": 3, "is_default": False}
        ]
        
        # Create a test project first
        test_project = Projects(
            name="Test Project",
            description="A test project for registration",
            created_by=1  # Will create user with ID 1
        )
        db.session.add(test_project)
        db.session.flush()  # Get the project ID
        
        for status_data in default_statuses:
            status = CustomStatus(
                name=status_data["name"],
                color=status_data["color"],
                position=status_data["position"],
                is_default=status_data["is_default"],
                project_id=test_project.id
            )
            db.session.add(status)
        
        # Create test user with proper Flask-Security hash
        print("👤 Creating test user...")
        test_user = Users(
            email="abc@gmail.com",
            password=hash_password("test123"),
            name="Test User",
            active=True,
            fs_uniquifier=str(uuid.uuid4()),
            fs_token_uniquifier=str(uuid.uuid4())
        )
        db.session.add(test_user)
        
        # Commit all changes
        db.session.commit()
        print("✅ Database recreated successfully!")
        
        # Test the connection
        print("\n🧪 Testing connection...")
        users = Users.query.all()
        print(f"✅ Found {len(users)} users")
        for user in users:
            print(f"   - {user.email} (ID: {user.id})")
        
        projects = Projects.query.all()
        print(f"✅ Found {len(projects)} projects")
        
        statuses = CustomStatus.query.all()
        print(f"✅ Found {len(statuses)} custom statuses")

if __name__ == "__main__":
    recreate_database() 