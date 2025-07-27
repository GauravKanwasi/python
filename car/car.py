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
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
DARK_GREEN = (0, 100, 0)
BROWN = (139, 69, 19)

# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
game_speed = 5
high_score = 0

# Font
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

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
        self.max_trail_length = 10
        
    def draw_car(self):
        # Create surface for the car
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Car body with gradient effect
        pygame.draw.rect(self.surface, self.color, (0, 0, self.width, self.height), border_radius=8)
        pygame.draw.rect(self.surface, (200, 0, 0), (2, 2, self.width-4, self.height-4), border_radius=6, width=2)
        
        # Car details
        pygame.draw.rect(self.surface, BLACK, (5, 5, self.width-10, 15), border_radius=3)  # windshield
        pygame.draw.rect(self.surface, BLACK, (5, self.height-20, self.width-10, 15), border_radius=3)  # rear
        
        # Windows
        pygame.draw.rect(self.surface, BLUE, (8, 8, self.width-16, 10), border_radius=2)
        pygame.draw.rect(self.surface, BLUE, (8, self.height-17, self.width-16, 10), border_radius=2)
        
        # Wheels with shine effect
        pygame.draw.rect(self.surface, BLACK, (2, 15, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, 15, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (2, self.height-30, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, self.height-30, 8, 15), border_radius=3)
        
        # Wheel details
        pygame.draw.circle(self.surface, GRAY if 'GRAY' in globals() else (128, 128, 128), (6, 22), 2)
        pygame.draw.circle(self.surface, GRAY if 'GRAY' in globals() else (128, 128, 128), (self.width-6, 22), 2)
        pygame.draw.circle(self.surface, GRAY if 'GRAY' in globals() else (128, 128, 128), (6, self.height-23), 2)
        pygame.draw.circle(self.surface, GRAY if 'GRAY' in globals() else (128, 128, 128), (self.width-6, self.height-23), 2)
        
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
        # Draw trail
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            size = int(5 * (i / len(self.trail)))
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
        
    def get_random_color(self):
        colors = [
            (0, 255, 0),    # Green
            (255, 165, 0),  # Orange
            (128, 0, 128),  # Purple
            (0, 255, 255),  # Cyan
            (255, 192, 203) # Pink
        ]
        return random.choice(colors)
        
    def draw_car(self):
        # Create surface for the car
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Car body with gradient effect
        pygame.draw.rect(self.surface, self.color, (0, 0, self.width, self.height), border_radius=8)
        pygame.draw.rect(self.surface, tuple(max(0, c-50) for c in self.color), (2, 2, self.width-4, self.height-4), border_radius=6, width=2)
        
        # Car details
        pygame.draw.rect(self.surface, BLACK, (5, 5, self.width-10, 15), border_radius=3)  # windshield
        pygame.draw.rect(self.surface, BLACK, (5, self.height-20, self.width-10, 15), border_radius=3)  # rear
        
        # Windows
        pygame.draw.rect(self.surface, YELLOW, (8, 8, self.width-16, 10), border_radius=2)
        pygame.draw.rect(self.surface, YELLOW, (8, self.height-17, self.width-16, 10), border_radius=2)
        
        # Wheels with shine effect
        pygame.draw.rect(self.surface, BLACK, (2, 15, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, 15, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (2, self.height-30, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, self.height-30, 8, 15), border_radius=3)
        
        # Wheel details
        pygame.draw.circle(self.surface, GRAY if 'GRAY' in globals() else (128, 128, 128), (6, 22), 2)
        pygame.draw.circle(self.surface, GRAY if 'GRAY' in globals() else (128, 128, 128), (self.width-6, 22), 2)
        pygame.draw.circle(self.surface, GRAY if 'GRAY' in globals() else (128, 128, 128), (6, self.height-23), 2)
        pygame.draw.circle(self.surface, GRAY if 'GRAY' in globals() else (128, 128, 128), (self.width-6, self.height-23), 2)
        
    def move(self):
        self.y += self.speed
        # Add slight wobble effect
        self.wobble += 0.1
        if self.wobble > 1:
            self.wobble_direction *= -1
            self.wobble = 0
        self.x += math.sin(self.wobble) * self.wobble_direction * 0.5
        
    def draw(self, screen):
        screen.blit(self.surface, (self.x, self.y))
        
    def is_off_screen(self):
        return self.y > HEIGHT

class Road:
    def __init__(self):
        self.line_height = 30
        self.line_width = 10
        self.line_gap = 30
        self.lines = []
        for i in range(HEIGHT // (self.line_height + self.line_gap) + 1):
            self.lines.append(i * (self.line_height + self.line_gap))
        self.side_lines = []
        for i in range(HEIGHT // 20 + 1):
            self.side_lines.append(i * 20)
    
    def update(self):
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
        
        # Draw road
        pygame.draw.rect(screen, ROAD_GRAY, (WIDTH//3, 0, WIDTH//3, HEIGHT))
        
        # Draw side borders
        pygame.draw.rect(screen, WHITE, (WIDTH//3-5, 0, 5, HEIGHT))
        pygame.draw.rect(screen, WHITE, (WIDTH*2//3, 0, 5, HEIGHT))
        
        # Draw road lines
        for line_y in self.lines:
            pygame.draw.rect(screen, ROAD_LINE, 
                            (WIDTH//2 - self.line_width//2, line_y, self.line_width, self.line_height))
        
        # Draw side lines
        for line_y in self.side_lines:
            pygame.draw.rect(screen, YELLOW, (WIDTH//3+5, line_y, 3, 10))
            pygame.draw.rect(screen, YELLOW, (WIDTH*2//3-8, line_y, 3, 10))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(2, 5)
        self.speed_x = random.uniform(-3, 3)
        self.speed_y = random.uniform(-3, 3)
        self.life = random.randint(20, 40)
        
    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.life -= 1
        self.size = max(0, self.size - 0.1)
        return self.life > 0
        
    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

def draw_environment(screen):
    # Draw sky with gradient
    for y in range(HEIGHT):
        # Create a gradient from light blue to darker blue
        color_value = max(100, 235 - (y // 3))
        pygame.draw.line(screen, (135, color_value, 235), (0, y), (WIDTH, y))
    
    # Draw sun with glow
    pygame.draw.circle(screen, YELLOW, (700, 80), 50)
    for i in range(5):
        s = pygame.Surface((120 + i*20, 120 + i*20), pygame.SRCALPHA)
        pygame.draw.circle(s, (*YELLOW[:3], 50 - i*10), (60 + i*10, 60 + i*10), 60 + i*10)
        screen.blit(s, (640 - i*10, 20 - i*10))
    
    # Draw clouds
    for i in range(3):
        x = 100 + i * 200
        y = 50 + i * 30
        pygame.draw.circle(screen, WHITE, (x, y), 20)
        pygame.draw.circle(screen, WHITE, (x+15, y-10), 25)
        pygame.draw.circle(screen, WHITE, (x+30, y), 20)
        pygame.draw.circle(screen, WHITE, (x+15, y+10), 20)

def create_explosion(x, y, color):
    particles = []
    for _ in range(50):
        particles.append(Particle(x, y, color))
    return particles

def main():
    global score, game_speed, high_score
    
    player = PlayerCar()
    road = Road()
    enemies = []
    enemy_spawn_timer = 0
    enemy_spawn_delay = 60  # frames
    particles = []
    
    running = True
    game_over = False
    
    while running:
        clock.tick(FPS)
        
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
                    enemy_spawn_delay -= 0.1
            
            # Update enemies
            for enemy in enemies[:]:
                enemy.move()
                if enemy.is_off_screen():
                    enemies.remove(enemy)
                    score += 1
                    # Increase game speed gradually
                    if game_speed < 15:
                        game_speed += 0.02
            
            # Update particles
            for particle in particles[:]:
                if not particle.update():
                    particles.remove(particle)
            
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
        road.draw(screen)
        player.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
            
        for particle in particles:
            particle.draw(screen)
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # Draw high score
        high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
        screen.blit(high_score_text, (20, 60))
        
        # Draw speed
        speed_text = font.render(f"Speed: {game_speed:.1f}", True, WHITE)
        screen.blit(speed_text, (WIDTH - speed_text.get_width() - 20, 20))
        
        # Draw controls hint
        controls_text = font.render("Use LEFT/RIGHT arrows to move", True, WHITE)
        screen.blit(controls_text, (WIDTH//2 - controls_text.get_width()//2, 20))
        
        # Draw game over screen
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = big_font.render("GAME OVER", True, RED)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
            restart_text = font.render("Press 'R' to Restart", True, WHITE)
            quit_text = font.render("Press ESC to Quit", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))
            screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2 - 30))
            screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 50))
            screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 90))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
