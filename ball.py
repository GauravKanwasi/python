"""
Enhanced Paddle Ball Game
A fun Pong-style game with progressive difficulty, improved physics, and comprehensive error handling.
Use LEFT/RIGHT arrow keys to move the paddle, SPACE to restart.
"""

import pygame
import random
import os
import math
import sys

# ============================================================================
# PYGAME INITIALIZATION
# ============================================================================
pygame.init()
pygame.mixer.init()

# ============================================================================
# GAME CONSTANTS AND CONFIGURATION
# ============================================================================

# Screen dimensions and frame rate
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
DELTA_TIME_MAX = 0.05  # Cap delta time to prevent large jumps (useful if game lags)

# Color definitions using descriptive names
COLORS = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "RED": (255, 0, 0),
    "BLUE": (0, 150, 255),
    "DARK_BLUE": (0, 100, 200),
    "GRAY": (200, 200, 200),
    "LIGHT_GRAY": (220, 220, 220),
    "GREEN": (0, 200, 0),
    "YELLOW": (255, 255, 0),
}

# Ball properties
BALL_RADIUS = 8
BALL_INITIAL_SPEED = 300  # pixels per second
BALL_SPEED_INCREASE = 1.08  # Multiplier each paddle hit (8% increase)
MAX_BALL_SPEED = 1000  # Cap ball speed to maintain playability
BALL_TRAIL_LENGTH = 8  # Visual trail behind the ball

# Paddle properties
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
PADDLE_SPEED = 600  # pixels per second
PADDLE_MARGIN = 20  # Distance from bottom of screen

# Difficulty settings - increases as score increases
DIFFICULTY_THRESHOLDS = {
    0: {"speed_multiplier": 1.0, "paddle_width": 100},
    10: {"speed_multiplier": 1.1, "paddle_width": 95},
    20: {"speed_multiplier": 1.2, "paddle_width": 90},
    30: {"speed_multiplier": 1.3, "paddle_width": 85},
    40: {"speed_multiplier": 1.4, "paddle_width": 80},
}

# ============================================================================
# DUMMY SOUND CLASS - Fallback for missing audio files
# ============================================================================

class DummySound:
    """
    Fallback class that does nothing when sound files are missing.
    Allows the game to continue without audio instead of crashing.
    """
    def play(self):
        pass


# ============================================================================
# BALL CLASS - Handles ball physics and rendering
# ============================================================================

