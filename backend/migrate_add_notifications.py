#!/usr/bin/env python3
"""
Migration script to add Notifications table for deadline warnings feature.
This script safely adds the new table without affecting existing data.
"""

from app import create_app
from database import db
from models import Notifications, Users, Tasks, Projects
from sqlalchemy import inspect

def migrate_notifications():
    """Add notifications table to existing database"""
    
    app = create_app()
    
    with app.app_context():
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print("Current tables:", existing_tables)
        
        # Check if notifications table already exists
        if 'notifications' in existing_tables:
            print("✅ Notifications table already exists!")
            return
        
        try:
            # Create only the notifications table
            print("🔄 Creating notifications table...")
            Notifications.__table__.create(db.engine)
            
            print("✅ Successfully created notifications table!")
            print("🚀 Deadline warnings feature is ready to use!")
            
            # Verify the table was created
            inspector = inspect(db.engine)
            updated_tables = inspector.get_table_names()
            
            if 'notifications' in updated_tables:
                print("✅ Migration completed successfully!")
                
                # Show table columns
                columns = inspector.get_columns('notifications')
                print("\n📋 Notifications table structure:")
                for col in columns:
                    print(f"  - {col['name']}: {col['type']}")
            else:
                print("❌ Migration failed - table not found")
                
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            raise

if __name__ == "__main__":
    print("🚀 Starting notifications table migration...")
    migrate_notifications()
    print("✨ Migration complete!") 