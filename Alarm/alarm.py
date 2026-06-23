import os
import json
import time
import datetime
import signal
import threading
import sys
import subprocess
import shutil
import csv
import glob
import random
import itertools
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple

# --- Cross-Platform Imports ---
try:
    from zoneinfo import ZoneInfo, available_timezones
except ImportError:
    print("Error: Python 3.9+ is required for the 'zoneinfo' module.")
    sys.exit(1)

try:
    import msvcrt
    WINDOWS = True
except ImportError:
    import tty
    import termios
    import select
    WINDOWS = False

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False

# --- Rich Imports ---
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, SpinnerColumn
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.align import Align
from rich.columns import Columns
from rich.rule import Rule
from rich.style import Style
from rich.theme import Theme
from rich.traceback import install as install_rich_traceback
# --------------------
install_rich_traceback()

# --- Configuration ---
SAVE_FILE = os.path.expanduser("~/.radiant_clock.json")
PLUGIN_DIR = os.path.expanduser("~/.radiant_plugins")
BELL_DIR = os.path.expanduser("~/.radiant_bell")
THEMES_FILE = os.path.expanduser("~/.radiant_themes.json")

# Create directories
for directory in [PLUGIN_DIR, BELL_DIR]:
    os.makedirs(directory, exist_ok=True)

# --- Console Setup ---
console = Console()

# --- Enhanced Color Themes ---
class ThemeManager:
    DEFAULT_THEMES = {
        "cyberpunk": {
            "primary": "#00ffff", "secondary": "#ff00ff", "warning": "#ffff00",
            "danger": "#ff0066", "info": "#00ff99", "dim": "#666666",
            "banner": "bold cyan on black", "background": "black",
            "panel_border": "#ff00ff", "accent": "#00ff99", "text": "white"
        },
        "nord": {
            "primary": "#88c0d0", "secondary": "#81a1c1", "warning": "#ebcb8b",
            "danger": "#bf616a", "info": "#5e81ac", "dim": "#4c566a",
            "banner": "bold #88c0d0 on #2e3440", "background": "#2e3440",
            "panel_border": "#5e81ac", "accent": "#a3be8c", "text": "#eceff4"
        },
        "dracula": {
            "primary": "#bd93f9", "secondary": "#50fa7b", "warning": "#f1fa8c",
            "danger": "#ff5555", "info": "#8be9fd", "dim": "#6272a4",
            "banner": "bold #bd93f9 on #282a36", "background": "#282a36",
            "panel_border": "#bd93f9", "accent": "#ff79c6", "text": "#f8f8f2"
        },
        "matrix": {
            "primary": "green", "secondary": "bright_green", "warning": "yellow",
            "danger": "red", "info": "cyan", "dim": "dark_green",
            "banner": "bold green on black", "background": "black",
            "panel_border": "green", "accent": "bright_green", "text": "green"
        }
    }

    def __init__(self, storage):
        self.storage = storage
        self.custom_themes = self._load_custom_themes()

    def _load_custom_themes(self) -> Dict:
        if os.path.exists(THEMES_FILE):
            try:
                with open(THEMES_FILE, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def get_all_themes(self) -> Dict:
        return {**self.DEFAULT_THEMES, **self.custom_themes}

    def get_theme(self, name: str) -> Dict:
        all_themes = self.get_all_themes()
        return all_themes.get(name, self.DEFAULT_THEMES["cyberpunk"])

    def save_custom_theme(self, name: str, theme: Dict):
        self.custom_themes[name] = theme
        with open(THEMES_FILE, 'w') as f:
            json.dump(self.custom_themes, f, indent=2)

# --- Animation Classes ---
class AnimationFrame:
    def __init__(self, text: str, duration: float = 0.1):
        self.text = text
        self.duration = duration

class Animation:
    def __init__(self, frames: List[AnimationFrame]):
        self.frames = frames
        self.current_frame = 0
        self.last_update = time.time()

    def update(self) -> str:
        current_time = time.time()
        if current_time - self.last_update >= self.frames[self.current_frame].duration:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.last_update = current_time
        return self.frames[self.current_frame].text

class LoadingAnimation(Animation):
    STYLES = {
        "dots": ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"],
        "clock": ["🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚", "🕛"],
        "earth": ["🌍", "🌎", "🌏"],
        "weather": ["☀️", "🌤️", "⛅", "🌥️", "☁️", "🌦️", "🌧️", "⛈️", "🌨️"],
    }

    def __init__(self, style: str = "dots", duration: float = 0.1):
        frames = [AnimationFrame(char, duration) for char in self.STYLES.get(style, self.STYLES["dots"])]
        super().__init__(frames)

# --- Enhanced Storage with Statistics ---
@dataclass
class AlarmData:
    hour: int
    minute: int
    label: str
    recurrence: str = "once"
    enabled: bool = True
    sound: Optional[str] = None
    volume: Optional[int] = None
    snooze_duration: int = 5
    fade_in: bool = False

class Storage:
    DEFAULT_DATA = {
        "alarms": [],
        "theme": "cyberpunk",
        "sound": "beep",
        "favorite_timezones": [],
        "bell_volume": 75,
        "voice_wake": False,
        "log": [],
        "show_quotes": True,
        "24hour_format": True,
        "animations_enabled": True,
        "startup_sound": True,
        "alarm_history": [],
        "statistics": {
            "alarms_created": 0, "alarms_dismissed": 0, "alarms_snoozed": 0,
            "timers_completed": 0, "total_runtime": 0
        }
    }

    def __init__(self, filepath=SAVE_FILE):
        self.filepath = filepath
        self.data = self.DEFAULT_DATA.copy()
        self.lock = threading.Lock()
        self.theme_manager = None
        self.load()
        self.start_time = time.time()

    def load(self):
        try:
            if os.path.isfile(self.filepath):
                with open(self.filepath, 'r') as file:
                    loaded_data = json.load(file)
                    self.data.update(loaded_data)
        except (json.JSONDecodeError, IOError) as error:
            console.print(f"[red]Error loading save file: {error}. Using defaults.[/red]")

    def save(self):
        with self.lock:
            self.data["statistics"]["total_runtime"] += int(time.time() - self.start_time)
            self.start_time = time.time()
            try:
                if os.path.exists(self.filepath):
                    backup_path = f"{self.filepath}.backup"
                    shutil.copy2(self.filepath, backup_path)
                with open(self.filepath, "w") as file:
                    json.dump(self.data, file, indent=2, sort_keys=True)
            except IOError as error:
                console.print(f"[red]Error saving: {error}[/red]")

    def increment_stat(self, stat_name: str, amount: int = 1):
        with self.lock:
            if stat_name in self.data["statistics"]:
                self.data["statistics"][stat_name] += amount

# --- Global Storage Instance ---
storage = Storage()
theme_manager = ThemeManager(storage)
storage.theme_manager = theme_manager

# --- Enhanced Utility Functions ---
def get_current_theme():
    theme_name = storage.data.get("theme", "cyberpunk")
    return theme_manager.get_theme(theme_name)

def clear_screen():
    if storage.data.get("animations_enabled", True):
        for i in range(3, 0, -1):
            console.clear()
            console.print("\n" * i)
            time.sleep(0.01)
    console.clear()

def print_banner(text, style=None, animate=True):
    theme = get_current_theme()
    if style is None:
        style = theme.get("banner", "")
    if animate and storage.data.get("animations_enabled", True):
        animated_text = ""
        panel = Panel(Align.center(Text(animated_text, style=style)),
                     expand=False, box=box.HEAVY, border_style=theme.get("panel_border"))
        with Live(Align.center(panel), refresh_per_second=30) as live:
            for char in text:
                animated_text += char
                panel = Panel(Align.center(Text(animated_text, style=style)),
                              expand=False, box=box.HEAVY, border_style=theme.get("panel_border"))
                live.update(Align.center(panel))
                time.sleep(0.01)
    else:
        panel = Panel(Align.center(Text(text, style=style)),
                     expand=False, box=box.HEAVY, border_style=theme.get("panel_border"))
        console.print(Align.center(panel))

def show_spinner(message, duration=1, style="clock"):
    if not storage.data.get("animations_enabled", True):
        time.sleep(duration)
        return
    animation = LoadingAnimation(style)
    theme = get_current_theme()
    with Live(refresh_per_second=10) as live:
        start_time = time.time()
        while time.time() - start_time < duration:
            spinner_char = animation.update()
            text = Text(f"{spinner_char} {message}...", style=theme["primary"])
            live.update(Align.center(text))
            time.sleep(0.1)

# --- Cross Platform Input Handling ---
def get_single_character():
    """Gets a single character input from the user (Cross-Platform)."""
    if WINDOWS:
        return msvcrt.getch().decode('utf-8', 'ignore')
    else:
        file_descriptor = sys.stdin.fileno()
        old_settings = termios.tcgetattr(file_descriptor)
        try:
            tty.setraw(file_descriptor)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)
        return char

