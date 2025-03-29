import pygame
import sys

pygame.init()

# Game constants
WIDTH, HEIGHT = 540, 600
CELL_SIZE = WIDTH // 9
GRID_ORIGIN = 0
FONT_SIZE = 40

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sudoku")
font = pygame.font.Font(None, FONT_SIZE)

# Sudoku puzzle setup
initial_grid = [
    [5, 3, 0, 0, 7, 0, 0, 0, 0],
    [6, 0, 0, 1, 9, 5, 0, 0, 0],
    [0, 9, 8, 0, 0, 0, 0, 6, 0],
    [8, 0, 0, 0, 6, 0, 0, 0, 3],
    [4, 0, 0, 8, 0, 3, 0, 0, 1],
    [7, 0, 0, 0, 2, 0, 0, 0, 6],
    [0, 6, 0, 0, 0, 0, 2, 8, 0],
    [0, 0, 0, 4, 1, 9, 0, 0, 5],
    [0, 0, 0, 0, 8, 0, 0, 7, 9]
]

working_grid = [row[:] for row in initial_grid]
selected = None
victory = False

def draw_grid():
    """Draw the Sudoku grid lines"""
    screen.fill(WHITE)
    for i in range(10):
        line_width = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, 
                         (i*CELL_SIZE, GRID_ORIGIN), (i*CELL_SIZE, WIDTH), line_width)
        pygame.draw.line(screen, BLACK,
                         (GRID_ORIGIN, i*CELL_SIZE), (WIDTH, i*CELL_SIZE), line_width)

def draw_numbers():
    """Draw the numbers on the grid"""
    for row in range(9):
        for col in range(9):
            num = working_grid[row][col]
            if num != 0:
                color = GRAY if initial_grid[row][col] != 0 else BLACK
                text = font.render(str(num), True, color)
                x = col * CELL_SIZE + (CELL_SIZE - text.get_width()) // 2
                y = row * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
                screen.blit(text, (x, y))

def draw_selection():
    """Highlight selected cell"""
    if selected:
        row, col = selected
        pygame.draw.rect(screen, LIGHT_BLUE, 
                        (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

def can_place(grid, row, col, num):
    """Check if a number can be placed in a cell"""
    if num in grid[row]:
        return False
    for i in range(9):
        if grid[i][col] == num:
            return False
    start_row, start_col = 3*(row//3), 3*(col//3)
    for i in range(start_row, start_row+3):
        for j in range(start_col, start_col+3):
            if grid[i][j] == num:
                return False
    return True

def is_solved():
    """Check if the puzzle is completely solved"""
    for row in working_grid:
        if 0 in row:
            return False
    for row in range(9):
        for col in range(9):
            num = working_grid[row][col]
            if not can_place(working_grid, row, col, num):
                return False
    return True

def show_victory():
    """Display victory message"""
    text = font.render("Congratulations! You won!", True, GREEN)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT - 60))

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            if initial_grid[row][col] == 0:
                selected = (row, col)
            else:
                selected = None
        
        if event.type == pygame.KEYDOWN:
            if selected and not victory:
                row, col = selected
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    working_grid[row][col] = 0
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_0
                    if can_place(working_grid, row, col, num):
                        working_grid[row][col] = num
                    else:
                        # Flash red for invalid input
                        screen.fill(RED, 
                                   (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                        pygame.display.update()
                        pygame.time.wait(100)
                
                # Check if puzzle is solved
                victory = is_solved()

    # Draw all elements
    draw_grid()
    draw_numbers()
    draw_selection()
    if victory:
        show_victory()
    
    pygame.display.update()

pygame.quit()
sys.exit()
