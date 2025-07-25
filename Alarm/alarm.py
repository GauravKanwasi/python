#!/usr/bin/env python3
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

SAVE_FILE = os.path.expanduser("~/.radiant_clock.json")
PLUGIN_DIR = os.path.expanduser("~/.radiant_plugins")
BELL_DIR = os.path.expanduser("~/.radiant_bell")

os.makedirs(PLUGIN_DIR, exist_ok=True)
os.makedirs(BELL_DIR, exist_ok=True)

class C:
    CYAN, GREEN, RED, YELLOW, DIM, RST, BOLD = ("\033[96m", "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[0m", "\033[1m")
    GRADIENT_COLORS = ["\033[38;5;196m", "\033[38;5;208m", "\033[38;5;226m", "\033[38;5;046m", "\033[38;5;047m"]

def clear_screen():
    print("\033[2J\033[H", end="")

def print_banner(text, color=C.BOLD):
    print(color + text.center(60) + C.RST)

def show_spinner(message, duration=1):
    for char in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        print(f"\r{message} {char}", end="", flush=True)
        time.sleep(0.1)
        duration -= 0.1
        if duration <= 0:
            print("\r" + " " * (len(message) + 2) + "\r", end="")
            break

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
        user_input = input(prompt).strip()
        try:
            result = validator_function(user_input)
            return result
        except ValueError:
            print(error_message)

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
            print(f"Error loading save file: {error}. Using defaults.")

    def save(self):
        with self.lock:
            try:
                with open(self.filepath, "w") as file:
                    json.dump(self.data, file, indent=2)
            except IOError as error:
                print(f"Error saving: {error}")

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
        volume = self.storage.data["bell_volume"]

        try:
            if sound_type == "beep":
                for _ in range(3):
                    print("\a", end="", flush=True)
                    time.sleep(0.5)
            elif sound_type == "speech":
                subprocess.run(["espeak", "Wake up!"], check=True)
            elif sound_type.endswith(".wav"):
                bell_path = os.path.join(BELL_DIR, sound_type)
                if os.path.isfile(bell_path):
                    volume_scaled = int(volume * 655.36)
                    subprocess.run(["paplay", "--volume", str(volume_scaled), bell_path], check=True)
                else:
                    print(f"Sound file not found: {bell_path}. Using beep.")
                    print("\a\a\a", end="")
            else:
                 print("\a\a\a", end="")
        except (subprocess.CalledProcessError, FileNotFoundError) as error:
            print(f"Error playing sound ({sound_type}): {error}. Using beep.")
            print("\a\a\a", end="")

    def _ring(self, alarm):
        alarm.reset_snooze()
        self.log_event(f"Alarm fired: {alarm.label}")

        clear_screen()
        print_banner("🔔  A L A R M", C.RED)
        print(f"{alarm.label}  {alarm.hour:02d}:{alarm.minute:02d}".center(60))

        bar_segment = "█" * 12
        for color in C.GRADIENT_COLORS:
            print(color + bar_segment + C.RST, end="", flush=True)
            time.sleep(0.6)
        print()

        self._play_bell()

        try:
            user_input = input("\nPress ENTER to stop, or type 's X' to snooze for X minutes: ").strip().lower()
            if user_input.startswith("s "):
                try:
                    snooze_minutes = int(user_input.split()[1])
                    if snooze_minutes > 0:
                        alarm.snooze(snooze_minutes)
                        show_spinner("Snoozing", 1)
                        print(f"Snoozed for {snooze_minutes} minutes.")
                    else:
                        print("Invalid snooze time. Stopping alarm.")
                        if alarm.recurrence == "once":
                            with alarm.lock:
                                alarm.enabled = False
                except (IndexError, ValueError):
                    print("Invalid snooze command. Stopping alarm.")
                    if alarm.recurrence == "once":
                        with alarm.lock:
                            alarm.enabled = False
            else:
                if alarm.recurrence == "once":
                    with alarm.lock:
                        alarm.enabled = False
                self.save_alarms()

        except (KeyboardInterrupt, EOFError):
            if alarm.recurrence == "once":
                with alarm.lock:
                    alarm.enabled = False
            self.save_alarms()
            print("\nAlarm stopped (interrupted).")

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
            print(f"Log exported successfully to {log_file_path}")
        except IOError as error:
            print(f"Error exporting log: {error}")
        input("Press Enter to continue...")

    def menu(self):
        while True:
            clear_screen()
            print_banner("⏰  A L A R M   C L O C K")
            print("1. Set alarm")
            print("2. List alarms")
            print("3. Delete alarm")
            print("4. Export log")
            print("5. Back")
            choice = input("> ").strip()

            if choice == "1":
                try:
                    time_input = input("Time (HH:MM or HH:MM AM/PM): ").strip()
                    hour, minute = get_validated_input("", lambda s: validate_time_string(s), "Invalid time format. Use HH:MM or HH:MM AM/PM.")
                    label = input("Label (default 'Alarm'): ").strip() or "Alarm"
                    recurrence_options = {"1": "once", "2": "daily", "3": "weekdays", "4": "weekends"}
                    print("Recur options: 1. once  2. daily  3. weekdays  4. weekends")
                    recurrence_choice = input("Choose recurrence (default 1): ").strip()
                    recurrence = recurrence_options.get(recurrence_choice, "once")

                    with self.lock:
                        self.alarms.append(Alarm(hour, minute, label, recurrence))
                    self.save_alarms()
                    show_spinner("Alarm Saved", 1)
                    print("Alarm set successfully.")
                    time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    print("\nInvalid input or operation cancelled.")
                    time.sleep(1)

            elif choice == "2":
                with self.lock:
                    if not self.alarms:
                        print("No alarms set.")
                    else:
                        print("--- Alarms ---")
                        for index, alarm in enumerate(self.alarms, 1):
                            status = "✓" if alarm.enabled else "✗"
                            print(f"{index}. {status} {alarm.hour:02d}:{alarm.minute:02d} '{alarm.label}' ({alarm.recurrence})")
                input("Press Enter to continue...")

            elif choice == "3":
                with self.lock:
                    if not self.alarms:
                        print("No alarms to delete.")
                        time.sleep(1)
                        continue
                    print("--- Delete Alarm ---")
                    for index, alarm in enumerate(self.alarms, 1):
                         status = "✓" if alarm.enabled else "✗"
                         print(f"{index}. {status} {alarm.hour:02d}:{alarm.minute:02d} '{alarm.label}' ({alarm.recurrence})")
                try:
                    index = get_validated_input("Enter alarm number to delete (0 to cancel): ",
                                                validate_integer_range(0, len(self.alarms)),
                                                "Invalid alarm number.")
                    if index > 0:
                        with self.lock:
                            deleted_alarm = self.alarms.pop(index - 1)
                        self.save_alarms()
                        print(f"Deleted alarm: {deleted_alarm.label}")
                        time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    print("\nDeletion cancelled or invalid input.")
                    time.sleep(1)

            elif choice == "4":
                self.export_log()

            elif choice == "5":
                break
            else:
                print("Invalid choice.")
                time.sleep(1)

