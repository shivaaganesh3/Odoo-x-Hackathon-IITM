import sqlite3

def debug_user_lookup():
    conn = sqlite3.connect('taskmanager.db')
    cursor = conn.cursor()
    
    try:
        # Get all users with their details
        cursor.execute('SELECT id, email, password, name FROM users ORDER BY id')
        all_users = cursor.fetchall()
        
        print("🔍 All users in database:")
        for i, user in enumerate(all_users):
            user_id, email, password_hash, name = user
            print(f"   User {i+1}:")
            print(f"     ID: {user_id}")
            print(f"     Email: {email}")
            print(f"     Name: {name}")
            print(f"     Password hash: {password_hash[:50]}{'...' if len(password_hash) > 50 else ''}")
            print(f"     Hash format: {'Valid' if password_hash.count('$') >= 2 else 'Invalid'}")
            print()
        
        # Specifically search for abc@gmail.com
        cursor.execute('SELECT id, email, password FROM users WHERE email = ?', ('abc@gmail.com',))
        user = cursor.fetchone()
        
        if user:
            user_id, email, password_hash = user
            print(f"🎯 Found abc@gmail.com:")
            print(f"   ID: {user_id}")
            print(f"   Email: {email}")
            print(f"   Full password hash: {password_hash}")
            print(f"   Hash parts: {password_hash.split('$') if '$' in password_hash else 'No $ found'}")
            
            # Test the hash manually
            from werkzeug.security import check_password_hash
            try:
                is_valid = check_password_hash(password_hash, 'test123')
                print(f"   Hash validation: {'✅ VALID' if is_valid else '❌ INVALID'}")
            except Exception as e:
                print(f"   Hash validation error: {e}")
        else:
            print("❌ abc@gmail.com not found!")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    debug_user_lookup() 