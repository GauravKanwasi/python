def fibonacci(n: int) -> list[int]:
    if n < 0:
        raise ValueError("n must be a non-negative integer")
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

if __name__ == "__main__":
    try:
        n = int(input("Enter count: "))
        print("Fibonacci:", fibonacci(n))
    except ValueError as e:
        print(f"Error: {e}")
