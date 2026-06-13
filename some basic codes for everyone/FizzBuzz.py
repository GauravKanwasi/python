def fizz_buzz(n):
    """
    FizzBuzz function that prints numbers from 1 to n with special rules.
    
    Rules:
    - If divisible by both 3 and 5: print "FizzBuzz"
    - If divisible by 3: print "Fizz"
    - If divisible by 5: print "Buzz"
    - Otherwise: print the number
    
    Args:
        n (int): The upper limit (inclusive) for the sequence
    """
    
    # Iterate through numbers from 1 to n (inclusive)
    for i in range(1, n + 1):
        # IMPORTANT: Check both 3 and 5 FIRST before individual checks
        # This ensures numbers like 15, 30, 45 print "FizzBuzz" not just "Fizz"
        if i % 3 == 0 and i % 5 == 0:
            print("FizzBuzz")
        
        # Check if the number is only divisible by 3
        elif i % 3 == 0:
            print("Fizz")
        
        # Check if the number is only divisible by 5
        elif i % 5 == 0:
            print("Buzz")
        
        # If none of the above conditions are true, print the number itself
        else:
            print(i)


# Example usage
if __name__ == "__main__":
    # Run FizzBuzz for numbers 1 to 30
    fizz_buzz(30)
