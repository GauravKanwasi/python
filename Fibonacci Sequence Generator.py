def fibonacci(n):
    """Generate the first n Fibonacci numbers starting from F(0) = 0."""
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    sequence = [0] * n  
    a, b = 0, 1
    for i in range(n):
        sequence[i] = a
        a, b = b, a + b 
    return sequence

if __name__ == "__main__":
    try:
        num = int(input("Enter the number of Fibonacci numbers to generate: "))
        if num < 0:
            print("Please enter a non-negative integer.")
        else:
            print("Fibonacci sequence:")
            print(fibonacci(num))
    except ValueError:
        print("Please enter a valid integer.")
