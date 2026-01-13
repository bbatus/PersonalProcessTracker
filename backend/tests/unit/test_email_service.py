"""
Unit tests for email service

Tests:
- Email template rendering
- SMTP connection handling
- Retry logic
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from app.services.email_service import EmailService


class TestEmailService:
    """Unit tests for EmailService"""
    
    def test_load_template_success(self):
        """Test loading email template successfully"""
        service = EmailService()
        
        # Should load existing template
        template = service._load_template("email_verification.html")
        assert template
        assert "{{username}}" in template
        assert "{{verification_url}}" in template
    
    def test_load_template_not_found(self):
        """Test loading non-existent template raises error"""
        service = EmailService()
        
        with pytest.raises(FileNotFoundError):
            service._load_template("nonexistent_template.html")
    
    def test_render_template(self):
        """Test template rendering with context"""
        service = EmailService()
        
        template = "Hello {{name}}, your code is {{code}}"
        context = {"name": "John", "code": "12345"}
        
        result = service._render_template(template, context)
        
        assert result == "Hello John, your code is 12345"
    
    def test_render_template_missing_variable(self):
        """Test template rendering with missing variable"""
        service = EmailService()
        
        template = "Hello {{name}}, your code is {{code}}"
        context = {"name": "John"}  # Missing 'code'
        
        result = service._render_template(template, context)
        
        # Jinja2 renders missing variables as empty string
        assert "Hello John" in result
    
    @patch('smtplib.SMTP')
    def test_send_email_success(self, mock_smtp):
        """Test successful email sending"""
        service = EmailService()
        
        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text"
        )
        
        assert result is True
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once()
        mock_server.send_message.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_retry_logic(self, mock_smtp):
        """Test email retry logic on failure"""
        service = EmailService()
        service.max_retries = 3
        service.retry_delay = 0.1  # Speed up test
        
        # Mock SMTP to fail twice, then succeed
        mock_server = MagicMock()
        mock_server.send_message.side_effect = [
            Exception("Connection failed"),
            Exception("Connection failed"),
            None  # Success on third try
        ]
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text"
        )
        
        assert result is True
        assert mock_server.send_message.call_count == 3
    
    @patch('smtplib.SMTP')
    def test_send_email_all_retries_fail(self, mock_smtp):
        """Test email sending fails after all retries"""
        service = EmailService()
        service.max_retries = 3
        service.retry_delay = 0.1
        
        # Mock SMTP to always fail
        mock_server = MagicMock()
        mock_server.send_message.side_effect = Exception("Connection failed")
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service._send_email(
            to_email="test@example.com",
            subject="Test Subject",
            html_content="<p>Test HTML</p>",
            text_content="Test Text"
        )
        
        assert result is False
        assert mock_server.send_message.call_count == 3
    
    @patch('smtplib.SMTP')
    def test_send_verification_email(self, mock_smtp):
        """Test sending verification email"""
        service = EmailService()
        
        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service.send_verification_email(
            to_email="test@example.com",
            username="testuser",
            verification_token="test-token-123"
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Check that message was created with correct subject
        call_args = mock_server.send_message.call_args
        message = call_args[0][0]
        assert message['Subject'] == "Verify Your Email - Personal Process Tracker"
        assert message['To'] == "test@example.com"
    
    @patch('smtplib.SMTP')
    def test_send_password_reset_email(self, mock_smtp):
        """Test sending password reset email"""
        service = EmailService()
        
        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service.send_password_reset_email(
            to_email="test@example.com",
            username="testuser",
            reset_token="reset-token-456"
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Check subject
        call_args = mock_server.send_message.call_args
        message = call_args[0][0]
        assert "Reset Your Password" in message['Subject']
    
    @patch('smtplib.SMTP')
    def test_send_welcome_email(self, mock_smtp):
        """Test sending welcome email"""
        service = EmailService()
        
        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service.send_welcome_email(
            to_email="test@example.com",
            username="testuser"
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Check subject
        call_args = mock_server.send_message.call_args
        message = call_args[0][0]
        assert "Welcome" in message['Subject']
    
    @patch('smtplib.SMTP')
    def test_send_security_notification(self, mock_smtp):
        """Test sending security notification email"""
        service = EmailService()
        
        # Mock SMTP
        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server
        
        result = service.send_security_notification(
            to_email="test@example.com",
            username="testuser",
            event_type="Password Changed",
            timestamp="2024-01-10 12:00:00 UTC",
            details="Your password was changed"
        )
        
        assert result is True
        mock_server.send_message.assert_called_once()
        
        # Check subject
        call_args = mock_server.send_message.call_args
        message = call_args[0][0]
        assert "Security" in message['Subject']
