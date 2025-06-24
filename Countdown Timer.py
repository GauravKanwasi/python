import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import sys
import math
import os

# Cross-platform sound support
try:
    import winsound  # Windows
except ImportError:
    try:
        import pygame.mixer as mixer  # Other platforms
        mixer.init()
    except ImportError:
        mixer = None

class CountdownApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vibrant Countdown Timer")
        self.root.geometry("500x550")
        self.root.resizable(False, False)
        self.root.configure(bg="#1e1e2e")
        
        # Set application icon
        try:
            self.root.iconbitmap("timer_icon.ico")  # Add an icon file to your project
        except:
            pass

        # State variables
        self.minutes = tk.IntVar(value=1)
        self.seconds = tk.IntVar(value=0)
        self.running = False
        self.paused = False
        self.remaining_time = 0
        self.end_time = 0
        self.last_second = None
        self.status = tk.StringVar(value="Ready")
        self.preset_times = [1, 5, 10, 15, 20, 30, 45, 60, 90, 120]

        # Styling
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Segoe UI", 12), foreground="#ffffff", background="#1e1e2e")
        self.style.configure("Timer.TLabel", font=("DS-Digital", 60, "bold"), foreground="#4CAF50")
        self.style.configure("Status.TLabel", font=("Segoe UI", 10), foreground="#bbbbbb")
        self.style.configure("Preset.TButton", font=("Segoe UI", 9), padding=5)
        self.style.configure("Control.TButton", font=("Segoe UI", 10, "bold"), padding=8)
        self.style.configure("TFrame", background="#1e1e2e")
        
        # Create GUI elements
        self.create_widgets()

    def create_widgets(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header_frame, text="VIBRANT COUNTDOWN TIMER", 
                 font=("Segoe UI", 14, "bold"), foreground="#4CAF50").pack()
        
        # Timer Display
        timer_frame = ttk.Frame(main_frame)
        timer_frame.pack(fill=tk.X, pady=15)
        
        self.timer_label = ttk.Label(timer_frame, text="01:00", style="Timer.TLabel")
        self.timer_label.pack()
        
        self.status_label = ttk.Label(timer_frame, textvariable=self.status, style="Status.TLabel")
        self.status_label.pack(pady=5)
        
        # Progress Bar
        self.progress = ttk.Progressbar(main_frame, length=400, mode="determinate")
        self.progress.pack(fill=tk.X, pady=10)
        
        # Preset buttons
        preset_frame = ttk.LabelFrame(main_frame, text="Quick Presets", padding=10)
        preset_frame.pack(fill=tk.X, pady=(10, 15))
        
        for i, minutes in enumerate(self.preset_times):
            btn = ttk.Button(
                preset_frame, 
                text=f"{minutes} min", 
                style="Preset.TButton",
                command=lambda m=minutes: self.set_preset(m)
            )
            btn.grid(row=i//5, column=i%5, padx=5, pady=5)
        
        # Time Input
        input_frame = ttk.LabelFrame(main_frame, text="Set Time", padding=10)
        input_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(input_frame, text="Minutes:").grid(row=0, column=0, padx=5, sticky="e")
        min_spin = ttk.Spinbox(input_frame, from_=0, to=120, width=5, textvariable=self.minutes)
        min_spin.grid(row=0, column=1, padx=5, sticky="w")
        min_spin.bind("<KeyRelease>", self.validate_input)
        
        ttk.Label(input_frame, text="Seconds:").grid(row=0, column=2, padx=(20, 5), sticky="e")
        sec_spin = ttk.Spinbox(input_frame, from_=0, to=59, width=5, textvariable=self.seconds)
        sec_spin.grid(row=0, column=3, padx=5, sticky="w")
        sec_spin.bind("<KeyRelease>", self.validate_input)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.start_btn = ttk.Button(
            button_frame, 
            text="Start", 
            style="Control.TButton",
            command=self.start_countdown
        )
        self.start_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.pause_btn = ttk.Button(
            button_frame, 
            text="Pause", 
            style="Control.TButton",
            state=tk.DISABLED,
            command=self.pause_countdown
        )
        self.pause_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.reset_btn = ttk.Button(
            button_frame, 
            text="Reset", 
            style="Control.TButton",
            state=tk.DISABLED,
            command=self.reset_countdown
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Theme toggle
        self.theme_btn = ttk.Button(
            button_frame, 
            text="🌙", 
            style="Control.TButton",
            command=self.toggle_theme
        )
        self.theme_btn.pack(side=tk.LEFT, padx=5, fill=tk.X)
        
        # Set initial values
        self.update_timer_display()
        self.root.after(100, self.animate_background)

    def set_preset(self, minutes):
        self.minutes.set(minutes)
        self.seconds.set(0)
        self.update_timer_display()
        
    def validate_input(self, event):
        """Validate input to ensure only numbers are entered"""
        widget = event.widget
        current = widget.get()
        if not current.isdigit():
            widget.delete(0, tk.END)
            widget.insert(0, current[:-1])
        self.update_timer_display()
        
    def update_timer_display(self):
        """Update the timer display with current values"""
        mins = self.minutes.get()
        secs = self.seconds.get()
        self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
        
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        current_bg = self.root.cget("bg")
        if current_bg == "#1e1e2e":  # Dark mode
            self.root.configure(bg="#f0f0f0")
            self.style.configure("TLabel", background="#f0f0f0", foreground="#333333")
            self.style.configure("Status.TLabel", background="#f0f0f0", foreground="#666666")
            self.style.configure("TFrame", background="#f0f0f0")
            self.theme_btn.configure(text="☀️")
        else:  # Light mode
            self.root.configure(bg="#1e1e2e")
            self.style.configure("TLabel", background="#1e1e2e", foreground="#ffffff")
            self.style.configure("Status.TLabel", background="#1e1e2e", foreground="#bbbbbb")
            self.style.configure("TFrame", background="#1e1e2e")
            self.theme_btn.configure(text="🌙")
    
    def animate_background(self):
        """Create a subtle animated background effect"""
        if not self.running and not self.paused:
            # Create a pulsing effect on the timer display
            current_color = self.timer_label.cget("foreground")
            if current_color == "#4CAF50":
                self.timer_label.config(foreground="#45a049")
            else:
                self.timer_label.config(foreground="#4CAF50")
        self.root.after(1000, self.animate_background)
    
    def start_countdown(self):
        """Start the countdown timer"""
        try:
            mins = self.minutes.get()
            secs = self.seconds.get()
            total_seconds = mins * 60 + secs
            
            if total_seconds <= 0:
                raise ValueError("Time must be greater than zero")
                
            if not self.running:
                self.running = True
                self.paused = False
                self.remaining_time = total_seconds
                self.end_time = time.monotonic() + total_seconds
                self.progress["maximum"] = total_seconds
                self.progress["value"] = total_seconds
                self.status.set("Running")
                
                # Update UI state
                self.start_btn.state(['disabled'])
                self.pause_btn.state(['!disabled'])
                self.reset_btn.state(['!disabled'])
                
                # Start the countdown thread
                threading.Thread(target=self.run_countdown, daemon=True).start()
        except ValueError as e:
            messagebox.showerror("Invalid Input", str(e))

    def pause_countdown(self):
        """Pause or resume the countdown"""
        if self.running:
            if self.paused:
                self.paused = False
                self.end_time = time.monotonic() + self.remaining_time
                self.pause_btn.config(text="Pause")
                self.status.set("Running")
                threading.Thread(target=self.run_countdown, daemon=True).start()
            else:
                self.paused = True
                self.pause_btn.config(text="Resume")
                self.status.set("Paused")

    def reset_countdown(self):
        """Reset the countdown to initial state"""
        self.running = False
        self.paused = False
        self.remaining_time = 0
        self.last_second = None
        self.status.set("Ready")
        
        # Reset UI
        self.update_timer_display()
        self.progress["value"] = 0
        self.timer_label.config(foreground="#4CAF50")
        
        # Enable/disable buttons
        self.start_btn.state(['!disabled'])
        self.pause_btn.state(['disabled'])
        self.reset_btn.state(['disabled'])
        self.pause_btn.config(text="Pause")

    def run_countdown(self):
        """Run the countdown loop with pulsing effect and sound"""
        next_wake = time.monotonic()
        step = 0.1  # Update interval in seconds
        
        while self.running and not self.paused and self.remaining_time > 0:
            self.remaining_time = self.end_time - time.monotonic()
            
            if self.remaining_time <= 0:
                self.remaining_time = 0
                self.running = False
                
            mins, secs = divmod(int(self.remaining_time), 60)
            self.timer_label.config(text=f"{mins:02d}:{secs:02d}")
            self.progress["value"] = self.remaining_time
            
            # Update progress bar color based on time remaining
            progress_percent = self.remaining_time / self.progress["maximum"]
            if progress_percent > 0.5:
                self.progress.configure(style="green.Horizontal.TProgressbar")
            elif progress_percent > 0.25:
                self.progress.configure(style="orange.Horizontal.TProgressbar")
            else:
                self.progress.configure(style="red.Horizontal.TProgressbar")
            
            # Pulsing effect and tick sound
            current_second = int(self.remaining_time)
            if self.last_second != current_second:
                # Visual pulse effect
                if current_second > 10:
                    self.timer_label.config(foreground="#4CAF50" if current_second % 2 == 0 else "#45a049")
                else:  # Last 10 seconds - more urgent pulsing
                    self.timer_label.config(foreground="#FF5722" if current_second % 2 == 0 else "#E64A19")
                
                # Play tick sound every second
                if current_second > 0:
                    self.play_sound(800, 50)
                
                self.last_second = current_second
            
            # Calculate next wake time for consistent timing
            next_wake += step
            sleep_time = next_wake - time.monotonic()
            if sleep_time > 0:
                time.sleep(sleep_time)

        # Timer completed
        if self.running and not self.paused:
            self.timer_label.config(text="00:00")
            self.progress["value"] = 0
            
            # Completion animation
            for _ in range(3):
                self.timer_label.config(foreground="#FF5722")
                self.root.update()
                time.sleep(0.3)
                self.timer_label.config(foreground="#4CAF50")
                self.root.update()
                time.sleep(0.3)
            
            # Play completion sound
            self.play_completion_sound()
            
            # Show completion message
            messagebox.showinfo("Time's Up!", "The countdown has finished!")
            self.reset_countdown()
    
    def play_sound(self, frequency, duration):
        """Play a sound (cross-platform)"""
        try:
            if 'win' in sys.platform:
                winsound.Beep(frequency, duration)
            elif mixer:
                # Use pygame for non-Windows systems
                sound = mixer.Sound(buffer=bytearray([128] * 44100))  # Generate simple beep
                sound.set_volume(0.1)
                sound.play(maxtime=duration)
            else:
                # Fallback: system beep
                print('\a', end='', flush=True)
        except Exception:
            pass  # Silently ignore sound errors
    
    def play_completion_sound(self):
        """Play a more noticeable completion sound"""
        try:
            if 'win' in sys.platform:
                winsound.Beep(1000, 500)
                winsound.Beep(1200, 300)
            elif mixer:
                # Use pygame for non-Windows systems
                for freq in [1000, 1200]:
                    duration = 0.5 if freq == 1000 else 0.3
                    samples = [int(127 + 127 * math.sin(2 * math.pi * freq * x / 44100)) 
                              for x in range(int(44100 * duration))]
                    sound = mixer.Sound(buffer=bytearray(samples))
                    sound.set_volume(0.2)
                    sound.play()
                    time.sleep(duration)
            else:
                # Fallback: multiple system beeps
                for _ in range(3):
                    print('\a', end='', flush=True)
                    time.sleep(0.3)
        except Exception:
            pass  # Silently ignore sound errors

    def run(self):
        """Start the application."""
        # Configure progress bar styles
        self.style.configure("green.Horizontal.TProgressbar", 
                           background="#4CAF50", 
                           troughcolor="#333333")
        self.style.configure("orange.Horizontal.TProgressbar", 
                           background="#FF9800", 
                           troughcolor="#333333")
        self.style.configure("red.Horizontal.TProgressbar", 
                           background="#F44336", 
                           troughcolor="#333333")
        
        self.root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = CountdownApp(root)
    app.run()
