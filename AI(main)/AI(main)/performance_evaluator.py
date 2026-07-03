from algorithms import backtracking, ac3_mrv, local_search, forward_checking

def evaluate(grid, algorithm_name, moves=None):
    """
    Evaluates a specific algorithm on the given grid.
    Returns (solved_grid, metrics).
    """
    if algorithm_name == "Backtracking":
        res = backtracking.solve(grid, moves=moves)
    elif algorithm_name == "AC-3 + MRV":
        res = ac3_mrv.solve(grid, moves=moves)
    elif algorithm_name == "Forward Checking":
        res = forward_checking.solve(grid, moves=moves)
    elif algorithm_name == "Simulated Annealing":
        res = local_search.solve(grid, moves=moves)
    else:
        raise ValueError(f"Unknown algorithm: {algorithm_name}")
        
    solved_grid, metrics = res
    return solved_grid, metrics

def run_all(grid):
    """
    Runs all algorithms on the given grid and returns their performance metrics.
    """
    results = {}
    algorithms = ["Backtracking", "Forward Checking", "AC-3 + MRV", "Simulated Annealing"]
    
    empty_cells = sum(1 for r in range(9) for c in range(9) if grid[r][c] == 0)
    target_duration_ms = empty_cells * 250.0
    refresh_rate_ms = 20
    total_ticks = max(1, target_duration_ms / refresh_rate_ms)
    
    for algo in algorithms:
        grid_copy = [row[:] for row in grid]
        moves = []
        solved_grid, metrics = evaluate(grid_copy, algo, moves=moves)
        
        # Calculate exactly how long the animation would take, to match user perception
        batch_size = max(1, int(len(moves) / total_ticks)) if moves else 1
        anim_time = (len(moves) / batch_size) * refresh_rate_ms / 1000.0 if moves else metrics.get('time', 0.0)
        metrics['time'] = anim_time
        
        results[algo] = {
            'metrics': metrics,
            'solved_grid': solved_grid
        }
    return results
