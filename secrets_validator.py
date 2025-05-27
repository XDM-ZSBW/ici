#!/usr/bin/env python3
"""
Secrets Configuration Validator for ICI Chat
Validates hybrid secrets management setup and provides recommendations
"""

import os
import sys
import argparse
from typing import Dict, Any, List
import json

# Add backend to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from backend.utils.config import config
    from backend.utils.secrets_manager import secrets_manager
    BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Backend imports not available: {e}")
    BACKEND_AVAILABLE = False

def check_environment_file() -> Dict[str, Any]:
    """Check if .env file exists and is properly configured"""
    result = {
        'env_file_exists': False,
        'env_example_exists': False,
        'env_variables_found': 0,
        'missing_variables': [],
        'recommendations': []
    }
    
    # Check .env.example exists
    env_example_path = '.env.example'
    if os.path.exists(env_example_path):
        result['env_example_exists'] = True
    else:
        result['recommendations'].append("Create .env.example file with template variables")
    
    # Check .env exists
    env_path = '.env'
    if os.path.exists(env_path):
        result['env_file_exists'] = True
        
        # Count configured variables (non-empty)
        with open(env_path, 'r') as f:
            lines = f.readlines()
            
        configured_vars = 0
        for line in lines:
            line = line.strip()
            if '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                if value and value != 'your_value_here':
                    configured_vars += 1
        
        result['env_variables_found'] = configured_vars
    else:
        result['recommendations'].append("Copy .env.example to .env and configure your secrets")
    
    return result

def check_secrets_configuration() -> Dict[str, Any]:
    """Check secrets configuration using the hybrid manager"""
    if not BACKEND_AVAILABLE:
        return {
            'error': 'Backend not available',
            'recommendations': ['Fix import issues before checking secrets']
        }
    
    try:
        # Get configuration health
        config_health = config.get_configuration_report()
        secrets_health = secrets_manager.check_configuration_health()
        validation = config.validate_configuration()
        
        return {
            'configuration_report': config_health,
            'secrets_health': secrets_health,
            'validation': validation,
            'email_status': config.is_email_enabled(),
            'provider': config.email_provider
        }
        
    except Exception as e:
        return {
            'error': f'Configuration check failed: {e}',
            'recommendations': ['Check that all required dependencies are installed']
        }

def check_email_providers() -> Dict[str, Any]:
    """Check which email providers are configured"""
    providers = {
        'sendgrid': {
            'configured': bool(os.getenv('SENDGRID_API_KEY')),
            'api_key_format': 'SG.xxx...',
            'setup_url': 'https://app.sendgrid.com/settings/api_keys'
        },
        'mailgun': {
            'configured': bool(os.getenv('MAILGUN_API_KEY') and os.getenv('MAILGUN_DOMAIN')),
            'api_key_format': 'key-xxx...',
            'setup_url': 'https://app.mailgun.com/mg/dashboard'
        },
        'tutanota': {
            'configured': bool(os.getenv('TUTANOTA_USERNAME') and os.getenv('TUTANOTA_PASSWORD')),
            'api_key_format': 'username@tutanota.com + password',
            'setup_url': 'https://tutanota.com/business'
        }
    }
    
    configured_count = sum(1 for p in providers.values() if p['configured'])
    
    return {
        'providers': providers,
        'configured_count': configured_count,
        'recommendations': [
            "Configure at least one email provider for notifications",
            "SendGrid recommended for production (reliable delivery)",
            "Mailgun good for development (generous free tier)",
            "Tutanota for privacy-focused deployments"
        ] if configured_count == 0 else []
    }

def check_google_cloud_setup() -> Dict[str, Any]:
    """Check Google Cloud / Secret Manager setup"""
    result = {
        'google_cloud_project': os.getenv('GOOGLE_CLOUD_PROJECT'),
        'environment': os.getenv('ENVIRONMENT', 'development'),
        'secret_manager_available': False,
        'recommendations': []
    }
    
    try:
        from google.cloud import secretmanager
        result['secret_manager_available'] = True
        
        if result['google_cloud_project']:
            result['recommendations'].append("Secret Manager configured for production use")
        else:
            result['recommendations'].append("Set GOOGLE_CLOUD_PROJECT for production deployments")
            
    except ImportError:
        result['recommendations'].append("Install google-cloud-secret-manager for production: pip install google-cloud-secret-manager")
    
    return result

