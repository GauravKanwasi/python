import pygame
import random
import math
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Python Car Racing Game")

# Colors
SKY_BLUE = (135, 206, 235)
ROAD_GRAY = (50, 50, 50)
ROAD_LINE = (255, 255, 255)
GRASS_GREEN = (34, 139, 34)
RED = (255, 0, 0)
BLUE = (30, 144, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
DARK_GREEN = (0, 100, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (40, 40, 40)
LIGHT_BLUE = (173, 216, 230)
GOLD = (255, 215, 0)

# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
game_speed = 5
high_score = 0

# Font
font_small = pygame.font.SysFont("Arial", 24)
font_medium = pygame.font.SysFont("Arial", 32)
font_large = pygame.font.SysFont("Arial", 48)
font_xlarge = pygame.font.SysFont("Arial", 72, bold=True)

class PlayerCar:
    def __init__(self):
        self.width = 40
        self.height = 70
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 8
        self.color = RED
        self.draw_car()
        self.trail = []
        self.max_trail_length = 15
        
    def draw_car(self):
        # Create surface for the car
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Car body with gradient effect
        pygame.draw.rect(self.surface, self.color, (0, 0, self.width, self.height), border_radius=10)
        pygame.draw.rect(self.surface, (200, 0, 0), (2, 2, self.width-4, self.height-4), border_radius=8, width=2)
        
        # Headlights
        pygame.draw.circle(self.surface, YELLOW, (8, 5), 4)
        pygame.draw.circle(self.surface, YELLOW, (self.width-8, 5), 4)
        
        # Car details
        pygame.draw.rect(self.surface, (30, 30, 30), (5, 5, self.width-10, 15), border_radius=5)  # windshield
        pygame.draw.rect(self.surface, (30, 30, 30), (5, self.height-20, self.width-10, 15), border_radius=5)  # rear
        
        # Windows
        pygame.draw.rect(self.surface, BLUE, (8, 8, self.width-16, 10), border_radius=3)
        pygame.draw.rect(self.surface, BLUE, (8, self.height-17, self.width-16, 10), border_radius=3)
        
        # Wheels with shine effect
        pygame.draw.rect(self.surface, BLACK, (2, 15, 8, 15), border_radius=4)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, 15, 8, 15), border_radius=4)
        pygame.draw.rect(self.surface, BLACK, (2, self.height-30, 8, 15), border_radius=4)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, self.height-30, 8, 15), border_radius=4)
        
        # Wheel details
        pygame.draw.circle(self.surface, GRAY, (6, 22), 3)
        pygame.draw.circle(self.surface, GRAY, (self.width-6, 22), 3)
        pygame.draw.circle(self.surface, GRAY, (6, self.height-23), 3)
        pygame.draw.circle(self.surface, GRAY, (self.width-6, self.height-23), 3)
        
    def move(self, direction):
        if direction == "left" and self.x > WIDTH//3 + 10:
            self.x -= self.speed
            # Add to trail
            self.trail.append((self.x + self.width//2, self.y + self.height))
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)
        if direction == "right" and self.x < WIDTH*2//3 - self.width - 10:
            self.x += self.speed
            # Add to trail
            self.trail.append((self.x + self.width//2, self.y + self.height))
            if len(self.trail) > self.max_trail_length:
                self.trail.pop(0)
            
    def draw(self, screen):
        # Draw trail with smooth fade
        for i, pos in enumerate(self.trail):
            alpha = int(200 * (i / len(self.trail)))
            size = max(1, int(4 * (i / len(self.trail))))
            if size > 0:
                s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*RED[:3], alpha), (size, size), size)
                screen.blit(s, (pos[0]-size, pos[1]-size))
                
        screen.blit(self.surface, (self.x, self.y))

class EnemyCar:
    def __init__(self):
        self.width = 40
        self.height = 70
        self.x = random.randint(WIDTH//3 + 20, WIDTH*2//3 - self.width - 20)
        self.y = -self.height
        self.speed = random.randint(4, 8)
        self.color = self.get_random_color()
        self.draw_car()
        self.wobble = 0
        self.wobble_direction = random.choice([-1, 1])
        self.blink_timer = 0
        self.headlight_on = True
        
    def get_random_color(self):
        colors = [
            (0, 200, 0),    # Green
            (255, 140, 0),  # Orange
            (138, 43, 226), # Purple
            (0, 206, 209),  # Cyan
            (255, 105, 180) # Pink
        ]
        return random.choice(colors)
        
    def draw_car(self):
        # Create surface for the car
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Car body with gradient effect
        pygame.draw.rect(self.surface, self.color, (0, 0, self.width, self.height), border_radius=10)
        darker_color = tuple(max(0, c-40) for c in self.color)
        pygame.draw.rect(self.surface, darker_color, (2, 2, self.width-4, self.height-4), border_radius=8, width=2)
        
        # Headlights (blinking effect)
        headlight_color = YELLOW if self.headlight_on else (100, 100, 0)
        pygame.draw.circle(self.surface, headlight_color, (8, self.height-5), 4)
        pygame.draw.circle(self.surface, headlight_color, (self.width-8, self.height-5), 4)
        
        # Car details
        pygame.draw.rect(self.surface, (30, 30, 30), (5, 5, self.width-10, 15), border_radius=5)  # windshield
        pygame.draw.rect(self.surface, (30, 30, 30), (5, self.height-20, self.width-10, 15), border_radius=5)  # rear
        
        # Windows
        pygame.draw.rect(self.surface, (173, 216, 230), (8, 8, self.width-16, 10), border_radius=3)
        pygame.draw.rect(self.surface, (173, 216, 230), (8, self.height-17, self.width-16, 10), border_radius=3)
        
        # Wheels with shine effect
        pygame.draw.rect(self.surface, BLACK, (2, 15, 8, 15), border_radius=4)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, 15, 8, 15), border_radius=4)
        pygame.draw.rect(self.surface, BLACK, (2, self.height-30, 8, 15), border_radius=4)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, self.height-30, 8, 15), border_radius=4)
        
        # Wheel details
        pygame.draw.circle(self.surface, GRAY, (6, 22), 3)
        pygame.draw.circle(self.surface, GRAY, (self.width-6, 22), 3)
        pygame.draw.circle(self.surface, GRAY, (6, self.height-23), 3)
        pygame.draw.circle(self.surface, GRAY, (self.width-6, self.height-23), 3)
        
    def move(self):
        self.y += self.speed
        # Add slight wobble effect
        self.wobble += 0.05
        if self.wobble > math.pi:
            self.wobble_direction *= -1
            self.wobble = 0
        self.x += math.sin(self.wobble) * self.wobble_direction * 0.8
        
        # Blinking headlights
        self.blink_timer += 1
        if self.blink_timer >= 30:
            self.blink_timer = 0
            self.headlight_on = not self.headlight_on
            self.draw_car()
        
    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))
        
    def is_off_screen(self):
        return self.y > HEIGHT