def check_keypress():
    """Returns True if a key is waiting to be read."""
    if WINDOWS:
        return msvcrt.kbhit()
    else:
        dr, _, _ = select.select([sys.stdin], [], [], 0.0)
        return bool(dr)

def format_time(hour: int, minute: int) -> str:
    if storage.data.get("24hour_format", True):
        return f"{hour:02d}:{minute:02d}"
    else:
        period = "AM" if hour < 12 else "PM"
        display_hour = hour % 12
        if display_hour == 0:
            display_hour = 12
        return f"{display_hour}:{minute:02d} {period}"

def validate_time_string(time_string):
    if " " in time_string:
        dt = datetime.datetime.strptime(time_string.upper(), "%I:%M %p")
        return dt.hour, dt.minute
    else:
        parts = time_string.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid format")
        hour, minute = int(parts[0]), int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time range")
        return hour, minute

def validate_integer_range(minimum_value, maximum_value):
    def validator(string_input):
        value = int(string_input)
        if not (minimum_value <= value <= maximum_value):
            raise ValueError(f"Value must be between {minimum_value} and {maximum_value}")
        return value
    return validator

def validate_strictly_positive_integer(string_input):
    value = int(string_input)
    if value <= 0:
        raise ValueError("Value must be greater than 0")
    return value

def get_validated_input(prompt, validator_function, error_message="Invalid input. Please try again."):
    while True:
        user_input = Prompt.ask(prompt)
        try:
            result = validator_function(user_input)
            return result
        except ValueError:
            console.print(f"[red]{error_message}[/red]")

# --- Enhanced Alarm System ---
class Alarm:
    def __init__(self, hour, minute, label, recurrence="once", enabled=True,
                 sound=None, volume=None, snooze_duration=5, fade_in=False):
        self.hour = hour
        self.minute = minute
        self.label = label
        self.recurrence = recurrence
        self.enabled = enabled
        self.sound = sound or storage.data["sound"]
        self.volume = volume or storage.data["bell_volume"]
        self.snooze_duration = snooze_duration
        self.fade_in = fade_in
        self.snooze_until = 0
        self.lock = threading.Lock()
        self.created_at = datetime.datetime.now()
        self.last_triggered = None
        self.trigger_count = 0

    def get_next_ring_time(self, current_time):
        today = current_time.date()
        ring_time = datetime.datetime.combine(today, datetime.time(self.hour, self.minute))
        if self.recurrence == "once":
            if ring_time <= current_time:
                return ring_time + datetime.timedelta(days=1)
            else:
                return ring_time
        else:
            days_checked = 0
            current_ring_time = ring_time
            while True:
                if current_ring_time > current_time:
                    day_of_week = current_ring_time.weekday()
                    if self.recurrence == "daily" or \
                       (self.recurrence == "weekdays" and day_of_week < 5) or \
                       (self.recurrence == "weekends" and day_of_week >= 5):
                        return current_ring_time
                current_ring_time += datetime.timedelta(days=1)
                days_checked += 1
                if days_checked > 14:
                    raise RuntimeError("Could not calculate next alarm time within 14 days.")

    def is_active(self, current_time):
        with self.lock:
            if not self.enabled:
                return False
            if self.snooze_until and current_time.timestamp() < self.snooze_until:
                return False
            next_ring = self.get_next_ring_time(current_time)
            return abs((current_time - next_ring).total_seconds()) < 1

    def snooze(self, minutes=None):
        with self.lock:
            snooze_time = minutes or self.snooze_duration
            self.snooze_until = int(time.time()) + (snooze_time * 60)
            storage.increment_stat("alarms_snoozed")

    def dismiss(self):
        with self.lock:
            self.snooze_until = 0
            self.last_triggered = datetime.datetime.now()
            self.trigger_count += 1
            storage.increment_stat("alarms_dismissed")
            history_entry = {
                "label": self.label,
                "time": f"{self.hour:02d}:{self.minute:02d}",
                "dismissed_at": self.last_triggered.isoformat(),
                "trigger_count": self.trigger_count
            }
            with storage.lock:
                storage.data["alarm_history"].append(history_entry)
                storage.data["alarm_history"] = storage.data["alarm_history"][-100:]

