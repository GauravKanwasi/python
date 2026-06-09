import tkinter as tk
from tkinter import messagebox, scrolledtext

class EnhancedCalculatorApp:
    def __init__(self, root):
        # Set up the main window properties
        self.root = root
        self.root.title("Enhanced Calculator")
        self.root.geometry("420x550")
        self.root.configure(bg="#ADD8E6")  # Light blue background

        self.setup_ui()

    def setup_ui(self):
        """Initialize and layout the user interface components."""
        # Title label
        title_label = tk.Label(self.root, text="Enhanced Calculator", font=("Arial", 18, "bold"), bg="#ADD8E6")
        title_label.pack(pady=15)

        # Input frame for numbers
        input_frame = tk.Frame(self.root, bg="#ADD8E6")
        input_frame.pack(pady=10)

        # First number
        tk.Label(input_frame, text="First Number:", font=("Arial", 12), bg="#ADD8E6").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.entry1 = tk.Entry(input_frame, width=15, font=("Arial", 12))
        self.entry1.grid(row=0, column=1, padx=5, pady=5)
        self.entry1.focus_set()  # Start with focus here
        self.entry1.bind('<Return>', self.calculate)  # Enter key triggers calculation

        # Second number
        tk.Label(input_frame, text="Second Number:", font=("Arial", 12), bg="#ADD8E6").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.entry2 = tk.Entry(input_frame, width=15, font=("Arial", 12))
        self.entry2.grid(row=1, column=1, padx=5, pady=5)
        self.entry2.bind('<Return>', self.calculate)  # Enter key triggers calculation

        # Operation selection with radio buttons
        self.operation_var = tk.StringVar(value="+")  # Default to addition
        operations_frame = tk.Frame(self.root, bg="#ADD8E6")
        operations_frame.pack(pady=10)
        
        # Loop to generate radio buttons cleanly
        operations = [("Add", "+"), ("Subtract", "-"), ("Multiply", "*"), ("Divide", "/")]
        for i, (text, op) in enumerate(operations):
            tk.Radiobutton(operations_frame, text=text, variable=self.operation_var, value=op, 
                           font=("Arial", 11), bg="#ADD8E6").grid(row=0, column=i, padx=5)

        # Result display label (Inline instead of intrusive popups)
        self.result_label = tk.Label(self.root, text="Result: --", font=("Arial", 14, "bold"), bg="#ADD8E6", fg="#2C3E50")
        self.result_label.pack(pady=10)

        # Main Button frame
        button_frame = tk.Frame(self.root, bg="#ADD8E6")
        button_frame.pack(pady=5)

        # Calculate & Clear Inputs buttons
        tk.Button(button_frame, text="Calculate", font=("Arial", 12, "bold"), command=self.calculate, width=10).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Clear Inputs", font=("Arial", 12), command=self.clear_inputs, width=10).grid(row=0, column=1, padx=10)

        # History section
        tk.Label(self.root, text="Calculation History:", font=("Arial", 12, "bold"), bg="#ADD8E6").pack(pady=(10, 0))
        self.history_text = scrolledtext.ScrolledText(self.root, width=45, height=8, font=("Arial", 10))
        self.history_text.pack(pady=5)
        self.history_text.configure(state='disabled')  # Read-only history

        # Bottom buttons (Clear History & Quit)
        bottom_btn_frame = tk.Frame(self.root, bg="#ADD8E6")
        bottom_btn_frame.pack(pady=10)
        tk.Button(bottom_btn_frame, text="Clear History", font=("Arial", 11), command=self.clear_history).grid(row=0, column=0, padx=15)
        tk.Button(bottom_btn_frame, text="Quit", font=("Arial", 11), command=self.root.quit).grid(row=0, column=1, padx=15)

    def calculate(self, event=None):
        """Perform the selected arithmetic operation and display the result."""
        try:
            num1 = float(self.entry1.get())
            num2 = float(self.entry2.get())
            operation = self.operation_var.get()
            
            if operation == "+":
                result = num1 + num2
            elif operation == "-":
                result = num1 - num2
            elif operation == "*":
                result = num1 * num2
            elif operation == "/":
                if num2 == 0:
                    messagebox.showerror("Error", "Cannot divide by zero")
                    return
                result = num1 / num2
            
            # Format numbers nicely (removes trailing zeros for whole numbers)
            result_formatted = f"{result:g}" if result.is_integer() else f"{result:.4f}"
            result_str = f"{num1:g} {operation} {num2:g} = {result_formatted}"
            
            # Update inline result label
            self.result_label.config(text=f"Result: {result_formatted}")
            
            # Update history
            self.history_text.configure(state='normal')
            self.history_text.insert(tk.END, result_str + "\n")
            self.history_text.configure(state='disabled')
            self.history_text.see(tk.END)  # Auto-scroll to the latest entry
            
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values")

    def clear_inputs(self):
        """Clear the number input fields and reset the result label."""
        self.entry1.delete(0, tk.END)
        self.entry2.delete(0, tk.END)
        self.result_label.config(text="Result: --")
        self.entry1.focus_set()

    def clear_history(self):
        """Clear the calculation history."""
        self.history_text.configure(state='normal')
        self.history_text.delete(1.0, tk.END)
        self.history_text.configure(state='disabled')


if __name__ == "__main__":
    # Start the application
    root = tk.Tk()
    app = EnhancedCalculatorApp(root)
    root.mainloop()
