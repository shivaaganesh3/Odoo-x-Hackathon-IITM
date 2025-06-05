"""
Migration script to add missing task_id column to discussions table.
"""

import sqlite3
from database import db
from app import create_app

def migrate_discussions_table():
    app = create_app()
    
    with app.app_context():
        print("Checking discussions table schema...")
        
        # Check current table structure
        connection = sqlite3.connect('taskmanager.db')
        cursor = connection.cursor()
        
        # Get current columns
        cursor.execute("PRAGMA table_info(discussions)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Current columns: {columns}")
        
        if 'task_id' not in columns:
            print("❌ Missing task_id column. Adding it now...")
            
            try:
                # Add the missing task_id column
                cursor.execute("ALTER TABLE discussions ADD COLUMN task_id INTEGER")
                connection.commit()
                print("✅ Successfully added task_id column")
                
                # Verify the column was added
                cursor.execute("PRAGMA table_info(discussions)")
                new_columns = [column[1] for column in cursor.fetchall()]
                print(f"Updated columns: {new_columns}")
                
            except sqlite3.Error as e:
                print(f"❌ Error adding column: {e}")
                
        else:
            print("✅ task_id column already exists")
        
        connection.close()
        print("🎉 Migration completed!")

if __name__ == "__main__":
    migrate_discussions_table() 