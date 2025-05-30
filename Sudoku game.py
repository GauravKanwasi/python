import pygame
import sys
import random
import time
import copy

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
notes = [[set() for _ in range(9)] for _ in range(9)]
selected = None
victory = False
game_timer = 0
start_time = 0
mistakes = 0
MAX_MISTAKES = 3
note_mode = False
hint_count = 3
undo_stack = []
redo_stack = []

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
new_game_button = Button(WIDTH//2 - 60, HEIGHT - BUTTON_HEIGHT - 140, 120, BUTTON_HEIGHT, "New Game", LIGHT_GRAY, LIGHT_BLUE, lambda: set_difficulty(current_difficulty))

def set_difficulty(difficulty):
    global current_difficulty, initial_grid, working_grid, solution_grid, selected, victory, game_state, start_time, mistakes, notes, undo_stack, redo_stack
    current_difficulty = difficulty
    initial_grid, solution_grid = generate_puzzle(difficulty)
    working_grid = [row[:] for row in initial_grid]
    notes = [[set() for _ in range(9)] for _ in range(9)]
    selected = None
    victory = False
    game_state = PLAYING
    start_time = time.time()
    mistakes = 0
    undo_stack = []
    redo_stack = []

def restart_game():
    global working_grid, selected, victory, start_time, mistakes, notes, hint_count, undo_stack, redo_stack
    working_grid = [row[:] for row in initial_grid]
    notes = [[set() for _ in range(9)] for _ in range(9)]
    selected = None
    victory = False
    start_time = time.time()
    mistakes = 0
    hint_count = 3
    update_hint_button()
    undo_stack = []
    redo_stack = []

def go_to_menu():
    global game_state
    game_state = MENU

def toggle_notes():
    global note_mode
    note_mode = not note_mode
    note_button.text = "Notes: ON" if note_mode else "Notes: OFF"

def use_hint():
    global hint_count, working_grid
    if hint_count <= 0 or victory:
        return
    undo_stack.append((copy.deepcopy(working_grid), copy.deepcopy(notes)))
    empty_cells = [(row, col) for row in range(9) for col in range(9) if working_grid[row][col] == 0]
    if empty_cells:
        row, col = random.choice(empty_cells)
        working_grid[row][col] = solution_grid[row][col]
        hint_count -= 1
        update_hint_button()
        victory = is_solved()
        redo_stack.clear()

def update_hint_button():
    hint_button.text = f"Hint ({hint_count})"

def solve_puzzle():
    global working_grid, victory
    undo_stack.append((copy.deepcopy(working_grid), copy.deepcopy(notes)))
    working_grid = [row[:] for row in solution_grid]
    victory = is_solved()
    redo_stack.clear()

def draw_grid():
    screen.fill(WHITE)
    for i in range(10):
        line_width = 3 if i % 3 == 0 else 1
        pygame.draw.line(screen, BLACK, (i*CELL_SIZE, GRID_ORIGIN), (i*CELL_SIZE, WIDTH), line_width)
        pygame.draw.line(screen, BLACK, (GRID_ORIGIN, i*CELL_SIZE), (WIDTH, i*CELL_SIZE), line_width)

def get_conflicts(grid):
    conflicts = set()
    # Check rows
    for row in range(9):
        num_count = {}
        for col in range(9):
            num = grid[row][col]
            if num != 0:
                if num in num_count:
                    conflicts.add((row, col))
                    conflicts.add(num_count[num])
                else:
                    num_count[num] = (row, col)
    # Check columns
    for col in range(9):
        num_count = {}
        for row in range(9):
            num = grid[row][col]
            if num != 0:
                if num in num_count:
                    conflicts.add((row, col))
                    conflicts.add(num_count[num])
                else:
                    num_count[num] = (row, col)
    # Check boxes
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            num_count = {}
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    num = grid[row][col]
                    if num != 0:
                        if num in num_count:
                            conflicts.add((row, col))
                            conflicts.add(num_count[num])
                        else:
                            num_count[num] = (row, col)
    return conflicts

def draw_numbers():
    conflicts = get_conflicts(working_grid)
    for row in range(9):
        for col in range(9):
            if (row, col) in conflicts:
                pygame.draw.rect(screen, RED, (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)
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
    if selected:
        row, col = selected
        pygame.draw.rect(screen, LIGHT_BLUE if not note_mode else YELLOW, 
                         (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE), 3)

def draw_ui():
    if game_state == PLAYING:
        current_time = time.time() - start_time
    elif game_state == MENU:
        current_time = 0
    else:
        current_time = game_timer
        
    time_text = font.render(f"Time: {int(current_time//60):02d}:{int(current_time%60):02d}", True, BLACK)
    screen.blit(time_text, (20, WIDTH + 20))
    
    difficulty_text = font.render(f"Difficulty: {'Easy' if current_difficulty == EASY else 'Medium' if current_difficulty == MEDIUM else 'Hard'}", True, BLACK)
    screen.blit(difficulty_text, (20, WIDTH + 60))
    
    mistake_text = font.render(f"Mistakes: {mistakes}/{MAX_MISTAKES}", True, 
                               RED if mistakes >= MAX_MISTAKES else BLACK)
    screen.blit(mistake_text, (WIDTH - 220, WIDTH + 20))
    
    if game_state == PLAYING:
        restart_button.draw()
        menu_button.draw()
        note_button.draw()
        hint_button.draw()
        solve_button.draw()
        new_game_button.draw()

def draw_menu():
    screen.fill(WHITE)
    title_text = font.render("SUDOKU", True, BLACK)
    screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))
    subtitle_text = small_font.render("Select difficulty:", True, BLACK)
    screen.blit(subtitle_text, (WIDTH//2 - subtitle_text.get_width()//2, HEIGHT//3))
    start_easy.draw()
    start_medium.draw()
    start_hard.draw()

def can_place(grid, row, col, num):
    for x in range(9):
        if grid[row][x] == num or grid[x][col] == num:
            return False
    start_row, start_col = 3*(row//3), 3*(col//3)
    for i in range(start_row, start_row+3):
        for j in range(start_col, start_col+3):
            if grid[i][j] == num:
                return False
    return True

def solve_sudoku(grid):
    empty = find_empty(grid)
    if not empty:
        return True
    row, col = empty
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
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)
    return None

def generate_puzzle(difficulty):
    grid = [[0 for _ in range(9)] for _ in range(9)]
    solve_sudoku(grid)
    solution = [row[:] for row in grid]
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    cells_to_keep = difficulty
    for i, j in cells[cells_to_keep:]:
        grid[i][j] = 0
    return grid, solution

def is_solved():
    for row in range(9):
        for col in range(9):
            if working_grid[row][col] == 0:
                return False
    return True

def show_victory():
    text = font.render("Congratulations! You won!", True, GREEN)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, WIDTH + 80))

