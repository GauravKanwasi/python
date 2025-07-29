import os
import json
import time
import datetime
import signal
import threading
import sys
import tty
import termios
import subprocess
import shutil
import csv
import glob
import random
import textwrap
import itertools
import pygame
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.spinner import Spinner
from rich.progress import Progress, BarColumn, TextColumn
from rich.prompt import Prompt, IntPrompt
from rich.align import Align

SAVE_FILE = os.path.expanduser("~/.radiant_clock.json")
PLUGIN_DIR = os.path.expanduser("~/.radiant_plugins")
BELL_DIR = os.path.expanduser("~/.radiant_bell")
os.makedirs(PLUGIN_DIR, exist_ok=True)
os.makedirs(BELL_DIR, exist_ok=True)

console = Console()

class C:
    CYAN, GREEN, RED, YELLOW, DIM, RST, BOLD = ("\033[96m", "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[0m", "\033[1m")
    RICH_THEMES = {
        "dark": {
            "primary": "cyan",
            "secondary": "green",
            "warning": "yellow",
            "danger": "red",
            "info": "blue",
            "dim": "bright_black",
            "banner": "bold magenta on black"
        },
        "light": {
            "primary": "blue",
            "secondary": "green",
            "warning": "orange3",
            "danger": "red",
            "info": "blue",
            "dim": "grey50",
            "banner": "bold blue on white"
        }
    }

def get_current_theme():
    theme_name = storage.data.get("theme", "dark")
    return C.RICH_THEMES.get(theme_name, C.RICH_THEMES["dark"])

def clear_screen():
    console.clear()

def print_banner(text, style=None):
    theme = get_current_theme()
    if style is None:
        style = theme.get("banner", "")
    panel = Panel(Align.center(Text(text, style=style)), expand=False, box=box.HEAVY)
    console.print(Align.center(panel))

def show_spinner(message, duration=1):
    with console.status(f"[bold green]{message}...", spinner="dots8Bit"):
        time.sleep(duration)

def get_single_character():
    file_descriptor = sys.stdin.fileno()
    old_settings = termios.tcgetattr(file_descriptor)
    try:
        tty.setraw(file_descriptor)
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)
    return char

def get_validated_input(prompt, validator_function, error_message="Invalid input. Please try again."):
    while True:
        user_input = Prompt.ask(prompt)
        try:
            result = validator_function(user_input)
            return result
        except ValueError:
            console.print(f"[red]{error_message}[/red]")

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

def validate_positive_integer(string_input):
    value = int(string_input)
    if value < 0:
        raise ValueError("Value must be positive")
    return value

class Storage:
    DEFAULT_DATA = {
        "alarms": [],
        "theme": "dark",
        "sound": "beep",
        "favorite_timezones": [],
        "bell_volume": 75,
        "voice_wake": False,
        "log": []
    }
    def __init__(self, filepath=SAVE_FILE):
        self.filepath = filepath
        self.data = self.DEFAULT_DATA.copy()
        self.lock = threading.Lock()
        self.load()

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
            try:
                with open(self.filepath, "w") as file:
                    json.dump(self.data, file, indent=2)
            except IOError as error:
                console.print(f"[red]Error saving: {error}[/red]")

storage = Storage()

class Alarm:
    def __init__(self, hour, minute, label, recurrence="once", enabled=True):
        self.hour = hour
        self.minute = minute
        self.label = label
        self.recurrence = recurrence
        self.enabled = enabled
        self.snooze_until = 0
        self.lock = threading.Lock()

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
            return current_time >= self.get_next_ring_time(current_time)

    def snooze(self, minutes):
        with self.lock:
            self.snooze_until = int(time.time()) + (minutes * 60)

    def reset_snooze(self):
        with self.lock:
            self.snooze_until = 0

