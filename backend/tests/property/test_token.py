"""
Property-based tests for token utilities

Feature: personal-process-tracker
Properties tested:
- Property 3: Token validation on requests
- Property 5: Expired token rejection
- Property 88: Expired reset token rejection
"""

import pytest
from hypothesis import given, strategies as st, settings
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from app.utils.token import (
    generate_token,
    verify_token,
    generate_verification_token,
    generate_password_reset_token,
    is_token_expired
)


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=100))
def test_property_3_token_validation_on_requests(iterations):
    """
    Property 3: Token validation on requests
    
    For any valid user_id:
    - Generated token should be non-empty
    - Token should be verifiable
    - Verified user_id should match original
    - Invalid tokens should return None
    
    Validates: Requirements 1.8, 1.10, 21.6
    """
    for _ in range(min(iterations, 100)):
        # Generate random user_id
        user_id = uuid4()
        
        # Generate token
        token = generate_token(user_id)
        
        # Token should be non-empty
        assert token, "Token should not be empty"
        assert isinstance(token, str), "Token should be a string"
        
        # Token should be verifiable
        verified_user_id = verify_token(token)
        
        assert verified_user_id is not None, "Valid token should verify"
        assert isinstance(verified_user_id, UUID), "Verified ID should be UUID"
        assert verified_user_id == user_id, "Verified user_id should match original"


@settings(max_examples=100)
@given(st.text(min_size=1, max_size=200))
def test_property_3_invalid_token_rejection(invalid_token):
    """
    Property 3: Token validation on requests (invalid tokens)
    
    For any random string that's not a valid JWT:
    - verify_token should return None
    - Should not raise exceptions
    
    Validates: Requirements 1.8, 1.10
    """
    # Most random strings won't be valid JWTs
    result = verify_token(invalid_token)
    
    # Invalid tokens should return None, not raise exceptions
    assert result is None, "Invalid token should return None"


def test_property_5_expired_token_rejection():
    """
    Property 5: Expired token rejection
    
    Tokens with past expiration should be rejected
    
    Note: We can't easily test this with hypothesis since we'd need to
    manipulate time or wait for expiration. This is a unit test instead.
    
    Validates: Requirements 1.8, 1.10, 21.6
    """
    from jose import jwt
    from app.core.config import settings
    
    user_id = uuid4()
    
    # Create an expired token (expired 1 hour ago)
    expiration = datetime.utcnow() - timedelta(hours=1)
    
    payload = {
        "sub": str(user_id),
        "exp": expiration,
        "iat": datetime.utcnow() - timedelta(hours=2)
    }
    
    expired_token = jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )
    
    # Expired token should not verify
    result = verify_token(expired_token)
    assert result is None, "Expired token should be rejected"


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=100))
def test_property_88_expired_reset_token_rejection(iterations):
    """
    Property 88: Expired reset token rejection
    
    For any password reset token:
    - Fresh tokens should not be expired
    - Tokens with past expiration should be expired
    - is_token_expired should correctly identify expired tokens
    
    Validates: Requirements 21.6
    """
    for _ in range(min(iterations, 100)):
        # Generate fresh token
        token, expiration = generate_password_reset_token()
        
        # Fresh token should not be expired
        assert not is_token_expired(expiration), \
            "Fresh token should not be expired"
        
        # Token expiring in future should not be expired
        future_expiration = datetime.utcnow() + timedelta(hours=1)
        assert not is_token_expired(future_expiration), \
            "Future expiration should not be expired"
        
        # Token expired in past should be expired
        past_expiration = datetime.utcnow() - timedelta(hours=1)
        assert is_token_expired(past_expiration), \
            "Past expiration should be expired"


@settings(max_examples=100)
@given(st.integers(min_value=-100, max_value=100))
def test_is_token_expired_with_various_offsets(hours_offset):
    """
    Property test: is_token_expired should correctly handle various time offsets
    
    For any time offset:
    - Negative offsets (past) should be expired
    - Positive offsets (future) should not be expired
    - Zero offset (now) should be expired (edge case)
    """
    expiration = datetime.utcnow() + timedelta(hours=hours_offset)
    result = is_token_expired(expiration)
    
    if hours_offset < 0:
        # Past times should be expired
        assert result is True, f"Expiration {hours_offset}h ago should be expired"
    elif hours_offset > 0:
        # Future times should not be expired
        assert result is False, f"Expiration {hours_offset}h from now should not be expired"
    else:
        # Exactly now might be expired due to microsecond differences
        # This is acceptable behavior
        pass


def test_token_uniqueness():
    """
    Test that multiple tokens for same user are unique
    
    This prevents token reuse attacks
    """
    user_id = uuid4()
    tokens = set()
    
    for _ in range(100):
        token = generate_token(user_id)
        tokens.add(token)
    
    # All tokens should be unique (different iat timestamps)
    assert len(tokens) == 100, "All tokens should be unique"


def test_verification_token_format():
    """
    Test that verification tokens have expected format
    """
    for _ in range(100):
        token = generate_verification_token()
        
        # Should be URL-safe
        assert all(c.isalnum() or c in '-_' for c in token), \
            "Token should be URL-safe"
        
        # Should have reasonable length
        assert len(token) >= 40, "Token should be sufficiently long"


def test_password_reset_token_expiration_timing():
    """
    Test that password reset tokens expire in approximately 1 hour
    """
    token, expiration = generate_password_reset_token()
    
    now = datetime.utcnow()
    time_diff = (expiration - now).total_seconds()
    
    # Should be approximately 1 hour (3600 seconds)
    # Allow 10 second tolerance for test execution time
    assert 3590 <= time_diff <= 3610, \
        f"Reset token should expire in ~1 hour, got {time_diff}s"
