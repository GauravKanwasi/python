import secrets
import string
import sys
from typing import List, Optional

# ANSI color codes for vibrant output
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "END": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m",
}

def cprint(text: str, color: str, end: str = "\n") -> None:
    """Print colored text"""
    print(f"{COLORS.get(color, '')}{text}{COLORS['END']}", end=end)

def generate_password(
    length: int = 12,
    exclude_chars: str = "",
    include_chars: str = "",
    require_lower: bool = True,
    require_upper: bool = True,
    require_digits: bool = True,
    require_symbols: bool = True,
    avoid_ambiguous: bool = False
) -> str:
    """Generate a secure random password with customizable requirements.
    
    Args:
        length: Desired password length
        exclude_chars: Characters to exclude
        include_chars: Additional characters to include
        require_lower: Require lowercase letters
        require_upper: Require uppercase letters
        require_digits: Require digits
        require_symbols: Require symbols
        avoid_ambiguous: Avoid ambiguous characters (1lI0O)
        
    Returns:
        Generated password string
        
    Raises:
        ValueError: If requirements can't be satisfied
    """
    if not isinstance(length, int) or length < 1:
        raise ValueError("Password length must be a positive integer")
    
    # Define ambiguous characters to avoid
    ambiguous = "1lI0O" if avoid_ambiguous else ""
    
    categories = {}
    
    if require_lower:
        lower_chars = [c for c in string.ascii_lowercase 
                      if c not in exclude_chars and c not in ambiguous]
        if not lower_chars:
            raise ValueError("Lowercase characters required but all excluded")
        categories['lower'] = lower_chars
    
    if require_upper:
        upper_chars = [c for c in string.ascii_uppercase 
                      if c not in exclude_chars and c not in ambiguous]
        if not upper_chars:
            raise ValueError("Uppercase characters required but all excluded")
        categories['upper'] = upper_chars
    
    if require_digits:
        digits_chars = [c for c in string.digits 
                       if c not in exclude_chars and c not in ambiguous]
        if not digits_chars:
            raise ValueError("Digits required but all excluded")
        categories['digits'] = digits_chars
    
    if require_symbols:
        symbols_chars = [c for c in string.punctuation 
                        if c not in exclude_chars and c not in ambiguous]
        if not symbols_chars:
            raise ValueError("Symbols required but all excluded")
        categories['symbols'] = symbols_chars
    
    required_categories = list(categories.keys())
    if not required_categories:
        raise ValueError("At least one character category must be required")
    
    min_length = len(required_categories)
    if length < min_length:
        raise ValueError(f"Password length must be at least {min_length} to meet requirements")
    
    include_filtered = [c for c in include_chars 
                       if c not in exclude_chars and c not in ambiguous]
    
    all_chars = []
    for chars in categories.values():
        all_chars.extend(chars)
    all_chars.extend(include_filtered)
    
    if not all_chars:
        raise ValueError("No characters available to generate password")
    
    password = []
    for cat in required_categories:
        password.append(secrets.choice(categories[cat]))
    
    remaining = length - len(password)
    password += [secrets.choice(all_chars) for _ in range(remaining)]
    
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

def get_yes_no(prompt: str, default: Optional[bool] = None) -> bool:
    """Get yes/no input with colored prompt and default option"""
    options = " (y/n)" 
    if default is True:
        options = " (Y/n)"
    elif default is False:
        options = " (y/N)"
    
    while True:
        cprint(prompt + options, "CYAN", end=" ")
        response = input().strip().lower()
        
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        if not response and default is not None:
            return default
            
        cprint("Please enter 'y' or 'n'", "RED")

def get_int(prompt: str, min_val: int, max_val: int = 100) -> int:
    """Get integer input within range with colored prompt"""
    while True:
        try:
            cprint(f"{prompt} [{min_val}-{max_val}]:", "CYAN", end=" ")
            value = int(input().strip())
            if min_val <= value <= max_val:
                return value
            cprint(f"Please enter a number between {min_val} and {max_val}", "RED")
        except ValueError:
            cprint("Please enter a valid number", "RED")

def get_string(prompt: str, allow_empty: bool = True) -> str:
    """Get string input with colored prompt"""
    while True:
        cprint(prompt, "CYAN", end=" ")
        value = input().strip()
        if allow_empty or value:
            return value
        cprint("This field cannot be empty", "RED")

def show_menu(title: str, options: List[str]) -> int:
    """Display a menu and return selected index"""
    cprint(f"\n{title}", "HEADER")
    for i, option in enumerate(options, 1):
        cprint(f"{i}. {option}", "YELLOW")
    
    while True:
        cprint("\nEnter your choice:", "BLUE", end=" ")
        choice = input().strip()
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice)
        cprint(f"Please enter a number between 1 and {len(options)}", "RED")

