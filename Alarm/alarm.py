import os, json, time, datetime, signal, threading, itertools, re, sys, tty, termios

SAVE = os.path.expanduser("~/.radiant_clock.json")

# ───────────────────────────────────────────────
# Utility helpers
# ───────────────────────────────────────────────
class Colour:
    CYAN   = "\033[96m"
    GREEN  = "\033[92m"
    RED    = "\033[91m"
    YELLOW = "\033[93m"
    DIM    = "\033[2m"
    RST    = "\033[0m"
    BOLD   = "\033[1m"

def clear(): print("\033[2J\033[H", end="")

# single-keypress without enter
def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# ───────────────────────────────────────────────
# Alarm
# ───────────────────────────────────────────────
class Alarm:
    def __init__(self, h, m, label, recur="once", enabled=True):
        self.h, self.m, self.label, self.recur, self.enabled = h, m, label, recur, enabled
        self.snooze = 0
    def next_ring(self, now):
        today = now.date()
        ring = datetime.datetime.combine(today, datetime.time(self.h, self.m))
        if self.recur == "once":
            return ring + (datetime.timedelta(days=1) if ring <= now else datetime.timedelta(0))
        delta = 1
        while True:
            if ring > now:
                dow = ring.weekday()
                ok = {"daily": True, "weekdays": dow < 5, "weekends": dow >= 5}[self.recur]
                if ok:
                    return ring
            ring += datetime.timedelta(days=1)
            delta += 1
            if delta > 14:
                raise RuntimeError("loop overflow")

class AlarmManager:
    def __init__(self):
        self.alarms = []
        self._load()
        threading.Thread(target=self._watcher, daemon=True).start()

    # ── storage ──
    def _load(self):
        if os.path.isfile(SAVE):
            self.alarms = [Alarm(**a) for a in json.load(open(SAVE)).get("alarms", [])]

    def _save(self):
        json.dump({"alarms": [a.__dict__ for a in self.alarms]}, open(SAVE, "w"), indent=2)

    # ── watcher thread ──
    def _watcher(self):
        while True:
            now = datetime.datetime.now()
            for a in self.alarms:
                if not a.enabled:
                    continue
                if a.snooze and now.timestamp() < a.snooze:
                    continue
                if now >= a.next_ring(now):
                    self._ring(a)
            time.sleep(1)

    def _ring(self, a):
        a.snooze = 0
        print("\n" + Colour.RED + "=" * 60)
        print(f"🔔  ALARM: {a.label}  {a.h:02d}:{a.m:02d}")
        print("=" * 60 + Colour.RST)
        try:
            ans = input("Press ENTER to stop / snooze <minutes>: ").strip().lower()
            if ans.startswith("snooze"):
                mins = int(ans.split()[1])
                a.snooze = int(time.time()) + mins * 60
                print(f"Snoozing {mins} minutes…")
            else:
                if a.recur == "once":
                    a.enabled = False
                self._save()
        except (KeyboardInterrupt, EOFError, ValueError):
            pass

    # ── CLI ──
    def add_cli(self):
        while True:
            t = input("Time (HH:MM) or (HH:MM AM/PM): ").strip()
            try:
                if " " in t:
                    dt = datetime.datetime.strptime(t.upper(), "%I:%M %p")
                    h, m = dt.hour, dt.minute
                else:
                    h, m = map(int, t.split(":"))
                if not (0 <= h <= 23 and 0 <= m <= 59):
                    raise ValueError
                break
            except ValueError:
                print("Invalid time.")
        label = input("Label: ").strip() or "Alarm"
        recur = input("Recur (once|daily|weekdays|weekends) [once]: ").strip() or "once"
        if recur not in {"once", "daily", "weekdays", "weekends"}:
            recur = "once"
        self.alarms.append(Alarm(h, m, label, recur))
        self._save()
        print("Alarm saved.")

    def list_(self):
        if not self.alarms:
            print("No alarms.")
            return
        for idx, a in enumerate(self.alarms, 1):
            status = "ON" if a.enabled else "OFF"
            print(f"{idx}. {a.h:02d}:{a.m:02d}  {a.label}  {a.recur}  {status}")

    def delete_cli(self):
        self.list_()
        if not self.alarms:
            return
        try:
            idx = int(input("Delete # (0 to cancel): ")) - 1
            if 0 <= idx < len(self.alarms):
                removed = self.alarms.pop(idx)
                self._save()
                print(f"Removed: {removed.label}")
            else:
                print("Cancelled.")
        except ValueError:
            print("Cancelled.")

