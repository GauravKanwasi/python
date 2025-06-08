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
        
        # Initialize selected folder
        self.selected_folder = ""
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Folder selection section
        folder_frame = ttk.LabelFrame(self.root, text="Select Folder")
        folder_frame.pack(pady=10, padx=10, fill="x")
        
        self.folder_entry = ttk.Entry(folder_frame, width=50)
        self.folder_entry.pack(side="left", padx=5)
        
        ttk.Button(folder_frame, text="Browse", command=self.select_folder).pack(side="left", padx=5)
        
        # Category management section
        cat_frame = ttk.LabelFrame(self.root, text="Category Management")
        cat_frame.pack(pady=10, padx=10, fill="both", expand=True)
        
        # Category list
        self.category_list = tk.Listbox(cat_frame, selectmode="single")
        self.category_list.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.category_list.bind("<<ListboxSelect>>", self.on_category_select)
        self.update_category_list()
        
        # Category controls
        control_frame = ttk.Frame(cat_frame)
        control_frame.pack(side="right", padx=5, fill="y")
        
        ttk.Label(control_frame, text="Category Name:").pack(anchor="w")
        self.new_cat_name = ttk.Entry(control_frame)
        self.new_cat_name.pack(fill="x", pady=2)
        
        ttk.Label(control_frame, text="Extensions (comma-separated):").pack(anchor="w")
        self.new_cat_exts = ttk.Entry(control_frame)
        self.new_cat_exts.pack(fill="x", pady=2)
        
        ttk.Button(control_frame, text="New Category", command=self.new_category).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="Add Category", command=self.add_category).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="Update Selected", command=self.update_category).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="Remove Selected", command=self.remove_category).pack(fill="x", pady=2)
        
        # Action buttons
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10, fill="x")
        
        self.simulate_var = tk.BooleanVar()
        ttk.Checkbutton(btn_frame, text="Simulate only", variable=self.simulate_var).pack(side="left", padx=5)
        
        ttk.Button(btn_frame, text="Organize Files", command=self.organize_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.update_category_list).pack(side="left", padx=5)
        
    def load_config(self):
        """Load categories from config file or return defaults."""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                messagebox.showwarning("Warning", "Config file corrupted. Using defaults.")
        return {
            "Documents": [".pdf", ".docx", ".txt"],
            "Images": [".jpg", ".png", ".gif"],
            "Audio": [".mp3", ".wav"],
            "Other": []
        }
    
    def save_config(self):
        """Save categories to config file."""
        with open(self.config_file, "w") as f:
            json.dump(self.categories, f, indent=4)
    
    def select_folder(self):
        """Open folder selection dialog."""
        self.selected_folder = filedialog.askdirectory()
        if self.selected_folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, self.selected_folder)
    
    def update_category_list(self):
        """Refresh the category list display."""
        self.category_list.delete(0, tk.END)
        for category in sorted(self.categories.keys()):
            exts = ", ".join(self.categories[category]) if self.categories[category] else "None"
            self.category_list.insert(tk.END, f"{category} ({exts})")
    
    def on_category_select(self, event):
        """Populate input fields when a category is selected."""
        selection = self.category_list.curselection()
        if selection:
            selected = self.category_list.get(selection[0])
            category = selected.split(" (")[0]
            self.new_cat_name.delete(0, tk.END)
            self.new_cat_name.insert(0, category)
            exts = ", ".join(self.categories[category])
            self.new_cat_exts.delete(0, tk.END)
            self.new_cat_exts.insert(0, exts)
    
    def new_category(self):
        """Clear fields for adding a new category."""
        self.new_cat_name.delete(0, tk.END)
        self.new_cat_exts.delete(0, tk.END)
        self.category_list.selection_clear(0, tk.END)
    
    def add_category(self):
        """Add a new category with validated inputs."""
        name = self.new_cat_name.get().strip()
        exts = [e.strip().lower() for e in self.new_cat_exts.get().split(",") if e.strip()]
        
        invalid_exts = [ext for ext in exts if not ext.startswith(".")]
        if invalid_exts:
            messagebox.showerror("Error", f"Invalid extensions: {', '.join(invalid_exts)}. Must start with a dot.")
            return
        
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
    
    def update_category(self):
        """Update the selected category's name and extensions."""
        selection = self.category_list.curselection()
        if not selection:
            messagebox.showerror("Error", "No category selected!")
            return
            
        selected = self.category_list.get(selection[0])
        old_category = selected.split(" (")[0]
        
        if old_category == "Other":
            messagebox.showerror("Error", "Cannot update 'Other' category!")
            return
            
        new_name = self.new_cat_name.get().strip()
        new_exts = [e.strip().lower() for e in self.new_cat_exts.get().split(",") if e.strip()]
        
        invalid_exts = [ext for ext in new_exts if not ext.startswith(".")]
        if invalid_exts:
            messagebox.showerror("Error", f"Invalid extensions: {', '.join(invalid_exts)}. Must start with a dot.")
            return
        
        if not new_name:
            messagebox.showerror("Error", "Category name cannot be empty!")
            return
            
        if new_name != old_category and new_name in self.categories:
            messagebox.showerror("Error", "Category name already exists!")
            return
            
        self.categories[new_name] = new_exts
        if new_name != old_category:
            del self.categories[old_category]
        self.save_config()
        self.update_category_list()
        self.new_cat_name.delete(0, tk.END)
        self.new_cat_exts.delete(0, tk.END)
    
    def remove_category(self):
        """Remove the selected category, except 'Other'."""
        selection = self.category_list.curselection()
        if not selection:
            messagebox.showinfo("Info", "No category selected to remove.")
            return
            
        selected = self.category_list.get(selection[0])
        category = selected.split(" (")[0]
        
        if category == "Other":
            messagebox.showerror("Error", "Cannot delete 'Other' category!")
            return
            
        del self.categories[category]
        self.save_config()
        self.update_category_list()
    
    def organize_files(self):
        """Organize files into category folders, with simulation option."""
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return
            
        target_dir = Path(self.selected_folder)
        simulate = self.simulate_var.get()
        
        if simulate:
            category_counts = {cat: 0 for cat in self.categories}
            for item in target_dir.iterdir():
                if item.is_file():
                    dest_category = "Other"
                    file_ext = item.suffix.lower()
                    for category, exts in self.categories.items():
                        if file_ext in exts:
                            dest_category = category
                            break
                    category_counts[dest_category] += 1
            summary = "\n".join([f"Would move {count} files to {cat}" for cat, count in category_counts.items() if count > 0])
            messagebox.showinfo("Simulation", summary or "No files would be moved.")
        else:
            report = {"moved": 0, "errors": 0}
            errors = []
            self.root.config(cursor="wait")
            self.root.update()  # Ensure cursor updates
            
            try:
                for category in self.categories:
                    (target_dir / category).mkdir(exist_ok=True)
                
                for item in target_dir.iterdir():
                    if item.is_file():
                        dest_category = "Other"
                        file_ext = item.suffix.lower()
                        for category, exts in self.categories.items():
                            if file_ext in exts:
                                dest_category = category
                                break
                        dest_path = target_dir / dest_category / item.name
                        if dest_path.exists():
                            stem = item.stem
                            suffix = item.suffix
                            counter = 1
                            while (target_dir / dest_category / f"{stem}_{counter}{suffix}").exists():
                                counter += 1
                            dest_path = target_dir / dest_category / f"{stem}_{counter}{suffix}"
                        try:
                            shutil.move(str(item), str(dest_path))
                            report["moved"] += 1
                        except Exception as e:
                            report["errors"] += 1
                            errors.append(f"Error moving {item.name}: {str(e)}")
            except Exception as e:
                messagebox.showerror("Error", f"Fatal error: {str(e)}")
            finally:
                self.root.config(cursor="")
            
            if errors:
                error_msg = "\n".join(errors[:5])
                if len(errors) > 5:
                    error_msg += f"\n... and {len(errors) - 5} more errors."
                messagebox.showerror("Errors", f"Encountered {report['errors']} errors:\n{error_msg}")
            else:
                messagebox.showinfo("Success", f"Moved {report['moved']} files successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileOrganizerApp(root)
    root.mainloop()