def show_game_over():
    text = font.render("Game Over! Too many mistakes.", True, RED)
    screen.blit(text, (WIDTH//2 - text.get_width()//2, WIDTH + 80))

# Generate initial puzzle
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
        new_game_button.update(mouse_pos)
    
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
                if mouse_pos[1] < WIDTH:
                    col = mouse_pos[0] // CELL_SIZE
                    row = mouse_pos[1] // CELL_SIZE
                    if 0 <= row < 9 and 0 <= col < 9:
                        if initial_grid[row][col] == 0:
                            selected = (row, col)
                        else:
                            selected = None
                else:
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
                    elif new_game_button.is_clicked(mouse_pos):
                        new_game_button.action()
            elif game_state == PAUSED:
                if menu_button.is_clicked(mouse_pos):
                    go_to_menu()
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                if game_state == PLAYING:
                    game_state = PAUSED
                    game_timer = time.time() - start_time
                elif game_state == PAUSED:
                    game_state = PLAYING
                    start_time = time.time() - game_timer
            elif game_state == PLAYING and not victory and mistakes < MAX_MISTAKES:
                if selected:
                    row, col = selected
                    if event.key == pygame.K_BACKSPACE or event.key == pygame.K_DELETE:
                        undo_stack.append((copy.deepcopy(working_grid), copy.deepcopy(notes)))
                        working_grid[row][col] = 0
                        notes[row][col].clear()
                        redo_stack.clear()
                    elif event.key in [pygame.K_1, pygame.K_KP1]: num = 1
                    elif event.key in [pygame.K_2, pygame.K_KP2]: num = 2
                    elif event.key in [pygame.K_3, pygame.K_KP3]: num = 3
                    elif event.key in [pygame.K_4, pygame.K_KP4]: num = 4
                    elif event.key in [pygame.K_5, pygame.K_KP5]: num = 5
                    elif event.key in [pygame.K_6, pygame.K_KP6]: num = 6
                    elif event.key in [pygame.K_7, pygame.K_KP7]: num = 7
                    elif event.key in [pygame.K_8, pygame.K_KP8]: num = 8
                    elif event.key in [pygame.K_9, pygame.K_KP9]: num = 9
                    else: num = None
                    if num:
                        undo_stack.append((copy.deepcopy(working_grid), copy.deepcopy(notes)))
                        if note_mode:
                            if num in notes[row][col]:
                                notes[row][col].remove(num)
                            else:
                                notes[row][col].add(num)
                        else:
                            if solution_grid[row][col] == num:
                                working_grid[row][col] = num
                                notes[row][col].clear()
                                for i in range(9):
                                    if num in notes[row][i]: notes[row][i].remove(num)
                                    if num in notes[i][col]: notes[i][col].remove(num)
                                start_row, start_col = 3*(row//3), 3*(col//3)
                                for i in range(start_row, start_row+3):
                                    for j in range(start_col, start_col+3):
                                        if num in notes[i][j]: notes[i][j].remove(num)
                                victory = is_solved()
                            else:
                                mistakes += 1
                                screen.fill(RED, (col*CELL_SIZE, row*CELL_SIZE, CELL_SIZE, CELL_SIZE))
                                pygame.display.update()
                                pygame.time.wait(100)
                        redo_stack.clear()
                if event.key == pygame.K_LEFT and selected:
                    row, col = selected
                    if col > 0: selected = (row, col - 1)
                elif event.key == pygame.K_RIGHT and selected:
                    row, col = selected
                    if col < 8: selected = (row, col + 1)
                elif event.key == pygame.K_UP and selected:
                    row, col = selected
                    if row > 0: selected = (row - 1, col)
                elif event.key == pygame.K_DOWN and selected:
                    row, col = selected
                    if row < 8: selected = (row + 1, col)
                elif event.key == pygame.K_SPACE:
                    toggle_notes()
                elif event.key == pygame.K_u and undo_stack:
                    redo_stack.append((copy.deepcopy(working_grid), copy.deepcopy(notes)))
                    working_grid, notes = undo_stack.pop()
                    victory = is_solved()
                elif event.key == pygame.K_r and redo_stack:
                    undo_stack.append((copy.deepcopy(working_grid), copy.deepcopy(notes)))
                    working_grid, notes = redo_stack.pop()
                    victory = is_solved()
    
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
    elif game_state == PAUSED:
        draw_grid()
        draw_numbers()
        draw_selection()
        draw_ui()
        pause_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pause_surf.fill((128, 128, 128, 128))
        screen.blit(pause_surf, (0, 0))
        pause_text = font.render("PAUSED", True, WHITE)
        screen.blit(pause_text, (WIDTH//2 - pause_text.get_width()//2, HEIGHT//2 - pause_text.get_height()//2))
    
    pygame.display.update()

pygame.quit()
sys.exit()