# ───────────────────────────────────────────────
# World Clock (ASCII globe + search)
# ───────────────────────────────────────────────
class GlobeClock:
    try:
        ZONES = [z.split("\t")[2] for z in open("/usr/share/zoneinfo/zone1970.tab") if not z.startswith("#")]
    except FileNotFoundError:
        ZONES = ["UTC", "Europe/London", "America/New_York", "Asia/Tokyo", "Australia/Sydney"]

    @staticmethod
    def _ascii_globe(lat, lon):
        h, w = 12, 48
        grid = [[" " for _ in range(w)] for _ in range(h)]
        y = int((90 - lat) / 180 * (h - 1))
        x = int((lon + 180) / 360 * (w - 1))
        for i in range(h):
            for j in range(w):
                if abs(i - y) < 1 and abs(j - x) < 2:
                    grid[i][j] = Colour.GREEN + "●" + Colour.RST
                elif (i + j) % 5 == 0:
                    grid[i][j] = Colour.CYAN + "·" + Colour.RST
        return "\n".join("".join(row) for row in grid)

    @staticmethod
    def pick_zone():
        lat, lon = 0, 0
        search_mode = False
        matches = []
        while True:
            clear()
            print(Colour.BOLD + Colour.YELLOW + "🌍  WORLD CLOCK SELECTOR" + Colour.RST)
            print("Use arrow keys to move dot / ENTER to pick / '/' to search / 'q' to quit\n")
            print(GlobeClock._ascii_globe(lat, lon))
            print(f"\nLat {lat:6.1f}   Lon {lon:6.1f}")
            if search_mode:
                pat = input("Search zone: ").strip()
                matches = [z for z in GlobeClock.ZONES if pat.lower() in z.lower()]
                search_mode = False
                if matches:
                    for i, z in enumerate(matches, 1):
                        print(f"{i}. {z}")
                    try:
                        pick = int(input("Pick #: ")) - 1
                        return matches[pick]
                    except (ValueError, IndexError):
                        continue
            ch = getch()
            if ch == "q":
                return None
            if ch == "/":
                search_mode = True
                continue
            if ch == "\r":
                # map to closest zone
                best = min(GlobeClock.ZONES,
                           key=lambda z: abs(lat) + abs(lon) if "/" not in z else
                           abs(lat - float(z.split("/")[0])) * 10 + abs(lon - float(z.split("/")[1])) if len(z.split("/")) > 1 else 999)
                return best
            if ch == "\x1b":  # arrow sequence
                ch += sys.stdin.read(2)
            if ch.endswith("A"): lat = min(lat + 15, 90)   # up
            elif ch.endswith("B"): lat = max(lat - 15, -90)  # down
            elif ch.endswith("C"): lon = min(lon + 15, 180)  # right
            elif ch.endswith("D"): lon = max(lon - 15, -180)  # left

    @staticmethod
    def show_world():
        zone = GlobeClock.pick_zone()
        if not zone:
            return
        while True:
            clear()
            print(Colour.CYAN + Colour.BOLD + f"\n{zone}\n" + Colour.RST)
            # set env temporarily
            old_tz = os.environ.get("TZ")
            os.environ["TZ"] = zone
            time.tzset()
            now = datetime.datetime.now()
            if old_tz:
                os.environ["TZ"] = old_tz
            else:
                os.unsetenv("TZ")
            time.tzset()
            print(now.strftime("%Y-%m-%d  %H:%M:%S"))
            print(Colour.DIM + "\n[q] quit   [r] re-pick   any key refresh" + Colour.RST)
            ch = getch()
            if ch == "q":
                break
            if ch == "r":
                return GlobeClock.show_world()

# ───────────────────────────────────────────────
# Main menu
# ───────────────────────────────────────────────
def main():
    am = AlarmManager()
    signal.signal(signal.SIGINT, lambda sig, frame: (print("\nBye!"), sys.exit(0)))
    while True:
        clear()
        print(Colour.BOLD + Colour.GREEN + "🕒  RADIANT CLOCK" + Colour.RST)
        print("1 Alarm Clock")
        print("2 World Clock")
        print("3 Quit")
        choice = input("> ").strip()
        if choice == "1":
            while True:
                clear()
                print(Colour.BOLD + Colour.YELLOW + "⏰  ALARM CLOCK" + Colour.RST)
                print("1 Set alarm")
                print("2 List alarms")
                print("3 Delete alarm")
                print("4 Back")
                sub = input("> ").strip()
                if sub == "1":
                    am.add_cli()
                elif sub == "2":
                    am.list_()
                    input("\nPress Enter…")
                elif sub == "3":
                    am.delete_cli()
                elif sub == "4":
                    break
        elif choice == "2":
            GlobeClock.show_world()
        elif choice == "3":
            break

if __name__ == "__main__":
    main()
