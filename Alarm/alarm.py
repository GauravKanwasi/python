import os, json, time, datetime, signal, threading, sys, tty, termios, subprocess, shutil, csv, glob, random, textwrap, itertools

SAVE = os.path.expanduser("~/.radiant_clock.json")
PLUGIN_DIR = os.path.expanduser("~/.radiant_plugins")
BELL_DIR   = os.path.expanduser("~/.radiant_bell")
for d in (PLUGIN_DIR, BELL_DIR):
    os.makedirs(d, exist_ok=True)

# ───────────────────────────────────────────────
# Colour & theming
# ───────────────────────────────────────────────
class C:
    CYAN, GREEN, RED, YELLOW, DIM, RST, BOLD = "\033[96m", "\033[92m", "\033[91m", "\033[93m", "\033[2m", "\033[0m", "\033[1m"
    GRAD = ["\033[38;5;196m", "\033[38;5;208m", "\033[38;5;226m", "\033[38;5;046m", "\033[38;5;047m"]
def clear(): print("\033[2J\033[H", end="")
def banner(text, col=C.BOLD): print(col + text.center(60) + C.RST)
def spin(msg, secs=1):
    for c in itertools.cycle("⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"):
        print(f"\r{msg} {c}", end="", flush=True)
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
# Storage
# ───────────────────────────────────────────────
class Storage:
    def __init__(self):
        self.data = {"alarms": [], "theme": "dark", "sound": "beep", "fav_zones": [],
                     "bell_vol": 75, "voice_wake": False, "log": []}
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
        if self.recur == "once":
            return ring + (datetime.timedelta(days=1) if ring <= now else datetime.timedelta(0))
        delta = 1
        while True:
            if ring > now:
                dow = ring.weekday()
                ok = {"daily": True, "weekdays": dow < 5, "weekends": dow >= 5}[self.recur]
                if ok: return ring
            ring += datetime.timedelta(days=1); delta += 1
            if delta > 14: raise RuntimeError

class AlarmManager:
    def __init__(self):
        self.alarms = [Alarm(**a) for a in storage.data["alarms"]]
        threading.Thread(target=self._watcher, daemon=True).start()
    def log(self, msg):
        storage.data["log"].append({"time": datetime.datetime.now().isoformat(), "msg": msg})
        storage.save()
    def _watcher(self):
        while True:
            now = datetime.datetime.now()
            for a in self.alarms:
                if not a.enabled: continue
                if a.snooze and now.timestamp() < a.snooze: continue
                if now >= a.next(now):
                    self._ring(a)
            time.sleep(1)
    def _play_bell(self):
        snd = storage.data["sound"]
        vol = storage.data["bell_vol"]
        if snd == "beep":
            print("\a\a\a", end="")
        elif snd == "speech":
            subprocess.run(["espeak", "Wake up!"])
        elif snd.endswith(".wav"):
            subprocess.run(["paplay", "--volume", str(int(vol*327.67)), os.path.join(BELL_DIR, snd)])
    def _ring(self, a):
        a.snooze = 0
        self.log(f"Alarm fired: {a.label}")
        clear(); banner("🔔  A L A R M", C.RED)
        print(f"{a.label}  {a.h:02d}:{a.m:02d}".center(60))
        # sunrise gradient bar
        bar = "█" * 60
        for i, col in enumerate(C.GRAD):
            print(col + bar[:12*i+12] + C.RST); time.sleep(0.6)
        self._play_bell()
        try:
            ans = input("\nENTER to stop / snooze <min>: ").strip().lower()
            if ans.startswith("snooze"):
                mins = int(ans.split()[1])
                a.snooze = int(time.time()) + mins * 60
                spin("Snoozing", 1)
            else:
                if a.recur == "once": a.enabled = False
                storage.data["alarms"] = [a.__dict__ for a in self.alarms]; storage.save()
        except: pass
    def export_log(self):
        fname = os.path.expanduser("~/radiant_log.csv")
        with open(fname, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["time", "msg"])
            writer.writeheader(); writer.writerows(storage.data["log"])
        print(f"Log exported → {fname}"); input()
    def menu(self):
        while True:
            clear(); banner("⏰  A L A R M   C L O C K")
            print("1 Set alarm\n2 List alarms\n3 Delete alarm\n4 Export log\n5 Back")
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
                spin("Saved", 1)
            elif ch == "2":
                if not self.alarms: print("No alarms."); input()
                else: [print(f"{i}. {a.h:02d}:{a.m:02d} {a.label} {a.recur}") for i,a in enumerate(self.alarms,1)]; input()
            elif ch == "3":
                try:
                    self.alarms.pop(int(input("Delete # (0 to cancel): "))-1)
                    storage.data["alarms"]=[a.__dict__ for a in self.alarms]; storage.save()
                except: pass
            elif ch == "4":
                self.export_log()
            elif ch == "5": break