def calculate_strength(password: str) -> str:
    """Estimate password strength based on complexity"""
    length = len(password)
    unique_chars = len(set(password))
    char_diversity = unique_chars / length
    
    # Strength calculation based on length and diversity
    if length >= 16 and char_diversity > 0.7:
        return "Very Strong"
    if length >= 12 and char_diversity > 0.6:
        return "Strong"
    if length >= 10:
        return "Good"
    return "Fair"

def main():
    """Interactive interface for generating custom passwords"""
    # Initial settings
    settings = {
        'length': 12,
        'exclude_chars': "",
        'include_chars': "",
        'require_lower': True,
        'require_upper': True,
        'require_digits': True,
        'require_symbols': True,
        'avoid_ambiguous': True,
        'num_passwords': 1
    }
    
    # Welcome message
    cprint("\n" + "=" * 50, "GREEN")
    cprint("SECURE PASSWORD GENERATOR", "HEADER")
    cprint("=" * 50, "GREEN")
    cprint("Create strong, customizable passwords with advanced options\n", "BLUE")
    
    while True:
        # Main menu
        choice = show_menu("MAIN MENU", [
            "Generate Password(s)",
            "Configure Settings",
            "View Current Settings",
            "Exit"
        ])
        
        if choice == 1:  # Generate passwords
            try:
                num_passwords = get_int("How many passwords to generate?", 1, 20)
                passwords = []
                
                for _ in range(num_passwords):
                    pwd = generate_password(
                        length=settings['length'],
                        exclude_chars=settings['exclude_chars'],
                        include_chars=settings['include_chars'],
                        require_lower=settings['require_lower'],
                        require_upper=settings['require_upper'],
                        require_digits=settings['require_digits'],
                        require_symbols=settings['require_symbols'],
                        avoid_ambiguous=settings['avoid_ambiguous']
                    )
                    passwords.append(pwd)
                
                # Display results
                cprint("\n" + "=" * 50, "GREEN")
                cprint("GENERATED PASSWORDS", "HEADER")
                cprint("=" * 50, "GREEN")
                
                for i, pwd in enumerate(passwords, 1):
                    strength = calculate_strength(pwd)
                    color = "GREEN" if "Strong" in strength else "YELLOW"
                    cprint(f"\nPassword #{i} ({strength}):", color)
                    cprint(pwd, "BOLD")
                
                cprint("\n" + "-" * 50, "BLUE")
                cprint("Important: Store these passwords securely!", "RED")
                cprint("-" * 50, "BLUE")
            
            except ValueError as e:
                cprint(f"\nError: {str(e)}", "RED")
        
        elif choice == 2:  # Configure settings
            cprint("\nCONFIGURE SETTINGS", "HEADER")
            
            # Password length
            settings['length'] = get_int("Password length", 4, 64)
            
            # Character types
            cprint("\nCharacter Requirements:", "UNDERLINE")
            settings['require_lower'] = get_yes_no("Include lowercase letters?", True)
            settings['require_upper'] = get_yes_no("Include uppercase letters?", True)
            settings['require_digits'] = get_yes_no("Include digits?", True)
            settings['require_symbols'] = get_yes_no("Include symbols?", True)
            
            # Advanced options
            cprint("\nAdvanced Options:", "UNDERLINE")
            settings['avoid_ambiguous'] = get_yes_no("Avoid ambiguous characters (e.g., 1lI0O)?", True)
            
            if get_yes_no("Exclude specific characters?"):
                settings['exclude_chars'] = get_string("Characters to exclude:")
            else:
                settings['exclude_chars'] = ""
            
            if get_yes_no("Include additional characters?"):
                settings['include_chars'] = get_string("Additional characters to include:")
            else:
                settings['include_chars'] = ""
            
            cprint("\nSettings updated successfully!", "GREEN")
        
        elif choice == 3:  # View settings
            cprint("\nCURRENT SETTINGS", "HEADER")
            cprint(f"Password Length: {settings['length']}", "YELLOW")
            cprint(f"Lowercase: {'Yes' if settings['require_lower'] else 'No'}", "YELLOW")
            cprint(f"Uppercase: {'Yes' if settings['require_upper'] else 'No'}", "YELLOW")
            cprint(f"Digits: {'Yes' if settings['require_digits'] else 'No'}", "YELLOW")
            cprint(f"Symbols: {'Yes' if settings['require_symbols'] else 'No'}", "YELLOW")
            cprint(f"Avoid Ambiguous: {'Yes' if settings['avoid_ambiguous'] else 'No'}", "YELLOW")
            cprint(f"Excluded Chars: {settings['exclude_chars'] or 'None'}", "YELLOW")
            cprint(f"Included Chars: {settings['include_chars'] or 'None'}", "YELLOW")
        
        elif choice == 4:  # Exit
            cprint("\nThank you for using the Secure Password Generator!", "GREEN")
            cprint("Stay safe online!\n", "BLUE")
            sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        cprint("\n\nOperation cancelled. Exiting...", "RED")
        sys.exit(0)
