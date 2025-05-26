import argparse
import secrets
import string
import os
from datetime import datetime

# ANSI color codes for vibrant output
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_strength(password):
    """Evaluate the strength of a password based on length and character variety."""
    length = len(password)
    has_lowercase = any(c.islower() for c in password)
    has_uppercase = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c in string.punctuation for c in password)
    char_types = sum([has_lowercase, has_uppercase, has_digit, has_symbol])
    
    if length < 8:
        return "Weak", RED
    elif length < 12:
        if char_types >= 3:
            return "Medium", YELLOW
        else:
            return "Weak", RED
    else:
        if char_types >= 3:
            return "Strong", GREEN
        elif char_types >= 2:
            return "Medium", YELLOW
        else:
            return "Weak", RED

def generate_password(length, symbols=True):
    """Generate a secure password with guaranteed character variety."""
    required_sets = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        required_sets.append(string.punctuation)
    
    min_length = len(required_sets)
    if length < min_length:
        raise ValueError(f"Password length must be at least {min_length} when symbols are {'enabled' if symbols else 'disabled'}.")
    
    password_chars = [secrets.choice(charset) for charset in required_sets]
    all_chars = ''.join(required_sets)
    password_chars += [secrets.choice(all_chars) for _ in range(length - min_length)]
    
    secrets.SystemRandom().shuffle(password_chars)
    return ''.join(password_chars)

def interactive_mode():
    """Run the password generator in interactive mode with a menu."""
    passwords = []
    while True:
        print(f"\n{YELLOW}=== Password Generator Menu ==={RESET}")
        print("1. Generate password(s)")
        print("2. View generated passwords")
        print("3. Check password strength")
        print("4. Save generated passwords to file")
        print("5. Exit")
        
        choice = input("Choose an option (1-5): ").strip()
        
        if choice == '1':
            try:
                length = int(input("Enter password length: "))
                num = int(input("Enter number of passwords: "))
                symbols = input("Include symbols? (y/n): ").lower() == 'y'
                min_length = 4 if symbols else 3
                if length < min_length:
                    print(f"{RED}Error: Length must be at least {min_length}.{RESET}")
                    continue
                if num <= 0:
                    print(f"{RED}Error: Number of passwords must be positive.{RESET}")
                    continue
                passwords = [generate_password(length, symbols) for _ in range(num)]
                print(f"\n{GREEN}Generated Passwords:{RESET}")
                for i, pwd in enumerate(passwords, 1):
                    strength, color = check_strength(pwd)
                    print(f"{color}{i}. {pwd} - Strength: {strength}{RESET}")
                save = input("Save to file? (y/n): ").lower()
                if save == 'y':
                    file_name = input("Enter file name: ")
                    save_to_file(passwords, file_name)
            except ValueError as e:
                print(f"{RED}Error: {e}{RESET}")
        
        elif choice == '2':
            if not passwords:
                print(f"{YELLOW}No passwords generated yet.{RESET}")
            else:
                print(f"\n{GREEN}Generated Passwords:{RESET}")
                for i, pwd in enumerate(passwords, 1):
                    strength, color = check_strength(pwd)
                    print(f"{color}{i}. {pwd} - Strength: {strength}{RESET}")
        
        elif choice == '3':
            pwd = input("Enter password to check: ")
            strength, color = check_strength(pwd)
            print(f"{color}Strength: {strength}{RESET}")
        
        elif choice == '4':
            if not passwords:
                print(f"{YELLOW}No passwords to save.{RESET}")
            else:
                file_name = input("Enter file name: ")
                save_to_file(passwords, file_name)
        
        elif choice == '5':
            print(f"{GREEN}Goodbye!{RESET}")
            break
        
        else:
            print(f"{RED}Invalid choice. Please select 1-5.{RESET}")

def save_to_file(passwords, file_name):
    """Save generated passwords to a file with timestamp."""
    if os.path.exists(file_name):
        action = input("File exists. Overwrite (o), append (a), or cancel (c)? ").lower()
        if action == 'o':
            mode = 'w'
        elif action == 'a':
            mode = 'a'
        else:
            print(f"{YELLOW}Save cancelled.{RESET}")
            return
    else:
        mode = 'w'
    
    with open(file_name, mode) as f:
        f.write(f"# Passwords generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        for i, pwd in enumerate(passwords, 1):
            f.write(f"Password {i}: {pwd}\n")
    print(f"{GREEN}Passwords saved to {file_name}{RESET}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate secure passwords with guaranteed variety. Use interactive mode for a dynamic experience!"
    )
    parser.add_argument("-l", "--length", type=int, default=12, help="Password length (minimum 3 without symbols, 4 with symbols)")
    parser.add_argument("-n", "--num", type=int, default=1, help="Number of passwords to generate")
    parser.add_argument("-ns", "--no-symbols", action="store_false", dest="symbols", help="Exclude special symbols")
    parser.add_argument("-o", "--output", help="Save passwords to a file")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run in interactive mode")
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        try:
            passwords = [generate_password(args.length, args.symbols) for _ in range(args.num)]
            for i, pwd in enumerate(passwords, 1):
                strength, color = check_strength(pwd)
                print(f"{color}{i}. {pwd} - Strength: {strength}{RESET}")
            if args.output:
                save_to_file(passwords, args.output)
        except ValueError as e:
            parser.error(str(e))