class AlarmManager:
    def __init__(self, storage_instance):
        self.storage = storage_instance
        self.alarms = []
        self.lock = threading.Lock()
        self.running = True
        self.active_alarm = None
        self.alarm_thread = None
        
        self.mixer_available = False
        if PYGAME_AVAILABLE:
            try:
                pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
                pygame.mixer.init()
                self.mixer_available = True
            except pygame.error:
                console.print("[yellow]Warning: Audio mixer unavailable. Using system beep.[/yellow]")
        else:
            console.print("[yellow]Warning: Pygame not installed. Audio disabled. Using system beep.[/yellow]")
            
        self._load_alarms()
        self.watcher_thread = threading.Thread(target=self._watcher, daemon=True)
        self.watcher_thread.start()

    def _load_alarms(self):
        with self.lock:
            self.alarms = []
            for alarm_data in self.storage.data["alarms"]:
                try:
                    if isinstance(alarm_data, dict):
                        alarm_data.setdefault("sound", None)
                        alarm_data.setdefault("volume", None)
                        alarm_data.setdefault("snooze_duration", 5)
                        alarm_data.setdefault("fade_in", False)
                        alarm = Alarm(**alarm_data)
                        self.alarms.append(alarm)
                except Exception as e:
                    console.print(f"[red]Error loading alarm: {e}[/red]")

    def _watcher(self):
        while self.running:
            time.sleep(0.5)
            now = datetime.datetime.now()
            with self.lock:
                alarms_to_check = list(self.alarms)
            for alarm in alarms_to_check:
                if alarm.is_active(now) and self.active_alarm is None:
                    self.active_alarm = alarm
                    self.alarm_thread = threading.Thread(target=self._ring, args=(alarm,))
                    self.alarm_thread.start()

    def _play_bell(self, alarm):
        sound_type = alarm.sound
        volume = (alarm.volume or 75) / 100.0
        try:
            if sound_type == "beep":
                beep_pattern = [0.2, 0.1, 0.2, 0.1, 0.5]
                for duration in beep_pattern * 3:
                    print("\a", end="", flush=True)
                    time.sleep(duration)
            elif sound_type == "speech":
                message = f"Wake up! {alarm.label}"
                subprocess.run(["espeak", "-s", "150", message], check=False)
            elif sound_type and sound_type.endswith((".wav", ".mp3", ".ogg")) and self.mixer_available:
                bell_path = os.path.join(BELL_DIR, sound_type)
                if os.path.isfile(bell_path):
                    pygame.mixer.music.load(bell_path)
                    if alarm.fade_in:
                        pygame.mixer.music.set_volume(0)
                        pygame.mixer.music.play(-1)
                        for i in range(30):
                            pygame.mixer.music.set_volume(volume * (i / 30))
                            time.sleep(0.1)
                    else:
                        pygame.mixer.music.set_volume(volume)
                        pygame.mixer.music.play(-1)
                    while pygame.mixer.music.get_busy() and self.active_alarm == alarm:
                        time.sleep(0.1)
                else:
                    console.print(f"[yellow]Sound file not found: {bell_path}[/yellow]")
                    self._play_bell(Alarm(0, 0, "", sound="beep"))
            else:
                for _ in range(5):
                    print("\a", end="", flush=True)
                    time.sleep(0.5)
        except Exception as error:
            console.print(f"[red]Error playing sound: {error}[/red]")
            print("\a\a\a", end="", flush=True)

    def _ring(self, alarm):
        alarm.dismiss()
        self.log_event(f"Alarm triggered: {alarm.label}")
        clear_screen()
        theme = get_current_theme()
        alarm_time = format_time(alarm.hour, alarm.minute)
        
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main", size=10),
            Layout(name="footer", size=3)
        )
        
        alarm_header = Panel(Align.center(Text("🔔 ALARM 🔔", style="bold red blink")), box=box.DOUBLE, border_style="red")
        layout["header"].update(alarm_header)
        
        alarm_info = Panel(
            Align.center(
                Text.from_markup(
                    f"[bold cyan]{alarm.label}[/bold cyan]\n"
                    f"[bold yellow]{alarm_time}[/bold yellow]\n"
                    f"[dim]Press ENTER to stop • Press 's' to snooze[/dim]"
                )
            ),
            box=box.ROUNDED, border_style=theme["accent"]
        )
        layout["main"].update(alarm_info)
        
        progress = Progress(
            SpinnerColumn("dots"), TextColumn("[progress.description]{task.description}"),
            BarColumn(bar_width=40), console=console, transient=True
        )
        task = progress.add_task("[red]Alarm Active", total=100)
        layout["footer"].update(Align.center(progress))
        
        sound_thread = threading.Thread(target=self._play_bell, args=(alarm,))
        sound_thread.start()
        
        with Live(layout, refresh_per_second=10) as live:
            try:
                for i in range(100):
                    progress.update(task, advance=1)
                    time.sleep(0.05)
                    
                    if check_keypress():
                        char = get_single_character()
                        if char.lower() == 's':
                            live.stop()
                            snooze_minutes = IntPrompt.ask("\n[bold]Snooze for how many minutes?[/bold]", default=alarm.snooze_duration)
                            if snooze_minutes > 0:
                                alarm.snooze(snooze_minutes)
                                show_spinner(f"Snoozing for {snooze_minutes} minutes", 2, "clock")
                                break
                        elif char == '\r' or char == '\n':
                            break
                            
                if self.active_alarm == alarm:
                    live.stop()
                    user_input = Prompt.ask("\n[green]ENTER[/green] to stop, or '[yellow]s[/yellow]' to snooze", default="").strip().lower()
                    if user_input == "s":
                        snooze_minutes = IntPrompt.ask("[bold]Snooze for how many minutes?[/bold]", default=alarm.snooze_duration)
                        if snooze_minutes > 0:
                            alarm.snooze(snooze_minutes)
                            show_spinner(f"Snoozing for {snooze_minutes} minutes", 2, "clock")
            except KeyboardInterrupt:
                pass
            finally:
                if self.mixer_available:
                    pygame.mixer.music.stop()
                if alarm.recurrence == "once" and alarm.snooze_until == 0:
                    with alarm.lock:
                        alarm.enabled = False
                self.active_alarm = None
                self.save_alarms()

    def log_event(self, message):
        event = {
            "time": datetime.datetime.now().isoformat(),
            "message": message
        }
        with self.storage.lock:
            self.storage.data["log"].append(event)
            self.storage.data["log"] = self.storage.data["log"][-1000:]
        self.storage.save()

    def save_alarms(self):
        with self.lock:
            alarms_data = []
            for alarm in self.alarms:
                alarm_dict = {
                    "hour": alarm.hour, "minute": alarm.minute, "label": alarm.label,
                    "recurrence": alarm.recurrence, "enabled": alarm.enabled,
                    "sound": alarm.sound, "volume": alarm.volume,
                    "snooze_duration": alarm.snooze_duration, "fade_in": alarm.fade_in
                }
                alarms_data.append(alarm_dict)
        with self.storage.lock:
            self.storage.data["alarms"] = alarms_data
        self.storage.save()

    def add_alarm(self, hour, minute, label, recurrence="once", sound=None,
                  volume=None, snooze_duration=5, fade_in=False):
        with self.lock:
            alarm = Alarm(hour, minute, label, recurrence, True,
                         sound, volume, snooze_duration, fade_in)
            self.alarms.append(alarm)
        self.save_alarms()
        storage.increment_stat("alarms_created")
        return alarm

    def delete_alarm(self, index):
        with self.lock:
            if 0 <= index < len(self.alarms):
                deleted = self.alarms.pop(index)
                self.save_alarms()
                return deleted
        return None

    def export_log(self):
        log_file_path = os.path.expanduser("~/radiant_alarm_log.csv")
        try:
            with self.storage.lock:
                log_data = self.storage.data["log"]
            with open(log_file_path, "w", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["time", "message"])
                writer.writeheader()
                writer.writerows(log_data)
            return log_file_path
        except IOError as error:
            raise IOError(f"Error exporting log: {error}")

    def get_statistics(self):
        with self.lock:
            total_alarms = len(self.alarms)
            enabled_alarms = sum(1 for a in self.alarms if a.enabled)
        with self.storage.lock:
            stats = self.storage.data["statistics"].copy()
        stats.update({
            "total_alarms": total_alarms,
            "enabled_alarms": enabled_alarms,
            "alarm_history_count": len(self.storage.data.get("alarm_history", []))
        })
        return stats

    def menu(self):
        while True:
            clear_screen()
            print_banner("⏰  A L A R M   C L O C K", animate=False)
            theme = get_current_theme()
            with self.lock:
                if self.alarms:
                    now = datetime.datetime.now()
                    next_alarms = []
                    for alarm in self.alarms:
                        if alarm.enabled:
                            try:
                                next_time = alarm.get_next_ring_time(now)
                                time_diff = next_time - now
                                next_alarms.append((alarm, next_time, time_diff))
                            except:
                                pass
                    if next_alarms:
                        next_alarms.sort(key=lambda x: x[2])
                        if next_alarms:
                            next_alarm, _, time_diff = next_alarms[0]
                            hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                            minutes, _ = divmod(remainder, 60)
                            next_alarm_text = Text.from_markup(
                                f"[dim]Next alarm:[/dim] [bold cyan]{next_alarm.label}[/bold cyan] "
                                f"[dim]in[/dim] [yellow]{hours}h {minutes}m[/yellow]"
                            )
                            console.print(Align.center(Panel(next_alarm_text, box=box.ROUNDED)))
                            console.print()
                            
            menu_items = [
                ("1", "➕ Set New Alarm", theme["primary"]),
                ("2", "📋 List Alarms", theme["primary"]),
                ("3", "✏️  Edit Alarm", theme["secondary"]),
                ("4", "🗑️  Delete Alarm", theme["danger"]),
                ("5", "📊 Statistics", theme["info"]),
                ("6", "📁 Export Log", theme["secondary"]),
                ("7", "🔙 Back", theme["dim"])
            ]
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Key", style="bold")
            table.add_column("Action")
            for key, action, color in menu_items:
                table.add_row(f"[{color}]{key}[/{color}]", f"[{color}]{action}[/{color}]")
            console.print(Align.center(table))
            
            choice = Prompt.ask("\n[bold]Select an option[/bold]", choices=[str(i) for i in range(1, 8)])
            if choice == "1": self._set_alarm_interactive()
            elif choice == "2": self._list_alarms()
            elif choice == "3": self._edit_alarm()
            elif choice == "4": self._delete_alarm_interactive()
            elif choice == "5": self._show_statistics()
            elif choice == "6": self._export_log_interactive()
            elif choice == "7": break

    def _set_alarm_interactive(self):
        clear_screen()
        print_banner("➕ SET NEW ALARM", animate=False)
        theme = get_current_theme()
        try:
            console.print("\n[bold]Enter alarm time:[/bold]")
            console.print("[dim]Format: HH:MM (24-hour) or HH:MM AM/PM (12-hour)[/dim]")
            time_input = Prompt.ask("Time")
            hour, minute = validate_time_string(time_input)

            label = Prompt.ask("\n[bold]Label[/bold]", default="Alarm")
            console.print("\n[bold]Recurrence:[/bold]")
            recurrence_options = [
                ("1", "Once", "📍", "Ring once then disable"),
                ("2", "Daily", "🔄", "Ring every day"),
                ("3", "Weekdays", "💼", "Monday to Friday"),
                ("4", "Weekends", "🏖️", "Saturday and Sunday")
            ]
            table = Table(show_header=False, box=box.ROUNDED)
            table.add_column("", width=3)
            table.add_column("Option", style=theme["primary"])
            table.add_column("", width=3)
            table.add_column("Description", style="dim")
            for num, name, icon, desc in recurrence_options:
                table.add_row(num, name, icon, desc)
            console.print(table)
            
            recurrence_choice = Prompt.ask("Choose recurrence", choices=["1", "2", "3", "4"], default="1")
            recurrence_map = {"1": "once", "2": "daily", "3": "weekdays", "4": "weekends"}
            recurrence = recurrence_map[recurrence_choice]
            
            if Confirm.ask("\n[bold]Configure advanced options?[/bold]", default=False):
                console.print("\n[bold]Sound:[/bold]")
                sounds = self._get_available_sounds()
                sound_table = Table(show_header=False, box=None)
                sound_table.add_column("", width=3)
                sound_table.add_column("Sound")
                for i, sound in enumerate(sounds, 1):
                    icon = "🔔" if sound == "beep" else "🗣️" if sound == "speech" else "🎵"
                    sound_table.add_row(str(i), f"{icon} {sound}")
                console.print(sound_table)
                sound_choice = IntPrompt.ask("Choose sound", default=1)
                sound = sounds[sound_choice - 1] if 1 <= sound_choice <= len(sounds) else None
                volume = IntPrompt.ask("\n[bold]Volume (0-100)[/bold]", default=storage.data["bell_volume"])
                volume = max(0, min(100, volume))
                snooze_duration = IntPrompt.ask("\n[bold]Snooze duration (minutes)[/bold]", default=5)
                fade_in = Confirm.ask("\n[bold]Enable fade-in effect?[/bold]", default=False)
            else:
                sound = None
                volume = None
                snooze_duration = 5
                fade_in = False
                
            alarm = self.add_alarm(hour, minute, label, recurrence, sound, volume, snooze_duration, fade_in)
            clear_screen()
            success_panel = Panel(
                Align.center(
                    Text.from_markup(
                        f"[bold green]✓ Alarm Set Successfully![/bold green]\n"
                        f"[cyan]Time:[/cyan] {format_time(hour, minute)}\n"
                        f"[cyan]Label:[/cyan] {label}\n"
                        f"[cyan]Recurrence:[/cyan] {recurrence.title()}\n"
                        f"[cyan]Sound:[/cyan] {alarm.sound}\n"
                        f"[cyan]Volume:[/cyan] {alarm.volume}%"
                    )
                ),
                box=box.DOUBLE, border_style="green", title="[bold]Alarm Created[/bold]"
            )
            console.print(success_panel)
            now = datetime.datetime.now()
            next_ring = alarm.get_next_ring_time(now)
            time_diff = next_ring - now
            hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
            minutes, _ = divmod(remainder, 60)
            console.print(f"\n[dim]Alarm will ring in {hours} hours and {minutes} minutes[/dim]")
            show_spinner("Saving", 1, "dots")
        except (ValueError, KeyboardInterrupt) as e:
            console.print(f"\n[red]Error: {str(e) if isinstance(e, ValueError) else 'Operation cancelled'}[/red]")
        input("\nPress Enter to continue...")

    def _list_alarms(self):
        clear_screen()
        print_banner("📋 ALARM LIST", animate=False)
        with self.lock:
            if not self.alarms:
                console.print(Panel("[yellow]No alarms set[/yellow]", box=box.ROUNDED))
            else:
                enabled_alarms = [a for a in self.alarms if a.enabled]
                disabled_alarms = [a for a in self.alarms if not a.enabled]
                if enabled_alarms:
                    self._display_alarm_table("Active Alarms", enabled_alarms, "green")
                if disabled_alarms:
                    console.print()
                    self._display_alarm_table("Disabled Alarms", disabled_alarms, "red")
        input("\nPress Enter to continue...")

    def _display_alarm_table(self, title, alarms, color):
        theme = get_current_theme()
        table = Table(title=title, box=box.ROUNDED, title_style=f"bold {color}")
        table.add_column("ID", style="dim", width=4)
        table.add_column("Time", style="cyan")
        table.add_column("Label", style="white")
        table.add_column("Recur", style="yellow")
        table.add_column("Sound", style="magenta")
        table.add_column("Next Ring", style="green")
        now = datetime.datetime.now()
        for i, alarm in enumerate(alarms, 1):
            try:
                next_ring = alarm.get_next_ring_time(now)
                time_diff = next_ring - now
                hours, remainder = divmod(int(time_diff.total_seconds()), 3600)
                minutes, _ = divmod(remainder, 60)
                next_ring_str = f"{hours}h {minutes}m"
            except:
                next_ring_str = "N/A"
            table.add_row(
                str(i), format_time(alarm.hour, alarm.minute), alarm.label,
                alarm.recurrence.title(), alarm.sound, next_ring_str
            )
        console.print(table)

    def _edit_alarm(self):
        clear_screen()
        print_banner("✏️ EDIT ALARM", animate=False)
        with self.lock:
            if not self.alarms:
                console.print(Panel("[yellow]No alarms to edit[/yellow]", box=box.ROUNDED))
                input("\nPress Enter to continue...")
                return
            self._display_alarm_table("Select Alarm to Edit", self.alarms, "blue")
        try:
            index = IntPrompt.ask("\nEnter alarm ID to edit") - 1
            with self.lock:
                if not (0 <= index < len(self.alarms)):
                    raise ValueError("Invalid alarm ID")
                alarm = self.alarms[index]
            while True:
                clear_screen()
                print_banner(f"✏️ EDITING: {alarm.label}", animate=False)
                info_table = Table(show_header=False, box=box.SIMPLE)
                info_table.add_column("Property", style="cyan")
                info_table.add_column("Value", style="white")
                info_table.add_row("Time", format_time(alarm.hour, alarm.minute))
                info_table.add_row("Label", alarm.label)
                info_table.add_row("Recurrence", alarm.recurrence.title())
                info_table.add_row("Enabled", "Yes" if alarm.enabled else "No")
                info_table.add_row("Sound", alarm.sound)
                info_table.add_row("Volume", f"{alarm.volume}%")
                info_table.add_row("Snooze Duration", f"{alarm.snooze_duration} min")
                info_table.add_row("Fade In", "Yes" if alarm.fade_in else "No")
                console.print(Align.center(info_table))
                
                console.print("\n[bold]What would you like to edit?[/bold]")
                options = ["1. Time", "2. Label", "3. Recurrence", "4. Enable/Disable",
                          "5. Sound", "6. Volume", "7. Snooze Duration", "8. Fade In", "9. Done"]
                for opt in options:
                    console.print(opt)
                choice = Prompt.ask("Choice", choices=[str(i) for i in range(1, 10)])
                
                if choice == "1":
                    time_input = Prompt.ask("New time (HH:MM)")
                    hour, minute = validate_time_string(time_input)
                    alarm.hour = hour
                    alarm.minute = minute
                elif choice == "2":
                    alarm.label = Prompt.ask("New label", default=alarm.label)
                elif choice == "3":
                    console.print("1. Once  2. Daily  3. Weekdays  4. Weekends")
                    rec_choice = Prompt.ask("Recurrence", choices=["1", "2", "3", "4"])
                    rec_map = {"1": "once", "2": "daily", "3": "weekdays", "4": "weekends"}
                    alarm.recurrence = rec_map[rec_choice]
                elif choice == "4":
                    alarm.enabled = not alarm.enabled
                    status = "enabled" if alarm.enabled else "disabled"
                    console.print(f"[green]Alarm {status}[/green]")
                elif choice == "5":
                    sounds = self._get_available_sounds()
                    for i, s in enumerate(sounds, 1):
                        console.print(f"{i}. {s}")
                    sound_choice = IntPrompt.ask("Choose sound")
                    if 1 <= sound_choice <= len(sounds):
                        alarm.sound = sounds[sound_choice - 1]
                elif choice == "6":
                    alarm.volume = IntPrompt.ask("Volume (0-100)", default=alarm.volume)
                    alarm.volume = max(0, min(100, alarm.volume))
                elif choice == "7":
                    alarm.snooze_duration = IntPrompt.ask("Snooze duration (minutes)", default=alarm.snooze_duration)
                elif choice == "8":
                    alarm.fade_in = not alarm.fade_in
                    status = "enabled" if alarm.fade_in else "disabled"
                    console.print(f"[green]Fade in {status}[/green]")
                elif choice == "9":
                    break
                self.save_alarms()
                if choice != "9":
                    show_spinner("Saving changes", 0.5)
            console.print("\n[green]✓ Alarm updated successfully[/green]")
        except (ValueError, IndexError) as e:
            console.print(f"\n[red]Error: {e}[/red]")
        input("\nPress Enter to continue...")

    def _delete_alarm_interactive(self):
        clear_screen()
        print_banner("🗑️ DELETE ALARM", animate=False)
        with self.lock:
            if not self.alarms:
                console.print(Panel("[yellow]No alarms to delete[/yellow]", box=box.ROUNDED))
                input("\nPress Enter to continue...")
                return
            self._display_alarm_table("Select Alarm to Delete", self.alarms, "red")
        try:
            index = IntPrompt.ask("\nEnter alarm ID to delete (0 to cancel)") - 1
            if index == -1:
                return
            deleted = self.delete_alarm(index)
            if deleted:
                console.print(f"\n[green]✓ Deleted alarm: {deleted.label}[/green]")
                show_spinner("Updating", 0.5)
            else:
                console.print("\n[red]Invalid alarm ID[/red]")
        except (ValueError, KeyboardInterrupt):
            console.print("\n[yellow]Deletion cancelled[/yellow]")
        input("\nPress Enter to continue...")

    def _show_statistics(self):
        clear_screen()
        print_banner("📊 ALARM STATISTICS", animate=False)
        stats = self.get_statistics()
        theme = get_current_theme()
        panels = []
        
        overview = Panel(
            Text.from_markup(
                f"[bold]Total Alarms:[/bold] {stats['total_alarms']}\n"
                f"[bold]Active Alarms:[/bold] {stats['enabled_alarms']}\n"
                f"[bold]Alarms Created:[/bold] {stats['alarms_created']}\n"
                f"[bold]Alarms Dismissed:[/bold] {stats['alarms_dismissed']}\n"
                f"[bold]Alarms Snoozed:[/bold] {stats['alarms_snoozed']}"
            ),
            title="Overview", box=box.ROUNDED, border_style=theme["primary"]
        )
        panels.append(overview)
        
        with storage.lock:
            history_data = storage.data.get("alarm_history", [])
        if history_data:
            history_items = []
            for entry in history_data[-5:]:
                try:
                    dismissed_time = datetime.datetime.fromisoformat(entry["dismissed_at"])
                    time_ago = datetime.datetime.now() - dismissed_time
                    if time_ago.days > 0:
                        ago_str = f"{time_ago.days}d ago"
                    elif time_ago.seconds > 3600:
                        ago_str = f"{time_ago.seconds // 3600}h ago"
                    else:
                        ago_str = f"{time_ago.seconds // 60}m ago"
                    history_items.append(f"• {entry['label']} ({ago_str})")
                except Exception:
                    history_items.append(f"• {entry['label']} (Unknown time)")
            history_panel = Panel(
                "\n".join(history_items), title="Recent Alarms",
                box=box.ROUNDED, border_style=theme["secondary"]
            )
            panels.append(history_panel)
            
        if panels:
            console.print(Columns(panels, equal=True, expand=True))
        else:
            console.print("[dim]No statistics available yet.[/dim]")
            
        if stats['alarms_dismissed'] > 0:
            console.print("\n[bold]Alarm Activity:[/bold]")
            total = stats['alarms_dismissed'] + stats['alarms_snoozed']
            if total > 0:
                dismissed_pct = stats['alarms_dismissed'] / total * 100
                snoozed_pct = stats['alarms_snoozed'] / total * 100
                bar_width = 40
                dismissed_width = int(bar_width * dismissed_pct / 100)
                snoozed_width = int(bar_width * snoozed_pct / 100)
                console.print(f"Dismissed: [green]{'█' * dismissed_width}{'░' * (bar_width - dismissed_width)}[/green] {dismissed_pct:.1f}%")
                console.print(f"Snoozed:   [yellow]{'█' * snoozed_width}{'░' * (bar_width - snoozed_width)}[/yellow] {snoozed_pct:.1f}%")
        input("\nPress Enter to continue...")

    def _export_log_interactive(self):
        clear_screen()
        print_banner("📁 EXPORT LOG", animate=False)
        try:
            filepath = self.export_log()
            console.print(f"[green]✓ Log exported successfully to:[/green]\n{filepath}")
            if Confirm.ask("\n[bold]Open file location?[/bold]", default=False):
                if sys.platform == "darwin":
                    subprocess.run(["open", "-R", filepath])
                elif sys.platform == "linux":
                    subprocess.run(["xdg-open", os.path.dirname(filepath)])
                elif sys.platform == "win32":
                    subprocess.run(["explorer", "/select,", filepath])
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
        input("\nPress Enter to continue...")

    def _get_available_sounds(self):
        sounds = ["beep", "speech"]
        for ext in ["*.wav", "*.mp3", "*.ogg"]:
            sounds.extend([os.path.basename(f) for f in glob.glob(os.path.join(BELL_DIR, ext))])
        return sounds