class Ball:
    """
    Represents the game ball with physics simulation.
    Handles position, velocity, collision detection, and visual trail effect.
    """
    
    def __init__(self):
        """Initialize ball with default properties."""
        self.radius = BALL_RADIUS
        self.color = COLORS["RED"]
        self.trail = []  # List of previous positions for visual effect
        self.reset()

    def reset(self):
        """
        Reset ball to center position with random upward direction.
        Called at game start and after game over.
        """
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        
        # Random angle between -30 and 30 degrees (upward direction)
        angle = random.uniform(-30, 30) * (math.pi / 180)
        self.dx = BALL_INITIAL_SPEED * math.sin(angle)  # Horizontal velocity
        self.dy = -BALL_INITIAL_SPEED * math.cos(angle)  # Vertical velocity (negative = upward)
        self.active = True
        self.trail = []

    def update(self, delta_time, speed_multiplier=1.0):
        """
        Update ball position based on velocity and elapsed time.
        
        Args:
            delta_time: Time elapsed since last frame (in seconds)
            speed_multiplier: Difficulty multiplier for ball speed (1.0 = normal)
        """
        if self.active:
            # Update position with speed multiplier for difficulty progression
            self.x += self.dx * delta_time * speed_multiplier
            self.y += self.dy * delta_time * speed_multiplier
            
            # Add current position to trail for visual effect
            self.trail.append((int(self.x), int(self.y)))
            
            # Keep trail length limited for performance
            if len(self.trail) > BALL_TRAIL_LENGTH:
                self.trail.pop(0)

    def draw(self, surface):
        """
        Draw ball with fading trail effect.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw trail with fading effect (smaller and more transparent as you go back)
        for i, pos in enumerate(self.trail):
            trail_radius = max(1, self.radius - i)
            # Fade alpha by making older trail positions smaller
            pygame.draw.circle(surface, self.color, pos, trail_radius)
        
        # Draw main ball on top
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def get_speed(self):
        """Calculate current ball speed in pixels per second."""
        return math.sqrt(self.dx ** 2 + self.dy ** 2)

    def set_speed(self, speed):
        """
        Set ball speed while maintaining current direction.
        
        Args:
            speed: New speed in pixels per second
        """
        current_speed = self.get_speed()
        if current_speed > 0:
            scale = speed / current_speed
            self.dx *= scale
            self.dy *= scale


# ============================================================================
# PADDLE CLASS - Handles paddle movement and rendering
# ============================================================================

class Paddle:
    """
    Represents the player's paddle at the bottom of the screen.
    Handles movement input, position constraints, and rendering.
    """
    
    def __init__(self, width=PADDLE_WIDTH):
        """
        Initialize paddle with given width (can change with difficulty).
        
        Args:
            width: Paddle width in pixels
        """
        self.width = width
        self.height = PADDLE_HEIGHT
        self.x = SCREEN_WIDTH // 2 - self.width // 2  # Center horizontally
        self.y = SCREEN_HEIGHT - self.height - PADDLE_MARGIN  # Positioned from bottom
        self.color = COLORS["BLUE"]
        self.speed = PADDLE_SPEED
        self.dx = 0  # Current horizontal velocity

    def update(self, delta_time):
        """
        Update paddle position based on input velocity.
        Clamps paddle within screen bounds.
        
        Args:
            delta_time: Time elapsed since last frame (in seconds)
        """
        # Update position based on velocity
        self.x += self.dx * delta_time
        
        # Clamp paddle position to stay within screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

    def draw(self, surface):
        """
        Draw paddle with border for visual clarity.
        
        Args:
            surface: Pygame surface to draw on
        """
        # Draw filled paddle
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height), border_radius=3)
        # Draw border for contrast
        pygame.draw.rect(surface, COLORS["DARK_BLUE"], (self.x, self.y, self.width, self.height), 3, border_radius=3)

    def resize(self, new_width):
        """
        Resize paddle (used for difficulty progression).
        Maintains center position during resize.
        
        Args:
            new_width: New width in pixels
        """
        old_center = self.x + self.width / 2
        self.width = new_width
        self.x = old_center - self.width / 2
        # Keep within bounds after resize
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))


# ============================================================================
# GAME CLASS - Main game controller
# ============================================================================

class Game:
    """
    Main game class that manages game state, physics, rendering, and game flow.
    Handles initialization, event processing, collision detection, and drawing.
    """
    
    def __init__(self):
        """Initialize game window, assets, and game objects."""
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Enhanced Paddle Ball - Press SPACE to start")
        self.clock = pygame.time.Clock()
        
        # Fonts for UI text
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        
        # Load or initialize high score
        self.high_score = self.load_high_score()
        
        # Initialize game objects
        self.ball = Ball()
        self.paddle = Paddle()
        self.score = 0
        self.game_active = False  # Game starts paused
        
        # Difficulty tracking
        self.current_difficulty = 0
        self.speed_multiplier = 1.0
        
        # Load sound effects with fallback for missing files
        self.sounds = {
            "bounce": self.load_sound("bounce.wav"),
            "score": self.load_sound("score.wav"),
            "game_over": self.load_sound("game_over.wav"),
        }
        
        # Load and play background music if available
        self.load_background_music()
        
        print("Game initialized successfully!")
        print(f"High score: {self.high_score}")

    def load_sound(self, filename):
        """
        Load a sound file with error handling.
        Returns a DummySound if file is missing or can't be loaded.
        
        Args:
            filename: Name of sound file to load
            
        Returns:
            pygame.mixer.Sound or DummySound object
        """
        try:
            if not os.path.exists(filename):
                print(f"⚠ Sound file not found: {filename}")
                return DummySound()
            return pygame.mixer.Sound(filename)
        except Exception as e:
            print(f"⚠ Could not load sound '{filename}': {e}")
            return DummySound()

    def load_background_music(self):
        """
        Load and play background music if available.
        Loops continuously with -1 flag.
        """
        if os.path.exists("background_music.mp3"):
            try:
                pygame.mixer.music.load("background_music.mp3")
                pygame.mixer.music.play(-1)  # -1 means loop indefinitely
                pygame.mixer.music.set_volume(0.3)  # 30% volume to not be too loud
                print("✓ Background music loaded and playing")
            except Exception as e:
                print(f"⚠ Could not load background music: {e}")
        else:
            print("ℹ Background music file not found (background_music.mp3)")

    def load_high_score(self):
        """
        Load high score from file.
        Returns 0 if file doesn't exist or is corrupted.
        
        Returns:
            int: Saved high score or 0
        """
        try:
            with open("highscore.txt", "r") as f:
                score = int(f.read().strip())
                return score
        except (FileNotFoundError, ValueError):
            return 0

    def save_high_score(self):
        """Save current high score to file for persistence."""
        new_high_score = max(self.score, self.high_score)
        try:
            with open("highscore.txt", "w") as f:
                f.write(str(new_high_score))
            self.high_score = new_high_score
        except Exception as e:
            print(f"⚠ Could not save high score: {e}")

    def update_difficulty(self):
        """
        Update game difficulty based on current score.
        Increases ball speed and decreases paddle width as player scores more.
        """
        # Find the appropriate difficulty threshold
        applicable_threshold = 0
        for threshold in sorted(DIFFICULTY_THRESHOLDS.keys()):
            if self.score >= threshold:
                applicable_threshold = threshold
        
        if applicable_threshold != self.current_difficulty:
            self.current_difficulty = applicable_threshold
            settings = DIFFICULTY_THRESHOLDS[applicable_threshold]
            self.speed_multiplier = settings["speed_multiplier"]
            
            # Resize paddle
            new_paddle_width = settings["paddle_width"]
            self.paddle.resize(new_paddle_width)
            
            print(f"✓ Difficulty level {applicable_threshold}: Speed {self.speed_multiplier}x, Paddle {new_paddle_width}px")

    def handle_events(self):
        """
        Process player input and window events.
        Handles paddle movement and game restart.
        """
        for event in pygame.event.get():
            # Window close event
            if event.type == pygame.QUIT:
                print("Game closed by user")
                pygame.quit()
                sys.exit()
            
            # Keyboard input
            if event.type == pygame.KEYDOWN:
                # Paddle movement
                if event.key == pygame.K_LEFT:
                    self.paddle.dx = -self.paddle.speed
                elif event.key == pygame.K_RIGHT:
                    self.paddle.dx = self.paddle.speed
                
                # Game restart
                elif event.key == pygame.K_SPACE:
                    if not self.game_active:
                        self.restart_game()
            
            # Key release - stop paddle movement
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.paddle.dx = 0

    def check_collisions(self):
        """
        Handle all collision detection and response.
        Detects wall collisions, paddle collisions, and game over condition.
        """
        # ===== WALL COLLISIONS =====
        # Left and right walls
        if self.ball.x - BALL_RADIUS <= 0 or self.ball.x + BALL_RADIUS >= SCREEN_WIDTH:
            self.ball.dx = -self.ball.dx
            # Push ball away from wall to prevent getting stuck
            self.ball.x = max(BALL_RADIUS, min(SCREEN_WIDTH - BALL_RADIUS, self.ball.x))
            self.sounds["bounce"].play()
        
        # Top wall
        if self.ball.y - BALL_RADIUS <= 0:
            self.ball.dy = -self.ball.dy
            self.ball.y = BALL_RADIUS
            self.sounds["bounce"].play()

        # ===== PADDLE COLLISION =====
        paddle_rect = pygame.Rect(
            self.paddle.x,
            self.paddle.y,
            self.paddle.width,
            self.paddle.height
        )
        ball_rect = pygame.Rect(
            self.ball.x - BALL_RADIUS,
            self.ball.y - BALL_RADIUS,
            BALL_RADIUS * 2,
            BALL_RADIUS * 2
        )
        
        # Check collision and ensure ball is moving downward into paddle
        if ball_rect.colliderect(paddle_rect) and self.ball.dy > 0:
            # Reflect ball upward
            self.ball.dy = -abs(self.ball.dy)
            
            # Add spin based on where ball hits paddle
            # -0.5 = left edge, 0 = center, +0.5 = right edge
            hit_pos = (self.ball.x - self.paddle.x) / self.paddle.width - 0.5
            # Clamp hit_pos to [-0.5, 0.5] to prevent extreme angles
            hit_pos = max(-0.5, min(0.5, hit_pos))
            
            # Add horizontal velocity based on hit position
            self.ball.dx += hit_pos * 200  # Spin effect
            
            # Increase ball speed and cap it
            current_speed = self.ball.get_speed()
            new_speed = min(current_speed * BALL_SPEED_INCREASE, MAX_BALL_SPEED)
            self.ball.set_speed(new_speed)
            
            # Increment score and update difficulty
            self.score += 1
            self.update_difficulty()
            self.sounds["score"].play()
            
            # Push ball up slightly to prevent multiple collision checks
            self.ball.y = self.paddle.y - BALL_RADIUS - 1

        # ===== GAME OVER CONDITION =====
        if self.ball.y > SCREEN_HEIGHT:
            self.end_game()

    def restart_game(self):
        """Reset game state to start a new game."""
        self.game_active = True
        self.ball.reset()
        self.score = 0
        self.current_difficulty = 0
        self.speed_multiplier = 1.0
        self.paddle.resize(PADDLE_WIDTH)
        self.paddle.x = SCREEN_WIDTH // 2 - self.paddle.width // 2
        print("Game restarted!")

    def end_game(self):
        """End the current game and save score."""
        self.game_active = False
        self.sounds["game_over"].play()
        self.save_high_score()
        print(f"Game Over! Final Score: {self.score}, High Score: {self.high_score}")

    def draw_game_over_screen(self):
        """
        Draw the game over screen with score information and restart instructions.
        """
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(COLORS["BLACK"])
        self.screen.blit(overlay, (0, 0))
        
        # Game Over text
        game_over_text = self.font_large.render("GAME OVER", True, COLORS["RED"])
        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Current score
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLORS["YELLOW"])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(score_text, score_rect)
        
        # High score
        high_score_text = self.font_medium.render(f"High Score: {self.high_score}", True, COLORS["GREEN"])
        hs_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(high_score_text, hs_rect)
        
        # Restart instruction
        restart_text = self.font_small.render("Press SPACE to Restart", True, COLORS["WHITE"])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        self.screen.blit(restart_text, restart_rect)

    def draw_ui(self):
        """
        Draw game UI elements during active gameplay.
        Shows score, high score, and difficulty level.
        """
        # Current score
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLORS["BLACK"])
        self.screen.blit(score_text, (15, 15))
        
        # High score
        high_score_text = self.font_small.render(f"High Score: {self.high_score}", True, COLORS["GRAY"])
        self.screen.blit(high_score_text, (15, 55))
        
        # Difficulty level indicator
        difficulty_text = self.font_small.render(f"Level: {self.current_difficulty}", True, COLORS["BLUE"])
        self.screen.blit(difficulty_text, (15, 85))
        
        # Ball speed indicator (as a simple bar)
        speed = self.ball.get_speed()
        speed_pct = min(100, int((speed / MAX_BALL_SPEED) * 100))
        speed_text = self.font_small.render(f"Speed: {speed_pct}%", True, COLORS["RED"])
        self.screen.blit(speed_text, (SCREEN_WIDTH - 200, 15))

    def run(self):
        """
        Main game loop.
        Handles events, updates physics, collision detection, and rendering.
        """
        print("Starting game loop...")
        
        while True:
            # Cap delta time to prevent physics issues if game lags
            delta_time = min(self.clock.tick(FPS) / 1000.0, DELTA_TIME_MAX)
            
            # Process input
            self.handle_events()
            
            # Clear screen
            self.screen.fill(COLORS["WHITE"])
            
            if self.game_active:
                # Update game objects
                self.paddle.update(delta_time)
                self.ball.update(delta_time, self.speed_multiplier)
                
                # Check for collisions
                self.check_collisions()
                
                # Draw game objects
                self.ball.draw(self.screen)
                self.paddle.draw(self.screen)
                
                # Draw UI
                self.draw_ui()
            else:
                # Show start/game over screen
                if self.score == 0:
                    # Initial start screen
                    start_text = self.font_large.render("Paddle Ball", True, COLORS["BLUE"])
                    start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
                    self.screen.blit(start_text, start_rect)
                    
                    instructions = self.font_small.render("Press SPACE to Start", True, COLORS["BLACK"])
                    instr_rect = instructions.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                    self.screen.blit(instructions, instr_rect)
                else:
                    # Game over screen
                    self.draw_game_over_screen()
            
            # Draw border around screen
            pygame.draw.rect(self.screen, COLORS["BLACK"], (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT), 5)
            
            # Update display
            pygame.display.flip()


# ============================================================================
# PROGRAM ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    try:
        game = Game()
        game.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        pygame.quit()
        sys.exit(1)
