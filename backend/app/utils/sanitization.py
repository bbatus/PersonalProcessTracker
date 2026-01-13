"""
Input sanitization utilities to prevent SQL injection and XSS attacks
"""

import html
import re
from typing import Any, Dict, List, Union


def sanitize_html(text: str) -> str:
    """
    Sanitize HTML to prevent XSS attacks
    
    Escapes HTML special characters to prevent script injection
    
    Args:
        text: Input text that may contain HTML
        
    Returns:
        Sanitized text with HTML entities escaped
    """
    if not isinstance(text, str):
        return text
    
    # Escape HTML special characters
    return html.escape(text)


def sanitize_input(value: Any) -> Any:
    """
    Sanitize user input to prevent SQL injection and XSS
    
    Note: SQLAlchemy with parameterized queries already prevents SQL injection.
    This function provides additional sanitization for string inputs.
    
    Args:
        value: Input value to sanitize
        
    Returns:
        Sanitized value
    """
    if isinstance(value, str):
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Trim whitespace
        value = value.strip()
        
        # Escape HTML for XSS prevention
        value = sanitize_html(value)
        
        return value
    
    elif isinstance(value, dict):
        # Recursively sanitize dictionary values
        return {k: sanitize_input(v) for k, v in value.items()}
    
    elif isinstance(value, list):
        # Recursively sanitize list items
        return [sanitize_input(item) for item in value]
    
    else:
        # Return other types as-is (numbers, booleans, None, etc.)
        return value


def validate_no_sql_injection(text: str) -> bool:
    """
    Check if text contains potential SQL injection patterns
    
    Note: This is a defense-in-depth measure. Primary protection
    comes from using parameterized queries in SQLAlchemy.
    
    Args:
        text: Text to validate
        
    Returns:
        True if text appears safe, False if suspicious patterns detected
    """
    if not isinstance(text, str):
        return True
    
    # Common SQL injection patterns (case-insensitive)
    suspicious_patterns = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bDROP\b.*\bTABLE\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(--)",  # SQL comment
        r"(;.*\b(DROP|DELETE|INSERT|UPDATE)\b)",
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
        r"('.*OR.*'.*=.*')",
    ]
    
    text_upper = text.upper()
    
    for pattern in suspicious_patterns:
        if re.search(pattern, text_upper, re.IGNORECASE):
            return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent directory traversal attacks
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename safe for file system operations
    """
    if not isinstance(filename, str):
        return ""
    
    # Remove path separators and parent directory references
    filename = filename.replace('/', '').replace('\\', '')
    filename = filename.replace('..', '')
    
    # Remove null bytes
    filename = filename.replace('\x00', '')
    
    # Keep only alphanumeric, dash, underscore, and dot
    filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
    
    # Limit length
    if len(filename) > 255:
        filename = filename[:255]
    
    return filename


def sanitize_email(email: str) -> str:
    """
    Basic email sanitization
    
    Args:
        email: Email address
        
    Returns:
        Sanitized email (lowercase, trimmed)
    """
    if not isinstance(email, str):
        return ""
    
    # Trim and lowercase
    email = email.strip().lower()
    
    # Remove null bytes
    email = email.replace('\x00', '')
    
    return email