# --- Enhanced World Clock ---
class WorldClock:
    MAJOR_CITIES = {
        "UTC": {"lat": 51.4769, "lon": -0.0005, "city": "London"},
        "America/New_York": {"lat": 40.7128, "lon": -74.0060, "city": "New York"},
        "America/Los_Angeles": {"lat": 34.0522, "lon": -118.2437, "city": "Los Angeles"},
        "America/Chicago": {"lat": 41.8781, "lon": -87.6298, "city": "Chicago"},
        "America/Toronto": {"lat": 43.6532, "lon": -79.3832, "city": "Toronto"},
        "America/Mexico_City": {"lat": 19.4326, "lon": -99.1332, "city": "Mexico City"},
        "America/Sao_Paulo": {"lat": -23.5505, "lon": -46.6333, "city": "São Paulo"},
        "Europe/London": {"lat": 51.5074, "lon": -0.1278, "city": "London"},
        "Europe/Paris": {"lat": 48.8566, "lon": 2.3522, "city": "Paris"},
        "Europe/Berlin": {"lat": 52.5200, "lon": 13.4050, "city": "Berlin"},
        "Europe/Moscow": {"lat": 55.7558, "lon": 37.6173, "city": "Moscow"},
        "Africa/Cairo": {"lat": 30.0444, "lon": 31.2357, "city": "Cairo"},
        "Asia/Dubai": {"lat": 25.2048, "lon": 55.2708, "city": "Dubai"},
        "Asia/Mumbai": {"lat": 19.0760, "lon": 72.8777, "city": "Mumbai"},
        "Asia/Shanghai": {"lat": 31.2304, "lon": 121.4737, "city": "Shanghai"},
        "Asia/Tokyo": {"lat": 35.6762, "lon": 139.6503, "city": "Tokyo"},
        "Asia/Singapore": {"lat": 1.3521, "lon": 103.8198, "city": "Singapore"},
        "Australia/Sydney": {"lat": -33.8688, "lon": 151.2093, "city": "Sydney"},
    }

    @classmethod
    def get_all_timezones(cls):
        try:
            return list(available_timezones())
        except NameError:
            return list(cls.MAJOR_CITIES.keys())

    @classmethod
    def get_time_for_zone(cls, timezone_name):
        try:
            return datetime.datetime.now(ZoneInfo(timezone_name))
        except Exception:
            return datetime.datetime.now()

    @classmethod
    def get_weather_emoji(cls, hour):
        if 6 <= hour < 12: return "🌅"
        elif 12 <= hour < 17: return "☀️"
        elif 17 <= hour < 20: return "🌇"
        else: return "🌙"

    @classmethod
    def show_world_map(cls):
        clear_screen()
        print_banner("🗺️ WORLD TIME MAP", animate=False)
        world_map = """
        ┌─────────────────────────────────────────────────────────────┐
        │     🌍 WORLD TIME ZONES                                     │
        │                                                             │
        │  LA ──── CHI ─── NYC ─── LON ─── BER ─── MOS                │
        │  🌃      🌆      🌃      🌙      🌙      🌙                 │
        │                                                             │
        │                DXB ─── MUM ─── SHA ─── TOK ─── SYD          │
        │                🌅      ☀️        🌇      🌃      🌅           │
        └─────────────────────────────────────────────────────────────┘
        """
        theme = get_current_theme()
        console.print(Panel(world_map, box=box.ROUNDED, border_style=theme["primary"]))
        cities = [
            ("LA", "America/Los_Angeles"), ("NYC", "America/New_York"),
            ("LON", "Europe/London"), ("TOK", "Asia/Tokyo"),
            ("SYD", "Australia/Sydney")
        ]
        time_row = ""
        for name, tz in cities:
            now = cls.get_time_for_zone(tz)
            time_str = now.strftime("%H:%M")
            time_row += f"{name}: {time_str}  "
        console.print(Align.center(Text(time_row, style=theme["info"])))
        input("\nPress Enter to continue...")

    @classmethod
    def show_timezone_converter(cls):
        clear_screen()
        print_banner("🔄 TIME CONVERTER", animate=False)
        theme = get_current_theme()
        try:
            console.print("[bold]Convert from:[/bold]")
            source_tz = cls._pick_timezone_interactive()
            if not source_tz: return
            
            console.print("\n[bold]Convert to:[/bold]")
            target_tz = cls._pick_timezone_interactive()
            if not target_tz: return
            
            console.print("\n[bold]Enter time in source timezone (HH:MM):[/bold]")
            time_input = Prompt.ask("Time")
            hour, minute = validate_time_string(time_input)
            
            today = datetime.date.today()
            source_time = datetime.datetime.combine(today, datetime.time(hour, minute)).replace(tzinfo=ZoneInfo(source_tz))
            target_time = source_time.astimezone(ZoneInfo(target_tz))
            
            result_panel = Panel(
                Text.from_markup(
                    f"[bold]{source_tz}[/bold]\n"
                    f"{format_time(hour, minute)}\n\n"
                    f"[bold]{target_tz}[/bold]\n"
                    f"{target_time.strftime('%H:%M')}"
                ),
                title="Conversion Result", box=box.DOUBLE, border_style=theme["accent"]
            )
            console.print("\n")
            console.print(Align.center(result_panel))
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
        input("\nPress Enter to continue...")

    @classmethod
    def _pick_timezone_interactive(cls):
        timezones = cls.get_all_timezones()
        if not timezones:
            console.print("[red]No timezones available.[/red]")
            return None
            
        # Optional sorting to easily find common ones
        timezones.sort()
        index = 0
        while True:
            clear_screen()
            print_banner("🌍 PICK A TIMEZONE", animate=False)
            theme = get_current_theme()
            console.print("[dim]Use 'n' (Next), 'p' (Prev) to scroll, '/' to search, 'q' to back, or type number to select[/dim]")
            console.print("-" * 60, style=theme["dim"])
            display_timezones = timezones[index:index+20]
            
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("No.", width=3)
            table.add_column("Timezone")
            for i, tz in enumerate(display_timezones, start=index+1):
                table.add_row(str(i), tz)
            console.print(table)
            
            action = Prompt.ask("Action").strip().lower()
            if action == 'n':
                index = min(len(timezones) - 20, index + 20)
            elif action == 'p':
                index = max(0, index - 20)
            elif action.startswith('/'):
                search_term = action[1:].strip()
                if search_term:
                    timezones = [z for z in cls.get_all_timezones() if search_term in z.lower()]
                    index = 0
                else:
                    timezones = cls.get_all_timezones()
            elif action == 'q':
                return None
            elif action.isdigit():
                sel_idx = int(action) - 1
                if 0 <= sel_idx < len(timezones):
                    return timezones[sel_idx]

    @classmethod
    def show_multiple_timezones(cls):
        clear_screen()
        print_banner("🌎 MULTIPLE TIMEZONES", animate=False)
        theme = get_current_theme()
        with storage.lock:
            zones_to_show = storage.data["favorite_timezones"] if storage.data["favorite_timezones"] else list(cls.MAJOR_CITIES.keys())[:9]
        if not zones_to_show:
            console.print("[yellow]No zones to display. Add some favorites![/yellow]")
            input("\nPress Enter to continue...")
            return
            
        panels = []
        for tz in zones_to_show:
            try:
                city_name = cls.MAJOR_CITIES.get(tz, {}).get("city", tz.split("/")[-1].replace("_", " "))
                now = cls.get_time_for_zone(tz)
                time_str = now.strftime("%H:%M:%S")
                emoji = cls.get_weather_emoji(now.hour)
                panel_content = f"[bold]{city_name}[/bold]\n{time_str}\n{emoji}"
                panel = Panel(panel_content, box=box.ROUNDED, border_style=theme["primary"])
                panels.append(panel)
            except Exception:
                pass 
                
        if panels:
            console.print(Columns(panels, equal=True, expand=True))
        else:
            console.print("[red]Could not display any timezones.[/red]")
        input("\nPress Enter to continue...")

    @classmethod
    def menu(cls):
        while True:
            clear_screen()
            print_banner("🌍 WORLD CLOCK", animate=False)
            theme = get_current_theme()
            menu_items = [
                ("1", "🗺️  World Map", theme["primary"]),
                ("2", "🔄 Timezone Converter", theme["primary"]),
                ("3", "🌎 Multiple Timezones", theme["primary"]),
                ("4", "🔙 Back", theme["dim"])
            ]
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Key", style="bold")
            table.add_column("Action")
            for key, action, color in menu_items:
                table.add_row(f"[{color}]{key}[/{color}]", f"[{color}]{action}[/{color}]")
            console.print(Align.center(table))
            
            choice = Prompt.ask("\n[bold]Select an option[/bold]", choices=["1", "2", "3", "4"])
            if choice == "1": cls.show_world_map()
            elif choice == "2": cls.show_timezone_converter()
            elif choice == "3": cls.show_multiple_timezones()
            elif choice == "4": break

