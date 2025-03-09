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
        self.current_theme = self.config.get("theme", "light")
        self.apply_theme()
        
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
        
        # Add scrollbar to treeview
        tree_scroll = ttk.Scrollbar(cat_frame)
        tree_scroll.pack(side="right", fill="y")
        
        self.category_tree = ttk.Treeview(cat_frame, columns=("Extensions"), show="tree headings", 
                                          yscrollcommand=tree_scroll.set)
        self.category_tree.heading("#0", text="Category")
        self.category_tree.heading("Extensions", text="Extensions")
        self.category_tree.column("#0", width=150)
        self.category_tree.column("Extensions", width=250)
        self.category_tree.pack(side="left", fill="both", expand=True)
        
        tree_scroll.config(command=self.category_tree.yview)
        
        # Bind selection event
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)
        
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
        
        # Status and Log
        log_frame = ttk.LabelFrame(self, text="Activity Log")
        log_frame.pack(pady=10, padx=10, fill="x")
        
        self.log_text = tk.Text(log_frame, height=5, width=70, wrap="word")
        self.log_text.pack(fill="x", padx=5, pady=5)
        self.log_text.config(state="disabled")
        
        # Progress and Actions
        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate")
        self.progress.pack(pady=10, fill="x", padx=10)
        
        action_frame = ttk.Frame(self)
        action_frame.pack(pady=10)
        
        ttk.Button(action_frame, text="🔍 Preview", command=self.show_preview).pack(side="left", padx=5)
        ttk.Button(action_frame, text="⚡ Organize", command=self.organize_files).pack(side="left", padx=5)
        ttk.Button(action_frame, text="⏪ Undo", command=self.undo_last).pack(side="left", padx=5)
        ttk.Button(action_frame, text="💾 Save Settings", command=self.save_config).pack(side="left", padx=5)
        
        self.update_category_tree()
        
    def load_config(self):
        defaults = {
            "categories": {
                "Documents": [".pdf", ".docx", ".txt"],
                "Images": [".jpg", ".png", ".gif"],
                "Audio": [".mp3", ".wav"],
                "Videos": [".mp4", ".avi", ".mov"],
                "Archives": [".zip", ".rar", ".7z"],
                "Code": [".py", ".js", ".html", ".css"]
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
        self.config["default_folder"] = self.default_folder.get()
        self.config["move_unmatched"] = self.move_unmatched.get()
        self.config["exclude_patterns"] = [x.strip() for x in self.exclude_entry.get().split(",") if x.strip()]
        self.config["theme"] = self.current_theme
        
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=2)
        
        self.log_message("Settings saved successfully")
    
    def update_category_tree(self):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
            
        for cat, exts in self.config["categories"].items():
            self.category_tree.insert("", "end", text=cat, values=(", ".join(exts),))
    
    def handle_drop(self, event):
        path = event.data.strip()
        # Remove curly braces that Windows adds when dragging folders
        path = path.replace("{", "").replace("}", "")
        
        if os.path.isdir(path):
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, path)
            self.selected_folder = path
            self.log_message(f"Directory selected: {path}")
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Directory to Organize")
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.selected_folder = folder
            self.log_message(f"Directory selected: {folder}")
    
    def on_category_select(self, event):
        selected = self.category_tree.selection()
        if selected:
            item = selected[0]
            category = self.category_tree.item(item, "text")
            extensions = self.category_tree.item(item, "values")[0]
            
            self.cat_name.delete(0, tk.END)
            self.cat_exts.delete(0, tk.END)
            
            self.cat_name.insert(0, category)
            self.cat_exts.insert(0, extensions)
    
    def save_category(self):
        category = self.cat_name.get().strip()
        extensions_raw = self.cat_exts.get().strip()
        
        if not category:
            messagebox.showerror("Error", "Category name cannot be empty")
            return
            
        if not extensions_raw:
            messagebox.showerror("Error", "Extensions list cannot be empty")
            return
            
        # Process extensions - make sure they all start with a dot
        extensions = []
        for ext in extensions_raw.replace(" ", "").split(","):
            if not ext.startswith("."):
                ext = "." + ext
            extensions.append(ext.lower())
            
        self.config["categories"][category] = extensions
        self.update_category_tree()
        self.log_message(f"Category '{category}' saved with extensions: {', '.join(extensions)}")
    
    def delete_category(self):
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a category to delete")
            return
            
        item = selected[0]
        category = self.category_tree.item(item, "text")
        
        if messagebox.askyesno("Confirm", f"Are you sure you want to delete the category '{category}'?"):
            if category in self.config["categories"]:
                del self.config["categories"][category]
                self.update_category_tree()
                self.log_message(f"Category '{category}' deleted")
    
    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.log_message(f"Switched to {self.current_theme} theme")
    
    def apply_theme(self):
        if self.current_theme == "dark":
            # Dark theme
            self.configure(background="#333333")
            self.style.configure("TLabel", background="#333333", foreground="white")
            self.style.configure("TButton", background="#555555", foreground="white")
            self.style.configure("TEntry", fieldbackground="#444444", foreground="white")
            self.style.configure("TLabelframe", background="#333333", foreground="white")
            self.style.configure("TLabelframe.Label", background="#333333", foreground="white")
            self.style.configure("Treeview", background="#444444", fieldbackground="#444444", foreground="white")
            self.style.map("Treeview", background=[("selected", "#007acc")])
            
            self.log_text.config(bg="#444444", fg="white")
        else:
            # Light theme
            self.configure(background="#f0f0f0")
            self.style.configure("TLabel", background="#f0f0f0", foreground="black")
            self.style.configure("TButton", background="#e0e0e0", foreground="black")
            self.style.configure("TEntry", fieldbackground="white", foreground="black")
            self.style.configure("TLabelframe", background="#f0f0f0", foreground="black")
            self.style.configure("TLabelframe.Label", background="#f0f0f0", foreground="black")
            self.style.configure("Treeview", background="white", fieldbackground="white", foreground="black")
            self.style.map("Treeview", background=[("selected", "#0078d7")])
            
            self.log_text.config(bg="white", fg="black")
    
    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f">> {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state="disabled")
    
    def get_category_for_file(self, filename):
        _, file_ext = os.path.splitext(filename.lower())
        
        for category, extensions in self.config["categories"].items():
            if file_ext in extensions:
                return category
                
        return self.config["default_folder"] if self.move_unmatched.get() else None
    
    def is_excluded(self, filename):
        exclude_patterns = [x.strip() for x in self.exclude_entry.get().split(",") if x.strip()]
        return any(fnmatch.fnmatch(filename, pattern) for pattern in exclude_patterns)
    
    def collect_files(self, directory):
        file_map = {}
        total_files = 0
        
        for root, _, files in os.walk(directory):
            for filename in files:
                if self.is_excluded(filename):
                    continue
                    
                filepath = os.path.join(root, filename)
                category = self.get_category_for_file(filename)
                
                if category:
                    if category not in file_map:
                        file_map[category] = []
                    file_map[category].append(filepath)
                    total_files += 1
                    
        return file_map, total_files
    
    def show_preview(self):
        directory = self.folder_entry.get().strip()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("Error", "Please select a valid directory first")
            return
            
        self.log_message("Scanning files for preview...")
        file_map, total_files = self.collect_files(directory)
        
        if not file_map:
            messagebox.showinfo("Preview", "No files found to organize")
            return
            
        preview_window = tk.Toplevel(self)
        preview_window.title("Organization Preview")
        preview_window.geometry("600x400")
        
        preview_frame = ttk.Frame(preview_window)
        preview_frame.pack(padx=10, pady=10, fill="both", expand=True)
        
        # Create scrollable text widget
        preview_scroll = ttk.Scrollbar(preview_frame)
        preview_scroll.pack(side="right", fill="y")
        
        preview_text = tk.Text(preview_frame, wrap="word", yscrollcommand=preview_scroll.set)
        preview_text.pack(fill="both", expand=True)
        preview_scroll.config(command=preview_text.yview)
        
        # Add preview content
        preview_text.insert(tk.END, f"Found {total_files} files to organize in {len(file_map)} categories:\n\n")
        
        for category, files in file_map.items():
            preview_text.insert(tk.END, f"Category: {category} ({len(files)} files)\n")
            # Show first 5 files as examples
            for i, filepath in enumerate(files[:5]):
                filename = os.path.basename(filepath)
                preview_text.insert(tk.END, f"  - {filename}\n")
            if len(files) > 5:
                preview_text.insert(tk.END, f"  - ... and {len(files) - 5} more files\n")
            preview_text.insert(tk.END, "\n")
            
        preview_text.config(state="disabled")
        self.log_message(f"Preview generated: {total_files} files in {len(file_map)} categories")
    
    def organize_files(self):
        directory = self.folder_entry.get().strip()
        if not directory or not os.path.isdir(directory):
            messagebox.showerror("Error", "Please select a valid directory first")
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to organize the files in this directory?"):
            return
            
        self.log_message("Starting file organization...")
        file_map, total_files = self.collect_files(directory)
        
        if not file_map:
            messagebox.showinfo("Organize", "No files found to organize")
            return
            
        # Prepare for undo
        undo_info = {
            "timestamp": os.path.getmtime(directory),
            "moves": []
        }
        
        # Reset progress bar
        self.progress["value"] = 0
        self.progress["maximum"] = total_files
        processed = 0
        
        for category, files in file_map.items():
            # Create category folder if it doesn't exist
            category_path = os.path.join(directory, category)
            if not os.path.exists(category_path):
                os.makedirs(category_path)
                
            for filepath in files:
                filename = os.path.basename(filepath)
                dest_path = os.path.join(category_path, filename)
                
                # Handle duplicate filenames
                if os.path.exists(dest_path):
                    base, ext = os.path.splitext(filename)
                    counter = 1
                    while os.path.exists(dest_path):
                        new_filename = f"{base}_{counter}{ext}"
                        dest_path = os.path.join(category_path, new_filename)
                        counter += 1
                
                # Move the file
                try:
                    shutil.move(filepath, dest_path)
                    undo_info["moves"].append({"src": dest_path, "dest": filepath})
                    self.log_message(f"Moved: {filename} -> {category}")
                except Exception as e:
                    self.log_message(f"Error moving {filename}: {str(e)}")
                
                # Update progress
                processed += 1
                self.progress["value"] = processed
                self.update_idletasks()
        
        # Add to undo stack
        self.undo_stack.append(undo_info)
        
        # Complete
        self.progress["value"] = 0
        messagebox.showinfo("Complete", f"Successfully organized {processed} files into {len(file_map)} categories")
        self.log_message(f"Organization complete: {processed} files organized")
    
    def undo_last(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo")
            return
            
        if not messagebox.askyesno("Confirm", "Are you sure you want to undo the last organization?"):
            return
            
        undo_info = self.undo_stack.pop()
        moves = undo_info["moves"]
        
        self.log_message("Starting undo operation...")
        self.progress["value"] = 0
        self.progress["maximum"] = len(moves)
        
        success_count = 0
        for i, move in enumerate(moves):
            src = move["src"]
            dest = move["dest"]
            
            # Make sure parent directory exists
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            
            try:
                shutil.move(src, dest)
                success_count += 1
                self.log_message(f"Restored: {os.path.basename(src)} -> {os.path.dirname(dest)}")
            except Exception as e:
                self.log_message(f"Error during undo: {str(e)}")
            
            # Update progress
            self.progress["value"] = i + 1
            self.update_idletasks()
        
        # Clean up empty directories
        directory = self.folder_entry.get().strip()
        if directory and os.path.isdir(directory):
            for category in self.config["categories"].keys():
                category_path = os.path.join(directory, category)
                if os.path.exists(category_path) and not os.listdir(category_path):
                    try:
                        os.rmdir(category_path)
                        self.log_message(f"Removed empty directory: {category}")
                    except:
                        pass
        
        # Complete
        self.progress["value"] = 0
        messagebox.showinfo("Undo Complete", f"Successfully restored {success_count} of {len(moves)} files")
        self.log_message(f"Undo complete: {success_count} files restored")

if __name__ == "__main__":
    app = EnhancedFileOrganizer()
    app.mainloop()
