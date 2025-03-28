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

# Create a working copy of the grid to modify during gameplay
working_grid = [row[:] for row in initial_grid]

# Function to print the grid in a readable format
def print_grid(grid):
    for i in range(9):
        if i % 3 == 0 and i != 0:
            print("- - - - - - - - - - -")  # Horizontal separator every 3 rows
        for j in range(9):
            if j % 3 == 0 and j != 0:
                print(" | ", end="")  # Vertical separator every 3 columns
            if grid[i][j] == 0:
                print(". ", end="")  # Empty cell represented by a dot
            else:
                print(str(grid[i][j]) + " ", end="")
        print()  # New line after each row

# Function to check if a number can be placed in a given cell
def can_place(grid, row, col, num):
    # Check the row for duplicates
    if num in grid[row]:
        return False
    
    # Check the column for duplicates
    for i in range(9):
        if grid[i][col] == num:
            return False
    
    # Check the 3x3 subgrid for duplicates
    start_row = (row // 3) * 3
    start_col = (col // 3) * 3
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if grid[i][j] == num:
                return False
    return True

# Welcome message and instructions
print("Welcome to Sudoku!")
print("Enter row (1-9), column (1-9), and number (1-9) to place a number, or 0 to clear a cell.")

# Main game loop
while True:
    print_grid(working_grid)  # Display the current state of the grid
    try:
        # Get user input (subtract 1 from row and column for 0-based indexing)
        row = int(input("Enter row (1-9): ")) - 1
        col = int(input("Enter column (1-9): ")) - 1
        num = int(input("Enter number (0-9): "))
        
        # Validate input ranges
        if row < 0 or row > 8 or col < 0 or col > 8 or num < 0 or num > 9:
            print("Invalid input. Row and column must be 1-9, number must be 0-9.")
            continue
        
        # Check if the cell is pre-filled (fixed)
        if initial_grid[row][col] != 0:
            print("Cannot change fixed cells.")
            continue
        
        # Handle clearing a cell
        if num == 0:
            working_grid[row][col] = 0
            print("Cell cleared.")
        
        # Handle placing a number
        elif can_place(working_grid, row, col, num):
            working_grid[row][col] = num
            print("Number placed successfully.")
        else:
            print("Cannot place that number there.")
        
        # Check if the puzzle is solved (no empty cells left)
        if all(all(cell != 0 for cell in row) for row in working_grid):
            print_grid(working_grid)
            print("Congratulations! You solved the puzzle!")
            break
    
    except ValueError:
        print("Invalid input. Please enter integers.")
