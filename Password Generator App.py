import argparse
import secrets
import string
import os
import math
from datetime import datetime
from typing import List, Tuple

# Optional clipboard support
try:
    import pyperclip
    CLIPBOARD_SUPPORT = True
except ImportError:
    CLIPBOARD_SUPPORT = False

# ANSI color codes for vibrant output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
CYAN = '\033[96m'
RESET = '\033[0m'

def calculate_entropy(password: str) -> float:
    """Calculate the mathematical entropy of the password in bits."""
    pool_size = 0
    if any(c.islower() for c in password):
        pool_size += 26
    if any(c.isupper() for c in password):
        pool_size += 26
    if any(c.isdigit() for c in password):
        pool_size += 10
    if any(c in string.punctuation for c in password):
        pool_size += len(string.punctuation)
        
    if pool_size == 0:
        return 0.0
        
    # Entropy = Length * log2(Pool Size)
    entropy = len(password) * math.log2(pool_size)
    return round(entropy, 2)

def check_strength(password: str) -> Tuple[str, str, float]:
    """Evaluate the strength of a password based on entropy bits."""
    entropy = calculate_entropy(password)
    
    # Standard entropy benchmarks:
    # < 50 bits: Weak | 50-70 bits: Reasonable | > 70 bits: Strong
    if entropy < 50:
        return "Weak", RED, entropy
    elif entropy < 70:
        return "Medium", YELLOW, entropy
    else:
        return "Strong", GREEN, entropy

def generate_password(length: int, use_lower=True, use_upper=True, use_digits=True, use_symbols=True) -> str:
    """Generate a secure password with guaranteed character variety."""
    required_sets = []
    if use_lower: required_sets.append(string.ascii_lowercase)
    if use_upper: required_sets.append(string.ascii_uppercase)
    if use_digits: required_sets.append(string.digits)
    if use_symbols: required_sets.append(string.punctuation)
    
    if not required_sets:
        raise ValueError("At least one character set must be selected.")
        
    min_length = len(required_sets)
    if length < min_length:
        raise ValueError(f"Length must be at least {min_length} for the selected criteria.")
    
    # Ensure at least one character from each selected set is included
    password_chars = [secrets.choice(charset) for charset in required_sets]
    
    # Fill the rest with random choices from the combined pool
    all_chars = ''.join(required_sets)
    password_chars += [secrets.choice(all_chars) for _ in range(length - min_length)]
    
    # Shuffle to prevent predictable patterns (like always starting with a lowercase letter)
    secrets.SystemRandom().shuffle(password_chars)
    return ''.join(password_chars)

def save_to_file(passwords: List[str], file_name: str) -> None:
    """Save generated passwords to a file with timestamp."""
    mode = 'w'
    if os.path.exists(file_name):
        action = input("File exists. Overwrite (o), append (a), or cancel (c)? ").lower().strip()
        if action == 'a':
            mode = 'a'
        elif action != 'o':
            print(f"{YELLOW}Save cancelled.{RESET}")
            return
            
    with open(file_name, mode) as f:
        f.write(f"\n--- Passwords generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for i, pwd in enumerate(passwords, 1):
            f.write(f"Password {i}: {pwd}\n")
    print(f"{GREEN}Passwords saved to {file_name}{RESET}")

def interactive_mode() -> None:
    """Run the password generator in interactive mode with a menu."""
    passwords = []
    
    while True:
        print(f"\n{CYAN}=== Advanced Password Generator ==={RESET}")
        print("1. Generate password(s)")
        print("2. View generated passwords")
        print("3. Check an existing password's strength")
        print("4. Save generated passwords to file")
        print("5. Exit")
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == '1':
            try:
                length = int(input("Enter password length: "))
                num = int(input("Enter number of passwords: "))
                use_symbols = input("Include symbols? (y/n): ").lower() == 'y'
                use_upper = input("Include uppercase? (y/n): ").lower() != 'n' # Default yes
                use_digits = input("Include numbers? (y/n): ").lower() != 'n'   # Default yes
                
                passwords = [generate_password(length, use_upper=use_upper, use_digits=use_digits, use_symbols=use_symbols) for _ in range(num)]
                
                print(f"\n{GREEN}Generated Passwords:{RESET}")
                for i, pwd in enumerate(passwords, 1):
                    strength, color, entropy = check_strength(pwd)
                    print(f"{color}{i}. {pwd} (Strength: {strength}, Entropy: {entropy} bits){RESET}")
                
                # Auto-copy to clipboard if only one was generated
                if num == 1 and CLIPBOARD_SUPPORT:
                    pyperclip.copy(passwords[0])
                    print(f"{CYAN}* Password copied to clipboard! *{RESET}")
                elif num == 1 and not CLIPBOARD_SUPPORT:
                    print(f"{YELLOW}* Install 'pyperclip' (pip install pyperclip) for auto-clipboard support *{RESET}")

            except ValueError as e:
                print(f"{RED}Error: {e}{RESET}")
        
        elif choice == '2':
            if not passwords:
                print(f"{YELLOW}No passwords generated yet in this session.{RESET}")
            else:
                print(f"\n{GREEN}Current Session Passwords:{RESET}")
                for i, pwd in enumerate(passwords, 1):
                    strength, color, entropy = check_strength(pwd)
                    print(f"{color}{i}. {pwd} (Strength: {strength}){RESET}")
        
        elif choice == '3':
            pwd = input("Enter password to check: ")
            strength, color, entropy = check_strength(pwd)
            print(f"{color}Strength: {strength} ({entropy} bits of entropy){RESET}")
        
        elif choice == '4':
            if not passwords:
                print(f"{YELLOW}No passwords to save.{RESET}")
            else:
                file_name = input("Enter file name (e.g., passwords.txt): ")
                save_to_file(passwords, file_name)
        
        elif choice == '5':
            print(f"{GREEN}Stay secure! Goodbye.{RESET}")
            break
        
        else:
            print(f"{RED}Invalid choice. Please select 1-5.{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate secure passwords with guaranteed variety and entropy checking."
    )
    parser.add_argument("-l", "--length", type=int, default=16, help="Password length")
    parser.add_argument("-n", "--num", type=int, default=1, help="Number of passwords to generate")
    parser.add_argument("-ns", "--no-symbols", action="store_false", dest="symbols", help="Exclude special symbols")
    parser.add_argument("-nu", "--no-upper", action="store_false", dest="upper", help="Exclude uppercase letters")
    parser.add_argument("-nd", "--no-digits", action="store_false", dest="digits", help="Exclude numbers")
    parser.add_argument("-o", "--output", help="Save passwords to a file")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        try:
            passwords = [generate_password(args.length, use_upper=args.upper, use_digits=args.digits, use_symbols=args.symbols) for _ in range(args.num)]
            for i, pwd in enumerate(passwords, 1):
                strength, color, entropy = check_strength(pwd)
                print(f"{color}{i}. {pwd} - Strength: {strength} ({entropy} bits){RESET}")
            
            if args.num == 1 and CLIPBOARD_SUPPORT:
                pyperclip.copy(passwords[0])
                print(f"{CYAN}* Password copied to clipboard! *{RESET}")
                
            if args.output:
                save_to_file(passwords, args.output)
        except ValueError as e:
            parser.error(str(e))
