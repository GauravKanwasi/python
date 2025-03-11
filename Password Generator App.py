import argparse
import secrets
import string

def generate_password(length, symbols=True):
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate secure passwords with guaranteed character variety.")
    parser.add_argument("-l", "--length", type=int, default=12, help="Password length (minimum 3 without symbols, 4 with symbols)")
    parser.add_argument("-ns", "--no-symbols", action="store_false", dest="symbols", help="Exclude special symbols")
    args = parser.parse_args()
    
    try:
        print(generate_password(args.length, args.symbols))
    except ValueError as e:
        parser.error(str(e))