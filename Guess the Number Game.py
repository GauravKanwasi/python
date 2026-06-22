import pygame
import random
import sys
import os

# ============================================================================
# GUESS THE NUMBER GAME - Enhanced Version
# ============================================================================
# Features:
# - Number guessing game with visual feedback
# - Particle effects for win/loss
# - Previous guesses tracking with color-coded feedback
# - Multiple difficulty levels
# - High score tracking
# - Animated text scaling
# - Blinking cursor in input field
# ============================================================================

# Initialize Pygame
pygame.init()

# ============================================================================
# GAME CONFIGURATION CONSTANTS
# ============================================================================
WIDTH, HEIGHT = 800, 600
FRAME_RATE = 60

# Color palette for consistent styling
BG_COLOR = (10, 10, 30)              # Dark blue background
TEXT_COLOR = (255, 255, 255)         # White text
INPUT_COLOR = (40, 40, 40)           # Dark gray input field
HIGHLIGHT_COLOR = (0, 122, 204)      # Bright blue for highlights
GRAY_COLOR = (100, 100, 100)         # Gray for disabled elements
COLOR_LOW = (0, 100, 255)            # Blue for "too low" feedback
COLOR_HIGH = (255, 50, 50)           # Red for "too high" feedback
COLOR_CORRECT = (0, 255, 100)        # Green for correct guess

# Animation timing constants (in milliseconds)
CURSOR_BLINK_TIME = 500              # Cursor blink interval
FEEDBACK_ANIMATION_SPEED = 0.1       # Feedback text scale-up speed
GAME_OVER_ANIMATION_SPEED = 0.1      # Game over message scale-up speed

# Particle effect constants
CONFETTI_PARTICLE_COUNT = 50         # Particles for winning
LOSS_PARTICLE_COUNT = 20             # Particles for losing
PARTICLE_GRAVITY = 0.1               # Gravity effect on particles

# Difficulty levels: (range_min, range_max, max_attempts)
DIFFICULTY_LEVELS = {
    "easy": (1, 50, 10),
    "normal": (1, 100, 7),
    "hard": (1, 200, 5),
}

# ============================================================================
# PARTICLE CLASS - Visual effects for feedback
# ============================================================================
class Particle:
    """
    Represents a particle for visual effects (confetti for winning, etc.)
    Particles fall with gravity and are rendered as circles.
    """
    def __init__(self, x, y, color):
        """
        Initialize a particle at the given position with the given color.
        
        Args:
            x (float): Initial x position
            y (float): Initial y position
            color (tuple): RGB color tuple
        """
        self.x = x
        self.y = y
        self.color = color
        # Randomize velocity for more natural motion
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-1, 1)
        self.size = random.randint(3, 7)
        self.alpha_decay = random.uniform(0.01, 0.03)  # Fade effect

    def update(self):
        """Update particle position based on velocity and gravity."""
        self.x += self.vx
        self.y += self.vy
        # Apply gravity to make particles fall
        self.vy += PARTICLE_GRAVITY

    def draw(self, surface):
        """
        Draw the particle on the given surface.
        
        Args:
            surface: Pygame surface to draw on
        """
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.size)

