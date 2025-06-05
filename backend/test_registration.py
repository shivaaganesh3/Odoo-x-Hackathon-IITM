import requests
import json

def test_registration():
    print("🧪 Testing Registration API")
    print("=" * 40)
    
    url = "http://localhost:5000/api/auth/register"
    
    # Test data
    test_user = {
        "name": "Test Registration User",
        "email": "registration@test.com", 
        "password": "test123456"
    }
    
    try:
        print(f"📡 Sending POST to: {url}")
        print(f"📝 Data: {json.dumps(test_user, indent=2)}")
        
        response = requests.post(
            url, 
            json=test_user,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"\n📊 Response Status: {response.status_code}")
        print(f"📄 Response Headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"📋 Response Data: {json.dumps(response_data, indent=2)}")
        except:
            print(f"📋 Response Text: {response.text}")
            
        if response.status_code in [200, 201]:
            print("✅ Registration SUCCESSFUL!")
        else:
            print("❌ Registration FAILED!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Is it running on port 5000?")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_registration() 