from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.database import get_db
from app.services.auth_service import get_auth_service
from app.utils.oauth import google_oauth
from app.models.user import User
from app.utils.token import generate_token
from app.api.dependencies import get_current_user, get_current_verified_user
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models

class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    timezone: str = "UTC"


class LoginRequest(BaseModel):
    username_or_email: str
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class ProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    timezone: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    username: str
    email: str
    email_verified: bool
    timezone: str
    avatar_url: Optional[str] = None
    created_at: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class MessageResponse(BaseModel):
    message: str


# OAuth Endpoints

@router.get("/google/login")
async def google_login():
    """Initiate Google OAuth login flow"""
    try:
        from app.core.config import settings
        from urllib.parse import urlencode
        
        # Build authorization URL
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline"
        }
        
        auth_url = f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"
        return RedirectResponse(url=auth_url)
        
    except Exception as e:
        logger.error(f"Google OAuth login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to initiate Google login"
        )


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: Session = Depends(get_db)
):
    """Handle Google OAuth callback"""
    try:
        # For now, we'll use a simpler approach without async
        # In production, consider using httpx for async requests
        import requests
        from app.core.config import settings
        
        # Exchange code for token
        token_url = "https://oauth2.googleapis.com/token"
        token_data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()
        token_json = token_response.json()
        
        # Get user info from Google
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {token_json['access_token']}"}
        userinfo_response = requests.get(userinfo_url, headers=headers)
        userinfo_response.raise_for_status()
        user_info = userinfo_response.json()
        
        # Check if user exists
        user = db.query(User).filter(
            User.oauth_provider == "google",
            User.oauth_id == user_info["id"]
        ).first()
        
        if not user:
            # Check if email already exists
            existing_user = db.query(User).filter(User.email == user_info["email"]).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered with password. Please login with password."
                )
            
            # Create new user
            user = User(
                username=user_info["email"].split("@")[0],  # Use email prefix as username
                email=user_info["email"],
                oauth_provider="google",
                oauth_id=user_info["id"],
                avatar_url=user_info.get("picture"),
                email_verified=True,  # Google emails are pre-verified
                password_hash=None  # OAuth users don't have passwords
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            logger.info(f"New user created via Google OAuth: {user.email}")
        
        # Generate JWT token
        access_token = generate_token(user.id)
        
        # Redirect to frontend with token
        frontend_url = "http://localhost:3000"
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Google OAuth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to complete Google login"
        )


# Traditional Auth Endpoints

@router.post("/register", response_model=MessageResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user with email/password"""
    logger.info(f"Registration attempt for username: {request.username}, email: {request.email}")
    
    auth_service = get_auth_service(db)
    
    user, error = auth_service.register(
        username=request.username,
        email=request.email,
        password=request.password,
        timezone=request.timezone
    )
    
    if error:
        logger.error(f"Registration failed: {error}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    logger.info(f"Registration successful for user: {request.username}")
    return MessageResponse(
        message="Registration successful. Please check your email to verify your account."
    )


@router.get("/verify", response_model=MessageResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """Verify user email with token"""
    auth_service = get_auth_service(db)
    
    success, error = auth_service.verify_email(token)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return MessageResponse(message="Email verified successfully!")


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login with username/email and password"""
    auth_service = get_auth_service(db)
    
    token, user, error = auth_service.login(
        username_or_email=request.username_or_email,
        password=request.password
    )
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error
        )
    
    return TokenResponse(
        access_token=token,
        user={
            "id": str(user.id),
            "username": user.username,
            "email": user.email,
            "email_verified": user.email_verified,
            "avatar_url": user.avatar_url
        }
    )


@router.post("/request-reset", response_model=MessageResponse)
async def request_password_reset(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset email"""
    auth_service = get_auth_service(db)
    
    success, error = auth_service.request_password_reset(request.email)
    
    if not success and error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error
        )
    
    # Always return success to prevent email enumeration
    return MessageResponse(
        message="If the email exists, a password reset link has been sent."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    auth_service = get_auth_service(db)
    
    success, error = auth_service.reset_password(
        token=request.token,
        new_password=request.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return MessageResponse(message="Password reset successfully!")


@router.post("/logout", response_model=MessageResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """Logout current user (client should discard token)"""
    # In a stateless JWT system, logout is handled client-side by discarding the token
    # For additional security, you could implement a token blacklist
    logger.info(f"User logged out: {current_user.username}")
    return MessageResponse(message="Logged out successfully")


@router.post("/resend-verification", response_model=MessageResponse)
async def resend_verification(
    request: PasswordResetRequest,  # Reuse the same model (has email field)
    db: Session = Depends(get_db)
):
    """Resend email verification link"""
    auth_service = get_auth_service(db)
    
    # Find user by email
    user = db.query(User).filter(User.email == request.email).first()
    
    if not user:
        # Don't reveal if email exists
        return MessageResponse(
            message="If the email exists and is not verified, a verification link has been sent."
        )
    
    if user.email_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate new verification token and send email
    from app.utils.token import generate_verification_token
    from app.services.email_service import get_email_service
    
    verification_token = generate_verification_token()
    user.email_verification_token = verification_token
    db.commit()
    
    email_service = get_email_service()
    email_service.send_verification_email(user.email, user.username, verification_token)
    
    return MessageResponse(
        message="If the email exists and is not verified, a verification link has been sent."
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        email_verified=current_user.email_verified,
        timezone=current_user.timezone,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat()
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    # Update username if provided
    if request.username:
        # Check if username is already taken
        existing_user = db.query(User).filter(
            User.username == request.username,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        current_user.username = request.username
    
    # Update timezone if provided
    if request.timezone:
        current_user.timezone = request.timezone
    
    db.commit()
    db.refresh(current_user)
    
    logger.info(f"Profile updated for user: {current_user.username}")
    
    return UserResponse(
        id=str(current_user.id),
        username=current_user.username,
        email=current_user.email,
        email_verified=current_user.email_verified,
        timezone=current_user.timezone,
        avatar_url=current_user.avatar_url,
        created_at=current_user.created_at.isoformat()
    )


@router.put("/password", response_model=MessageResponse)
async def change_password(
    request: PasswordChangeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change user password (requires current password verification)"""
    from app.utils.password import verify_password, hash_password, validate_password_strength
    from app.services.email_service import get_email_service
    
    # OAuth users don't have passwords
    if current_user.oauth_provider:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth accounts"
        )
    
    # Verify current password
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Validate new password strength
    is_valid, error = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    # Update password
    current_user.password_hash = hash_password(request.new_password)
    db.commit()
    
    # Send security notification email
    from datetime import datetime
    email_service = get_email_service()
    email_service.send_security_notification(
        current_user.email,
        current_user.username,
        "Password Changed",
        datetime.utcnow().isoformat(),
        "Your password has been changed successfully. If you did not make this change, please contact support immediately."
    )
    
    logger.info(f"Password changed for user: {current_user.username}")
    
    return MessageResponse(message="Password changed successfully")

