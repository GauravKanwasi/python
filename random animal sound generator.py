import random
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from PIL import Image, ImageTk
import sqlite3
import os
from playsound import playsound

# Define media directories
IMAGE_DIR = "media/images"
SOUND_DIR = "media/sounds"
VIDEO_DIR = "media/videos"

class AnimalSoundExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("BioAcoustic Explorer 2.0")
        self.root.geometry("1200x800")
        
        # Database setup
        self.conn = sqlite3.connect('animal_db.sqlite')
        self.create_tables()
        
        # Initialize animal IDs list
        self.animal_ids = []
        
        # GUI components
        self.create_widgets()
        self.load_animals()
        self.current_animal = None
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0')
        self.style.configure('TButton', font=('Arial', 10))
        
    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS animals
            (id INTEGER PRIMARY KEY, name TEXT, sound_file TEXT, 
             image_file TEXT, video_file TEXT, clicks INTEGER)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS favorites
            (id INTEGER PRIMARY KEY, animal_id INTEGER)''')
        self.conn.commit()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Animal Selection Panel
        left_panel = ttk.Frame(main_frame, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        
        self.search_entry = ttk.Entry(left_panel)
        self.search_entry.pack(fill=tk.X, pady=5)
        self.search_entry.bind('<KeyRelease>', self.search_animals)
        
        self.animal_list = tk.Listbox(left_panel)
        self.animal_list.pack(fill=tk.BOTH, expand=True)
        self.animal_list.bind('<<ListboxSelect>>', self.show_animal_details)
        
        ttk.Button(left_panel, text="Random Animal", 
                 command=self.show_random_animal).pack(fill=tk.X, pady=5)
        
        # Details Panel
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.image_label = ttk.Label(right_panel)
        self.image_label.pack(pady=10)
        
        info_frame = ttk.Frame(right_panel)
        info_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(info_frame, text="Name:", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        self.name_label = ttk.Label(info_frame, font=('Arial', 14))
        self.name_label.pack(side=tk.LEFT, padx=10)
        
        # Removed sound_label since we now play actual sounds
        
        button_frame = ttk.Frame(right_panel)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Play Sound", 
                 command=self.play_sound).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Watch Video", 
                 command=self.open_video).pack(side=tk.LEFT, padx=5)
        self.fav_button = ttk.Button(button_frame, text="☆ Favorite", 
                                    command=self.toggle_favorite)
        self.fav_button.pack(side=tk.LEFT, padx=5)
        
        # Status Bar
        self.status = ttk.Label(self.root, relief=tk.SUNKEN, anchor=tk.W)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def load_animals(self):
        animals = [
            {"name": "Mongoose", "sound_file": "mongoose.mp3", 
             "image_file": "mongoose.jpg", "video_file": "mongoose.mp4"},
            {"name": "Elephant", "sound_file": "elephant.mp3", 
             "image_file": "elephant.jpg", "video_file": "elephant.mp4"},
            {"name": "Lion", "sound_file": "lion.mp3", 
             "image_file": "lion.jpg", "video_file": "lion.mp4"},
            # Add more animals as needed
        ]
        
        cursor = self.conn.cursor()
        for animal in animals:
            cursor.execute('''INSERT OR IGNORE INTO animals 
                            (name, sound_file, image_file, video_file, clicks)
                            VALUES (?, ?, ?, ?, 0)''',
                         (animal['name'], animal['sound_file'], 
                          animal['image_file'], animal['video_file']))
        self.conn.commit()
        self.search_animals()
    
    def search_animals(self, event=None):
        query = self.search_entry.get()
        cursor = self.conn.cursor()
        cursor.execute('''SELECT id, name FROM animals 
                        WHERE name LIKE ? ORDER BY clicks DESC''',
                     (f'%{query}%',))
        self.animal_list.delete(0, tk.END)
        self.animal_ids = []
        for row in cursor.fetchall():
            self.animal_list.insert(tk.END, row[1])
            self.animal_ids.append(row[0])
    
    def show_animal_details(self, event):
        selection = self.animal_list.curselection()
        if selection:
            index = selection[0]
            animal_id = self.animal_ids[index]
            cursor = self.conn.cursor()
            cursor.execute('''SELECT * FROM animals WHERE id=?''', (animal_id,))
            self.current_animal = cursor.fetchone()
            
            # Update display
            self.name_label.config(text=self.current_animal[1])
            
            # Load image
            image_path = os.path.join(IMAGE_DIR, self.current_animal[3])
            if not os.path.exists(image_path):
                image_path = os.path.join(IMAGE_DIR, "no_image.jpg")
            try:
                image = Image.open(image_path)
                image.thumbnail((600, 400))
                photo = ImageTk.PhotoImage(image)
                self.image_label.config(image=photo)
                self.image_label.image = photo
            except Exception as e:
                self.status.config(text=f"Error loading image: {str(e)}")
            
            # Update click counter
            cursor.execute('''UPDATE animals SET clicks = clicks + 1 
                           WHERE id=?''', (animal_id,))
            self.conn.commit()
            
            # Update favorite button
            cursor.execute('''SELECT id FROM favorites 
                            WHERE animal_id=?''', (animal_id,))
            self.fav_button.config(text="★ Unfavorite" if cursor.fetchone() else "☆ Favorite")
    
    def play_sound(self):
        if self.current_animal:
            sound_path = os.path.join(SOUND_DIR, self.current_animal[2])
            if os.path.exists(sound_path):
                try:
                    playsound(sound_path)
                except Exception as e:
                    messagebox.showerror("Error", f"Could not play sound: {str(e)}")
            else:
                messagebox.showerror("Error", "Sound file not found.")
    
    def open_video(self):
        if self.current_animal:
            video_path = os.path.join(VIDEO_DIR, self.current_animal[4])
            if os.path.exists(video_path):
                webbrowser.open(video_path)
            else:
                messagebox.showerror("Error", "Video file not found.")
    
    def toggle_favorite(self):
        if self.current_animal:
            cursor = self.conn.cursor()
            cursor.execute('''SELECT id FROM favorites 
                            WHERE animal_id=?''', (self.current_animal[0],))
            if cursor.fetchone():
                cursor.execute('''DELETE FROM favorites 
                                WHERE animal_id=?''', (self.current_animal[0],))
                self.fav_button.config(text="☆ Favorite")
            else:
                cursor.execute('''INSERT INTO favorites (animal_id) 
                               VALUES (?)''', (self.current_animal[0],))
                self.fav_button.config(text="★ Unfavorite")
            self.conn.commit()
    
    def show_random_animal(self):
        if self.animal_ids:
            index = random.randint(0, len(self.animal_ids) - 1)
            self.animal_list.selection_clear(0, tk.END)
            self.animal_list.selection_set(index)
            self.animal_list.see(index)
            self.show_animal_details(None)
        else:
            self.status.config(text="No animals to select.")

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimalSoundExplorer(root)
    root.mainloop()
