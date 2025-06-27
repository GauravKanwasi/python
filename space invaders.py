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
    if not os.path.exists(f'assets/{sound_file}'):
        open(f'assets/{sound_file}', 'a').close()

# Load sounds
try:
    shoot_sound = mixer.Sound('assets/shoot.wav')
    explosion_sound = mixer.Sound('assets/explosion.wav')
    powerup_sound = mixer.Sound('assets/powerup.wav')
    hit_sound = mixer.Sound('assets/hit.wav')
    mixer.music.load('assets/music.wav')
    mixer.music.set_volume(0.3)
    mixer.music.play(-1)  # Loop the music
except:
    # If sounds can't be loaded, create dummy functions
    def shoot_sound(): pass
    def explosion_sound(): pass
    def powerup_sound(): pass
    def hit_sound(): pass
    mixer.music.stop = lambda: None

# Particle class for visual effects
class Particle:
    def __init__(self, x, y, color, velocity_x=0, velocity_y=0, size=3, life=20):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.size = size
        self.life = life
        self.age = 0
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # Gravity effect
        self.age += 1
        self.size = max(0, self.size - 0.05)
        return self.age < self.life
        
    def draw(self, surface):
        alpha = 255 * (1 - self.age / self.life)
        color_with_alpha = (*self.color, int(alpha))
        pygame.draw.circle(surface, color_with_alpha, (int(self.x), int(self.y)), int(self.size))

# Starfield background
class Starfield:
    def __init__(self, num_stars=100):
        self.stars = []
        for _ in range(num_stars):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            speed = random.uniform(0.1, 0.5)
            size = random.randint(1, 2)
            brightness = random.randint(100, 255)
            self.stars.append([x, y, speed, size, brightness])
            
    def update(self):
        for star in self.stars:
            star[1] += star[2]  # Move down
            if star[1] > SCREEN_HEIGHT:
                star[1] = 0
                star[0] = random.randint(0, SCREEN_WIDTH)
                
    def draw(self, surface):
        for star in self.stars:
            x, y, _, size, brightness = star
            color = (brightness, brightness, brightness)
            pygame.draw.circle(surface, color, (int(x), int(y)), size)