# --- Enhanced Timer ---
class Timer:
    @staticmethod
    def countdown():
        try:
            minutes = get_validated_input("Enter minutes for countdown: ", validate_strictly_positive_integer)
        except (ValueError, KeyboardInterrupt):
            console.print("\n[red]Invalid input or cancelled.[/red]")
            time.sleep(1)
            return
            
        total_seconds = minutes * 60
        paused = False
        pause_start_time = None
        theme = get_current_theme()
        
        with Live(console=console, auto_refresh=False) as live:
            while total_seconds > 0 or paused:
                if not paused:
                    hours, remainder = divmod(total_seconds, 3600)
                    mins, secs = divmod(remainder, 60)
                    time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"

                    progress_percentage = 1.0 - (total_seconds / (minutes * 60))
                    progress_bar = Progress(
                        TextColumn("[progress.description]{task.description}"),
                        BarColumn(bar_width=40),
                        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                        TimeRemainingColumn(), console=console
                    )
                    task_id = progress_bar.add_task("Countdown", total=1.0)
                    progress_bar.update(task_id, completed=progress_percentage)

                    panel_content = f"[bold red]{time_str}[/bold red]\n"
                    panel = Panel(panel_content, title="[blink]⏳ Countdown[/blink]", expand=False, border_style="red", box=box.DOUBLE)
                    layout = Layout()
                    layout.split_column(Layout(Align.center(panel)), Layout(Align.center(progress_bar)))
                    live.update(layout)
                    live.refresh()

                    if check_keypress():
                        char = get_single_character()
                        if char.lower() == 'p':
                            paused = True
                            pause_start_time = time.time()

                    if not paused:
                        time.sleep(1)
                        total_seconds -= 1
                else:
                    elapsed_pause = int(time.time() - pause_start_time)
                    pause_str = f"[yellow]PAUSED ({elapsed_pause}s)[/yellow]\nPress 'r' to resume."
                    panel = Panel(pause_str, title="[blink]⏳ Countdown[/blink]", expand=False, border_style="yellow", box=box.DOUBLE)
                    live.update(Align.center(panel))
                    live.refresh()

                    time.sleep(0.1)
                    if check_keypress():
                        char = get_single_character()
                        if char.lower() == 'r':
                            paused = False
                            # Compensate to not skip seconds during pause
                            time.sleep(0.9) 

        clear_screen()
        console.print(Panel("[bold red blink]🔔 TIME'S UP!!![/bold red blink]", expand=False, box=box.DOUBLE, border_style="red"))
        alarm_manager = AlarmManager(storage)
        alarm_manager._play_bell(Alarm(0,0,"Timer Up", sound="beep"))
        input("Press Enter to stop alarm...")
        storage.increment_stat("timers_completed")

    @staticmethod
    def stopwatch():
        start_time = time.time()
        laps = []
        console.print("[green] Stopwatch started. 'l': Lap, 's': Stop [/green]")
        try:
            theme = get_current_theme()
            with Live(console=console, auto_refresh=False) as live:
                while True:
                    elapsed = time.time() - start_time
                    hours, remainder = divmod(elapsed, 3600)
                    mins, secs = divmod(remainder, 60)
                    time_str = f"{int(hours):02d}:{int(mins):02d}:{secs:06.3f}"

                    panel_content = f"[bold green]{time_str}[/bold green]"
                    if laps:
                        panel_content += "\n[dim]--- Laps ---[/dim]\n"
                        for i, lap_time in enumerate(laps[-5:], max(1, len(laps)-4)):
                            panel_content += f"[dim]{i}. {lap_time}[/dim]\n"

                    panel = Panel(panel_content.rstrip(), title="[blink]⏱ Stopwatch[/blink]", expand=False, border_style="green", box=box.ROUNDED)
                    live.update(Align.center(panel))
                    live.refresh()
                    
                    time.sleep(0.05)
                    if check_keypress():
                        char = get_single_character().lower()
                        if char == 's':
                            break
                        elif char == 'l':
                            lap_elapsed = time.time() - start_time
                            lap_hours, lap_rem = divmod(lap_elapsed, 3600)
                            lap_mins, lap_secs = divmod(lap_rem, 60)
                            lap_str = f"{int(lap_hours):02d}:{int(lap_mins):02d}:{lap_secs:06.3f}"
                            laps.append(lap_str)

        except KeyboardInterrupt:
            pass
        finally:
            elapsed_final = time.time() - start_time
            hours_f, remainder_f = divmod(elapsed_final, 3600)
            mins_f, secs_f = divmod(remainder_f, 60)
            time_str_f = f"{int(hours_f):02d}:{int(mins_f):02d}:{secs_f:06.3f}"
            console.print(f"\n[green] Stopwatch stopped at {time_str_f}[/green]")
            if laps:
                console.print("[blue]--- Final Laps ---[/blue]")
                for i, lap_time in enumerate(laps, 1):
                    console.print(f"[blue]{i}. {lap_time}[/blue]")
            input("Press Enter to continue...")

