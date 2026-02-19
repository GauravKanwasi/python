import pygame
import random
import sys
import math
import os
from pygame.locals import *
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ENEMY_SPEED = 1
BULLET_SPEED = 7
ENEMY_ROWS = 5
ENEMY_COLS = 10
ENEMY_SPACING = 60
ENEMY_DROP = 30

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
DARK_BLUE = (0, 0, 128)

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Invaders Deluxe")
clock = pygame.time.Clock()

# Game states
MENU = 0
INSTRUCTIONS = 1
PLAYING = 2
GAME_OVER = 3
SHOP = 4
LEVEL_COMPLETE = 5
PAUSED = 6

# Create assets directory if it doesn't exist
if not os.path.exists('assets'):
    os.makedirs('assets')

# Create dummy sound files if they don't exist
sound_files = ['shoot.wav', 'explosion.wav', 'powerup.wav', 'hit.wav', 'music.wav']
for sound_file in sound_files:
    path = f'assets/{sound_file}'
    if not os.path.exists(path):
        open(path, 'a').close()

# Load sounds with safe fallback
class DummySound:
    def play(self): pass
    def stop(self): pass
    def set_volume(self, v): pass

def load_sound(path):
    try:
        s = mixer.Sound(path)
        return s
    except Exception:
        return DummySound()

shoot_sound = load_sound('assets/shoot.wav')
explosion_sound = load_sound('assets/explosion.wav')
powerup_sound = load_sound('assets/powerup.wav')
hit_sound = load_sound('assets/hit.wav')

try:
    mixer.music.load('assets/music.wav')
    mixer.music.set_volume(0.3)
    mixer.music.play(-1)
except Exception:
    pass


# ----- Particle System -----

class Particle:
    __slots__ = ('x', 'y', 'color', 'vx', 'vy', 'size', 'life', 'age')

    def __init__(self, x, y, color, vx=0.0, vy=0.0, size=3.0, life=20):
        self.x = x
        self.y = y
        self.color = color
        self.vx = vx
        self.vy = vy
        self.size = size
        self.life = life
        self.age = 0

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1
        self.age += 1
        self.size = max(0.0, self.size - 0.05)
        return self.age < self.life

    def draw(self, surface):
        if self.size < 0.5:
            return
        alpha = int(255 * (1 - self.age / self.life))
        color = (*self.color, alpha)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), int(self.size))


def emit_particles(lst, x, y, color, count, vx_range=(-2, 2), vy_range=(-2, 2),
                   size_range=(2, 4), life_range=(20, 40)):
    """Helper to batch-create particles into a list."""
    for _ in range(count):
        lst.append(Particle(
            x + random.uniform(-10, 10), y + random.uniform(-10, 10),
            color,
            vx=random.uniform(*vx_range), vy=random.uniform(*vy_range),
            size=random.uniform(*size_range),
            life=random.randint(*life_range)
        ))


# ----- Starfield -----

class Starfield:
    def __init__(self, num_stars=150):
        self.stars = [
            [random.randint(0, SCREEN_WIDTH),
             random.randint(0, SCREEN_HEIGHT),
             random.uniform(0.1, 0.5),
             random.randint(1, 2),
             random.randint(100, 255)]
            for _ in range(num_stars)
        ]

    def update(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)

    def draw(self, surface):
        for x, y, _, size, brightness in self.stars:
            c = (brightness, brightness, brightness)
            pygame.draw.circle(surface, c, (int(x), int(y)), size)


# ----- Pre-built surfaces cache -----

_surface_cache = {}

def cached_surface(key, builder):
    if key not in _surface_cache:
        _surface_cache[key] = builder()
    return _surface_cache[key]


# ----- Sprite Classes -----

