"""
Security utilities for Larry Navigator
Input sanitization and validation
"""

import re
from typing import Optional

# Dangerous patterns that could indicate prompt injection or malicious input
DANGEROUS_PATTERNS = [
    r'<script[^>]*>.*?</script>',  # Script tags
    r'javascript:',  # JavaScript protocol
    r'on\w+\s*=',  # Event handlers (onclick, onerror, etc.)
    r'<iframe[^>]*>',  # Iframes
    r'eval\s*\(',  # eval() calls
    r'exec\s*\(',  # exec() calls
    r'__import__',  # Python imports
    r'system\s*\(',  # System calls
]

# Prompt injection patterns
INJECTION_PATTERNS = [
    r'ignore\s+(all\s+)?(previous|prior|above)\s+(instructions|prompts|commands)',
    r'disregard\s+(all\s+)?(previous|prior|above)',
    r'forget\s+(all\s+)?(previous|prior|above)',
    r'new\s+instructions?:',
    r'system\s*:\s*you\s+are',
    r'["\']?\s*\+\s*["\']',  # String concatenation attempts
]

def sanitize_user_input(user_input: str, max_length: int = 10000) -> tuple[str, Optional[str]]:
    """
    Sanitize user input to prevent prompt injection and malicious code.
    
    Args:
        user_input: The raw user input string
        max_length: Maximum allowed length for input
        
    Returns:
        tuple: (sanitized_input, warning_message)
               warning_message is None if no issues found
    """
    if not user_input or not isinstance(user_input, str):
        return "", "Invalid input: must be a non-empty string"
    
    # Check length
    if len(user_input) > max_length:
        return user_input[:max_length], f"Input truncated to {max_length} characters"
    
    # Check for dangerous patterns
    for pattern in DANGEROUS_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return "", f"Input rejected: potentially malicious content detected"
    
    # Check for prompt injection attempts
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, user_input, re.IGNORECASE):
            return "", f"Input rejected: potential prompt injection detected"
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', user_input).strip()
    
    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')
    
    return sanitized, None

def validate_api_key(api_key: str, key_type: str = "anthropic") -> tuple[bool, Optional[str]]:
    """
    Validate API key format.
    
    Args:
        api_key: The API key to validate
        key_type: Type of API key ("anthropic", "exa", "neo4j")
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not api_key or not isinstance(api_key, str):
        return False, "API key must be a non-empty string"
    
    # Remove whitespace
    api_key = api_key.strip()
    
    # Check format based on type
    if key_type == "anthropic":
        if not api_key.startswith("sk-ant-"):
            return False, "Anthropic API key must start with 'sk-ant-'"
        if len(api_key) < 20:
            return False, "Anthropic API key appears to be too short"
    
    elif key_type == "exa":
        if len(api_key) < 10:
            return False, "Exa API key appears to be too short"
    
    # Check for suspicious characters
    if re.search(r'[<>"\']', api_key):
        return False, "API key contains invalid characters"
    
    return True, None

def check_rate_limit(session_state, max_messages: int = 10, time_window: int = 60) -> tuple[bool, Optional[str]]:
    """
    Check if user has exceeded rate limit.
    
    Args:
        session_state: Streamlit session state object
        max_messages: Maximum number of messages allowed in time window
        time_window: Time window in seconds
        
    Returns:
        tuple: (is_allowed, error_message)
    """
    import time
    
    # Initialize message timestamps if not exists
    if "message_timestamps" not in session_state:
        session_state.message_timestamps = []
    
    current_time = time.time()
    
    # Remove timestamps older than time window
    session_state.message_timestamps = [
        ts for ts in session_state.message_timestamps 
        if current_time - ts < time_window
    ]
    
    # Check if limit exceeded
    if len(session_state.message_timestamps) >= max_messages:
        wait_time = int(time_window - (current_time - session_state.message_timestamps[0]))
        return False, f"Rate limit exceeded. Please wait {wait_time} seconds before sending another message."
    
    # Add current timestamp
    session_state.message_timestamps.append(current_time)
    
    return True, None