# --- Settings ---
class Settings:
    @staticmethod
    def menu(storage_instance):
        bells = ["beep", "speech"]
        for ext in ["*.wav", "*.mp3", "*.ogg"]:
            bells.extend([os.path.basename(f) for f in glob.glob(os.path.join(BELL_DIR, ext))])
            
        while True:
            clear_screen()
            print_banner("⚙️ SETTINGS", animate=False)
            theme = get_current_theme()
            with storage_instance.lock:
                console.print(f"Theme: [bold]{storage_instance.data['theme']}[/bold]   Sound: [bold]{storage_instance.data['sound']}[/bold]   Volume: [bold]{storage_instance.data['bell_volume']}%[/bold]", style=theme["info"])
                console.print(f"Show Quotes: [bold]{'Yes' if storage_instance.data['show_quotes'] else 'No'}[/bold]   24H Format: [bold]{'Yes' if storage_instance.data['24hour_format'] else 'No'}[/bold]", style=theme["info"])
                console.print(f"Animations: [bold]{'On' if storage_instance.data['animations_enabled'] else 'Off'}[/bold]", style=theme["info"])

            console.print("1. Change Theme", style=theme["primary"])
            console.print("2. Pick Sound", style=theme["primary"])
            console.print("3. Set Volume", style=theme["primary"])
            console.print("4. Toggle 24H Format", style=theme["primary"])
            console.print("5. Toggle Quotes", style=theme["primary"])
            console.print("6. Toggle Animations", style=theme["primary"])
            console.print("7. Back", style=theme["primary"])
            choice = Prompt.ask("[bold]Select an option[/bold]", choices=["1", "2", "3", "4", "5", "6", "7"])

            if choice == "1":
                 theme_names = list(theme_manager.get_all_themes().keys())
                 current_theme_name = storage.data.get("theme", "cyberpunk")
                 console.print("--- Available Themes ---", style=theme["secondary"])
                 table = Table(show_header=False, box=None)
                 table.add_column("Sel", width=2)
                 table.add_column("No.", width=3)
                 table.add_column("Theme")

                 for index, name in enumerate(theme_names, 1):
                     marker = ">>" if name == current_theme_name else "  "
                     table.add_row(marker, str(index), name)
                 console.print(table)

                 try:
                     theme_choice = get_validated_input("Select theme (number): ",
                                                       validate_integer_range(1, len(theme_names)),
                                                       "Invalid selection.")
                     selected_theme_name = theme_names[theme_choice - 1]
                     with storage_instance.lock:
                         storage_instance.data["theme"] = selected_theme_name
                     storage_instance.save()
                     console.print(f"[green]Theme set to '{selected_theme_name}'.[/green]")
                     new_theme = theme_manager.get_theme(selected_theme_name)
                     preview_text = Text("Theme Preview: This is sample text.", style=new_theme["primary"])
                     console.print(Panel(preview_text, expand=False, border_style=new_theme["panel_border"]))
                     time.sleep(1.5)
                 except (ValueError, KeyboardInterrupt):
                     console.print("\n[yellow]Theme selection cancelled.[/yellow]")
                     time.sleep(1)

            elif choice == "2":
                console.print("--- Available Sounds ---", style=theme["secondary"])
                table = Table(show_header=False, box=None)
                table.add_column("Sel", width=2)
                table.add_column("No.", width=3)
                table.add_column("Sound")

                for index, bell in enumerate(bells, 1):
                    marker = ">>" if bell == storage.data["sound"] else "  "
                    table.add_row(marker, str(index), bell)
                console.print(table)

                try:
                    bell_choice = get_validated_input("Select sound (number): ",
                                                      validate_integer_range(1, len(bells)),
                                                      "Invalid selection.")
                    selected_bell = bells[bell_choice - 1]
                    with storage_instance.lock:
                        storage_instance.data["sound"] = selected_bell
                    storage_instance.save()
                    console.print(f"[green]Sound set to '{selected_bell}'.[/green]")
                    time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    console.print("\n[yellow]Sound selection cancelled.[/yellow]")
                    time.sleep(1)

            elif choice == "3":
                try:
                    new_volume = get_validated_input("Enter volume (0-100): ",
                                                     validate_integer_range(0, 100),
                                                     "Volume must be between 0 and 100.")
                    with storage_instance.lock:
                        storage_instance.data["bell_volume"] = new_volume
                    storage_instance.save()
                    console.print(f"[green]Volume set to {new_volume}%.[/green]")
                    time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    console.print("\n[yellow]Volume setting cancelled.[/yellow]")
                    time.sleep(1)

            elif choice == "4":
                 with storage_instance.lock:
                     storage_instance.data["24hour_format"] = not storage_instance.data["24hour_format"]
                 storage_instance.save()
                 status = "enabled" if storage.data["24hour_format"] else "disabled"
                 console.print(f"[green]24H Format {status}.[/green]")
                 time.sleep(1)

            elif choice == "5":
                 with storage_instance.lock:
                     storage_instance.data["show_quotes"] = not storage_instance.data["show_quotes"]
                 storage_instance.save()
                 status = "enabled" if storage.data["show_quotes"] else "disabled"
                 console.print(f"[green]Quotes {status}.[/green]")
                 time.sleep(1)

            elif choice == "6":
                 with storage_instance.lock:
                     storage_instance.data["animations_enabled"] = not storage_instance.data["animations_enabled"]
                 storage_instance.save()
                 status = "enabled" if storage.data["animations_enabled"] else "disabled"
                 console.print(f"[green]Animations {status}.[/green]")
                 time.sleep(1)

            elif choice == "7":
                break
            else:
                console.print("[red]Invalid choice.[/red]")
                time.sleep(1)

