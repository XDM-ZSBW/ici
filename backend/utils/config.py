# config.py - Transparent configuration management for ICI Chat
"""
Configuration management with transparent status reporting
Integrates with hybrid secrets management approach
"""

import os
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .secrets_manager import secrets_manager

logger = logging.getLogger(__name__)

class Config:
    """
    Configuration management for ICI Chat
    Transparent about what's configured, secure about values
    
    Features:
    - Transparent status reporting
    - Multiple email provider support
    - Environment-specific configuration
    - Health check integration
    """
    
    def __init__(self):
        self.secrets = secrets_manager
        self.environment = os.getenv('ENVIRONMENT', 'development')
        self.config_status = self._check_configuration()
        
        logger.info(f"Configuration initialized for environment: {self.environment}")
    
    def _check_configuration(self) -> Dict[str, bool]:
        """
        Check configuration status transparently
        Returns what's configured without exposing values
        """
        status = {
            'email_configured': False,
            'database_configured': False,
            'auth_configured': False,
            'admin_configured': False
        }
        
        # Check email configuration (any provider)
        email_providers = [
            'SENDGRID_API_KEY',
            'MAILGUN_API_KEY', 
            'TUTANOTA_USERNAME'
        ]
        
        for provider in email_providers:
            if self.secrets.get_secret(provider):
                status['email_configured'] = True
                break
        
        # Check database configuration
        if self.secrets.get_secret('DATABASE_URL'):
            status['database_configured'] = True
        
        # Check authentication
        if self.secrets.get_secret('JWT_SECRET_KEY'):
            status['auth_configured'] = True
        
        # Check admin access
        admin_email = self.secrets.get_secret('ADMIN_EMAIL')
        admin_password = self.secrets.get_secret('ADMIN_PASSWORD')
        if admin_email or admin_password:
            status['admin_configured'] = True
        
        logger.info(f"Configuration status: {sum(status.values())}/{len(status)} modules configured")
        return status
    
    @property
    def email_provider(self) -> Optional[str]:
        """Determine which email provider is configured"""
        if self.secrets.get_secret('SENDGRID_API_KEY'):
            return 'sendgrid'
        elif self.secrets.get_secret('MAILGUN_API_KEY'):
            return 'mailgun'
        elif self.secrets.get_secret('TUTANOTA_USERNAME'):
            return 'tutanota'
        else:
            return None
    
    @property
    def email_api_key(self) -> Optional[str]:
        """Get email API key with provider fallback"""
        provider = self.email_provider
        
        if provider == 'sendgrid':
            return self.secrets.get_secret('SENDGRID_API_KEY')
        elif provider == 'mailgun':
            return self.secrets.get_secret('MAILGUN_API_KEY')
        elif provider == 'tutanota':
            return self.secrets.get_secret('TUTANOTA_PASSWORD')
        else:
            return None
    
    @property 
    def email_config(self) -> Dict[str, Any]:
        """Get complete email configuration"""
        provider = self.email_provider
        
        if provider == 'sendgrid':
            return {
                'provider': 'sendgrid',
                'api_key': self.secrets.get_secret('SENDGRID_API_KEY'),
                'from_email': self.secrets.get_secret('ADMIN_EMAIL') or 'noreply@ici-chat.com'
            }
        elif provider == 'mailgun':
            return {
                'provider': 'mailgun',
                'api_key': self.secrets.get_secret('MAILGUN_API_KEY'),
                'domain': self.secrets.get_secret('MAILGUN_DOMAIN'),
                'from_email': self.secrets.get_secret('ADMIN_EMAIL') or 'noreply@ici-chat.com'
            }
        elif provider == 'tutanota':
            return {
                'provider': 'tutanota',
                'username': self.secrets.get_secret('TUTANOTA_USERNAME'),
                'password': self.secrets.get_secret('TUTANOTA_PASSWORD'),
                'from_email': self.secrets.get_secret('TUTANOTA_USERNAME')
            }
        else:
            return {'provider': None}
    
    @property
    def admin_email(self) -> Optional[str]:
        """Get admin email address"""
        return self.secrets.get_secret('ADMIN_EMAIL')
    
    @property
    def jwt_secret(self) -> Optional[str]:
        """Get JWT secret key"""
        return self.secrets.get_secret('JWT_SECRET_KEY')
    
    @property
    def database_url(self) -> Optional[str]:
        """Get database connection URL"""
        return self.secrets.get_secret('DATABASE_URL')
    
    def is_email_enabled(self) -> bool:
        """Check if email functionality should be enabled"""
        return self.config_status['email_configured']
    
    def get_configuration_report(self) -> Dict[str, Any]:
        """
        Generate configuration report for admin dashboard
        Shows what's configured without exposing secrets
        """
        secrets_health = self.secrets.check_configuration_health()
        
        return {
            'environment': self.environment,
            'secrets_source': 'Secret Manager' if self.secrets.project_id else 'Environment Variables',
            'configuration_status': self.config_status,
            'email_provider': self.email_provider,
            'secrets_health': secrets_health,
            'available_secrets': len(self.secrets.list_available_secrets()),
            'email_enabled': self.is_email_enabled(),
            'last_check': datetime.now().isoformat(),
            'google_cloud_project': self.secrets.project_id,
            'total_configured': sum(self.config_status.values())
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """
        Validate current configuration and return recommendations
        """
        validation = {
            'valid': True,
            'warnings': [],
            'errors': [],
            'recommendations': []
        }
        
        # Check critical configurations
        if not self.config_status['email_configured']:
            validation['warnings'].append("No email provider configured - email notifications disabled")
            validation['recommendations'].append("Configure at least one email provider (SendGrid, Mailgun, or Tutanota)")
        
        if not self.config_status['auth_configured']:
            validation['warnings'].append("JWT secret not configured - authentication may be insecure")
            validation['recommendations'].append("Generate and configure JWT_SECRET_KEY")
        
        if self.environment == 'production':
            if not self.secrets.client:
                validation['warnings'].append("Production environment without Secret Manager")
                validation['recommendations'].append("Configure Google Secret Manager for production")
            
            if not self.config_status['admin_configured']:
                validation['warnings'].append("Admin access not properly configured")
                validation['recommendations'].append("Configure ADMIN_EMAIL and ADMIN_PASSWORD")
        
        # Set validation status
        validation['valid'] = len(validation['errors']) == 0
        
        return validation

# Global configuration instance
config = Config()