class GlobeClock:
    try:
        with open("/usr/share/zoneinfo/zone1970.tab", 'r') as file:
            TIMEZONES = [line.split("\t")[2] for line in file if not line.startswith("#")]
    except (FileNotFoundError, IOError):
        print("Warning: Could not load zone1970.tab. Using default zones.")
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
             print("No zones available.")
             input("Press Enter...")
             return None

        index = 0
        while True:
            clear_screen()
            print_banner("🌍  PICK A TIME-ZONE")
            print("↑/↓: Scroll  /: Search  f: Toggle Favorite  q: Back")
            print("-" * 60)

            display_timezones = timezones[index:index+20]
            for i, timezone in enumerate(display_timezones, start=index+1):
                mark = "♥" if timezone in storage.data["favorite_timezones"] else " "
                print(f"{i:>3} {mark} {timezone}")

            char = get_single_character()
            if char == "\x1b":
                char += sys.stdin.read(2)
                if char == "\x1b[A":
                    index = max(0, index - 1)
                elif char == "\x1b[B":
                    index = min(len(timezones) - 20, index + 1)
            elif char == "/":
                search_term = input("\nSearch term: ").strip().lower()
                if search_term:
                    timezones = [z for z in cls.TIMEZONES if search_term in z.lower()]
                    index = 0
                else:
                    timezones = storage.data["favorite_timezones"] if favorites_only and storage.data["favorite_timezones"] else cls.TIMEZONES
            elif char == "f" and not favorites_only:
                if display_timezones:
                     selected_timezone = display_timezones[min(len(display_timezones)-1, max(0, index - (index // 20) * 20))]
                     if 0 <= index < len(display_timezones):
                         selected_timezone = display_timezones[index]
                         with storage.lock:
                            if selected_timezone in storage.data["favorite_timezones"]:
                                storage.data["favorite_timezones"].remove(selected_timezone)
                                action = "removed from"
                            else:
                                storage.data["favorite_timezones"].append(selected_timezone)
                                action = "added to"
                         storage.save()
                         print(f"'{selected_timezone}' {action} favorites.")
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
            print_banner(timezone, C.CYAN)
            previous_timezone = os.environ.get("TZ")
            os.environ["TZ"] = timezone
            time.tzset()
            now_local = datetime.datetime.now()
            if previous_timezone:
                os.environ["TZ"] = previous_timezone
            else:
                os.unsetenv("TZ")
            time.tzset()

            print(now_local.strftime("%Y-%m-%d  %H:%M:%S").center(60))
            weather_info = cls._get_weather(city)
            print(C.DIM + weather_info + C.RST)
            print("\n[r] Re-pick zone  [f] Show favorites only  [q] Quit  [any key] Refresh")
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
            print("\nInvalid input or cancelled.")
            time.sleep(1)
            return

        total_seconds = minutes * 60
        while total_seconds > 0:
            clear_screen()
            print_banner(f"⏳  {total_seconds // 3600:02d}:{(total_seconds % 3600) // 60:02d}:{total_seconds % 60:02d}", C.RED)
            time.sleep(1)
            total_seconds -= 1

        clear_screen()
        print_banner("🔔  TIME'S UP", C.RED)
        alarm_manager = AlarmManager(storage)
        alarm_manager._play_bell()
        input("Press Enter to stop alarm...")

    @staticmethod
    def stopwatch():
        start_time = time.time()
        print(" Stopwatch started. Press any key to stop. ")
        try:
            while True:
                elapsed = int(time.time() - start_time)
                clear_screen()
                print_banner(f"⏱  {elapsed // 3600:02d}:{(elapsed // 60) % 60:02d}:{elapsed % 60:02d}", C.GREEN)
                print("\nPress any key to stop...")
                get_single_character()
                break
        except KeyboardInterrupt:
            pass
        finally:
            elapsed_final = int(time.time() - start_time)
            print(f"\n Stopwatch stopped at {elapsed_final // 3600:02d}:{(elapsed_final // 60) % 60:02d}:{elapsed_final % 60:02d}")

def ntp_sync():
    clear_screen()
    print_banner("⏲  NTP SYNC", C.YELLOW)
    try:
        show_spinner("Querying NTP", 2)
        result = subprocess.run(["sudo", "ntpdate", "-s", "pool.ntp.org"], capture_output=True, text=True, check=True)
        print("System time updated successfully ✓")
    except subprocess.CalledProcessError as error:
        print(f"Could not sync: ntpdate failed. {error}")
    except FileNotFoundError:
        print("Could not sync: 'ntpdate' command not found. Is it installed?")
    except KeyboardInterrupt:
        print("\nNTP sync cancelled.")
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
                print(f"Warning: Plugin '{plugin_name}' does not have a 'plugin_menu' function.")
        except Exception as error:
            print(f"Error loading plugin '{plugin_name}': {error}")
    return plugins

class Settings:
    @staticmethod
    def menu(storage_instance):
        bells = ["beep", "speech"] + [os.path.basename(f) for f in glob.glob(os.path.join(BELL_DIR, "*.wav"))]

        while True:
            clear_screen()
            print_banner("⚙️  SETTINGS")
            with storage_instance.lock:
                print(f"Theme: {storage_instance.data['theme']}   Sound: {storage_instance.data['sound']}   Volume: {storage_instance.data['bell_volume']}%")
            print("1. Toggle theme")
            print("2. Pick sound")
            print("3. Set volume")
            print("4. NTP sync")
            print("5. Back")
            choice = input("> ").strip()

            if choice == "1":
                with storage_instance.lock:
                    storage_instance.data["theme"] = "light" if storage_instance.data["theme"] == "dark" else "dark"
                storage_instance.save()
                show_spinner("Theme Saved", 0.5)
                print(f"Theme set to {storage.data['theme']}.")
                time.sleep(0.5)

            elif choice == "2":
                print("--- Available Sounds ---")
                for index, bell in enumerate(bells, 1):
                    marker = ">>" if bell == storage.data["sound"] else "  "
                    print(f"{marker} {index}. {bell}")
                try:
                    bell_choice = get_validated_input("Select sound (number): ",
                                                      validate_integer_range(1, len(bells)),
                                                      "Invalid selection.")
                    selected_bell = bells[bell_choice - 1]
                    with storage_instance.lock:
                        storage_instance.data["sound"] = selected_bell
                    storage_instance.save()
                    print(f"Sound set to '{selected_bell}'.")
                    time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    print("\nSound selection cancelled.")
                    time.sleep(1)

            elif choice == "3":
                try:
                    new_volume = get_validated_input("Enter volume (0-100): ",
                                                     validate_integer_range(0, 100),
                                                     "Volume must be between 0 and 100.")
                    with storage_instance.lock:
                        storage_instance.data["bell_volume"] = new_volume
                    storage_instance.save()
                    print(f"Volume set to {new_volume}%.")
                    time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    print("\nVolume setting cancelled.")
                    time.sleep(1)

            elif choice == "4":
                ntp_sync()

            elif choice == "5":
                break
            else:
                print("Invalid choice.")
                time.sleep(1)

def main():
    def signal_handler(sig, frame):
        print("\nBye!")
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    plugins = load_plugins()
    alarm_manager = AlarmManager(storage)

    while True:
        clear_screen()
        print_banner("🕒  R A D I A N T   C L O C K")
        print(C.DIM + daily_quote().center(60) + C.RST)
        print("\n1. Alarm Clock")
        print("2. World Clock")
        print("3. Countdown Timer")
        print("4. Stopwatch")
        print("5. Settings")
        for idx, (name, _) in enumerate(plugins, start=6):
            print(f"{idx}. Plugin: {name}")
        print(f"{6 + len(plugins)}. Quit")

        choice = input("> ").strip()
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
                    print(f"Plugin error: {error}")
                    input("Press Enter to continue...")
            elif choice_number == 6 + len(plugins):
                print("Shutting down...")
                alarm_manager.running = False
                alarm_manager.watcher_thread.join(timeout=2)
                break
            else:
                print("Invalid option.")
                time.sleep(1)
        except ValueError:
            print("Please enter a number.")
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nReceived interrupt signal. Exiting...")
            alarm_manager.running = False
            alarm_manager.watcher_thread.join(timeout=2)
            break

if __name__ == "__main__":
    main()
