"""
Migration script to convert from hardcoded status strings to custom status system.
This script should be run once to migrate existing data.
"""

from database import db
from models import Tasks, Projects, CustomStatus
from app import create_app

def migrate_status_system():
    app = create_app()
    
    with app.app_context():
        print("Starting migration to custom status system...")
        
        # Create tables if they don't exist
        db.create_all()
        
        # Get all projects
        projects = Projects.query.all()
        
        for project in projects:
            print(f"Processing project: {project.name} (ID: {project.id})")
            
            # Check if project already has custom statuses
            existing_statuses = CustomStatus.query.filter_by(project_id=project.id).count()
            if existing_statuses > 0:
                print(f"  Project {project.id} already has custom statuses, skipping...")
                continue
            
            # Create default statuses for this project
            default_statuses = [
                {"name": "To-Do", "description": "Tasks that need to be started", "color": "#FACC15", "position": 1, "is_default": True},
                {"name": "In Progress", "description": "Tasks currently being worked on", "color": "#3B82F6", "position": 2, "is_default": False},
                {"name": "Done", "description": "Completed tasks", "color": "#22C55E", "position": 3, "is_default": False}
            ]
            
            status_mapping = {}
            
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
                status_mapping[status_data["name"]] = status.id
                print(f"  Created status: {status.name} (ID: {status.id})")
            
            # Migrate existing tasks for this project
            tasks = Tasks.query.filter_by(project_id=project.id).all()
            for task in tasks:
                # Check if task has the old status field
                if hasattr(task, 'status') and task.status:
                    old_status = task.status
                    # Map old status to new status_id
                    if old_status in status_mapping:
                        task.status_id = status_mapping[old_status]
                        print(f"  Migrated task '{task.title}': {old_status} -> status_id {task.status_id}")
                    else:
                        # Default to "To-Do" if status doesn't match
                        task.status_id = status_mapping["To-Do"]
                        print(f"  Migrated task '{task.title}': {old_status} (unknown) -> To-Do")
                else:
                    # Task has no status, set to default
                    task.status_id = status_mapping["To-Do"]
                    print(f"  Set default status for task '{task.title}' -> To-Do")
        
        # Commit all changes
        db.session.commit()
        print("Migration completed successfully!")

if __name__ == "__main__":
    migrate_status_system() 