import tkinter as tk
from tkinter import messagebox
import math
import time

class PrimeChecker:
    def __init__(self, root):
        self.root = root
        self.root.title("Prime Number Checker")
        self.root.geometry("600x650")
        self.root.config(bg="#1e1e1e")
        
        self.setup_ui()
    
    def setup_ui(self):
        title_frame = tk.Frame(self.root, bg="#1e1e1e")
        title_frame.pack(pady=20)
        
        title_label = tk.Label(
            title_frame,
            text="Prime Number Checker",
            font=("Arial", 24, "bold"),
            fg="#00ff00",
            bg="#1e1e1e"
        )
        title_label.pack()
        
        input_frame = tk.Frame(self.root, bg="#1e1e1e")
        input_frame.pack(pady=15)
        
        input_label = tk.Label(
            input_frame,
            text="Enter a number:",
            font=("Arial", 12),
            fg="#ffffff",
            bg="#1e1e1e"
        )
        input_label.pack(side=tk.LEFT, padx=10)
        
        self.input_field = tk.Entry(
            input_frame,
            font=("Arial", 14),
            width=20,
            bg="#333333",
            fg="#ffffff",
            insertbackground="#00ff00"
        )
        self.input_field.pack(side=tk.LEFT, padx=10)
        self.input_field.bind("<Return>", lambda e: self.check_prime())
        
        button_frame = tk.Frame(self.root, bg="#1e1e1e")
        button_frame.pack(pady=15)
        
        check_btn = tk.Button(
            button_frame,
            text="Check Prime",
            command=self.check_prime,
            font=("Arial", 12, "bold"),
            bg="#00ff00",
            fg="#000000",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        check_btn.pack(side=tk.LEFT, padx=10)
        
        clear_btn = tk.Button(
            button_frame,
            text="Clear",
            command=self.clear_fields,
            font=("Arial", 12, "bold"),
            bg="#ff6666",
            fg="#ffffff",
            padx=20,
            pady=10,
            cursor="hand2"
        )
        clear_btn.pack(side=tk.LEFT, padx=10)
        
        result_label = tk.Label(
            self.root,
            text="Results:",
            font=("Arial", 12, "bold"),
            fg="#ffff00",
            bg="#1e1e1e"
        )
        result_label.pack(pady=(20, 10), anchor="w", padx=30)
        
        self.result_frame = tk.Frame(self.root, bg="#2a2a2a", relief=tk.SUNKEN, bd=2)
        self.result_frame.pack(pady=10, padx=30, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_text = tk.Text(
            self.result_frame,
            font=("Courier", 11),
            bg="#2a2a2a",
            fg="#00ff00",
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_text.yview)
    
    def is_prime(self, num):
        if num < 2:
            return False
        if num == 2:
            return True
        if num % 2 == 0:
            return False
        
        for i in range(3, int(math.sqrt(num)) + 1, 2):
            if num % i == 0:
                return False
        return True
    
    def prime_factorization(self, num):
        factors = []
        d = 2
        while d * d <= num:
            while num % d == 0:
                factors.append(d)
                num //= d
            d += 1
        if num > 1:
            factors.append(num)
        return factors
    
    def get_divisors(self, num):
        divisors = []
        for i in range(1, int(math.sqrt(num)) + 1):
            if num % i == 0:
                divisors.append(i)
                if i != num // i:
                    divisors.append(num // i)
        return sorted(divisors)
    
    def check_prime(self):
        try:
            num = int(self.input_field.get().strip())
            
            if num < 0:
                messagebox.showerror("Invalid Input", "Please enter a non-negative number")
                return
            
            start_time = time.time()
            prime_result = self.is_prime(num)
            elapsed_time = (time.time() - start_time) * 1000
            
            self.result_text.config(state=tk.NORMAL)
            self.result_text.delete(1.0, tk.END)
            
            if num == 0 or num == 1:
                self.result_text.insert(tk.END, f"Number: {num}\n")
                self.result_text.insert(tk.END, f"Status: Neither prime nor composite\n")
                self.result_text.insert(tk.END, f"Time: {elapsed_time:.4f}ms\n")
            else:
                status = "✓ PRIME NUMBER" if prime_result else "✗ NOT PRIME"
                self.result_text.insert(tk.END, f"Number: {num}\n", "")
                
                if prime_result:
                    self.result_text.insert(tk.END, f"Status: {status}\n", "")
                    self.result_text.insert(tk.END, f"\nDivisors: 1, {num}\n", "")
                else:
                    self.result_text.insert(tk.END, f"Status: {status}\n", "")
                    factors = self.prime_factorization(num)
                    self.result_text.insert(tk.END, f"\nPrime Factors: {' × '.join(map(str, factors))}\n", "")
                    
                    divisors = self.get_divisors(num)
                    divisors_str = ", ".join(map(str, divisors))
                    self.result_text.insert(tk.END, f"All Divisors: {divisors_str}\n", "")
                
                self.result_text.insert(tk.END, f"\nExecution Time: {elapsed_time:.4f}ms\n", "")
                self.result_text.insert(tk.END, f"Square Root: {math.sqrt(num):.2f}\n", "")
            
            self.result_text.config(state=tk.DISABLED)
            
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid integer")
            self.input_field.delete(0, tk.END)
    
    def clear_fields(self):
        self.input_field.delete(0, tk.END)
        self.result_text.config(state=tk.NORMAL)
        self.result_text.delete(1.0, tk.END)
        self.result_text.config(state=tk.DISABLED)
        self.input_field.focus()

def main():
    root = tk.Tk()
    app = PrimeChecker(root)
    root.mainloop()

if __name__ == "__main__":
    main()
