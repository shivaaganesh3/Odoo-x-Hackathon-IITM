import sqlite3
from werkzeug.security import generate_password_hash
import uuid

def clean_users():
    print("🧹 Cleaning up users table...")
    
    conn = sqlite3.connect('taskmanager.db')
    cursor = conn.cursor()
    
    try:
        # Delete all existing users
        cursor.execute('DELETE FROM users')
        print("   Deleted all existing users")
        
        # Create one clean user
        email = 'abc@gmail.com'
        password = 'test123'
        name = 'abc'
        hashed_password = generate_password_hash(password, method='scrypt')
        fs_uniquifier = str(uuid.uuid4())
        
        cursor.execute('''
            INSERT INTO users (id, email, password, fs_uniquifier, name, active) 
            VALUES (1, ?, ?, ?, ?, 1)
        ''', (email, hashed_password, fs_uniquifier, name))
        
        conn.commit()
        
        # Verify the user
        cursor.execute('SELECT id, email, password, name FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        
        if user:
            user_id, email, password_hash, name = user
            print(f"\n✅ Created clean user:")
            print(f"   ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Name: {name}")
            print(f"   Password: test123")
            print(f"   Hash format: {'Valid' if password_hash.count('$') >= 2 else 'Invalid'}")
            
            # Test hash
            from werkzeug.security import check_password_hash
            is_valid = check_password_hash(password_hash, 'test123')
            print(f"   Hash test: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        print(f"\n🎯 Authentication should now work with:")
        print(f"   Email: abc@gmail.com")
        print(f"   Password: test123")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    clean_users() 