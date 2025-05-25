import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (10, 10, 30)  # Darker blue background for vibrancy
TEXT_COLOR = (255, 255, 255)
INPUT_COLOR = (40, 40, 40)
HIGHLIGHT_COLOR = (0, 122, 204)
GRAY_COLOR = (100, 100, 100)

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guess the Number Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)

# Particle class for visual effects
class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(0, 2)
        self.size = random.randint(2, 5)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1  # Gravity effect

    def draw(self):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)

class NumberGuesser:
    def __init__(self):
        self.min_num = 1
        self.max_num = 100
        self.max_attempts = 7
        self.attempts = 0
        self.number = random.randint(self.min_num, self.max_num)
        self.guess = ""
        self.feedback = ""
        self.current_min = self.min_num
        self.current_max = self.max_num
        self.game_over = False
        self.won = False
        self.feedback_scale = 1.0  # For feedback animation
        self.game_over_scale = 1.0  # For game over animation
        self.particles = []  # List for particles
        self.guesses = []  # List for previous guesses
        self.cursor_visible = True  # For blinking cursor
        self.cursor_timer = 0

    def reset_game(self):
        self.__init__()

    def handle_input(self, event):
        if event.key == pygame.K_RETURN:
            self.check_guess()
        elif event.key == pygame.K_BACKSPACE:
            self.guess = self.guess[:-1]
        elif event.key in (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, 
                          pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, 
                          pygame.K_8, pygame.K_9):
            self.guess += event.unicode

    def check_guess(self):
        if not self.guess:
            return

        try:
            guess_num = int(self.guess)
            if guess_num < self.current_min or guess_num > self.current_max:
                self.feedback = f"Number must be between {self.current_min}-{self.current_max}"
                self.feedback_scale = 0.1
                return

            self.attempts += 1

            if guess_num == self.number:
                self.game_over = True
                self.won = True
                self.game_over_scale = 0.1
                self.guesses.append((guess_num, "correct"))
                # Add confetti particles for winning
                for _ in range(50):
                    particle = Particle(random.randint(0, WIDTH), 0, 
                                       (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255)))
                    self.particles.append(particle)
            elif self.attempts >= self.max_attempts:
                self.game_over = True
                self.won = False
                self.game_over_scale = 0.1
                self.guesses.append((guess_num, "high" if guess_num > self.number else "low"))
                # Add gray particles for losing
                for _ in range(20):
                    particle = Particle(random.randint(0, WIDTH), 0, (50, 50, 50))
                    self.particles.append(particle)
            elif guess_num < self.number:
                self.current_min = guess_num + 1
                self.feedback = f"{guess_num} is too low! Go higher."
                self.feedback_scale = 0.1
                self.guesses.append((guess_num, "low"))
            else:
                self.current_max = guess_num - 1
                self.feedback = f"{guess_num} is too high! Go lower."
                self.feedback_scale = 0.1
                self.guesses.append((guess_num, "high"))

            self.guess = ""

        except ValueError:
            self.feedback = "Please enter a valid number"
            self.feedback_scale = 0.1

def draw_text(text, position, color=TEXT_COLOR):
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def main():
    game = NumberGuesser()
    input_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 50, 200, 40)

    running = True
    while running:
        screen.fill(BG_COLOR)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif not game.game_over:
                    game.handle_input(event)
                elif event.key == pygame.K_SPACE:
                    game.reset_game()

        # Update particles
        for particle in game.particles:
            particle.update()
        game.particles = [p for p in game.particles if p.y < HEIGHT]

        # Draw particles
        for particle in game.particles:
            particle.draw()

        # Draw game title
        draw_text("Guess the Number Game", (WIDTH//2 - 120, 50), HIGHLIGHT_COLOR)
        
        # Draw current range
        draw_text(f"Range: {game.current_min} - {game.current_max}", 
                 (WIDTH//2 - 60, 150))
        
        # Draw attempts counter
        draw_text(f"Attempts: {game.attempts}/{game.max_attempts}", 
                 (WIDTH//2 - 60, 200))
        
        # Draw previous guesses
        for i, (guess, status) in enumerate(game.guesses):
            if status == "low":
                color = (0, 0, 255)  # Blue for too low
            elif status == "high":
                color = (255, 0, 0)  # Red for too high
            else:
                color = (0, 255, 0)  # Green for correct
            draw_text(f"{guess}", (50, 100 + i * 30), color)
        
        # Draw input box with border and cursor
        if game.game_over:
            pygame.draw.rect(screen, GRAY_COLOR, input_rect)
        else:
            pygame.draw.rect(screen, INPUT_COLOR, input_rect)
            pygame.draw.rect(screen, HIGHLIGHT_COLOR, input_rect, 2)  # Highlight border
            # Blinking cursor
            current_time = pygame.time.get_ticks()
            if current_time - game.cursor_timer > 500:
                game.cursor_visible = not game.cursor_visible
                game.cursor_timer = current_time
            if game.cursor_visible:
                text_surface = font.render(game.guess, True, TEXT_COLOR)
                cursor_x = input_rect.x + 10 + text_surface.get_width()
                pygame.draw.line(screen, TEXT_COLOR, (cursor_x, input_rect.y + 10), 
                                (cursor_x, input_rect.y + 30), 2)
        draw_text(game.guess, (input_rect.x + 10, input_rect.y + 10))
        
        # Update animation scales
        if game.feedback_scale < 1.0:
            game.feedback_scale += 0.1
            if game.feedback_scale > 1.0:
                game.feedback_scale = 1.0
        if game.game_over and game.game_over_scale < 1.0:
            game.game_over_scale += 0.1
            if game.game_over_scale > 1.0:
                game.game_over_scale = 1.0
        
        # Draw feedback message with scaling animation
        if game.feedback:
            feedback_surface = font.render(game.feedback, True, TEXT_COLOR)
            scaled_width = int(feedback_surface.get_width() * game.feedback_scale)
            scaled_height = int(feedback_surface.get_height() * game.feedback_scale)
            scaled_surface = pygame.transform.scale(feedback_surface, (scaled_width, scaled_height))
            center_x = WIDTH // 2
            center_y = HEIGHT - 150
            pos_x = center_x - scaled_width // 2
            pos_y = center_y - scaled_height // 2
            screen.blit(scaled_surface, (pos_x, pos_y))
        
        # Draw game over message with scaling animation
        if game.game_over:
            if game.won:
                message = f"Congratulations! You won in {game.attempts} attempts!"
                color = HIGHLIGHT_COLOR
            else:
                message = f"Game Over! The number was {game.number}"
                color = (255, 50, 50)
            game_over_surface = font.render(message, True, color)
            scaled_width = int(game_over_surface.get_width() * game.game_over_scale)
            scaled_height = int(game_over_surface.get_height() * game.game_over_scale)
            scaled_surface = pygame.transform.scale(game_over_surface, (scaled_width, scaled_height))
            center_x = WIDTH // 2
            center_y = HEIGHT - 100
            pos_x = center_x - scaled_width // 2
            pos_y = center_y - scaled_height // 2
            screen.blit(scaled_surface, (pos_x, pos_y))
            
            # Draw restart message
            restart_surface = font.render("Press SPACE to play again", True, TEXT_COLOR)
            screen.blit(restart_surface, (WIDTH//2 - restart_surface.get_width()//2, HEIGHT - 50))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