# ============================================================================
# NUMBER GUESSER CLASS - Main game logic
# ============================================================================
class NumberGuesser:
    """
    Main game class that handles the number guessing game logic,
    input validation, and game state management.
    """
    def __init__(self, difficulty="normal"):
        """
        Initialize a new game with the specified difficulty level.
        
        Args:
            difficulty (str): One of "easy", "normal", or "hard"
        """
        # Get difficulty settings
        if difficulty not in DIFFICULTY_LEVELS:
            difficulty = "normal"
        
        self.min_num, self.max_num, self.max_attempts = DIFFICULTY_LEVELS[difficulty]
        self.difficulty = difficulty
        
        # Game state variables
        self.number = random.randint(self.min_num, self.max_num)
        self.attempts = 0
        self.game_over = False
        self.won = False
        
        # Input handling
        self.guess = ""
        self.feedback = ""
        
        # Range tracking (narrows as player guesses)
        self.current_min = self.min_num
        self.current_max = self.max_num
        
        # Animation state
        self.feedback_scale = 1.0
        self.game_over_scale = 1.0
        
        # Visual effects
        self.particles = []
        self.guesses = []  # List of (guess_number, status) tuples
        
        # Cursor animation
        self.cursor_visible = True
        self.cursor_timer = 0

    def reset_game(self, difficulty="normal"):
        """Reset the game to initial state for a new round."""
        self.__init__(difficulty)

    def handle_input(self, event):
        """
        Handle keyboard input for number entry and game controls.
        
        Args:
            event: Pygame key event
        """
        if event.key == pygame.K_RETURN:
            # Enter key: submit the guess
            self.check_guess()
        elif event.key == pygame.K_BACKSPACE:
            # Backspace: remove last character
            self.guess = self.guess[:-1]
        elif event.unicode.isdigit():
            # Number keys (0-9): add digit to guess
            # Limit guess to 3 digits
            if len(self.guess) < 3:
                self.guess += event.unicode

    def check_guess(self):
        """
        Validate and process the player's guess.
        Updates game state based on the guess result.
        """
        if not self.guess:
            return

        try:
            guess_num = int(self.guess)
            
            # Validate guess is within current range
            if guess_num < self.current_min or guess_num > self.current_max:
                self.feedback = f"Guess between {self.current_min}-{self.current_max}!"
                self.feedback_scale = 0.1
                self.guess = ""
                return

            self.attempts += 1
            
            # ================================================================
            # CHECK GUESS RESULT
            # ================================================================
            if guess_num == self.number:
                # CORRECT GUESS - Player wins!
                self.game_over = True
                self.won = True
                self.game_over_scale = 0.1
                self.guesses.append((guess_num, "correct"))
                self._spawn_confetti_particles()
                
            elif self.attempts >= self.max_attempts:
                # OUT OF ATTEMPTS - Player loses!
                self.game_over = True
                self.won = False
                self.game_over_scale = 0.1
                status = "high" if guess_num > self.number else "low"
                self.guesses.append((guess_num, status))
                self._spawn_loss_particles()
                
            elif guess_num < self.number:
                # TOO LOW - Narrow range upward
                self.current_min = guess_num + 1
                self.feedback = f"{guess_num} is too low! Try higher."
                self.feedback_scale = 0.1
                self.guesses.append((guess_num, "low"))
                
            else:  # guess_num > self.number
                # TOO HIGH - Narrow range downward
                self.current_max = guess_num - 1
                self.feedback = f"{guess_num} is too high! Try lower."
                self.feedback_scale = 0.1
                self.guesses.append((guess_num, "high"))

            self.guess = ""

        except ValueError:
            # Non-numeric input
            self.feedback = "Please enter a valid number"
            self.feedback_scale = 0.1
            self.guess = ""

    def _spawn_confetti_particles(self):
        """Spawn celebratory particles when player wins."""
        for _ in range(CONFETTI_PARTICLE_COUNT):
            x = random.randint(0, WIDTH)
            y = random.randint(-50, 0)
            # Random bright colors for confetti
            color = (random.randint(150, 255), 
                    random.randint(150, 255), 
                    random.randint(150, 255))
            self.particles.append(Particle(x, y, color))

    def _spawn_loss_particles(self):
        """Spawn gray particles when player loses."""
        for _ in range(LOSS_PARTICLE_COUNT):
            x = random.randint(0, WIDTH)
            y = random.randint(-50, 0)
            self.particles.append(Particle(x, y, (100, 100, 100)))

