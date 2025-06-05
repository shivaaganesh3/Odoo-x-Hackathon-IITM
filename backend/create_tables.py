"""
Script to create/update database tables with the new custom status schema.
This should be run to initialize or update the database.
"""

from database import db
from models import Users, Roles, Projects, CustomStatus, Tasks, TeamMembers, Discussions, UserRoles
from app import create_app
import sqlite3

def create_tables_with_migration():
    app = create_app()
    
    with app.app_context():
        print("Creating/updating database tables...")
        
        # First, let's check if we need to migrate the old tasks table
        connection = sqlite3.connect('taskmanager.db')
        cursor = connection.cursor()
        
        # Check if the old status column exists
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in cursor.fetchall()]
        has_old_status = 'status' in columns
        has_new_status_id = 'status_id' in columns
        
        print(f"Table analysis:")
        print(f"  - Has old 'status' column: {has_old_status}")
        print(f"  - Has new 'status_id' column: {has_new_status_id}")
        
        # Get existing tasks if they exist
        existing_tasks = []
        if has_old_status:
            try:
                cursor.execute("SELECT id, title, description, status, due_date, priority, project_id, assigned_to FROM tasks")
                existing_tasks = cursor.fetchall()
                print(f"  - Found {len(existing_tasks)} existing tasks to migrate")
            except sqlite3.Error as e:
                print(f"  - Error reading existing tasks: {e}")
        
        connection.close()
        
        # Create all tables (this will create new ones and update existing ones)
        db.create_all()
        print("✅ Database tables created/updated")
        
        # If we have existing tasks and the old status column, we need to migrate
        if existing_tasks and has_old_status and not has_new_status_id:
            print("🔄 Migrating existing tasks...")
            
            # Create default statuses for each project first
            projects = Projects.query.all()
            status_mappings = {}
            
            for project in projects:
                print(f"  Processing project: {project.name} (ID: {project.id})")
                
                # Check if project already has custom statuses
                existing_statuses = CustomStatus.query.filter_by(project_id=project.id).count()
                if existing_statuses > 0:
                    print(f"    Project {project.id} already has custom statuses")
                    # Map existing statuses
                    statuses = CustomStatus.query.filter_by(project_id=project.id).all()
                    project_mapping = {}
                    for status in statuses:
                        if status.name == "To-Do":
                            project_mapping["To-Do"] = status.id
                        elif status.name == "In Progress":
                            project_mapping["In Progress"] = status.id
                        elif status.name == "Done":
                            project_mapping["Done"] = status.id
                        # Set first as default if none is marked as default
                        if not any(s.is_default for s in statuses):
                            statuses[0].is_default = True
                            db.session.commit()
                    status_mappings[project.id] = project_mapping
                    continue
                
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
                    print(f"    Created status: {status.name} (ID: {status.id})")
                
                status_mappings[project.id] = project_mapping
            
            # Now migrate the existing tasks by recreating them with status_id
            print("  Migrating task data...")
            
            # Delete old tasks (we'll recreate them)
            Tasks.query.delete()
            db.session.commit()
            
            # Recreate tasks with new schema
            for task_data in existing_tasks:
                task_id, title, description, old_status, due_date, priority, project_id, assigned_to = task_data
                
                # Map old status to new status_id
                project_statuses = status_mappings.get(project_id, {})
                status_id = project_statuses.get(old_status, project_statuses.get("To-Do"))
                
                if not status_id:
                    print(f"    Warning: No status mapping found for task '{title}', skipping...")
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
                print(f"    Migrated task: '{title}' -> status_id {status_id}")
            
            db.session.commit()
            print("✅ Task migration completed")
        else:
            print("ℹ️ No migration needed or already completed")
        
        print("🎉 Database setup completed successfully!")

if __name__ == "__main__":
    create_tables_with_migration() 