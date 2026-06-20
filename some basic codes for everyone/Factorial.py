import tkinter as tk
from tkinter import ttk, messagebox
import threading

def factorial(n):
    """Calculate factorial recursively"""
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)

class FactorialCalculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Factorial Calculator")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Configure style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Factorial Calculator", 
                               font=("Segoe UI", 20, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Calculate n! instantly",
                                  font=("Segoe UI", 10), foreground="gray")
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Input label
        input_label = ttk.Label(main_frame, text="Enter a number:", 
                               font=("Segoe UI", 11))
        input_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Input field
        self.number_var = tk.StringVar()
        self.input_field = ttk.Entry(main_frame, textvariable=self.number_var,
                                     font=("Segoe UI", 12), width=30)
        self.input_field.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.input_field.bind("<Return>", lambda e: self.calculate())
        
        # Calculate button
        self.calc_button = ttk.Button(main_frame, text="Calculate", 
                                      command=self.calculate)
        self.calc_button.grid(row=4, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Result frame
        self.result_frame = ttk.LabelFrame(main_frame, text="Result", padding="15")
        self.result_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        self.result_frame.grid_remove()
        
        # Result label
        self.result_label = ttk.Label(self.result_frame, text="", 
                                     font=("Courier New", 14, "bold"), foreground="#667eea")
        self.result_label.pack(side=tk.LEFT)
        
        # Info frame
        info_frame = ttk.LabelFrame(main_frame, text="Info", padding="10")
        info_frame.grid(row=6, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        info_text = "Example: 5! = 5 × 4 × 3 × 2 × 1 = 120\nWorks with numbers from 0 to 170"
        info_label = ttk.Label(info_frame, text=info_text, 
                              font=("Segoe UI", 9), foreground="gray", justify=tk.LEFT)
        info_label.pack(anchor=tk.W)
        
        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
    def calculate(self):
        """Handle calculate button click"""
        number_str = self.number_var.get().strip()
        
        if not number_str:
            messagebox.showerror("Error", "Please enter a number")
            return
        
        try:
            num = int(number_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            self.number_var.set("")
            return
        
        if num < 0:
            messagebox.showerror("Error", "Please enter a non-negative number")
            return
        
        if num > 170:
            messagebox.showerror("Error", "Number too large (max 170)")
            return
        
        # Disable button and show loading
        self.calc_button.config(state="disabled", text="Computing...")
        self.root.update()
        
        # Calculate in separate thread to prevent freezing
        def compute():
            try:
                result = factorial(num)
                self.root.after(0, lambda: self.show_result(num, result))
            except RecursionError:
                self.root.after(0, lambda: messagebox.showerror("Error", "Recursion limit exceeded"))
            finally:
                self.root.after(0, lambda: self.calc_button.config(state="normal", text="Calculate"))
        
        thread = threading.Thread(target=compute)
        thread.daemon = True
        thread.start()
    
    def show_result(self, num, result):
        """Display the result"""
        self.result_label.config(text=f"{num}! = {result:,}")
        self.result_frame.grid()

if __name__ == "__main__":
    root = tk.Tk()
    app = FactorialCalculator(root)
    root.mainloop()
