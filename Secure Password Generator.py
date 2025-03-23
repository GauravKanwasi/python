import secrets
import string
from typing import Optional

def generate_password(
    length: int = 12,
    exclude_chars: str = "",
    include_chars: str = "",
    require_lower: bool = True,
    require_upper: bool = True,
    require_digits: bool = True,
    require_symbols: bool = True
) -> str:
    """Generate a secure random password with customizable requirements.
    
    Args:
        length: Desired password length (minimum based on requirements)
        exclude_chars: Characters to exclude from password
        include_chars: Additional characters to include in the password pool
        require_*: Whether to require specific character types
        
    Returns:
        Generated password string
        
    Raises:
        ValueError: If requirements can't be satisfied
    """
    
    if not isinstance(length, int) or length < 1:
        raise ValueError("Password length must be a positive integer")
    
    categories = {}
    
    # Process required categories with validation
    if require_lower:
        lower_chars = [c for c in string.ascii_lowercase if c not in exclude_chars]
        if not lower_chars:
            raise ValueError("Lowercase characters are required but all excluded")
        categories['lower'] = lower_chars
    
    if require_upper:
        upper_chars = [c for c in string.ascii_uppercase if c not in exclude_chars]
        if not upper_chars:
            raise ValueError("Uppercase characters are required but all excluded")
        categories['upper'] = upper_chars
    
    if require_digits:
        digits_chars = [c for c in string.digits if c not in exclude_chars]
        if not digits_chars:
            raise ValueError("Digits are required but all excluded")
        categories['digits'] = digits_chars
    
    if require_symbols:
        symbols_chars = [c for c in string.punctuation if c not in exclude_chars]
        if not symbols_chars:
            raise ValueError("Symbols are required but all excluded")
        categories['symbols'] = symbols_chars
    
    required_categories = list(categories.keys())
    if not required_categories:
        raise ValueError("At least one character category must be required")
    
    min_length = len(required_categories)
    if length < min_length:
        raise ValueError(f"Password length must be at least {min_length} to meet requirements")
    
    # Process included characters
    include_filtered = [c for c in include_chars if c not in exclude_chars]
    
    # Build character pool
    all_chars = []
    for chars in categories.values():
        all_chars.extend(chars)
    all_chars.extend(include_filtered)
    
    # Generate password with required characters
    password = []
    for cat in required_categories:
        password.append(secrets.choice(categories[cat]))
    
    # Fill remaining characters
    remaining = length - len(password)
    password += [secrets.choice(all_chars) for _ in range(remaining)]
    
    # Shuffle to avoid predictable patterns
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

# Example usage
print("Secure password:", generate_password(
    length=14,
    exclude_chars="<>{}'\"",
    include_chars="€$",
    require_symbols=False
))
