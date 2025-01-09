def is_anagram(str1, str2):
    return sorted(str1.lower()) == sorted(str2.lower())  # Sort the characters and compare