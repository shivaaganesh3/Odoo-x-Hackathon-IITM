"""
Script to create budget and expense related tables in the database.
"""

from database import db
from models import Budget, Expense, ExpenseCategory
from app import create_app

def create_budget_tables():
    app = create_app()
    
    with app.app_context():
        print("Creating budget and expense tables...")
        
        # Create the tables
        Budget.__table__.create(db.engine, checkfirst=True)
        ExpenseCategory.__table__.create(db.engine, checkfirst=True)
        Expense.__table__.create(db.engine, checkfirst=True)
        
        print("✅ Budget and expense tables created successfully!")
        
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
    create_budget_tables() 