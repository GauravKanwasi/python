import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Enhanced Space Shooter")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Game settings
enemy_speed = 2
enemy_shoot_chance = 0.01
bullet_speed = 7
powerup_duration = 5000  # 5 seconds
powerup_types = ["double_shoot", "shield", "one_shot_kill", "chain_reaction"]

# Game state variables
score = 0
high_score = 0
level = 1
double_shoot = False
shield_active = False
one_shot_kill = False
chain_reaction = False
game_over = False
power_up_end_times = {powerup: 0 for powerup in powerup_types}

# Clock
clock = pygame.time.Clock()

# Starfield background
stars = [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT)) for _ in range(50)]

# Sprite classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.width = 50
        self.height = 50
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, GREEN, (0, 0, self.width, self.height))
        triangle_points = [(self.width // 2, -10), (0, 0), (self.width, 0)]
        pygame.draw.polygon(self.image, GREEN, triangle_points)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - self.height - 10))
        self.speed = 5
        self.health = 100
        self.shoot_cooldown = 250
        self.last_shot_time = 0
        self.invincibility_timer = 0

    def update(self, keys, current_time):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > SCREEN_HEIGHT // 2:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < SCREEN_HEIGHT:
            self.rect.y += self.speed

        if self.invincibility_timer > 0:
            self.image.set_alpha(128 if (current_time // 100) % 2 == 0 else 255)
            self.invincibility_timer -= clock.get_time()
            if self.invincibility_timer <= 0:
                self.image.set_alpha(255)
        else:
            self.image.set_alpha(255)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type, direction, health):
        super().__init__()
        self.width = 50
        self.height = 50
        self.type = type
        self.normal_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        if type == "enemy":
            pygame.draw.rect(self.normal_image, RED, (0, 0, self.width, self.height))
        elif type == "alien":
            pygame.draw.ellipse(self.normal_image, BLUE, (0, 0, self.width, self.height))
        self.hit_image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(self.hit_image, WHITE, (0, 0, self.width, self.height)) if type == "enemy" else pygame.draw.ellipse(self.hit_image, WHITE, (0, 0, self.width, self.height))
        self.image = self.normal_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = direction
        self.health = health
        self.hit_timer = 0

    def update(self):
        self.rect.x += self.direction * enemy_speed
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1
            self.rect.y += 20
        if self.hit_timer > 0:
            self.image = self.hit_image
            self.hit_timer -= clock.get_time()
            if self.hit_timer <= 0:
                self.image = self.normal_image
        else:
            self.image = self.normal_image

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        super().__init__()
        self.width = 10
        self.height = 20
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.line(self.image, WHITE, (self.width // 2, 0), (self.width // 2, self.height), 2)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity_y = -bullet_speed if direction == "up" else bullet_speed

    def update(self):
        self.rect.y += self.velocity_y
        if self.rect.bottom < 0 or self.rect.top > SCREEN_HEIGHT:
            self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 10
        self.height = 10
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(self.image, RED, (self.width // 2, self.height // 2), 5)
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity_y = bullet_speed

    def update(self):
        self.rect.y += self.velocity_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, type):
        super().__init__()
        self.width = 20
        self.height = 20
        self.type = type
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        color = BLUE if type == "shield" else GREEN
        pygame.draw.rect(self.image, color, (0, 0, self.width, self.height))
        self.rect = self.image.get_rect(center=(x, y))
        self.velocity_y = 1  # Fall slowly

    def update(self):
        self.rect.y += self.velocity_y
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = 5
        self.max_radius = 30
        self.grow_speed = 1
        self.lifetime = 500  # milliseconds
        self.start_time = pygame.time.get_ticks()
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(x, y))

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.start_time > self.lifetime:
            self.kill()
        else:
            self.radius += self.grow_speed
            if self.radius > self.max_radius:
                self.radius = self.max_radius
            alpha = int(255 * (1 - (self.radius / self.max_radius)))
            self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 255, 255, alpha), (self.radius, self.radius), self.radius)
            self.rect = self.image.get_rect(center=(self.x, self.y))

# Functions
def create_enemies():
    for _ in range(5):
        enemy_x = random.randint(0, SCREEN_WIDTH - 50)
        enemy_y = random.randint(50, 200)
        type = random.choice(["enemy", "alien"])
        direction = random.choice([-1, 1])
        health = level
        enemy = Enemy(enemy_x, enemy_y, type, direction, health)
        enemies.add(enemy)
        all_sprites.add(enemy)

def create_powerup():
    powerup_x = random.randint(0, SCREEN_WIDTH - 20)
    powerup_y = 0  # Start from top
    type = random.choice(powerup_types)
    powerup = PowerUp(powerup_x, powerup_y, type)
    powerups.add(powerup)
    all_sprites.add(powerup)

def reset_game():
    global score, level, game_over, enemy_speed, enemy_shoot_chance, double_shoot, shield_active, one_shot_kill, chain_reaction, player
    score = 0
    level = 1
    game_over = False
    enemy_speed = 2
    enemy_shoot_chance = 0.01
    double_shoot = False
    shield_active = False
    one_shot_kill = False
    chain_reaction = False
    for power_up in power_up_end_times:
        power_up_end_times[power_up] = 0
    all_sprites.empty()
    enemies.empty()
    player_bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    player = Player()
    all_sprites.add(player)
    create_enemies()

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

# Initial setup
player = Player()
all_sprites.add(player)
create_enemies()

# Game loop
running = True
while running:
    screen.fill(BLACK)
    current_time = pygame.time.get_ticks()

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_r:
                reset_game()

    if not game_over:
        keys = pygame.key.get_pressed()
        player.update(keys, current_time)

        # Player shooting
        if keys[pygame.K_SPACE] and current_time - player.last_shot_time >= player.shoot_cooldown:
            if double_shoot:
                bullet1 = Bullet(player.rect.centerx - 10, player.rect.top, "up")
                bullet2 = Bullet(player.rect.centerx + 10, player.rect.top, "up")
                player_bullets.add(bullet1, bullet2)
                all_sprites.add(bullet1, bullet2)
            else:
                bullet = Bullet(player.rect.centerx, player.rect.top, "up")
                player_bullets.add(bullet)
                all_sprites.add(bullet)
            player.last_shot_time = current_time

        # Update all sprites
        all_sprites.update()

        # Enemy shooting
        for enemy in enemies:
            if random.random() < enemy_shoot_chance:
                bullet = EnemyBullet(enemy.rect.centerx, enemy.rect.bottom)
                enemy_bullets.add(bullet)
                all_sprites.add(bullet)

        # Collisions
        # Player bullets vs enemies
        hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
        for enemy, bullets in hits.items():
            for _ in bullets:
                damage = 100 if one_shot_kill else 1
                enemy.health -= damage
                enemy.hit_timer = 100  # Flash for 100ms
                if enemy.health <= 0:
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(explosion)
                    enemy.kill()
                    score += 10
                    if chain_reaction:
                        for e in enemies:
                            if e != enemy and math.hypot(e.rect.centerx - enemy.rect.centerx, e.rect.centery - enemy.rect.centery) < 50:
                                e.health -= 1
                                if e.health <= 0:
                                    explosion = Explosion(e.rect.centerx, e.rect.centery)
                                    all_sprites.add(explosion)
                                    e.kill()
                                    score += 10

        # Enemy bullets vs player
        if not shield_active and player.invincibility_timer <= 0:
            hits = pygame.sprite.spritecollide(player, enemy_bullets, True)
            for _ in hits:
                player.health -= 10
                player.invincibility_timer = 1000  # 1 second invincibility
                if player.health <= 0:
                    game_over = True

        # Player vs power-ups
        hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in hits:
            power_up_type = powerup.type
            power_up_end_times[power_up_type] = current_time + powerup_duration
            globals()[power_up_type] = True

        # Check if enemies reach bottom
        for enemy in enemies:
            if enemy.rect.bottom >= SCREEN_HEIGHT:
                game_over = True
                break

        # Level progression
        if not enemies:
            level += 1
            enemy_speed = min(2 + level * 0.5, 8)
            enemy_shoot_chance = min(0.01 + level * 0.002, 0.05)
            create_enemies()
            create_powerup()
            player.health = min(player.health + 20, 100)

        # Draw starfield
        for star in stars:
            pygame.draw.circle(screen, WHITE, star, 1)
        stars = [(x, y + 1) if y < SCREEN_HEIGHT else (x, 0) for x, y in stars]

        # Draw sprites
        all_sprites.draw(screen)

        # HUD
        font = pygame.font.SysFont("Arial", 24)
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Health: {player.health}", True, WHITE), (10, 40))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 70))

        # Active power-ups
        power_up_y = 100
        for power_up, end_time in power_up_end_times.items():
            if current_time < end_time:
                remaining_time = (end_time - current_time) / 1000
                screen.blit(font.render(f"{power_up}: {remaining_time:.1f}s", True, GREEN), (10, power_up_y))
                power_up_y += 30
            elif globals()[power_up]:
                globals()[power_up] = False

    else:
        # Game Over screen
        if score > high_score:
            high_score = score
        font = pygame.font.SysFont("Arial", 64)
        screen.blit(font.render("GAME OVER", True, RED), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 150))
        screen.blit(font.render(f"Final Score: {score}", True, WHITE), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))
        screen.blit(font.render(f"High Score: {high_score}", True, WHITE), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50))
        screen.blit(font.render("Press R to Restart", True, WHITE), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 150))

    # Update display
    pygame.display.update()
    clock.tick(60)

pygame.quit()
