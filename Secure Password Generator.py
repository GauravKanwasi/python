import secrets
import string
from typing import Optional

def generate_password(
    length: int = 12,
    exclude_chars: str = "",
    require_lower: bool = True,
    require_upper: bool = True,
    require_digits: bool = True,
    require_symbols: bool = True
) -> str:
    """Generate a secure random password with customizable requirements.
    
    Args:
        length: Desired password length (minimum 4)
        exclude_chars: Characters to exclude from password
        require_*: Whether to require specific character types
        
    Returns:
        Generated password string
        
    Raises:
        ValueError: If requirements can't be satisfied
    """
    
    if not isinstance(length, int) or length < 1:
        raise ValueError("Password length must be a positive integer")
    
    categories = {}
    if require_lower:
        categories['lower'] = [c for c in string.ascii_lowercase if c not in exclude_chars]
    if require_upper:
        categories['upper'] = [c for c in string.ascii_uppercase if c not in exclude_chars]
    if require_digits:
        categories['digits'] = [c for c in string.digits if c not in exclude_chars]
    if require_symbols:
        categories['symbols'] = [c for c in string.punctuation if c not in exclude_chars]
    
    # Check for available categories
    required_categories = [name for name, chars in categories.items() if chars]
    if not required_categories:
        raise ValueError("No character categories available after exclusions")
    
    min_length = len(required_categories)
    if length < min_length:
        raise ValueError(f"Password length must be at least {min_length} for current requirements")
    
    password = []
    for cat in required_categories:
        password.append(secrets.choice(categories[cat]))
    
    all_chars = [c for chars in categories.values() for c in chars]
    remaining = length - len(password)
    password += [secrets.choice(all_chars) for _ in range(remaining)]
    
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

print("Secure password:", generate_password(
    length=14,
    exclude_chars="<>{}'\"",
    require_symbols=False
))
