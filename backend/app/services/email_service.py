import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Dict, Optional
from jinja2 import Template
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Service for sending emails with retry logic"""
    
    def __init__(self):
        self.smtp_host = settings.EMAIL_HOST
        self.smtp_port = settings.EMAIL_PORT
        self.username = settings.EMAIL_USERNAME
        self.password = settings.EMAIL_PASSWORD
        self.from_email = settings.EMAIL_FROM
        self.templates_dir = Path(__file__).parent.parent / "templates"
        self.max_retries = 3
        self.retry_delay = 2  # seconds
    
    def _load_template(self, template_name: str) -> str:
        """Load email template from file"""
        template_path = self.templates_dir / template_name
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_name}")
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _render_template(self, template_content: str, context: Dict[str, str]) -> str:
        """Render template with context variables"""
        template = Template(template_content)
        return template.render(**context)
    
    def _send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str
    ) -> bool:
        """Send email with retry logic"""
        
        for attempt in range(self.max_retries):
            try:
                # Create message
                msg = MIMEMultipart('alternative')
                msg['Subject'] = subject
                msg['From'] = self.from_email
                msg['To'] = to_email
                
                # Attach both plain text and HTML versions
                part1 = MIMEText(text_content, 'plain')
                part2 = MIMEText(html_content, 'html')
                msg.attach(part1)
                msg.attach(part2)
                
                # Send email
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.username, self.password)
                    server.send_message(msg)
                
                logger.info(f"Email sent successfully to {to_email}: {subject}")
                return True
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1}/{self.max_retries} failed to send email to {to_email}: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Failed to send email to {to_email} after {self.max_retries} attempts")
                    return False
        
        return False
    
    def send_verification_email(
        self,
        to_email: str,
        username: str,
        verification_token: str,
        base_url: str = "http://localhost:3000"
    ) -> bool:
        """Send email verification email"""
        
        verification_url = f"{base_url}/auth/verify?token={verification_token}"
        
        context = {
            "username": username,
            "verification_url": verification_url
        }
        
        # Load and render templates
        html_template = self._load_template("email_verification.html")
        text_template = self._load_template("email_verification.txt")
        
        html_content = self._render_template(html_template, context)
        text_content = self._render_template(text_template, context)
        
        return self._send_email(
            to_email=to_email,
            subject="Verify Your Email - Personal Process Tracker",
            html_content=html_content,
            text_content=text_content
        )
    
    def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_token: str,
        base_url: str = "http://localhost:3000"
    ) -> bool:
        """Send password reset email"""
        
        reset_url = f"{base_url}/auth/reset-password?token={reset_token}"
        
        context = {
            "username": username,
            "reset_url": reset_url
        }
        
        # Load and render templates
        html_template = self._load_template("password_reset.html")
        text_template = self._load_template("password_reset.txt")
        
        html_content = self._render_template(html_template, context)
        text_content = self._render_template(text_template, context)
        
        return self._send_email(
            to_email=to_email,
            subject="Reset Your Password - Personal Process Tracker",
            html_content=html_content,
            text_content=text_content
        )
    
    def send_welcome_email(
        self,
        to_email: str,
        username: str,
        app_url: str = "http://localhost:3000"
    ) -> bool:
        """Send welcome email after successful verification"""
        
        context = {
            "username": username,
            "app_url": app_url
        }
        
        # Load and render templates
        html_template = self._load_template("welcome.html")
        text_template = self._load_template("welcome.txt")
        
        html_content = self._render_template(html_template, context)
        text_content = self._render_template(text_template, context)
        
        return self._send_email(
            to_email=to_email,
            subject="Welcome to Personal Process Tracker! 🎉",
            html_content=html_content,
            text_content=text_content
        )
    
    def send_security_notification(
        self,
        to_email: str,
        username: str,
        event_type: str,
        timestamp: str,
        details: str,
        base_url: str = "http://localhost:3000"
    ) -> bool:
        """Send security notification email"""
        
        reset_password_url = f"{base_url}/auth/request-reset"
        
        context = {
            "username": username,
            "event_type": event_type,
            "timestamp": timestamp,
            "details": details,
            "reset_password_url": reset_password_url
        }
        
        # Load and render templates
        html_template = self._load_template("security_notification.html")
        text_template = self._load_template("security_notification.txt")
        
        html_content = self._render_template(html_template, context)
        text_content = self._render_template(text_template, context)
        
        return self._send_email(
            to_email=to_email,
            subject="🔒 Security Alert - Personal Process Tracker",
            html_content=html_content,
            text_content=text_content
        )


# Singleton instance
email_service = EmailService()


def get_email_service() -> EmailService:
    """Get email service instance"""
    return email_service
