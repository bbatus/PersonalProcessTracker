"""
Property-based tests for password utilities

Feature: personal-process-tracker
Properties tested:
- Property 6: Password hashing strength
- Property 89: Password strength validation
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from app.utils.password import hash_password, verify_password, validate_password_strength
import re


@settings(max_examples=100)
@given(st.text(min_size=1, max_size=100))
def test_property_6_password_hashing_strength(password):
    """
    Property 6: Password hashing strength
    
    For any password string:
    - Hash should be different from original password
    - Hash should be non-empty
    - Hash should start with bcrypt identifier ($2b$)
    - Verifying correct password should return True
    - Verifying wrong password should return False
    - Same password should produce different hashes (salt)
    
    Validates: Requirements 1.5, 22.1
    """
    # Hash the password
    hashed = hash_password(password)
    
    # Hash should be non-empty
    assert hashed, "Hash should not be empty"
    
    # Hash should be different from original (unless password is the hash itself, unlikely)
    assert hashed != password, "Hash should differ from original password"
    
    # Hash should start with bcrypt identifier
    assert hashed.startswith("$2b$") or hashed.startswith("$2a$"), \
        "Hash should use bcrypt format"
    
    # Should contain round information (e.g., $2b$12$)
    assert re.match(r'\$2[ab]\$\d{2}\$', hashed), \
        "Hash should contain bcrypt round information"
    
    # Verifying correct password should succeed
    assert verify_password(password, hashed), \
        "Correct password should verify successfully"
    
    # Verifying wrong password should fail
    wrong_password = password + "wrong"
    assert not verify_password(wrong_password, hashed), \
        "Wrong password should not verify"
    
    # Same password should produce different hashes (due to salt)
    hashed2 = hash_password(password)
    assert hashed != hashed2, \
        "Same password should produce different hashes (salt)"
    
    # But both hashes should verify the same password
    assert verify_password(password, hashed2), \
        "Second hash should also verify the password"


@settings(max_examples=100)
@given(
    st.text(min_size=8, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),  # Uppercase, Lowercase, Decimal number
        min_codepoint=33, max_codepoint=126  # Printable ASCII
    ))
)
def test_property_89_password_strength_validation_valid(password):
    """
    Property 89: Password strength validation (valid passwords)
    
    For any password that meets requirements:
    - At least 8 characters
    - Contains uppercase letter
    - Contains lowercase letter
    - Contains number
    
    Validation should return (True, "")
    
    Validates: Requirements 1.5, 22.1
    """
    # Ensure password meets all requirements
    assume(len(password) >= 8)
    assume(any(c.isupper() for c in password))
    assume(any(c.islower() for c in password))
    assume(any(c.isdigit() for c in password))
    
    is_valid, error_msg = validate_password_strength(password)
    
    assert is_valid, f"Valid password should pass validation: {error_msg}"
    assert error_msg == "", "Valid password should have no error message"


@settings(max_examples=100)
@given(st.text(min_size=0, max_size=7))
def test_property_89_password_too_short(password):
    """
    Property 89: Password strength validation (too short)
    
    For any password shorter than 8 characters:
    - Validation should return (False, error_message)
    - Error message should mention length requirement
    
    Validates: Requirements 1.5, 22.1
    """
    is_valid, error_msg = validate_password_strength(password)
    
    assert not is_valid, "Short password should fail validation"
    assert "8 characters" in error_msg.lower() or "length" in error_msg.lower(), \
        "Error message should mention length requirement"


@settings(max_examples=100)
@given(st.text(min_size=8, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyz0123456789'))
def test_property_89_password_no_uppercase(password):
    """
    Property 89: Password strength validation (no uppercase)
    
    For any password without uppercase letters:
    - Validation should return (False, error_message)
    - Error message should mention uppercase requirement
    
    Validates: Requirements 1.5, 22.1
    """
    # Ensure no uppercase
    assume(not any(c.isupper() for c in password))
    
    is_valid, error_msg = validate_password_strength(password)
    
    assert not is_valid, "Password without uppercase should fail"
    assert "uppercase" in error_msg.lower(), \
        "Error message should mention uppercase requirement"


@settings(max_examples=100)
@given(st.text(min_size=8, max_size=50, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
def test_property_89_password_no_lowercase(password):
    """
    Property 89: Password strength validation (no lowercase)
    
    For any password without lowercase letters:
    - Validation should return (False, error_message)
    - Error message should mention uppercase or lowercase requirement
    
    Validates: Requirements 1.5, 22.1
    """
    # Ensure no lowercase
    assume(not any(c.islower() for c in password))
    # Ensure has uppercase (otherwise it will fail on uppercase check first)
    assume(any(c.isupper() for c in password))
    
    is_valid, error_msg = validate_password_strength(password)
    
    assert not is_valid, "Password without lowercase should fail"
    assert "lowercase" in error_msg.lower(), \
        "Error message should mention lowercase requirement"


@settings(max_examples=100)
@given(st.text(min_size=8, max_size=50, alphabet='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'))
def test_property_89_password_no_number(password):
    """
    Property 89: Password strength validation (no number)
    
    For any password without numbers:
    - Validation should return (False, error_message)
    - Error message should mention number requirement
    
    Validates: Requirements 1.5, 22.1
    """
    # Ensure no numbers
    assume(not any(c.isdigit() for c in password))
    # Ensure has uppercase and lowercase (otherwise will fail on those checks first)
    assume(any(c.isupper() for c in password))
    assume(any(c.islower() for c in password))
    
    is_valid, error_msg = validate_password_strength(password)
    
    assert not is_valid, "Password without numbers should fail"
    assert "number" in error_msg.lower() or "digit" in error_msg.lower(), \
        "Error message should mention number requirement"


def test_password_hashing_is_deterministic_verification():
    """
    Test that password verification is deterministic
    
    The same password and hash should always verify the same way
    """
    password = "TestPassword123"
    hashed = hash_password(password)
    
    # Verify multiple times - should always succeed
    for _ in range(10):
        assert verify_password(password, hashed)
    
    # Wrong password should always fail
    for _ in range(10):
        assert not verify_password("WrongPassword123", hashed)
