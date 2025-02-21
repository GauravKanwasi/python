import pygame
import random
import time

# Initialize pygame
pygame.init()

# Set up the display
width, height = 400, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Random Card Picker')

# Card ranks and suits
ranks = ['Ace', '2', '3', '4', '5']
suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

# Function to draw the card on the screen
def draw_card(rank, suit):
    # Set card dimensions and background color
    card_width, card_height = 200, 300
    card_color = (255, 255, 255)  # White background for the card
    border_color = (0, 0, 0)  # Black border for the card
    
    # Draw the card
    pygame.draw.rect(screen, card_color, (100, 150, card_width, card_height))
    pygame.draw.rect(screen, border_color, (100, 150, card_width, card_height), 5)  # Border around card
    
    # Draw the rank and suit text on the card
    font = pygame.font.SysFont("Arial", 40)
    rank_text = font.render(rank, True, (0, 0, 0))  # Black text for rank
    suit_text = font.render(suit, True, (0, 0, 0))  # Black text for suit
    
    # Render rank text at the top left
    screen.blit(rank_text, (120, 170))
    
    # Render suit text at the bottom right
    screen.blit(suit_text, (120, 230))

# Function to animate and display the card
def display_card(rank, suit):
    # Card flipping animation
    for i in range(10):
        screen.fill((0, 128, 0))  # Set the background color (green like a card table)
        draw_card(rank, suit)  # Draw the card
        pygame.display.update()
        time.sleep(0.1)  # Delay for animation effect
        if i < 5:
            pygame.draw.rect(screen, (0, 0, 0), (100, 150, 200, 300), 5)  # Simulate flipping effect
        pygame.display.update()
    
    # Pause for a moment to display the final card
    time.sleep(1)

# Main game loop
running = True
while running:
    screen.fill((0, 128, 0))  # Set the background to green (like a card table)

    # Check for events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                # Choose a random rank and suit from the deck
                random_rank = random.choice(ranks)
                random_suit = random.choice(suits)
                
                # Display the random card with animation
                display_card(random_rank, random_suit)

    # Update the screen
    pygame.display.update()

# Clean up and close the pygame window
pygame.quit()
