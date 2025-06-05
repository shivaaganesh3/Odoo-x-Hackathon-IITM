import requests
import json

def test_login():
    base_url = "http://localhost:5000/api"
    
    # Test backend connectivity
    print("🔌 Testing backend connectivity...")
    try:
        response = requests.get(f"{base_url}/auth/debug/users")
        print(f"   ✅ Backend responsive: {response.status_code}")
        print(f"   Users: {response.json()}")
    except Exception as e:
        print(f"   ❌ Backend connection failed: {e}")
        return
    
    # Test login
    print("\n🔐 Testing login...")
    login_data = {
        "email": "abc@gmail.com",
        "password": "test123"
    }
    
    try:
        response = requests.post(
            f"{base_url}/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.text}")
        
        if response.status_code == 200:
            print("   ✅ Login successful!")
            
            # Test authenticated endpoint
            cookies = response.cookies
            me_response = requests.get(f"{base_url}/auth/me", cookies=cookies)
            print(f"   Current user check: {me_response.status_code}")
            
            if me_response.status_code == 200:
                print(f"   User data: {me_response.json()}")
            
        else:
            print(f"   ❌ Login failed")
            
    except Exception as e:
        print(f"   ❌ Login error: {e}")

if __name__ == "__main__":
    test_login() 