# --- Utility Functions ---
def daily_quote():
    quotes = [
        "The bad news is time flies. The good news is you're the pilot. - Michael Altshuler",
        "Time is an illusion. Lunchtime doubly so. - Douglas Adams",
        "Lost time is never found again. - Benjamin Franklin",
        "You will never find time for anything. You must make it. - Charles Buxton",
        "The future is something which everyone reaches at the rate of sixty minutes an hour. - C.S. Lewis",
        "Time is really the only valuable thing a man can spend. - T.M. Luhrmann",
        "The key is in not spending time, but in investing it. - Stephen R. Covey",
        "Time is the most valuable thing a man can spend. - Theophrastus",
        "Don't watch the clock; do what it does. Keep going. - Sam Levenson"
    ]
    return random.choice(quotes)

def load_plugins():
    plugins = []
    for plugin_file in glob.glob(os.path.join(PLUGIN_DIR, "*.py")):
        plugin_name = os.path.splitext(os.path.basename(plugin_file))[0]
        if plugin_name.startswith("__"): continue
        try:
            plugin_directory = os.path.dirname(plugin_file)
            if plugin_directory not in sys.path:
                sys.path.insert(0, plugin_directory)
            spec = __import__(plugin_name, fromlist=[""])
            if hasattr(spec, "plugin_menu") and callable(getattr(spec, "plugin_menu")):
                plugins.append((plugin_name, spec.plugin_menu))
            else:
                console.print(f"[yellow]Warning: Plugin '{plugin_name}' does not have a 'plugin_menu' function.[/yellow]")
        except Exception as error:
            console.print(f"[red]Error loading plugin '{plugin_name}': {error}[/red]")
    return plugins