def generate_setup_commands() -> List[str]:
    """Generate setup commands based on current state"""
    commands = []
    
    # Check if .env exists
    if not os.path.exists('.env'):
        commands.append("# Copy environment template")
        commands.append("Copy-Item .env.example .env")
        commands.append("")
    
    # Generate JWT secret if needed
    if not os.getenv('JWT_SECRET_KEY'):
        commands.append("# Generate JWT secret")
        commands.append('python -c "import secrets; print(f\'JWT_SECRET_KEY={secrets.token_urlsafe(32)}\')" >> .env')
        commands.append("")
    
    # Check email setup
    email_configured = any([
        os.getenv('SENDGRID_API_KEY'),
        os.getenv('MAILGUN_API_KEY'),
        os.getenv('TUTANOTA_USERNAME')
    ])
    
    if not email_configured:
        commands.append("# Configure email provider (choose one):")
        commands.append("# For SendGrid: Get API key from https://app.sendgrid.com/settings/api_keys")
        commands.append("# echo 'SENDGRID_API_KEY=SG.your_key_here' >> .env")
        commands.append("")
        commands.append("# For Mailgun: Get API key from https://app.mailgun.com/mg/dashboard")
        commands.append("# echo 'MAILGUN_API_KEY=key-your_key_here' >> .env")
        commands.append("# echo 'MAILGUN_DOMAIN=your-domain.com' >> .env")
        commands.append("")
    
    # Test configuration
    commands.append("# Test configuration")
    commands.append("python validate.py --check-secrets")
    commands.append(".\\daily_health_check.ps1")
    
    return commands

def print_results(results: Dict[str, Any], verbose: bool = False):
    """Print validation results in a readable format"""
    print("🔐 ICI Chat Secrets Configuration Validator")
    print("=" * 50)
    
    # Environment file check
    env_check = results['environment_check']
    print(f"\n📁 Environment Files:")
    print(f"   .env.example exists: {'✅' if env_check['env_example_exists'] else '❌'}")
    print(f"   .env file exists: {'✅' if env_check['env_file_exists'] else '❌'}")
    if env_check['env_file_exists']:
        print(f"   Configured variables: {env_check['env_variables_found']}")
    
    # Email providers
    email_check = results['email_providers']
    print(f"\n📧 Email Providers:")
    for provider, info in email_check['providers'].items():
        status = '✅' if info['configured'] else '❌'
        print(f"   {provider.title()}: {status}")
    
    print(f"   Total configured: {email_check['configured_count']}/3")
    
    # Google Cloud setup
    gc_check = results['google_cloud']
    print(f"\n☁️  Google Cloud Setup:")
    print(f"   Project ID: {gc_check['google_cloud_project'] or 'Not set'}")
    print(f"   Environment: {gc_check['environment']}")
    print(f"   Secret Manager: {'✅' if gc_check['secret_manager_available'] else '❌'}")
    
    # Configuration health (if backend available)
    if 'secrets_config' in results and 'error' not in results['secrets_config']:
        config_health = results['secrets_config']
        print(f"\n⚙️  Configuration Health:")
        
        if 'configuration_report' in config_health:
            report = config_health['configuration_report']
            print(f"   Email enabled: {'✅' if report['email_enabled'] else '❌'}")
            print(f"   Email provider: {report['email_provider'] or 'None'}")
            print(f"   Total configured: {report['total_configured']}/4 modules")
            
        if 'validation' in config_health:
            validation = config_health['validation']
            print(f"   Validation: {'✅ Valid' if validation['valid'] else '⚠️  Issues found'}")
    
    # Recommendations
    all_recommendations = []
    for check_name, check_result in results.items():
        if isinstance(check_result, dict) and 'recommendations' in check_result:
            all_recommendations.extend(check_result['recommendations'])
    
    if all_recommendations:
        print(f"\n💡 Recommendations:")
        for i, rec in enumerate(all_recommendations[:5], 1):  # Limit to top 5
            print(f"   {i}. {rec}")
    
    # Setup commands
    setup_commands = results['setup_commands']
    if setup_commands and len(setup_commands) > 2:  # More than just test commands
        print(f"\n🚀 Quick Setup Commands:")
        for cmd in setup_commands[:8]:  # Limit output
            if cmd.strip():
                print(f"   {cmd}")
      # Overall status
    email_configured = email_check['configured_count'] > 0
    env_exists = env_check['env_file_exists']
    
    print(f"\n📊 Overall Status:")
    if email_configured and env_exists:
        print("   ✅ Ready for email functionality")
    elif env_exists:
        print("   ⚠️  Environment configured, but no email provider")
    else:
        print("   ❌ Setup required")
    
    if verbose and 'secrets_config' in results:
        print(f"\n🔍 Detailed Configuration:")
        print(json.dumps(results['secrets_config'], indent=2, default=str))

def main():
    parser = argparse.ArgumentParser(description='Validate ICI Chat secrets configuration')
    parser.add_argument('--check-secrets', action='store_true', help='Check secrets configuration')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='Output JSON format')
    
    args = parser.parse_args()
    
    # Run all checks
    results = {
        'environment_check': check_environment_file(),
        'email_providers': check_email_providers(),
        'google_cloud': check_google_cloud_setup(),
        'secrets_config': check_secrets_configuration(),
        'setup_commands': generate_setup_commands()
    }
    
    if args.json:
        print(json.dumps(results, indent=2, default=str))
    else:
        print_results(results, verbose=args.verbose)
    
    # Exit code based on status
    email_configured = results['email_providers']['configured_count'] > 0
    env_exists = results['environment_check']['env_file_exists']
    
    if email_configured and env_exists:
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Setup needed

if __name__ == '__main__':
    main()
