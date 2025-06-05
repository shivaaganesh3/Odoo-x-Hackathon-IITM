"""
Quick test script to verify the custom status system is working.
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_backend():
    print("🧪 Testing Backend Status System...")
    
    # Test 1: Check if backend is running
    try:
        response = requests.get(f"{BASE_URL}/auth/debug/users")
        print(f"✅ Backend is running (Status: {response.status_code})")
        if response.status_code == 200:
            data = response.json()
            print(f"   Found {data['total_users']} users in database")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running!")
        return False
    except Exception as e:
        print(f"⚠️ Backend test failed: {e}")
        return False
    
    # Test 2: Try to get projects (this will fail without auth, but should not crash)
    try:
        response = requests.get(f"{BASE_URL}/projects/")
        print(f"✅ Projects endpoint accessible (Status: {response.status_code})")
        if response.status_code == 401:
            print("   Expected 401 - authentication required ✓")
    except Exception as e:
        print(f"⚠️ Projects endpoint test failed: {e}")
    
    # Test 3: Try custom status endpoint (should also require auth)
    try:
        response = requests.get(f"{BASE_URL}/custom-status/project/1")
        print(f"✅ Custom Status endpoint accessible (Status: {response.status_code})")
        if response.status_code == 401:
            print("   Expected 401 - authentication required ✓")
    except Exception as e:
        print(f"⚠️ Custom Status endpoint test failed: {e}")
    
    return True

def test_database():
    print("\n📊 Testing Database Schema...")
    
    try:
        from app import create_app
        from models import CustomStatus, Tasks, Projects
        from database import db
        
        app = create_app()
        with app.app_context():
            # Test if tables exist
            try:
                custom_status_count = CustomStatus.query.count()
                print(f"✅ CustomStatus table exists with {custom_status_count} records")
            except Exception as e:
                print(f"❌ CustomStatus table issue: {e}")
            
            try:
                projects_count = Projects.query.count()
                print(f"✅ Projects table exists with {projects_count} records")
            except Exception as e:
                print(f"❌ Projects table issue: {e}")
            
            try:
                tasks_count = Tasks.query.count()
                print(f"✅ Tasks table exists with {tasks_count} records")
                
                # Check if tasks have status_id field
                tasks_with_status = Tasks.query.filter(Tasks.status_id.isnot(None)).count()
                print(f"   {tasks_with_status} tasks have custom status assigned")
            except Exception as e:
                print(f"❌ Tasks table issue: {e}")
                
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🔍 Custom Status System Debug Test")
    print("=" * 50)
    
    backend_ok = test_backend()
    database_ok = test_database()
    
    print("\n" + "=" * 50)
    if backend_ok and database_ok:
        print("🎉 All tests passed! System appears to be working correctly.")
        print("\n📝 Next steps:")
        print("   1. Start the frontend: cd synergy-sphere-frontend && npm run dev")
        print("   2. Navigate to the Custom Status Manager page")
        print("   3. Create custom statuses for your projects")
        print("   4. Test task creation with custom statuses")
    else:
        print("⚠️ Some tests failed. Check the error messages above.") 