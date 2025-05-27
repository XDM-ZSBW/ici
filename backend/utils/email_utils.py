# email_utils.py - Multi-provider email gateway for ICI Chat
"""
Email utilities with multi-provider support and transparent logging
Supports SendGrid, Mailgun, Tutanota, and simulated email for development
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

# Import requests with graceful fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.warning("requests library not available - email providers will use simulation mode")
    REQUESTS_AVAILABLE = False


class EmailProvider(ABC):
    """Abstract base class for email providers"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider_name = self.__class__.__name__.lower().replace('emailprovider', '')
        logger.info(f"Initialized {self.provider_name} email provider")
    
    @abstractmethod
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
        """Send email using provider's API"""
        pass
    
    def validate_config(self) -> bool:
        """Validate provider configuration"""
        return True
    
    def log_email_attempt(self, to_email: str, subject: str, success: bool, details: str = ""):
        """Log email sending attempt transparently"""
        status = "SUCCESS" if success else "FAILED"
        # Mask email for privacy in logs
        masked_email = f"{to_email[:2]}***@{to_email.split('@')[1]}" if '@' in to_email else "***"
        logger.info(f"Email {status} via {self.provider_name}: to={masked_email}, subject='{subject}' - {details}")


class SendGridEmailProvider(EmailProvider):
    """SendGrid email provider implementation"""
    
    def validate_config(self) -> bool:
        return bool(self.config.get('api_key'))
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
        if not REQUESTS_AVAILABLE:
            return self._simulate_send(to_email, subject, body)
        
        if not self.validate_config():
            return {"success": False, "error": "SendGrid API key not configured"}
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "personalizations": [{
                "to": [{"email": to_email}]
            }],
            "from": {"email": self.config.get('from_email', 'noreply@ici-chat.com')},
            "subject": subject,
            "content": [
                {"type": "text/plain", "value": body}
            ]
        }
        
        if html_body:
            data["content"].append({"type": "text/html", "value": html_body})
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30)
            success = response.status_code == 202
            
            result = {
                "success": success,
                "provider": "sendgrid",
                "status_code": response.status_code,
                "message_id": response.headers.get('X-Message-Id'),
                "timestamp": datetime.now().isoformat()
            }
            
            if not success:
                result["error"] = f"SendGrid API error: {response.status_code}"
                result["details"] = response.text[:200]
            
            self.log_email_attempt(to_email, subject, success, f"status_code={response.status_code}")
            return result
            
        except Exception as e:
            error_msg = f"SendGrid request failed: {str(e)}"
            self.log_email_attempt(to_email, subject, False, error_msg)
            return {"success": False, "error": error_msg, "provider": "sendgrid"}
    
    def _simulate_send(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        self.log_email_attempt(to_email, subject, True, "SIMULATED - requests not available")
        return {
            "success": True,
            "provider": "sendgrid",
            "simulated": True,
            "message_id": f"sim_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat()
        }


class MailgunEmailProvider(EmailProvider):
    """Mailgun email provider implementation"""
    
    def validate_config(self) -> bool:
        return bool(self.config.get('api_key')) and bool(self.config.get('domain'))
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
        if not REQUESTS_AVAILABLE:
            return self._simulate_send(to_email, subject, body)
        
        if not self.validate_config():
            return {"success": False, "error": "Mailgun API key or domain not configured"}
        
        domain = self.config['domain']
        url = f"https://api.mailgun.net/v3/{domain}/messages"
        
        data = {
            "from": self.config.get('from_email', f'ICI Chat <noreply@{domain}>'),
            "to": to_email,
            "subject": subject,
            "text": body
        }
        
        if html_body:
            data["html"] = html_body
        
        try:
            response = requests.post(
                url,
                auth=("api", self.config['api_key']),
                data=data,
                timeout=30
            )
            success = response.status_code == 200
            
            result = {
                "success": success,
                "provider": "mailgun",
                "status_code": response.status_code,
                "timestamp": datetime.now().isoformat()
            }
            
            if success:
                response_data = response.json()
                result["message_id"] = response_data.get("id")
                result["message"] = response_data.get("message")
            else:
                result["error"] = f"Mailgun API error: {response.status_code}"
                result["details"] = response.text[:200]
            
            self.log_email_attempt(to_email, subject, success, f"status_code={response.status_code}")
            return result
            
        except Exception as e:
            error_msg = f"Mailgun request failed: {str(e)}"
            self.log_email_attempt(to_email, subject, False, error_msg)
            return {"success": False, "error": error_msg, "provider": "mailgun"}
    
    def _simulate_send(self, to_email: str, subject: str, body: str) -> Dict[str, Any]:
        self.log_email_attempt(to_email, subject, True, "SIMULATED - requests not available")
        return {
            "success": True,
            "provider": "mailgun",
            "simulated": True,
            "message_id": f"sim_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat()
        }


class TutanotaEmailProvider(EmailProvider):
    """Tutanota email provider implementation (simplified)"""
    
    def validate_config(self) -> bool:
        return bool(self.config.get('username')) and bool(self.config.get('password'))
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
        # Note: Tutanota doesn't have a public API for sending emails
        # This would require SMTP or a custom implementation
        # For now, we'll simulate the send
        
        if not self.validate_config():
            return {"success": False, "error": "Tutanota credentials not configured"}
        
        self.log_email_attempt(to_email, subject, True, "SIMULATED - Tutanota integration pending")
        
        return {
            "success": True,
            "provider": "tutanota",
            "simulated": True,
            "message_id": f"tutanota_{datetime.now().timestamp()}",
            "timestamp": datetime.now().isoformat(),
            "note": "Tutanota integration requires SMTP setup"
        }


class SimulatedEmailProvider(EmailProvider):
    """Simulated email provider for development and testing"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.sent_emails: List[Dict[str, Any]] = []
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
        email_data = {
            "to": to_email,
            "subject": subject,
            "body": body,
            "html_body": html_body,
            "timestamp": datetime.now().isoformat(),
            "message_id": f"sim_{len(self.sent_emails) + 1}_{datetime.now().timestamp()}"
        }
        
        self.sent_emails.append(email_data)
        self.log_email_attempt(to_email, subject, True, "SIMULATED for development")
        
        return {
            "success": True,
            "provider": "simulated",
            "simulated": True,
            "message_id": email_data["message_id"],
            "timestamp": email_data["timestamp"]
        }
    
    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get all simulated sent emails for testing"""
        return self.sent_emails.copy()
    
    def clear_sent_emails(self):
        """Clear sent emails log"""
        self.sent_emails.clear()


class EmailService:
    """
    Main email service with multi-provider support
    Handles provider selection, fallbacks, and transparent logging
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = self._initialize_provider()
        
        logger.info(f"EmailService initialized with provider: {self.provider.provider_name}")
    
    def _initialize_provider(self) -> EmailProvider:
        """Initialize email provider based on configuration"""
        provider_name = self.config.get('provider')
        
        if provider_name == 'sendgrid':
            return SendGridEmailProvider(self.config)
        elif provider_name == 'mailgun':
            return MailgunEmailProvider(self.config)
        elif provider_name == 'tutanota':
            return TutanotaEmailProvider(self.config)
        else:
            logger.info("No email provider configured - using simulated provider")
            return SimulatedEmailProvider(self.config)
    
    def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
        """
        Send email using configured provider
        Returns standardized response with success status and details
        """
        try:
            # Validate inputs
            if not to_email or '@' not in to_email:
                return {"success": False, "error": "Invalid email address"}
            
            if not subject or not body:
                return {"success": False, "error": "Subject and body are required"}
            
            # Send email
            result = self.provider.send_email(to_email, subject, body, html_body)
            
            # Add service-level metadata
            result.update({
                "service": "EmailService",
                "provider_type": type(self.provider).__name__,
                "sent_at": datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            error_msg = f"EmailService error: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "error": error_msg}
    
    def send_notification(self, to_email: str, notification_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send predefined notification types with context
        """
        templates = {
            'welcome': {
                'subject': 'Welcome to ICI Chat',
                'body': 'Welcome to ICI Chat! Your account has been created successfully.\n\n'
                       'ICI Chat is designed to support cognitive accessibility with clear communication.\n\n'
                       'If you need assistance, please contact our support team.'
            },
            'password_reset': {
                'subject': 'Password Reset Request',
                'body': 'A password reset has been requested for your account.\n\n'
                       'If you did not request this, please ignore this email.\n\n'
                       'Reset token: {reset_token}'
            },
            'admin_alert': {
                'subject': 'ICI Chat Admin Alert',
                'body': 'Administrative alert for ICI Chat:\n\n{message}\n\n'
                       'Timestamp: {timestamp}'
            }
        }
        
        template = templates.get(notification_type)
        if not template:
            return {"success": False, "error": f"Unknown notification type: {notification_type}"}
        
        # Format template with context
        try:
            subject = template['subject'].format(**context)
            body = template['body'].format(**context)
            
            return self.send_email(to_email, subject, body)
            
        except KeyError as e:
            return {"success": False, "error": f"Missing context variable: {e}"}
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get current provider status and configuration"""
        return {
            "provider": self.provider.provider_name,
            "provider_class": type(self.provider).__name__,
            "config_valid": self.provider.validate_config(),
            "requests_available": REQUESTS_AVAILABLE,
            "timestamp": datetime.now().isoformat()
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on email service"""
        status = self.get_provider_status()
        
        # Test with simulated email if provider is configured
        if status['config_valid']:
            test_result = self.send_email(
                "test@example.com",
                "Health Check",
                "This is a health check test email"
            )
            status['health_check'] = {
                "test_send": test_result.get('success', False),
                "test_details": test_result.get('error', 'OK')
            }
        else:
            status['health_check'] = {
                "test_send": False,
                "test_details": "Provider not properly configured"
            }
        
        return status


# Global email service factory
def create_email_service(config: Optional[Dict[str, Any]] = None) -> EmailService:
    """
    Factory function to create EmailService with configuration
    Falls back to environment variables if no config provided
    """
    if config is None:
        # Try to import config from our config module
        try:
            from .config import config as app_config
            email_config = app_config.email_config
        except ImportError:
            # Fallback to environment variables
            email_config = {
                'provider': None,
                'from_email': os.getenv('ADMIN_EMAIL', 'noreply@ici-chat.com')
            }
            
            # Check for explicit EMAIL_PROVIDER setting first
            explicit_provider = os.getenv('EMAIL_PROVIDER')
            if explicit_provider:
                email_config['provider'] = explicit_provider.lower()
                
                # For simulated provider, we're done
                if explicit_provider.lower() == 'simulated':
                    pass  # No additional config needed
                # For other providers, still need their specific config
                elif explicit_provider.lower() == 'sendgrid' and os.getenv('SENDGRID_API_KEY'):
                    email_config['api_key'] = os.getenv('SENDGRID_API_KEY')
                elif explicit_provider.lower() == 'mailgun' and os.getenv('MAILGUN_API_KEY'):
                    email_config.update({
                        'api_key': os.getenv('MAILGUN_API_KEY'),
                        'domain': os.getenv('MAILGUN_DOMAIN')
                    })
                elif explicit_provider.lower() == 'tutanota' and os.getenv('TUTANOTA_USERNAME'):
                    email_config.update({
                        'username': os.getenv('TUTANOTA_USERNAME'),
                        'password': os.getenv('TUTANOTA_PASSWORD')
                    })
            else:
                # Auto-detect provider based on available API keys
                if os.getenv('SENDGRID_API_KEY'):
                    email_config.update({
                        'provider': 'sendgrid',
                        'api_key': os.getenv('SENDGRID_API_KEY')
                    })
                elif os.getenv('MAILGUN_API_KEY'):
                    email_config.update({
                        'provider': 'mailgun',
                        'api_key': os.getenv('MAILGUN_API_KEY'),
                        'domain': os.getenv('MAILGUN_DOMAIN')
                    })
                elif os.getenv('TUTANOTA_USERNAME'):
                    email_config.update({
                        'provider': 'tutanota',
                        'username': os.getenv('TUTANOTA_USERNAME'),
                        'password': os.getenv('TUTANOTA_PASSWORD')
                    })
    else:
        email_config = config
    
    return EmailService(email_config)


# Global email service instance
email_service = create_email_service()

# Convenience functions for backward compatibility
def send_email(to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> Dict[str, Any]:
    """Send email using global email service"""
    return email_service.send_email(to_email, subject, body, html_body)

def send_notification(to_email: str, notification_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """Send notification using global email service"""
    return email_service.send_notification(to_email, notification_type, context)
