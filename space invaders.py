import pygame
import random
import sys
import math
from pygame.locals import *

# Initialize pygame
pygame.init()

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

### Classes

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))  # TODO: Replace with sprite image
        self.image.fill(GREEN)
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
    
    def update(self):
        self.rect.x += self.speed_x
        # Keep player within screen bounds
        self.rect.clamp_ip(screen.get_rect())
        
        # Update shield status
        if self.shield and pygame.time.get_ticks() - self.shield_time > self.shield_duration:
            self.shield = False
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.fire_rate:
            self.last_shot = current_time
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
            # TODO: Add shooting sound effect

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type=0):
        super().__init__()
        self.enemy_type = enemy_type
        if enemy_type == 0:  # Basic enemy
            self.image = pygame.Surface((40, 40))  # TODO: Replace with sprite
            self.image.fill(RED)
            self.health = 1
            self.points = 10
            self.drop_chance = 0.05
        elif enemy_type == 1:  # Stronger enemy
            self.image = pygame.Surface((40, 40))
            self.image.fill(BLUE)
            self.health = 2
            self.points = 20
            self.drop_chance = 0.1
        elif enemy_type == 2:  # Elite enemy
            self.image = pygame.Surface((50, 50))
            self.image.fill(PURPLE)
            self.health = 3
            self.points = 30
            self.drop_chance = 0.15
        elif enemy_type == 3:  # Boss enemy
            self.image = pygame.Surface((60, 60))
            self.image.fill(YELLOW)
            self.health = 10 + current_level * 2
            self.points = 100 + current_level * 20
            self.drop_chance = 0.5
            self.shoot_chance = 0.01 * (current_level // 5 + 1)
        
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.shoot_chance = 0.002 * (enemy_type + 1) if enemy_type < 3 else self.shoot_chance
    
    def update(self):
        self.rect.x += ENEMY_SPEED * self.direction * (1 + current_level * 0.1)
        if random.random() < self.shoot_chance:
            self.shoot()
    
    def shoot(self):
        if self.enemy_type == 3:  # Boss shoots spread bullets
            for angle in [-15, 0, 15]:
                speed_x = math.sin(math.radians(angle)) * BULLET_SPEED / 2
                speed_y = math.cos(math.radians(angle)) * BULLET_SPEED / 2
                bullet = EnemyBullet(self.rect.centerx, self.rect.bottom, speed_x, speed_y)
                all_sprites.add(bullet)
                enemy_bullets.add(bullet)
        else:
            bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
            all_sprites.add(bullet)
            enemy_bullets.add(bullet)
    
    def hit(self):
        self.health -= 1
        return self.health <= 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_y=-BULLET_SPEED, speed_x=0):
        super().__init__()
        self.image = pygame.Surface((4, 10))  # TODO: Replace with sprite
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_y = speed_y
        self.speed_x = speed_x
    
    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, speed_x=0, speed_y=BULLET_SPEED / 2):
        super().__init__()
        self.image = pygame.Surface((4, 10))  # TODO: Replace with sprite
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speed_x = speed_x
        self.speed_y = speed_y
    
    def update(self):
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        if not screen.get_rect().colliderect(self.rect):
            self.kill()

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface((20, 20))  # TODO: Replace with sprite
        if powerup_type == 0:  # Extra life
            self.image.fill(GREEN)
        elif powerup_type == 1:  # Shield
            self.image.fill(BLUE)
        elif powerup_type == 2:  # Coin
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
    
    def update(self):
        self.rect.y += 2
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size))  # TODO: Replace with animation
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.max_frame = 5
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
    
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == self.max_frame:
                self.kill()
            else:
                size = self.size - self.frame * 5
                self.image = pygame.Surface((size, size))
                self.image.fill(RED)
                self.rect = self.image.get_rect(center=self.rect.center)

class ShopItem:
    def __init__(self, name, description, cost, effect_func):
        self.name = name
        self.description = description
        self.cost = cost
        self.effect_func = effect_func
    
    def purchase(self, player):
        if player.coins >= self.cost:
            player.coins -= self.cost
            self.effect_func(player)
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

