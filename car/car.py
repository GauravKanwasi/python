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

# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
game_speed = 5

# Font
font = pygame.font.SysFont(None, 36)

class PlayerCar:
    def __init__(self):
        self.width = 40
        self.height = 70
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - self.height - 20
        self.speed = 8
        self.color = RED
        self.draw_car()
        
    def draw_car(self):
        # Create surface for the car
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Car body
        pygame.draw.rect(self.surface, self.color, (0, 0, self.width, self.height), border_radius=8)
        
        # Car details
        pygame.draw.rect(self.surface, BLACK, (5, 5, self.width-10, 15), border_radius=3)  # windshield
        pygame.draw.rect(self.surface, BLACK, (5, self.height-20, self.width-10, 15), border_radius=3)  # rear
        
        # Windows
        pygame.draw.rect(self.surface, BLUE, (8, 8, self.width-16, 10), border_radius=2)
        pygame.draw.rect(self.surface, BLUE, (8, self.height-17, self.width-16, 10), border_radius=2)
        
        # Wheels
        pygame.draw.rect(self.surface, BLACK, (2, 15, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, 15, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (2, self.height-30, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, self.height-30, 8, 15), border_radius=3)
        
    def move(self, direction):
        if direction == "left" and self.x > WIDTH//3:
            self.x -= self.speed
        if direction == "right" and self.x < WIDTH*2//3 - self.width:
            self.x += self.speed
            
    def draw(self, screen):
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
        
        # Car body
        pygame.draw.rect(self.surface, self.color, (0, 0, self.width, self.height), border_radius=8)
        
        # Car details
        pygame.draw.rect(self.surface, BLACK, (5, 5, self.width-10, 15), border_radius=3)  # windshield
        pygame.draw.rect(self.surface, BLACK, (5, self.height-20, self.width-10, 15), border_radius=3)  # rear
        
        # Windows
        pygame.draw.rect(self.surface, YELLOW, (8, 8, self.width-16, 10), border_radius=2)
        pygame.draw.rect(self.surface, YELLOW, (8, self.height-17, self.width-16, 10), border_radius=2)
        
        # Wheels
        pygame.draw.rect(self.surface, BLACK, (2, 15, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, 15, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (2, self.height-30, 8, 15), border_radius=3)
        pygame.draw.rect(self.surface, BLACK, (self.width-10, self.height-30, 8, 15), border_radius=3)
        
    def move(self):
        self.y += self.speed
        
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
    
    def update(self):
        for i in range(len(self.lines)):
            self.lines[i] += game_speed
            if self.lines[i] > HEIGHT:
                self.lines[i] = -self.line_height
    
    def draw(self, screen):
        # Draw grass
        pygame.draw.rect(screen, GRASS_GREEN, (0, 0, WIDTH//3, HEIGHT))
        pygame.draw.rect(screen, GRASS_GREEN, (WIDTH*2//3, 0, WIDTH//3, HEIGHT))
        
        # Draw road
        pygame.draw.rect(screen, ROAD_GRAY, (WIDTH//3, 0, WIDTH//3, HEIGHT))
        
        # Draw road lines
        for line_y in self.lines:
            pygame.draw.rect(screen, ROAD_LINE, 
                            (WIDTH//2 - self.line_width//2, line_y, self.line_width, self.line_height))

def draw_environment(screen):
    # Draw sky
    screen.fill(SKY_BLUE)
    
    # Draw sun
    pygame.draw.circle(screen, YELLOW, (700, 80), 50)

def main():
    global score, game_speed
    
    player = PlayerCar()
    road = Road()
    enemies = []
    enemy_spawn_timer = 0
    enemy_spawn_delay = 60  # frames
    
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
                    if game_speed < 12:
                        game_speed += 0.01
            
            # Check collisions
            player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
            for enemy in enemies:
                enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                if player_rect.colliderect(enemy_rect):
                    game_over = True
            
            # Update road
            road.update()
        
        # Drawing
        draw_environment(screen)
        road.draw(screen)
        player.draw(screen)
        
        for enemy in enemies:
            enemy.draw(screen)
        
        # Draw score
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (20, 20))
        
        # Draw speed
        speed_text = font.render(f"Speed: {game_speed:.1f}", True, WHITE)
        screen.blit(speed_text, (20, 60))
        
        # Draw game over screen
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            game_over_text = font.render("GAME OVER", True, RED)
            final_score_text = font.render(f"Final Score: {score}", True, WHITE)
            restart_text = font.render("Press 'R' to Restart", True, WHITE)
            quit_text = font.render("Press ESC to Quit", True, WHITE)
            
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 60))
            screen.blit(final_score_text, (WIDTH//2 - final_score_text.get_width()//2, HEIGHT//2))
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))
            screen.blit(quit_text, (WIDTH//2 - quit_text.get_width()//2, HEIGHT//2 + 100))
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
