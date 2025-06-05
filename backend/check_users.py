import sqlite3
import os

def check_users():
    if not os.path.exists('taskmanager.db'):
        print("Database not found!")
        return
    
    conn = sqlite3.connect('taskmanager.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute('SELECT id, email, name FROM users')
        users = cursor.fetchall()
        
        print(f"Found {len(users)} users:")
        for user in users:
            print(f"   ID: {user[0]}, Email: {user[1]}, Name: {user[2]}")
        
        cursor.execute('SELECT COUNT(*) FROM projects')
        project_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM custom_status')
        status_count = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM tasks')
        task_count = cursor.fetchone()[0]
        
        print(f"\nDatabase overview:")
        print(f"   Projects: {project_count}")
        print(f"   Custom Statuses: {status_count}")
        print(f"   Tasks: {task_count}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_users() 