### Classes

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Create player ship with more detail
        self.image = pygame.Surface((50, 40), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (0, 40), (50, 40)])
        pygame.draw.polygon(self.image, BLUE, [(25, 10), (10, 30), (40, 30)])
        pygame.draw.circle(self.image, YELLOW, (25, 20), 5)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.bullet_power = 1
        self.fire_rate = 500  # Milliseconds between shots
        self.last_shot = 0
        self.shield = False
        self.shield_time = 0
        self.shield_duration = 10000  # 10 seconds
        self.bullet_speed = 7  # Customizable bullet speed
        self.spread_shot = False
        self.spread_shot_time = 0
        self.spread_duration = 10000  # 10 seconds
        self.particles = []
    
    def update(self):
        self.rect.x += self.speed_x
        # Keep player within screen bounds
        self.rect.clamp_ip(screen.get_rect())
        
        # Update shield status
        if self.shield and pygame.time.get_ticks() - self.shield_time > self.shield_duration:
            self.shield = False
            
        # Update spread shot status
        if self.spread_shot and pygame.time.get_ticks() - self.spread_shot_time > self.spread_duration:
            self.spread_shot = False
            
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Create engine particles
        if random.random() < 0.3:
            self.particles.append(Particle(
                self.rect.centerx + random.randint(-5, 5),
                self.rect.bottom,
                (0, random.randint(150, 255), random.randint(200, 255)),
                velocity_y=random.uniform(1.0, 3.0),
                velocity_x=random.uniform(-0.5, 0.5),
                size=random.uniform(2, 4),
                life=random.randint(20, 40)
            )
    
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.fire_rate:
            self.last_shot = current_time
            shoot_sound()
            
            # Create bullets based on power level
            if self.bullet_power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top, speed_y=-self.bullet_speed)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif self.bullet_power == 2:
                bullet1 = Bullet(self.rect.left + 10, self.rect.top, speed_y=-self.bullet_speed)
                bullet2 = Bullet(self.rect.right - 10, self.rect.top, speed_y=-self.bullet_speed)
                all_sprites.add(bullet1, bullet2)
                bullets.add(bullet1, bullet2)
            elif self.bullet_power >= 3:
                bullet1 = Bullet(self.rect.left + 10, self.rect.top, speed_y=-self.bullet_speed)
                bullet2 = Bullet(self.rect.centerx, self.rect.top, speed_y=-self.bullet_speed)
                bullet3 = Bullet(self.rect.right - 10, self.rect.top, speed_y=-self.bullet_speed)
                all_sprites.add(bullet1, bullet2, bullet3)
                bullets.add(bullet1, bullet2, bullet3)
                if self.bullet_power >= 4:
                    bullet4 = Bullet(self.rect.left, self.rect.centery, speed_y=-self.bullet_speed, speed_x=-2)
                    bullet5 = Bullet(self.rect.right, self.rect.centery, speed_y=-self.bullet_speed, speed_x=2)
                    all_sprites.add(bullet4, bullet5)
                    bullets.add(bullet4, bullet5)
            
            # Add spread shot if active
            if self.spread_shot:
                for angle in [-30, -15, 0, 15, 30]:
                    rad = math.radians(angle)
                    speed_x = math.sin(rad) * 3
                    speed_y = math.cos(rad) * -self.bullet_speed
                    spread_bullet = Bullet(self.rect.centerx, self.rect.top, speed_y=speed_y, speed_x=speed_x)
                    all_sprites.add(spread_bullet)
                    bullets.add(spread_bullet)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type=0, level=1):
        super().__init__()
        self.enemy_type = enemy_type
        self.level = level
        self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
        
        # Different appearances for different enemy types
        if enemy_type == 0:  # Basic enemy
            pygame.draw.circle(self.image, RED, (20, 20), 15)
            pygame.draw.circle(self.image, (255, 150, 150), (20, 20), 10)
            self.health = 1
            self.points = 10
            self.drop_chance = 0.05
            self.shoot_chance = 0.002
        elif enemy_type == 1:  # Stronger enemy
            pygame.draw.rect(self.image, BLUE, (5, 5, 30, 30))
            pygame.draw.rect(self.image, (100, 100, 255), (10, 10, 20, 20))
            self.health = 2
            self.points = 20
            self.drop_chance = 0.1
            self.shoot_chance = 0.003
        elif enemy_type == 2:  # Elite enemy
            pygame.draw.polygon(self.image, PURPLE, [(20, 0), (0, 40), (40, 40)])
            pygame.draw.polygon(self.image, (200, 100, 200), [(20, 10), (10, 30), (30, 30)])
            self.health = 3
            self.points = 30
            self.drop_chance = 0.15
            self.shoot_chance = 0.005
        elif enemy_type == 3:  # Boss enemy
            size = 60
            self.image = pygame.Surface((size, size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, YELLOW, (size//2, size//2), size//2)
            pygame.draw.circle(self.image, ORANGE, (size//2, size//2), size//2 - 5)
            # Draw boss details
            pygame.draw.circle(self.image, RED, (size//3, size//3), 5)
            pygame.draw.circle(self.image, RED, (2*size//3, size//3), 5)
            pygame.draw.arc(self.image, BLACK, (size//4, size//2, size//2, size//3), 0, math.pi, 3)
            self.health = 10 + level * 2
            self.max_health = self.health
            self.points = 100 + level * 20
            self.drop_chance = 0.5
            self.shoot_chance = 0.01 * (level // 5 + 1)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.oscillation = 0
        self.particles = []
        self.osc_speed = random.uniform(0.05, 0.1)
        self.osc_amp = random.randint(5, 15)
        
    def update(self):
        # Horizontal movement with oscillation for more dynamic motion
        self.rect.x += ENEMY_SPEED * self.direction * (1 + self.level * 0.1)
        self.oscillation += self.osc_speed
        self.rect.y += math.sin(self.oscillation) * self.osc_amp * 0.1
        
        # Shooting logic
        if random.random() < self.shoot_chance:
            self.shoot()
            
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        # Create engine particles for boss
        if self.enemy_type == 3 and random.random() < 0.1:
            self.particles.append(Particle(
                self.rect.centerx + random.randint(-20, 20),
                self.rect.bottom,
                (random.randint(200, 255), random.randint(100, 150), 0),
                velocity_y=random.uniform(1.0, 2.0),
                velocity_x=random.uniform(-0.5, 0.5),
                size=random.uniform(3, 6),
                life=random.randint(30, 50)
            )
    
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)
    
    def shoot(self):
        if self.enemy_type == 3:  # Boss shoots spread bullets
            for angle in [-30, -15, 0, 15, 30]:
                rad = math.radians(angle)
                speed_x = math.sin(rad) * BULLET_SPEED / 2
                speed_y = math.cos(rad) * BULLET_SPEED / 2
                bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, speed_x, speed_y)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)
        elif self.enemy_type == 2:  # Elite shoots double bullets
            bullet1 = EnemyBullet(self.rect.left + 10, self.rect.bottom)
            bullet2 = EnemyBullet(self.rect.right - 10, self.rect.bottom)
            all_sprites.add(bullet1, bullet2)
            enemy_bullets.add(bullet1, bullet2)
        else:
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
    
    def hit(self, particles):
        self.health -= 1
        hit_sound()
        
        # Create hit particles
        for _ in range(10):
            particles.append(Particle(
                self.rect.centerx + random.randint(-15, 15),
                self.rect.centery + random.randint(-15, 15),
                (255, random.randint(50, 150), 0),
                velocity_x=random.uniform(-2, 2),
                velocity_y=random.uniform(-2, 2),
                size=random.uniform(2, 4),
                life=random.randint(15, 30)
            ))
        
        return self.health <= 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y=-BULLET_SPEED, speed_x=0, color=WHITE):
        super().__init__()
        self.image = pygame.Surface((6, 15), pygame.SRCALPHA)
        pygame.draw.rect(self.image, color, (0, 0, 6, 15))
        pygame.draw.rect(self.image, YELLOW, (1, 1, 4, 13))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = speed_y
        self.speed_x = speed_x
        self.particles = []
    
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        
        # Create trail particles
        if random.random() < 0.5:
            self.particles.append(Particle(
                self.rect.centerx,
                self.rect.bottom,
                (random.randint(200, 255), random.randint(200, 255), random.randint(50, 150)),
                velocity_y=random.uniform(-1.0, 1.0),
                velocity_x=random.uniform(-0.5, 0.5),
                size=random.uniform(1, 3),
                life=random.randint(10, 20)
            )
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
        
        if not screen.get_rect().colliderect(self.rect):
            self.kill()
    
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)

class EnemyBullet(Bullet):
    def __init__(self, x, y, speed_x=0, speed_y=BULLET_SPEED / 2):
        super().__init__(x, y, speed_y, speed_x, color=RED)
        self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
        pygame.draw.rect(self.image, RED, (0, 0, 8, 20))
        pygame.draw.rect(self.image, ORANGE, (1, 1, 6, 18))
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        
        # Different appearances for different powerups
        if powerup_type == 0:  # Extra life
            pygame.draw.circle(self.image, GREEN, (15, 15), 12)
            pygame.draw.circle(self.image, (150, 255, 150), (15, 15), 8)
            pygame.draw.polygon(self.image, WHITE, [(15, 8), (10, 18), (20, 18)])
        elif powerup_type == 1:  # Shield
            pygame.draw.circle(self.image, BLUE, (15, 15), 12)
            pygame.draw.circle(self.image, CYAN, (15, 15), 8)
            pygame.draw.circle(self.image, BLUE, (15, 15), 12, 3)
        elif powerup_type == 2:  # Coin
            pygame.draw.circle(self.image, YELLOW, (15, 15), 12)
            pygame.draw.circle(self.image, (255, 200, 0), (15, 15), 8)
            pygame.draw.circle(self.image, (200, 150, 0), (15, 15), 12, 2)
        elif powerup_type == 3:  # Spread shot
            pygame.draw.circle(self.image, PURPLE, (15, 15), 12)
            pygame.draw.circle(self.image, (200, 100, 200), (15, 15), 8)
            # Draw spread pattern
            for angle in [-30, 0, 30]:
                rad = math.radians(angle)
                end_x = 15 + math.sin(rad) * 10
                end_y = 15 - math.cos(rad) * 10
                pygame.draw.line(self.image, WHITE, (15, 15), (end_x, end_y), 2)
        
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.animation_offset = 0
        self.animation_direction = 1
    
    def update(self):
        self.rect.y += 2
        
        # Float animation
        self.animation_offset += 0.1 * self.animation_direction
        if abs(self.animation_offset) > 5:
            self.animation_direction *= -1
        self.rect.x += math.sin(self.animation_offset) * 0.5
        
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size, color=RED):
        super().__init__()
        self.size = size
        self.color = color
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size//2, size//2), size//2)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.max_frame = 10
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.particles = []
        
        # Create initial explosion particles
        for _ in range(30):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1.0, 5.0)
            self.particles.append(Particle(
                center[0], center[1],
                (random.randint(200, 255), random.randint(50, 150), 0),
                velocity_x=math.sin(angle) * speed,
                velocity_y=math.cos(angle) * speed,
                size=random.uniform(2, 5),
                life=random.randint(20, 40)
            )
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == self.max_frame:
                self.kill()
            else:
                # Update explosion size
                self.size = max(5, self.size - 2)
                self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
                alpha = 255 * (1 - self.frame / self.max_frame)
                pygame.draw.circle(self.image, (*self.color, int(alpha)), 
                                 (self.size//2, self.size//2), self.size//2)
                self.rect = self.image.get_rect(center=self.rect.center)
        
        # Update particles
        self.particles = [p for p in self.particles if p.update()]
    
    def draw_particles(self, surface):
        for particle in self.particles:
            particle.draw(surface)

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
            powerup_sound()
            return True
        return False

### Sprite Groups and Initial Setup

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

# Menu and shop variables
menu_options = ["Start Game", "Instructions", "Quit"]
selected_option = 0
selected_shop_item = 0
menu_animation = 0

# Instructions text
instructions = [
    "Welcome to Space Invaders Deluxe!",
    "Controls:",
    "- Move left/right with arrow keys",
    "- Shoot with spacebar",
    "- Press S to access shop",
    "- Press P to pause game",
    "",
    "Objective:",
    "- Destroy all enemies to complete the level",
    "- Avoid enemy bullets and keep enemies from reaching the bottom",
    "",
    "Shop:",
    "- Use coins to buy upgrades/powerups",
    "- Press S during gameplay to shop",
    "",
    "Powerups:",
    "- Green: Extra Life",
    "- Blue: Temporary Shield",
    "- Yellow: Coins",
    "- Purple: Spread Shot",
    "",
    "Press ESC to return to menu"
]

### Functions

def create_enemies(level):
    """Create enemies for the given level."""
    global boss_spawned
    boss_spawned = False
    rows = min(ENEMY_ROWS + level // 2, 8)
    cols = min(ENEMY_COLS + level // 3, 15)
    for row in range(rows):
        for col in range(cols):
            # Adjust enemy type probabilities based on level
            weights = [
                0.6 - level * 0.03,  # Basic
                0.25 + level * 0.02, # Stronger
                0.15 + level * 0.01  # Elite
            ]
            if level % 5 == 0 and row == 0:  # First row has elites on boss levels
                weights = [0.1, 0.3, 0.6]
                
            enemy_type = random.choices([0, 1, 2], weights=weights)[0]
            x = col * ENEMY_SPACING + 50
            y = row * ENEMY_SPACING + 50
            
            # Create enemy with level parameter
            enemy = Enemy(x, y, enemy_type, level)
            all_sprites.add(enemy)
            enemies.add(enemy)

def initialize_shop():
    """Initialize shop items with effects."""
    global shop_items
    shop_items = [
        ShopItem("Extra Life", "Gain an additional life", 50, 
                 lambda p: setattr(p, 'lives', p.lives + 1), GREEN),
        ShopItem("Shield", "Temporary invulnerability", 30, 
                 lambda p: [setattr(p, 'shield', True), setattr(p, 'shield_time', pygame.time.get_ticks())], BLUE),
        ShopItem("Weapon Upgrade", "Increase bullet power", 40, 
                 lambda p: setattr(p, 'bullet_power', min(p.bullet_power + 1, 4)), CYAN),
        ShopItem("Rapid Fire", "Shoot faster", 35, 
                 lambda p: setattr(p, 'fire_rate', max(p.fire_rate - 100, 200)), PURPLE),
        ShopItem("Bullet Speed", "Increase bullet speed", 25, 
                 lambda p: setattr(p, 'bullet_speed', min(p.bullet_speed + 1, 15)), YELLOW),
        ShopItem("Shield Extender", "Increase shield duration", 30, 
                 lambda p: setattr(p, 'shield_duration', p.shield_duration + 5000)), ORANGE),
        ShopItem("Spread Shot", "Temporary spread shot", 45, 
                 lambda p: [setattr(p, 'spread_shot', True), setattr(p, 'spread_shot_time', pygame.time.get_ticks())], (255, 100, 255))
    ]

def reset_game():
    """Reset game to initial state."""
    global game_state, current_level, player, all_sprites, enemies, bullets, enemy_bullets, powerups, boss_spawned, global_particles
    game_state = MENU
    current_level = 1
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    global_particles = []
    player = Player()
    all_sprites.add(player)
    create_enemies(current_level)
    boss_spawned = False

def handle_input():
    """Handle user input based on game state."""
    global game_state, selected_option, selected_shop_item, boss_spawned, high_score, global_particles
    
    for event in pygame.event.get():
        if event.type == QUIT:
            # Save high score
            if player.score > high_score:
                high_score = player.score
            sys.exit()
        elif event.type == KEYDOWN:
            if game_state == MENU:
                if event.key == K_UP:
                    selected_option = (selected_option - 1) % len(menu_options)
                elif event.key == K_DOWN:
                    selected_option = (selected_option + 1) % len(menu_options)
                elif event.key == K_RETURN:
                    if menu_options[selected_option] == "Start Game":
                        game_state = PLAYING
                    elif menu_options[selected_option] == "Instructions":
                        game_state = INSTRUCTIONS
                    elif menu_options[selected_option] == "Quit":
                        if player.score > high_score:
                            high_score = player.score
                        sys.exit()
            elif game_state == INSTRUCTIONS:
                if event.key == K_ESCAPE:
                    game_state = MENU
            elif game_state == PLAYING:
                if event.key == K_LEFT:
                    player.speed_x = -PLAYER_SPEED
                elif event.key == K_RIGHT:
                    player.speed_x = PLAYER_SPEED
                elif event.key == K_SPACE:
                    player.shoot()
                elif event.key == K_s:
                    game_state = SHOP
                elif event.key == K_p:
                    game_state = PAUSED
            elif game_state == GAME_OVER:
                if event.key == K_r:
                    # Save high score
                    if player.score > high_score:
                        high_score = player.score
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
                    global current_level
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
    """Update game logic when playing."""
    global game_state, boss_spawned, global_particles
    
    if game_state == PLAYING:
        all_sprites.update()
        starfield.update()
        
        # Update global particles
        global_particles = [p for p in global_particles if p.update()]
        
        # Enemy movement and direction change
        change_direction = False
        for enemy in enemies:
            if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                change_direction = True
                break
        
        if change_direction:
            for enemy in enemies:
                enemy.rect.y += ENEMY_DROP
                enemy.direction *= -1
        
        # Bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            for _ in bullet_list:
                if enemy.hit(global_particles):
                    # Drop powerup
                    if random.random() < enemy.drop_chance:
                        powerup_type = random.randint(0, 3)  # Now includes spread shot
                        powerup = Powerup(enemy.rect.centerx, enemy.rect.centery, powerup_type)
                        all_sprites.add(powerup)
                        powerups.add(powerup)
                    
                    player.score += enemy.points
                    player.coins += max(1, enemy.points // 5)
                    
                    # Create explosion
                    explosion = Explosion(enemy.rect.center, 40, 
                                        color=(255, min(200, enemy.points), 0))
                    all_sprites.add(explosion)
                    explosion_sound()
                    enemy.kill()
        
        # Player-enemy bullet collisions
        if not player.shield and pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.lives -= 1
            if player.lives <= 0:
                game_state = GAME_OVER
            else:
                # Create hit effect
                for _ in range(20):
                    global_particles.append(Particle(
                        player.rect.centerx + random.randint(-20, 20),
                        player.rect.centery + random.randint(-20, 20),
                        (255, 50, 50),
                        velocity_x=random.uniform(-3, 3),
                        velocity_y=random.uniform(-3, 3),
                        size=random.uniform(3, 6),
                        life=random.randint(20, 40)
                    ))
                hit_sound()
        
        # Powerup collection
        for powerup in pygame.sprite.spritecollide(player, powerups, True):
            if powerup.powerup_type == 0:
                player.lives += 1
            elif powerup.powerup_type == 1:
                player.shield = True
                player.shield_time = pygame.time.get_ticks()
            elif powerup.powerup_type == 2:
                player.coins += 10
            elif powerup.powerup_type == 3:
                player.spread_shot = True
                player.spread_shot_time = pygame.time.get_ticks()
            
            # Create collection effect
            for _ in range(15):
                color = (0, 255, 0) if powerup.powerup_type == 0 else \
                        (0, 200, 255) if powerup.powerup_type == 1 else \
                        (255, 200, 0) if powerup.powerup_type == 2 else \
                        (200, 100, 200)
                global_particles.append(Particle(
                    powerup.rect.centerx,
                    powerup.rect.centery,
                    color,
                    velocity_x=random.uniform(-2, 2),
                    velocity_y=random.uniform(-2, 2),
                    size=random.uniform(2, 4),
                    life=random.randint(20, 40)
                ))
            powerup_sound()
        
        # Check if enemies reach bottom
        if any(e.rect.bottom >= SCREEN_HEIGHT - 50 for e in enemies):
            game_state = GAME_OVER
        
        # Level completion or boss spawn
        if not enemies:
            if current_level % 5 == 0 and not boss_spawned:
                boss = Enemy(SCREEN_WIDTH // 2, 50, 3, current_level)
                all_sprites.add(boss)
                enemies.add(boss)
                boss_spawned = True
            else:
                game_state = LEVEL_COMPLETE
                # Add level complete particles
                for _ in range(100):
                    global_particles.append(Particle(
                        random.randint(0, SCREEN_WIDTH),
                        random.randint(0, SCREEN_HEIGHT),
                        (random.randint(100, 255), random.randint(100, 255), random.randint(200, 255)),
                        velocity_x=random.uniform(-1, 1),
                        velocity_y=random.uniform(-1, 1),
                        size=random.uniform(2, 5),
                        life=random.randint(30, 60)
                    ))

def render_game():
    """Render the game based on current state."""
    screen.fill(DARK_BLUE)
    starfield.draw(screen)
    
    # Draw global particles
    for particle in global_particles:
        particle.draw(screen)
    
    if game_state == MENU:
        # Animated title
        title_offset = math.sin(menu_animation) * 5
        title = title_font.render("SPACE INVADERS DELUXE", True, (100, 255, 255))
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 80 + title_offset))
        
        # High score
        if high_score > 0:
            score_text = font.render(f"High Score: {high_score}", True, YELLOW)
            screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 150))
        
        # Menu options with animation
        for i, option in enumerate(menu_options):
            color = (100, 255, 100) if i == selected_option else (200, 200, 255)
            offset = math.sin(menu_animation + i * 0.5) * 3
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 50 + offset))
            
            # Add particles for selected option
            if i == selected_option:
                pygame.draw.circle(screen, color, 
                                  (SCREEN_WIDTH // 2 - text.get_width() // 2 - 20, 
                                   250 + i * 50 + offset + text.get_height() // 2), 
                                  8)
                pygame.draw.circle(screen, color, 
                                  (SCREEN_WIDTH // 2 + text.get_width() // 2 + 20, 
                                   250 + i * 50 + offset + text.get_height() // 2), 
                                  8)
        
        # Add animated stars
        for i in range(5):
            x = math.sin(menu_animation * 0.5 + i) * 100 + SCREEN_WIDTH // 2
            y = math.cos(menu_animation * 0.3 + i) * 50 + 400
            size = 2 + math.sin(menu_animation + i) * 1
            pygame.draw.circle(screen, (200, 200, 255), (int(x), int(y)), int(size))
        
        # Version info
        version = small_font.render("v2.0 Enhanced Edition", True, (150, 150, 255))
        screen.blit(version, (SCREEN_WIDTH - version.get_width() - 10, SCREEN_HEIGHT - 30))
        
    elif game_state == INSTRUCTIONS:
        # Draw instructions with background
        pygame.draw.rect(screen, (30, 30, 60), (50, 50, SCREEN_WIDTH-100, SCREEN_HEIGHT-100), border_radius=10)
        pygame.draw.rect(screen, (100, 100, 200), (50, 50, SCREEN_WIDTH-100, SCREEN_HEIGHT-100), 3, border_radius=10)
        
        y = 80
        for i, line in enumerate(instructions):
            color = (200, 200, 255) if i < 2 else (180, 220, 255) if i < 6 else (200, 255, 200) if i < 11 else (255, 220, 180)
            text = small_font.render(line, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 25
        
        # Back button
        back_text = font.render("Press ESC to go back", True, (255, 150, 150))
        screen.blit(back_text, (SCREEN_WIDTH // 2 - back_text.get_width() // 2, SCREEN_HEIGHT - 60))
        
    elif game_state in (PLAYING, LEVEL_COMPLETE, GAME_OVER, PAUSED):
        # Draw all sprites
        for entity in all_sprites:
            if hasattr(entity, 'draw_particles'):
                entity.draw_particles(screen)
            screen.blit(entity.image, entity.rect)
        
        # Draw player particles
        player.draw_particles(screen)
        
        # Draw shield if active
        if player.shield:
            pygame.draw.circle(screen, (100, 200, 255, 100), player.rect.center, 40, 3)
        
        # HUD background
        pygame.draw.rect(screen, (20, 20, 50, 180), (0, 0, SCREEN_WIDTH, 80))
        pygame.draw.line(screen, (100, 100, 200), (0, 80), (SCREEN_WIDTH, 80), 2)
        
        # HUD elements
        screen.blit(font.render(f"Score: {player.score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Level: {current_level}/{max_level}", True, WHITE), (SCREEN_WIDTH // 2 - 50, 10))
        
        # Lives display
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
        for i in range(player.lives):
            pygame.draw.polygon(screen, GREEN, 
                              [(SCREEN_WIDTH - 40 - i*20, 45), 
                               (SCREEN_WIDTH - 60 - i*20, 65), 
                               (SCREEN_WIDTH - 20 - i*20, 65)])
        
        # Coins display
        screen.blit(font.render(f"Coins: {player.coins}", True, YELLOW), (SCREEN_WIDTH - 150, 40))
        pygame.draw.circle(screen, YELLOW, (SCREEN_WIDTH - 185, 55), 8)
        
        # Weapon info
        screen.blit(small_font.render(f"Weapon Lvl: {player.bullet_power}", True, CYAN), (10, 40))
        screen.blit(small_font.render(f"Fire Rate: {1000 // player.fire_rate}/sec", True, PURPLE), (10, 70))
        
        # Shop indicator
        shop_text = small_font.render("Press S for Shop", True, (150, 255, 150))
        screen.blit(shop_text, (SCREEN_WIDTH // 2 - shop_text.get_width() // 2, SCREEN_HEIGHT - 30))
        
        # Pause indicator
        pause_text = small_font.render("Press P to Pause", True, (150, 200, 255))
        screen.blit(pause_text, (SCREEN_WIDTH - pause_text.get_width() - 10, SCREEN_HEIGHT - 30))
        
        # Draw boss health bar if boss exists
        for enemy in enemies:
            if enemy.enemy_type == 3:  # Boss
                bar_width = 200
                bar_height = 15
                x = SCREEN_WIDTH // 2 - bar_width // 2
                y = 90
                
                # Background
                pygame.draw.rect(screen, (50, 50, 50), (x, y, bar_width, bar_height))
                # Health
                health_width = max(0, bar_width * enemy.health / enemy.max_health)
                health_color = (
                    min(255, 255 * (1 - enemy.health / enemy.max_health)),
                    min(255, 255 * (enemy.health / enemy.max_health)),
                    0
                )
                pygame.draw.rect(screen, health_color, (x, y, health_width, bar_height))
                # Border
                pygame.draw.rect(screen, (200, 200, 200), (x, y, bar_width, bar_height), 2)
                
                # Boss label
                boss_text = font.render("BOSS", True, RED)
                screen.blit(boss_text, (SCREEN_WIDTH // 2 - boss_text.get_width() // 2, y - 30))
        
        if game_state == LEVEL_COMPLETE:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            text = font.render(f"LEVEL {current_level} COMPLETE!", True, GREEN)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            text = font.render(f"Score: {player.score}  Coins: {player.coins}", True, YELLOW)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            text = font.render("Press N for Next Level or S for Shop", True, CYAN)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        
        elif game_state == GAME_OVER:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            screen.blit(overlay, (0, 0))
            
            text = title_font.render("GAME OVER", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
            
            if current_level > max_level:
                text = font.render("CONGRATULATIONS! ALL LEVELS COMPLETED!", True, GREEN)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            
            text = font.render(f"Final Score: {player.score}", True, YELLOW)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            
            if player.score > high_score:
                high_score = player.score
                text = font.render("NEW HIGH SCORE!", True, (255, 200, 0))
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))
            
            text = font.render("Press R to Restart", True, (100, 255, 100))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
        
        elif game_state == PAUSED:
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 50, 180))
            screen.blit(overlay, (0, 0))
            
            text = title_font.render("PAUSED", True, CYAN)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            text = font.render("Press P to Resume", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
            
            text = font.render("Press ESC for Main Menu", True, (200, 200, 255))
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
            
    elif game_state == SHOP:
        # Shop background
        pygame.draw.rect(screen, (20, 20, 50), (50, 50, SCREEN_WIDTH-100, SCREEN_HEIGHT-100), border_radius=15)
        pygame.draw.rect(screen, (100, 100, 200), (50, 50, SCREEN_WIDTH-100, SCREEN_HEIGHT-100), 3, border_radius=15)
        
        # Shop title
        title = font.render("SHOP", True, YELLOW)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 70))
        
        # Player coins
        coins_text = font.render(f"Your Coins: {player.coins}", True, YELLOW)
        screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 110))
        
        # Shop items
        for i, item in enumerate(shop_items):
            # Item background
            bg_color = (40, 40, 80) if i != selected_shop_item else (60, 60, 120)
            pygame.draw.rect(screen, bg_color, (100, 160 + i * 70, SCREEN_WIDTH-200, 60), border_radius=10)
            pygame.draw.rect(screen, (150, 150, 220), (100, 160 + i * 70, SCREEN_WIDTH-200, 60), 2, border_radius=10)
            
            # Item icon
            pygame.draw.circle(screen, item.icon_color, (130, 190 + i * 70), 15)
            
            # Item name and cost
            name_color = (200, 255, 200) if i == selected_shop_item else (200, 200, 255)
            name_text = font.render(f"{item.name} - {item.cost} coins", True, name_color)
            screen.blit(name_text, (160, 170 + i * 70))
            
            # Item description
            desc_text = small_font.render(item.description, True, (180, 220, 255))
            screen.blit(desc_text, (160, 200 + i * 70))
            
            # Selection indicator
            if i == selected_shop_item:
                pygame.draw.polygon(screen, (100, 255, 100), 
                                  [(SCREEN_WIDTH - 120, 190 + i * 70),
                                   (SCREEN_WIDTH - 140, 180 + i * 70),
                                   (SCREEN_WIDTH - 140, 200 + i * 70)])
        
        # Instructions
        text = small_font.render("UP/DOWN to select, ENTER to buy, ESC/S to return", True, (200, 200, 255))
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 60))

### Initialization and Main Loop

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

pygame.quit()
sys.exit()
