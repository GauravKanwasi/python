import tkinter as tk
from tkinter import ttk, messagebox

def sum_of_digits(n):
    try:
        n = abs(int(n))
        return sum(int(digit) for digit in str(n))
    except ValueError:
        raise ValueError("Input must be a valid integer")

def calculate():
    try:
        user_input = entry.get().strip()
        if not user_input:
            messagebox.showwarning("Input Error", "Please enter a number")
            return
        
        result = sum_of_digits(user_input)
        result_var.set(f"Sum of digits: {result}")
        
        history_list.insert(0, f"{user_input} → {result}")
        if history_list.size() > 10:
            history_list.delete(history_list.size() - 1)
            
        entry.delete(0, tk.END)
    except ValueError as e:
        messagebox.showerror("Error", str(e))

def clear_all():
    entry.delete(0, tk.END)
    result_var.set("")
    history_list.delete(0, tk.END)

def on_enter(event):
    calculate()

root = tk.Tk()
root.title("Sum of Digits Calculator")
root.geometry("400x500")
root.configure(bg="#f0f0f0")

title_label = tk.Label(root, text="Sum of Digits Calculator", font=("Arial", 16, "bold"), bg="#f0f0f0")
title_label.pack(pady=15)

input_frame = ttk.Frame(root)
input_frame.pack(padx=20, pady=10, fill=tk.X)

ttk.Label(input_frame, text="Enter Number:").pack(anchor=tk.W)
entry = ttk.Entry(input_frame, font=("Arial", 12), width=30)
entry.pack(fill=tk.X, pady=5)
entry.bind("<Return>", on_enter)

button_frame = ttk.Frame(root)
button_frame.pack(padx=20, pady=10, fill=tk.X)

ttk.Button(button_frame, text="Calculate", command=calculate).pack(side=tk.LEFT, padx=5)
ttk.Button(button_frame, text="Clear All", command=clear_all).pack(side=tk.LEFT, padx=5)

result_var = tk.StringVar(value="")
result_label = tk.Label(root, textvariable=result_var, font=("Arial", 14, "bold"), fg="#2ecc71", bg="#f0f0f0")
result_label.pack(pady=15)

history_label = tk.Label(root, text="History (Recent 10):", font=("Arial", 11, "bold"), bg="#f0f0f0")
history_label.pack(anchor=tk.W, padx=20, pady=(15, 5))

history_frame = ttk.Frame(root)
history_frame.pack(padx=20, pady=10, fill=tk.BOTH, expand=True)

scrollbar = ttk.Scrollbar(history_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

history_list = tk.Listbox(history_frame, yscrollcommand=scrollbar.set, font=("Arial", 10), height=10)
history_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.config(command=history_list.yview)

root.mainloop()
