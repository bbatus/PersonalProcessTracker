"""
Property-based tests for email service

Feature: personal-process-tracker
Properties tested:
- Property 84: Email verification token generation
- Property 86: Password reset token generation
"""

import pytest
from hypothesis import given, strategies as st, settings
from app.utils.token import generate_verification_token, generate_password_reset_token
from datetime import datetime, timedelta


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=1000))
def test_property_84_email_verification_token_generation(iterations):
    """
    Property 84: Email verification token generation
    
    For any number of token generations, each token should be:
    - Non-empty string
    - URL-safe (no special characters that need encoding)
    - Unique (no collisions in reasonable sample size)
    
    Validates: Requirements 21.1, 21.4
    """
    tokens = set()
    
    for _ in range(min(iterations, 100)):
        token = generate_verification_token()
        
        # Token should be non-empty
        assert token, "Token should not be empty"
        
        # Token should be a string
        assert isinstance(token, str), "Token should be a string"
        
        # Token should be URL-safe (alphanumeric, dash, underscore)
        assert all(c.isalnum() or c in '-_' for c in token), \
            "Token should be URL-safe"
        
        # Token should have reasonable length (32 bytes = ~43 chars in base64)
        assert len(token) >= 40, "Token should be at least 40 characters"
        
        # Collect tokens to check uniqueness
        tokens.add(token)
    
    # All tokens should be unique (no collisions)
    assert len(tokens) == min(iterations, 100), \
        "All generated tokens should be unique"


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=100))
def test_property_86_password_reset_token_generation(iterations):
    """
    Property 86: Password reset token generation
    
    For any number of token generations, each token should:
    - Be a tuple of (token, expiration)
    - Token should be non-empty and URL-safe
    - Expiration should be ~1 hour in the future
    - All tokens should be unique
    
    Validates: Requirements 21.1, 21.4
    """
    tokens = set()
    now = datetime.utcnow()
    
    for _ in range(min(iterations, 100)):
        result = generate_password_reset_token()
        
        # Should return a tuple
        assert isinstance(result, tuple), "Should return a tuple"
        assert len(result) == 2, "Tuple should have 2 elements"
        
        token, expiration = result
        
        # Token should be non-empty string
        assert token, "Token should not be empty"
        assert isinstance(token, str), "Token should be a string"
        
        # Token should be URL-safe
        assert all(c.isalnum() or c in '-_' for c in token), \
            "Token should be URL-safe"
        
        # Token should have reasonable length
        assert len(token) >= 40, "Token should be at least 40 characters"
        
        # Expiration should be a datetime
        assert isinstance(expiration, datetime), \
            "Expiration should be a datetime"
        
        # Expiration should be approximately 1 hour in the future
        time_diff = (expiration - now).total_seconds()
        assert 3500 <= time_diff <= 3700, \
            f"Expiration should be ~1 hour (3600s) in future, got {time_diff}s"
        
        # Collect tokens to check uniqueness
        tokens.add(token)
    
    # All tokens should be unique
    assert len(tokens) == min(iterations, 100), \
        "All generated tokens should be unique"


@settings(max_examples=100)
@given(
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',))),
    st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',)))
)
def test_email_template_rendering_with_various_inputs(username, token):
    """
    Property test: Email templates should render without errors for any valid input
    
    For any username and token strings, template rendering should:
    - Not raise exceptions
    - Produce non-empty output
    - Include the input values in the output
    """
    from app.services.email_service import EmailService
    
    service = EmailService()
    
    # Test verification email template
    try:
        html_template = service._load_template("email_verification.html")
        text_template = service._load_template("email_verification.txt")
        
        context = {
            "username": username,
            "verification_url": f"http://test.com/verify?token={token}"
        }
        
        html_content = service._render_template(html_template, context)
        text_content = service._render_template(text_template, context)
        
        # Should produce non-empty output
        assert html_content, "HTML content should not be empty"
        assert text_content, "Text content should not be empty"
        
        # Should include username in output
        assert username in html_content or username in text_content, \
            "Username should appear in rendered content"
        
    except Exception as e:
        # Template rendering should not fail for valid inputs
        pytest.fail(f"Template rendering failed: {str(e)}")
