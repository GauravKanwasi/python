#!/usr/bin/env python3
"""
Enhanced ASCII dodger
Arrow keys to move, q/ctrl-c to quit
Collect power-ups, survive as long as possible
"""
import curses, itertools, random, time, os, json, math

FPS          = 30
SHIP_CHAR    = "▲"
LASER_CHAR   = "│"
POWER_CHARS  = {"SHIELD": "◉", "SLOW": "◆", "RAPID": "◈"}
ENEMY_CHAR   = "▼"
PARTICLE_AGE = 15           # frames a particle lives
HIGHSCORE_FILE = os.path.expanduser("~/.ascii_dodger_hs.json")

# -------------------------------------------------
# Helper utilities
# -------------------------------------------------
def clamp(v, lo, hi):
    return max(lo, min(v, hi))

def beep(freq=800, length=20):
    """Very cheap ‘bell’ effect: prints \a if enabled"""
    if ENABLE_SOUND:
        print("\a", end="", flush=True)
        time.sleep(length/1000)

def load_hs():
    try:
        return json.load(open(HIGHSCORE_FILE))
    except (IOError, ValueError):
        return []

def save_hs(table):
    json.dump(table[:10], open(HIGHSCORE_FILE, "w"), indent=2)

# -------------------------------------------------
# Colour initialiser (safe fallback if colours off)
# -------------------------------------------------
def init_colours(stdscr):
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED,   -1)   # lasers / enemies
    curses.init_pair(2, curses.COLOR_GREEN, -1)   # ship
    curses.init_pair(3, curses.COLOR_YELLOW,-1)   # powerups
    curses.init_pair(4, curses.COLOR_BLUE,  -1)   # shield
    curses.init_pair(5, curses.COLOR_WHITE, -1)   # particles
    curses.init_pair(6, curses.COLOR_MAGENTA,-1)  # rapid fire

# -------------------------------------------------
# Game objects
# -------------------------------------------------
class Ship:
    def __init__(self, x, y):
        self.x, self.y, self.shield = x, y, 0
        self.rapid_fire = 0
    def draw(self, win):
        ch = SHIP_CHAR
        attr = curses.color_pair(2)
        if self.shield:
            ch = POWER_CHARS["SHIELD"]
            attr |= curses.A_BOLD | curses.color_pair(4)
        win.addstr(self.y, self.x, ch, attr)

class Laser:
    def __init__(self, x, y, friendly=False):
        self.x, self.y, self.friendly = x, y, friendly
    def move(self, dy):
        self.y += dy
    def draw(self, win):
        win.addstr(int(self.y), self.x, LASER_CHAR,
                   curses.color_pair(2 if self.friendly else 1) | curses.A_BOLD)

