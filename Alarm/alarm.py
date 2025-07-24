import os, json, time, datetime, signal, threading, sys, tty, termios, subprocess, shutil, csv, glob, random, textwrap, itertools

# ───────────────────────────────────────────────
# Configuration & Constants
# ───────────────────────────────────────────────
SAVE_FILE = os.path.expanduser("~/.radiant_clock.json")
PLUGIN_DIR = os.path.expanduser("~/.radiant_plugins")
BELL_DIR   = os.path.expanduser("~/.radiant_bell")

# Ensure directories exist
os.makedirs(PLUGIN_DIR, exist_ok=True)
os.makedirs(BELL_DIR, exist_ok=True)

# ───────────────────────────────────────────────
# Colour & Theming
# ───────────────────────────────────────────────
class C:
    CYAN, GREEN, RED, YELLOW, DIM, RST, BOLD = "\033[96m", "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[0m", "\033[1m"
    GRAD = ["\033[38;5;196m", "\033[38;5;208m", "\033[38;5;226m", "\033[38;5;046m", "\033[38;5;047m"]

def clear_screen(): print("\033[2J\033[H", end="")

def print_banner(text, col=C.BOLD): print(col + text.center(60) + C.RST)

def show_spinner(msg, duration=1):
    """Shows a simple spinner for a given duration."""
    for c in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        print(f"\r{msg} {c}", end="", flush=True)
        time.sleep(0.1)
        duration -= 0.1
        if duration <= 0:
            print("\r" + " " * (len(msg) + 2) + "\r", end="") # Clear line
            break

# ───────────────────────────────────────────────
# Utility Functions
# ───────────────────────────────────────────────
def get_single_char():
    """Reads a single character from stdin without needing Enter."""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        char = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return char

def get_validated_input(prompt, validator_func, error_msg="Invalid input. Please try again."):
    """Gets input and validates it using a provided function."""
    while True:
        user_input = input(prompt).strip()
        try:
            result = validator_func(user_input)
            return result
        except ValueError:
            print(error_msg)

def validate_time_str(time_str):
    """Validates time string (HH:MM or HH:MM AM/PM). Returns (hour, minute)."""
    if " " in time_str:
        dt = datetime.datetime.strptime(time_str.upper(), "%I:%M %p")
        return dt.hour, dt.minute
    else:
        parts = time_str.split(":")
        if len(parts) != 2:
            raise ValueError("Invalid format")
        h, m = int(parts[0]), int(parts[1])
        if not (0 <= h <= 23 and 0 <= m <= 59):
            raise ValueError("Invalid time range")
        return h, m

def validate_int_range(min_val, max_val):
    """Returns a validator function for integers within a range."""
    def validator(s):
        val = int(s)
        if not (min_val <= val <= max_val):
            raise ValueError(f"Value must be between {min_val} and {max_val}")
        return val
    return validator

def validate_positive_int(s):
    """Validator for positive integers."""
    val = int(s)
    if val < 0:
        raise ValueError("Value must be positive")
    return val

# ───────────────────────────────────────────────
# Storage
# ───────────────────────────────────────────────
class Storage:
    DEFAULT_DATA = {
        "alarms": [],
        "theme": "dark",
        "sound": "beep",
        "fav_zones": [],
        "bell_vol": 75,
        "voice_wake": False,
        "log": []
    }

    def __init__(self, filepath=SAVE_FILE):
        self.filepath = filepath
        self.data = self.DEFAULT_DATA.copy()
        self.lock = threading.Lock() # Protect data access
        self.load()

    def load(self):
        """Loads data from the save file."""
        try:
            if os.path.isfile(self.filepath):
                with open(self.filepath, 'r') as f:
                    loaded_data = json.load(f)
                    self.data.update(loaded_data) # Update defaults with loaded data
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading save file: {e}. Using defaults.")

    def save(self):
        """Saves data to the save file."""
        with self.lock: # Acquire lock before writing
            try:
                with open(self.filepath, "w") as f:
                    json.dump(self.data, f, indent=2)
            except IOError as e:
                print(f"Error saving data: {e}")

storage = Storage()