SCREEN_RECT = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = cached_surface('player', self._build_image)
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH // 2, bottom=SCREEN_HEIGHT - 10)
        self.speed_x = 0
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.bullet_power = 1
        self.fire_rate = 500
        self.last_shot = 0
        self.shield = False
        self.shield_time = 0
        self.shield_duration = 10000
        self.bullet_speed = 7
        self.spread_shot = False
        self.spread_shot_time = 0
        self.spread_duration = 10000
        self.particles = []
        self._engine_acc = 0.0

    @staticmethod
    def _build_image():
        img = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(img, GREEN, [(25, 0), (0, 40), (50, 40)])
        pygame.draw.polygon(img, BLUE, [(25, 10), (10, 30), (40, 30)])
        pygame.draw.circle(img, YELLOW, (25, 20), 5)
        return img

    def update(self):
        self.rect.x += self.speed_x
        self.rect.clamp_ip(SCREEN_RECT)

        now = pygame.time.get_ticks()
        if self.shield and now - self.shield_time > self.shield_duration:
            self.shield = False
        if self.spread_shot and now - self.spread_shot_time > self.spread_duration:
            self.spread_shot = False

        # Update particles
        self.particles = [p for p in self.particles if p.update()]

        # Engine trail (throttled)
        self._engine_acc += 0.3
        while self._engine_acc >= 1:
            self._engine_acc -= 1
            self.particles.append(Particle(
                self.rect.centerx + random.randint(-5, 5),
                self.rect.bottom,
                (0, random.randint(150, 255), random.randint(200, 255)),
                vy=random.uniform(1.0, 3.0),
                vx=random.uniform(-0.5, 0.5),
                size=random.uniform(2, 4),
                life=random.randint(20, 40)
            ))

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)

    def shoot(self, all_sprites, bullets):
        now = pygame.time.get_ticks()
        if now - self.last_shot <= self.fire_rate:
            return
        self.last_shot = now
        shoot_sound.play()

        cx, top = self.rect.centerx, self.rect.top
        sp = self.bullet_speed
        bp = self.bullet_power
        new_bullets = []

        if bp == 1:
            new_bullets.append(Bullet(cx, top, speed_y=-sp))
        elif bp == 2:
            new_bullets += [Bullet(self.rect.left + 10, top, speed_y=-sp),
                            Bullet(self.rect.right - 10, top, speed_y=-sp)]
        elif bp >= 3:
            new_bullets += [Bullet(self.rect.left + 10, top, speed_y=-sp),
                            Bullet(cx, top, speed_y=-sp),
                            Bullet(self.rect.right - 10, top, speed_y=-sp)]
            if bp >= 4:
                new_bullets += [Bullet(self.rect.left, self.rect.centery, speed_y=-sp, speed_x=-2),
                                Bullet(self.rect.right, self.rect.centery, speed_y=-sp, speed_x=2)]

        if self.spread_shot:
            for angle in (-30, -15, 0, 15, 30):
                rad = math.radians(angle)
                new_bullets.append(Bullet(cx, top,
                                          speed_y=math.cos(rad) * -sp,
                                          speed_x=math.sin(rad) * 3))

        for b in new_bullets:
            all_sprites.add(b)
            bullets.add(b)


