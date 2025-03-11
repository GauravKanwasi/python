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
PLAYING = 1
GAME_OVER = 2
SHOP = 3
LEVEL_COMPLETE = 4

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 30))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10
        self.speed_x = 0
        self.lives = 3
        self.score = 0
        self.coins = 0
        self.bullet_power = 1
        self.fire_rate = 500  # milliseconds between shots
        self.last_shot = 0
        self.shield = False
        self.shield_time = 0
        self.shield_duration = 10000  # 10 seconds
    
    def update(self):
        self.rect.x += self.speed_x
        # Keep player on screen
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
            
        # Update shield
        if self.shield:
            if pygame.time.get_ticks() - self.shield_time > self.shield_duration:
                self.shield = False
    
    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot > self.fire_rate:
            self.last_shot = current_time
            
            # Create bullets based on power level
            if self.bullet_power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
            elif self.bullet_power == 2:
                bullet1 = Bullet(self.rect.left + 10, self.rect.top)
                bullet2 = Bullet(self.rect.right - 10, self.rect.top)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
            elif self.bullet_power >= 3:
                bullet1 = Bullet(self.rect.left + 10, self.rect.top)
                bullet2 = Bullet(self.rect.centerx, self.rect.top)
                bullet3 = Bullet(self.rect.right - 10, self.rect.top)
                all_sprites.add(bullet1, bullet2, bullet3)
                bullets.add(bullet1, bullet2, bullet3)
                
                # Special side bullets for power level 4
                if self.bullet_power >= 4:
                    bullet4 = Bullet(self.rect.left, self.rect.centery)
                    bullet4.speed_x = -2
                    bullet5 = Bullet(self.rect.right, self.rect.centery)
                    bullet5.speed_x = 2
                    all_sprites.add(bullet4, bullet5)
                    bullets.add(bullet4, bullet5)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type=0):
        super().__init__()
        self.enemy_type = enemy_type
        
        if enemy_type == 0:  # Basic enemy
            self.image = pygame.Surface((40, 40))
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
            
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.direction = 1
        self.drop_distance = 0
        self.shoot_chance = 0.002 * (enemy_type + 1)
    
    def update(self):
        self.rect.x += ENEMY_SPEED * self.direction * (1 + current_level * 0.1)
        
        # Randomly shoot
        if random.random() < self.shoot_chance:
            self.shoot()
    
    def shoot(self):
        enemy_bullet = EnemyBullet(self.rect.centerx, self.rect.bottom)
        all_sprites.add(enemy_bullet)
        enemy_bullets.add(enemy_bullet)
    
    def hit(self):
        self.health -= 1
        return self.health <= 0  # Return True if enemy is destroyed

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speed_x = 0
    
    def update(self):
        self.rect.y -= BULLET_SPEED
        self.rect.x += self.speed_x
        # Remove bullet if it goes off screen
        if self.rect.bottom < 0 or self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((4, 10))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
    
    def update(self):
        self.rect.y += BULLET_SPEED / 2
        # Remove bullet if it goes off screen
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Powerup(pygame.sprite.Sprite):
    def __init__(self, x, y, powerup_type):
        super().__init__()
        self.powerup_type = powerup_type
        self.image = pygame.Surface((20, 20))
        
        # Different powerups
        if powerup_type == 0:  # Extra life
            self.image.fill(GREEN)
        elif powerup_type == 1:  # Shield
            self.image.fill(BLUE)
        elif powerup_type == 2:  # Coin
            self.image.fill(YELLOW)
        
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.centery = y
    
    def update(self):
        self.rect.y += 2
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size))
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
                self.rect = self.image.get_rect()
                self.rect.center = self.rect.center

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

# Create sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Create player
player = Player()
all_sprites.add(player)

# Game state variables
game_state = MENU
current_level = 1
max_level = 10
shop_items = []

