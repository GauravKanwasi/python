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
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)

# Font for score
font = pygame.font.SysFont(None, 36)

# Ball settings
ball_radius = 20
ball_x = random.randint(ball_radius, width - ball_radius)
ball_y = random.randint(ball_radius, height - ball_radius)
ball_dx = random.choice([-5, 5])
ball_dy = random.choice([-5, 5])

# Paddle settings
paddle_width = 100
paddle_height = 20
paddle_x = width // 2 - paddle_width // 2
paddle_y = height - paddle_height - 10
paddle_dx = 0
paddle_speed = 8

# Game variables
score = 0
ball_speed_increase = 1.05  # Speed increase factor

# Game loop
running = True
clock = pygame.time.Clock()

# Add background music
pygame.mixer.music.load("background_music.mp3")  # Replace with a valid file path
pygame.mixer.music.play(-1, 0.0)  # Loop music indefinitely

# Add sound effects
bounce_sound = pygame.mixer.Sound("bounce.wav")  # Replace with a valid file path
score_sound = pygame.mixer.Sound("score.wav")  # Replace with a valid file path

while running:
    screen.fill(WHITE)  # Fill screen with white color
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                paddle_dx = -paddle_speed
            elif event.key == pygame.K_RIGHT:
                paddle_dx = paddle_speed
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                paddle_dx = 0

    # Update paddle position
    paddle_x += paddle_dx
    if paddle_x < 0:
        paddle_x = 0
    elif paddle_x > width - paddle_width:
        paddle_x = width - paddle_width

    # Update ball position
    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collision with screen borders
    if ball_x <= ball_radius or ball_x >= width - ball_radius:
        ball_dx = -ball_dx
        bounce_sound.play()

    if ball_y <= ball_radius:
        ball_dy = -ball_dy
        bounce_sound.play()

    # Ball collision with the paddle
    if (paddle_y < ball_y + ball_radius and paddle_y + paddle_height > ball_y - ball_radius and
            paddle_x < ball_x < paddle_x + paddle_width):
        ball_dy = -ball_dy
        score += 1
        ball_dx *= ball_speed_increase  # Increase speed after bouncing on paddle
        ball_dy *= ball_speed_increase
        bounce_sound.play()

    # Ball goes past the paddle (game over)
    if ball_y > height:
        print(f"Game Over! Final Score: {score}")
        running = False

    # Draw ball
    pygame.draw.circle(screen, RED, (ball_x, ball_y), ball_radius)

    # Draw paddle
    pygame.draw.rect(screen, BLUE, (paddle_x, paddle_y, paddle_width, paddle_height))

    # Draw the score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    # Draw a border
    pygame.draw.rect(screen, BLACK, (0, 0, width, height), 5)

    # Update screen
    pygame.display.flip()

    # Frame rate
    clock.tick(60)

# Quit pygame
pygame.quit()
