import pygame
import random

# Initialize pygame
pygame.init()

# Screen dimensions
width, height = 800, 600
screen = pygame.display.set_mode((width, height))

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Ball settings
ball_radius = 20
ball_x = random.randint(ball_radius, width - ball_radius)
ball_y = random.randint(ball_radius, height - ball_radius)
ball_dx = random.choice([-5, 5])
ball_dy = random.choice([-5, 5])

# Game loop
running = True
clock = pygame.time.Clock()

while running:
    screen.fill(WHITE)  # Fill screen with white color
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Update ball position
    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collision with screen borders
    if ball_x <= ball_radius or ball_x >= width - ball_radius:
        ball_dx = -ball_dx
    if ball_y <= ball_radius or ball_y >= height - ball_radius:
        ball_dy = -ball_dy

    # Draw ball
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)

    # Update screen
    pygame.display.flip()
    
    # Frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