class Enemy:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.shoot_cd  = random.randint(FPS//2, FPS*2)
    def draw(self, win):
        win.addstr(self.y, self.x, ENEMY_CHAR,
                   curses.color_pair(1) | curses.A_BOLD)
    def maybe_shoot(self, lasers):
        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            lasers.append(Laser(self.x, self.y+1, friendly=False))
            self.shoot_cd = random.randint(FPS//2, FPS*2)

class PowerUp:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.kind = random.choice(["SHIELD", "SLOW", "RAPID"])
    def draw(self, win):
        col = {"SHIELD":4, "SLOW":3, "RAPID":6}[self.kind]
        win.addstr(self.y, self.x, POWER_CHARS[self.kind],
                   curses.color_pair(col) | curses.A_BOLD)

class Particle:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.vx = random.uniform(-0.8, 0.8)
        self.vy = random.uniform(-0.8, 0.8)
        self.age = PARTICLE_AGE
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.age -= 1
    def draw(self, win):
        if 0 <= int(self.x) < curses.COLS and 0 <= int(self.y) < curses.LINES:
            win.addstr(int(self.y), int(self.x), "✦",
                       curses.color_pair(5) | (curses.A_DIM if self.age < 5 else 0))

# -------------------------------------------------
# Main game
# -------------------------------------------------
def main(stdscr):
    global ENABLE_SOUND
    ENABLE_SOUND = os.environ.get("DODGER_NOSOUND") is None
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000//FPS)
    init_colours(stdscr)
    h, w = stdscr.getmaxyx()

    # Game state
    ship   = Ship(w//2, h-3)
    lasers, enemies, powerups, particles = [], [], [], []
    score, frame = 0, 0
    laser_delay   = 30           # frames between new downward lasers
    enemy_spawn   = FPS*4        # frames between new enemies
    next_enemy    = enemy_spawn

    high_scores = load_hs()
    stdscr.addstr(h//2-3, w//2-10, "GET READY!", curses.A_BOLD)
    stdscr.refresh()
    time.sleep(1)

    for frame in itertools.count():
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            break

        # Input
        if key == curses.KEY_LEFT:  ship.x = clamp(ship.x-1, 1, w-2)
        if key == curses.KEY_RIGHT: ship.x = clamp(ship.x+1, 1, w-2)
        if key == curses.KEY_UP:    ship.y = clamp(ship.y-1, 1, h-2)
        if key == curses.KEY_DOWN:  ship.y = clamp(ship.y+1, 1, h-2)

        # Enemy & laser spawning
        laser_delay = max(10, 30 - score//10)
        if frame % laser_delay == 0:
            lasers.append(Laser(random.randint(1, w-2), 0))

        next_enemy -= 1
        if next_enemy <= 0:
            enemies.append(Enemy(random.randint(1, w-2), 2))
            next_enemy = max(FPS, enemy_spawn - score*2)

        # Random power-ups
        if random.random() < 0.003 + score/10000:
            powerups.append(PowerUp(random.randint(1, w-2), random.randint(1, h//2)))

        # Update positions
        for laser in lasers:
            laser.move(1 if laser.friendly else 0.5)
        lasers = [l for l in lasers if 0 <= l.y < h]

        for enemy in enemies:
            enemy.maybe_shoot(lasers)
        enemies = [e for e in enemies if 0 <= e.y < h]

        for p in particles:
            p.update()
        particles = [p for p in particles if p.age > 0]

        # Collisions
        for laser in lasers[:]:
            if int(laser.y) == ship.y and laser.x == ship.x and not laser.friendly:
                if ship.shield > 0:
                    ship.shield = max(0, ship.shield - 30)
                    lasers.remove(laser)
                    beep(300, 50)
                    for _ in range(8):
                        particles.append(Particle(ship.x, ship.y))
                else:
                    beep(200, 300)
                    save_hs(high_scores)
                    stdscr.addstr(h//2, w//2-5, "GAME OVER", curses.A_BLINK | curses.color_pair(1))
                    stdscr.refresh()
                    time.sleep(2)
                    return

        for laser in lasers[:]:
            for enemy in enemies[:]:
                if int(laser.y) == enemy.y and laser.x == enemy.x and laser.friendly:
                    lasers.remove(laser)
                    enemies.remove(enemy)
                    score += 5
                    beep(600, 30)
                    for _ in range(12):
                        particles.append(Particle(enemy.x, enemy.y))
                    break

        for pu in powerups[:]:
            if pu.y == ship.y and pu.x == ship.x:
                if pu.kind == "SHIELD":
                    ship.shield = FPS*5
                    beep(800, 20)
                elif pu.kind == "SLOW":
                    laser_delay = min(60, laser_delay+15)
                    beep(400, 20)
                elif pu.kind == "RAPID":
                    ship.rapid_fire = FPS*3
                    beep(1000, 20)
                powerups.remove(pu)

        # Ship can shoot (rapid fire)
        if ship.rapid_fire > 0:
            ship.rapid_fire -= 1
            if frame % 4 == 0:
                lasers.append(Laser(ship.x, ship.y-1, friendly=True))

        # Count score
        if frame % FPS == 0:
            score += 1

        # Shield timer
        if ship.shield > 0:
            ship.shield -= 1

        # Draw
        stdscr.erase()
        stdscr.border()
        stdscr.addstr(0, 2, f"Score {score}", curses.color_pair(2))
        stdscr.addstr(0, 15, f"Shield {ship.shield//FPS}s", curses.color_pair(4))
        stdscr.addstr(0, 35, f"High {high_scores[0] if high_scores else 0}", curses.color_pair(3))
        ship.draw(stdscr)
        for obj in itertools.chain(lasers, enemies, powerups, particles):
            obj.draw(stdscr)

        stdscr.refresh()

    # Graceful exit: save score
    high_scores.append(score)
    high_scores.sort(reverse=True)
    save_hs(high_scores)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
