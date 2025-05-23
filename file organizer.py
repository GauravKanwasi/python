import os
import json
import shutil
import fnmatch
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_FILES
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import time
import queue

class EnhancedFileOrganizer(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Smart File Organizer Pro")
        self.geometry("1200x900")
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Configuration
        self.config_file = Path.home() / ".smart_organizer_config.json"
        self.config = self.load_config()
        self.undo_stack = []
        self.redo_stack = []
        self.monitor_thread = None
        self.monitor_queue = queue.Queue()
        self.is_monitoring = False
        
        # UI Setup
        self.create_widgets()
        self.selected_folder = ""
        self.current_theme = self.config.get("theme", "light")
        self.apply_theme()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def create_widgets(self):
        # Main container
        main_frame = ttk.PanedWindow(self, orient="vertical")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top frame: Folder and monitoring controls
        top_frame = ttk.LabelFrame(main_frame, text="Directory Control")
        main_frame.add(top_frame, weight=1)
        
        # Folder selection
        folder_frame = ttk.Frame(top_frame)
        folder_frame.pack(fill="x", pady=5)
        
        self.folder_entry = ttk.Entry(folder_frame, width=60)
        self.folder_entry.pack(side="left", padx=5, fill="x", expand=True)
        self.folder_entry.drop_target_register(DND_FILES)
        self.folder_entry.dnd_bind('<<Drop>>', self.handle_drop)
        
        ttk.Button(folder_frame, text="📁 Browse", command=self.select_folder).pack(side="left", padx=5)
        self.monitor_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(folder_frame, text="🔄 Monitor Directory", variable=self.monitor_var, 
                       command=self.toggle_monitoring).pack(side="left", padx=5)
        
        # Search and filter
        search_frame = ttk.Frame(top_frame)
        search_frame.pack(fill="x", pady=5)
        ttk.Label(search_frame, text="Search Files:").pack(side="left")
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_files)
        
        # Exclusion patterns
        ttk.Label(top_frame, text="Exclude Patterns (comma-separated):").pack(anchor="w", padx=5)
        self.exclude_entry = ttk.Entry(top_frame)
        self.exclude_entry.pack(fill="x", padx=5, pady=2)
        self.exclude_entry.insert(0, ",".join(self.config["exclude_patterns"]))
        
        # Category Management
        cat_frame = ttk.LabelFrame(main_frame, text="File Categories")
        main_frame.add(cat_frame, weight=2)
        
        # Category tree with scrollbar
        tree_frame = ttk.Frame(cat_frame)
        tree_frame.pack(fill="both", expand=True, padx=5)
        
        self.category_tree = ttk.Treeview(tree_frame, columns=("Extensions", "Count"), 
                                        show="tree headings")
        self.category_tree.heading("#0", text="Category")
        self.category_tree.heading("Extensions", text="Extensions")
        self.category_tree.heading("Count", text="Files")
        self.category_tree.column("#0", width=200)
        self.category_tree.column("Extensions", width=300)
        self.category_tree.column("Count", width=100)
        self.category_tree.pack(side="left", fill="both", expand=True)
        
        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=self.category_tree.yview)
        tree_scroll.pack(side="right", fill="y")
        self.category_tree.configure(yscrollcommand=tree_scroll.set)
        
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)
        self.category_tree.bind("<Double-1>", self.open_category_folder)
        
        # Category controls
        control_frame = ttk.Frame(cat_frame)
        control_frame.pack(side="right", padx=5)
        
        ttk.Label(control_frame, text="Category Name:").pack(anchor="w")
        self.cat_name = ttk.Entry(control_frame)
        self.cat_name.pack(fill="x", pady=2)
        
        ttk.Label(control_frame, text="Extensions (comma-separated):").pack(anchor="w")
        self.cat_exts = ttk.Entry(control_frame)
        self.cat_exts.pack(fill="x", pady=2)
        
        ttk.Button(control_frame, text="➕ Add/Update", command=self.save_category).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="🗑️ Delete", command=self.delete_category).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="📋 Import", command=self.import_categories).pack(fill="x", pady=2)
        ttk.Button(control_frame, text="📤 Export", command=self.export_categories).pack(fill="x", pady=2)
        
        # Unmatched files settings
        default_frame = ttk.LabelFrame(top_frame, text="Unmatched Files")
        default_frame.pack(fill="x", pady=5)
        
        ttk.Label(default_frame, text="Folder Name:").pack(side="left")
        self.default_folder = ttk.Entry(default_frame, width=20)
        self.default_folder.pack(side="left", padx=5)
        self.default_folder.insert(0, self.config["default_folder"])
        
        self.move_unmatched = tk.BooleanVar(value=self.config["move_unmatched"])
        ttk.Checkbutton(default_frame, text="Move Unmatched", variable=self.move_unmatched).pack(side="left", padx=5)
        
        # Log and status
        log_frame = ttk.LabelFrame(main_frame, text="Activity Log")
        main_frame.add(log_frame, weight=1)
        
        self.log_text = tk.Text(log_frame, height=8, wrap="word")
        self.log_text.pack(fill="both", padx=5, pady=5, expand=True)
        self.log_text.config(state="disabled")
        
        # Progress and actions
        action_frame = ttk.Frame(self)
        action_frame.pack(fill="x", pady=10)
        
        ttk.Button(action_frame, text="🌓 Theme", command=self.toggle_theme).pack(side="left", padx=5)
        ttk.Button(action_frame, text="🔍 Preview", command=self.show_preview).pack(side="left", padx=5)
        ttk.Button(action_frame, text="⚡ Organize", command=self.organize_files).pack(side="left", padx=5)
        ttk.Button(action_frame, text="⏪ Undo", command=self.undo_last).pack(side="left", padx=5)
        ttk.Button(action_frame, text="⏩ Redo", command=self.redo_last).pack(side="left", padx=5)
        ttk.Button(action_frame, text="💾 Save", command=self.save_config).pack(side="left", padx=5)
        
        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)
        
        self.update_category_tree()
        self.after(100, self.check_monitor_queue)

    def load_config(self):
        defaults = {
            "categories": {
                "Documents": [".pdf", ".docx", ".txt", ".doc"],
                "Images": [".jpg", ".png", ".gif", ".jpeg", ".bmp"],
                "Audio": [".mp3", ".wav", ".flac", ".aac"],
                "Videos": [".mp4", ".avi", ".mov", ".mkv"],
                "Archives": [".zip", ".rar", ".7z", ".tar"],
                "Code": [".py", ".js", ".html", ".css", ".java"],
                "Executables": [".exe", ".msi", ".bat"]
            },
            "default_folder": "Other",
            "move_unmatched": True,
            "exclude_patterns": ["*.tmp", "*.bak", "*.log", "desktop.ini"],
            "theme": "light",
            "recent_folders": []
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                    return {**defaults, **config, "categories": {**defaults["categories"], **config.get("categories", {})}}
            except json.JSONDecodeError:
                return defaults
        return defaults

    def save_config(self):
        self.config["default_folder"] = self.default_folder.get()
        self.config["move_unmatched"] = self.move_unmatched.get()
        self.config["exclude_patterns"] = [x.strip() for x in self.exclude_entry.get().split(",") if x.strip()]
        self.config["theme"] = self.current_theme
        
        if self.selected_folder and self.selected_folder not in self.config["recent_folders"]:
            self.config["recent_folders"].append(self.selected_folder)
            if len(self.config["recent_folders"]) > 5:
                self.config["recent_folders"].pop(0)
                
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=2)
            self.log_message("Settings saved successfully")
        except Exception as e:
            self.log_message(f"Error saving settings: {str(e)}")

    def import_categories(self):
        file = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file:
            try:
                with open(file, "r") as f:
                    imported = json.load(f)
                    if isinstance(imported, dict) and "categories" in imported:
                        self.config["categories"].update(imported["categories"])
                        self.update_category_tree()
                        self.log_message(f"Imported categories from {file}")
                    else:
                        messagebox.showerror("Error", "Invalid categories file format")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import categories: {str(e)}")

    def export_categories(self):
        file = filedialog.asksaveasfilename(defaultextension=".json", 
                                          filetypes=[("JSON files", "*.json")])
        if file:
            try:
                with open(file, "w") as f:
                    json.dump({"categories": self.config["categories"]}, f, indent=2)
                self.log_message(f"Exported categories to {file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export categories: {str(e)}")

    def toggle_theme(self):
        self.current_theme = "dark" if self.current_theme == "light" else "light"
        self.apply_theme()
        self.log_message(f"Switched to {self.current_theme} theme")

    def apply_theme(self):
        if self.current_theme == "dark":
            self.configure(background="#2b2b2b")
            self.style.configure("TLabel", background="#2b2b2b", foreground="#ffffff")
            self.style.configure("TButton", background="#3c3f41", foreground="#ffffff")
            self.style.configure("TEntry", fieldbackground="#3c3f41", foreground="#ffffff")
            self.style.configure("TLabelframe", background="#2b2b2b", foreground="#ffffff")
            self.style.configure("TLabelframe.Label", background="#2b2b2b", foreground="#ffffff")
            self.style.configure("Treeview", background="#3c3f41", fieldbackground="#3c3f41", foreground="#ffffff")
            self.style.map("Treeview", background=[("selected", "#0078d4")])
            self.log_text.config(bg="#3c3f41", fg="#ffffff")
        else:
            self.configure(background="#ffffff")
            self.style.configure("TLabel", background="#ffffff", foreground="#000000")
            self.style.configure("TButton", background="#f0f0f0", foreground="#000000")
            self.style.configure("TEntry", fieldbackground="#ffffff", foreground="#000000")
            self.style.configure("TLabelframe", background="#ffffff", foreground="#000000")
            self.style.configure("TLabelframe.Label", background="#ffffff", foreground="#000000")
            self.style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="#000000")
            self.style.map("Treeview", background=[("selected", "#0078d4")])
            self.log_text.config(bg="#ffffff", fg="#000000")

    def handle_drop(self, event):
        path = event.data.strip().replace("{", "").replace("}", "")
        if os.path.isdir(path):
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, path)
            self.selected_folder = path
            self.log_message(f"Directory selected: {path}")
            self.update_category_tree()

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select Directory to Organize")
        if folder:
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)
            self.selected_folder = folder
            self.log_message(f"Directory selected: {folder}")
            self.update_category_tree()

    def open_category_folder(self, event):
        selected = self.category_tree.selection()
        if selected and self.selected_folder:
            item = selected[0]
            category = self.category_tree.item(item, "text")
            folder_path = os.path.join(self.selected_folder, category)
            if os.path.exists(folder_path):
                try:
                    os.startfile(folder_path) if os.name == 'nt' else os.system(f"open '{folder_path}'")
                except Exception as e:
                    self.log_message(f"Error opening folder {category}: {str(e)}")

    def save_category(self):
        category = self.cat_name.get().strip()
        extensions_raw = self.cat_exts.get().strip()
        
        if not category or not extensions_raw:
            messagebox.showerror("Error", "Category name and extensions cannot be empty")
            return
            
        extensions = [f".{ext.strip().lstrip('.')}" for ext in extensions_raw.split(",") if ext.strip()]
        self.config["categories"][category] = extensions
        self.update_category_tree()
        self.log_message(f"Category '{category}' saved with extensions: {', '.join(extensions)}")
        self.save_config()

    def delete_category(self):
        selected = self.category_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a category to delete")
            return
            
        item = selected[0]
        category = self.category_tree.item(item, "text")
        
        if messagebox.askyesno("Confirm", f"Delete category '{category}'?"):
            del self.config["categories"][category]
            self.update_category_tree()
            self.log_message(f"Category '{category}' deleted")
            self.save_config()

    def log_message(self, message):
        self.log_text.config(state="normal")
        self.log_text.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
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
        return any(fnmatch.fnmatch(filename.lower(), pattern.lower()) for pattern in exclude_patterns)

    def collect_files(self, directory):
        file_map = {cat: [] for cat in self.config["categories"]}
        file_map[self.config["default_folder"]] = []
        total_files = 0
        
        for root, _, files in os.walk(directory):
            if root == directory:  # Only process files in the root directory
                for filename in files:
                    if self.is_excluded(filename):
                        continue
                    filepath = os.path.join(root, filename)
                    category = self.get_category_for_file(filename)
                    if category:
                        file_map[category].append(filepath)
                        total_files += 1
                        
        return file_map, total_files

    def search_files(self, event=None):
        search_term = self.search_entry.get().lower()
        self.update_category_tree(search_term)

    def update_category_tree(self, search_term=""):
        for item in self.category_tree.get_children():
            self.category_tree.delete(item)
            
        if self.selected_folder:
            file_map, _ = self.collect_files(self.selected_folder)
            
        for cat, exts in self.config["categories"].items():
            count = len(file_map.get(cat, [])) if self.selected_folder else 0
            if not search_term or search_term in cat.lower() or any(search_term in ext.lower() for ext in exts):
                self.category_tree.insert("", "end", text=cat, 
                                       values=(", ".join(exts), count if self.selected_folder else "-"))

    def show_preview(self):
        if not self.selected_folder or not os.path.isdir(self.selected_folder):
            messagebox.showerror("Error", "Please select a valid directory")
            return
            
        self.log_message("Generating preview...")
        file_map, total_files = self.collect_files(self.selected_folder)
        
        if not total_files:
            messagebox.showinfo("Preview", "No files found to organize")
            return
            
        preview_window = tk.Toplevel(self)
        preview_window.title("Organization Preview")
        preview_window.geometry("800x600")
        
        tree_frame = ttk.Frame(preview_window)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        preview_tree = ttk.Treeview(tree_frame, columns=("File", "Size"), show="tree headings")
        preview_tree.heading("#0", text="Category")
        preview_tree.heading("File", text="File Name")
        preview_tree.heading("Size", text="Size")
        preview_tree.column("#0", width=200)
        preview_tree.column("File", width=300)
        preview_tree.column("Size", width=100)
        
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=preview_tree.yview)
        scroll.pack(side="right", fill="y")
        preview_tree.configure(yscrollcommand=scroll.set)
        preview_tree.pack(fill="both", expand=True)
        
        for category, files in file_map.items():
            if files:
                cat_id = preview_tree.insert("", "end", text=category, open=True)
                for filepath in files:
                    filename = os.path.basename(filepath)
                    size = f"{os.path.getsize(filepath)/1024:.1f} KB"
                    preview_tree.insert(cat_id, "end", text="", values=(filename, size))
        
        ttk.Button(preview_window, text="Organize Now", 
                  command=lambda: [preview_window.destroy(), self.organize_files()]).pack(pady=5)
        
        self.log_message(f"Preview: {total_files} files in {len([c for c in file_map if file_map[c]])} categories")

    def organize_files(self):
        if not self.selected_folder or not os.path.isdir(self.selected_folder):
            messagebox.showerror("Error", "Please select a valid directory")
            return
            
        if not messagebox.askyesno("Confirm", "Organize files in this directory?"):
            return
            
        self.redo_stack.clear()
        self.log_message("Starting file organization...")
        file_map, total_files = self.collect_files(self.selected_folder)
        
        if not total_files:
            messagebox.showinfo("Organize", "No files to organize")
            return
            
        undo_info = {"timestamp": time.time(), "moves": []}
        self.progress["maximum"] = total_files
        processed = 0
        
        for category, files in file_map.items():
            if not files:
                continue
            category_path = os.path.join(self.selected_folder, category)
            os.makedirs(category_path, exist_ok=True)
            
            for filepath in files:
                filename = os.path.basename(filepath)
                dest_path = os.path.join(category_path, filename)
                
                # Handle duplicates
                base, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(dest_path):
                    new_filename = f"{base}_{counter}{ext}"
                    dest_path = os.path.join(category_path, new_filename)
                    counter += 1
                
                try:
                    shutil.move(filepath, dest_path)
                    undo_info["moves"].append({"src": dest_path, "dest": filepath})
                    self.log_message(f"Moved: {filename} -> {category}")
                except Exception as e:
                    self.log_message(f"Error moving {filename}: {str(e)}")
                
                processed += 1
                self.progress["value"] = processed
                self.update_idletasks()
        
        self.undo_stack.append(undo_info)
        self.progress["value"] = 0
        self.update_category_tree()
        messagebox.showinfo("Complete", f"Organized {processed} files into {len([c for c in file_map if file_map[c]])} categories")
        self.log_message(f"Organization complete: {processed} files")

    def undo_last(self):
        if not self.undo_stack:
            messagebox.showinfo("Undo", "Nothing to undo")
            return
            
        if not messagebox.askyesno("Confirm", "Undo last organization?"):
            return
            
        undo_info = self.undo_stack.pop()
        redo_info = {"timestamp": time.time(), "moves": []}
        moves = undo_info["moves"]
        
        self.progress["maximum"] = len(moves)
        success_count = 0
        
        for i, move in enumerate(moves):
            src, dest = move["src"], move["dest"]
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(src, dest)
                redo_info["moves"].append({"src": dest, "dest": src})
                self.log_message(f"Restored: {os.path.basename(src)} -> {os.path.dirname(dest)}")
                success_count += 1
            except Exception as e:
                self.log_message(f"Undo error: {str(e)}")
                
            self.progress["value"] = i + 1
            self.update_idletasks()
        
        self.redo_stack.append(redo_info)
        self.cleanup_empty_dirs()
        self.progress["value"] = 0
        self.update_category_tree()
        messagebox.showinfo("Undo Complete", f"Restored {success_count} of {len(moves)} files")
        self.log_message(f"Undo complete: {success_count} files restored")

    def redo_last(self):
        if not self.redo_stack:
            messagebox.showinfo("Redo", "Nothing to redo")
            return
            
        if not messagebox.askyesno("Confirm", "Redo last operation?"):
            return
            
        redo_info = self.redo_stack.pop()
        undo_info = {"timestamp": time.time(), "moves": []}
        moves = redo_info["moves"]
        
        self.progress["maximum"] = len(moves)
        success_count = 0
        
        for i, move in enumerate(moves):
            src, dest = move["src"], move["dest"]
            try:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.move(src, dest)
                undo_info["moves"].append({"src": dest, "dest": src})
                self.log_message(f"Redone: {os.path.basename(src)} -> {os.path.dirname(dest)}")
                success_count += 1
            except Exception as e:
                self.log_message(f"Redo error: {str(e)}")
                
            self.progress["value"] = i + 1
            self.update_idletasks()
        
        self.undo_stack.append(undo_info)
        self.cleanup_empty_dirs()
        self.progress["value"] = 0
        self.update_category_tree()
        messagebox.showinfo("Redo Complete", f"Redone {success_count} of {len(moves)} files")
        self.log_message(f"Redo complete: {success_count} files")

    def cleanup_empty_dirs(self):
        if not self.selected_folder:
            return
        for category in list(self.config["categories"].keys()) + [self.config["default_folder"]]:
            path = os.path.join(self.selected_folder, category)
            if os.path.exists(path) and not os.listdir(path):
                try:
                    os.rmdir(path)
                    self.log_message(f"Removed empty directory: {category}")
                except:
                    pass

    def toggle_monitoring(self):
        if self.monitor_var.get():
            if not self.selected_folder or not os.path.isdir(self.selected_folder):
                messagebox.showerror("Error", "Select a valid directory to monitor")
                self.monitor_var.set(False)
                return
            self.start_monitoring()
        else:
            self.stop_monitoring()

    def start_monitoring(self):
        self.is_monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_directory, daemon=True)
        self.monitor_thread.start()
        self.log_message("Started directory monitoring")

    def stop_monitoring(self):
        self.is_monitoring = False
        if self.monitor_thread:
            self.monitor_thread = None
        self.log_message("Stopped directory monitoring")

    def monitor_directory(self):
        class FileEventHandler(FileSystemEventHandler):
            def __init__(self, queue, organizer):
                super().__init__()
                self.queue = queue
                self.organizer = organizer

            def on_created(self, event):
                if not event.is_directory:
                    self.queue.put(("created", event.src_path))

        observer = Observer()
        observer.schedule(FileEventHandler(self.monitor_queue, self), self.selected_folder, recursive=False)
        observer.start()
        
        try:
            while self.is_monitoring:
                time.sleep(1)
        finally:
            observer.stop()
            observer.join()

    def check_monitor_queue(self):
        try:
            while True:
                event_type, path = self.monitor_queue.get_nowait()
                if event_type == "created" and os.path.isfile(path):
                    category = self.get_category_for_file(os.path.basename(path))
                    if category and not self.is_excluded(os.path.basename(path)):
                        dest_path = os.path.join(self.selected_folder, category, os.path.basename(path))
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        try:
                            shutil.move(path, dest_path)
                            self.log_message(f"Auto-organized: {os.path.basename(path)} -> {category}")
                            self.update_category_tree()
                        except Exception as e:
                            self.log_message(f"Auto-organize error: {str(e)}")
        except queue.Empty:
            pass
        finally:
            self.after(100, self.check_monitor_queue)

    def on_closing(self):
        self.stop_monitoring()
        self.save_config()
        self.destroy()

    def on_category_select(self, event):
        selected = self.category_tree.selection()
        if selected:
            item = selected[0]
            category = self.category_tree.item(item, "text")
            extensions = self.config["categories"].get(category, [])
            self.cat_name.delete(0, tk.END)
            self.cat_name.insert(0, category)
            self.cat_exts.delete(0, tk.END)
            self.cat_exts.insert(0, ", ".join(extensions))

if __name__ == "__main__":
    app = EnhancedFileOrganizer()
    app.mainloop()
