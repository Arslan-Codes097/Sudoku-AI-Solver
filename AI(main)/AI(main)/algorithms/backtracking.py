import time

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

def _backtrack(grid, metrics, moves):
    empty = _get_first_empty(grid)
    if not empty:
        return True
    row, col = empty
    
    for num in range(1, 10):
        metrics['states_explored'] += 1
        if _is_safe(grid, row, col, num):
            grid[row][col] = num
            if moves is not None:
                moves.append((row, col, num))
            if _backtrack(grid, metrics, moves):
                return True
            # Backtracking step
            metrics['backtracks'] += 1
            grid[row][col] = 0
            if moves is not None:
                moves.append((row, col, 0))
            
    return False

def solve(grid, moves=None):
    """
    Uninformed Search: Backtracking Search (depth-first).
    Returns a tuple (solved_grid, metrics).
    """
    # Create a copy to avoid mutating the original until solved
    grid_copy = [row[:] for row in grid]
    metrics = {'time': 0, 'states_explored': 0, 'backtracks': 0, 'optimal': True}
    
    start_time = time.time()
    success = _backtrack(grid_copy, metrics, moves)
    end_time = time.time()
    
    metrics['time'] = end_time - start_time
    
    if success:
        return grid_copy, metrics
    else:
        return None, metrics