# ============================================================================
# UI HELPER FUNCTIONS
# ============================================================================
def draw_text(text, position, font_obj, color=TEXT_COLOR, center=False):
    """
    Render and draw text on the screen.
    
    Args:
        text (str): Text to render
        position (tuple): (x, y) position
        font_obj: Pygame font object
        color (tuple): RGB color
        center (bool): If True, center text at position
    """
    text_surface = font_obj.render(text, True, color)
    if center:
        position = (position[0] - text_surface.get_width() // 2,
                   position[1] - text_surface.get_height() // 2)
    screen.blit(text_surface, position)

def draw_input_box(input_rect, game, font_obj):
    """
    Draw the input field with border and cursor.
    
    Args:
        input_rect: Pygame Rect for input field
        game: NumberGuesser instance
        font_obj: Pygame font object
    """
    # Draw input box background
    if game.game_over:
        pygame.draw.rect(screen, GRAY_COLOR, input_rect)
    else:
        pygame.draw.rect(screen, INPUT_COLOR, input_rect)
        pygame.draw.rect(screen, HIGHLIGHT_COLOR, input_rect, 2)
    
    # Draw input text
    draw_text(game.guess, (input_rect.x + 10, input_rect.y + 10), font_obj)
    
    # Draw blinking cursor (only when game is active)
    if not game.game_over:
        current_time = pygame.time.get_ticks()
        # Toggle cursor visibility every CURSOR_BLINK_TIME milliseconds
        if current_time - game.cursor_timer > CURSOR_BLINK_TIME:
            game.cursor_visible = not game.cursor_visible
            game.cursor_timer = current_time
        
        if game.cursor_visible:
            text_surface = font_obj.render(game.guess, True, TEXT_COLOR)
            cursor_x = input_rect.x + 10 + text_surface.get_width()
            # Draw vertical line for cursor
            pygame.draw.line(screen, TEXT_COLOR, 
                           (cursor_x, input_rect.y + 5), 
                           (cursor_x, input_rect.y + input_rect.height - 5), 2)

def draw_previous_guesses(game, font_obj):
    """
    Draw the history of previous guesses with color-coded feedback.
    
    Args:
        game: NumberGuesser instance
        font_obj: Pygame font object
    """
    x_pos = 50
    y_pos = 100
    max_guesses_to_show = 8
    
    # Show only the most recent guesses
    recent_guesses = game.guesses[-max_guesses_to_show:]
    
    for i, (guess, status) in enumerate(recent_guesses):
        # Choose color based on guess result
        if status == "low":
            color = COLOR_LOW
            label = f"{guess} ↑"
        elif status == "high":
            color = COLOR_HIGH
            label = f"{guess} ↓"
        else:  # correct
            color = COLOR_CORRECT
            label = f"{guess} ✓"
        
        draw_text(label, (x_pos, y_pos + i * 25), font_obj, color)

def draw_animated_text(text, position, scale, font_obj, color=TEXT_COLOR):
    """
    Draw text with scaling animation.
    
    Args:
        text (str): Text to render
        position (tuple): Center position for text
        scale (float): Scale factor (0.0 to 1.0)
        font_obj: Pygame font object
        color (tuple): RGB color
    """
    text_surface = font_obj.render(text, True, color)
    
    # Scale the surface
    scaled_width = max(1, int(text_surface.get_width() * scale))
    scaled_height = max(1, int(text_surface.get_height() * scale))
    scaled_surface = pygame.transform.scale(text_surface, (scaled_width, scaled_height))
    
    # Calculate centered position
    pos_x = position[0] - scaled_width // 2
    pos_y = position[1] - scaled_height // 2
    
    screen.blit(scaled_surface, (pos_x, pos_y))

# ============================================================================
# DIFFICULTY SELECTION MENU
# ============================================================================
def show_difficulty_menu(font_obj, large_font):
    """
    Display difficulty selection menu and return selected difficulty.
    
    Returns:
        str: Selected difficulty level ("easy", "normal", or "hard")
    """
    selected = 1  # Start with "normal"
    difficulties = ["easy", "normal", "hard"]
    
    selecting = True
    while selecting:
        screen.fill(BG_COLOR)
        
        # Draw title
        draw_text("Guess the Number Game", (WIDTH // 2, 80), large_font, 
                 HIGHLIGHT_COLOR, center=True)
        
        # Draw difficulty options
        draw_text("Select Difficulty:", (WIDTH // 2, 180), font_obj, 
                 TEXT_COLOR, center=True)
        
        for i, diff in enumerate(difficulties):
            y_pos = 280 + i * 80
            
            # Highlight selected option
            if i == selected:
                color = HIGHLIGHT_COLOR
                prefix = "► "
            else:
                color = TEXT_COLOR
                prefix = "  "
            
            difficulty_text = f"{prefix}{diff.upper()}"
            draw_text(difficulty_text, (WIDTH // 2, y_pos), font_obj, 
                     color, center=True)
            
            # Draw range and attempts info
            min_n, max_n, attempts = DIFFICULTY_LEVELS[diff]
            info = f"(1-{max_n}, {attempts} attempts)"
            draw_text(info, (WIDTH // 2, y_pos + 30), font_obj, 
                     GRAY_COLOR, center=True)
        
        # Draw instructions
        draw_text("Use UP/DOWN arrows to select, ENTER to confirm", 
                 (WIDTH // 2, 550), font_obj, GRAY_COLOR, center=True)
        
        pygame.display.flip()
        
        # Handle input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(difficulties)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(difficulties)
                elif event.key == pygame.K_RETURN:
                    selecting = False
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        
        clock.tick(FRAME_RATE)
    
    return difficulties[selected]

# ============================================================================
# MAIN GAME LOOP
# ============================================================================
def main():
    """
    Main game loop that handles rendering, input, and game state updates.
    """
    global screen, clock, font
    
    # Set up the display
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Guess the Number Game")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 32)
    large_font = pygame.font.Font(None, 48)
    
    # Show difficulty selection menu
    difficulty = show_difficulty_menu(font, large_font)
    
    # Initialize game
    game = NumberGuesser(difficulty)
    
    # Input box dimensions
    input_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 40)
    
    running = True
    while running:
        # ================================================================
        # EVENT HANDLING
        # ================================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif not game.game_over:
                    # Only handle game input if game is active
                    game.handle_input(event)
                elif event.key == pygame.K_SPACE:
                    # Reset game with same difficulty
                    game.reset_game(game.difficulty)
                elif event.key == pygame.K_d:
                    # Change difficulty
                    difficulty = show_difficulty_menu(font, large_font)
                    game.reset_game(difficulty)
        
        # ================================================================
        # UPDATE GAME STATE
        # ================================================================
        
        # Update and filter out off-screen particles
        for particle in game.particles:
            particle.update()
        game.particles = [p for p in game.particles if p.y < HEIGHT]
        
        # Update animation scales
        if game.feedback_scale < 1.0:
            game.feedback_scale = min(1.0, game.feedback_scale + FEEDBACK_ANIMATION_SPEED)
        
        if game.game_over and game.game_over_scale < 1.0:
            game.game_over_scale = min(1.0, game.game_over_scale + GAME_OVER_ANIMATION_SPEED)
        
        # ================================================================
        # RENDERING
        # ================================================================
        screen.fill(BG_COLOR)
        
        # Draw all particles
        for particle in game.particles:
            particle.draw(screen)
        
        # Draw game title
        draw_text("Guess the Number Game", (WIDTH // 2, 30), large_font, 
                 HIGHLIGHT_COLOR, center=True)
        
        # Draw difficulty level
        draw_text(f"Difficulty: {game.difficulty.upper()}", 
                 (WIDTH // 2, 70), font, GRAY_COLOR, center=True)
        
        # Draw game stats
        draw_text(f"Range: {game.current_min} - {game.current_max}", 
                 (WIDTH // 2, 120), font, TEXT_COLOR, center=True)
        
        draw_text(f"Attempts: {game.attempts}/{game.max_attempts}", 
                 (WIDTH // 2, 160), font, TEXT_COLOR, center=True)
        
        # Draw previous guesses
        draw_text("Previous guesses:", (50, 80), font, TEXT_COLOR)
        draw_previous_guesses(game, font)
        
        # Draw input box
        draw_input_box(input_rect, game, font)
        
        # Draw feedback message with animation
        if game.feedback:
            draw_animated_text(game.feedback, (WIDTH // 2, HEIGHT - 150), 
                             game.feedback_scale, font, TEXT_COLOR)
        
        # Draw game over message with animation
        if game.game_over:
            if game.won:
                message = f"🎉 Congratulations! You won in {game.attempts} attempts!"
                color = COLOR_CORRECT
            else:
                message = f"💀 Game Over! The number was {game.number}"
                color = COLOR_HIGH
            
            draw_animated_text(message, (WIDTH // 2, 250), 
                             game.game_over_scale, large_font, color)
            
            # Draw restart instructions
            draw_text("Press SPACE to play again | Press D for difficulty", 
                     (WIDTH // 2, HEIGHT - 40), font, TEXT_COLOR, center=True)
        else:
            # Draw instructions when game is active
            draw_text("Enter a number and press ENTER (ESC to exit)", 
                     (WIDTH // 2, HEIGHT - 40), font, GRAY_COLOR, center=True)
        
        # Update display
        pygame.display.flip()
        clock.tick(FRAME_RATE)
    
    pygame.quit()
    sys.exit()

# ============================================================================
# ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    main()