# Create enemies
def create_enemies(level):
    # Scale difficulty with level
    rows = min(ENEMY_ROWS + level // 2, 8)
    cols = min(ENEMY_COLS + level // 3, 15)
    
    for row in range(rows):
        for col in range(cols):
            # Determine enemy type based on level and position
            if level >= 8:
                enemy_type = random.choices([0, 1, 2], weights=[0.3, 0.4, 0.3])[0]
            elif level >= 4:
                enemy_type = random.choices([0, 1, 2], weights=[0.5, 0.3, 0.2])[0]
            else:
                enemy_type = random.choices([0, 1], weights=[0.8, 0.2])[0]
                
            # Add more elite enemies in higher rows
            if row < 2 and random.random() < 0.3 * (level / 3):
                enemy_type = min(enemy_type + 1, 2)
                
            enemy = Enemy(col * ENEMY_SPACING + 50, row * ENEMY_SPACING + 50, enemy_type)
            all_sprites.add(enemy)
            enemies.add(enemy)

# Initialize shop items
def initialize_shop():
    global shop_items
    shop_items = [
        ShopItem("Extra Life", "Gain an additional life", 50, lambda player: setattr(player, 'lives', player.lives + 1)),
        ShopItem("Shield", "Temporary invulnerability", 30, lambda player: [setattr(player, 'shield', True), setattr(player, 'shield_time', pygame.time.get_ticks())]),
        ShopItem("Weapon Upgrade", "Increase bullet power", 40, lambda player: setattr(player, 'bullet_power', min(player.bullet_power + 1, 4))),
        ShopItem("Rapid Fire", "Shoot faster", 35, lambda player: setattr(player, 'fire_rate', max(player.fire_rate - 100, 200)))
    ]

initialize_shop()
create_enemies(current_level)

# Game font
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)

# Menu options
menu_options = ["Start Game", "Instructions", "Quit"]
selected_option = 0

# Shop variables
shop_scroll = 0
selected_shop_item = 0

# Game loop
running = True

while running:
    # Keep game running at the right speed
    clock.tick(60)
    
    # Process events
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
            
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
                        # Show instructions here (could be another state)
                        pass
                    elif menu_options[selected_option] == "Quit":
                        running = False
                        
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
                    # Reset game
                    game_state = MENU
                    all_sprites = pygame.sprite.Group()
                    enemies = pygame.sprite.Group()
                    bullets = pygame.sprite.Group()
                    enemy_bullets = pygame.sprite.Group()
                    powerups = pygame.sprite.Group()
                    player = Player()
                    all_sprites.add(player)
                    current_level = 1
                    create_enemies(current_level)
                    
            elif game_state == SHOP:
                if event.key == K_UP:
                    selected_shop_item = (selected_shop_item - 1) % len(shop_items)
                elif event.key == K_DOWN:
                    selected_shop_item = (selected_shop_item + 1) % len(shop_items)
                elif event.key == K_RETURN:
                    # Try to purchase the selected item
                    if shop_items[selected_shop_item].purchase(player):
                        pass  # Purchase successful
                elif event.key == K_ESCAPE or event.key == K_p:
                    game_state = PLAYING
                    
            elif game_state == LEVEL_COMPLETE:
                if event.key == K_n:
                    # Go to next level
                    current_level += 1
                    if current_level > max_level:
                        game_state = GAME_OVER
                    else:
                        create_enemies(current_level)
                        game_state = PLAYING
                elif event.key == K_p:
                    game_state = SHOP
                
        elif event.type == KEYUP:
            if game_state == PLAYING:
                if event.key in (K_LEFT, K_RIGHT):
                    player.speed_x = 0
    
    # Update
    if game_state == PLAYING:
        # Update all sprites
        all_sprites.update()
        
        # Check if enemies need to change direction
        change_direction = False
        for enemy in enemies:
            if enemy.rect.right >= SCREEN_WIDTH or enemy.rect.left <= 0:
                change_direction = True
                break
        
        # Move enemies down and change direction
        if change_direction:
            for enemy in enemies:
                enemy.rect.y += ENEMY_DROP
                enemy.direction *= -1
        
        # Check for bullet collisions with enemies
        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
        for enemy, bullet_list in hits.items():
            if enemy.hit():  # If enemy is destroyed
                # Chance to drop powerup
                if random.random() < enemy.drop_chance:
                    powerup_type = random.randint(0, 2)
                    powerup = Powerup(enemy.rect.centerx, enemy.rect.centery, powerup_type)
                    all_sprites.add(powerup)
                    powerups.add(powerup)
                
                # Add score
                player.score += enemy.points
                player.coins += max(1, enemy.points // 5)
                
                # Create explosion
                explosion = Explosion(enemy.rect.center, 40)
                all_sprites.add(explosion)
                
                # Remove enemy
                enemy.kill()
        
        # Check if player is hit by enemy bullet
        hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
        if hits and not player.shield:
            player.lives -= 1
            if player.lives <= 0:
                game_state = GAME_OVER
        
        # Check for powerup collection
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in hits:
            if powerup.powerup_type == 0:  # Extra life
                player.lives += 1
            elif powerup.powerup_type == 1:  # Shield
                player.shield = True
                player.shield_time = pygame.time.get_ticks()
            elif powerup.powerup_type == 2:  # Coin
                player.coins += 10
        
        # Check if any enemy reached the bottom
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT - 50:
                game_state = GAME_OVER
        
        # Check if all enemies are gone (level complete)
        if len(enemies) == 0:
            game_state = LEVEL_COMPLETE
    
    # Draw everything
    screen.fill(BLACK)
    
    if game_state == MENU:
        # Draw menu
        title = font.render("SPACE INVADERS DELUXE", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        for i, option in enumerate(menu_options):
            color = GREEN if i == selected_option else WHITE
            text = font.render(option, True, color)
            screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 250 + i * 50))
    
    elif game_state in (PLAYING, LEVEL_COMPLETE, GAME_OVER):
        # Draw all sprites
        all_sprites.draw(screen)
        
        # Draw shield if active
        if player.shield:
            pygame.draw.circle(screen, BLUE, player.rect.center, 40, 2)
        
        # Draw HUD
        score_text = font.render(f"Score: {player.score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        
        level_text = font.render(f"Level: {current_level}", True, WHITE)
        screen.blit(level_text, (SCREEN_WIDTH // 2 - level_text.get_width() // 2, 10))
        
        lives_text = font.render(f"Lives: {player.lives}", True, WHITE)
        screen.blit(lives_text, (SCREEN_WIDTH - 150, 10))
        
        coins_text = font.render(f"Coins: {player.coins}", True, YELLOW)
        screen.blit(coins_text, (SCREEN_WIDTH - 150, 40))
        
        # Show weapon level
        weapon_text = small_font.render(f"Weapon Lvl: {player.bullet_power}", True, WHITE)
        screen.blit(weapon_text, (10, 40))
        
        # Show fire rate
        fire_rate_text = small_font.render(f"Fire Rate: {1000 // player.fire_rate}/sec", True, WHITE)
        screen.blit(fire_rate_text, (10, 70))
        
        # Show shop hint
        shop_text = small_font.render("Press P for Shop", True, WHITE)
        screen.blit(shop_text, (SCREEN_WIDTH // 2 - shop_text.get_width() // 2, SCREEN_HEIGHT - 30))
        
        if game_state == LEVEL_COMPLETE:
            # Level complete overlay
            level_complete_text = font.render(f"LEVEL {current_level} COMPLETE!", True, GREEN)
            screen.blit(level_complete_text, (SCREEN_WIDTH // 2 - level_complete_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            next_level_text = font.render("Press N for Next Level or P for Shop", True, WHITE)
            screen.blit(next_level_text, (SCREEN_WIDTH // 2 - next_level_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))
        
        if game_state == GAME_OVER:
            # Game over overlay
            game_over_text = font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            
            if current_level > max_level:
                win_text = font.render("YOU WON! ALL LEVELS COMPLETE!", True, GREEN)
                screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2))
            
            restart_text = font.render("Press R to Restart", True, WHITE)
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
            
            final_score_text = font.render(f"Final Score: {player.score}", True, WHITE)
            screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))
    
    elif game_state == SHOP:
        # Draw shop
        shop_title = font.render("SHOP", True, YELLOW)
        screen.blit(shop_title, (SCREEN_WIDTH // 2 - shop_title.get_width() // 2, 50))
        
        coins_text = font.render(f"Your Coins: {player.coins}", True, YELLOW)
        screen.blit(coins_text, (SCREEN_WIDTH // 2 - coins_text.get_width() // 2, 100))
        
        # Draw shop items
        for i, item in enumerate(shop_items):
            color = GREEN if i == selected_shop_item else WHITE
            item_text = font.render(f"{item.name} - {item.cost} coins", True, color)
            screen.blit(item_text, (SCREEN_WIDTH // 2 - item_text.get_width() // 2, 180 + i * 60))
            
            desc_text = small_font.render(item.description, True, WHITE)
            screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, 180 + i * 60 + 30))
        
        # Draw instructions
        controls_text = small_font.render("UP/DOWN to select, ENTER to buy, ESC or P to return", True, WHITE)
        screen.blit(controls_text, (SCREEN_WIDTH // 2 - controls_text.get_width() // 2, SCREEN_HEIGHT - 50))
    
    # Flip display
    pygame.display.flip()

# Quit the game
pygame.quit()
sys.exit()