# ───────────────────────────────────────────────
# Alarm
# ───────────────────────────────────────────────
class Alarm:
    def __init__(self, h, m, label, recur="once", enabled=True):
        self.h = h
        self.m = m
        self.label = label
        self.recur = recur # once, daily, weekdays, weekends
        self.enabled = enabled
        self.snooze_until = 0 # Timestamp until which snooze is active
        self.lock = threading.Lock() # Protect snooze and enabled state

    def get_next_ring_time(self, now):
        """Calculates the next time this alarm should ring."""
        today = now.date()
        ring_time = datetime.datetime.combine(today, datetime.time(self.h, self.m))

        if self.recur == "once":
            # Ring tomorrow if it's today or later
            if ring_time <= now:
                return ring_time + datetime.timedelta(days=1)
            else:
                return ring_time
        else: # daily, weekdays, weekends
            days_checked = 0
            current_ring_time = ring_time
            while True:
                if current_ring_time > now:
                    dow = current_ring_time.weekday()
                    if self.recur == "daily" or \
                       (self.recur == "weekdays" and dow < 5) or \
                       (self.recur == "weekends" and dow >= 5):
                        return current_ring_time

                current_ring_time += datetime.timedelta(days=1)
                days_checked += 1
                if days_checked > 14: # Prevent infinite loop
                    raise RuntimeError("Could not calculate next alarm time within 14 days.")

    def is_active(self, now):
        """Checks if the alarm should ring now (considering snooze)."""
        with self.lock:
            if not self.enabled:
                return False
            if self.snooze_until and now.timestamp() < self.snooze_until:
                return False
            return now >= self.get_next_ring_time(now)

    def snooze(self, minutes):
        """Sets the snooze time."""
        with self.lock:
            self.snooze_until = int(time.time()) + (minutes * 60)

    def reset_snooze(self):
        """Resets the snooze time."""
        with self.lock:
            self.snooze_until = 0

