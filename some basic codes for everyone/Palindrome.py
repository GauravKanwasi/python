def is_palindrome(s):
    s = ''.join(e for e in s if e.isalnum()).lower()  # Remove non-alphanumeric and make lowercase
    return s == s[::-1]  # Check if the string is the same forward and backward