# --- Main Application ---
def main():
    def signal_handler(sig, frame):
        console.print("\n[bold green]Bye![/bold green]")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    plugins = load_plugins()
    alarm_manager = AlarmManager(storage)
    
    while True:
        clear_screen()
        print_banner("🕒 R A D I A N T   C L O C K", animate=True)
        theme = get_current_theme()
        if storage.data.get("show_quotes", True):
            quote_panel = Panel(Align.center(Text(daily_quote(), style=theme["dim"])), box=box.SIMPLE)
            console.print(quote_panel)
        console.print("")
        
        menu_items = [
            ("1", "⏰ Alarm Clock", theme["primary"]),
            ("2", "🌍 World Clock", theme["primary"]),
            ("3", "⏳ Countdown Timer", theme["primary"]),
            ("4", "⏱ Stopwatch", theme["primary"]),
            ("5", "⚙️ Settings", theme["primary"]),
        ]
        
        for idx, (name, _) in enumerate(plugins, start=6):
            menu_items.append((str(idx), f"🔌 Plugin: {name}", theme["info"]))
        menu_items.append((str(6 + len(plugins)), "🚪 Quit", theme["danger"]))

        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_column("Key", style="bold")
        table.add_column("Action")
        for key, action, color in menu_items:
            table.add_row(f"[{color}]{key}[/{color}]", f"[{color}]{action}[/{color}]")
        console.print(Align.center(table))

        choice = Prompt.ask("\n[bold]Select an option[/bold]", choices=[str(i) for i in range(1, 7 + len(plugins))])

        try:
            choice_number = int(choice)
            if choice_number == 1:
                alarm_manager.menu()
            elif choice_number == 2:
                WorldClock.menu()
            elif choice_number == 3:
                Timer.countdown()
            elif choice_number == 4:
                Timer.stopwatch()
            elif choice_number == 5:
                Settings.menu(storage)
            elif 6 <= choice_number < 6 + len(plugins):
                _, plugin_function = plugins[choice_number - 6]
                try:
                    plugin_function()
                except Exception as error:
                    console.print(f"[red]Plugin error: {error}[/red]")
                    input("Press Enter to continue...")
            elif choice_number == 6 + len(plugins):
                console.print("[yellow]Shutting down...[/yellow]")
                alarm_manager.running = False
                alarm_manager.watcher_thread.join(timeout=2)
                if alarm_manager.mixer_available:
                    pygame.mixer.quit()
                storage.save()
                break
            else:
                console.print("[red]Invalid option.[/red]")
                time.sleep(1)
        except ValueError:
            console.print("[red]Please enter a number.[/red]")
            time.sleep(1)
        except KeyboardInterrupt:
            console.print("\n[yellow]Received interrupt signal. Exiting...[/yellow]")
            alarm_manager.running = False
            alarm_manager.watcher_thread.join(timeout=2)
            if alarm_manager.mixer_available:
                pygame.mixer.quit()
            storage.save()
            break

if __name__ == "__main__":
    main()
