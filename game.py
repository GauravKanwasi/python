import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player
player_width = 50
player_height = 50
player_x = (SCREEN_WIDTH - player_width) // 2
player_y = SCREEN_HEIGHT - player_height - 10
player_speed = 5
player_health = 100
shoot_cooldown = 250  # milliseconds
last_shot_time = 0

# Enemy
enemy_width = 50
enemy_height = 50
enemy_speed = 2
enemy_shoot_chance = 0.01
enemies = []
enemy_bullets = []

# Bullet
bullet_width = 10
bullet_height = 20
bullet_speed = 7
bullets = []

# Power-ups
powerups = []
powerup_types = ["double_shoot", "shield", "one_shot_kill", "chain_reaction"]
powerup_duration = 5000  # 5 seconds

# Game state
score = 0
level = 1
double_shoot = False
shield_active = False
one_shot_kill = False
chain_reaction = False
game_over = False
power_up_end_times = {
    "double_shoot": 0,
    "shield": 0,
    "one_shot_kill": 0,
    "chain_reaction": 0
}

# Clock
clock = pygame.time.Clock()

# Function to draw the player
def draw_player(x, y):
    pygame.draw.rect(screen, GREEN, (x, y, player_width, player_height))

# Function to draw an enemy
def draw_enemy(x, y, img):
    # Use different colors for different enemy types
    color = RED if img == "enemy" else BLUE
    pygame.draw.rect(screen, color, (x, y, enemy_width, enemy_height))

# Function to draw a bullet
def draw_bullet(x, y):
    pygame.draw.rect(screen, WHITE, (x, y, bullet_width, bullet_height))

# Function to draw a power-up
def draw_powerup(x, y, type):
    color = BLUE if type == "shield" else GREEN
    pygame.draw.rect(screen, color, (x, y, 20, 20))

# Function to create enemies
def create_enemies():
    enemies.clear()  # Clear existing enemies first
    for i in range(5):
        enemy_x = random.randint(0, SCREEN_WIDTH - enemy_width)
        enemy_y = random.randint(50, 200)
        enemies.append([enemy_x, enemy_y, random.choice(["enemy", "alien"])])

# Function to create power-ups
def create_powerup():
    powerup_x = random.randint(0, SCREEN_WIDTH - 20)
    powerup_y = random.randint(50, 200)
    powerups.append([powerup_x, powerup_y, random.choice(powerup_types), pygame.time.get_ticks()])

# Function to check collisions
def check_collision(obj1_x, obj1_y, obj1_width, obj1_height, obj2_x, obj2_y, obj2_width, obj2_height):
    return (obj1_x < obj2_x + obj2_width and
            obj1_x + obj1_width > obj2_x and
            obj1_y < obj2_y + obj2_height and
            obj1_y + obj1_height > obj2_y)

# Function to draw enemy bullets
def draw_enemy_bullet(x, y):
    pygame.draw.rect(screen, RED, (x, y, bullet_width, bullet_height))

# Function to reset game
def reset_game():
    global player_x, player_y, player_health, score, enemies, bullets, powerups
    global double_shoot, shield_active, one_shot_kill, chain_reaction, game_over, level
    global enemy_bullets, enemy_speed, enemy_shoot_chance
    
    player_x = (SCREEN_WIDTH - player_width) // 2
    player_y = SCREEN_HEIGHT - player_height - 10
    player_health = 100
    score = 0
    level = 1
    enemies.clear()
    bullets.clear()
    enemy_bullets.clear()
    powerups.clear()
    double_shoot = False
    shield_active = False
    one_shot_kill = False
    chain_reaction = False
    game_over = False
    enemy_speed = 2
    enemy_shoot_chance = 0.01
    create_enemies()

# Create initial enemies
create_enemies()

