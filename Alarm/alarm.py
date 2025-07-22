import os, json, time, datetime, signal, threading, sys, tty, termios, subprocess, shlex

SAVE = os.path.expanduser("~/.radiant_clock.json")

# ───────────────────────────────────────────────
# Colour & theming
# ───────────────────────────────────────────────
class C:
    CYAN, GREEN, RED, YELLOW, DIM, RST, BOLD = "\033[96m", "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[0m", "\033[1m"
def clear(): print("\033[2J\033[H", end="")
def banner(text, col=C.BOLD): print(col + text.center(60) + C.RST)
def spin(msg, secs=1):
    for c in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        print(f"\r{msg} {c}", end="")
        time.sleep(0.1)
        secs -= 0.1
        if secs <= 0: print("\r" + " " * 30 + "\r"); break

# ───────────────────────────────────────────────
# Key reader
# ───────────────────────────────────────────────
def getch():
    fd = sys.stdin.fileno(); old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd); ch = sys.stdin.read(1)
    finally: termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

# ───────────────────────────────────────────────
# Storage & themes
# ───────────────────────────────────────────────
class Storage:
    def __init__(self):
        self.data = {"alarms": [], "theme": "dark", "sound": "beep", "fav_zones": []}
        if os.path.isfile(SAVE):
            self.data.update(json.load(open(SAVE)))
    def save(self): json.dump(self.data, open(SAVE, "w"), indent=2)
storage = Storage()

# ───────────────────────────────────────────────
# Alarm
# ───────────────────────────────────────────────
class Alarm:
    def __init__(self, h, m, label, recur="once", enabled=True):
        self.h, self.m, self.label, self.recur, self.enabled = h, m, label, recur, enabled
        self.snooze = 0
    def next(self, now):
        today = now.date()
        ring = datetime.datetime.combine(today, datetime.time(self.h, self.m))
        if self.recur == "once": return ring + (datetime.timedelta(days=1) if ring <= now else datetime.timedelta(0))
        delta = 1
        while True:
            if ring > now:
                ok = {"daily": True, "weekdays": ring.weekday() < 5, "weekends": ring.weekday() >= 5}[self.recur]
                if ok: return ring
            ring += datetime.timedelta(days=1); delta += 1
            if delta > 14: raise RuntimeError

class AlarmManager:
    def __init__(self):
        self.alarms = [Alarm(**a) for a in storage.data["alarms"]]
        threading.Thread(target=self._watcher, daemon=True).start()
    def _watcher(self):
        while True:
            now = datetime.datetime.now()
            for a in self.alarms:
                if not a.enabled: continue
                if a.snooze and now.timestamp() < a.snooze: continue
                if now >= a.next(now): self._ring(a)
            time.sleep(1)
    def _ring(self, a):
        a.snooze = 0
        clear(); banner("🔔  A L A R M", C.RED)
        print(f"{a.label}  {a.h:02d}:{a.m:02d}".center(60))
        # sunrise visual
        for i in range(1, 6):
            print(C.YELLOW + "█" * i * 10 + C.RST); time.sleep(0.5)
        # sound
        snd = storage.data["sound"]
        if snd == "beep":
            print("\a\a\a", end="")
        elif snd == "speech" and shutil.which("say"):
            subprocess.run(["say", "Good morning"])
        try:
            ans = input("\nPress ENTER to stop / snooze <min>: ").strip().lower()
            if ans.startswith("snooze"):
                mins = int(ans.split()[1])
                a.snooze = int(time.time()) + mins * 60
                spin("Snoozing", 1)
            else:
                if a.recur == "once": a.enabled = False
                self._save()
        except: pass
    def menu(self):
        while True:
            clear(); banner("⏰  A L A R M   C L O C K")
            print("1 Set alarm\n2 List alarms\n3 Delete alarm\n4 Back")
            ch = input("> ").strip()
            if ch == "1":
                t = input("Time (HH:MM or HH:MM AM/PM): ").strip()
                try:
                    if " " in t: h,m=datetime.datetime.strptime(t.upper(), "%I:%M %p").hour,datetime.datetime.strptime(t.upper(), "%I:%M %p").minute
                    else: h,m=map(int, t.split(":"))
                except: continue
                label = input("Label: ").strip() or "Alarm"
                recur = input("Recur (once|daily|weekdays|weekends) [once]: ").strip() or "once"
                self.alarms.append(Alarm(h,m,label,recur)); storage.data["alarms"]=[a.__dict__ for a in self.alarms]; storage.save()
                spin("Saving", 1)
            elif ch == "2":
                if not self.alarms: print("No alarms."); input()
                else: [print(f"{i}. {a.h:02d}:{a.m:02d} {a.label} {a.recur}") for i,a in enumerate(self.alarms,1)]; input()
            elif ch == "3":
                self.alarms.pop(int(input("Delete # (0 to cancel): "))-1); storage.save()
            elif ch == "4": break

