def count_vowels_and_consonants(s):
    vowels = "aeiouAEIOU"
    consonants = "bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ"
    
    num_vowels = sum(1 for char in s if char in vowels)
    num_consonants = sum(1 for char in s if char in consonants)
    
    return num_vowels, num_consonants