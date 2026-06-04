#!/usr/bin/env python3
"""
Enhanced ASCII Dodger
Arrow keys to move, Q or Ctrl-C to quit.
Collect power-ups, shoot enemies (with Rapid Fire), and survive!
"""

import curses
import itertools
import random
import time
import os
import json
from typing import List, Dict, Any, Optional

# =================================================
# GAME CONFIGURATION & CONSTANTS
# =================================================
FPS: int = 30
SHIP_CHAR: str = "▲"
LASER_CHAR: str = "│"
POWER_CHARS: Dict[str, str] = {"SHIELD": "◉", "SLOW": "◆", "RAPID": "◈"}
ENEMY_CHAR: str = "▼"
PARTICLE_AGE: int = 15  # frames a particle lives
HIGHSCORE_FILE: str = os.path.expanduser("~/.ascii_dodger_hs.json")
ENABLE_SOUND: bool = os.environ.get("DODGER_NOSOUND") is None

# =================================================
# HELPER UTILITIES
# =================================================
def clamp(v: int, lo: int, hi: int) -> int:
    """Restricts a value v to be between lo and hi."""
    return max(lo, min(v, hi))

def beep(freq: int = 800, length: int = 20) -> None:
    """Very basic 'bell' effect: prints \\a if sound is enabled."""
    if ENABLE_SOUND:
        print("\a", end="", flush=True)
        time.sleep(length / 1000)

def load_hs() -> List[int]:
    """Loads high scores from the JSON file."""
    try:
        with open(HIGHSCORE_FILE, 'r') as f:
            return json.load(f)
    except (IOError, ValueError):
        return []

def save_hs(table: List[int]) -> None:
    """Saves the top 10 high scores to the JSON file."""
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(table[:10], f, indent=2)
    except IOError as e:
        pass  # Fail silently if we don't have write permissions

def safe_addstr(win: curses.window, y: int, x: int, string: str, attr: int = 0) -> None:
    """Safely draws to the screen, ignoring out-of-bounds errors common in curses."""
    try:
        win.addstr(int(y), int(x), string, attr)
    except curses.error:
        pass

# =================================================
# INITIALIZATION
# =================================================
def init_colours() -> None:
    """Initializes standard curses color pairs."""
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_RED, -1)     # Lasers / Enemies
    curses.init_pair(2, curses.COLOR_GREEN, -1)   # Ship / Friendly Lasers
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # Slow Powerup / Highscore
    curses.init_pair(4, curses.COLOR_BLUE, -1)    # Shield
    curses.init_pair(5, curses.COLOR_WHITE, -1)   # Particles
    curses.init_pair(6, curses.COLOR_MAGENTA, -1) # Rapid Fire

# =================================================
# GAME ENTITIES
# =================================================
class Ship:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.shield: int = 0
        self.rapid_fire: int = 0

    def draw(self, win: curses.window) -> None:
        ch = SHIP_CHAR
        attr = curses.color_pair(2)
        
        # Override visual if shield is active
        if self.shield:
            ch = POWER_CHARS["SHIELD"]
            attr |= curses.A_BOLD | curses.color_pair(4)
            
        safe_addstr(win, self.y, self.x, ch, attr)

class Laser:
    def __init__(self, x: int, y: float, friendly: bool = False):
        self.x: int = x
        self.y: float = y
        self.friendly: bool = friendly

    def move(self, dy: float) -> None:
        self.y += dy

    def draw(self, win: curses.window) -> None:
        attr = curses.color_pair(2 if self.friendly else 1) | curses.A_BOLD
        safe_addstr(win, int(self.y), self.x, LASER_CHAR, attr)