# ───────────────────────────────────────────────
# World Clock
# ───────────────────────────────────────────────
class GlobeClock:
    try:
        ZONES = [z.split("\t")[2] for z in open("/usr/share/zoneinfo/zone1970.tab") if not z.startswith("#")]
    except: ZONES = ["UTC", "Europe/London", "America/New_York", "Asia/Tokyo"]
    @staticmethod
    def _weather(city):
        try:
            out = subprocess.check_output(["curl", "-s", f"wttr.in/{city}?format=%c+%t"], timeout=3).decode().strip()
            return out
        except: return "Weather unavailable"
    @staticmethod
    def pick_zone(fav_only=False):
        zones = storage.data["fav_zones"] if fav_only else GlobeClock.ZONES
        idx = 0
        while True:
            clear(); banner("🌍  PICK A TIME-ZONE")
            print("↑↓ scroll  / search  f toggle fav  q back\n")
            for i,z in enumerate(zones[idx:idx+20], idx+1):
                mark = "♥" if z in storage.data["fav_zones"] else " "
                print(f"{i:>3} {mark} {z}")
            ch = getch()
            if ch == "\x1b": ch += sys.stdin.read(2)
            if ch.endswith("A"): idx = max(0, idx-1)
            elif ch.endswith("B"): idx = min(len(zones)-20, idx+1)
            elif ch == "/":
                pat = input("\nSearch: ").strip()
                zones = [z for z in zones if pat.lower() in z.lower()]; idx=0
            elif ch == "f" and not fav_only:
                z = zones[idx]
                if z in storage.data["fav_zones"]: storage.data["fav_zones"].remove(z)
                else: storage.data["fav_zones"].append(z); storage.save()
            elif ch == "\r":
                return zones[idx]
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
            now = datetime.datetime.now()
            if old: os.environ["TZ"] = old
            else: os.unsetenv("TZ"); time.tzset()
            print(now.strftime("%Y-%m-%d  %H:%M:%S").center(60))
            print(C.DIM + GlobeClock._weather(city) + C.RST)
            print("\n[r] re-pick  [f] favs only  [q] quit  any key refresh")
            ch = getch()
            if ch == "q": break
            if ch == "r": return GlobeClock.show()
            if ch == "f": zone = GlobeClock.pick_zone(fav_only=True) or zone

# ───────────────────────────────────────────────
# Timer tools
# ───────────────────────────────────────────────
class Timer:
    @staticmethod
    def countdown():
        try: mins = int(input("Minutes: "))
        except: return
        secs = mins * 60
        while secs:
            clear(); banner(f"⏳  {secs//60:02d}:{secs%60:02d}", C.RED)
            time.sleep(1); secs -= 1
        clear(); banner("🔔  TIME'S UP", C.RED)
        AlarmManager()._play_bell(); input()
    @staticmethod
    def stopwatch():
        start = time.time()
        while True:
            elapsed = int(time.time() - start)
            clear(); banner(f"⏱  {elapsed//3600:02d}:{elapsed//60%60:02d}:{elapsed%60:02d}", C.GREEN)
            print("\nPress any key to stop")
            if getch(): break

