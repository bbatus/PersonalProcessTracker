"""
CSRF protection middleware

Note: For JWT-based APIs, CSRF is less of a concern if tokens are stored
in httpOnly cookies and proper CORS is configured. This is a defense-in-depth measure.
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import secrets
from typing import Set


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection middleware for state-changing operations
    
    For JWT-based APIs with Bearer tokens, CSRF is less critical,
    but this provides additional protection for cookie-based sessions.
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Methods that require CSRF protection
        self.protected_methods: Set[str] = {"POST", "PUT", "PATCH", "DELETE"}
        # Paths that don't require CSRF (e.g., login, public endpoints)
        self.exempt_paths: Set[str] = {
            "/api/auth/login",
            "/api/auth/register",
            "/api/auth/verify",
            "/api/auth/request-reset",
            "/api/auth/reset-password",
            "/api/auth/google/login",
            "/api/auth/google/callback",
            "/health",
            "/ready",
            "/docs",
            "/redoc",
            "/openapi.json"
        }
    
    def _is_exempt(self, path: str) -> bool:
        """Check if path is exempt from CSRF protection"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    async def dispatch(self, request: Request, call_next):
        # Skip CSRF for safe methods (GET, HEAD, OPTIONS)
        if request.method not in self.protected_methods:
            return await call_next(request)
        
        # Skip CSRF for exempt paths
        if self._is_exempt(request.url.path):
            return await call_next(request)
        
        # For JWT Bearer token auth, CSRF is not needed
        # (tokens are not automatically sent by browser)
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return await call_next(request)
        
        # If using cookie-based auth, validate CSRF token
        csrf_token_header = request.headers.get("X-CSRF-Token")
        csrf_token_cookie = request.cookies.get("csrf_token")
        
        if not csrf_token_header or not csrf_token_cookie:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )
        
        if csrf_token_header != csrf_token_cookie:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token invalid"
            )
        
        return await call_next(request)


def generate_csrf_token() -> str:
    """Generate a new CSRF token"""
    return secrets.token_urlsafe(32)