class AlarmManager:
    def __init__(self, storage_instance):
        self.storage = storage_instance
        self.alarms = [Alarm(**alarm_data) for alarm_data in self.storage.data["alarms"]]
        self.lock = threading.Lock() # Protect alarms list
        self.running = True
        self.watcher_thread = threading.Thread(target=self._watcher, daemon=True)
        self.watcher_thread.start()

    def log_event(self, msg):
        """Logs an event with timestamp."""
        event = {
            "time": datetime.datetime.now().isoformat(),
            "msg": msg
        }
        with self.storage.lock: # Lock storage for modification
            self.storage.data["log"].append(event)
        self.storage.save()

    def _watcher(self):
        """Background thread to check for alarm triggers."""
        while self.running:
            time.sleep(1) # Check every second
            now = datetime.datetime.now()
            with self.lock: # Lock alarms list for iteration
                alarms_to_check = list(self.alarms) # Copy list to iterate safely

            for alarm in alarms_to_check:
                if alarm.is_active(now):
                    self._ring(alarm)

    def _play_bell(self):
        """Plays the configured alarm sound."""
        sound_type = self.storage.data["sound"]
        volume = self.storage.data["bell_vol"]

        try:
            if sound_type == "beep":
                # Multiple beeps
                for _ in range(3):
                    print("\a", end="", flush=True)
                    time.sleep(0.5)
            elif sound_type == "speech":
                subprocess.run(["espeak", "Wake up!"], check=True)
            elif sound_type.endswith(".wav"):
                bell_path = os.path.join(BELL_DIR, sound_type)
                if os.path.isfile(bell_path):
                    # paplay volume is 0-65536 (100%)
                    vol_scaled = int(volume * 655.36)
                    subprocess.run(["paplay", "--volume", str(vol_scaled), bell_path], check=True)
                else:
                    print(f"Sound file not found: {bell_path}. Using beep.")
                    print("\a\a\a", end="")
            else:
                 print("\a\a\a", end="") # Default beep if unknown sound
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            print(f"Error playing sound ({sound_type}): {e}. Using beep.")
            print("\a\a\a", end="")


    def _ring(self, alarm):
        """Handles the alarm ringing process."""
        alarm.reset_snooze() # Reset snooze when ringing
        self.log_event(f"Alarm fired: {alarm.label}")

        clear_screen()
        print_banner("🔔  A L A R M", C.RED)
        print(f"{alarm.label}  {alarm.h:02d}:{alarm.m:02d}".center(60))

        # Sunrise gradient bar animation
        bar_segment = "█" * 12
        for i, color in enumerate(C.GRAD):
            print(color + bar_segment + C.RST, end="", flush=True)
            time.sleep(0.6)
        print() # Newline after bar

        self._play_bell()

        try:
            user_input = input("\nPress ENTER to stop, or type 's X' to snooze for X minutes: ").strip().lower()
            if user_input.startswith("s "):
                try:
                    snooze_mins = int(user_input.split()[1])
                    if snooze_mins > 0:
                        alarm.snooze(snooze_mins)
                        show_spinner("Snoozing", 1)
                        print(f"Snoozed for {snooze_mins} minutes.")
                    else:
                        print("Invalid snooze time. Stopping alarm.")
                        if alarm.recur == "once":
                            with alarm.lock:
                                alarm.enabled = False
                except (IndexError, ValueError):
                    print("Invalid snooze command. Stopping alarm.")
                    if alarm.recur == "once":
                        with alarm.lock:
                            alarm.enabled = False
            else:
                # Stop alarm (ENTER or any other input)
                if alarm.recur == "once":
                    with alarm.lock:
                        alarm.enabled = False
                self.save_alarms() # Save state after stopping/snoozing

        except (KeyboardInterrupt, EOFError):
             # If interrupted during alarm, stop it
            if alarm.recur == "once":
                with alarm.lock:
                    alarm.enabled = False
            self.save_alarms()
            print("\nAlarm stopped (interrupted).")


    def save_alarms(self):
        """Saves the current alarm list to storage."""
        with self.lock: # Lock alarms list for reading
            alarms_data = [vars(alarm) for alarm in self.alarms]
        with self.storage.lock: # Lock storage for modification
            self.storage.data["alarms"] = alarms_data
        self.storage.save()

    def export_log(self):
        """Exports the log to a CSV file."""
        log_file_path = os.path.expanduser("~/radiant_log.csv")
        try:
            with self.storage.lock: # Lock storage for reading log
                log_data = self.storage.data["log"]
            with open(log_file_path, "w", newline="") as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=["time", "msg"])
                writer.writeheader()
                writer.writerows(log_data)
            print(f"Log exported successfully to {log_file_path}")
        except IOError as e:
            print(f"Error exporting log: {e}")
        input("Press Enter to continue...")

    def menu(self):
        """Displays the alarm management menu."""
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
                    h, m = get_validated_input("", lambda s: validate_time_str(s), "Invalid time format. Use HH:MM or HH:MM AM/PM.")
                    label = input("Label (default 'Alarm'): ").strip() or "Alarm"
                    recur_options = {"1": "once", "2": "daily", "3": "weekdays", "4": "weekends"}
                    print("Recur options: 1. once  2. daily  3. weekdays  4. weekends")
                    recur_choice = input("Choose recurrence (default 1): ").strip()
                    recur = recur_options.get(recur_choice, "once")

                    with self.lock: # Lock alarms list for modification
                        self.alarms.append(Alarm(h, m, label, recur))
                    self.save_alarms()
                    show_spinner("Alarm Saved", 1)
                    print("Alarm set successfully.")
                    time.sleep(1)
                except (ValueError, KeyboardInterrupt):
                    print("\nInvalid input or operation cancelled.")
                    time.sleep(1)

            elif choice == "2":
                with self.lock: # Lock for reading
                    if not self.alarms:
                        print("No alarms set.")
                    else:
                        print("--- Alarms ---")
                        for i, alarm in enumerate(self.alarms, 1):
                            status = "✓" if alarm.enabled else "✗"
                            print(f"{i}. {status} {alarm.h:02d}:{alarm.m:02d} '{alarm.label}' ({alarm.recur})")
                input("Press Enter to continue...")

            elif choice == "3":
                with self.lock: # Lock for reading
                    if not self.alarms:
                        print("No alarms to delete.")
                        time.sleep(1)
                        continue
                    print("--- Delete Alarm ---")
                    for i, alarm in enumerate(self.alarms, 1):
                         status = "✓" if alarm.enabled else "✗"
                         print(f"{i}. {status} {alarm.h:02d}:{alarm.m:02d} '{alarm.label}' ({alarm.recur})")
                try:
                    index = get_validated_input("Enter alarm number to delete (0 to cancel): ",
                                                validate_int_range(0, len(self.alarms)),
                                                "Invalid alarm number.")
                    if index > 0:
                        with self.lock: # Lock for modification
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

