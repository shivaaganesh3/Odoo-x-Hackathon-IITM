#!/usr/bin/env python3
"""
Database Migration Script for Smart Task Prioritization Engine
Adds new fields to the Tasks table for the prioritization engine.
"""

import sqlite3
import json
from datetime import datetime
from config import Config

def migrate_database():
    """Add new columns for Smart Task Prioritization Engine"""
    db_path = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("Starting Smart Task Prioritization Engine migration...")
        
        # Check if columns already exist
        cursor.execute("PRAGMA table_info(tasks)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        # Check what columns need to be added
        if 'effort_score' not in columns:
            migrations_needed.append(('effort_score', 'INTEGER DEFAULT 3'))
        
        if 'impact_score' not in columns:
            migrations_needed.append(('impact_score', 'INTEGER DEFAULT 3'))
        
        if 'dependency_map' not in columns:
            migrations_needed.append(('dependency_map', 'TEXT DEFAULT "[]"'))
        
        if 'blocked_by' not in columns:
            migrations_needed.append(('blocked_by', 'TEXT DEFAULT "[]"'))
        
        # Check if priority_score needs to be updated to REAL
        if 'priority_score' in columns:
            cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='tasks'")
            table_sql = cursor.fetchone()[0]
            if 'priority_score INTEGER' in table_sql:
                print("Note: priority_score will be treated as REAL in new calculations")
        
        if not migrations_needed:
            print("✅ Database already has all Smart Prioritization fields!")
            return
        
        # Add new columns
        for column_name, column_def in migrations_needed:
            try:
                sql = f"ALTER TABLE tasks ADD COLUMN {column_name} {column_def}"
                cursor.execute(sql)
                print(f"✅ Added column: {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e).lower():
                    print(f"⚠️  Column {column_name} already exists")
                else:
                    raise e
        
        # Initialize JSON columns properly
        if 'dependency_map' in [col[0] for col in migrations_needed]:
            cursor.execute("UPDATE tasks SET dependency_map = '[]' WHERE dependency_map IS NULL")
            print("✅ Initialized dependency_map values")
        
        if 'blocked_by' in [col[0] for col in migrations_needed]:
            cursor.execute("UPDATE tasks SET blocked_by = '[]' WHERE blocked_by IS NULL")
            print("✅ Initialized blocked_by values")
        
        # Commit changes
        conn.commit()
        
        # Verify migration
        cursor.execute("SELECT COUNT(*) FROM tasks")
        task_count = cursor.fetchone()[0]
        print(f"✅ Migration completed successfully for {task_count} tasks!")
        
        # Show new schema
        cursor.execute("PRAGMA table_info(tasks)")
        columns = cursor.fetchall()
        print("\n📋 Updated Tasks table schema:")
        for col in columns:
            if col[1] in ['effort_score', 'impact_score', 'dependency_map', 'blocked_by', 'priority_score']:
                print(f"   🆕 {col[1]}: {col[2]} (default: {col[4]})")
        
        conn.close()
        
        print("\n🎯 Smart Task Prioritization Engine migration completed!")
        print("Next steps:")
        print("1. Restart your Flask application")
        print("2. Use the new API endpoints to recalculate priorities")
        print("3. Update your frontend to use the new prioritization features")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        raise

def recalculate_existing_priorities():
    """Recalculate priorities for existing tasks"""
    print("\n🔄 Recalculating priorities for existing tasks...")
    
    # This would be done through the Flask app context
    print("To recalculate priorities, run from your Flask app:")
    print("from task_prioritization import TaskPrioritizationEngine")
    print("from models import Tasks, Projects")
    print("")
    print("projects = Projects.query.all()")
    print("for project in projects:")
    print("    TaskPrioritizationEngine.update_project_task_priorities(project.id)")

if __name__ == "__main__":
    migrate_database()
    recalculate_existing_priorities() 