class Enemy:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.shoot_cd: int = random.randint(FPS // 2, FPS * 2)

    def draw(self, win: curses.window) -> None:
        safe_addstr(win, self.y, self.x, ENEMY_CHAR, curses.color_pair(1) | curses.A_BOLD)

    def maybe_shoot(self, lasers: List[Laser]) -> None:
        self.shoot_cd -= 1
        if self.shoot_cd <= 0:
            lasers.append(Laser(self.x, self.y + 1, friendly=False))
            self.shoot_cd = random.randint(FPS // 2, FPS * 2)

class PowerUp:
    def __init__(self, x: int, y: int):
        self.x: int = x
        self.y: int = y
        self.kind: str = random.choice(["SHIELD", "SLOW", "RAPID"])

    def draw(self, win: curses.window) -> None:
        col = {"SHIELD": 4, "SLOW": 3, "RAPID": 6}[self.kind]
        safe_addstr(win, self.y, self.x, POWER_CHARS[self.kind], curses.color_pair(col) | curses.A_BOLD)

class Particle:
    def __init__(self, x: int, y: int):
        self.x: float = x
        self.y: float = y
        self.vx: float = random.uniform(-0.8, 0.8)
        self.vy: float = random.uniform(-0.8, 0.8)
        self.age: int = PARTICLE_AGE

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.age -= 1

    def draw(self, win: curses.window) -> None:
        attr = curses.color_pair(5) | (curses.A_DIM if self.age < 5 else 0)
        safe_addstr(win, int(self.y), int(self.x), "✦", attr)

# =================================================
# MAIN GAME LOOP
# =================================================
def main(stdscr: curses.window) -> None:
    # Setup Window Environment
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000 // FPS)
    init_colours()
    h, w = stdscr.getmaxyx()

    # Initialize Game State
    ship = Ship(w // 2, h - 3)
    lasers: List[Laser] = []
    enemies: List[Enemy] = []
    powerups: List[PowerUp] = []
    particles: List[Particle] = []
    
    score: int = 0
    laser_delay: int = 30       # Frames between ambient downward lasers
    enemy_spawn: int = FPS * 4  # Frames between new enemies
    next_enemy: int = enemy_spawn

    high_scores = load_hs()
    
    # Ready Screen
    safe_addstr(stdscr, h // 2 - 3, w // 2 - 10, "GET READY!", curses.A_BOLD)
    stdscr.refresh()
    time.sleep(1)

    for frame in itertools.count():
        # --- PHASE 1: INPUT ---
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            break
        
        if key == curses.KEY_LEFT:  ship.x = clamp(ship.x - 1, 1, w - 2)
        if key == curses.KEY_RIGHT: ship.x = clamp(ship.x + 1, 1, w - 2)
        if key == curses.KEY_UP:    ship.y = clamp(ship.y - 1, 1, h - 2)
        if key == curses.KEY_DOWN:  ship.y = clamp(ship.y + 1, 1, h - 2)

        # --- PHASE 2: SPAWNING ---
        # Spawn ambient falling lasers. Delay decreases as score increases.
        laser_delay = max(10, 30 - score // 10)
        if frame % laser_delay == 0:
            lasers.append(Laser(random.randint(1, w - 2), 0))

        # Spawn enemies over time
        next_enemy -= 1
        if next_enemy <= 0:
            enemies.append(Enemy(random.randint(1, w - 2), 2))
            next_enemy = max(FPS, enemy_spawn - score * 2)

        # Spawn random power-ups
        if random.random() < 0.003 + score / 10000:
            powerups.append(PowerUp(random.randint(1, w - 2), random.randint(1, h // 2)))

        # Ship shooting (if rapid fire active)
        if ship.rapid_fire > 0:
            ship.rapid_fire -= 1
            if frame % 4 == 0:
                lasers.append(Laser(ship.x, ship.y - 1, friendly=True))

        # --- PHASE 3: UPDATES ---
        # Update and clean up off-screen entities
        for laser in lasers:
            laser.move(1 if laser.friendly else 0.5)
        lasers = [l for l in lasers if 0 <= l.y < h]

        for enemy in enemies:
            enemy.maybe_shoot(lasers)
        enemies = [e for e in enemies if 0 <= e.y < h]

        for p in particles:
            p.update()
        particles = [p for p in particles if p.age > 0]

        # General state updates
        if ship.shield > 0:
            ship.shield -= 1
        if frame % FPS == 0:
            score += 1

        # --- PHASE 4: COLLISIONS ---
        # 1. Ship hit by hostile lasers
        for laser in lasers[:]:
            if int(laser.y) == ship.y and laser.x == ship.x and not laser.friendly:
                if ship.shield > 0:
                    # Shield absorbs hit
                    ship.shield = max(0, ship.shield - 30)
                    if laser in lasers:
                        lasers.remove(laser)
                    beep(300, 50)
                    for _ in range(8):
                        particles.append(Particle(ship.x, ship.y))
                else:
                    # Game Over
                    beep(200, 300)
                    high_scores.append(score)
                    high_scores.sort(reverse=True)
                    save_hs(high_scores)
                    
                    safe_addstr(stdscr, h // 2, w // 2 - 5, "GAME OVER", curses.A_BLINK | curses.color_pair(1))
                    stdscr.refresh()
                    time.sleep(2)
                    return

        # 2. Enemies hit by friendly lasers
        for laser in lasers[:]:
            if not laser.friendly:
                continue
            for enemy in enemies[:]:
                if int(laser.y) == enemy.y and laser.x == enemy.x:
                    if laser in lasers: lasers.remove(laser)
                    if enemy in enemies: enemies.remove(enemy)
                    score += 5
                    beep(600, 30)
                    for _ in range(12):
                        particles.append(Particle(enemy.x, enemy.y))
                    break

        # 3. Ship collecting power-ups
        for pu in powerups[:]:
            if pu.y == ship.y and pu.x == ship.x:
                if pu.kind == "SHIELD":
                    ship.shield = FPS * 5
                    beep(800, 20)
                elif pu.kind == "SLOW":
                    laser_delay = min(60, laser_delay + 15)
                    beep(400, 20)
                elif pu.kind == "RAPID":
                    ship.rapid_fire = FPS * 3
                    beep(1000, 20)
                powerups.remove(pu)

        # --- PHASE 5: RENDERING ---
        stdscr.erase()
        stdscr.border()
        
        # HUD
        safe_addstr(stdscr, 0, 2, f"Score {score}", curses.color_pair(2))
        safe_addstr(stdscr, 0, 15, f"Shield {ship.shield // FPS}s", curses.color_pair(4))
        safe_addstr(stdscr, 0, 35, f"High {high_scores[0] if high_scores else 0}", curses.color_pair(3))
        
        # Entities
        ship.draw(stdscr)
        for obj in itertools.chain(lasers, enemies, powerups, particles):
            obj.draw(stdscr)

        stdscr.refresh()

    # Graceful exit save
    high_scores.append(score)
    high_scores.sort(reverse=True)
    save_hs(high_scores)

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
