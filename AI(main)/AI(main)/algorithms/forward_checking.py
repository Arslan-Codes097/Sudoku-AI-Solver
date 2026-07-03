import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sudoku_csp import get_peers, is_complete

def _get_first_empty(grid):
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                return (r, c)
    return None

def _forward_check(grid, domains, metrics, moves):
    empty = _get_first_empty(grid)
    if not empty:
        return True
    row, col = empty
    
    for val in list(domains[(row, col)]):
        metrics['states_explored'] += 1
        
        # Save state
        old_domains = {k: set(v) for k, v in domains.items()}
        
        grid[row][col] = val
        if moves is not None:
            moves.append((row, col, val))
        domains[(row, col)] = {val}
        
        # Forward checking step
        is_consistent = True
        for pr, pc in get_peers(row, col):
            if grid[pr][pc] == 0:
                if val in domains[(pr, pc)]:
                    domains[(pr, pc)].remove(val)
                    if len(domains[(pr, pc)]) == 0:
                        is_consistent = False
                        break
        
        if is_consistent:
            if _forward_check(grid, domains, metrics, moves):
                return True
                
        # Backtracking step
        metrics['backtracks'] += 1
        grid[row][col] = 0
        if moves is not None:
            moves.append((row, col, 0))
        for k in domains:
            domains[k] = set(old_domains[k])
            
    return False

def solve(grid, moves=None):
    """
    Constraint Propagation strategy using Forward Checking.
    Returns a tuple (solved_grid, metrics).
    """
    grid_copy = [row[:] for row in grid]
    metrics = {'time': 0, 'states_explored': 0, 'backtracks': 0, 'optimal': True}
    
    start_time = time.time()
    
    domains = {}
    for r in range(9):
        for c in range(9):
            if grid_copy[r][c] != 0:
                domains[(r, c)] = {grid_copy[r][c]}
            else:
                domains[(r, c)] = set(range(1, 10))
                
    # Initial prune based on fixed cells
    is_consistent = True
    for r in range(9):
        for c in range(9):
            if grid_copy[r][c] != 0:
                val = grid_copy[r][c]
                for pr, pc in get_peers(r, c):
                    if grid_copy[pr][pc] == 0 and val in domains[(pr, pc)]:
                        domains[(pr, pc)].remove(val)
                        if len(domains[(pr, pc)]) == 0:
                            is_consistent = False
                            break
            if not is_consistent:
                break
    
    if is_consistent:
        success = _forward_check(grid_copy, domains, metrics, moves)
    else:
        success = False
        
    end_time = time.time()
    metrics['time'] = end_time - start_time
    
    if success:
        return grid_copy, metrics
    else:
        return None, metrics
