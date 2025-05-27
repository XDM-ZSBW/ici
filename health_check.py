#!/usr/bin/env python3
"""
Daily Health Check Script for ICI Chat Hybrid Secrets Management
Validates configuration, tests services, and generates health reports
"""

import sys
import os
import json
import requests
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def check_server_health() -> Dict[str, Any]:
    """Check if the server is running and responsive"""
    try:
        response = requests.get('https://localhost:8080/health', 
                              verify=False, timeout=10)
        return {
            'server_running': True,
            'status_code': response.status_code,
            'response_time': response.elapsed.total_seconds(),
            'healthy': response.status_code == 200
        }
    except Exception as e:
        return {
            'server_running': False,
            'error': str(e),
            'healthy': False
        }

def check_configuration() -> Dict[str, Any]:
    """Check configuration status via API"""
    try:
        response = requests.get('https://localhost:8080/admin/config',
                              verify=False, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Config check failed: {response.status_code}'}
    except Exception as e:
        return {'error': f'Config check error: {str(e)}'}

def check_secrets_health() -> Dict[str, Any]:
    """Check secrets management health"""
    try:
        response = requests.get('https://localhost:8080/admin/secrets-health',
                              verify=False, timeout=10)
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f'Secrets health check failed: {response.status_code}'}
    except Exception as e:
        return {'error': f'Secrets health error: {str(e)}'}

def test_email_service() -> Dict[str, Any]:
    """Test email service functionality"""
    try:
        test_data = {'to_email': 'health-check@ici-chat.com'}
        response = requests.post('https://localhost:8080/admin/test-email',
                               json=test_data, verify=False, timeout=30)
        
        result = response.json()
        return {
            'email_test_completed': True,
            'provider_responding': response.status_code == 200 or response.status_code == 500,
            'result': result
        }
    except Exception as e:
        return {
            'email_test_completed': False,
            'error': str(e)
        }

def generate_health_report() -> Dict[str, Any]:
    """Generate comprehensive health report"""
    print("🏥 ICI Chat Daily Health Check")
    print("=" * 50)
    print(f"📅 Check Time: {datetime.now().isoformat()}")
    print()
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'checks': {},
        'overall_health': 'unknown'
    }
    
    # Check server health
    print("🌐 Checking server health...")
    server_health = check_server_health()
    report['checks']['server'] = server_health
    
    if server_health['healthy']:
        print("   ✅ Server is running and responsive")
        print(f"   📊 Response time: {server_health.get('response_time', 'N/A')}s")
    else:
        print("   ❌ Server is not responding")
        print(f"   ⚠️  Error: {server_health.get('error', 'Unknown')}")
        return report
    
    # Check configuration
    print("\n⚙️  Checking configuration...")
    config_check = check_configuration()
    report['checks']['configuration'] = config_check
    
    if 'error' not in config_check:
        config_status = config_check.get('configuration', {}).get('configuration_status', {})
        total_configured = sum(config_status.values())
        total_modules = len(config_status)
        print(f"   📋 Configuration: {total_configured}/{total_modules} modules configured")
        
        for module, status in config_status.items():
            status_icon = "✅" if status else "⚠️ "
            print(f"   {status_icon} {module.replace('_', ' ').title()}: {'Configured' if status else 'Not Configured'}")
    else:
        print(f"   ❌ Configuration check failed: {config_check.get('error')}")
    
    # Check secrets health
    print("\n🔐 Checking secrets management...")
    secrets_health = check_secrets_health()
    report['checks']['secrets'] = secrets_health
    
    if 'error' not in secrets_health:
        secrets_source = secrets_health.get('secrets_source', 'Unknown')
        available_secrets = secrets_health.get('available_secrets', 0)
        print(f"   🔑 Secrets source: {secrets_source}")
        print(f"   📊 Available secrets: {available_secrets}")
        
        config_health = secrets_health.get('configuration_health', {})
        if config_health.get('healthy', False):
            print("   ✅ Secrets management is healthy")
        else:
            issues = config_health.get('issues', [])
            print(f"   ⚠️  Secrets issues: {len(issues)}")
            for issue in issues[:3]:  # Show first 3 issues
                print(f"      - {issue}")
    else:
        print(f"   ❌ Secrets health check failed: {secrets_health.get('error')}")
    
    # Test email service
    print("\n📧 Testing email service...")
    email_test = test_email_service()
    report['checks']['email'] = email_test
    
    if email_test.get('email_test_completed', False):
        print("   ✅ Email test completed")
        if email_test.get('provider_responding', False):
            print("   📤 Email provider is responding")
            result = email_test.get('result', {})
            if result.get('success', False):
                print(f"   ✉️  Test email sent via {result.get('provider', 'unknown')}")
            else:
                print(f"   ⚠️  Email test failed: {result.get('error', 'Unknown error')}")
        else:
            print("   ❌ Email provider not responding")
    else:
        print(f"   ❌ Email test failed: {email_test.get('error')}")
    
    # Determine overall health
    all_checks = [
        server_health.get('healthy', False),
        'error' not in config_check,
        'error' not in secrets_health,
        email_test.get('provider_responding', False)
    ]
    
    if all(all_checks):
        report['overall_health'] = 'healthy'
        print("\n🎉 Overall Status: HEALTHY")
    elif any(all_checks):
        report['overall_health'] = 'warning'
        print("\n⚠️  Overall Status: WARNING - Some issues detected")
    else:
        report['overall_health'] = 'critical'
        print("\n🚨 Overall Status: CRITICAL - Multiple failures")
    
    # Save report
    report_file = f"health_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    try:
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\n📄 Report saved to: {report_file}")
    except Exception as e:
        print(f"\n⚠️  Could not save report: {e}")
    
    return report

def main():
    """Main health check function"""
    try:
        # Check if server is likely running
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', 8080))
        sock.close()
        
        if result != 0:
            print("🚨 Server not running on port 8080")
            print("   Start the server with: python app.py")
            return 1
        
        report = generate_health_report()
        
        # Exit with appropriate code
        if report['overall_health'] == 'healthy':
            return 0
        elif report['overall_health'] == 'warning':
            return 1
        else:
            return 2
            
    except KeyboardInterrupt:
        print("\n⏹️  Health check interrupted")
        return 130
    except Exception as e:
        print(f"\n💥 Health check failed: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
