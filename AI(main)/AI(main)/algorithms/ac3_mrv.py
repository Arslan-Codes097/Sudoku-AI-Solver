import time
import sys
import os

# Add parent directory to path to import sudoku_csp
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from sudoku_csp import get_peers, is_complete

def _select_unassigned_variable(grid, domains):
    """
    Selects the next variable to assign using MRV and Degree Heuristic.
    """
    min_len = 10
    best_vars = []
    
    # Minimum Remaining Values (MRV)
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                l = len(domains[(r, c)])
                if l < min_len:
                    min_len = l
                    best_vars = [(r, c)]
                elif l == min_len:
                    best_vars.append((r, c))
                    
    if not best_vars:
        return None
                    
    if len(best_vars) == 1:
        return best_vars[0]
        
    # Tie-breaker: Degree heuristic (most constraints on remaining unassigned variables)
    max_degree = -1
    best_var = None
    for r, c in best_vars:
        degree = 0
        for pr, pc in get_peers(r, c):
            if grid[pr][pc] == 0:
                degree += 1
        if degree > max_degree:
            max_degree = degree
            best_var = (r, c)
            
    return best_var

def _ac3(domains, queue=None):
    """
    Arc Consistency Algorithm 3.
    """
    if queue is None:
        queue = []
        for r in range(9):
            for c in range(9):
                for pr, pc in get_peers(r, c):
                    queue.append(((r, c), (pr, pc)))
                    
    while queue:
        (xi, xj) = queue.pop(0)
        if _revise(domains, xi, xj):
            if len(domains[xi]) == 0:
                return False
            for pk in get_peers(xi[0], xi[1]):
                if pk != xj:
                    queue.append((pk, xi))
    return True

def _revise(domains, xi, xj):
    """
    Revises domain of xi based on domain of xj.
    Since the constraint is xi != xj, we only remove a value from xi's domain
    if xj has ONLY ONE value, and it's that same value.
    """
    revised = False
    if len(domains[xj]) == 1:
        val_j = list(domains[xj])[0]
        if val_j in domains[xi]:
            domains[xi].remove(val_j)
            revised = True
    return revised

def _backtrack_ac3(grid, domains, metrics, moves):
    if is_complete(grid):
        return True
        
    var = _select_unassigned_variable(grid, domains)
    if not var:
        return True
        
    r, c = var
    
    for val in list(domains[var]):
        metrics['states_explored'] += 1
        
        # Save state
        old_domains = {k: set(v) for k, v in domains.items()}
        
        grid[r][c] = val
        if moves is not None:
            moves.append((r, c, val))
        domains[var] = {val}
        
        # Enforce AC-3 starting from neighbors of assigned variable
        queue = [((pr, pc), var) for pr, pc in get_peers(r, c) if grid[pr][pc] == 0]
        
        is_consistent = _ac3(domains, queue)
        
        if is_consistent:
            if _backtrack_ac3(grid, domains, metrics, moves):
                return True
                
        # Backtrack
        metrics['backtracks'] += 1
        grid[r][c] = 0
        if moves is not None:
            moves.append((r, c, 0))
        # Restore domains
        for k in domains:
            domains[k] = set(old_domains[k])
            
    return False

def solve(grid, moves=None):
    """
    Informed Search: AC-3 + MRV + Degree Heuristic.
    Returns a tuple (solved_grid, metrics).
    """
    grid_copy = [row[:] for row in grid]
    metrics = {'time': 0, 'states_explored': 0, 'backtracks': 0, 'optimal': True}
    
    start_time = time.time()
    
    # Initialize domains
    domains = {}
    for r in range(9):
        for c in range(9):
            if grid_copy[r][c] != 0:
                domains[(r, c)] = {grid_copy[r][c]}
            else:
                domains[(r, c)] = set(range(1, 10))
                
    # Initial AC3
    if _ac3(domains):
        success = _backtrack_ac3(grid_copy, domains, metrics, moves)
    else:
        success = False
        
    end_time = time.time()
    metrics['time'] = end_time - start_time
    
    if success:
        return grid_copy, metrics
    else:
        return None, metrics
