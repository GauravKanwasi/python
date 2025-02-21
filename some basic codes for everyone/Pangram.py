import string

def is_pangram(sentence):
    alphabet = set(string.ascii_lowercase)  # All lowercase letters
    sentence = sentence.lower()
    return set(sentence) >= alphabet  # Check if sentence contains all letters
