import os
import json
import shutil
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path

DEFAULT_CATEGORIES = {
    "Documents": [".pdf", ".docx", ".txt"],
    "Images": [".jpg", ".png", ".gif"],
    "Audio": [".mp3", ".wav"],
    "Other": []
}

class FileOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Organizer")
        self.root.geometry("800x600")
        self.config_file = Path.home() / ".file_organizer_config.json"
        self.categories = self.load_config()
        self.selected_folder = ""
        self.create_widgets()

    def create_widgets(self):
        folder_frame = ttk.LabelFrame(self.root, text="Select Folder")
        folder_frame.pack(pady=10, padx=10, fill="x")
        self.folder_entry = ttk.Entry(folder_frame, width=50)
        self.folder_entry.pack(side="left", padx=5)
        ttk.Button(folder_frame, text="Browse", command=self.select_folder).pack(side="left", padx=5)

        cat_frame = ttk.LabelFrame(self.root, text="Category Management")
        cat_frame.pack(pady=10, padx=10, fill="both", expand=True)
        self.category_list = tk.Listbox(cat_frame, selectmode="single")
        self.category_list.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.category_list.bind("<<ListboxSelect>>", self.on_category_select)
        self.update_category_list()

        control_frame = ttk.Frame(cat_frame)
        control_frame.pack(side="right", padx=5, fill="y")
        ttk.Label(control_frame, text="Category Name:").pack(anchor="w")
        self.new_cat_name = ttk.Entry(control_frame)
        self.new_cat_name.pack(fill="x", pady=2)
        ttk.Label(control_frame, text="Extensions (comma-separated):").pack(anchor="w")
        self.new_cat_exts = ttk.Entry(control_frame)
        self.new_cat_exts.pack(fill="x", pady=2)
        for text, cmd in [
            ("New Category", self.new_category),
            ("Add Category", self.add_category),
            ("Update Selected", self.update_category),
            ("Remove Selected", self.remove_category),
        ]:
            ttk.Button(control_frame, text=text, command=cmd).pack(fill="x", pady=2)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(pady=10, fill="x")
        self.simulate_var = tk.BooleanVar()
        ttk.Checkbutton(btn_frame, text="Simulate only", variable=self.simulate_var).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Organize Files", command=self.organize_files).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Refresh", command=self.update_category_list).pack(side="left", padx=5)

    def load_config(self):
        if self.config_file.exists():
            try:
                return json.loads(self.config_file.read_text())
            except json.JSONDecodeError:
                messagebox.showwarning("Warning", "Config file corrupted. Using defaults.")
        return DEFAULT_CATEGORIES.copy()

    def save_config(self):
        self.config_file.write_text(json.dumps(self.categories, indent=4))

    def select_folder(self):
        if folder := filedialog.askdirectory():
            self.selected_folder = folder
            self.folder_entry.delete(0, tk.END)
            self.folder_entry.insert(0, folder)

    def update_category_list(self):
        self.category_list.delete(0, tk.END)
        for category in sorted(self.categories):
            exts = ", ".join(self.categories[category]) or "None"
            self.category_list.insert(tk.END, f"{category} ({exts})")

    def on_category_select(self, event):
        if selection := self.category_list.curselection():
            category = self.category_list.get(selection[0]).split(" (")[0]
            self.new_cat_name.delete(0, tk.END)
            self.new_cat_name.insert(0, category)
            self.new_cat_exts.delete(0, tk.END)
            self.new_cat_exts.insert(0, ", ".join(self.categories[category]))

    def new_category(self):
        self.new_cat_name.delete(0, tk.END)
        self.new_cat_exts.delete(0, tk.END)
        self.category_list.selection_clear(0, tk.END)

    def _parse_inputs(self):
        name = self.new_cat_name.get().strip()
        exts = [e.strip().lower() for e in self.new_cat_exts.get().split(",") if e.strip()]
        invalid = [e for e in exts if not e.startswith(".")]
        if invalid:
            messagebox.showerror("Error", f"Invalid extensions: {', '.join(invalid)}. Must start with a dot.")
            return None, None
        if not name:
            messagebox.showerror("Error", "Category name cannot be empty!")
            return None, None
        return name, exts

    def _clear_inputs(self):
        self.new_cat_name.delete(0, tk.END)
        self.new_cat_exts.delete(0, tk.END)

    def add_category(self):
        name, exts = self._parse_inputs()
        if name is None:
            return
        if name in self.categories:
            messagebox.showerror("Error", "Category already exists!")
            return
        self.categories[name] = exts
        self.save_config()
        self.update_category_list()
        self._clear_inputs()

    def update_category(self):
        if not (selection := self.category_list.curselection()):
            messagebox.showerror("Error", "No category selected!")
            return
        old_name = self.category_list.get(selection[0]).split(" (")[0]
        if old_name == "Other":
            messagebox.showerror("Error", "Cannot update 'Other' category!")
            return
        new_name, new_exts = self._parse_inputs()
        if new_name is None:
            return
        if new_name != old_name and new_name in self.categories:
            messagebox.showerror("Error", "Category name already exists!")
            return
        if new_name != old_name:
            del self.categories[old_name]
        self.categories[new_name] = new_exts
        self.save_config()
        self.update_category_list()
        self._clear_inputs()

    def remove_category(self):
        if not (selection := self.category_list.curselection()):
            messagebox.showinfo("Info", "No category selected to remove.")
            return
        category = self.category_list.get(selection[0]).split(" (")[0]
        if category == "Other":
            messagebox.showerror("Error", "Cannot delete 'Other' category!")
            return
        del self.categories[category]
        self.save_config()
        self.update_category_list()

    def _categorize_file(self, file_ext):
        for category, exts in self.categories.items():
            if file_ext in exts:
                return category
        return "Other"

    def _unique_dest(self, dest_dir, name, suffix):
        counter = 1
        while (dest_dir / f"{name}_{counter}{suffix}").exists():
            counter += 1
        return dest_dir / f"{name}_{counter}{suffix}"

    def organize_files(self):
        if not self.selected_folder:
            messagebox.showerror("Error", "Please select a folder first!")
            return

        target_dir = Path(self.selected_folder)
        files = [f for f in target_dir.iterdir() if f.is_file()]

        if self.simulate_var.get():
            counts = {}
            for f in files:
                cat = self._categorize_file(f.suffix.lower())
                counts[cat] = counts.get(cat, 0) + 1
            summary = "\n".join(f"Would move {n} files to {c}" for c, n in counts.items()) or "No files would be moved."
            messagebox.showinfo("Simulation", summary)
            return

        for cat in self.categories:
            (target_dir / cat).mkdir(exist_ok=True)

        moved, errors = 0, []
        self.root.config(cursor="wait")
        self.root.update()

        try:
            for item in files:
                cat = self._categorize_file(item.suffix.lower())
                dest = target_dir / cat / item.name
                if dest.exists():
                    dest = self._unique_dest(target_dir / cat, item.stem, item.suffix)
                try:
                    shutil.move(str(item), str(dest))
                    moved += 1
                except Exception as e:
                    errors.append(f"Error moving {item.name}: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Fatal error: {e}")
        finally:
            self.root.config(cursor="")

        if errors:
            msg = "\n".join(errors[:5])
            if len(errors) > 5:
                msg += f"\n... and {len(errors) - 5} more errors."
            messagebox.showerror("Errors", f"Encountered {len(errors)} errors:\n{msg}")
        else:
            messagebox.showinfo("Success", f"Moved {moved} files successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    FileOrganizerApp(root)
    root.mainloop()
