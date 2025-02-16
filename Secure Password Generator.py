import secrets
import string

def generate_password(length: int = 12, exclude_chars: str = "") -> str:
    """Generate a secure random password with customizable rules."""
    characters = string.ascii_letters + string.digits + string.punctuation
    characters = ''.join(c for c in characters if c not in exclude_chars)
    
    # Ensure at least one character from each category if length >= 4
    password = [
        secrets.choice(string.ascii_lowercase),
        secrets.choice(string.ascii_uppercase),
        secrets.choice(string.digits),
        secrets.choice(string.punctuation)
    ] + [secrets.choice(characters) for _ in range(length - 4)]
    
    secrets.SystemRandom().shuffle(password)
    return ''.join(password)

# Example usage
print("Your secure password:", generate_password(exclude_chars="<>{}"))
