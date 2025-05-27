# secrets_manager.py - Transparent secret management for ICI Chat
"""
Hybrid secrets management implementation
- Development: Environment variables with clear documentation
- Production: Google Secret Manager with audit logging
- Transparency: Clear logging without exposing secret values
"""

import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

# Only import Google Cloud client if available (production)
try:
    from google.cloud import secretmanager
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    secretmanager = None

logger = logging.getLogger(__name__)

class TransparentSecretsManager:
    """
    Transparent secrets management for ICI Chat
    Balances security with open-source transparency
    
    Features:
    - Hybrid approach: env vars (dev) + Secret Manager (prod)
    - Transparent logging without exposing values
    - Graceful fallbacks for different environments
    - Clear error reporting and debugging
    """
    
    def __init__(self):
        self.project_id = os.getenv('GOOGLE_CLOUD_PROJECT')
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.client = None
        
        # Initialize Google Cloud client if available and configured
        if GOOGLE_CLOUD_AVAILABLE and self.project_id:
            try:
                self.client = secretmanager.SecretManagerServiceClient()
                logger.info(f"Secret Manager client initialized - Project: {self.project_id}")
            except Exception as e:
                logger.warning(f"Could not initialize Secret Manager client: {e}")
                self.client = None
        
        # Log configuration transparently (no secret values)
        logger.info(f"Secrets Manager initialized - Environment: {self.environment}, "
                   f"Secret Manager available: {bool(self.client)}")
    
    def get_secret(self, secret_name: str) -> Optional[str]:
        """
        Retrieve secret with transparent logging
        Logs access attempts without exposing values
        
        Args:
            secret_name: Name of the secret to retrieve
            
        Returns:
            Secret value or None if not found
        """
        try:
            if self.client and self.project_id and self.environment == 'production':
                # Production: Use Secret Manager
                return self._get_from_secret_manager(secret_name)
            else:
                # Development: Use environment variables
                return self._get_from_environment(secret_name)
                
        except Exception as e:
            logger.error(f"Failed to retrieve secret {secret_name}: {str(e)}")
            return None
    
    def _get_from_secret_manager(self, secret_name: str) -> Optional[str]:
        """Get secret from Google Secret Manager"""
        try:
            secret_path = f"projects/{self.project_id}/secrets/{secret_name}/versions/latest"
            response = self.client.access_secret_version(request={"name": secret_path})
            
            # Transparent logging (no secret value)
            logger.info(f"Secret retrieved from Secret Manager: {secret_name}")
            return response.payload.data.decode("UTF-8")
            
        except Exception as e:
            logger.warning(f"Secret {secret_name} not found in Secret Manager: {e}")
            # Fallback to environment variables
            return self._get_from_environment(secret_name)
    
    def _get_from_environment(self, secret_name: str) -> Optional[str]:
        """Get secret from environment variables"""
        value = os.getenv(secret_name)
        if value:
            logger.info(f"Secret retrieved from environment: {secret_name}")
        else:
            logger.warning(f"Secret not found in environment: {secret_name}")
        return value
    
    def list_available_secrets(self) -> List[str]:
        """
        List available secrets for debugging
        Returns secret names only (not values) for transparency
        """
        secrets = []
        
        # Known secrets to check for
        known_secrets = [
            'SENDGRID_API_KEY',
            'MAILGUN_API_KEY', 
            'MAILGUN_DOMAIN',
            'TUTANOTA_USERNAME',
            'TUTANOTA_PASSWORD',
            'JWT_SECRET_KEY',
            'DATABASE_URL',
            'ADMIN_EMAIL',
            'ADMIN_PASSWORD'
        ]
        
        # Check environment variables
        for secret in known_secrets:
            if os.getenv(secret):
                secrets.append(f"env:{secret}")
        
        # Check Secret Manager (names only)
        if self.client and self.project_id:
            try:
                parent = f"projects/{self.project_id}"
                for secret in self.client.list_secrets(request={"parent": parent}):
                    secret_name = secret.name.split('/')[-1]
                    secrets.append(f"sm:{secret_name}")
            except Exception as e:
                logger.warning(f"Could not list Secret Manager secrets: {e}")
        
        logger.info(f"Available secrets: {len(secrets)} found")
        return secrets
    
    def check_configuration_health(self) -> Dict[str, Any]:
        """
        Check secrets configuration health
        Returns status without exposing values
        """
        health = {
            'environment': self.environment,
            'secret_manager_available': bool(self.client),
            'google_cloud_project': bool(self.project_id),
            'secrets_found': {},
            'total_secrets': 0,
            'healthy': True,
            'issues': []
        }
        
        # Check critical secrets
        critical_secrets = ['SENDGRID_API_KEY', 'MAILGUN_API_KEY', 'TUTANOTA_USERNAME']
        email_configured = False
        
        for secret in critical_secrets:
            if self.get_secret(secret):
                health['secrets_found'][secret] = True
                email_configured = True
            else:
                health['secrets_found'][secret] = False
        
        # Check if email is configured
        if not email_configured:
            health['healthy'] = False
            health['issues'].append("No email provider configured")
        
        # Check JWT secret
        if not self.get_secret('JWT_SECRET_KEY'):
            health['issues'].append("JWT secret not configured (optional)")
        
        health['total_secrets'] = len([s for s in health['secrets_found'].values() if s])
        
        return health

# Global instance for easy access
secrets_manager = TransparentSecretsManager()
