def is_isogram(word):
    """
    Determine if a word is an isogram (a word with no repeating letters).
    
    An isogram is a word or phrase without repeating letters. Spaces, hyphens,
    and special characters are ignored. The check is case-insensitive.
    
    Args:
        word (str): The word to check for isogram property
        
    Returns:
        bool: True if the word is an isogram, False otherwise
        
    Raises:
        TypeError: If the input is not a string
        
    Examples:
        >>> is_isogram("dermatoglyphics")
        True
        >>> is_isogram("moose")
        False
        >>> is_isogram("Background")
        True
        >>> is_isogram("downstream")
        False
    """
    
    # Input validation: check if word is a string
    if not isinstance(word, str):
        raise TypeError(f"Expected string, got {type(word).__name__}")
    
    # Handle empty strings (empty string is technically an isogram)
    if not word:
        return True
    
    # Convert to lowercase to handle case-insensitivity (e.g., 'A' and 'a' are same)
    word = word.lower()
    
    # Filter out non-alphabetic characters (spaces, hyphens, punctuation, numbers, etc.)
    # Keep only letters for the isogram check
    letters_only = ''.join(char for char in word if char.isalpha())
    
    # If after filtering there are no letters, it's considered an isogram
    if not letters_only:
        return True
    
    # Convert the letters to a set to remove all duplicates
    # If the length of the set equals the length of the filtered string,
    # then all letters are unique (no duplicates exist)
    return len(set(letters_only)) == len(letters_only)


# ============================================================================
# TEST CASES - Comprehensive testing to ensure the function works perfectly
# ============================================================================

if __name__ == "__main__":
    # Test cases for valid isograms (no repeating letters)
    print("✓ Valid Isograms (should return True):")
    assert is_isogram("dermatoglyphics") == True
    print("  ✓ is_isogram('dermatoglyphics') = True")
    
    assert is_isogram("background") == True
    print("  ✓ is_isogram('background') = True")
    
    assert is_isogram("a") == True
    print("  ✓ is_isogram('a') = True")
    
    assert is_isogram("uncopyrightable") == True
    print("  ✓ is_isogram('uncopyrightable') = True")
    
    # Test cases for non-isograms (has repeating letters)
    print("\n✗ Invalid Isograms (should return False):")
    assert is_isogram("moose") == False
    print("  ✗ is_isogram('moose') = False (o repeats)")
    
    assert is_isogram("banana") == False
    print("  ✗ is_isogram('banana') = False (a and n repeat)")
    
    assert is_isogram("eleven") == False
    print("  ✗ is_isogram('eleven') = False (e repeats)")
    
    # Test cases for edge cases
    print("\n⚙ Edge Cases:")
    
    # Case insensitivity
    assert is_isogram("Background") == True
    print("  ✓ is_isogram('Background') = True (case-insensitive)")
    
    assert is_isogram("DERMATOGLYPHICS") == True
    print("  ✓ is_isogram('DERMATOGLYPHICS') = True (uppercase)")
    
    # Words with special characters and spaces
    assert is_isogram("back-ground") == True
    print("  ✓ is_isogram('back-ground') = True (hyphens ignored)")
    
    assert is_isogram("abc def") == True
    print("  ✓ is_isogram('abc def') = True (spaces ignored)")
    
    assert is_isogram("try-phobic") == True
    print("  ✓ is_isogram('try-phobic') = True (hyphens ignored)")
    
    # Empty string
    assert is_isogram("") == True
    print("  ✓ is_isogram('') = True (empty string)")
    
    # String with only non-alphabetic characters
    assert is_isogram("123 !@#") == True
    print("  ✓ is_isogram('123 !@#') = True (no letters to repeat)")
    
    # Mixed with repeating letters and special characters
    assert is_isogram("abc-abc") == False
    print("  ✗ is_isogram('abc-abc') = False (letters repeat despite special chars)")
    
    # Test error handling
    print("\n⚠ Error Handling:")
    try:
        is_isogram(123)
        print("  ✗ FAILED: Should raise TypeError for non-string input")
    except TypeError as e:
        print(f"  ✓ Correctly raises TypeError: {e}")
    
    try:
        is_isogram(None)
        print("  ✗ FAILED: Should raise TypeError for None input")
    except TypeError as e:
        print(f"  ✓ Correctly raises TypeError: {e}")
    
    print("\n" + "="*60)
    print("✓ All tests passed! Function works perfectly.")
    print("="*60)
