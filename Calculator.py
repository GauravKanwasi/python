import tkinter as tk
from tkinter import messagebox, scrolledtext

def calculate(event=None):
    """Perform the selected arithmetic operation and display the result."""
    try:
        num1 = float(entry1.get())
        num2 = float(entry2.get())
        operation = operation_var.get()
        
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
        
        result_str = f"{num1} {operation} {num2} = {result:.2f}"
        messagebox.showinfo("Result", result_str)
        
        # Update history
        history_text.configure(state='normal')
        history_text.insert(tk.END, result_str + "\n")
        history_text.configure(state='disabled')
        history_text.see(tk.END)  # Auto-scroll to the latest entry
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numbers")

def clear_history():
    """Clear the calculation history."""
    history_text.configure(state='normal')
    history_text.delete(1.0, tk.END)
    history_text.configure(state='disabled')

# Set up the main window
root = tk.Tk()
root.title("Enhanced Calculator")
root.geometry("400x500")
root.configure(bg="#ADD8E6")  # Light blue background

# Title label
title_label = tk.Label(root, text="Enhanced Calculator", font=("Arial", 18, "bold"), bg="#ADD8E6")
title_label.pack(pady=10)

# Input frame for numbers
input_frame = tk.Frame(root, bg="#ADD8E6")
input_frame.pack(pady=10)

# First number
label1 = tk.Label(input_frame, text="First Number:", font=("Arial", 12), bg="#ADD8E6")
label1.grid(row=0, column=0, padx=5, pady=5)
entry1 = tk.Entry(input_frame, width=10, font=("Arial", 12))
entry1.grid(row=0, column=1, padx=5, pady=5)
entry1.focus_set()  # Start with focus here
entry1.bind('<Return>', calculate)  # Enter key triggers calculation

# Second number
label2 = tk.Label(input_frame, text="Second Number:", font=("Arial", 12), bg="#ADD8E6")
label2.grid(row=1, column=0, padx=5, pady=5)
entry2 = tk.Entry(input_frame, width=10, font=("Arial", 12))
entry2.grid(row=1, column=1, padx=5, pady=5)
entry2.bind('<Return>', calculate)  # Enter key triggers calculation

# Operation selection with radio buttons
operation_var = tk.StringVar(value="+")  # Default to addition
operations_frame = tk.Frame(root, bg="#ADD8E6")
operations_frame.pack(pady=10)
tk.Radiobutton(operations_frame, text="Add", variable=operation_var, value="+", font=("Arial", 12), bg="#ADD8E6").grid(row=0, column=0, padx=5)
tk.Radiobutton(operations_frame, text="Subtract", variable=operation_var, value="-", font=("Arial", 12), bg="#ADD8E6").grid(row=0, column=1, padx=5)
tk.Radiobutton(operations_frame, text="Multiply", variable=operation_var, value="*", font=("Arial", 12), bg="#ADD8E6").grid(row=0, column=2, padx=5)
tk.Radiobutton(operations_frame, text="Divide", variable=operation_var, value="/", font=("Arial", 12), bg="#ADD8E6").grid(row=0, column=3, padx=5)

# Calculate button
calculate_button = tk.Button(root, text="Calculate", font=("Arial", 12), command=calculate)
calculate_button.pack(pady=10)

# History section
history_label = tk.Label(root, text="Calculation History:", font=("Arial", 12), bg="#ADD8E6")
history_label.pack()
history_text = scrolledtext.ScrolledText(root, width=40, height=10, font=("Arial", 10))
history_text.pack(pady=5)
history_text.configure(state='disabled')  # Read-only history

# Clear history button
clear_button = tk.Button(root, text="Clear History", font=("Arial", 12), command=clear_history)
clear_button.pack(pady=5)

# Quit button
quit_button = tk.Button(root, text="Quit", font=("Arial", 12), command=root.quit)
quit_button.pack(pady=5)

# Start the application
root.mainloop()
