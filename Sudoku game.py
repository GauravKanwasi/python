import pygame
import sys
import random
import time

pygame.init()

# Game constants
WIDTH, HEIGHT = 540, 700
CELL_SIZE = WIDTH // 9
GRID_ORIGIN = 0
FONT_SIZE = 40
BUTTON_HEIGHT = 50
BUTTON_MARGIN = 20

# Color definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
DARK_BLUE = (0, 0, 139)
LIGHT_GRAY = (200, 200, 200)

# Initialize display
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Enhanced Sudoku")
font = pygame.font.Font(None, FONT_SIZE)
small_font = pygame.font.Font(None, FONT_SIZE // 2)
button_font = pygame.font.Font(None, 36)

# Game states
MENU = 0
PLAYING = 1
PAUSED = 2
game_state = MENU

# Difficulty levels
EASY = 35  # 35 cells filled
MEDIUM = 30  # 30 cells filled
HARD = 25  # 25 cells filled
current_difficulty = MEDIUM

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
solution_grid = None
notes = [[set() for _ in range(9)] for _ in range(9)]  # For pencil marks
selected = None
victory = False
game_timer = 0
start_time = 0
mistakes = 0
MAX_MISTAKES = 3
note_mode = False
hint_count = 3

class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.action = action
        self.hovered = False

    def draw(self):
        color = self.hover_color if self.hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=10)
        pygame.draw.rect(screen, BLACK, self.rect, 2, border_radius=10)
        
        text_surf = button_font.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