class AlarmManager:
    def __init__(self, storage_instance):
        self.storage = storage_instance
        self.alarms = [Alarm(**alarm_data) for alarm_data in self.storage.data["alarms"]]
        self.lock = threading.Lock()
        self.running = True
        self.watcher_thread = threading.Thread(target=self._watcher, daemon=True)
        self.watcher_thread.start()
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()

    def log_event(self, message):
        event = {
            "time": datetime.datetime.now().isoformat(),
            "message": message
        }
        with self.storage.lock:
            self.storage.data["log"].append(event)
        self.storage.save()

    def _watcher(self):
        while self.running:
            time.sleep(1)
            now = datetime.datetime.now()
            with self.lock:
                alarms_to_check = list(self.alarms)
            for alarm in alarms_to_check:
                if alarm.is_active(now):
                    self._ring(alarm)

    def _play_bell(self):
        sound_type = self.storage.data["sound"]
        volume = self.storage.data["bell_volume"] / 100.0

        try:
            if sound_type == "beep":
                for _ in range(3):
                    print("\a", end="", flush=True)
                    time.sleep(0.5)
            elif sound_type == "speech":
                 subprocess.run(["espeak", "Wake up!"], check=True)
            elif sound_type.endswith((".wav", ".mp3", ".ogg")):
                bell_path = os.path.join(BELL_DIR, sound_type)
                if os.path.isfile(bell_path):
                    pygame.mixer.music.load(bell_path)
                    pygame.mixer.music.set_volume(volume)
                    pygame.mixer.music.play()
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.1)
                else:
                    console.print(f"[yellow]Sound file not found: {bell_path}. Using beep.[/yellow]")
                    print("\a\a\a", end="")
            else:
                 console.print(f"[yellow]Unknown sound type or file: {sound_type}. Using beep.[/yellow]")
                 print("\a\a\a", end="")

        except (subprocess.CalledProcessError, FileNotFoundError, pygame.error) as error:
            console.print(f"[red]Error playing sound ({sound_type}): {error}. Using beep.[/red]")
            print("\a\a\a", end="")


    def _ring(self, alarm):
        alarm.reset_snooze()
        self.log_event(f"Alarm fired: {alarm.label}")
        clear_screen()

        theme = get_current_theme()
        console.print(Panel("[bold red blink]🔔 ALARM!!![/bold red blink]", expand=False, box=box.DOUBLE, border_style="red"))
        console.print(Align.center(f"[bold]{alarm.label}[/bold]  [cyan]{alarm.hour:02d}:{alarm.minute:02d}[/cyan]"))

        bar_text = Text("█" * 60)
        bar_text.stylize(theme["danger"])
        console.print(bar_text)

        self._play_bell()

        try:
            user_input = Prompt.ask("\nPress [green]ENTER[/green] to stop, or type '[yellow]s X[/yellow]' to snooze for X minutes", default="", show_default=False).strip().lower()
            if user_input.startswith("s "):
                try:
                    snooze_minutes = int(user_input.split()[1])
                    if snooze_minutes > 0:
                        alarm.snooze(snooze_minutes)
                        show_spinner("Snoozing", 1)
                        console.print(f"[green]Snoozed for {snooze_minutes} minutes.[/green]")
                    else:
                        console.print("[yellow]Invalid snooze time. Stopping alarm.[/yellow]")
                        if alarm.recurrence == "once":
                            with alarm.lock:
                                alarm.enabled = False
                except (IndexError, ValueError):
                    console.print("[red]Invalid snooze command. Stopping alarm.[/red]")
                    if alarm.recurrence == "once":
                        with alarm.lock:
                            alarm.enabled = False
            else:
                if alarm.recurrence == "once":
                    with alarm.lock:
                        alarm.enabled = False
                self.save_alarms()
        except KeyboardInterrupt:
            if alarm.recurrence == "once":
                with alarm.lock:
                    alarm.enabled = False
            self.save_alarms()
            console.print("\n[yellow]Alarm stopped (interrupted).[/yellow]")


    def save_alarms(self):
        with self.lock:
            alarms_data = [vars(alarm) for alarm in self.alarms]
        with self.storage.lock:
            self.storage.data["alarms"] = alarms_data
        self.storage.save()

    def export_log(self):
        log_file_path = os.path.expanduser("~/radiant_log.csv")
        try:
            with self.storage.lock:
                log_data = self.storage.data["log"]
            with open(log_file_path, "w", newline="") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=["time", "message"])
                writer.writeheader()
                writer.writerows(log_data)
            console.print(f"[green]Log exported successfully to {log_file_path}[/green]")
        except IOError as error:
            console.print(f"[red]Error exporting log: {error}[/red]")
        input("Press Enter to continue...")

    def menu(self):
        while True:
            clear_screen()
            print_banner("⏰  A L A R M   C L O C K")
            theme = get_current_theme()
            console.print("1. Set alarm", style=theme["primary"])
            console.print("2. List alarms", style=theme["primary"])
            console.print("3. Delete alarm", style=theme["primary"])
            console.print("4. Export log", style=theme["primary"])
            console.print("5. Back", style=theme["primary"])
            choice = Prompt.ask("[bold]Select an option[/bold]", choices=["1", "2", "3", "4", "5"])

            if choice == "1":
                try:
                    time_input = Prompt.ask("Time (HH:MM or HH:MM AM/PM)")
                    hour, minute = get_validated_input("", lambda s: validate_time_string(s), "Invalid time format. Use HH:MM or HH:MM AM/PM.")
                    label = Prompt.ask("Label", default="Alarm") or "Alarm"
                    recurrence_options = {"1": "once", "2": "daily", "3": "weekdays", "4": "weekends"}
                    console.print("Recur options: 1. once  2. daily  3. weekdays  4. weekends")
                    recurrence_choice = Prompt.ask("Choose recurrence", choices=["1", "2", "3", "4"], default="1")
                    recurrence = recurrence_options.get(recurrence_choice, "once")
                    with self.lock:
                        self.alarms.append(Alarm(hour, minute, label, recurrence))
                    self.save_alarms()
                    show_spinner("Saving Alarm", 1)
                    console.print("[green]Alarm set successfully.[/green]")
                    time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    console.print("\n[red]Invalid input or operation cancelled.[/red]")
                    time.sleep(1)

            elif choice == "2":
                with self.lock:
                    if not self.alarms:
                        console.print("[yellow]No alarms set.[/yellow]")
                    else:
                        table = Table(title="Alarms", box=box.ROUNDED, style=get_current_theme()["primary"])
                        table.add_column("No.", style="dim", width=3)
                        table.add_column("Status")
                        table.add_column("Time")
                        table.add_column("Label")
                        table.add_column("Recurrence")

                        for index, alarm in enumerate(self.alarms, 1):
                            status = "✓" if alarm.enabled else "✗"
                            status_style = "green" if alarm.enabled else "red"
                            table.add_row(
                                str(index),
                                f"[{status_style}]{status}[/{status_style}]",
                                f"{alarm.hour:02d}:{alarm.minute:02d}",
                                alarm.label,
                                alarm.recurrence
                            )
                        console.print(table)
                input("Press Enter to continue...")

            elif choice == "3":
                with self.lock:
                    if not self.alarms:
                        console.print("[yellow]No alarms to delete.[/yellow]")
                        time.sleep(1)
                        continue
                    table = Table(title="Delete Alarm", box=box.ROUNDED, style=get_current_theme()["warning"])
                    table.add_column("No.", style="dim", width=3)
                    table.add_column("Status")
                    table.add_column("Time")
                    table.add_column("Label")
                    table.add_column("Recurrence")

                    for index, alarm in enumerate(self.alarms, 1):
                         status = "✓" if alarm.enabled else "✗"
                         status_style = "green" if alarm.enabled else "red"
                         table.add_row(
                             str(index),
                             f"[{status_style}]{status}[/{status_style}]",
                             f"{alarm.hour:02d}:{alarm.minute:02d}",
                             alarm.label,
                             alarm.recurrence
                         )
                    console.print(table)

                try:
                    index = get_validated_input("Enter alarm number to delete (0 to cancel): ",
                                                validate_integer_range(0, len(self.alarms)),
                                                "Invalid alarm number.")
                    if index > 0:
                        with self.lock:
                            deleted_alarm = self.alarms.pop(index - 1)
                        self.save_alarms()
                        console.print(f"[green]Deleted alarm: {deleted_alarm.label}[/green]")
                        time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    console.print("\n[yellow]Deletion cancelled or invalid input.[/yellow]")
                    time.sleep(1)

            elif choice == "4":
                self.export_log()
            elif choice == "5":
                break
            else:
                console.print("[red]Invalid choice.[/red]")
                time.sleep(1)

