#!/usr/bin/env python3
import argparse
import secrets
import string

def generate_password(length, symbols=True):
    chars = string.ascii_letters + string.digits
    if symbols: chars += string.punctuation
    return ''.join(secrets.choice(chars) for _ in range(length))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Password Generator")
    parser.add_argument("-l", "--length", type=int, default=12, help="Password length")
    parser.add_argument("-ns", "--no-symbols", action="store_false", help="Exclude symbols")
    args = parser.parse_args()
    print(generate_password(args.length, args.no_symbols))
