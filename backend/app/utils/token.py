import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from uuid import UUID

from app.core.config import settings


def generate_token(user_id: UUID) -> str:
    """
    Generate JWT access token for user
    
    Args:
        user_id: User's UUID
        
    Returns:
        JWT token string
    """
    expiration = datetime.utcnow() + timedelta(days=settings.JWT_EXPIRATION_DAYS)
    
    payload = {
        "sub": str(user_id),
        "exp": expiration,
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return token


def verify_token(token: str) -> Optional[UUID]:
    """
    Verify JWT token and extract user_id
    
    Args:
        token: JWT token string
        
    Returns:
        User UUID if valid, None if invalid or expired
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        user_id_str = payload.get("sub")
        if user_id_str is None:
            return None
        
        return UUID(user_id_str)
        
    except JWTError:
        return None
    except ValueError:  # Invalid UUID
        return None


def generate_verification_token() -> str:
    """
    Generate random token for email verification
    
    Returns:
        Random URL-safe token string (32 bytes = 43 characters base64)
    """
    return secrets.token_urlsafe(32)


def generate_password_reset_token() -> tuple[str, datetime]:
    """
    Generate random token for password reset with 1-hour expiration
    
    Returns:
        Tuple of (token, expiration_datetime)
    """
    token = secrets.token_urlsafe(32)
    expiration = datetime.utcnow() + timedelta(hours=1)
    
    return token, expiration


def is_token_expired(expiration: datetime) -> bool:
    """
    Check if a token expiration datetime has passed
    
    Args:
        expiration: Token expiration datetime
        
    Returns:
        True if expired, False otherwise
    """
    return datetime.utcnow() > expiration
