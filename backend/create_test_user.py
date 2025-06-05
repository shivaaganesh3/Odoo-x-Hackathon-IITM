import sqlite3
from werkzeug.security import generate_password_hash
import uuid

def create_test_user():
    conn = sqlite3.connect('taskmanager.db')
    cursor = conn.cursor()
    
    try:
        # Check if user exists
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', ('abc@gmail.com',))
        if cursor.fetchone()[0] > 0:
            print("User abc@gmail.com already exists!")
            return
        
        # Create test user with known password
        email = 'abc@gmail.com'
        password = 'test123'  # Simple password for testing
        name = 'abc'
        hashed_password = generate_password_hash(password)
        fs_uniquifier = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO users (email, password, fs_uniquifier, name, active) 
            VALUES (?, ?, ?, ?, 1)
        ''', (email, hashed_password, fs_uniquifier, name))
        
        conn.commit()
        print(f"✅ Created test user:")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Name: {name}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    create_test_user() 