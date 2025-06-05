import sqlite3
from werkzeug.security import generate_password_hash

def fix_password_hash():
    print("🔧 Fixing password hash format...")
    
    conn = sqlite3.connect('taskmanager.db')
    cursor = conn.cursor()
    
    try:
        # Check current password hash
        cursor.execute('SELECT id, email, password FROM users WHERE email = ?', ('abc@gmail.com',))
        user = cursor.fetchone()
        
        if not user:
            print("❌ User not found!")
            return
        
        user_id, email, current_hash = user
        print(f"📋 Current user:")
        print(f"   Email: {email}")
        print(f"   Current hash: {current_hash}")
        print(f"   Hash format valid: {current_hash.count('$') >= 2}")
        
        # Generate a proper Werkzeug password hash
        new_password = 'test123'
        new_hash = generate_password_hash(new_password, method='scrypt')
        
        print(f"\n🔐 Generating new hash:")
        print(f"   Password: {new_password}")
        print(f"   New hash: {new_hash}")
        print(f"   Hash format: {new_hash.split('$')[0] if '$' in new_hash else 'No $ found'}")
        
        # Update password
        cursor.execute('UPDATE users SET password = ? WHERE email = ?', (new_hash, email))
        conn.commit()
        
        # Verify update
        cursor.execute('SELECT password FROM users WHERE email = ?', (email,))
        updated_hash = cursor.fetchone()[0]
        
        print(f"\n✅ Password updated:")
        print(f"   Updated hash: {updated_hash}")
        print(f"   Hash parts: {updated_hash.split('$') if '$' in updated_hash else 'No $ delimiter'}")
        
        # Test the hash
        from werkzeug.security import check_password_hash
        is_valid = check_password_hash(updated_hash, new_password)
        print(f"   Hash validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    fix_password_hash() 