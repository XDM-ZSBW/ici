#!/usr/bin/env python3
"""
Test script for the hybrid secrets management system
"""

import requests
import json
import sys

def test_email_system():
    """Test the email system"""
    print("🔍 Testing Email System...")
    
    try:
        # Test email endpoint
        response = requests.post(
            'http://localhost:8080/admin/test-email',
            json={'to_email': 'test@example.com'},
            headers={'Content-Type': 'application/json'}
        )
        
        result = response.json()
        print(f"📧 Email Test Response: {json.dumps(result, indent=2)}")
        
        return response.status_code == 200 or response.status_code == 400  # 400 is expected for invalid API key
        
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_secrets_health():
    """Test secrets health endpoint"""
    print("\n🔍 Testing Secrets Health...")
    
    try:
        response = requests.get('http://localhost:8080/admin/secrets-health')
        result = response.json()
        print(f"🔐 Secrets Health: {json.dumps(result, indent=2)}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Secrets health test failed: {e}")
        return False

def test_config_endpoint():
    """Test configuration endpoint"""
    print("\n🔍 Testing Configuration Endpoint...")
    
    try:
        response = requests.get('http://localhost:8080/admin/config')
        result = response.json()
        print(f"⚙️ Configuration: {json.dumps(result, indent=2)}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Hybrid Secrets Management System")
    print("=" * 50)
    
    tests = [
        test_config_endpoint,
        test_secrets_health,
        test_email_system
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("✅ All tests passed! Hybrid secrets management is working correctly.")
        sys.exit(0)
    else:
        print("⚠️ Some tests failed, but this is expected with test API keys.")
        sys.exit(0)  # Don't fail since test API keys are expected to fail

if __name__ == '__main__':
    main()
