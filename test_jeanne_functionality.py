# Test script to verify "Who is [person]?" functionality
import requests
import urllib3
import json

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_who_is_functionality():
    print("=== Testing 'Who is [person]?' Functionality ===\n")
    
    base_url = "https://localhost:8080"
    
    # Step 1: Add some data about Jeanne to memory
    print("Step 1: Adding information about Jeanne to shared memory...")
    
    test_data = {
        "env_id": "test-jeanne-demo",
        "value": [
            {
                "text": "Jeanne is the project manager for our new initiative",
                "user": "alice",
                "timestamp": 1640995200000
            },
            {
                "text": "Jeanne works in the marketing department and loves coffee",
                "user": "bob", 
                "timestamp": 1640995300000
            },
            {
                "text": "Meeting with Jeanne scheduled for tomorrow at 3pm",
                "user": "charlie",
                "timestamp": 1640995400000
            }
        ]
    }
    
    try:
        # Post data to env-box
        response = requests.post(f"{base_url}/env-box", json=test_data, verify=False, timeout=10)
        if response.status_code == 200:
            print(f"✅ Successfully stored data about Jeanne")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed to store data: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"❌ Error storing data: {e}")
        return
    
    print()
    
    # Step 2: Add more data about Jeanne to IP-shared memory  
    print("Step 2: Adding more information about Jeanne to IP-shared memory...")
    
    ip_data = {
        "env_id": "test-jeanne-demo",
        "public_ip": "192.168.1.100",
        "value": [
            {
                "text": "Jeanne mentioned she's available for the client call on Friday",
                "user": "diana",
                "timestamp": 1640995500000
            }
        ]
    }
    
    try:
        response = requests.post(f"{base_url}/ip-box", json=ip_data, verify=False, timeout=10)
        if response.status_code == 200:
            print(f"✅ Successfully stored IP-shared data about Jeanne")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Failed to store IP data: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error storing IP data: {e}")
    
    print()
    
    # Step 3: Test the "Who is Jeanne?" query
    print("Step 3: Testing 'Who is Jeanne?' query...")
    
    chat_data = {
        "message": "Who is Jeanne?",
        "user_id": "test-user"
    }
    
    try:
        response = requests.post(f"{base_url}/ai-chat-enhanced", json=chat_data, verify=False, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"   Memory Context Found: {result.get('memory_context_found', False)}")
            print(f"   Response: {result.get('response', 'No response')}")
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error querying: {e}")
    
    print()
    
    # Step 4: Test a person not in memory
    print("Step 4: Testing 'Who is Unknown?' query...")
    
    chat_data = {
        "message": "Who is Unknown?",
        "user_id": "test-user"
    }
    
    try:
        response = requests.post(f"{base_url}/ai-chat-enhanced", json=chat_data, verify=False, timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Query successful!")
            print(f"   Memory Context Found: {result.get('memory_context_found', False)}")
            print(f"   Response: {result.get('response', 'No response')}")
        else:
            print(f"❌ Query failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error querying: {e}")

if __name__ == "__main__":
    test_who_is_functionality()
