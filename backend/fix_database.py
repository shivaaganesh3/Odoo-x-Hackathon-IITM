"""
Script to fix the database schema by properly migrating the tasks table.
This handles the SQLite limitation where we can't easily add foreign key columns.
"""

import sqlite3
from app import create_app
from database import db
from models import Tasks, CustomStatus, Projects

def fix_database_schema():
    print("🔧 Fixing database schema...")
    
    app = create_app()
    
    with app.app_context():
        # Direct SQLite operations
        connection = sqlite3.connect('taskmanager.db')
        cursor = connection.cursor()
        
        try:
            # 1. Check current tasks table structure
            cursor.execute("PRAGMA table_info(tasks)")
            columns = cursor.fetchall()
            print("Current tasks table structure:")
            for col in columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # 2. Backup existing tasks data
            print("\n💾 Backing up existing tasks...")
            try:
                cursor.execute("""
                    SELECT id, title, description, status, due_date, priority, 
                           project_id, assigned_to 
                    FROM tasks
                """)
                existing_tasks = cursor.fetchall()
                print(f"   Found {len(existing_tasks)} tasks to migrate")
            except sqlite3.Error as e:
                print(f"   Error reading tasks: {e}")
                existing_tasks = []
            
            # 3. Drop the old tasks table
            print("\n🗑️ Dropping old tasks table...")
            cursor.execute("DROP TABLE IF EXISTS tasks")
            
            # 4. Create all tables with the new schema
            print("\n🏗️ Creating new tables...")
            db.create_all()
            
            # 5. Create default statuses for existing projects
            print("\n🎨 Creating default statuses for projects...")
            projects = Projects.query.all()
            status_mappings = {}
            
            for project in projects:
                print(f"   Processing project: {project.name} (ID: {project.id})")
                
                # Create default statuses for this project
                default_statuses = [
                    {"name": "To-Do", "description": "Tasks that need to be started", "color": "#FACC15", "position": 1, "is_default": True},
                    {"name": "In Progress", "description": "Tasks currently being worked on", "color": "#3B82F6", "position": 2, "is_default": False},
                    {"name": "Done", "description": "Completed tasks", "color": "#22C55E", "position": 3, "is_default": False}
                ]
                
                project_mapping = {}
                
                for status_data in default_statuses:
                    status = CustomStatus(
                        name=status_data["name"],
                        description=status_data["description"],
                        color=status_data["color"],
                        position=status_data["position"],
                        is_default=status_data["is_default"],
                        project_id=project.id
                    )
                    db.session.add(status)
                    db.session.flush()  # Get the ID
                    project_mapping[status_data["name"]] = status.id
                    print(f"     Created status: {status.name} (ID: {status.id})")
                
                status_mappings[project.id] = project_mapping
            
            # Commit status creation
            db.session.commit()
            
            # 6. Recreate tasks with new schema
            if existing_tasks:
                print(f"\n📝 Recreating {len(existing_tasks)} tasks with new schema...")
                
                for task_data in existing_tasks:
                    task_id, title, description, old_status, due_date, priority, project_id, assigned_to = task_data
                    
                    # Map old status to new status_id
                    project_statuses = status_mappings.get(project_id, {})
                    
                    # Try to match old status name, default to "To-Do"
                    status_id = None
                    if old_status in project_statuses:
                        status_id = project_statuses[old_status]
                    else:
                        status_id = project_statuses.get("To-Do")
                    
                    if not status_id:
                        print(f"     Warning: No status mapping found for task '{title}', skipping...")
                        continue
                    
                    # Convert due_date string to date object if needed
                    if due_date and isinstance(due_date, str):
                        from datetime import datetime
                        try:
                            due_date = datetime.strptime(due_date, "%Y-%m-%d").date()
                        except:
                            due_date = None
                    
                    new_task = Tasks(
                        title=title,
                        description=description,
                        status_id=status_id,
                        due_date=due_date,
                        priority=priority or 'Medium',
                        priority_score=0,
                        project_id=project_id,
                        assigned_to=assigned_to
                    )
                    db.session.add(new_task)
                    print(f"     Recreated task: '{title}' -> status_id {status_id}")
                
                db.session.commit()
            
            print("\n✅ Database schema fixed successfully!")
            
            # 7. Verify the new structure
            print("\n🔍 Verifying new structure...")
            cursor.execute("PRAGMA table_info(tasks)")
            new_columns = cursor.fetchall()
            print("New tasks table structure:")
            for col in new_columns:
                print(f"  - {col[1]} ({col[2]})")
            
            # Check counts
            custom_status_count = CustomStatus.query.count()
            tasks_count = Tasks.query.count()
            print(f"\n📊 Final counts:")
            print(f"   - Custom Statuses: {custom_status_count}")
            print(f"   - Tasks: {tasks_count}")
            
        except Exception as e:
            print(f"❌ Error fixing database: {e}")
            connection.rollback()
            raise
        finally:
            connection.close()

if __name__ == "__main__":
    fix_database_schema() 