# ───────────────────────────────────────────────
# NTP sync
# ───────────────────────────────────────────────
def ntp_sync():
    clear(); banner("⏲  NTP SYNC", C.YELLOW)
    try:
        spin("Querying NTP", 2)
        subprocess.run(["sudo", "ntpdate", "-s", "pool.ntp.org"], check=True)
        print("System time updated ✓"); input()
    except Exception as e:
        print("Could not sync:", e); input()

# ───────────────────────────────────────────────
# Quote of the day
# ───────────────────────────────────────────────
def daily_quote():
    quotes = [
        "The bad news is time flies. The good news is you're the pilot.",
        "Time is an illusion. Lunchtime doubly so.",
        "Lost time is never found again.",
        "You will never find time for anything. You must make it."
    ]
    return random.choice(quotes)

# ───────────────────────────────────────────────
# Plugin loader
# ───────────────────────────────────────────────
def load_plugins():
    plugins = []
    for py in glob.glob(os.path.join(PLUGIN_DIR, "*.py")):
        name = os.path.splitext(os.path.basename(py))[0]
        spec = __import__(name, fromlist=[""])
        if hasattr(spec, "plugin_menu"):
            plugins.append((name, spec.plugin_menu))
    return plugins

# ───────────────────────────────────────────────
# Settings
# ───────────────────────────────────────────────
class Settings:
    @staticmethod
    def menu():
        bells = ["beep","speech","none"] + [os.path.basename(f) for f in glob.glob(os.path.join(BELL_DIR,"*.wav"))]
        while True:
            clear(); banner("⚙️  SETTINGS")
            print(f"Theme: {storage.data['theme']}   Sound: {storage.data['sound']}   Vol: {storage.data['bell_vol']}")
            print("1 Toggle theme\n2 Pick sound\n3 Volume\n4 NTP sync\n5 Back")
            ch = input("> ").strip()
            if ch == "1":
                storage.data["theme"] = "light" if storage.data["theme"]=="dark" else "dark"; storage.save(); spin("Saved", 0.5)
            elif ch == "2":
                for i,b in enumerate(bells,1): print(f"{i}. {b}")
                try:
                    storage.data["sound"] = bells[int(input("> "))-1]; storage.save()
                except: pass
            elif ch == "3":
                storage.data["bell_vol"] = int(input("Volume 0-100: ") or storage.data["bell_vol"]); storage.save()
            elif ch == "4":
                ntp_sync()
            elif ch == "5": break

# ───────────────────────────────────────────────
# Main loop
# ───────────────────────────────────────────────
def main():
    signal.signal(signal.SIGINT, lambda s,f: (print("\nBye!"),sys.exit(0)))
    plugins = load_plugins()
    while True:
        clear()
        banner("🕒  R A D I A N T   C L O C K")
        print(C.DIM + daily_quote().center(60) + C.RST)
        print("\n1 Alarm Clock\n2 World Clock\n3 Countdown\n4 Stopwatch\n5 Settings")
        for idx,(name,_) in enumerate(plugins,6):
            print(f"{idx} Plugin: {name}")
        print(f"{6+len(plugins)} Quit")
        ch = input("> ").strip()
        try:
            ich = int(ch)
            if ich == 1: AlarmManager().menu()
            elif ich == 2: GlobeClock.show()
            elif ich == 3: Timer.countdown()
            elif ich == 4: Timer.stopwatch()
            elif ich == 5: Settings.menu()
            elif 6 <= ich < 6+len(plugins):
                plugins[ich-6][1]()  # call plugin
            elif ich == 6+len(plugins): break
        except: pass

if __name__ == "__main__":
    main()
