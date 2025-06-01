import pygame
import random
import os
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
FPS = 60
COLORS = {
    "WHITE": (255, 255, 255),
    "RED": (255, 0, 0),
    "BLUE": (0, 0, 255),
    "BLACK": (0, 0, 0),
    "GRAY": (200, 200, 200)
}

# Game settings
BALL_RADIUS = 15
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
BALL_SPEED_INCREASE = 1.05
MAX_BALL_SPEED = 800  # pixels per second

# Dummy sound class for fallback
class DummySound:
    def play(self):
        pass

# Ball class
class Ball:
    def __init__(self):
        self.radius = BALL_RADIUS
        self.color = COLORS["RED"]
        self.trail = []
        self.reset()

    def reset(self):
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        initial_speed = 300  # pixels per second
        angle = random.uniform(-30, 30) * (math.pi / 180)  # Random angle in radians
        self.dx = initial_speed * math.sin(angle)
        self.dy = -initial_speed * math.cos(angle)
        self.active = True
        self.trail = []

    def update(self, delta_time):
        if self.active:
            self.x += self.dx * delta_time
            self.y += self.dy * delta_time
            self.trail.append((int(self.x), int(self.y)))
            if len(self.trail) > 5:
                self.trail.pop(0)

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            pygame.draw.circle(surface, self.color, pos, self.radius - i)
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

# Paddle class
class Paddle:
    def __init__(self):
        self.width = PADDLE_WIDTH
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2
        self.y = SCREEN_HEIGHT - self.height - 20
        self.color = COLORS["BLUE"]
        self.speed = 600  # pixels per second
        self.dx = 0

    def update(self, delta_time):
        self.x += self.dx * delta_time
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, COLORS["BLACK"], (self.x, self.y, self.width, self.height), 2)

# Game class
class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Paddle Ball")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.high_score = self.load_high_score()
        
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = 0
        self.game_active = True
        
        # Load sounds with fallback
        self.sounds = {
            "bounce": self.load_sound("bounce.wav"),
            "score": self.load_sound("score.wav"),
            "game_over": self.load_sound("game_over.wav")
        }
        
        # Background music
        if os.path.exists("background_music.mp3"):
            pygame.mixer.music.load("background_music.mp3")
            pygame.mixer.music.play(-1)
        else:
            print("Background music not found - continuing without music")

    def load_sound(self, filename):
        try:
            return pygame.mixer.Sound(filename)
        except Exception as e:
            print(f"Sound error: {e} - continuing without sound")
            return DummySound()

    def load_high_score(self):
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        with open("highscore.txt", "w") as f:
            f.write(str(max(self.score, self.high_score)))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.paddle.dx = -self.paddle.speed
                elif event.key == pygame.K_RIGHT:
                    self.paddle.dx = self.paddle.speed
                elif event.key == pygame.K_SPACE and not self.game_active:
                    self.game_active = True
                    self.ball.reset()
                    self.score = 0
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.paddle.dx = 0

    def check_collisions(self):
        # Wall collisions
        if self.ball.x <= BALL_RADIUS or self.ball.x >= SCREEN_WIDTH - BALL_RADIUS:
            self.ball.dx = -self.ball.dx
            self.sounds["bounce"].play()
        if self.ball.y <= BALL_RADIUS:
            self.ball.dy = -self.ball.dy
            self.sounds["bounce"].play()

        # Paddle collision
        paddle_rect = pygame.Rect(self.paddle.x, self.paddle.y, self.paddle.width, self.paddle.height)
        ball_rect = pygame.Rect(self.ball.x - BALL_RADIUS, self.ball.y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
        
        if ball_rect.colliderect(paddle_rect) and self.ball.dy > 0:
            self.ball.dy = -self.ball.dy
            hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width - 0.5  # -0.5 to 0.5
            self.ball.dx += hit_pos * 100  # Horizontal influence
            # Increase and cap speed
            current_speed = (self.ball.dx ** 2 + self.ball.dy ** 2) ** 0.5
            new_speed = min(current_speed * BALL_SPEED_INCREASE, MAX_BALL_SPEED)
            if current_speed > 0:
                scale = new_speed / current_speed
                self.ball.dx *= scale
                self.ball.dy *= scale
            self.score += 1
            self.sounds["score"].play()

        # Game over condition
        if self.ball.y > SCREEN_HEIGHT:
            self.sounds["game_over"].play()
            self.save_high_score()
            self.game_active = False

    def draw_game_over(self):
        text = self.font.render(f"Game Over! Score: {self.score}", True, COLORS["BLACK"])
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)

        high_score_text = self.font.render(f"High Score: {max(self.score, self.high_score)}", True, COLORS["BLACK"])
        hs_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(high_score_text, hs_rect)

        restart_text = self.font.render("Press SPACE to Restart", True, COLORS["BLUE"])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        while True:
            delta_time = self.clock.tick(FPS) / 1000.0  # Time in seconds
            self.handle_events()
            self.screen.fill(COLORS["WHITE"])

            if self.game_active:
                self.paddle.update(delta_time)
                self.ball.update(delta_time)
                self.check_collisions()

                self.ball.draw(self.screen)
                self.paddle.draw(self.screen)

                # Draw scores
                score_text = self.font.render(f"Score: {self.score}", True, COLORS["BLACK"])
                self.screen.blit(score_text, (10, 10))
                high_score_text = self.font.render(f"High Score: {self.high_score}", True, COLORS["GRAY"])
                self.screen.blit(high_score_text, (10, 50))
            else:
                self.draw_game_over()

            pygame.draw.rect(self.screen, COLORS["BLACK"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)
            pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()
