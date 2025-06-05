"""
Migration script to add task_id to discussions table
"""

import sqlite3
from app import create_app
from database import db

def migrate():
    print("Starting migration: Adding task_id to discussions table...")
    
    # Connect to database
    connection = sqlite3.connect('taskmanager.db')
    cursor = connection.cursor()
    
    try:
        # Check if task_id column exists
        cursor.execute("PRAGMA table_info(discussions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'task_id' not in columns:
            print("Adding task_id column to discussions table...")
            cursor.execute('''
                ALTER TABLE discussions
                ADD COLUMN task_id INTEGER
                REFERENCES tasks(id)
            ''')
            print("✅ Added task_id column")
        else:
            print("task_id column already exists")
        
        connection.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        migrate() 