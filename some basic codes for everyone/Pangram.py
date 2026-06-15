import tkinter as tk
from tkinter import ttk, font
import string

class PangramCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pangram Checker")
        self.root.geometry("700x700")
        self.root.resizable(True, True)
        
        bg_color = "#f8f7f3"
        self.root.configure(bg=bg_color)
        
        main_frame = tk.Frame(root, bg=bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_font = font.Font(family="Helvetica", size=24, weight="bold")
        title_label = tk.Label(main_frame, text="Pangram Checker", font=title_font, bg=bg_color, fg="#1a1a1a")
        title_label.pack(pady=(0, 5))
        
        subtitle_font = font.Font(family="Helvetica", size=11)
        subtitle_label = tk.Label(main_frame, text="Check if your text contains all 26 letters of the alphabet", 
                                  font=subtitle_font, bg=bg_color, fg="#666")
        subtitle_label.pack(pady=(0, 20))
        
        card_frame = tk.Frame(main_frame, bg="white", relief=tk.FLAT)
        card_frame.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
        card_frame.configure(highlightthickness=1, highlightbackground="#e0e0e0")
        
        content_frame = tk.Frame(card_frame, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        label_font = font.Font(family="Helvetica", size=12, weight="bold")
        input_label = tk.Label(content_frame, text="Enter a sentence", font=label_font, bg="white", fg="#1a1a1a")
        input_label.pack(anchor="w", pady=(0, 10))
        
        self.text_input = tk.Text(content_frame, height=6, width=40, 
                                  font=("Helvetica", 11), wrap=tk.WORD, 
                                  bg="#f8f7f3", fg="#1a1a1a", 
                                  relief=tk.FLAT, borderwidth=1, 
                                  highlightthickness=1, highlightbackground="#d3d1c7")
        self.text_input.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        self.text_input.bind("<<Change>>", lambda *args: self.on_text_change())
        self.text_input.bind("<KeyRelease>", lambda *args: self.on_text_change())
        
        self.result_frame = tk.Frame(content_frame, bg="#eaf3de", relief=tk.FLAT)
        self.result_frame.pack(fill=tk.X, pady=(0, 15), padx=0)
        self.result_frame.configure(highlightthickness=1, highlightbackground="#97c459")
        
        result_content = tk.Frame(self.result_frame, bg="#eaf3de")
        result_content.pack(fill=tk.BOTH, expand=True, padx=15, pady=12)
        
        self.result_status = tk.Label(result_content, text="✓ Pangram Detected!", 
                                     font=("Helvetica", 11, "bold"), bg="#eaf3de", fg="#3b6d11")
        self.result_status.pack(anchor="w", pady=(0, 8))
        
        self.result_count = tk.Label(result_content, text="26/26 letters found", 
                                    font=("Helvetica", 18, "bold"), bg="#eaf3de", fg="#3b6d11")
        self.result_count.pack(anchor="w")
        
        self.missing_section = tk.Frame(content_frame, bg="white")
        self.missing_section.pack(fill=tk.X, pady=(0, 15))
        
        missing_title_font = font.Font(family="Helvetica", size=11, weight="bold")
        self.missing_title = tk.Label(self.missing_section, text="Missing letters (0)", 
                                     font=missing_title_font, bg="white", fg="#444441")
        self.missing_title.pack(anchor="w", pady=(0, 10))
        
        self.missing_letters_frame = tk.Frame(self.missing_section, bg="white")
        self.missing_letters_frame.pack(fill=tk.X)
        
        alphabet_title = tk.Label(content_frame, text="Alphabet coverage", 
                                 font=missing_title_font, bg="white", fg="#444441")
        alphabet_title.pack(anchor="w", pady=(0, 10))
        
        self.alphabet_frame = tk.Frame(content_frame, bg="white")
        self.alphabet_frame.pack(fill=tk.BOTH, expand=True)
        
        self.create_alphabet_grid()
        
        tip_frame = tk.Frame(main_frame, bg="#f1efe8", relief=tk.FLAT)
        tip_frame.pack(fill=tk.X, pady=(20, 0), padx=0)
        tip_frame.configure(highlightthickness=1, highlightbackground="#888780")
        
        tip_content = tk.Frame(tip_frame, bg="#f1efe8")
        tip_content.pack(fill=tk.BOTH, padx=15, pady=12)
        
        tip_text = tk.Label(tip_content, text='Tip: A pangram is a sentence that uses every letter of the alphabet at least once. The most famous example is "The quick brown fox jumps over the lazy dog."',
                           font=("Helvetica", 10), bg="#f1efe8", fg="#5f5e5a", wraplength=500, justify=tk.LEFT)
        tip_text.pack(anchor="w")
    
    def create_alphabet_grid(self):
        for widget in self.alphabet_frame.winfo_children():
            widget.destroy()
        
        grid_frame = tk.Frame(self.alphabet_frame, bg="white")
        grid_frame.pack(anchor="w")
        
        for i, letter in enumerate(string.ascii_lowercase):
            btn = tk.Label(grid_frame, text=letter.upper(), 
                          width=3, height=1,
                          font=("Helvetica", 10, "bold"),
                          bg="#f1efe8", fg="#5f5e5a",
                          relief=tk.FLAT,
                          borderwidth=1)
            btn.grid(row=i//13, column=i%13, padx=4, pady=4)
            btn.name = f"letter_{letter}"
    
    def is_pangram(self, sentence):
        alphabet = set(string.ascii_lowercase)
        sentence = sentence.lower()
        return set(sentence) >= alphabet
    
    def on_text_change(self):
        sentence = self.text_input.get("1.0", tk.END)
        
        alphabet = set(string.ascii_lowercase)
        sentence_lower = sentence.lower()
        sentence_chars = set(c for c in sentence_lower if c in alphabet)
        
        found_letters = sorted(sentence_chars)
        missing_letters = sorted(alphabet - sentence_chars)
        is_pangram = len(missing_letters) == 0
        
        if is_pangram:
            self.result_frame.configure(bg="#eaf3de", highlightbackground="#97c459")
            for widget in self.result_frame.winfo_children():
                widget.configure(bg="#eaf3de")
            self.result_status.configure(text="✓ Pangram Detected!", fg="#3b6d11", bg="#eaf3de")
            self.result_count.configure(fg="#3b6d11", bg="#eaf3de")
        else:
            self.result_frame.configure(bg="#fcebeb", highlightbackground="#f09595")
            for widget in self.result_frame.winfo_children():
                widget.configure(bg="#fcebeb")
            self.result_status.configure(text="✗ Not a Pangram", fg="#a32d2d", bg="#fcebeb")
            self.result_count.configure(fg="#a32d2d", bg="#fcebeb")
        
        self.result_count.configure(text=f"{len(found_letters)}/26 letters found")
        
        for widget in self.missing_letters_frame.winfo_children():
            widget.destroy()
        
        if missing_letters:
            self.missing_title.configure(text=f"Missing letters ({len(missing_letters)})")
            for letter in missing_letters:
                badge = tk.Label(self.missing_letters_frame, text=letter.upper(),
                               font=("Helvetica", 10, "bold"),
                               bg="#fcebeb", fg="#a32d2d",
                               padx=8, pady=4, relief=tk.FLAT, borderwidth=1)
                badge.pack(side=tk.LEFT, padx=3, pady=3)
        else:
            self.missing_title.configure(text="")
        
        alphabet_labels = self.alphabet_frame.winfo_children()[0].winfo_children() if self.alphabet_frame.winfo_children() else []
        
        for i, letter in enumerate(string.ascii_lowercase):
            if i < len(alphabet_labels):
                widget = alphabet_labels[i]
                if letter in found_letters:
                    widget.configure(bg="#eaf3de", fg="#3b6d11", highlightbackground="#97c459")
                else:
                    widget.configure(bg="#f1efe8", fg="#5f5e5a", highlightbackground="#d3d1c7")

if __name__ == "__main__":
    root = tk.Tk()
    app = PangramCheckerApp(root)
    root.mainloop()
