import tkinter as tk
from tkinter import ttk, messagebox
import time
import sys

# ==========================================================
# CROSS PLATFORM SOUND
# ==========================================================

try:
    import winsound

    def beep(freq=1000, duration=150):
        winsound.Beep(freq, duration)

except ImportError:

    def beep(freq=1000, duration=150):
        # Terminal bell fallback
        print("\a", end="", flush=True)


# ==========================================================
# COUNTDOWN TIMER APPLICATION
# ==========================================================

class CountdownTimer:

    def __init__(self, root):

        self.root = root
        self.root.title("Advanced Countdown Timer")
        self.root.geometry("550x500")
        self.root.resizable(False, False)

        # --------------------------------------------------
        # TIMER STATE VARIABLES
        # --------------------------------------------------
        self.running = False
        self.paused = False

        self.total_time = 0
        self.remaining_time = 0

        self.dark_mode = True

        # --------------------------------------------------
        # USER INPUT VARIABLES
        # --------------------------------------------------
        self.minutes = tk.IntVar(value=1)
        self.seconds = tk.IntVar(value=0)

        self.status = tk.StringVar(value="Ready")

        # --------------------------------------------------
        # STYLE
        # --------------------------------------------------
        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.configure_styles()

        # --------------------------------------------------
        # BUILD GUI
        # --------------------------------------------------
        self.create_widgets()

        # --------------------------------------------------
        # KEYBOARD SHORTCUTS
        # --------------------------------------------------
        self.root.bind("<Return>", lambda e: self.start_timer())
        self.root.bind("<space>", lambda e: self.pause_resume())
        self.root.bind("<Escape>", lambda e: self.reset_timer())

        # --------------------------------------------------
        # SAFE WINDOW CLOSE
        # --------------------------------------------------
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ======================================================
    # STYLING
    # ======================================================

    def configure_styles(self):

        self.style.configure(
            "Timer.TLabel",
            font=("Consolas", 48, "bold")
        )

        self.style.configure(
            "Status.TLabel",
            font=("Segoe UI", 10)
        )

        self.style.configure(
            "Green.Horizontal.TProgressbar",
            troughcolor="#2b2b2b",
            background="#4CAF50"
        )

        self.style.configure(
            "Orange.Horizontal.TProgressbar",
            troughcolor="#2b2b2b",
            background="#FF9800"
        )

        self.style.configure(
            "Red.Horizontal.TProgressbar",
            troughcolor="#2b2b2b",
            background="#F44336"
        )

    # ======================================================
    # GUI
    # ======================================================

    def create_widgets(self):

        self.main = ttk.Frame(self.root, padding=20)
        self.main.pack(fill="both", expand=True)

        title = ttk.Label(
            self.main,
            text="COUNTDOWN TIMER",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=10)

        self.timer_label = ttk.Label(
            self.main,
            text="01:00",
            style="Timer.TLabel"
        )
        self.timer_label.pack(pady=10)

        self.status_label = ttk.Label(
            self.main,
            textvariable=self.status,
            style="Status.TLabel"
        )
        self.status_label.pack()

        # Progress Bar
        self.progress = ttk.Progressbar(
            self.main,
            length=450,
            mode="determinate",
            style="Green.Horizontal.TProgressbar"
        )
        self.progress.pack(pady=20)

        # Input Frame
        input_frame = ttk.LabelFrame(
            self.main,
            text="Set Time"
        )
        input_frame.pack(fill="x", pady=10)

        ttk.Label(input_frame, text="Minutes").grid(
            row=0,
            column=0,
            padx=10,
            pady=10
        )

        self.min_spin = ttk.Spinbox(
            input_frame,
            from_=0,
            to=999,
            textvariable=self.minutes,
            width=10
        )
        self.min_spin.grid(row=0, column=1)

        ttk.Label(input_frame, text="Seconds").grid(
            row=0,
            column=2,
            padx=10
        )

        self.sec_spin = ttk.Spinbox(
            input_frame,
            from_=0,
            to=59,
            textvariable=self.seconds,
            width=10
        )
        self.sec_spin.grid(row=0, column=3)

        # Presets
        preset_frame = ttk.LabelFrame(
            self.main,
            text="Quick Presets"
        )
        preset_frame.pack(fill="x", pady=10)

        presets = [1, 5, 10, 15, 20, 30]

        for i, p in enumerate(presets):

            ttk.Button(
                preset_frame,
                text=f"{p} min",
                command=lambda m=p: self.set_preset(m)
            ).grid(
                row=0,
                column=i,
                padx=5,
                pady=5
            )

        # Control Buttons
        btn_frame = ttk.Frame(self.main)
        btn_frame.pack(fill="x", pady=15)

        self.start_btn = ttk.Button(
            btn_frame,
            text="Start",
            command=self.start_timer
        )
        self.start_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.pause_btn = ttk.Button(
            btn_frame,
            text="Pause",
            state="disabled",
            command=self.pause_resume
        )
        self.pause_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.reset_btn = ttk.Button(
            btn_frame,
            text="Reset",
            state="disabled",
            command=self.reset_timer
        )
        self.reset_btn.pack(side="left", expand=True, fill="x", padx=5)

        self.theme_btn = ttk.Button(
            btn_frame,
            text="🌙",
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="left", padx=5)

        self.apply_dark_theme()

    # ======================================================
    # PRESETS
    # ======================================================

    def set_preset(self, minutes):
        self.minutes.set(minutes)
        self.seconds.set(0)
        self.update_display(minutes * 60)

    # ======================================================
    # DISPLAY
    # ======================================================

    def update_display(self, seconds):

        mins, secs = divmod(seconds, 60)

        self.timer_label.config(
            text=f"{mins:02d}:{secs:02d}"
        )

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate_time(self):

        try:

            mins = max(0, int(self.minutes.get()))
            secs = max(0, int(self.seconds.get()))

            if secs > 59:
                secs = 59

            self.minutes.set(mins)
            self.seconds.set(secs)

            return mins * 60 + secs

        except Exception:
            return 0

    # ======================================================
    # START
    # ======================================================

    def start_timer(self):

        if self.running:
            return

        total = self.validate_time()

        if total <= 0:

            messagebox.showerror(
                "Invalid Time",
                "Enter a value greater than zero."
            )
            return

        self.total_time = total
        self.remaining_time = total

        self.running = True
        self.paused = False

        self.progress["maximum"] = total
        self.progress["value"] = total

        self.status.set("Running")

        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self.reset_btn.config(state="normal")

        self.countdown()

    # ======================================================
    # COUNTDOWN LOOP
    # ======================================================

    def countdown(self):

        # Tkinter is NOT thread-safe.
        # All GUI updates stay on main thread.

        if not self.running:
            return

        if self.paused:
            return

        if self.remaining_time <= 0:
            self.timer_finished()
            return

        self.update_display(self.remaining_time)

        self.progress["value"] = self.remaining_time

        self.update_progress_style()

        if self.remaining_time <= 10:
            beep(1000, 75)

        self.remaining_time -= 1

        self.root.after(
            1000,
            self.countdown
        )

    # ======================================================
    # PROGRESS COLORS
    # ======================================================

    def update_progress_style(self):

        if self.total_time == 0:
            return

        percent = self.remaining_time / self.total_time

        if percent > 0.5:

            self.progress.configure(
                style="Green.Horizontal.TProgressbar"
            )

        elif percent > 0.2:

            self.progress.configure(
                style="Orange.Horizontal.TProgressbar"
            )

        else:

            self.progress.configure(
                style="Red.Horizontal.TProgressbar"
            )

    # ======================================================
    # PAUSE / RESUME
    # ======================================================

    def pause_resume(self):

        if not self.running:
            return

        self.paused = not self.paused

        if self.paused:

            self.status.set("Paused")
            self.pause_btn.config(text="Resume")

        else:

            self.status.set("Running")
            self.pause_btn.config(text="Pause")

            self.countdown()

    # ======================================================
    # RESET
    # ======================================================

    def reset_timer(self):

        self.running = False
        self.paused = False

        self.status.set("Ready")

        self.pause_btn.config(
            text="Pause",
            state="disabled"
        )

        self.reset_btn.config(
            state="disabled"
        )

        self.start_btn.config(
            state="normal"
        )

        self.progress["value"] = 0

        total = (
            self.minutes.get() * 60
            + self.seconds.get()
        )

        self.update_display(total)

    # ======================================================
    # FINISHED
    # ======================================================

    def timer_finished(self):

        self.running = False

        self.timer_label.config(
            foreground="red"
        )

        for _ in range(3):
            beep(1200, 250)

        self.status.set("Completed")

        messagebox.showinfo(
            "Time's Up!",
            "Countdown completed."
        )

        self.reset_timer()

    # ======================================================
    # THEME
    # ======================================================

    def toggle_theme(self):

        self.dark_mode = not self.dark_mode

        if self.dark_mode:
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def apply_dark_theme(self):

        self.root.configure(bg="#1e1e2e")
        self.theme_btn.config(text="🌙")

    def apply_light_theme(self):

        self.root.configure(bg="#f4f4f4")
        self.theme_btn.config(text="☀️")

    # ======================================================
    # CLOSE
    # ======================================================

    def on_close(self):

        self.running = False
        self.root.destroy()


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = CountdownTimer(root)

    root.mainloop()
