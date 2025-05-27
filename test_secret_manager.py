#!/usr/bin/env python3
"""
Google Secret Manager Test Script
Tests retrieval of "A_Secret_Seed" secret and prints to console
"""

import os
import sys
import logging

def ensure_project_id():
    project_id = os.environ.get('GOOGLE_CLOUD_PROJECT')
    if not project_id or not project_id.strip():
        print("GOOGLE_CLOUD_PROJECT environment variable is not set or is empty.")
        project_id = input("Please enter your Google Cloud Project ID: ").strip()
        if project_id:
            os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
            print(f"Set GOOGLE_CLOUD_PROJECT to '{project_id}' for this session.")
        else:
            print("No project ID entered. Exiting.")
            sys.exit(1)
    return project_id

# Configure logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_secret_retrieval(secrets_manager):
    """Test retrieving a secret from Secret Manager or environment"""
    
    print("=" * 60)
    print("Google Secret Manager Test")
    print("=" * 60)
    
    # Display current configuration
    print(f"Environment: {secrets_manager.environment}")
    print(f"Google Cloud Project: {secrets_manager.project_id or 'Not set'}")
    print(f"Secret Manager Client Available: {bool(secrets_manager.client)}")
    print()
    
    # Prompt for secret name
    secret_name = input("Enter the secret name to retrieve: ").strip()
    print(f"Attempting to retrieve secret: {secret_name}")
    print("-" * 40)
    
    try:
        # Try original, UPPERCASE, and lowercase
        secret_value = secrets_manager.get_secret(secret_name)
        if not secret_value:
            secret_value = secrets_manager.get_secret(secret_name.upper())
        if not secret_value:
            secret_value = secrets_manager.get_secret(secret_name.lower())

        if secret_value:
            print(f"✅ SUCCESS: Secret '{secret_name}' retrieved successfully!")
            print(f"Secret Value: {secret_value}")
            print(f"Secret Length: {len(secret_value)} characters")
        else:
            print(f"❌ FAILED: Secret '{secret_name}' not found or could not be retrieved")
            print("This could mean:")
            print("  - Secret doesn't exist in Secret Manager")
            print("  - Secret not set in environment variables")
            print("  - Authentication/permission issues")
            
    except Exception as e:
        print(f"❌ ERROR: Exception occurred while retrieving secret: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Show configuration health
    print("Configuration Health Check:")
    print("-" * 40)
    health = secrets_manager.check_configuration_health()
    print(f"Overall Health: {'✅ Healthy' if health['healthy'] else '❌ Issues Found'}")
    print(f"Environment: {health['environment']}")
    print(f"Secret Manager Available: {health['secret_manager_available']}")
    print(f"Google Cloud Project Set: {health['google_cloud_project']}")
    print(f"Total Secrets Found: {health['total_secrets']}")
    
    if health['issues']:
        print("Issues:")
        for issue in health['issues']:
            print(f"  - {issue}")
    
    print()
    
    # List available secrets
    print("Available Secrets:")
    print("-" * 40)
    available_secrets = secrets_manager.list_available_secrets()
    if available_secrets:
        for secret in available_secrets:
            print(f"  - {secret}")
    else:
        print("  No secrets found")
    
    print()
    print("=" * 60)
    print("Test Complete")
    print("=" * 60)

def setup_environment_instructions():
    """Provide instructions for setting up the environment"""
    print("\n" + "=" * 60)
    print("SETUP INSTRUCTIONS")
    print("=" * 60)
    print("To test with Google Secret Manager:")
    print()
    print("1. Set environment variables:")
    print("   $env:GOOGLE_CLOUD_PROJECT = 'your-project-id'")
    print("   $env:ENVIRONMENT = 'production'")
    print()
    print("2. Authenticate with Google Cloud:")
    print("   gcloud auth application-default login")
    print()
    print("3. Install Google Cloud Secret Manager:")
    print("   pip install google-cloud-secret-manager")
    print()
    print("4. Create the secret in Google Cloud:")
    print("   gcloud secrets create A_Secret_Seed --data-file=-")
    print("   (then type your secret value and press Ctrl+Z on Windows)")
    print()
    print("To test with environment variables only:")
    print("   $env:A_Secret_Seed = 'your-secret-value'")
    print("=" * 60)

if __name__ == "__main__":
    # Always prompt for project id, even if env var is set
    print("[DEBUG] Forcing prompt for Google Cloud Project ID...")
    project_id = input("Please enter your Google Cloud Project ID: ").strip()
    if not project_id:
        print("No project ID entered. Exiting.")
        sys.exit(1)
    os.environ['GOOGLE_CLOUD_PROJECT'] = project_id
    print(f"[DEBUG] GOOGLE_CLOUD_PROJECT set to: {os.environ.get('GOOGLE_CLOUD_PROJECT')}")

    # Add a switch to set environment to production
    set_prod = '--production' in sys.argv
    if set_prod:
        os.environ['ENVIRONMENT'] = 'production'
        print("[DEBUG] ENVIRONMENT set to: production")
    else:
        print("[DEBUG] ENVIRONMENT set to:", os.environ.get('ENVIRONMENT', '(not set)'))

    from backend.utils.secrets_manager import secrets_manager
    test_secret_retrieval(secrets_manager)
    setup_environment_instructions()