# Game loop
running = True
while running:
    screen.fill(BLACK)
    current_time = pygame.time.get_ticks()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width:
            player_x += player_speed

        # Shooting with cooldown
        if keys[pygame.K_SPACE] and current_time - last_shot_time >= shoot_cooldown:
            if double_shoot:
                bullets.append([player_x + player_width // 4 - bullet_width // 2, player_y])
                bullets.append([player_x + 3 * player_width // 4 - bullet_width // 2, player_y])
            else:
                bullets.append([player_x + player_width // 2 - bullet_width // 2, player_y])
            last_shot_time = current_time

        # Enemy shooting
        for enemy in enemies:
            if random.random() < enemy_shoot_chance:
                enemy_bullets.append([enemy[0] + enemy_width // 2, enemy[1] + enemy_height])

        # Move enemy bullets
        for bullet in enemy_bullets[:]:
            bullet[1] += bullet_speed
            if bullet[1] > SCREEN_HEIGHT:
                enemy_bullets.remove(bullet)

        # Check for enemy bullet collisions with player
        for bullet in enemy_bullets[:]:
            if check_collision(player_x, player_y, player_width, player_height, 
                             bullet[0], bullet[1], bullet_width, bullet_height):
                enemy_bullets.remove(bullet)
                if not shield_active:
                    player_health -= 10
                    if player_health <= 0:
                        game_over = True

        # Check power-up timers
        for power_up in list(power_up_end_times.keys()):
            if current_time > power_up_end_times[power_up]:
                if power_up == "double_shoot":
                    double_shoot = False
                elif power_up == "shield":
                    shield_active = False
                elif power_up == "one_shot_kill":
                    one_shot_kill = False
                elif power_up == "chain_reaction":
                    chain_reaction = False

        # Level progression
        if len(enemies) == 0:
            level += 1
            enemy_speed = min(2 + level * 0.5, 8)
            enemy_shoot_chance = min(0.01 + level * 0.002, 0.05)
            create_enemies()
            create_powerup()

        # Add bullet movement and collision
        for bullet in bullets[:]:
            bullet[1] -= bullet_speed  # Move bullets upward
            if bullet[1] < 0:  # Remove off-screen bullets
                bullets.remove(bullet)
                continue
                
            # Bullet-enemy collision
            for enemy in enemies[:]:
                if check_collision(enemy[0], enemy[1], enemy_width, enemy_height,
                                 bullet[0], bullet[1], bullet_width, bullet_height):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10
                    if chain_reaction:
                        # Chain reaction implementation
                        for e in enemies[:]:
                            if abs(e[0] - enemy[0]) < 50 and abs(e[1] - enemy[1]) < 50:
                                enemies.remove(e)
                                score += 10
                    break

        # Add power-up collection
        for powerup in powerups[:]:
            if check_collision(player_x, player_y, player_width, player_height,
                             powerup[0], powerup[1], 20, 20):
                power_up_type = powerup[2]
                power_up_end_times[power_up_type] = current_time + powerup_duration
                globals()[power_up_type] = True
                powerups.remove(powerup)

        # Draw everything
        draw_player(player_x, player_y)
        for enemy in enemies:
            draw_enemy(enemy[0], enemy[1], enemy[2])
        for bullet in bullets:
            draw_bullet(bullet[0], bullet[1])
        for bullet in enemy_bullets:
            draw_enemy_bullet(bullet[0], bullet[1])
        for powerup in powerups:
            draw_powerup(powerup[0], powerup[1], powerup[2])

        # Display HUD
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {score}", True, WHITE)
        health_text = font.render(f"Health: {player_health}", True, WHITE)
        level_text = font.render(f"Level: {level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(health_text, (10, 40))
        screen.blit(level_text, (10, 70))

        # Display active power-ups
        power_up_y = 100
        for power_up, end_time in power_up_end_times.items():
            if current_time < end_time:
                remaining_time = (end_time - current_time) / 1000
                power_up_text = font.render(f"{power_up}: {remaining_time:.1f}s", True, GREEN)
                screen.blit(power_up_text, (10, power_up_y))
                power_up_y += 30
    else:
        # Game Over screen
        font = pygame.font.SysFont("Arial", 64)
        game_over_text = font.render("GAME OVER", True, RED)
        score_text = font.render(f"Final Score: {score}", True, WHITE)
        restart_text = font.render("Press R to Restart", True, WHITE)
        
        screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 100))
        screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2))
        screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 100))

    # Update the display
    pygame.display.update()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
