import sqlite3
import os

def debug_database():
    print("🔍 Database Debug Analysis")
    print("=" * 50)
    
    # Check if database file exists
    db_file = 'taskmanager.db'
    if os.path.exists(db_file):
        print(f"✅ Database file exists: {db_file}")
        file_size = os.path.getsize(db_file)
        print(f"   File size: {file_size} bytes")
    else:
        print(f"❌ Database file missing: {db_file}")
        return
    
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"\n📋 Tables found: {len(tables)}")
        for table in tables:
            table_name = table[0]
            print(f"   - {table_name}")
            
            # Get table structure
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            print(f"     Columns: {len(columns)}")
            for col in columns:
                print(f"       • {col[1]} ({col[2]})")
            
            # Get row count
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"     Rows: {count}")
            print()
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")

if __name__ == "__main__":
    debug_database() 