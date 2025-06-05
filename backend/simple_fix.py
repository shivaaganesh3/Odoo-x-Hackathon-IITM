"""
Simple fix to create the correct database structure from scratch.
"""

import sqlite3
import os

def recreate_database():
    print("🔄 Recreating database with correct schema...")
    
    # Remove old database
    if os.path.exists('taskmanager.db'):
        os.remove('taskmanager.db')
        print("   Removed old database")
    
    # Create new database with correct schema
    connection = sqlite3.connect('taskmanager.db')
    cursor = connection.cursor()
    
    try:
        # Create all tables with correct structure
        print("   Creating tables...")
        
        # Users table
        cursor.execute('''
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                active BOOLEAN DEFAULT 1,
                fs_uniquifier VARCHAR(255) NOT NULL UNIQUE,
                fs_token_uniquifier VARCHAR(255),
                name VARCHAR(100)
            )
        ''')
        
        # Roles table
        cursor.execute('''
            CREATE TABLE roles (
                id INTEGER PRIMARY KEY,
                name VARCHAR(80) NOT NULL UNIQUE,
                description VARCHAR(255)
            )
        ''')
        
        # User roles junction table
        cursor.execute('''
            CREATE TABLE user_roles (
                id INTEGER PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                role_id INTEGER REFERENCES roles(id)
            )
        ''')
        
        # Projects table
        cursor.execute('''
            CREATE TABLE projects (
                id INTEGER PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                description TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER NOT NULL REFERENCES users(id)
            )
        ''')
        
        # Custom Status table
        cursor.execute('''
            CREATE TABLE custom_status (
                id INTEGER PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                color VARCHAR(7) DEFAULT '#6B7280',
                position INTEGER DEFAULT 0,
                is_default BOOLEAN DEFAULT 0,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, project_id)
            )
        ''')
        
        # Tasks table with correct schema
        cursor.execute('''
            CREATE TABLE tasks (
                id INTEGER PRIMARY KEY,
                title VARCHAR(150) NOT NULL,
                description TEXT,
                status_id INTEGER REFERENCES custom_status(id),
                due_date DATE,
                priority VARCHAR(20) DEFAULT 'Medium',
                priority_score INTEGER DEFAULT 0,
                project_id INTEGER NOT NULL REFERENCES projects(id),
                assigned_to INTEGER REFERENCES users(id),
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Team Members table
        cursor.execute('''
            CREATE TABLE team_members (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id),
                project_id INTEGER NOT NULL REFERENCES projects(id)
            )
        ''')
        
        # Discussions table
        cursor.execute('''
            CREATE TABLE discussions (
                id INTEGER PRIMARY KEY,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                parent_id INTEGER REFERENCES discussions(id),
                user_id INTEGER NOT NULL REFERENCES users(id),
                project_id INTEGER NOT NULL REFERENCES projects(id)
            )
        ''')
        
        # Insert a test user
        cursor.execute('''
            INSERT INTO users (email, password, fs_uniquifier, name) 
            VALUES ('test@example.com', 'pbkdf2:sha256:600000$test', 'test-unique-id', 'Test User')
        ''')
        
        # Insert a test project
        cursor.execute('''
            INSERT INTO projects (name, description, created_by) 
            VALUES ('Sample Project', 'A sample project for testing', 1)
        ''')
        
        # Insert default statuses for the test project
        default_statuses = [
            ('To-Do', 'Tasks that need to be started', '#FACC15', 1, 1, 1),
            ('In Progress', 'Tasks currently being worked on', '#3B82F6', 2, 0, 1),
            ('Done', 'Completed tasks', '#22C55E', 3, 0, 1)
        ]
        
        for name, desc, color, pos, is_default, project_id in default_statuses:
            cursor.execute('''
                INSERT INTO custom_status (name, description, color, position, is_default, project_id) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, desc, color, pos, is_default, project_id))
        
        # Insert a test task
        cursor.execute('''
            INSERT INTO tasks (title, description, status_id, project_id, assigned_to) 
            VALUES ('Sample Task', 'This is a sample task', 1, 1, 1)
        ''')
        
        connection.commit()
        print("✅ Database recreated successfully!")
        
        # Verify structure
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        print("\n📋 Tasks table structure:")
        for col in columns:
            print(f"   - {col[1]} ({col[2]})")
        
        # Check counts
        cursor.execute("SELECT COUNT(*) FROM custom_status")
        status_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        
        print(f"\n📊 Record counts:")
        print(f"   - Projects: {project_count}")
        print(f"   - Custom Statuses: {status_count}")
        print(f"   - Tasks: {task_count}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        connection.rollback()
        raise
    finally:
        connection.close()

if __name__ == "__main__":
    recreate_database() 