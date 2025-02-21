import random
import tkinter as tk
from tkinter import ttk, messagebox
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import sqlite3

class AnimalSoundExplorer:
    def __init__(self, root):
        self.root = root
        self.root.title("BioAcoustic Explorer 2.0")
        self.root.geometry("1200x800")
        
        # Database setup
        self.conn = sqlite3.connect('animal_db.sqlite')
        self.create_tables()
        
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
            (id INTEGER PRIMARY KEY, name TEXT, sound TEXT, 
             image_url TEXT, video_url TEXT, clicks INTEGER)''')
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
        
        self.sound_label = ttk.Label(right_panel, font=('Arial', 12))
        self.sound_label.pack(pady=5)
        
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
            {"name": "Mongoose", "sound": "Squeak-squeak-bite!", 
             "image": "https://example.com/mongoose.jpg",
             "video": "https://youtube.com/watch?v=Wk_3BdXgQ5U"},
            # Add other animals with image/video URLs
        ]
        
        cursor = self.conn.cursor()
        for animal in animals:
            cursor.execute('''INSERT OR IGNORE INTO animals 
                            (name, sound, image_url, video_url, clicks)
                            VALUES (?, ?, ?, ?, 0)''',
                         (animal['name'], animal['sound'], 
                          animal['image'], animal['video']))
        self.conn.commit()
        self.search_animals()
    
    def search_animals(self, event=None):
        query = self.search_entry.get()
        cursor = self.conn.cursor()
        cursor.execute('''SELECT id, name FROM animals 
                        WHERE name LIKE ? ORDER BY clicks DESC''',
                     (f'%{query}%',))
        self.animal_list.delete(0, tk.END)
        for row in cursor.fetchall():
            self.animal_list.insert(tk.END, row[1], row[0])
    
    def show_animal_details(self, event):
        selection = self.animal_list.curselection()
        if selection:
            animal_id = self.animal_list.get(selection[0], selection[0])[0]
            cursor = self.conn.cursor()
            cursor.execute('''SELECT * FROM animals WHERE id=?''', (animal_id,))
            self.current_animal = cursor.fetchone()
            
            # Update display
            self.name_label.config(text=self.current_animal[1])
            self.sound_label.config(text=self.current_animal[2])
            
            # Load image
            try:
                response = requests.get(self.current_animal[3])
                image = Image.open(BytesIO(response.content))
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
        # Implement actual sound playback using pygame
        messagebox.showinfo("Coming Soon", 
                          "Sound playback feature in development!")
    
    def open_video(self):
        if self.current_animal:
            webbrowser.open(self.current_animal[4])
    
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
        cursor = self.conn.cursor()
        cursor.execute('''SELECT id FROM animals ORDER BY RANDOM() LIMIT 1''')
        random_id = cursor.fetchone()[0]
        self.animal_list.selection_clear(0, tk.END)
        self.animal_list.selection_set(random_id)
        self.show_animal_details(None)

if __name__ == "__main__":
    root = tk.Tk()
    app = AnimalSoundExplorer(root)
    root.mainloop()
