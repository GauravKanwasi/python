import tkinter as tk
from tkinter import messagebox

# --- CORE LOGIC ---

def is_prime(n: int) -> bool:
    """
    Determines if a number is prime using the 6k +/- 1 optimization method.
    """
    # 1. Base cases: 0, 1, and negative numbers are mathematically not prime.
    if n <= 1:
        return False
        
    # 2. Base cases: 2 and 3 are the fundamental building block primes.
    if n <= 3:
        return True
        
    # 3. Quick elimination: If it's divisible by 2 or 3, it's not prime.
    # This single check eliminates 2/3rds of all integers instantly.
    if n % 2 == 0 or n % 3 == 0:
        return False
        
    # 4. The 6k +/- 1 Optimization:
    # All prime numbers greater than 3 can be written as (6k - 1) or (6k + 1).
    # Instead of checking every number, we step by 6, checking i and i+2.
    i = 5
    while i * i <= n:
        # If n is divisible by either of the 6k +/- 1 pair, it's composite.
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6 # Skip forward by 6 to test the next pair
        
    return True

# --- USER INTERFACE (UI) ---

def handle_check():
    """
    Triggered when the user clicks the 'Check' button.
    Grabs the input, validates it, and displays the result.
    """
    user_input = entry.get()
    
    try:
        # Attempt to convert the input string to an integer
        num = int(user_input)
        
        # Run our enhanced prime function
        if is_prime(num):
            # Display a success message if prime
            result_label.config(text=f"✅ {num} is a Prime Number!", fg="green")
        else:
            # Display an alternate message if not prime
            result_label.config(text=f"❌ {num} is Composite (Not Prime).", fg="red")
            
    except ValueError:
        # Catch the error if the user types letters or symbols instead of a number
        messagebox.showerror("Invalid Input", "Please enter a valid whole integer.")

# 1. Initialize the main window
root = tk.Tk()
root.title("Prime Number Checker")
root.geometry("350x200")
root.eval('tk::PlaceWindow . center') # Centers the window on your screen

# 2. Add a Title Label
title_label = tk.Label(root, text="Enter a number to check:", font=("Arial", 12))
title_label.pack(pady=(20, 5))

# 3. Add an Entry box for user input
entry = tk.Entry(root, font=("Arial", 14), justify="center", width=15)
entry.pack(pady=5)

# 4. Add a Button to trigger the check
check_button = tk.Button(root, text="Check Prime", font=("Arial", 10, "bold"), command=handle_check)
check_button.pack(pady=10)

# 5. Add a Label to display the result dynamically
result_label = tk.Label(root, text="", font=("Arial", 12, "bold"))
result_label.pack(pady=5)

# 6. Run the application loop
if __name__ == "__main__":
    root.mainloop()