# ───────────────────────────────────────────────
# World Clock with weather
# ───────────────────────────────────────────────
class GlobeClock:
    try:
        ZONES = [z.split("\t")[2] for z in open("/usr/share/zoneinfo/zone1970.tab") if not z.startswith("#")]
    except: ZONES = ["UTC", "Europe/London", "America/New_York", "Asia/Tokyo"]
    @staticmethod
    def _weather(city):
        try:
            out = subprocess.check_output(["curl", "-s", f"wttr.in/{city}?format=%l:+%c+%t"], timeout=3).decode().strip()
            return out
        except: return "Weather unavailable"
    @staticmethod
    def pick_zone():
        idx = 0
        while True:
            clear(); banner("🌍  PICK A TIME-ZONE")
            print("↑↓ scroll  / search  f fav  q back\n")
            for i,z in enumerate(GlobeClock.ZONES[idx:idx+20], idx+1):
                mark = "♥" if z in storage.data["fav_zones"] else " "
                print(f"{i:>3} {mark} {z}")
            ch = getch()
            if ch == "\x1b": ch += sys.stdin.read(2)
            if ch.endswith("A"): idx = max(0, idx-1)
            elif ch.endswith("B"): idx = min(len(GlobeClock.ZONES)-20, idx+1)
            elif ch == "/":
                pat = input("\nSearch: ").strip()
                GlobeClock.ZONES = [z for z in GlobeClock.ZONES if pat.lower() in z.lower()]; idx=0
            elif ch == "f":
                z = GlobeClock.ZONES[idx]
                if z in storage.data["fav_zones"]: storage.data["fav_zones"].remove(z)
                else: storage.data["fav_zones"].append(z); storage.save()
            elif ch == "\r":
                return GlobeClock.ZONES[idx]
            elif ch == "q": return None
    @staticmethod
    def show():
        zone = GlobeClock.pick_zone()
        if not zone: return
        city = zone.split("/")[-1].replace("_", " ")
        while True:
            clear(); banner(zone, C.CYAN)
            old = os.environ.get("TZ")
            os.environ["TZ"] = zone; time.tzset()
            print(datetime.datetime.now().strftime("%Y-%m-%d  %H:%M:%S").center(60))
            print(C.DIM + GlobeClock._weather(city) + C.RST)
            if old: os.environ["TZ"] = old
            else: os.unsetenv("TZ")
            time.tzset()
            print("\n[r] re-pick  [q] quit  any key refresh")
            ch = getch()
            if ch == "q": break
            if ch == "r": return GlobeClock.show()

# ───────────────────────────────────────────────
# Countdown & Stopwatch
# ───────────────────────────────────────────────
class Timer:
    @staticmethod
    def countdown():
        try:
            mins = int(input("Minutes: "))
        except: return
        secs = mins * 60
        while secs:
            clear(); banner(f"⏳  {secs//60:02d}:{secs%60:02d}", C.RED)
            time.sleep(1); secs -= 1
        clear(); banner("🔔  TIME'S UP", C.RED)
        print("\a\a\a", end=""); input()
    @staticmethod
    def stopwatch():
        start = time.time()
        while True:
            elapsed = int(time.time() - start)
            clear(); banner(f"⏱  {elapsed//60:02d}:{elapsed%60:02d}", C.GREEN)
            print("\nPress any key to stop")
            if getch(): break

# ───────────────────────────────────────────────
# Settings
# ───────────────────────────────────────────────
class Settings:
    @staticmethod
    def menu():
        while True:
            clear(); banner("⚙️  SETTINGS")
            print(f"Theme: {storage.data['theme']}   Sound: {storage.data['sound']}")
            print("1 Toggle theme\n2 Sound: beep / speech / none\n3 Back")
            ch = input("> ").strip()
            if ch == "1":
                storage.data["theme"] = "light" if storage.data["theme"] == "dark" else "dark"
                storage.save(); spin("Saved", 0.5)
            elif ch == "2":
                print("1 beep  2 speech  3 none")
                s = {"1":"beep","2":"speech","3":"none"}.get(input("> ").strip(),"beep")
                storage.data["sound"] = s; storage.save(); spin("Saved", 0.5)
            elif ch == "3": break

# ───────────────────────────────────────────────
# Main loop
# ───────────────────────────────────────────────
def main():
    signal.signal(signal.SIGINT, lambda s,f: (print("\nBye!"),sys.exit(0)))
    while True:
        clear()
        banner("🕒  R A D I A N T   C L O C K")
        print("1 Alarm Clock")
        print("2 World Clock")
        print("3 Countdown")
        print("4 Stopwatch")
        print("5 Settings")
        print("6 Quit")
        ch = input("> ").strip()
        if ch == "1": AlarmManager().menu()
        elif ch == "2": GlobeClock.show()
        elif ch == "3": Timer.countdown()
        elif ch == "4": Timer.stopwatch()
        elif ch == "5": Settings.menu()
        elif ch == "6": break

if __name__ == "__main__":
    main()
