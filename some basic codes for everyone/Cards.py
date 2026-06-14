import pygame
import random
import time

# Initialize pygame
pygame.init()

# Set up the display
width, height = 600, 800
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Random Card Picker')
clock = pygame.time.Clock()

# Card ranks and suits - Full deck
ranks = ['Ace', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

# Suit symbols and colors
suit_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠'}
suit_colors = {'Hearts': (220, 20, 60), 'Diamonds': (220, 20, 60), 'Clubs': (0, 0, 0), 'Spades': (0, 0, 0)}  # Red for red suits, black for black suits

# Game variables
cards_picked = 0
current_card = None
is_animating = False

# Function to draw the card on the screen
def draw_card(rank, suit, x=200, y=200):
    # Set card dimensions and background color
    card_width, card_height = 200, 300
    card_color = (255, 255, 255)  # White background for the card
    border_color = suit_colors[suit]  # Colored border based on suit
    
    # Draw the card rectangle
    pygame.draw.rect(screen, card_color, (x, y, card_width, card_height))
    pygame.draw.rect(screen, border_color, (x, y, card_width, card_height), 8)  # Thicker, colored border
    
    # Draw corner symbols (top-left and bottom-right)
    small_font = pygame.font.SysFont("Arial", 30, bold=True)
    symbol_text = small_font.render(suit_symbols[suit], True, border_color)
    screen.blit(symbol_text, (x + 10, y + 10))  # Top-left corner
    
    # Rotate and place bottom-right (upside down)
    rotated_symbol = pygame.transform.rotate(symbol_text, 180)
    screen.blit(rotated_symbol, (x + card_width - 40, y + card_height - 40))  # Bottom-right corner
    
    # Draw the rank and suit text on the card (centered)
    font = pygame.font.SysFont("Arial", 48, bold=True)
    rank_text = font.render(rank, True, border_color)  # Colored text matching suit
    
    # Calculate center position for rank
    rank_rect = rank_text.get_rect(center=(x + card_width // 2, y + card_height // 2 - 30))
    screen.blit(rank_text, rank_rect)
    
    # Draw the suit text below the rank
    suit_font = pygame.font.SysFont("Arial", 32)
    suit_text = suit_font.render(suit, True, border_color)
    suit_rect = suit_text.get_rect(center=(x + card_width // 2, y + card_height // 2 + 40))
    screen.blit(suit_text, suit_rect)

# Function to draw a back of card (for flipping animation)
def draw_card_back(x=200, y=200):
    # Set card dimensions
    card_width, card_height = 200, 300
    back_color = (0, 100, 150)  # Dark blue back
    border_color = (255, 255, 255)  # White border
    
    # Draw the card rectangle
    pygame.draw.rect(screen, back_color, (x, y, card_width, card_height))
    pygame.draw.rect(screen, border_color, (x, y, card_width, card_height), 5)
    
    # Draw a pattern on the back
    for i in range(10, 20, 3):
        pygame.draw.line(screen, (100, 150, 200), (x + 20 + i, y + 20), (x + 20 + i, y + card_height - 20), 2)

# Function to display instructions and info
def draw_ui():
    # Draw title
    title_font = pygame.font.SysFont("Arial", 48, bold=True)
    title_text = title_font.render("Card Picker", True, (255, 255, 255))
    title_rect = title_text.get_rect(center=(width // 2, 40))
    screen.blit(title_text, title_rect)
    
    # Draw instructions
    instruction_font = pygame.font.SysFont("Arial", 24)
    instruction_text = instruction_font.render("Press SPACE to pick a random card", True, (255, 255, 255))
    instruction_rect = instruction_text.get_rect(center=(width // 2, 100))
    screen.blit(instruction_text, instruction_rect)
    
    # Draw cards picked counter
    counter_text = instruction_font.render(f"Cards picked: {cards_picked}", True, (255, 255, 200))
    screen.blit(counter_text, (20, height - 50))
    
    # Draw reset instructions
    reset_font = pygame.font.SysFont("Arial", 18)
    reset_text = reset_font.render("Press R to reset counter | Press Q to quit", True, (200, 200, 200))
    screen.blit(reset_text, (20, height - 25))

# Function to animate and display the card
def display_card(rank, suit):
    global is_animating
    is_animating = True
    
    # Card flipping animation - flip from back to front
    for i in range(15):
        screen.fill((0, 128, 0))  # Set the background color (green like a card table)
        draw_ui()  # Draw UI elements
        
        # Calculate flip progress
        flip_progress = i / 15
        
        # Draw card with flipping effect (opacity change to simulate flip)
        if flip_progress < 0.5:
            # Flipping to back
            alpha = int(255 * (1 - flip_progress * 2))
            draw_card_back()
        else:
            # Flipping to front
            alpha = int(255 * ((flip_progress - 0.5) * 2))
            draw_card(rank, suit)
        
        pygame.display.update()
        clock.tick(30)  # 30 FPS for smooth animation
    
    # Ensure final card is displayed
    screen.fill((0, 128, 0))
    draw_ui()
    draw_card(rank, suit)
    pygame.display.update()
    
    # Pause to display the final card
    time.sleep(1.5)
    
    is_animating = False

# Main game loop
running = True
while running:
    screen.fill((0, 128, 0))  # Set the background to green (like a card table)
    
    # Draw UI when not animating
    if not is_animating:
        draw_ui()
        if current_card:
            draw_card(current_card[0], current_card[1])
    
    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not is_animating:
                # Choose a random rank and suit from the deck
                random_rank = random.choice(ranks)
                random_suit = random.choice(suits)
                current_card = (random_rank, random_suit)
                
                # Increment counter
                cards_picked += 1
                
                # Display the random card with animation
                display_card(random_rank, random_suit)
            
            elif event.key == pygame.K_r:
                # Reset the counter
                cards_picked = 0
                current_card = None
            
            elif event.key == pygame.K_q:
                # Quit the application
                running = False
    
    # Update the screen
    pygame.display.update()
    clock.tick(60)  # 60 FPS for smooth gameplay

# Clean up and close the pygame window
pygame.quit()
