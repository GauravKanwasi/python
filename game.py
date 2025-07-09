import pygame
import random
import math  # Required for particle explosions

# Initialize Pygame and mixer for sound
pygame.init()
pygame.mixer.init()

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
lives = 3  # New lives system
game_over = False
paused = False  # Pause menu flag

# Load sounds (ensure files exist in the same directory)
try:
    shoot_sound = pygame.mixer.Sound("laser.wav")
    explosion_sound = pygame.mixer.Sound("explosion.wav")
    powerup_sound = pygame.mixer.Sound("powerup.wav")
    background_music = pygame.mixer.Sound("background.mp3")
    background_music.play(-1)  # Loop background music
except FileNotFoundError:
    print("Warning: Sound files not found. Place laser.wav, explosion.wav, powerup.wav, and background.mp3 in the directory.")

# Starfield layers for parallax [[9]](https://github.com/pygame/pygame-starfield )
stars = [
    [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(0.5, 2)) for _ in range(50)],
    [(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT), random.uniform(0.5, 2)) for _ in range(50)]
]

# Sprite classes
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        pygame.draw.polygon(self.image, GREEN, [(25, 0), (0, 50), (50, 50)])
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT-50))
        self.speed = 5
        self.shoot_cooldown = 250
        self.last_shot_time = 0
        self.invincibility_timer = 0
        self.lives = 3  # Track lives

    def update(self, keys, current_time):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed
        if self.invincibility_timer > 0:
            self.image.set_alpha(128 if (current_time // 100) % 2 == 0 else 255)
            self.invincibility_timer -= clock.get_time()
            if self.invincibility_timer <= 0:
                self.image.set_alpha(255)

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, type, direction, health):
        super().__init__()
        self.type = type
        self.health = health
        self.image = pygame.Surface((50, 50), pygame.SRCALPHA)
        if type == "boss":
            pygame.draw.rect(self.image, (255, 165, 0), (0, 0, 50, 50))  # Boss color
        else:
            pygame.draw.rect(self.image, RED if type == "enemy" else BLUE, (0, 0, 50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = direction

    def update(self):
        self.rect.x += self.direction * enemy_speed
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.direction *= -1
            self.rect.y += 20

class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.particles = []
        for _ in range(20):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            self.particles.append([x, y, math.cos(angle)*speed, math.sin(angle)*speed, 10])
    
    def update(self):
        new_particles = []
        for p in self.particles:
            p[0] += p[2]  # x
            p[1] += p[3]  # y
            p[4] -= 1     # lifespan
            if p[4] > 0:
                new_particles.append(p)
        self.particles = new_particles
    
    def draw(self, surface):
        for p in self.particles:
            pygame.draw.circle(surface, WHITE, (int(p[0]), int(p[1])), 2)

# Functions
def create_enemies():
    global level
    if level % 5 == 0:  # Boss every 5 levels
        boss = Enemy(SCREEN_WIDTH//2 - 25, 50, "boss", 1, level*2)
        enemies.add(boss)
        all_sprites.add(boss)
    else:
        for _ in range(5 + level):
            type = random.choice(["enemy", "alien"])
            enemy = Enemy(random.randint(0, SCREEN_WIDTH-50), random.randint(50, 200), type, random.choice([-1, 1]), level)
            enemies.add(enemy)
            all_sprites.add(enemy)

def reset_game():
    global score, level, game_over, lives
    score = 0
    level = 1
    lives = 3
    game_over = False
    all_sprites.empty()
    enemies.empty()
    player_bullets.empty()
    enemy_bullets.empty()
    powerups.empty()
    player = Player()
    all_sprites.add(player)
    create_enemies()

# Load high score
try:
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
except FileNotFoundError:
    high_score = 0

# Sprite groups
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player_bullets = pygame.sprite.Group()
enemy_bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
create_enemies()

# Game loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(BLACK)
    current_time = pygame.time.get_ticks()

    # Parallax starfield
    for layer in stars:
        for i, (x, y, speed) in enumerate(layer):
            pygame.draw.circle(screen, WHITE, (x, y), 1)
            layer[i] = (x, (y + speed) % SCREEN_HEIGHT, speed)

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                paused = not paused  # Toggle pause
            if game_over and event.key == pygame.K_r:
                reset_game()

    if paused:
        font = pygame.font.SysFont("Arial", 64)
        screen.blit(font.render("PAUSED", True, WHITE), (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2))
        pygame.display.update()
        continue

    if not game_over:
        keys = pygame.key.get_pressed()
        player.update(keys, current_time)

        # Player shooting
        if keys[pygame.K_SPACE] and current_time - player.last_shot_time >= player.shoot_cooldown:
            shoot_sound.play()  # Play gunfire sound
            bullet = Bullet(player.rect.centerx, player.rect.top, "up")
            player_bullets.add(bullet)
            all_sprites.add(bullet)
            player.last_shot_time = current_time

        # Update sprites
        all_sprites.update()

        # Collisions
        hits = pygame.sprite.groupcollide(enemies, player_bullets, False, True)
        for enemy, bullets in hits.items():
            for _ in bullets:
                enemy.health -= 1
                if enemy.health <= 0:
                    explosion_sound.play()  # Play explosion sound
                    explosion = Explosion(enemy.rect.centerx, enemy.rect.centery)
                    all_sprites.add(explosion)
                    enemy.kill()
                    score += 10

        # Level progression
        if not enemies:
            level += 1
            create_enemies()

        # Draw sprites
        all_sprites.draw(screen)

        # HUD
        font = pygame.font.SysFont("Arial", 24)
        screen.blit(font.render(f"Score: {score}", True, WHITE), (10, 10))
        screen.blit(font.render(f"Level: {level}", True, WHITE), (10, 40))
        screen.blit(font.render(f"Lives: {player.lives}", True, WHITE), (10, 70))

    else:
        # Game Over screen
        if score > high_score:
            high_score = score
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))
        font = pygame.font.SysFont("Arial", 64)
        screen.blit(font.render("GAME OVER", True, RED), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 150))
        screen.blit(font.render(f"Final Score: {score}", True, WHITE), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 - 50))
        screen.blit(font.render(f"High Score: {high_score}", True, WHITE), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 50))
        screen.blit(font.render("Press R to Restart", True, WHITE), (SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2 + 150))

    pygame.display.update()
    clock.tick(60)

pygame.quit()
