def is_isogram(word):
    word = word.lower()  # Convert to lowercase to handle case-insensitivity
    return len(set(word)) == len(word)  # Convert to a set to remove duplicates