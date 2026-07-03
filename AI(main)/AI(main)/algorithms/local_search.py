import random
import math
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_block_indices(block_num):
    r_start = (block_num // 3) * 3
    c_start = (block_num % 3) * 3
    indices = []
    for r in range(r_start, r_start + 3):
        for c in range(c_start, c_start + 3):
            indices.append((r, c))
    return indices

def initial_state(grid):
    state = [row[:] for row in grid]
    for block in range(9):
        indices = get_block_indices(block)
        available = set(range(1, 10))
        empty_cells = []
        for r, c in indices:
            if state[r][c] != 0:
                available.remove(state[r][c])
            else:
                empty_cells.append((r, c))
        
        available = list(available)
        random.shuffle(available)
        for i, (r, c) in enumerate(empty_cells):
            state[r][c] = available[i]
    return state

def count_conflicts(state):
    conflicts = 0
    # Check rows and cols
    for i in range(9):
        row_set = set()
        col_set = set()
        for j in range(9):
            row_set.add(state[i][j])
            col_set.add(state[j][i])
        conflicts += (9 - len(row_set)) + (9 - len(col_set))
    return conflicts

def get_neighbor(state, original_grid):
    neighbor = [row[:] for row in state]
    block = random.randint(0, 8)
    indices = get_block_indices(block)
    
    # filter indices to only those that were initially empty
    movable = [(r, c) for r, c in indices if original_grid[r][c] == 0]
    
    if len(movable) < 2:
        return neighbor, None, None # can't swap
        
    (r1, c1), (r2, c2) = random.sample(movable, 2)
    neighbor[r1][c1], neighbor[r2][c2] = neighbor[r2][c2], neighbor[r1][c1]
    return neighbor, (r1, c1), (r2, c2)

def solve(grid, moves=None):
    """
    Local Search: Simulated Annealing.
    Starts from a complete assignment and minimizes constraint violations.
    Returns a tuple (solved_grid, metrics).
    """
    metrics = {'time': 0, 'states_explored': 0, 'backtracks': 0, 'optimal': False}
    start_time = time.time()
    
    current_state = initial_state(grid)
    current_conflicts = count_conflicts(current_state)
    
    T = 1.0
    T_min = 0.00001
    alpha = 0.9999 # slower cooling for better convergence
    
    best_state = current_state
    best_conflicts = current_conflicts
    
    max_iterations = 200000
    iterations = 0
    
    if moves is not None:
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    moves.append((r, c, current_state[r][c]))

    while T > T_min and best_conflicts > 0 and iterations < max_iterations:
        neighbor, pos1, pos2 = get_neighbor(current_state, grid)
        neighbor_conflicts = count_conflicts(neighbor)
        
        delta = neighbor_conflicts - current_conflicts
        
        metrics['states_explored'] += 1
        
        if delta < 0 or random.random() < math.exp(-delta / T):
            current_state = neighbor
            current_conflicts = neighbor_conflicts
            
            if moves is not None and pos1 is not None:
                moves.append((pos1[0], pos1[1], current_state[pos1[0]][pos1[1]]))
                moves.append((pos2[0], pos2[1], current_state[pos2[0]][pos2[1]]))
                
            if current_conflicts < best_conflicts:
                best_state = current_state
                best_conflicts = current_conflicts
        
        T *= alpha
        iterations += 1
        
    end_time = time.time()
    metrics['time'] = end_time - start_time
    
    if best_conflicts == 0:
        metrics['optimal'] = True
        return best_state, metrics
    else:
        # Local search might fail, return best found
        metrics['optimal'] = False
        return best_state, metrics
