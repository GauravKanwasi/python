#!/usr/bin/env python3
import curses
import itertools
import random
import time

FPS          = 30
SHIP_CHAR    = ord('^')
LASER_CHAR   = ord('|')
POWER_CHAR   = ord('+')
SHIELD_CHAR  = ord('O')
INITIAL_LASER_SPEED = 0.15
MIN_LASER_SPEED     = 0.03

def clamp(v, lo, hi):
    return max(lo, min(v, hi))

class Ship:
    def __init__(self, x, y):
        self.x, self.y, self.shield = x, y, 0
    def draw(self, w):
        w.addch(self.y, self.x, SHIELD_CHAR if self.shield else SHIP_CHAR)

class Laser:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def move(self, s):
        self.y += s
    def draw(self, w):
        w.addch(int(self.y), self.x, LASER_CHAR)

class PowerUp:
    def __init__(self, x, y):
        self.x, self.y = x, y
    def draw(self, w):
        w.addch(self.y, self.x, POWER_CHAR)

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(1000//FPS)
    h, w = stdscr.getmaxyx()
    ship = Ship(w//2, h-2)
    lasers, powerups, score = [], [], 0
    laser_timer, laser_speed, laser_delay = 0.0, INITIAL_LASER_SPEED, INITIAL_LASER_SPEED
    for frame in itertools.count():
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == curses.KEY_LEFT:
            ship.x = clamp(ship.x-1, 1, w-2)
        elif key == curses.KEY_RIGHT:
            ship.x = clamp(ship.x+1, 1, w-2)
        elif key == curses.KEY_UP:
            ship.y = clamp(ship.y-1, 1, h-2)
        elif key == curses.KEY_DOWN:
            ship.y = clamp(ship.y+1, 1, h-2)
        laser_timer += 1/FPS
        if laser_timer >= laser_delay:
            laser_timer = 0.0
            lasers.append(Laser(random.randint(1, w-2), 0))
        if random.random() < 0.004:
            powerups.append(PowerUp(random.randint(1, w-2), random.randint(1, h//2)))
        for laser in lasers:
            laser.move(1/laser_speed)
        lasers = [l for l in lasers if l.y < h]
        for laser in lasers[:]:
            if int(laser.y) == ship.y and laser.x == ship.x:
                if ship.shield:
                    ship.shield = max(0, ship.shield-30)
                    lasers.remove(laser)
                    stdscr.addstr(0, 0, " *CLANG* ", curses.A_REVERSE)
                else:
                    stdscr.addstr(h//2, w//2-5, "GAME OVER")
                    stdscr.refresh()
                    time.sleep(2)
                    return
        for pu in powerups[:]:
            if pu.y == ship.y and pu.x == ship.x:
                ship.shield += FPS*3
                powerups.remove(pu)
                stdscr.addstr(0, 0, " *POWER* ", curses.A_REVERSE)
        if frame % FPS == 0:
            score += 1
            laser_speed = max(MIN_LASER_SPEED, laser_speed-0.001)
        stdscr.erase()
        stdscr.border()
        stdscr.addstr(0, 2, f"Score {score} Shield {ship.shield//FPS}s")
        ship.draw(stdscr)
        for l in lasers:
            l.draw(stdscr)
        for p in powerups:
            p.draw(stdscr)
        if ship.shield:
            ship.shield -= 1
        stdscr.refresh()

if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
