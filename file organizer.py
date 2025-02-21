import os
import json
import shutil
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_FILES

class EnhancedFileOrganizer(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Advanced File Organizer")
        self.geometry("1000x800")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configuration
        self.config_file = Path.home() / ".smart_organizer_config.json"
        self.config = self.load_config()
        self.undo_stack = []
        self.exclude_patterns = []
        
        # UI Setup
        self.create_widgets()
        self.selected_folder = ""
        self.current_theme = "light"
        
    def create_widgets(self):
        # Theme Toggle
        ttk.Button(self, text="🌓 Toggle Theme", command=self.toggle_theme).pack(anchor="ne", padx=10, pady=5)
        
        # Folder Selection
        folder_frame = ttk.LabelFrame(self, text="Target Directory")
        folder_frame.pack(pady=10, padx=10, fill="x")
        
        self.folder_entry = ttk.Entry(folder_frame, width=60)
        self.folder_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.folder_entry.drop_target_register(DND_FILES)
        self.folder_entry.dnd_bind('<<Drop>>', self.handle_drop)
        
        ttk.Button(folder_frame, text="Browse", command=self.select_folder).pack(side="left", padx=5)
        
        # Exclusion Patterns
        ttk.Label(self, text="Exclusion Patterns (comma-separated):").pack(anchor="w", padx=15)
        self.exclude_entry = ttk.Entry(self)
        self.exclude_entry.pack(padx=10, fill="x")
        self.exclude_entry.insert(0, ",".join(self.config["exclude_patterns"]))
        
        # Category Management
        cat_frame = ttk.LabelFrame(self, text="File Categories")
        cat_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        self.category_tree = ttk.Treeview(cat_frame, columns=("Extensions"), show="headings")
        self.category_tree.heading("#0", text="Category")
        self.category_tree.heading("Extensions", text="Extensions")
        self.category_tree.pack(side="left", fill="both", expand=True)
        
        control_frame = ttk.Frame(cat_frame)
        control_frame.pack(side="right", padx=5)
        
        ttk.Label(control_frame, text="Category:").pack(anchor="w")
        self.cat_name = ttk.Entry(control_frame)
        self.cat_name.pack(fill="x", pady=2)
        
        ttk.Label(control_frame, text="Extensions:").pack(anchor="w")
        self.cat_exts = ttk.Entry(control_frame)
        self.cat_exts.pack(fill="x", pady=2)
        
        ttk.Button(control_frame, text="➕ Add/Update", command=self.save_category).pack(fill="x", pady=5)
        ttk.Button(control_frame, text="🗑️ Remove", command=self.delete_category).pack(fill="x", pady=5)
        
        # Default Folder Settings
        default_frame = ttk.LabelFrame(self, text="Unmatched Files")
        default_frame.pack(pady=10, padx=10, fill="x")
        
        ttk.Label(default_frame, text="Folder Name:").pack(side="left")
        self.default_folder = ttk.Entry(default_frame, width=20)
        self.default_folder.pack(side="left", padx=5)
        self.default_folder.insert(0, self.config["default_folder"])
        
        self.move_unmatched = tk.BooleanVar(value=self.config["move_unmatched"])
        ttk.Checkbutton(default_frame, text="Move Unmatched Files", variable=self.move_unmatched).pack(side="left", padx=5)
        
        # Progress and Actions
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10, fill="x", padx=10)
        
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=10)
        
        ttk.Button(action_frame, text="🔍 Preview", command=self.show_preview).pack(side="left", padx=5)
        ttk.Button(action_frame, text="⚡ Organize", command=self.organize_files).pack(side="left", padx=5)
        ttk.Button(action_frame, text="⏪ Undo", command=self.undo_last).pack(side="left", padx=5)
        
        self.update_category_tree()
        
    def load_config(self):
        defaults = {
            "categories": {
                "Documents": [".pdf", ".docx", ".txt"],
                "Images": [".jpg", ".png", ".gif"],
                "Audio": [".mp3", ".wav"]
            },
            "default_folder": "Other",
            "move_unmatched": True,
            "exclude_patterns": ["*.tmp", "*.bak"],
            "theme": "light"
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return {**defaults, **json.load(f)}
            except json.JSONDecodeError:
                return defaults
        return defaults
    
    def save_config(self):
        config = {
            "categories": self.config["categories"],
            "default_folder": self.default_folder.get(),
            "move_unmatched": self.move_unmatched.get(),
            "exclude_patterns": [x.strip() for x in self.exclude_entry.get().split(",")],
            "theme": self.current_theme
        }
        with open(self.config_file, "w") as f:
            json.dump(config, f)
    
    def update_category_tree(self):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
        for cat, exts in self.config["categories"].items():
            self.category_tree.insert("", "end", text=cat, values=(", ".join(exts)))
    
    def handle_drop(self, event):
        path = event.data.strip().replace("{", "").replace("}", "")
        if os.path.isdir(path):
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, path)
            self.selected_folder = path
    
    # ... (Other methods for category management, file organization, undo, etc.)
    # Full implementation would include all the discussed features

if __name__ == "__main__":
    app = EnhancedFileOrganizer()
    app.mainloop()
