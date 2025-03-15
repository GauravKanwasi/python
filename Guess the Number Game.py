import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Game constants
WIDTH, HEIGHT = 800, 600
BG_COLOR = (28, 28, 28)
TEXT_COLOR = (255, 255, 255)
INPUT_COLOR = (40, 40, 40)
HIGHLIGHT_COLOR = (0, 122, 204)

# Set up the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Guess the Number Game")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 32)

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
                return

            self.attempts += 1

            if guess_num == self.number:
                self.game_over = True
                self.won = True
            elif self.attempts >= self.max_attempts:
                self.game_over = True
                self.won = False
            elif guess_num < self.number:
                self.current_min = guess_num + 1
                self.feedback = f"{guess_num} is too low! Go higher."
            else:
                self.current_max = guess_num - 1
                self.feedback = f"{guess_num} is too high! Go lower."

            self.guess = ""

        except ValueError:
            self.feedback = "Please enter a valid number"

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

        # Draw game title
        draw_text("Guess the Number Game", (WIDTH//2 - 120, 50), HIGHLIGHT_COLOR)
        
        # Draw current range
        draw_text(f"Range: {game.current_min} - {game.current_max}", 
                 (WIDTH//2 - 60, 150))
        
        # Draw attempts counter
        draw_text(f"Attempts: {game.attempts}/{game.max_attempts}", 
                 (WIDTH//2 - 60, 200))
        
        # Draw input box
        pygame.draw.rect(screen, INPUT_COLOR, input_rect)
        draw_text(game.guess, (input_rect.x + 10, input_rect.y + 10))
        
        # Draw feedback message
        if game.feedback:
            draw_text(game.feedback, (WIDTH//2 - 200, HEIGHT - 150))
        
        # Draw game over message
        if game.game_over:
            if game.won:
                draw_text(f"Congratulations! You won in {game.attempts} attempts!", 
                         (WIDTH//2 - 200, HEIGHT - 100), HIGHLIGHT_COLOR)
            else:
                draw_text(f"Game Over! The number was {game.number}", 
                         (WIDTH//2 - 150, HEIGHT - 100), (255, 50, 50))
            draw_text("Press SPACE to play again", 
                     (WIDTH//2 - 120, HEIGHT - 50))

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
