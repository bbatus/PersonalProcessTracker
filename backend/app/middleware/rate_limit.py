"""
Rate limiting middleware
"""

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, Tuple
import asyncio

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware
    
    For production, use Redis-based rate limiting for distributed systems
    """
    
    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.RATE_LIMIT_PER_MINUTE
        # Store: {ip_address: [(timestamp, count)]}
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.cleanup_interval = 60  # Clean up old entries every 60 seconds
        self.last_cleanup = datetime.utcnow()
    
    def _cleanup_old_entries(self):
        """Remove entries older than 1 minute"""
        now = datetime.utcnow()
        
        # Only cleanup if enough time has passed
        if (now - self.last_cleanup).total_seconds() < self.cleanup_interval:
            return
        
        cutoff = now - timedelta(minutes=1)
        
        # Clean up old entries
        for ip in list(self.request_counts.keys()):
            self.request_counts[ip] = [
                (ts, count) for ts, count in self.request_counts[ip]
                if ts > cutoff
            ]
            
            # Remove empty entries
            if not self.request_counts[ip]:
                del self.request_counts[ip]
        
        self.last_cleanup = now
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded IP (behind proxy)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _check_rate_limit(self, ip: str) -> Tuple[bool, int, int]:
        """
        Check if IP has exceeded rate limit
        
        Returns:
            Tuple of (is_allowed, remaining, reset_time_seconds)
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(minutes=1)
        
        # Get requests in last minute
        recent_requests = [
            (ts, count) for ts, count in self.request_counts[ip]
            if ts > cutoff
        ]
        
        # Calculate total requests
        total_requests = sum(count for _, count in recent_requests)
        
        # Check if limit exceeded
        is_allowed = total_requests < self.requests_per_minute
        remaining = max(0, self.requests_per_minute - total_requests - 1)
        
        # Calculate reset time (time until oldest request expires)
        if recent_requests:
            oldest_ts = min(ts for ts, _ in recent_requests)
            reset_seconds = int((oldest_ts + timedelta(minutes=1) - now).total_seconds())
        else:
            reset_seconds = 60
        
        return is_allowed, remaining, max(0, reset_seconds)
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/ready"]:
            return await call_next(request)
        
        # Cleanup old entries periodically
        self._cleanup_old_entries()
        
        # Get client IP
        ip = self._get_client_ip(request)
        
        # Check rate limit
        is_allowed, remaining, reset_seconds = self._check_rate_limit(ip)
        
        if not is_allowed:
            # Rate limit exceeded
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=f"Rate limit exceeded. Try again in {reset_seconds} seconds.",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(reset_seconds),
                    "Retry-After": str(reset_seconds)
                }
            )
        
        # Record this request
        now = datetime.utcnow()
        self.request_counts[ip].append((now, 1))
        
        # Process request
        response: Response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(reset_seconds)
        
        return response
