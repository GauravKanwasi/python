import os
import json
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("800x600")
        
        # Configuration file
        self.config_file = Path.home() / ".file_organizer_config.json"
        self.categories = self.load_config()
        
        # Create GUI elements
        self.create_widgets()
        self.selected_folder = ""
        
    def create_widgets(self):
        # Folder selection section
        folder_frame = ttk.LabelFrame(self.root, text="Select Folder")
        folder_frame.pack(pady=10, padx=10, fill="x")
        
        self.folder_entry = ttk.Entry(folder_frame, width=50)
        self.folder_entry.pack(side="left", padx=5)
        
        ttk.Button(
            folder_frame, 
            text="Browse", 
            command=self.select_folder
        ).pack(side="left", padx=5)
        
        # Category management section
        cat_frame = ttk.LabelFrame(self.root, text="Category Management")
        cat_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Category list
        self.category_list = tk.Listbox(cat_frame, selectmode="single")
        self.category_list.pack(side="left", fill="both", expand=True)
        self.update_category_list()
        
        # Category controls
        control_frame = ttk.Frame(cat_frame)
        control_frame.pack(side="right", padx=5)
        
        ttk.Label(control_frame, text="Category Name:").pack(anchor="w")
        self.new_cat_name = ttk.Entry(control_frame)
        self.new_cat_name.pack(fill="x", pady=2)
        
        ttk.Label(control_frame, text="File Extensions (comma-separated):").pack(anchor="w")
        self.new_cat_exts = ttk.Entry(control_frame)
        self.new_cat_exts.pack(fill="x", pady=2)
        
        ttk.Button(
            control_frame,
            text="Add Category",
            command=self.add_category
        ).pack(fill="x", pady=5)
        
        ttk.Button(
            control_frame,
            text="Remove Selected",
            command=self.remove_category
        ).pack(fill="x", pady=5)
        
        # Action buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10, fill="x")
        
        ttk.Button(
            btn_frame,
            text="Organize Files",
            command=self.organize_files
        ).pack(side="left", padx=5)
        
        ttk.Button(
            btn_frame,
            text="Refresh",
            command=self.update_category_list
        ).pack(side="left", padx=5)
        
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {
            "Documents": [".pdf", ".docx", ".txt"],
            "Images": [".jpg", ".png", ".gif"],
            "Audio": [".mp3", ".wav"],
            "Other": []
        }
    
    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.categories, f)
    
    def select_folder(self):
        self.selected_folder = filedialog.askdirectory()
        self.folder_entry.delete(0, tk.END)
        self.folder_entry.insert(0, self.selected_folder)
    
    def update_category_list(self):
        self.category_list.delete(0, tk.END)
        for category in self.categories:
            exts = ", ".join(self.categories[category])
            self.category_list.insert(tk.END, f"{category} ({exts})")
    
    def add_category(self):
        name = self.new_cat_name.get().strip()
        exts = [e.strip().lower() for e in self.new_cat_exts.get().split(",")]
        
        if not name:
            messagebox.showerror("Error", "Category name cannot be empty!")
            return
            
        if name in self.categories:
            messagebox.showerror("Error", "Category already exists!")
            return
            
        self.categories[name] = exts
        self.save_config()
        self.update_category_list()
        self.new_cat_name.delete(0, tk.END)
        self.new_cat_exts.delete(0, tk.END)
    
    def remove_category(self):
        selection = self.category_list.curselection()
        if not selection:
            return
            
        selected = self.category_list.get(selection[0])
        category = selected.split(" ")[0]
        
        if category == "Other":
            messagebox.showerror("Error", "Cannot delete 'Other' category")
            return
            
        del self.categories[category]
        self.save_config()
        self.update_category_list()
    
    def organize_files(self):
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
            
        target_dir = Path(self.selected_folder)
        report = {"moved": 0, "errors": 0}
        
        try:
            # Create category directories
            for category in self.categories:
                (target_dir / category).mkdir(exist_ok=True)
            
            # Process files
            for item in target_dir.iterdir():
                if item.is_file():
                    dest_category = "Other"
                    file_ext = item.suffix.lower()
                    
                    for category, exts in self.categories.items():
                        if file_ext in exts:
                            dest_category = category
                            break
                            
                    dest_path = target_dir / dest_category / item.name
                    try:
                        shutil.move(str(item), str(dest_path))
                        report["moved"] += 1
                    except Exception as e:
                        report["errors"] += 1
            
            messagebox.showinfo(
                "Organization Complete",
                f"Files organized successfully!\n\n"
                f"Moved files: {report['moved']}\n"
                f"Errors: {report['errors']}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
