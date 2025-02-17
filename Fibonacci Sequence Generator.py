def fibonacci(n):
    sequence = []
    a, b = 0, 1
    for _ in range(n):
        sequence.append(a)
        a, b = b, a + b
    return sequence

if __name__ == "__main__":
    try:
        num = int(input("Enter the number of Fibonacci numbers to generate: "))
        print("Fibonacci sequence:")
        print(fibonacci(num))
    except ValueError:
        print("Please enter a valid integer.")