class GlobeClock:
    try:
        with open("/usr/share/zoneinfo/zone1970.tab", 'r') as file:
            TIMEZONES = [line.split("\t")[2] for line in file if not line.startswith("#")]
    except (FileNotFoundError, IOError):
        console.print("[yellow]Warning: Could not load zone1970.tab. Using default zones.[/yellow]")
        TIMEZONES = ["UTC", "Europe/London", "America/New_York", "Asia/Tokyo", "Australia/Sydney"]

    @staticmethod
    def _get_weather(city):
        try:
            result = subprocess.run(
                ["curl", "-m", "5", "-s", f"wttr.in/{city}?format=%c+%t"],
                capture_output=True, text=True, check=True, timeout=6
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return "Weather data unavailable"

    @classmethod
    def pick_timezone(cls, favorites_only=False):
        timezones = storage.data["favorite_timezones"] if favorites_only and storage.data["favorite_timezones"] else cls.TIMEZONES
        if not timezones:
             console.print("[red]No zones available.[/red]")
             input("Press Enter...")
             return None
        index = 0
        while True:
            clear_screen()
            print_banner("🌍  PICK A TIME-ZONE")
            theme = get_current_theme()
            console.print("[dim]↑/↓: Scroll  /: Search  f: Toggle Favorite  q: Back[/dim]")
            console.print("-" * 60, style=theme["dim"])
            display_timezones = timezones[index:index+20]
            table = Table(show_header=False, box=None, padding=(0, 1))
            table.add_column("No.", width=3)
            table.add_column("Fav")
            table.add_column("Timezone")

            for i, timezone in enumerate(display_timezones, start=index+1):
                mark = "♥" if timezone in storage.data["favorite_timezones"] else " "
                table.add_row(str(i), mark, timezone)
            console.print(table)

            char = get_single_character()
            if char == "\x1b":
                char += sys.stdin.read(2)
                if char == "\x1b[A":
                    index = max(0, index - 1)
                elif char == "\x1b[B":
                    index = min(len(timezones) - 20, index + 1)
            elif char == "/":
                search_term = Prompt.ask("\nSearch term").strip().lower()
                if search_term:
                    timezones = [z for z in cls.TIMEZONES if search_term in z.lower()]
                    index = 0
                else:
                    timezones = storage.data["favorite_timezones"] if favorites_only and storage.data["favorite_timezones"] else cls.TIMEZONES
            elif char == "f" and not favorites_only:
                if display_timezones:
                     selected_index_in_display = min(len(display_timezones)-1, max(0, index - (index // 20) * 20))
                     if 0 <= selected_index_in_display < len(display_timezones):
                         selected_timezone = display_timezones[selected_index_in_display]
                         with storage.lock:
                            if selected_timezone in storage.data["favorite_timezones"]:
                                storage.data["favorite_timezones"].remove(selected_timezone)
                                action = "removed from"
                            else:
                                storage.data["favorite_timezones"].append(selected_timezone)
                                action = "added to"
                         storage.save()
                         console.print(f"'{selected_timezone}' {action} favorites.", style="green")
                         time.sleep(0.5)
            elif char == "\r":
                if display_timezones:
                    selected_index_in_display = min(len(display_timezones)-1, max(0, index - (index // 20) * 20))
                    if 0 <= selected_index_in_display < len(display_timezones):
                        return display_timezones[selected_index_in_display]
            elif char.lower() == "q":
                return None

    @classmethod
    def show(cls):
        timezone = cls.pick_timezone()
        if not timezone:
            return
        city = timezone.split("/")[-1].replace("_", " ")
        while True:
            clear_screen()
            print_banner(timezone, style=get_current_theme()["primary"])
            previous_timezone = os.environ.get("TZ")
            os.environ["TZ"] = timezone
            time.tzset()
            now_local = datetime.datetime.now()
            if previous_timezone:
                os.environ["TZ"] = previous_timezone
            else:
                os.unsetenv("TZ")
            time.tzset()
            console.print(now_local.strftime("%Y-%m-%d  %H:%M:%S").center(60), style="bold")
            weather_info = cls._get_weather(city)
            console.print(f"[dim]{weather_info}[/dim]")
            console.print("\n[r] Re-pick zone  [f] Show favorites only  [q] Quit  [any key] Refresh")
            char = get_single_character().lower()
            if char == "q":
                break
            elif char == "r":
                cls.show()
                break
            elif char == "f":
                timezone = cls.pick_timezone(favorites_only=True)
                if timezone:
                    city = timezone.split("/")[-1].replace("_", " ")

class Timer:
    @staticmethod
    def countdown():
        try:
            minutes = get_validated_input("Enter minutes for countdown: ", validate_positive_integer)
        except (ValueError, KeyboardInterrupt):
            console.print("\n[red]Invalid input or cancelled.[/red]")
            time.sleep(1)
            return
        total_seconds = minutes * 60

        theme = get_current_theme()
        with Live(console=console, auto_refresh=False) as live:
            while total_seconds > 0:
                hours, remainder = divmod(total_seconds, 3600)
                mins, secs = divmod(remainder, 60)
                time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"

                panel = Panel(f"[bold red]{time_str}[/bold red]", title="[blink]⏳ Countdown[/blink]", expand=False, border_style="red", box=box.DOUBLE)
                live.update(Align.center(panel))
                live.refresh()

                time.sleep(1)
                total_seconds -= 1

        clear_screen()
        console.print(Panel("[bold red blink]🔔 TIME'S UP!!![/bold red blink]", expand=False, box=box.DOUBLE, border_style="red"))
        alarm_manager = AlarmManager(storage)
        alarm_manager._play_bell()
        input("Press Enter to stop alarm...")

    @staticmethod
    def stopwatch():
        start_time = time.time()
        console.print("[green] Stopwatch started. Press any key to stop. [/green]")
        try:
            theme = get_current_theme()
            with Live(console=console, auto_refresh=False) as live:
                while True:
                    elapsed = int(time.time() - start_time)
                    hours, remainder = divmod(elapsed, 3600)
                    mins, secs = divmod(remainder, 60)
                    time_str = f"{hours:02d}:{mins:02d}:{secs:02d}"

                    panel = Panel(f"[bold green]{time_str}[/bold green]", title="[blink]⏱ Stopwatch[/blink]", expand=False, border_style="green", box=box.ROUNDED)
                    live.update(Align.center(panel))
                    live.refresh()

                    time.sleep(0.1)
                    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                         get_single_character()
                         break

        except KeyboardInterrupt:
            pass
        finally:
            elapsed_final = int(time.time() - start_time)
            hours_f, remainder_f = divmod(elapsed_final, 3600)
            mins_f, secs_f = divmod(remainder_f, 60)
            time_str_f = f"{hours_f:02d}:{mins_f:02d}:{secs_f:02d}"
            console.print(f"\n[green] Stopwatch stopped at {time_str_f}[/green]")

def ntp_sync():
    clear_screen()
    print_banner("⏲  NTP SYNC", style=get_current_theme()["warning"])
    try:
        show_spinner("Querying NTP", 2)
        result = subprocess.run(["sudo", "ntpdate", "-s", "pool.ntp.org"], capture_output=True, text=True, check=True)
        console.print("[green]System time updated successfully ✓[/green]")
    except subprocess.CalledProcessError as error:
        console.print(f"[red]Could not sync: ntpdate failed. {error}[/red]")
    except FileNotFoundError:
        console.print("[red]Could not sync: 'ntpdate' command not found. Is it installed?[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]NTP sync cancelled.[/yellow]")
    input("Press Enter to continue...")

def daily_quote():
    quotes = [
        "The bad news is time flies. The good news is you're the pilot. - Michael Altshuler",
        "Time is an illusion. Lunchtime doubly so. - Douglas Adams",
        "Lost time is never found again. - Benjamin Franklin",
        "You will never find time for anything. You must make it. - Charles Buxton",
        "The future is something which everyone reaches at the rate of sixty minutes an hour. - C.S. Lewis",
        "Time is really the only valuable thing a man can spend. - T.M. Luhrmann"
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

class Settings:
    @staticmethod
    def menu(storage_instance):
        bells = ["beep", "speech"] + [os.path.basename(f) for f in glob.glob(os.path.join(BELL_DIR, "*.wav"))]
        bells += [os.path.basename(f) for f in glob.glob(os.path.join(BELL_DIR, "*.mp3"))]
        bells += [os.path.basename(f) for f in glob.glob(os.path.join(BELL_DIR, "*.ogg"))]
        while True:
            clear_screen()
            print_banner("⚙️  SETTINGS")
            theme = get_current_theme()
            with storage_instance.lock:
                console.print(f"Theme: [bold]{storage_instance.data['theme']}[/bold]   Sound: [bold]{storage_instance.data['sound']}[/bold]   Volume: [bold]{storage_instance.data['bell_volume']}%[/bold]", style=theme["info"])

            console.print("1. Toggle theme", style=theme["primary"])
            console.print("2. Pick sound", style=theme["primary"])
            console.print("3. Set volume", style=theme["primary"])
            console.print("4. NTP sync", style=theme["primary"])
            console.print("5. Back", style=theme["primary"])
            choice = Prompt.ask("[bold]Select an option[/bold]", choices=["1", "2", "3", "4", "5"])

            if choice == "1":
                with storage_instance.lock:
                    storage_instance.data["theme"] = "light" if storage_instance.data["theme"] == "dark" else "dark"
                storage_instance.save()
                show_spinner("Saving Theme", 0.5)
                console.print(f"[green]Theme set to {storage.data['theme']}.[/green]")
                time.sleep(0.5)

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
                ntp_sync()
            elif choice == "5":
                break
            else:
                console.print("[red]Invalid choice.[/red]")
                time.sleep(1)

def main():
    def signal_handler(sig, frame):
        console.print("\n[bold green]Bye![/bold green]")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
    except pygame.error as e:
        console.print(f"[yellow]Warning: Could not initialize pygame mixer: {e}[/yellow]")

    plugins = load_plugins()
    alarm_manager = AlarmManager(storage)
    while True:
        clear_screen()
        print_banner("🕒  R A D I A N T   C L O C K")
        theme = get_current_theme()
        console.print(f"[{theme['dim']}]{daily_quote().center(60)}[/{theme['dim']}]")
        console.print("")
        console.print("1. Alarm Clock", style=theme["primary"])
        console.print("2. World Clock", style=theme["primary"])
        console.print("3. Countdown Timer", style=theme["primary"])
        console.print("4. Stopwatch", style=theme["primary"])
        console.print("5. Settings", style=theme["primary"])
        for idx, (name, _) in enumerate(plugins, start=6):
            console.print(f"{idx}. Plugin: {name}", style=theme["info"])
        console.print(f"{6 + len(plugins)}. Quit", style=theme["danger"])
        choice = Prompt.ask("[bold]Select an option[/bold]", choices=[str(i) for i in range(1, 7 + len(plugins))])

        try:
            choice_number = int(choice)
            if choice_number == 1:
                alarm_manager.menu()
            elif choice_number == 2:
                GlobeClock.show()
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
                pygame.mixer.quit()
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
            pygame.mixer.quit()
            break

if __name__ == "__main__":
    try:
        import select
    except ImportError:
        select = None
        console.print("[yellow]Note: Non-blocking keypress for stopwatch might not work on this system.[/yellow]")
    main()