# Create buttons
button_width = WIDTH // 3
start_easy = Button(WIDTH//2 - button_width//2, HEIGHT//2 - 80, button_width, BUTTON_HEIGHT, "Easy", LIGHT_GRAY, LIGHT_BLUE, lambda: set_difficulty(EASY))
start_medium = Button(WIDTH//2 - button_width//2, HEIGHT//2, button_width, BUTTON_HEIGHT, "Medium", LIGHT_GRAY, LIGHT_BLUE, lambda: set_difficulty(MEDIUM))
start_hard = Button(WIDTH//2 - button_width//2, HEIGHT//2 + 80, button_width, BUTTON_HEIGHT, "Hard", LIGHT_GRAY, LIGHT_BLUE, lambda: set_difficulty(HARD))

restart_button = Button(30, HEIGHT - BUTTON_HEIGHT - 20, 120, BUTTON_HEIGHT, "Restart", LIGHT_GRAY, LIGHT_BLUE, restart_game)
menu_button = Button(WIDTH - 150, HEIGHT - BUTTON_HEIGHT - 20, 120, BUTTON_HEIGHT, "Menu", LIGHT_GRAY, LIGHT_BLUE, go_to_menu)
note_button = Button(WIDTH//2 - 60, HEIGHT - BUTTON_HEIGHT - 20, 120, BUTTON_HEIGHT, "Notes: OFF", LIGHT_GRAY, YELLOW, toggle_notes)
hint_button = Button(WIDTH//2 - 150, HEIGHT - BUTTON_HEIGHT - 80, 120, BUTTON_HEIGHT, "Hint (3)", LIGHT_GRAY, LIGHT_BLUE, use_hint)
solve_button = Button(WIDTH//2 + 30, HEIGHT - BUTTON_HEIGHT - 80, 120, BUTTON_HEIGHT, "Solve", LIGHT_GRAY, LIGHT_BLUE, solve_puzzle)

def is_valid_sudoku(grid):
    """Check if the current grid has any obvious contradictions"""
    # Check rows
    for row in grid:
        seen = set()
        for num in row:
            if num != 0 and num in seen:
                return False
            seen.add(num)
    
    # Check columns
    for col in range(9):
        seen = set()
        for row in range(9):
            num = grid[row][col]
            if num != 0 and num in seen:
                return False
            seen.add(num)
    
    # Check 3x3 boxes
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            seen = set()
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    num = grid[row][col]
                    if num != 0 and num in seen:
                        return False
                    seen.add(num)
    
    return True

def solve_sudoku(grid):
    """Solve the Sudoku puzzle using backtracking"""
    empty = find_empty(grid)
    if not empty:
        return True
    
    row, col = empty
    
    # Randomly try numbers 1-9
    nums = list(range(1, 10))
    random.shuffle(nums)
    
    for num in nums:
        if can_place(grid, row, col, num):
            grid[row][col] = num
            
            if solve_sudoku(grid):
                return True
                
            grid[row][col] = 0
    
    return False

def find_empty(grid):
    """Find an empty cell in the grid"""
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)
    return None

def generate_puzzle(difficulty):
    """Generate a new Sudoku puzzle with specified difficulty"""
    # Start with an empty grid
    grid = [[0 for _ in range(9)] for _ in range(9)]
    
    # Solve the empty grid to get a full solution
    solve_sudoku(grid)
    
    # Store the full solution
    solution = [row[:] for row in grid]
    
    # Remove cells based on difficulty
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    
    # Keep only 'difficulty' number of cells
    cells_to_keep = difficulty
    for i, j in cells[cells_to_keep:]:
        grid[i][j] = 0
    
    return grid, solution

def set_difficulty(difficulty):
    """Set the game difficulty and start a new game"""
    global current_difficulty, initial_grid, working_grid, solution_grid
    global selected, victory, game_state, start_time, mistakes
    
    current_difficulty = difficulty
    initial_grid, solution_grid = generate_puzzle(difficulty)
    working_grid = [row[:] for row in initial_grid]
    notes = [[set() for _ in range(9)] for _ in range(9)]
    selected = None
    victory = False
    game_state = PLAYING
    start_time = time.time()
    mistakes = 0

def restart_game():
    """Restart the current game"""
    global working_grid, selected, victory, start_time, mistakes, notes, hint_count
    working_grid = [row[:] for row in initial_grid]
    notes = [[set() for _ in range(9)] for _ in range(9)]
    selected = None
    victory = False
    start_time = time.time()
    mistakes = 0
    hint_count = 3
    update_hint_button()

def go_to_menu():
    """Return to the main menu"""
    global game_state
    game_state = MENU

def toggle_notes():
    """Toggle note mode on/off"""
    global note_mode
    note_mode = not note_mode
    note_button.text = "Notes: ON" if note_mode else "Notes: OFF"

def use_hint():
    """Provide a hint by filling in a random empty cell"""
    global hint_count, working_grid
    
    if hint_count <= 0 or victory:
        return
    
    # Find all empty cells
    empty_cells = []
    for row in range(9):
        for col in range(9):
            if working_grid[row][col] == 0:
                empty_cells.append((row, col))
    
    if empty_cells:
        # Choose a random empty cell
        row, col = random.choice(empty_cells)
        working_grid[row][col] = solution_grid[row][col]
        hint_count -= 1
        update_hint_button()
        
        # Check if this hint completes the puzzle
        victory = is_solved()

def update_hint_button():
    """Update the hint button text"""
    hint_button.text = f"Hint ({hint_count})"

def solve_puzzle():
    """Solve the entire puzzle"""
    global working_grid, victory
    working_grid = [row[:] for row in solution_grid]
    victory = True

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
    """Draw the numbers and notes on the grid"""
    for row in range(9):
        for col in range(9):
            num = working_grid[row][col]
            if num != 0:
                is_original = initial_grid[row][col] != 0
                is_correct = solution_grid[row][col] == num if solution_grid else True
                
                color = GRAY if is_original else (GREEN if is_correct else RED)
                text = font.render(str(num), True, color)
                x = col * CELL_SIZE + (CELL_SIZE - text.get_width()) // 2
                y = row * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
                screen.blit(text, (x, y))
            else:
                # Draw notes
                cell_notes = notes[row][col]
                if cell_notes:
                    note_size = CELL_SIZE // 3
                    for note_num in range(1, 10):
                        if note_num in cell_notes:
                            note_text = small_font.render(str(note_num), True, DARK_BLUE)
                            note_x = col * CELL_SIZE + ((note_num-1) % 3) * note_size + 5
                            note_y = row * CELL_SIZE + ((note_num-1) // 3) * note_size + 5
                            screen.blit(note_text, (note_x, note_y))

def draw_selection():
    """Highlight selected cell"""
    if selected:
        row, col = selected
        pygame.draw.rect(screen, LIGHT_BLUE if not note_mode else YELLOW, 
                        (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

def draw_ui():
    """Draw UI elements like timer, mistakes counter, and buttons"""
    # Timer
    if game_state == PLAYING:
        current_time = time.time() - start_time
    elif game_state == MENU:
        current_time = 0
    else:
        current_time = game_timer
        
    time_text = font.render(f"Time: {int(current_time//60):02d}:{int(current_time%60):02d}", True, BLACK)
    screen.blit(time_text, (20, WIDTH + 20))
    
    # Mistakes counter
    mistake_text = font.render(f"Mistakes: {mistakes}/{MAX_MISTAKES}", True, 
                              RED if mistakes >= MAX_MISTAKES else BLACK)
    screen.blit(mistake_text, (WIDTH - 220, WIDTH + 20))
    
    # Draw buttons
    if game_state == PLAYING:
        restart_button.draw()
        menu_button.draw()
        note_button.draw()
        hint_button.draw()
        solve_button.draw()

def draw_menu():
    """Draw the main menu"""
    screen.fill(WHITE)
    
    # Title
    title_text = font.render("SUDOKU", True, BLACK)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
    
    # Subtitle
    subtitle_text = small_font.render("Select difficulty:", True, BLACK)
    screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//3))
    
    # Difficulty buttons
    start_easy.draw()
    start_medium.draw()
    start_hard.draw()

def can_place(grid, row, col, num):
    """Check if a number can be placed in a cell"""
    # Check row
    for x in range(9):
        if grid[row][x] == num:
            return False
            
    # Check column
    for x in range(9):
        if grid[x][col] == num:
            return False
    
    # Check 3x3 box
    start_row, start_col = 3*(row//3), 3*(col//3)
    for i in range(start_row, start_row+3):
        for j in range(start_col, start_col+3):
            if grid[i][j] == num:
                return False
                
    return True

def is_solved():
    """Check if the puzzle is completely solved"""
    for row in range(9):
        for col in range(9):
            if working_grid[row][col] == 0:
                return False
                
    return is_valid_sudoku(working_grid)

def show_victory():
    """Display victory message"""
    text = font.render("Congratulations! You won!", True, GREEN)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, WIDTH + 80))

def show_game_over():
    """Display game over message"""
    text = font.render("Game Over! Too many mistakes.", True, RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, WIDTH + 80))

# Generate initial puzzle and solution
initial_grid, solution_grid = generate_puzzle(current_difficulty)
working_grid = [row[:] for row in initial_grid]

# Main game loop
running = True
while running:
    mouse_pos = pygame.mouse.get_pos()
    
    if game_state == MENU:
        start_easy.update(mouse_pos)
        start_medium.update(mouse_pos)
        start_hard.update(mouse_pos)
    elif game_state == PLAYING:
        restart_button.update(mouse_pos)
        menu_button.update(mouse_pos)
        note_button.update(mouse_pos)
        hint_button.update(mouse_pos)
        solve_button.update(mouse_pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == MENU:
                if start_easy.is_clicked(mouse_pos):
                    start_easy.action()
                elif start_medium.is_clicked(mouse_pos):
                    start_medium.action()
                elif start_hard.is_clicked(mouse_pos):
                    start_hard.action()
            
            elif game_state == PLAYING:
                if mouse_pos[1] < WIDTH:  # Click on grid
                    col = mouse_pos[0] // CELL_SIZE
                    row = mouse_pos[1] // CELL_SIZE
                    if 0 <= row < 9 and 0 <= col < 9:
                        if initial_grid[row][col] == 0:
                            selected = (row, col)
                        else:
                            selected = None
                else:  # Click on UI
                    if restart_button.is_clicked(mouse_pos):
                        restart_game()
                    elif menu_button.is_clicked(mouse_pos):
                        go_to_menu()
                    elif note_button.is_clicked(mouse_pos):
                        toggle_notes()
                    elif hint_button.is_clicked(mouse_pos):
                        use_hint()
                    elif solve_button.is_clicked(mouse_pos):
                        solve_puzzle()
        
        elif event.type == pygame.KEYDOWN:
            if game_state == PLAYING and selected and not victory and mistakes < MAX_MISTAKES:
                row, col = selected
                
                if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                    working_grid[row][col] = 0
                    notes[row][col].clear()
                
                elif pygame.K_1 <= event.key <= pygame.K_9:
                    num = event.key - pygame.K_0
                    
                    if note_mode:
                        # Toggle note on/off
                        if num in notes[row][col]:
                            notes[row][col].remove(num)
                        else:
                            notes[row][col].add(num)
                    else:
                        # Place number
                        if solution_grid[row][col] == num:
                            working_grid[row][col] = num
                            # Clear pencil marks for this cell
                            notes[row][col].clear()
                            
                            # Clear pencil marks in row, column and box
                            for i in range(9):
                                # Remove from row
                                if num in notes[row][i]:
                                    notes[row][i].remove(num)
                                # Remove from column
                                if num in notes[i][col]:
                                    notes[i][col].remove(num)
                            
                            # Remove from box
                            start_row, start_col = 3*(row//3), 3*(col//3)
                            for i in range(start_row, start_row+3):
                                for j in range(start_col, start_col+3):
                                    if num in notes[i][j]:
                                        notes[i][j].remove(num)
                                        
                            # Check if puzzle is solved
                            victory = is_solved()
                        else:
                            # Flash red for invalid input
                            mistakes += 1
                            screen.fill(RED, 
                                      (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                            pygame.display.update()
                            pygame.time.wait(100)
    
    # Draw appropriate screen based on game state
    if game_state == MENU:
        draw_menu()
    elif game_state == PLAYING:
        draw_grid()
        draw_numbers()
        draw_selection()
        draw_ui()
        if victory:
            show_victory()
        elif mistakes >= MAX_MISTAKES:
            show_game_over()
    
    pygame.display.update()

pygame.quit()
sys.exit()
