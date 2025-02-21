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

# Load images
player_img = pygame.image.load("player.png")
enemy_img = pygame.image.load("enemy.png")
alien_img = pygame.image.load("alien.png")
bullet_img = pygame.image.load("bullet.png")
explosion_img = pygame.image.load("explosion.png")

# Player
player_width = 50
player_height = 50
player_x = (SCREEN_WIDTH - player_width) // 2
player_y = SCREEN_HEIGHT - player_height - 10
player_speed = 5

# Enemy
enemy_width = 50
enemy_height = 50
enemy_speed = 2
enemies = []

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
double_shoot = False
shield_active = False
one_shot_kill = False
chain_reaction = False
game_over = False

# Clock
clock = pygame.time.Clock()

# Function to draw the player
def draw_player(x, y):
    screen.blit(player_img, (x, y))

# Function to draw an enemy
def draw_enemy(x, y, img):
    screen.blit(img, (x, y))

# Function to draw a bullet
def draw_bullet(x, y):
    screen.blit(bullet_img, (x, y))

# Function to draw a power-up
def draw_powerup(x, y, type):
    color = BLUE if type == "shield" else GREEN
    pygame.draw.rect(screen, color, (x, y, 20, 20))

# Function to create enemies
def create_enemies():
    for i in range(5):
        enemy_x = random.randint(0, SCREEN_WIDTH - enemy_width)
        enemy_y = random.randint(50, 200)
        enemies.append([enemy_x, enemy_y, random.choice([enemy_img, alien_img])])

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

# Create initial enemies
create_enemies()

# Game loop
running = True
while running:
    screen.fill(BLACK)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        # Player movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < SCREEN_WIDTH - player_width:
            player_x += player_speed

        # Shooting
        if keys[pygame.K_SPACE]:
            if double_shoot:
                bullets.append([player_x + player_width // 4 - bullet_width // 2, player_y])
                bullets.append([player_x + 3 * player_width // 4 - bullet_width // 2, player_y])
            else:
                bullets.append([player_x + player_width // 2 - bullet_width // 2, player_y])

        # Move bullets
        for bullet in bullets:
            bullet[1] -= bullet_speed
            if bullet[1] < 0:
                bullets.remove(bullet)

        # Move enemies
        for enemy in enemies:
            enemy[0] += enemy_speed
            if enemy[0] <= 0 or enemy[0] >= SCREEN_WIDTH - enemy_width:
                enemy_speed *= -1
                for e in enemies:
                    e[1] += 20

        # Check for collisions
        for bullet in bullets:
            for enemy in enemies:
                if check_collision(bullet[0], bullet[1], bullet_width, bullet_height, enemy[0], enemy[1], enemy_width, enemy_height):
                    bullets.remove(bullet)
                    enemies.remove(enemy)
                    score += 10
                    if chain_reaction:
                        for e in enemies[:]:
                            if math.hypot(e[0] - enemy[0], e[1] - enemy[1]) < 100:
                                enemies.remove(e)
                                score += 10
                    break

        # Check for power-up collisions
        for powerup in powerups[:]:
            if check_collision(player_x, player_y, player_width, player_height, powerup[0], powerup[1], 20, 20):
                if powerup[2] == "double_shoot":
                    double_shoot = True
                elif powerup[2] == "shield":
                    shield_active = True
                elif powerup[2] == "one_shot_kill":
                    one_shot_kill = True
                elif powerup[2] == "chain_reaction":
                    chain_reaction = True
                powerups.remove(powerup)

        # Draw everything
        draw_player(player_x, player_y)
        for enemy in enemies:
            draw_enemy(enemy[0], enemy[1], enemy[2])
        for bullet in bullets:
            draw_bullet(bullet[0], bullet[1])
        for powerup in powerups:
            draw_powerup(powerup[0], powerup[1], powerup[2])

        # Display score
        font = pygame.font.SysFont("Arial", 24)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # Update the display
        pygame.display.update()

        # Cap the frame rate
        clock.tick(60)

# Quit Pygame
pygame.quit()