# Fonts
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Menu and shop variables
menu_options = ["Start Game", "Instructions", "Quit"]
selected_option = 0
selected_shop_item = 0

# Instructions text
instructions = [
    "Welcome to Space Invaders Deluxe!",
    "Controls:",
    "- Move left/right with arrow keys",
    "- Shoot with spacebar",
    "- Press P to access shop",
    "",
    "Objective:",
    "- Destroy all enemies to complete the level",
    "- Avoid enemy bullets and keep enemies from reaching the bottom",
    "",
    "Shop:",
    "- Use coins to buy upgrades/powerups",
    "- Press P during gameplay to shop",
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
            weights = [0.5 - level * 0.05, 0.3 + level * 0.02, 0.2 + level * 0.03]
            if sum(weights) <= 0:
                weights = [0.5, 0.3, 0.2]
            enemy_type = random.choices([0, 1, 2], weights=weights)[0]
            enemy = Enemy(col * ENEMY_SPACING + 50, row * ENEMY_SPACING + 50, enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)

def initialize_shop():
    """Initialize shop items with effects."""
    global shop_items
    shop_items = [
        ShopItem("Extra Life", "Gain an additional life", 50, lambda p: setattr(p, 'lives', p.lives + 1)),
        ShopItem("Shield", "Temporary invulnerability", 30, lambda p: [setattr(p, 'shield', True), setattr(p, 'shield_time', pygame.time.get_ticks())]),
        ShopItem("Weapon Upgrade", "Increase bullet power", 40, lambda p: setattr(p, 'bullet_power', min(p.bullet_power + 1, 4))),
        ShopItem("Rapid Fire", "Shoot faster", 35, lambda p: setattr(p, 'fire_rate', max(p.fire_rate - 100, 200))),
        ShopItem("Bullet Speed", "Increase bullet speed", 25, lambda p: setattr(p, 'bullet_speed', min(p.bullet_speed + 1, 15))),
        ShopItem("Shield Extender", "Increase shield duration", 30, lambda p: setattr(p, 'shield_duration', p.shield_duration + 5000))
    ]

def reset_game():
    """Reset game to initial state."""
    global game_state, current_level, player, all_sprites, enemies, bullets, enemy_bullets, powerups, boss_spawned
    game_state = MENU
    current_level = 1
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    player = Player()
    all_sprites.add(player)
    create_enemies(current_level)
    boss_spawned = False

def handle_input():
    """Handle user input based on game state."""
    global game_state, selected_option, selected_shop_item, boss_spawned
    for event in pygame.event.get():
        if event.type == QUIT:
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
                elif event.key == K_p:
                    game_state = SHOP
            elif game_state == GAME_OVER:
                if event.key == K_r:
                    reset_game()
            elif game_state == SHOP:
                if event.key == K_UP:
                    selected_shop_item = (selected_shop_item - 1) % len(shop_items)
                elif event.key == K_DOWN:
                    selected_shop_item = (selected_shop_item + 1) % len(shop_items)
                elif event.key == K_RETURN:
                    shop_items[selected_shop_item].purchase(player)
                elif event.key in (K_ESCAPE, K_p):
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
                elif event.key == K_p:
                    game_state = SHOP
        elif event.type == KEYUP:
            if game_state == PLAYING and event.key in (K_LEFT, K_RIGHT):
                player.speed_x = 0

def update_game():
    """Update game logic when playing."""
    if game_state == PLAYING:
        all_sprites.update()
        
        # Enemy movement and direction change
        change_direction = any(e.rect.right >= SCREEN_WIDTH or e.rect.left <= 0 for e in enemies)
        if change_direction:
            for enemy in enemies:
                enemy.rect.y += ENEMY_DROP
                enemy.direction *= -1
        
        # Bullet-enemy collisions
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, _ in hits.items():
            if enemy.hit():
                if random.random() < enemy.drop_chance:
                    powerup = Powerup(enemy.rect.centerx, enemy.rect.centery, random.randint(0, 2))
                    all_sprites.add(powerup)
                    powerups.add(powerup)
                player.score += enemy.points
                player.coins += max(1, enemy.points // 5)
                explosion = Explosion(enemy.rect.center, 40)
                all_sprites.add(explosion)
                enemy.kill()
                # TODO: Add explosion sound
        
        # Player-enemy bullet collisions
        if not player.shield and pygame.sprite.spritecollide(player, enemy_bullets, True):
            player.lives -= 1
            if player.lives <= 0:
                game_state = GAME_OVER
        
        # Powerup collection
        for powerup in pygame.sprite.spritecollide(player, powerups, True):
            if powerup.powerup_type == 0:
                player.lives += 1
            elif powerup.powerup_type == 1:
                player.shield = True
                player.shield_time = pygame.time.get_ticks()
            elif powerup.powerup_type == 2:
                player.coins += 10
            # TODO: Add pickup sound
        
        # Check if enemies reach bottom
        if any(e.rect.bottom >= SCREEN_HEIGHT - 50 for e in enemies):
            game_state = GAME_OVER
        
        # Level completion or boss spawn
        if not enemies:
            if current_level % 5 == 0 and not boss_spawned:
                boss = Enemy(SCREEN_WIDTH // 2, 50, 3)
                all_sprites.add(boss)
                enemies.add(boss)
                boss_spawned = True
            else:
                game_state = LEVEL_COMPLETE

def render_game():
    """Render the game based on current state."""
    screen.fill(BLACK)
    if game_state == MENU:
        title = font.render("SPACE INVADERS DELUXE", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        for i, option in enumerate(menu_options):
            color = GREEN if i == selected_option else WHITE
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 50))
    elif game_state == INSTRUCTIONS:
        y = 100
        for line in instructions:
            text = font.render(line, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, y))
            y += 40
    elif game_state in (PLAYING, LEVEL_COMPLETE, GAME_OVER):
        all_sprites.draw(screen)
        if player.shield:
            pygame.draw.circle(screen, BLUE, player.rect.center, 40, 2)
        # HUD
        screen.blit(font.render(f"Score: {player.score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Level: {current_level}", True, WHITE), (SCREEN_WIDTH // 2 - 50, 10))
        screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (SCREEN_WIDTH - 150, 10))
        screen.blit(font.render(f"Coins: {player.coins}", True, YELLOW), (SCREEN_WIDTH - 150, 40))
        screen.blit(small_font.render(f"Weapon Lvl: {player.bullet_power}", True, WHITE), (10, 40))
        screen.blit(small_font.render(f"Fire Rate: {1000 // player.fire_rate}/sec", True, WHITE), (10, 70))
        shop_text = small_font.render("Press P for Shop", True, WHITE)
        screen.blit(shop_text, (SCREEN_WIDTH // 2 - shop_text.get_width() // 2, SCREEN_HEIGHT - 30))
        
        if game_state == LEVEL_COMPLETE:
            text = font.render(f"LEVEL {current_level} COMPLETE!", True, GREEN)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            text = font.render("Press N for Next Level or P for Shop", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        
        if game_state == GAME_OVER:
            text = font.render("GAME OVER", True, RED)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            if current_level > max_level:
                text = font.render("YOU WON! ALL LEVELS COMPLETE!", True, GREEN)
                screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2))
            text = font.render("Press R to Restart", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            text = font.render(f"Final Score: {player.score}", True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
    elif game_state == SHOP:
        screen.blit(font.render("SHOP", True, YELLOW), (SCREEN_WIDTH // 2 - 50, 50))
        screen.blit(font.render(f"Your Coins: {player.coins}", True, YELLOW), (SCREEN_WIDTH // 2 - 80, 100))
        for i, item in enumerate(shop_items):
            color = GREEN if i == selected_shop_item else WHITE
            text = font.render(f"{item.name} - {item.cost} coins", True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 180 + i * 60))
            text = small_font.render(item.description, True, WHITE)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 210 + i * 60))
        text = small_font.render("UP/DOWN to select, ENTER to buy, ESC/P to return", True, WHITE)
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, SCREEN_HEIGHT - 50))

### Initialization and Main Loop

initialize_shop()
create_enemies(current_level)

while True:
    handle_input()
    update_game()
    render_game()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
