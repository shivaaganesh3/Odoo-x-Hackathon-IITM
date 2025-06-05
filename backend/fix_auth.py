import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

def fix_authentication():
    print("🔧 Fixing authentication issue...")
    
    conn = sqlite3.connect('taskmanager.db')
    cursor = conn.cursor()
    
    try:
        # Check all users
        cursor.execute('SELECT id, email, password FROM users')
        all_users = cursor.fetchall()
        
        print(f"📋 All users in database:")
        for user in all_users:
            print(f"   ID: {user[0]}, Email: {user[1]}")
        
        # Focus on abc@gmail.com
        cursor.execute('SELECT id, email, password FROM users WHERE email = ?', ('abc@gmail.com',))
        user = cursor.fetchone()
        
        if not user:
            print("❌ User abc@gmail.com not found!")
            return
        
        user_id, email, current_hash = user
        print(f"\n🎯 Target user:")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        
        # Test current password
        test_password = 'test123'
        is_valid_current = check_password_hash(current_hash, test_password)
        
        print(f"\n🔐 Password verification:")
        print(f"   Password: {test_password}")
        print(f"   Current hash valid: {is_valid_current}")
        
        # Generate new hash and test
        new_hash = generate_password_hash(test_password)
        is_valid_new = check_password_hash(new_hash, test_password)
        
        print(f"   New hash valid: {is_valid_new}")
        
        # Update with new hash
        print(f"\n🔄 Updating password hash...")
        cursor.execute('UPDATE users SET password = ? WHERE email = ?', (new_hash, email))
        conn.commit()
        
        # Verify update
        cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
        updated_hash = cursor.fetchone()[0]
        is_valid_updated = check_password_hash(updated_hash, test_password)
        
        print(f"   ✅ Updated hash valid: {is_valid_updated}")
        
        # Also ensure fs_uniquifier exists
        cursor.execute('SELECT fs_uniquifier FROM users WHERE email = ?', (email,))
        uniquifier = cursor.fetchone()[0]
        
        if not uniquifier:
            import uuid
            new_uniquifier = str(uuid.uuid4())
            cursor.execute('UPDATE users SET fs_uniquifier = ? WHERE email = ?', (new_uniquifier, email))
            conn.commit()
            print(f"   ✅ Added fs_uniquifier: {new_uniquifier}")
        else:
            print(f"   ✅ fs_uniquifier exists: {uniquifier}")
        
        print(f"\n✅ Authentication should now work!")
        print(f"   Email: {email}")
        print(f"   Password: {test_password}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_authentication() 