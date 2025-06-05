import sqlite3
from werkzeug.security import check_password_hash

def verify_user():
    conn = sqlite3.connect('taskmanager.db')
    cursor = conn.cursor()
    
    try:
        # Get user data
        cursor.execute('SELECT id, email, password, name FROM users WHERE email = ?', ('abc@gmail.com',))
        user = cursor.fetchone()
        
        if not user:
            print("❌ User not found!")
            return
        
        user_id, email, hashed_password, name = user
        print(f"✅ User found:")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Name: {name}")
        print(f"   Password hash: {hashed_password[:50]}...")
        
        # Test password
        test_password = 'test123'
        is_valid = check_password_hash(hashed_password, test_password)
        
        print(f"\n🔐 Password test:")
        print(f"   Testing password: {test_password}")
        print(f"   Result: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
        if not is_valid:
            print(f"\n🔧 Let's update the password...")
            from werkzeug.security import generate_password_hash
            new_hash = generate_password_hash(test_password)
            cursor.execute('UPDATE users SET password = ? WHERE email = ?', (new_hash, email))
            conn.commit()
            print(f"   Password updated successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    verify_user() 