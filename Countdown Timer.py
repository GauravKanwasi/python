import tkinter as tk
from tkinter import messagebox, ttk
import time
import winsound  # Windows-specific; for cross-platform, consider pygame
import threading

class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vibrant Countdown Timer")
        self.root.geometry("400x500")
        self.root.resizable(False, False)

        # State variables
        self.seconds = tk.IntVar(value=0)
        self.running = False
        self.paused = False
        self.remaining_time = 0
        self.end_time = 0
        self.last_second = None

        # Styling
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Helvetica", 14), foreground="#ffffff")
        self.style.configure("Timer.TLabel", font=("DS-Digital", 48, "bold"), foreground="#00ff00")

        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Canvas for gradient background
        self.canvas = tk.Canvas(self.root, width=400, height=500, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_gradient()

        # Title
        self.title_label = ttk.Label(self.root, text="Countdown Timer", style="TLabel")
        self.canvas.create_window(200, 50, window=self.title_label, anchor=tk.CENTER)

        # Timer Display
        self.timer_label = ttk.Label(self.root, text="00:00", style="Timer.TLabel")
        self.canvas.create_window(200, 150, window=self.timer_label, anchor=tk.CENTER)

        # Progress Bar
        self.progress = ttk.Progressbar(self.root, length=300, mode="determinate")
        self.canvas.create_window(200, 250, window=self.progress, anchor=tk.CENTER)

        # Input Frame
        self.input_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.canvas.create_window(200, 350, window=self.input_frame, anchor=tk.CENTER)
        ttk.Label(self.input_frame, text="Seconds:", style="TLabel").pack(side=tk.LEFT, padx=5)
        self.entry = ttk.Entry(self.input_frame, textvariable=self.seconds, width=10)
        self.entry.pack(side=tk.LEFT, padx=5)

        # Buttons Frame
        self.button_frame = tk.Frame(self.root, bg="#1e1e2e")
        self.canvas.create_window(200, 450, window=self.button_frame, anchor=tk.CENTER)
        
        # Buttons with vibrant colors
        self.start_btn = tk.Button(self.button_frame, text="Start", command=self.start_countdown, 
                                  bg="#4CAF50", fg="white", font=("Helvetica", 12), relief=tk.RAISED)
        self.start_btn.pack(side=tk.LEFT, padx=5)
        
        self.pause_btn = tk.Button(self.button_frame, text="Pause", command=self.pause_countdown, 
                                  bg="#2196F3", fg="white", font=("Helvetica", 12), relief=tk.RAISED, state=tk.DISABLED)
        self.pause_btn.pack(side=tk.LEFT, padx=5)
        
        self.reset_btn = tk.Button(self.button_frame, text="Reset", command=self.reset_countdown, 
                                  bg="#f44336", fg="white", font=("Helvetica", 12), relief=tk.RAISED, state=tk.DISABLED)
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        # Add hover effects
        for btn in [self.start_btn, self.pause_btn, self.reset_btn]:
            btn.bind("<Enter>", self.on_enter)
            btn.bind("<Leave>", self.on_leave)

    def draw_gradient(self):
        """Draw a vibrant gradient background from dark blue to light green."""
        for i in range(500):
            r = 0
            g = int(255 * (i / 500))  # Increase green intensity
            b = int(139 - 139 * (i / 500))  # Decrease blue intensity
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(0, i, 400, i, fill=color)

    def on_enter(self, event):
        """Change button color on hover."""
        if event.widget['state'] != 'disabled':
            if event.widget == self.start_btn:
                event.widget['background'] = '#45a049'
            elif event.widget == self.pause_btn:
                event.widget['background'] = '#1e88e5'
            else:  # reset_btn
                event.widget['background'] = '#e53935'

    def on_leave(self, event):
        """Revert button color when mouse leaves."""
        if event.widget['state'] != 'disabled':
            if event.widget == self.start_btn:
                event.widget['background'] = '#4CAF50'
            elif event.widget == self.pause_btn:
                event.widget['background'] = '#2196F3'
            else:  # reset_btn
                event.widget['background'] = '#f44336'

    def start_countdown(self):
        """Start the countdown timer."""
        try:
            seconds = self.seconds.get()
            if seconds <= 0:
                raise ValueError("Seconds must be positive")
            if not self.running:
                self.running = True
                self.paused = False
                self.remaining_time = seconds
                self.end_time = time.monotonic() + seconds
                self.progress["maximum"] = seconds
                self.progress["value"] = seconds
                self.start_btn.config(state=tk.DISABLED)
                self.pause_btn.config(state=tk.NORMAL)
                self.reset_btn.config(state=tk.NORMAL)
                self.entry.config(state=tk.DISABLED)
                threading.Thread(target=self.run_countdown, daemon=True).start()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid positive integer.")

    def pause_countdown(self):
        """Pause or resume the countdown."""
        if self.running:
            if self.paused:
                self.paused = False
                self.end_time = time.monotonic() + self.remaining_time
                self.pause_btn.config(text="Pause")
                threading.Thread(target=self.run_countdown, daemon=True).start()
            else:
                self.paused = True
                self.pause_btn.config(text="Resume")

    def reset_countdown(self):
        """Reset the countdown to initial state."""
        self.running = False
        self.paused = False
        self.remaining_time = 0
        self.last_second = None
        self.timer_label.config(text="00:00", foreground="#00ff00")
        self.progress["value"] = 0
        self.start_btn.config(state=tk.NORMAL)
        self.pause_btn.config(text="Pause", state=tk.DISABLED)
        self.reset_btn.config(state=tk.DISABLED)
        self.entry.config(state=tk.NORMAL)
        self.seconds.set(0)

    def run_countdown(self):
        """Run the countdown loop with pulsing effect and sound."""
        while self.running and not self.paused and self.remaining_time > 0:
            self.remaining_time = self.end_time - time.monotonic()
            if self.remaining_time <= 0:
                self.remaining_time = 0
                self.running = False
            mins, secs = divmod(int(self.remaining_time), 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            self.progress["value"] = self.remaining_time

            # Pulsing effect and tick sound
            current_second = int(self.remaining_time)
            if self.last_second != current_second:
                self.timer_label.config(foreground="#00ff00" if current_second % 2 == 0 else "#00cc00")
                try:
                    threading.Thread(target=lambda: winsound.Beep(1000, 100), daemon=True).start()
                except:
                    pass  # Silently ignore if sound fails
                self.last_second = current_second
            self.root.update()
            time.sleep(0.1)

        if self.running and not self.paused:
            self.timer_label.config(text="00:00")
            self.progress["value"] = 0
            try:
                winsound.Beep(1000, 500)  # Completion sound
            except:
                pass
            messagebox.showinfo("Time's Up!", "The countdown has finished!")
            self.reset_countdown()

    def run(self):
        """Start the application."""
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    app.run()
