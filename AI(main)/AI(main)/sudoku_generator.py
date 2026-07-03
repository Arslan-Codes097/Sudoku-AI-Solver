import random

def generate_solved_grid():
    """Generates a complete, valid Sudoku grid."""
    grid = [[0 for _ in range(9)] for _ in range(9)]
    _fill_grid(grid)
    return grid

def _fill_grid(grid):
    empty = _get_first_empty(grid)
    if not empty:
        return True
    row, col = empty
    
    numbers = list(range(1, 10))
    random.shuffle(numbers)
    
    for num in numbers:
        if _is_safe(grid, row, col, num):
            grid[row][col] = num
            if _fill_grid(grid):
                return True
            grid[row][col] = 0
    return False

def _get_first_empty(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return (r, c)
    return None

def _is_safe(grid, row, col, num):
    for i in range(9):
        if grid[row][i] == num or grid[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if grid[start_row + i][start_col + j] == num:
                return False
    return True

def count_solutions(grid, limit=2):
    """Returns number of solutions up to `limit` to check for uniqueness."""
    empty = _get_first_empty(grid)
    if not empty:
        return 1
        
    row, col = empty
    count = 0
    for num in range(1, 10):
        if _is_safe(grid, row, col, num):
            grid[row][col] = num
            count += count_solutions(grid, limit)
            grid[row][col] = 0
            if count >= limit:
                break
    return count

def remove_cells(grid, target_filled):
    """Removes cells to reach target_filled while maintaining a unique solution."""
    cells = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(cells)
    
    filled = 81
    for row, col in cells:
        if filled <= target_filled:
            break
            
        temp = grid[row][col]
        grid[row][col] = 0
        
        # Check if unique solution still exists
        grid_copy = [r[:] for r in grid]
        if count_solutions(grid_copy) != 1:
            # Not unique, put it back
            grid[row][col] = temp
        else:
            filled -= 1
            
    return grid

def generate_puzzle(difficulty="Medium"):
    """Generates a puzzle of the specified difficulty."""
    grid = generate_solved_grid()
    
    # Difficulty targets (approximate number of filled cells)
    if difficulty == "Easy":
        target = random.randint(36, 42)
    elif difficulty == "Medium":
        target = random.randint(30, 35)
    elif difficulty == "Hard":
        target = random.randint(25, 29)
    elif difficulty == "Expert":
        target = random.randint(20, 24)
    else:
        target = 30
        
    puzzle = remove_cells(grid, target)
    return puzzle
