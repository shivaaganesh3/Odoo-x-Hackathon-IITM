"""
Script to create ALL database tables including potentially missing ones.
"""

from database import db
from models import (
    Users, Roles, UserRoles, Projects, CustomStatus, Tasks, TeamMembers, 
    Discussions, Notifications, Budget, Expense, ExpenseCategory
)
from app import create_app
import sqlite3

def create_all_tables():
    app = create_app()
    
    with app.app_context():
        print("Creating ALL database tables...")
        
        # Check which tables exist
        connection = sqlite3.connect('taskmanager.db')
        cursor = connection.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing_tables = [row[0] for row in cursor.fetchall()]
        print(f"Existing tables: {existing_tables}")
        
        # Required tables
        required_tables = [
            'users', 'roles', 'user_roles', 'projects', 'custom_status', 'tasks', 
            'team_members', 'discussions', 'notifications', 'budgets', 'expenses', 'expense_categories'
        ]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        print(f"Missing tables: {missing_tables}")
        
        connection.close()
        
        # Create all tables
        print("Creating/updating all tables...")
        db.create_all()
        print("✅ All tables created/updated!")
        
        # Verify tables were created
        connection = sqlite3.connect('taskmanager.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        final_tables = [row[0] for row in cursor.fetchall()]
        print(f"Final tables: {final_tables}")
        connection.close()
        
        # Check if expense categories exist, if not create defaults
        if ExpenseCategory.query.count() == 0:
            print("Creating default expense categories...")
            
            default_categories = [
                {"name": "Labor", "description": "Employee wages and contractor fees"},
                {"name": "Materials", "description": "Raw materials and supplies"},
                {"name": "Equipment", "description": "Hardware and equipment purchases"},
                {"name": "Software", "description": "Software licenses and subscriptions"},
                {"name": "Travel", "description": "Business travel and transportation"},
                {"name": "Marketing", "description": "Advertising and promotional expenses"},
                {"name": "Office", "description": "Office rent, utilities, and supplies"},
                {"name": "Training", "description": "Employee training and development"},
                {"name": "Consulting", "description": "External consulting services"},
                {"name": "Other", "description": "Miscellaneous expenses"}
            ]
            
            for cat_data in default_categories:
                category = ExpenseCategory(
                    name=cat_data["name"],
                    description=cat_data["description"]
                )
                db.session.add(category)
                print(f"  Created category: {cat_data['name']}")
            
            db.session.commit()
            print("✅ Default expense categories created!")
        else:
            print("ℹ️ Expense categories already exist")

if __name__ == "__main__":
    create_all_tables() 