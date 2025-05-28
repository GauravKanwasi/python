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
        require_lower: Whether to require lowercase letters
        require_upper: Whether to require uppercase letters
        require_digits: Whether to require digits
        require_symbols: Whether to require symbols
        
    Returns:
        Generated password string
        
    Raises:
        ValueError: If requirements can't be satisfied
    """
    if not isinstance(length, int) or length < 1:
        raise ValueError("Password length must be a positive integer")
    
    categories = {}
    
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
    
    include_filtered = [c for c in include_chars if c not in exclude_chars]
    
    all_chars = []
    for chars in categories.values():
        all_chars.extend(chars)
    all_chars.extend(include_filtered)
    
    password = []
    for cat in required_categories:
        password.append(secrets.choice(categories[cat]))
    
    remaining = length - len(password)
    password += [secrets.choice(all_chars) for _ in range(remaining)]
    
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

def main():
    """Interactive interface for generating a custom password."""
    print("Welcome to the Secure Password Generator!")
    
    # Ask about excluding characters
    exclude = input("Do you want to exclude any characters? (y/n): ").lower()
    if exclude in ['y', 'yes']:
        exclude_chars = input("Enter characters to exclude (e.g., <>'): ")
    else:
        exclude_chars = ""
    
    # Ask about including additional characters
    include = input("Do you want to include any additional characters? (y/n): ").lower()
    if include in ['y', 'yes']:
        include_chars = input("Enter additional characters to include (e.g., €$): ")
    else:
        include_chars = ""
    
    # Let user select required character types
    print("\nPlease select which character types to require (select at least one):")
    print("1. Lowercase letters (a-z)")
    print("2. Uppercase letters (A-Z)")
    print("3. Digits (0-9)")
    print("4. Symbols (!@#$%^&*)")
    while True:
        selection = input("Enter the numbers separated by commas (e.g., 1,2,3): ")
        # Parse input into a list of integers, filtering out non-digits
        selected = [int(x.strip()) for x in selection.split(',') if x.strip().isdigit()]
        if selected and all(1 <= x <= 4 for x in selected):
            break
        print("Please select at least one valid option (1-4).")
    
    # Set requirements based on user selection
    require_lower = 1 in selected
    require_upper = 2 in selected
    require_digits = 3 in selected
    require_symbols = 4 in selected
    
    # Calculate minimum length based on number of required categories
    min_length = len(selected)
    
    # Ask for password length, ensuring it meets the minimum
    while True:
        try:
            length = int(input(f"Enter desired password length (at least {min_length}): "))
            if length >= min_length:
                break
            print(f"Length must be at least {min_length} to include all required types.")
        except ValueError:
            print("Please enter a valid integer.")
    
    # Generate and display the password
    try:
        password = generate_password(
            length=length,
            exclude_chars=exclude_chars,
            include_chars=include_chars,
            require_lower=require_lower,
            require_upper=require_upper,
            require_digits=require_digits,
            require_symbols=require_symbols
        )
        print("\nGenerated password:", password)
    except ValueError as e:
        print("\nError:", str(e))

if __name__ == "__main__":
    main()
