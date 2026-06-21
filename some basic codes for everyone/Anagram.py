from collections import Counter

def is_anagram(str1, str2):
    """Check if two strings are anagrams (ignores spaces, punctuation, case)."""
    # Validate inputs
    if not isinstance(str1, str) or not isinstance(str2, str):
        raise TypeError("Both arguments must be strings")
    
    # Remove non-alphanumeric characters and convert to lowercase
    clean1 = ''.join(char.lower() for char in str1 if char.isalnum())
    clean2 = ''.join(char.lower() for char in str2 if char.isalnum())
    
    return Counter(clean1) == Counter(clean2)


# Test cases
if __name__ == "__main__":
    print(is_anagram("listen", "silent"))  # True
    print(is_anagram("hello", "world"))  # False
    print(is_anagram("A Gentleman", "Elegant Man"))  # True