class Enemy(pygame.sprite.Sprite):
    # Per-type base stats
    _TYPE_STATS = {
        0: dict(health=1, points=10, drop_chance=0.05, shoot_chance=0.002),
        1: dict(health=2, points=20, drop_chance=0.10, shoot_chance=0.003),
        2: dict(health=3, points=30, drop_chance=0.15, shoot_chance=0.005),
        3: dict(points=100, drop_chance=0.5, shoot_chance=0.01),  # boss – health set per instance
    }

    def __init__(self, x, y, enemy_type=0, level=1):
        super().__init__()
        self.enemy_type = enemy_type
        self.level = level

        self.image = cached_surface(f'enemy_{enemy_type}', lambda et=enemy_type: self._build_image(et))
        self.rect = self.image.get_rect(x=x, y=y)

        stats = self._TYPE_STATS[enemy_type]
        if enemy_type == 3:
            self.health = 10 + level * 2
            self.max_health = self.health
            self.points = 100 + level * 20
            self.shoot_chance = 0.01 * (level // 5 + 1)
        else:
            self.health = stats['health']
            self.points = stats['points']
            self.shoot_chance = stats['shoot_chance']
        self.drop_chance = stats['drop_chance']

        self.direction = 1
        self.oscillation = 0.0
        self.particles = []
        self.osc_speed = random.uniform(0.05, 0.1)
        self.osc_amp = random.randint(5, 15)
        self._boss_particle_acc = 0.0

    @staticmethod
    def _build_image(enemy_type):
        if enemy_type == 3:
            size = 60
            img = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(img, YELLOW, (size // 2, size // 2), size // 2)
            pygame.draw.circle(img, ORANGE, (size // 2, size // 2), size // 2 - 5)
            pygame.draw.circle(img, RED, (size // 3, size // 3), 5)
            pygame.draw.circle(img, RED, (2 * size // 3, size // 3), 5)
            pygame.draw.arc(img, BLACK, (size // 4, size // 2, size // 2, size // 3), 0, math.pi, 3)
        else:
            img = pygame.Surface((40, 40), pygame.SRCALPHA)
            if enemy_type == 0:
                pygame.draw.circle(img, RED, (20, 20), 15)
                pygame.draw.circle(img, (255, 150, 150), (20, 20), 10)
            elif enemy_type == 1:
                pygame.draw.rect(img, BLUE, (5, 5, 30, 30))
                pygame.draw.rect(img, (100, 100, 255), (10, 10, 20, 20))
            elif enemy_type == 2:
                pygame.draw.polygon(img, PURPLE, [(20, 0), (0, 40), (40, 40)])
                pygame.draw.polygon(img, (200, 100, 200), [(20, 10), (10, 30), (30, 30)])
        return img

    def update(self, all_sprites=None, enemy_bullets=None):
        speed = ENEMY_SPEED * self.direction * (1 + self.level * 0.1)
        self.rect.x += speed
        self.oscillation += self.osc_speed
        self.rect.y += math.sin(self.oscillation) * self.osc_amp * 0.1

        if random.random() < self.shoot_chance and all_sprites is not None:
            self._do_shoot(all_sprites, enemy_bullets)

        self.particles = [p for p in self.particles if p.update()]

        if self.enemy_type == 3:
            self._boss_particle_acc += 0.1
            while self._boss_particle_acc >= 1:
                self._boss_particle_acc -= 1
                self.particles.append(Particle(
                    self.rect.centerx + random.randint(-20, 20),
                    self.rect.bottom,
                    (random.randint(200, 255), random.randint(100, 150), 0),
                    vy=random.uniform(1.0, 2.0),
                    vx=random.uniform(-0.5, 0.5),
                    size=random.uniform(3, 6),
                    life=random.randint(30, 50)
                ))

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)

    def _do_shoot(self, all_sprites, enemy_bullets):
        if self.enemy_type == 3:
            for angle in (-30, -15, 0, 15, 30):
                rad = math.radians(angle)
                b = EnemyBullet(self.rect.centerx, self.rect.bottom,
                                math.sin(rad) * BULLET_SPEED / 2,
                                math.cos(rad) * BULLET_SPEED / 2)
                all_sprites.add(b); enemy_bullets.add(b)
        elif self.enemy_type == 2:
            for b in (EnemyBullet(self.rect.left + 10, self.rect.bottom),
                      EnemyBullet(self.rect.right - 10, self.rect.bottom)):
                all_sprites.add(b); enemy_bullets.add(b)
        else:
            b = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(b); enemy_bullets.add(b)

    def hit(self, global_particles):
        self.health -= 1
        hit_sound.play()
        emit_particles(global_particles, self.rect.centerx, self.rect.centery,
                       (255, 100, 0), 10,
                       vx_range=(-2, 2), vy_range=(-2, 2),
                       size_range=(2, 4), life_range=(15, 30))
        return self.health <= 0


class Bullet(pygame.sprite.Sprite):
    _img_cache = {}

    def __init__(self, x, y, speed_y=-BULLET_SPEED, speed_x=0, color=WHITE):
        super().__init__()
        key = color
        if key not in Bullet._img_cache:
            img = pygame.Surface((6, 15), pygame.SRCALPHA)
            pygame.draw.rect(img, color, (0, 0, 6, 15))
            pygame.draw.rect(img, YELLOW, (1, 1, 4, 13))
            Bullet._img_cache[key] = img
        self.image = Bullet._img_cache[key]
        self.rect = self.image.get_rect(centerx=x, bottom=y)
        self.speed_y = speed_y
        self.speed_x = speed_x
        self.particles = []
        self._trail_acc = 0.0

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x

        # Trail particles (throttled)
        self._trail_acc += 0.5
        while self._trail_acc >= 1:
            self._trail_acc -= 1
            self.particles.append(Particle(
                self.rect.centerx, self.rect.bottom,
                (random.randint(200, 255), random.randint(200, 255), random.randint(50, 150)),
                vy=random.uniform(-1.0, 1.0),
                vx=random.uniform(-0.5, 0.5),
                size=random.uniform(1, 3),
                life=random.randint(10, 20)
            ))

        self.particles = [p for p in self.particles if p.update()]

        if not SCREEN_RECT.colliderect(self.rect):
            self.kill()

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)


class EnemyBullet(Bullet):
    _enemy_img = None

    def __init__(self, x, y, speed_x=0, speed_y=BULLET_SPEED / 2):
        super().__init__(x, y, speed_y, speed_x, color=RED)
        if EnemyBullet._enemy_img is None:
            img = pygame.Surface((8, 20), pygame.SRCALPHA)
            pygame.draw.rect(img, RED, (0, 0, 8, 20))
            pygame.draw.rect(img, ORANGE, (1, 1, 6, 18))
            EnemyBullet._enemy_img = img
        self.image = EnemyBullet._enemy_img
        self.rect = self.image.get_rect(centerx=x, top=y)


class Powerup(pygame.sprite.Sprite):
    _images = {}

    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        if powerup_type not in Powerup._images:
            Powerup._images[powerup_type] = self._build_image(powerup_type)
        self.image = Powerup._images[powerup_type]
        self.rect = self.image.get_rect(center=(x, y))
        self._t = 0.0

    @staticmethod
    def _build_image(pt):
        img = pygame.Surface((30, 30), pygame.SRCALPHA)
        if pt == 0:
            pygame.draw.circle(img, GREEN, (15, 15), 12)
            pygame.draw.circle(img, (150, 255, 150), (15, 15), 8)
            pygame.draw.polygon(img, WHITE, [(15, 8), (10, 18), (20, 18)])
        elif pt == 1:
            pygame.draw.circle(img, BLUE, (15, 15), 12)
            pygame.draw.circle(img, CYAN, (15, 15), 8)
            pygame.draw.circle(img, BLUE, (15, 15), 12, 3)
        elif pt == 2:
            pygame.draw.circle(img, YELLOW, (15, 15), 12)
            pygame.draw.circle(img, (255, 200, 0), (15, 15), 8)
            pygame.draw.circle(img, (200, 150, 0), (15, 15), 12, 2)
        elif pt == 3:
            pygame.draw.circle(img, PURPLE, (15, 15), 12)
            pygame.draw.circle(img, (200, 100, 200), (15, 15), 8)
            for angle in (-30, 0, 30):
                rad = math.radians(angle)
                pygame.draw.line(img, WHITE, (15, 15),
                                 (15 + math.sin(rad) * 10, 15 - math.cos(rad) * 10), 2)
        return img

    def update(self):
        self.rect.y += 2
        self._t += 0.1
        self.rect.x += math.sin(self._t) * 0.5
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size, color=RED):
        super().__init__()
        self.size = size
        self.color = color
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size // 2, size // 2), size // 2)
        self.rect = self.image.get_rect(center=center)
        self.frame = 0
        self.max_frame = 10
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.particles = []
        # Initial burst
        for _ in range(30):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(1.0, 5.0)
            self.particles.append(Particle(
                center[0], center[1],
                (random.randint(200, 255), random.randint(50, 150), 0),
                vx=math.sin(angle) * speed,
                vy=math.cos(angle) * speed,
                size=random.uniform(2, 5),
                life=random.randint(20, 40)
            ))

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame >= self.max_frame:
                self.kill()
                return
            self.size = max(5, self.size - 2)
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            alpha = int(255 * (1 - self.frame / self.max_frame))
            pygame.draw.circle(self.image, (*self.color, alpha),
                               (self.size // 2, self.size // 2), self.size // 2)
            self.rect = self.image.get_rect(center=self.rect.center)
        self.particles = [p for p in self.particles if p.update()]

    def draw_particles(self, surface):
        for p in self.particles:
            p.draw(surface)


class ShopItem:
    def __init__(self, name, description, cost, effect_func, icon_color):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect_func = effect_func
        self.icon_color = icon_color

    def purchase(self, player):
        if player.coins >= self.cost:
            player.coins -= self.cost
            self.effect_func(player)
            powerup_sound.play()
            return True
        return False


# ----- Sprite Groups and initial state -----

all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Game state variables
game_state = MENU
current_level = 1
max_level = 10
shop_items = []
boss_spawned = False
global_particles = []
high_score = 0
starfield = Starfield(200)

# Fonts
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 64)

menu_options = ["Start Game", "Instructions", "Quit"]
selected_option = 0
selected_shop_item = 0
menu_animation = 0.0

instructions_text = [
    "Welcome to Space Invaders Deluxe!",
    "Controls:",
    "  Arrow keys: Move left/right",
    "  Space: Shoot",
    "  S: Shop",
    "  P: Pause",
    "",
    "Objective:",
    "  Destroy all enemies to complete the level",
    "  Avoid enemy bullets!",
    "",
    "Powerups:",
    "  Green: Extra Life",
    "  Blue: Temporary Shield",
    "  Yellow: Coins",
    "  Purple: Spread Shot",
    "",
    "Press ESC to return"
]

# Pre-render overlay surfaces
_overlay_dark = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
_overlay_dark.fill((0, 0, 0, 150))
_overlay_blue = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
_overlay_blue.fill((0, 0, 50, 180))


# ----- Game Functions -----

def create_enemies(level):
    global boss_spawned
    boss_spawned = False
    rows = min(ENEMY_ROWS + level // 2, 8)
    cols = min(ENEMY_COLS + level // 3, 15)
    w0 = max(0.0, 0.6 - level * 0.03)
    w1 = min(1.0, 0.25 + level * 0.02)
    w2 = min(1.0, 0.15 + level * 0.01)
    weights_normal = [w0, w1, w2]
    weights_boss_row = [0.1, 0.3, 0.6]
    boss_level = (level % 5 == 0)
    for row in range(rows):
        w = weights_boss_row if boss_level and row == 0 else weights_normal
        for col in range(cols):
            enemy_type = random.choices((0, 1, 2), weights=w)[0]
            e = Enemy(col * ENEMY_SPACING + 50, row * ENEMY_SPACING + 50, enemy_type, level)
            all_sprites.add(e)
            enemies.add(e)


def initialize_shop():
    global shop_items
    shop_items = [
        ShopItem("Extra Life", "Gain an additional life", 50,
                 lambda p: setattr(p, 'lives', p.lives + 1), GREEN),
        ShopItem("Shield", "Temporary invulnerability", 30,
                 lambda p: (setattr(p, 'shield', True),
                            setattr(p, 'shield_time', pygame.time.get_ticks())), BLUE),
        ShopItem("Weapon Upgrade", "Increase bullet power", 40,
                 lambda p: setattr(p, 'bullet_power', min(p.bullet_power + 1, 4)), CYAN),
        ShopItem("Rapid Fire", "Shoot faster", 35,
                 lambda p: setattr(p, 'fire_rate', max(p.fire_rate - 100, 200)), PURPLE),
        ShopItem("Bullet Speed", "Increase bullet speed", 25,
                 lambda p: setattr(p, 'bullet_speed', min(p.bullet_speed + 1, 15)), YELLOW),
        ShopItem("Shield Extender", "Increase shield duration", 30,
                 lambda p: setattr(p, 'shield_duration', p.shield_duration + 5000), ORANGE),
        ShopItem("Spread Shot", "Temporary spread shot", 45,
                 lambda p: (setattr(p, 'spread_shot', True),
                            setattr(p, 'spread_shot_time', pygame.time.get_ticks())), (255, 100, 255)),
    ]


def reset_game():
    global game_state, current_level, player
    global all_sprites, enemies, bullets, enemy_bullets, powerups
    global boss_spawned, global_particles

    all_sprites.empty()
    enemies.empty()
    bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    global_particles.clear()

    game_state = MENU
    current_level = 1
    boss_spawned = False
    player = Player()
    all_sprites.add(player)
    create_enemies(current_level)


def handle_input():
    global game_state, selected_option, selected_shop_item, boss_spawned
    global high_score, global_particles, current_level

    for event in pygame.event.get():
        if event.type == QUIT:
            high_score = max(high_score, player.score)
            pygame.quit(); sys.exit()

        elif event.type == KEYDOWN:
            if game_state == MENU:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == K_RETURN:
                    choice = menu_options[selected_option]
                    if choice == "Start Game":
                        game_state = PLAYING
                    elif choice == "Instructions":
                        game_state = INSTRUCTIONS
                    elif choice == "Quit":
                        high_score = max(high_score, player.score)
                        pygame.quit(); sys.exit()

            elif game_state == INSTRUCTIONS:
                if event.key == K_ESCAPE:
                    game_state = MENU

            elif game_state == PLAYING:
                if event.key == K_LEFT:
                    player.speed_x = -PLAYER_SPEED
                elif event.key == K_RIGHT:
                    player.speed_x = PLAYER_SPEED
                elif event.key == K_SPACE:
                    player.shoot(all_sprites, bullets)
                elif event.key == K_s:
                    game_state = SHOP
                elif event.key == K_p:
                    game_state = PAUSED

            elif game_state == GAME_OVER:
                if event.key == K_r:
                    high_score = max(high_score, player.score)
                    reset_game()

            elif game_state == SHOP:
                if event.key == K_UP:
                    selected_shop_item = (selected_shop_item - 1) % len(shop_items)
                elif event.key == K_DOWN:
                    selected_shop_item = (selected_shop_item + 1) % len(shop_items)
                elif event.key == K_RETURN:
                    shop_items[selected_shop_item].purchase(player)
                elif event.key in (K_ESCAPE, K_s):
                    game_state = PLAYING

            elif game_state == LEVEL_COMPLETE:
                if event.key == K_n:
                    current_level += 1
                    if current_level > max_level:
                        game_state = GAME_OVER
                    else:
                        create_enemies(current_level)
                        boss_spawned = False
                        game_state = PLAYING
                elif event.key == K_s:
                    game_state = SHOP

            elif game_state == PAUSED:
                if event.key == K_p:
                    game_state = PLAYING
                elif event.key == K_ESCAPE:
                    game_state = MENU

        elif event.type == KEYUP:
            if game_state == PLAYING and event.key in (K_LEFT, K_RIGHT):
                player.speed_x = 0


def update_game():
    global game_state, boss_spawned, global_particles, current_level

    # Pass shoot groups to enemy.update
    for entity in list(all_sprites):
        if isinstance(entity, Enemy):
            entity.update(all_sprites, enemy_bullets)
        else:
            entity.update()

    starfield.update()
    global_particles = [p for p in global_particles if p.update()]

    # Enemy wall-bounce
    if any(e.rect.right >= SCREEN_WIDTH or e.rect.left <= 0 for e in enemies):
        for e in enemies:
            e.rect.y += ENEMY_DROP
            e.direction *= -1

    # Bullet-enemy collisions
    hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
    for enemy, _ in hits.items():
        if enemy.hit(global_particles):
            if random.random() < enemy.drop_chance:
                p = Powerup(enemy.rect.centerx, enemy.rect.centery, random.randint(0, 3))
                all_sprites.add(p); powerups.add(p)
            player.score += enemy.points
            player.coins += max(1, enemy.points // 5)
            exp = Explosion(enemy.rect.center, 40, color=(255, min(200, enemy.points), 0))
            all_sprites.add(exp)
            explosion_sound.play()
            enemy.kill()

    # Player hit by enemy bullets
    if not player.shield and pygame.sprite.spritecollide(player, enemy_bullets, True):
        player.lives -= 1
        emit_particles(global_particles, player.rect.centerx, player.rect.centery,
                       (255, 50, 50), 20,
                       vx_range=(-3, 3), vy_range=(-3, 3),
                       size_range=(3, 6), life_range=(20, 40))
        hit_sound.play()
        if player.lives <= 0:
            game_state = GAME_OVER

    # Powerup collection
    POWERUP_COLORS = {0: GREEN, 1: (0, 200, 255), 2: (255, 200, 0), 3: (200, 100, 200)}
    for pu in pygame.sprite.spritecollide(player, powerups, True):
        if pu.powerup_type == 0:
            player.lives += 1
        elif pu.powerup_type == 1:
            player.shield = True; player.shield_time = pygame.time.get_ticks()
        elif pu.powerup_type == 2:
            player.coins += 10
        elif pu.powerup_type == 3:
            player.spread_shot = True; player.spread_shot_time = pygame.time.get_ticks()
        emit_particles(global_particles, pu.rect.centerx, pu.rect.centery,
                       POWERUP_COLORS[pu.powerup_type], 15,
                       size_range=(2, 4), life_range=(20, 40))
        powerup_sound.play()

    # Enemies reach bottom
    if any(e.rect.bottom >= SCREEN_HEIGHT - 50 for e in enemies):
        game_state = GAME_OVER

    # Level complete / boss spawn
    if not enemies:
        if current_level % 5 == 0 and not boss_spawned:
            boss = Enemy(SCREEN_WIDTH // 2, 50, 3, current_level)
            all_sprites.add(boss); enemies.add(boss)
            boss_spawned = True
        else:
            game_state = LEVEL_COMPLETE
            emit_particles(global_particles,
                           random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT),
                           (200, 200, 255), 100,
                           vx_range=(-1, 1), vy_range=(-1, 1),
                           size_range=(2, 5), life_range=(30, 60))


def render_game():
    global high_score
    screen.fill(DARK_BLUE)
    starfield.draw(screen)

    for p in global_particles:
        p.draw(screen)

    if game_state == MENU:
        offset = math.sin(menu_animation) * 5
        title = title_font.render("SPACE INVADERS DELUXE", True, (100, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80 + int(offset)))

        if high_score > 0:
            st = font.render(f"High Score: {high_score}", True, YELLOW)
            screen.blit(st, (SCREEN_WIDTH // 2 - st.get_width() // 2, 150))

        for i, option in enumerate(menu_options):
            color = (100, 255, 100) if i == selected_option else (200, 200, 255)
            off = math.sin(menu_animation + i * 0.5) * 3
            txt = font.render(option, True, color)
            bx = SCREEN_WIDTH // 2 - txt.get_width() // 2
            by = 250 + i * 50 + int(off)
            screen.blit(txt, (bx, by))
            if i == selected_option:
                mid_y = by + txt.get_height() // 2
                pygame.draw.circle(screen, color, (bx - 20, mid_y), 8)
                pygame.draw.circle(screen, color, (bx + txt.get_width() + 20, mid_y), 8)

        ver = small_font.render("v2.0 Enhanced Edition", True, (150, 150, 255))
        screen.blit(ver, (SCREEN_WIDTH - ver.get_width() - 10, SCREEN_HEIGHT - 30))

    elif game_state == INSTRUCTIONS:
        pygame.draw.rect(screen, (30, 30, 60), (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 200), (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 3, border_radius=10)
        y = 80
        for line in instructions_text:
            txt = small_font.render(line, True, (200, 220, 255))
            screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, y))
            y += 25
        back = font.render("Press ESC to go back", True, (255, 150, 150))
        screen.blit(back, (SCREEN_WIDTH // 2 - back.get_width() // 2, SCREEN_HEIGHT - 60))

    elif game_state in (PLAYING, LEVEL_COMPLETE, GAME_OVER, PAUSED):
        # Draw sprites + particle trails
        for entity in all_sprites:
            if hasattr(entity, 'draw_particles'):
                entity.draw_particles(screen)
            screen.blit(entity.image, entity.rect)
        player.draw_particles(screen)

        # Shield ring
        if player.shield:
            pygame.draw.circle(screen, (100, 200, 255), player.rect.center, 40, 3)

        # HUD
        pygame.draw.rect(screen, (20, 20, 50), (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.line(screen, (100, 100, 200), (0, 80), (SCREEN_WIDTH, 80), 2)

        screen.blit(font.render(f"Score: {player.score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Level: {current_level}/{max_level}", True, WHITE),
                    (SCREEN_WIDTH // 2 - 50, 10))
        screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (SCREEN_WIDTH - 150, 10))
        for i in range(player.lives):
            ox = i * 20
            pygame.draw.polygon(screen, GREEN,
                                [(SCREEN_WIDTH - 40 - ox, 45),
                                 (SCREEN_WIDTH - 60 - ox, 65),
                                 (SCREEN_WIDTH - 20 - ox, 65)])
        screen.blit(font.render(f"Coins: {player.coins}", True, YELLOW), (SCREEN_WIDTH - 150, 40))
        pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH - 185, 55), 8)
        screen.blit(small_font.render(f"Weapon Lvl: {player.bullet_power}", True, CYAN), (10, 40))
        screen.blit(small_font.render(f"Fire Rate: {1000 // player.fire_rate}/sec", True, PURPLE), (10, 60))

        shop_hint = small_font.render("S: Shop  P: Pause", True, (150, 255, 150))
        screen.blit(shop_hint, (SCREEN_WIDTH // 2 - shop_hint.get_width() // 2, SCREEN_HEIGHT - 25))

        # Boss health bar
        for enemy in enemies:
            if enemy.enemy_type == 3:
                bw, bh = 200, 15
                bx, by = SCREEN_WIDTH // 2 - bw // 2, 90
                pygame.draw.rect(screen, (50, 50, 50), (bx, by, bw, bh))
                hw = max(0, int(bw * enemy.health / enemy.max_health))
                ratio = enemy.health / enemy.max_health
                hc = (min(255, int(255 * (1 - ratio))), min(255, int(255 * ratio)), 0)
                pygame.draw.rect(screen, hc, (bx, by, hw, bh))
                pygame.draw.rect(screen, (200, 200, 200), (bx, by, bw, bh), 2)
                bl = font.render("BOSS", True, RED)
                screen.blit(bl, (SCREEN_WIDTH // 2 - bl.get_width() // 2, by - 30))

        # Overlays
        if game_state == LEVEL_COMPLETE:
            screen.blit(_overlay_dark, (0, 0))
            cy = SCREEN_HEIGHT // 2
            for txt, color, dy in [
                (font.render(f"LEVEL {current_level} COMPLETE!", True, GREEN), None, -50),
                (font.render(f"Score: {player.score}  Coins: {player.coins}", True, YELLOW), None, 0),
                (font.render("Press N for Next Level or S for Shop", True, CYAN), None, 50),
            ]:
                screen.blit(txt, (SCREEN_WIDTH // 2 - txt.get_width() // 2, cy + dy))

        elif game_state == GAME_OVER:
            screen.blit(_overlay_dark, (0, 0))
            cy = SCREEN_HEIGHT // 2
            go = title_font.render("GAME OVER", True, RED)
            screen.blit(go, (SCREEN_WIDTH // 2 - go.get_width() // 2, cy - 100))
            if current_level > max_level:
                ct = font.render("CONGRATULATIONS! ALL LEVELS COMPLETED!", True, GREEN)
                screen.blit(ct, (SCREEN_WIDTH // 2 - ct.get_width() // 2, cy - 30))
            fs = font.render(f"Final Score: {player.score}", True, YELLOW)
            screen.blit(fs, (SCREEN_WIDTH // 2 - fs.get_width() // 2, cy + 20))
            if player.score > high_score:
                high_score = player.score
                nh = font.render("NEW HIGH SCORE!", True, (255, 200, 0))
                screen.blit(nh, (SCREEN_WIDTH // 2 - nh.get_width() // 2, cy + 60))
            rt = font.render("Press R to Restart", True, (100, 255, 100))
            screen.blit(rt, (SCREEN_WIDTH // 2 - rt.get_width() // 2, cy + 100))

        elif game_state == PAUSED:
            screen.blit(_overlay_blue, (0, 0))
            cy = SCREEN_HEIGHT // 2
            pt = title_font.render("PAUSED", True, CYAN)
            screen.blit(pt, (SCREEN_WIDTH // 2 - pt.get_width() // 2, cy - 50))
            for label, color, dy in [
                ("Press P to Resume", WHITE, 20),
                ("Press ESC for Main Menu", (200, 200, 255), 70),
            ]:
                t = font.render(label, True, color)
                screen.blit(t, (SCREEN_WIDTH // 2 - t.get_width() // 2, cy + dy))

    elif game_state == SHOP:
        pygame.draw.rect(screen, (20, 20, 50), (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), border_radius=15)
        pygame.draw.rect(screen, (100, 100, 200), (50, 50, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 100), 3, border_radius=15)

        title = font.render("SHOP", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))
        ct = font.render(f"Your Coins: {player.coins}", True, YELLOW)
        screen.blit(ct, (SCREEN_WIDTH // 2 - ct.get_width() // 2, 110))

        for i, item in enumerate(shop_items):
            bg = (60, 60, 120) if i == selected_shop_item else (40, 40, 80)
            pygame.draw.rect(screen, bg, (100, 160 + i * 70, SCREEN_WIDTH - 200, 60), border_radius=10)
            pygame.draw.rect(screen, (150, 150, 220), (100, 160 + i * 70, SCREEN_WIDTH - 200, 60), 2, border_radius=10)
            pygame.draw.circle(screen, item.icon_color, (130, 190 + i * 70), 15)
            nc = (200, 255, 200) if i == selected_shop_item else (200, 200, 255)
            nt = font.render(f"{item.name} - {item.cost} coins", True, nc)
            screen.blit(nt, (160, 170 + i * 70))
            dt = small_font.render(item.description, True, (180, 220, 255))
            screen.blit(dt, (160, 200 + i * 70))
            if i == selected_shop_item:
                pygame.draw.polygon(screen, (100, 255, 100),
                                    [(SCREEN_WIDTH - 120, 190 + i * 70),
                                     (SCREEN_WIDTH - 140, 180 + i * 70),
                                     (SCREEN_WIDTH - 140, 200 + i * 70)])

        hint = small_font.render("UP/DOWN: select  ENTER: buy  ESC/S: return", True, (200, 200, 255))
        screen.blit(hint, (SCREEN_WIDTH // 2 - hint.get_width() // 2, SCREEN_HEIGHT - 60))


# ----- Main -----

initialize_shop()
create_enemies(current_level)

while True:
    menu_animation += 0.05
    handle_input()

    if game_state == PLAYING:
        update_game()

    render_game()
    pygame.display.flip()
    clock.tick(60)
