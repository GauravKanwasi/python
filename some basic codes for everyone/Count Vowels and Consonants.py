import tkinter as tk

def count_vowels_and_consonants(text):
    # Use a set for faster O(1) character lookups
    vowels = set("aeiouAEIOU")
    num_vowels = 0
    num_consonants = 0
    
    for char in text:
        if char.isalpha():  # Ensure the character is a letter
            if char in vowels:
                num_vowels += 1
            else:
                num_consonants += 1
                
    return num_vowels, num_consonants

def on_count_clicked():
    # Retrieve input, calculate, and update the result label
    user_text = text_entry.get()
    v, c = count_vowels_and_consonants(user_text)
    result_label.config(text=f"Vowels: {v} | Consonants: {c}")

# --- UI Setup ---
root = tk.Tk()
root.title("Text Analyzer")
root.geometry("350x200")
root.configure(padx=20, pady=20)

# Input Field
tk.Label(root, text="Enter your text below:", font=("Arial", 10)).pack(anchor="w")
text_entry = tk.Entry(root, width=40, font=("Arial", 12))
text_entry.pack(pady=10)

# Action Button
count_button = tk.Button(root, text="Count Characters", command=on_count_clicked, bg="#4CAF50", fg="black")
count_button.pack(pady=5)

# Results Display
result_label = tk.Label(root, text="Vowels: 0 | Consonants: 0", font=("Arial", 12, "bold"))
result_label.pack(pady=15)

# Start the application loop
root.mainloop()
