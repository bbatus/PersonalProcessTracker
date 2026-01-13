from datetime import datetime, timedelta
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.user import User
from app.utils.password import hash_password, verify_password, validate_password_strength
from app.utils.token import (
    generate_token,
    generate_verification_token,
    generate_password_reset_token,
    is_token_expired
)
from app.services.email_service import email_service
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication and authorization operations"""
    
    # Account lockout settings
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    FAILED_ATTEMPTS_WINDOW_MINUTES = 15
    
    def __init__(self, db: Session):
        self.db = db
    
    # Account Lockout Methods
    
    def record_failed_login(self, user: User) -> None:
        """
        Record a failed login attempt and lock account if threshold exceeded
        
        Args:
            user: User model instance
        """
        user.failed_login_attempts += 1
        
        # Lock account if threshold exceeded
        if user.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
            self.lock_account(user)
        
        self.db.commit()
    
    def check_account_lockout(self, user: User) -> bool:
        """
        Check if account is currently locked
        
        Args:
            user: User model instance
            
        Returns:
            True if account is locked, False otherwise
        """
        if user.account_locked_until is None:
            return False
        
        # Check if lockout has expired
        if datetime.utcnow() > user.account_locked_until:
            self.unlock_account(user)
            return False
        
        return True
    
    def lock_account(self, user: User) -> None:
        """
        Lock user account for configured duration
        
        Args:
            user: User model instance
        """
        user.account_locked_until = datetime.utcnow() + timedelta(
            minutes=self.LOCKOUT_DURATION_MINUTES
        )
        logger.warning(f"Account locked for user {user.username} until {user.account_locked_until}")
        self.db.commit()
    
    def unlock_account(self, user: User) -> None:
        """
        Unlock user account and reset failed attempts
        
        Args:
            user: User model instance
        """
        user.account_locked_until = None
        user.failed_login_attempts = 0
        self.db.commit()
    
    def auto_unlock_expired_accounts(self) -> int:
        """
        Background task to unlock accounts with expired lockout periods
        
        Returns:
            Number of accounts unlocked
        """
        now = datetime.utcnow()
        locked_users = self.db.query(User).filter(
            User.account_locked_until.isnot(None),
            User.account_locked_until <= now
        ).all()
        
        count = 0
        for user in locked_users:
            self.unlock_account(user)
            count += 1
        
        if count > 0:
            logger.info(f"Auto-unlocked {count} expired accounts")
        
        return count
    
    # Authentication Methods
    
    def register(
        self,
        username: str,
        email: str,
        password: str,
        timezone: str = "UTC"
    ) -> Tuple[Optional[User], Optional[str]]:
        """
        Register a new user with email verification
        
        Args:
            username: Unique username
            email: Unique email address
            password: Plain text password
            timezone: User's timezone (default: UTC)
            
        Returns:
            Tuple of (User, error_message). User is None if registration failed.
        """
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            return None, error_msg
        
        # Check username uniqueness
        existing_user = self.db.query(User).filter(
            or_(User.username == username, User.email == email)
        ).first()
        
        if existing_user:
            if existing_user.username == username:
                return None, "Username already exists"
            if existing_user.email == email:
                return None, "Email already exists"
        
        # Create user
        verification_token = generate_verification_token()
        
        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            timezone=timezone,
            email_verification_token=verification_token,
            email_verified=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        # Send verification email
        try:
            email_service.send_verification_email(
                to_email=email,
                username=username,
                verification_token=verification_token
            )
        except Exception as e:
            logger.error(f"Failed to send verification email to {email}: {str(e)}")
            # Don't fail registration if email fails
        
        logger.info(f"User registered: {username} ({email})")
        return user, None
    
    def verify_email(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Verify user email with token
        
        Args:
            token: Email verification token
            
        Returns:
            Tuple of (success, error_message)
        """
        user = self.db.query(User).filter(
            User.email_verification_token == token
        ).first()
        
        if not user:
            return False, "Invalid verification token"
        
        if user.email_verified:
            return False, "Email already verified"
        
        # Verify email
        user.email_verified = True
        user.email_verification_token = None
        self.db.commit()
        
        # Send welcome email
        try:
            email_service.send_welcome_email(
                to_email=user.email,
                username=user.username
            )
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        
        logger.info(f"Email verified for user: {user.username}")
        return True, None
    
    def login(
        self,
        username_or_email: str,
        password: str
    ) -> Tuple[Optional[str], Optional[User], Optional[str]]:
        """
        Authenticate user and generate access token
        
        Args:
            username_or_email: Username or email
            password: Plain text password
            
        Returns:
            Tuple of (token, user, error_message). Token and user are None if login failed.
        """
        # Find user by username or email
        user = self.db.query(User).filter(
            or_(User.username == username_or_email, User.email == username_or_email)
        ).first()
        
        if not user:
            return None, None, "Invalid credentials"
        
        # Check account lockout
        if self.check_account_lockout(user):
            lockout_until = user.account_locked_until.strftime("%Y-%m-%d %H:%M:%S UTC")
            return None, None, f"Account is locked until {lockout_until}"
        
        # Verify password
        if not verify_password(password, user.password_hash):
            self.record_failed_login(user)
            return None, None, "Invalid credentials"
        
        # Reset failed attempts on successful login
        if user.failed_login_attempts > 0:
            user.failed_login_attempts = 0
            self.db.commit()
        
        # Update last login
        user.last_login_at = datetime.utcnow()
        self.db.commit()
        
        # Generate token
        token = generate_token(user.id)
        
        logger.info(f"User logged in: {user.username}")
        return token, user, None
    
    def logout(self, user_id: UUID) -> bool:
        """
        Logout user (token invalidation handled by client)
        
        Args:
            user_id: User's UUID
            
        Returns:
            True if successful
        """
        # In a stateless JWT system, logout is handled client-side by removing the token
        # For additional security, we could maintain a token blacklist in Redis
        logger.info(f"User logged out: {user_id}")
        return True
    
    def request_password_reset(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Request password reset and send email
        
        Args:
            email: User's email address
            
        Returns:
            Tuple of (success, error_message)
        """
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            # Don't reveal if email exists
            return True, None
        
        # Generate reset token
        reset_token, expiration = generate_password_reset_token()
        
        user.password_reset_token = reset_token
        user.password_reset_expires = expiration
        self.db.commit()
        
        # Send reset email
        try:
            email_service.send_password_reset_email(
                to_email=email,
                username=user.username,
                reset_token=reset_token
            )
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")
            return False, "Failed to send reset email"
        
        logger.info(f"Password reset requested for: {user.username}")
        return True, None
    
    def reset_password(
        self,
        token: str,
        new_password: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Reset password with token
        
        Args:
            token: Password reset token
            new_password: New plain text password
            
        Returns:
            Tuple of (success, error_message)
        """
        # Validate password strength
        is_valid, error_msg = validate_password_strength(new_password)
        if not is_valid:
            return False, error_msg
        
        # Find user with token
        user = self.db.query(User).filter(
            User.password_reset_token == token
        ).first()
        
        if not user:
            return False, "Invalid or expired reset token"
        
        # Check token expiration
        if user.password_reset_expires is None or is_token_expired(user.password_reset_expires):
            return False, "Invalid or expired reset token"
        
        # Reset password
        user.password_hash = hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        user.failed_login_attempts = 0  # Reset failed attempts
        user.account_locked_until = None  # Unlock account if locked
        self.db.commit()
        
        # Send security notification
        try:
            email_service.send_security_notification(
                to_email=user.email,
                username=user.username,
                event_type="Password Reset",
                timestamp=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                details="Your password was successfully reset"
            )
        except Exception as e:
            logger.error(f"Failed to send security notification to {user.email}: {str(e)}")
        
        logger.info(f"Password reset for user: {user.username}")
        return True, None


def get_auth_service(db: Session) -> AuthService:
    """Factory function to create AuthService instance"""
    return AuthService(db)
