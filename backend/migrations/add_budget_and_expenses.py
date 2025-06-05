"""
Migration script to add budget and expense tracking tables
"""

import sqlite3
import os
import sys
from datetime import datetime

def migrate():
    print("Starting migration: Adding budget and expense tracking tables...")
    
    # Get the database path
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'taskmanager.db')
    print(f"Using database at: {db_path}")
    
    # Connect to database
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    
    try:
        # Create expense_categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expense_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ Created expense_categories table")

        # Create budgets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS budgets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                start_date TIMESTAMP NOT NULL,
                end_date TIMESTAMP NOT NULL,
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                project_id INTEGER REFERENCES projects(id),
                task_id INTEGER REFERENCES tasks(id),
                created_by INTEGER NOT NULL REFERENCES users(id)
            )
        ''')
        print("✅ Created budgets table")

        # Create expenses table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                date TIMESTAMP NOT NULL,
                notes TEXT,
                receipt_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                project_id INTEGER REFERENCES projects(id),
                task_id INTEGER REFERENCES tasks(id),
                category_id INTEGER NOT NULL REFERENCES expense_categories(id),
                created_by INTEGER NOT NULL REFERENCES users(id)
            )
        ''')
        print("✅ Created expenses table")

        # Insert default expense categories
        default_categories = [
            ('Labor', 'Staff and contractor costs'),
            ('Materials', 'Physical materials and supplies'),
            ('Equipment', 'Equipment purchase or rental'),
            ('Software', 'Software licenses and subscriptions'),
            ('Travel', 'Travel and accommodation expenses'),
            ('Services', 'External services and consultants'),
            ('Other', 'Miscellaneous expenses')
        ]

        cursor.executemany('''
            INSERT INTO expense_categories (name, description)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM expense_categories WHERE name = ?
            )
        ''', [(c[0], c[1], c[0]) for c in default_categories])
        print("✅ Added default expense categories")

        connection.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        connection.rollback()
    finally:
        connection.close()

if __name__ == '__main__':
    migrate() 