class Road:
    def __init__(self):
        self.line_height = 30
        self.line_width = 12
        self.line_gap = 30
        self.lines = []
        for i in range(HEIGHT // (self.line_height + self.line_gap) + 1):
            self.lines.append(i * (self.line_height + self.line_gap))
        self.side_lines = []
        for i in range(HEIGHT // 20 + 1):
            self.side_lines.append(i * 20)
        self.road_texture_offset = 0
    
    def update(self):
        self.road_texture_offset = (self.road_texture_offset + game_speed) % 20
        for i in range(len(self.lines)):
            self.lines[i] += game_speed
            if self.lines[i] > HEIGHT:
                self.lines[i] = -self.line_height
                
        for i in range(len(self.side_lines)):
            self.side_lines[i] += game_speed
            if self.side_lines[i] > HEIGHT:
                self.side_lines[i] = -20
    
    def draw(self, screen):
        # Draw grass with texture
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(screen, DARK_GREEN, (0, y), (WIDTH//3, y), 1)
            pygame.draw.line(screen, DARK_GREEN, (WIDTH*2//3, y), (WIDTH, y), 1)
            # Add some variation
            if random.randint(0, 5) == 0:
                pygame.draw.line(screen, (25, 120, 25), (random.randint(0, WIDTH//3-10), y), 
                                (random.randint(0, WIDTH//3-10), y+5), 2)
                pygame.draw.line(screen, (25, 120, 25), (random.randint(WIDTH*2//3+10, WIDTH-10), y), 
                                (random.randint(WIDTH*2//3+10, WIDTH-10), y+5), 2)
        
        # Draw road with texture
        road_rect = pygame.Rect(WIDTH//3, 0, WIDTH//3, HEIGHT)
        pygame.draw.rect(screen, ROAD_GRAY, road_rect)
        
        # Add road texture
        for y in range(0, HEIGHT, 20):
            pygame.draw.line(screen, DARK_GRAY, (WIDTH//3+10, y+self.road_texture_offset), 
                            (WIDTH*2//3-10, y+self.road_texture_offset), 1)
        
        # Draw side borders
        pygame.draw.rect(screen, WHITE, (WIDTH//3-5, 0, 5, HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH*2//3, 0, 5, HEIGHT))
        
        # Draw road lines
        for line_y in self.lines:
            pygame.draw.rect(screen, ROAD_LINE, 
                            (WIDTH//2 - self.line_width//2, line_y, self.line_width, self.line_height), border_radius=3)
        
        # Draw side lines
        for line_y in self.side_lines:
            pygame.draw.rect(screen, YELLOW, (WIDTH//3+5, line_y, 3, 12), border_radius=1)
            pygame.draw.rect(screen, YELLOW, (WIDTH*2//3-8, line_y, 3, 12), border_radius=1)

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 6)
        self.speed_x = random.uniform(-4, 4)
        self.speed_y = random.uniform(-4, 4)
        self.life = random.randint(30, 50)
        self.gravity = 0.1
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.speed_y += self.gravity
        self.life -= 1
        self.size = max(0, self.size - 0.05)
        return self.life > 0
        
    def draw(self, screen):
        alpha = min(255, self.life * 5)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*self.color[:3], alpha), (self.size, self.size), self.size)
        screen.blit(s, (self.x-self.size, self.y-self.size))

class Cloud:
    def __init__(self):
        self.x = random.randint(-100, WIDTH+100)
        self.y = random.randint(20, 150)
        self.speed = random.uniform(0.5, 1.5)
        self.size = random.randint(30, 60)
        
    def update(self):
        self.x += self.speed
        if self.x > WIDTH + 100:
            self.x = -100
            self.y = random.randint(20, 150)
            
    def draw(self, screen):
        # Draw fluffy cloud
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, WHITE, (int(self.x+self.size*0.7), int(self.y-self.size*0.3)), int(self.size*0.8))
        pygame.draw.circle(screen, WHITE, (int(self.x+self.size*0.7), int(self.y+self.size*0.3)), int(self.size*0.8))
        pygame.draw.circle(screen, WHITE, (int(self.x+self.size*1.4), int(self.y)), int(self.size*0.9))

def draw_environment(screen):
    # Draw sky with smooth gradient
    for y in range(0, HEIGHT, 2):
        # Create a smooth gradient from light blue to darker blue
        ratio = y / HEIGHT
        r = int(135 + (100 * (1 - ratio)))
        g = int(206 + (20 * (1 - ratio)))
        b = int(235 - (50 * ratio))
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
    
    # Draw sun with glow
    sun_pos = (700, 80)
    pygame.draw.circle(screen, YELLOW, sun_pos, 50)
    
    # Sun glow effect
    for i in range(5):
        alpha = 80 - i*15
        size = 60 + i*10
        s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*YELLOW[:3], alpha), (size, size), size)
        screen.blit(s, (sun_pos[0]-size, sun_pos[1]-size))

def create_explosion(x, y, color):
    particles = []
    for _ in range(70):
        particles.append(Particle(x, y, color))
    return particles

def draw_hud(screen, score, high_score, game_speed):
    # Draw semi-transparent HUD background
    hud_surface = pygame.Surface((WIDTH, 40), pygame.SRCALPHA)
    hud_surface.fill((0, 0, 0, 150))
    screen.blit(hud_surface, (0, 10))
    
    # Draw score
    score_text = font_medium.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (20, 20))
    
    # Draw high score
    high_score_text = font_medium.render(f"High Score: {high_score}", True, GOLD)
    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, 20))
    
    # Draw speed
    speed_text = font_medium.render(f"Speed: {game_speed:.1f}", True, LIGHT_BLUE)
    screen.blit(speed_text, (WIDTH - speed_text.get_width() - 20, 20))

def draw_controls_hint(screen):
    controls_text = font_small.render("← → Arrow Keys to Move", True, WHITE)
    screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, HEIGHT - 40))

def draw_game_over(screen, score, high_score):
    # Dark overlay
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))
    
    # Game over title
    game_over_text = font_xlarge.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 120))
    
    # Score display
    score_text = font_large.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 40))
    
    # High score display
    high_score_text = font_large.render(f"High Score: {high_score}", True, GOLD)
    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 10))
    
    # Restart instructions
    restart_text = font_medium.render("Press 'R' to Restart", True, LIGHT_BLUE)
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 80))
    
    # Quit instructions
    quit_text = font_medium.render("Press ESC to Quit", True, WHITE)
    screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 130))

def main():
    global score, game_speed, high_score
    
    player = PlayerCar()
    road = Road()
    enemies = []
    enemy_spawn_timer = 0
    enemy_spawn_delay = 60  # frames
    particles = []
    clouds = [Cloud() for _ in range(5)]
    
    running = True
    game_over = False
    
    while running:
        dt = clock.tick(FPS)
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and game_over:
                    # Reset game
                    player = PlayerCar()
                    road = Road()
                    enemies = []
                    particles = []
                    score = 0
                    game_speed = 5
                    game_over = False
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        if not game_over:
            # Player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                player.move("left")
            if keys[pygame.K_RIGHT]:
                player.move("right")
            
            # Spawn enemies
            enemy_spawn_timer += 1
            if enemy_spawn_timer >= enemy_spawn_delay:
                enemies.append(EnemyCar())
                enemy_spawn_timer = 0
                # Increase difficulty over time
                if enemy_spawn_delay > 20:
                    enemy_spawn_delay -= 0.05
            
            # Update enemies
            for enemy in enemies[:]:
                enemy.move()
                if enemy.is_off_screen():
                    enemies.remove(enemy)
                    score += 1
                    # Increase game speed gradually
                    if game_speed < 15:
                        game_speed += 0.015
            
            # Update particles
            for particle in particles[:]:
                if not particle.update():
                    particles.remove(particle)
            
            # Update clouds
            for cloud in clouds:
                cloud.update()
            
            # Check collisions
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            for enemy in enemies[:]:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if player_rect.colliderect(enemy_rect):
                    # Create explosion
                    particles.extend(create_explosion(
                        enemy.x + enemy.width//2, 
                        enemy.y + enemy.height//2, 
                        enemy.color
                    ))
                    enemies.remove(enemy)
                    game_over = True
                    if score > high_score:
                        high_score = score
            
            # Update road
            road.update()
        
        # Drawing
        draw_environment(screen)
        
        # Draw clouds
        for cloud in clouds:
            cloud.draw(screen)
        
        road.draw(screen)
        player.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
            
        for particle in particles:
            particle.draw(screen)
        
        # Draw HUD
        draw_hud(screen, score, high_score, game_speed)
        draw_controls_hint(screen)
        
        # Draw game over screen
        if game_over:
            draw_game_over(screen, score, high_score)
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