# ───────────────────────────────────────────────
# World Clock
# ───────────────────────────────────────────────
class GlobeClock:
    # Load timezone list
    try:
        with open("/usr/share/zoneinfo/zone1970.tab", 'r') as f:
            ZONES = [line.split("\t")[2] for line in f if not line.startswith("#")]
    except (FileNotFoundError, IOError):
        print("Warning: Could not load zone1970.tab. Using default zones.")
        ZONES = ["UTC", "Europe/London", "America/New_York", "Asia/Tokyo", "Australia/Sydney"]

    @staticmethod
    def _get_weather(city):
        """Fetches weather for a city using wttr.in."""
        try:
            # wttr.in can be slow or unreliable, add timeout
            result = subprocess.run(
                ["curl", "-m", "5", "-s", f"wttr.in/{city}?format=%c+%t"],
                capture_output=True, text=True, check=True, timeout=6
            )
            return result.stdout.strip()
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
            return "Weather data unavailable"

    @classmethod
    def pick_zone(cls, fav_only=False):
        """Allows user to pick a timezone from a list."""
        zones = storage.data["fav_zones"] if fav_only and storage.data["fav_zones"] else cls.ZONES
        if not zones:
             print("No zones available.")
             input("Press Enter...")
             return None

        index = 0
        while True:
            clear_screen()
            print_banner("🌍  PICK A TIME-ZONE")
            print("↑/↓: Scroll  /: Search  f: Toggle Favorite  q: Back")
            print("-" * 60)

            # Display 20 zones at a time
            display_zones = zones[index:index+20]
            for i, zone in enumerate(display_zones, start=index+1):
                mark = "♥" if zone in storage.data["fav_zones"] else " "
                print(f"{i:>3} {mark} {zone}")

            char = get_single_char()
            if char == "\x1b": # Escape sequence (arrow keys)
                char += sys.stdin.read(2)
                if char == "\x1b[A": # Up arrow
                    index = max(0, index - 1)
                elif char == "\x1b[B": # Down arrow
                    index = min(len(zones) - 20, index + 1)
            elif char == "/":
                search_term = input("\nSearch term: ").strip().lower()
                if search_term:
                    zones = [z for z in cls.ZONES if search_term in z.lower()]
                    index = 0
                else:
                    zones = storage.data["fav_zones"] if fav_only and storage.data["fav_zones"] else cls.ZONES
            elif char == "f" and not fav_only: # Toggle favorite (only in full list)
                if display_zones:
                    selected_zone = display_zones[min(len(display_zones)-1, max(0, index - (index // 20) * 20))] # Simplified selection logic
                    # More robust: use index directly if within display range
                    actual_index_in_full_list = index + (index // 20) * 20 if index < len(display_zones) else index
                    if 0 <= index < len(display_zones):
                         selected_zone = display_zones[index]
                         with storage.lock:
                            if selected_zone in storage.data["fav_zones"]:
                                storage.data["fav_zones"].remove(selected_zone)
                                action = "removed from"
                            else:
                                storage.data["fav_zones"].append(selected_zone)
                                action = "added to"
                         storage.save()
                         print(f"'{selected_zone}' {action} favorites.")
                         time.sleep(0.5) # Brief feedback
            elif char == "\r": # Enter
                if display_zones:
                    # Select the zone currently "highlighted" (based on index)
                    selected_idx_in_display = min(len(display_zones)-1, max(0, index - (index // 20) * 20))
                    if 0 <= selected_idx_in_display < len(display_zones):
                        return display_zones[selected_idx_in_display]
            elif char.lower() == "q":
                return None

    @classmethod
    def show(cls):
        """Displays the world clock for a selected timezone."""
        zone = cls.pick_zone()
        if not zone:
            return

        city = zone.split("/")[-1].replace("_", " ")
        while True:
            clear_screen()
            print_banner(zone, C.CYAN)
            # Use pytz or datetime.timezone for better timezone handling if available
            # For simplicity, we stick to the original approach, but note it affects the whole process TZ
            old_tz = os.environ.get("TZ")
            os.environ["TZ"] = zone
            time.tzset()
            now_local = datetime.datetime.now()
            if old_tz:
                os.environ["TZ"] = old_tz
            else:
                os.unsetenv("TZ")
            time.tzset() # Reset to original TZ

            print(now_local.strftime("%Y-%m-%d  %H:%M:%S").center(60))
            weather_info = cls._get_weather(city)
            print(C.DIM + weather_info + C.RST)
            print("\n[r] Re-pick zone  [f] Show favorites only  [q] Quit  [any key] Refresh")
            char = get_single_char().lower()
            if char == "q":
                break
            elif char == "r":
                cls.show() # Recursive call to re-pick
                break # Exit current instance after recursive call
            elif char == "f":
                zone = cls.pick_zone(fav_only=True)
                if zone:
                    city = zone.split("/")[-1].replace("_", " ")
                # If None returned, stay in current loop

# ───────────────────────────────────────────────
# Timer tools
# ───────────────────────────────────────────────
class Timer:
    @staticmethod
    def countdown():
        """Runs a countdown timer."""
        try:
            minutes = get_validated_input("Enter minutes for countdown: ", validate_positive_int)
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
        alarm_manager = AlarmManager(storage) # Create temp instance for bell
        alarm_manager._play_bell()
        input("Press Enter to stop alarm...")

    @staticmethod
    def stopwatch():
        """Runs a simple stopwatch."""
        start_time = time.time()
        print(" Stopwatch started. Press any key to stop. ")
        try:
            while True:
                elapsed = int(time.time() - start_time)
                clear_screen()
                print_banner(f"⏱  {elapsed // 3600:02d}:{(elapsed // 60) % 60:02d}:{elapsed % 60:02d}", C.GREEN)
                print("\nPress any key to stop...")
                # Non-blocking check for input (requires select on Unix, msvcrt on Windows)
                # Simplified: just wait for a keypress
                get_single_char() # Blocks until keypress
                break
        except KeyboardInterrupt:
            pass # Stop on Ctrl+C
        finally:
            elapsed_final = int(time.time() - start_time)
            print(f"\n Stopwatch stopped at {elapsed_final // 3600:02d}:{(elapsed_final // 60) % 60:02d}:{elapsed_final % 60:02d}")

# ───────────────────────────────────────────────
# NTP sync
# ───────────────────────────────────────────────
def ntp_sync():
    """Attempts to synchronize system time using NTP."""
    clear_screen()
    print_banner("⏲  NTP SYNC", C.YELLOW)
    try:
        show_spinner("Querying NTP", 2)
        # Note: ntpdate might not be available on all systems. Consider using systemd-timesyncd or chrony.
        result = subprocess.run(["sudo", "ntpdate", "-s", "pool.ntp.org"], capture_output=True, text=True, check=True)
        print("System time updated successfully ✓")
        # print(result.stdout) # Optional: show ntpdate output
    except subprocess.CalledProcessError as e:
        print(f"Could not sync: ntpdate failed. {e}")
        # print(e.stderr) # Show error output
    except FileNotFoundError:
        print("Could not sync: 'ntpdate' command not found. Is it installed?")
    except KeyboardInterrupt:
        print("\nNTP sync cancelled.")
    input("Press Enter to continue...")

# ───────────────────────────────────────────────
# Quote of the day
# ───────────────────────────────────────────────
def daily_quote():
    """Returns a random motivational quote."""
    quotes = [
        "The bad news is time flies. The good news is you're the pilot. - Michael Altshuler",
        "Time is an illusion. Lunchtime doubly so. - Douglas Adams",
        "Lost time is never found again. - Benjamin Franklin",
        "You will never find time for anything. You must make it. - Charles Buxton",
        "The future is something which everyone reaches at the rate of sixty minutes an hour. - C.S. Lewis",
        "Time is really the only valuable thing a man can spend. - T.M. Luhrmann"
    ]
    return random.choice(quotes)

# ───────────────────────────────────────────────
# Plugin loader
# ───────────────────────────────────────────────
def load_plugins():
    """Dynamically loads plugins from the PLUGIN_DIR."""
    plugins = []
    for plugin_file in glob.glob(os.path.join(PLUGIN_DIR, "*.py")):
        plugin_name = os.path.splitext(os.path.basename(plugin_file))[0]
        if plugin_name.startswith("__"): continue # Skip __pycache__ etc.
        try:
            # Add plugin dir to path to allow imports within plugin
            plugin_dir = os.path.dirname(plugin_file)
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)

            spec = __import__(plugin_name, fromlist=[""])
            if hasattr(spec, "plugin_menu") and callable(getattr(spec, "plugin_menu")):
                plugins.append((plugin_name, spec.plugin_menu))
            else:
                print(f"Warning: Plugin '{plugin_name}' does not have a 'plugin_menu' function.")
        except Exception as e:
            print(f"Error loading plugin '{plugin_name}': {e}")
    return plugins

# ───────────────────────────────────────────────
# Settings
# ───────────────────────────────────────────────
class Settings:
    @staticmethod
    def menu(storage_instance):
        """Displays the settings menu."""
        # Gather available sounds
        bells = ["beep", "speech"] + [os.path.basename(f) for f in glob.glob(os.path.join(BELL_DIR, "*.wav"))]

        while True:
            clear_screen()
            print_banner("⚙️  SETTINGS")
            with storage_instance.lock: # Lock for reading settings
                print(f"Theme: {storage_instance.data['theme']}   Sound: {storage_instance.data['sound']}   Volume: {storage_instance.data['bell_vol']}%")
            print("1. Toggle theme")
            print("2. Pick sound")
            print("3. Set volume")
            print("4. NTP sync")
            print("5. Back")
            choice = input("> ").strip()

            if choice == "1":
                with storage_instance.lock: # Lock for modification
                    storage_instance.data["theme"] = "light" if storage_instance.data["theme"] == "dark" else "dark"
                storage_instance.save()
                show_spinner("Theme Saved", 0.5)
                print(f"Theme set to {storage.data['theme']}.")
                time.sleep(0.5)

            elif choice == "2":
                print("--- Available Sounds ---")
                for i, bell in enumerate(bells, 1):
                    marker = ">>" if bell == storage.data["sound"] else "  "
                    print(f"{marker} {i}. {bell}")
                try:
                    bell_choice = get_validated_input("Select sound (number): ",
                                                      validate_int_range(1, len(bells)),
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
                                                     validate_int_range(0, 100),
                                                     "Volume must be between 0 and 100.")
                    with storage_instance.lock:
                        storage_instance.data["bell_vol"] = new_volume
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

# ───────────────────────────────────────────────
# Main loop
# ───────────────────────────────────────────────
def main():
    """Main application loop."""
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\nBye!")
        # Ensure AlarmManager thread stops if needed (though daemon should handle it)
        # alarm_manager.running = False # If alarm_manager was global
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    plugins = load_plugins()
    # Initialize AlarmManager once
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
            choice_num = int(choice)
            if choice_num == 1:
                alarm_manager.menu()
            elif choice_num == 2:
                GlobeClock.show()
            elif choice_num == 3:
                Timer.countdown()
            elif choice_num == 4:
                Timer.stopwatch()
            elif choice_num == 5:
                 Settings.menu(storage) # Pass storage instance
            elif 6 <= choice_num < 6 + len(plugins):
                _, plugin_func = plugins[choice_num - 6]
                try:
                    plugin_func() # Call plugin menu
                except Exception as e:
                    print(f"Plugin error: {e}")
                    input("Press Enter to continue...")
            elif choice_num == 6 + len(plugins):
                print("Shutting down...")
                alarm_manager.running = False # Signal watcher thread to stop
                alarm_manager.watcher_thread.join(timeout=2) # Wait for thread to finish
                break
            else:
                print("Invalid option.")
                time.sleep(1)
        except ValueError:
            print("Please enter a number.")
            time.sleep(1)
        except KeyboardInterrupt:
            # This might not be reached due to signal handler, but good practice
            print("\nReceived interrupt signal. Exiting...")
            alarm_manager.running = False
            alarm_manager.watcher_thread.join(timeout=2)
            break

if __name__ == "__main__":
    main()
