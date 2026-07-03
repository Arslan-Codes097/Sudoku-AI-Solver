def get_peers(row, col):
    """Returns a set of all peers (row, column, and 3x3 block) for a given cell (row, col)."""
    peers = set()
    for i in range(9):
        peers.add((row, i))
        peers.add((i, col))
        
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            peers.add((start_row + i, start_col + j))
            
    peers.remove((row, col))
    return peers

def is_valid_assignment(grid, row, col, value):
    """Checks if assigning value to grid[row][col] is valid according to Sudoku rules."""
    for r, c in get_peers(row, col):
        if grid[r][c] == value:
            return False
    return True

def get_empty_cells(grid):
    """Returns a list of empty cell coordinates."""
    empty = []
    for r in range(9):
        for c in range(9):
            if grid[r][c] == 0:
                empty.append((r, c))
    return empty

def is_complete(grid):
    """Checks if the grid is completely filled."""
    for row in range(9):
        for col in range(9):
            if grid[row][col] == 0:
                return False
    return True

def count_conflicts(grid):
    """Counts the total number of constraint violations. Useful for Local Search."""
    conflicts = 0
    for r in range(9):
        for c in range(9):
            val = grid[r][c]
            if val != 0:
                for pr, pc in get_peers(r, c):
                    if grid[pr][pc] == val:
                        conflicts += 1
    # Each conflict is counted twice (A conflicts B, B conflicts A)
    return conflicts // 2

def get_domain(grid, row, col):
    """Returns the set of possible valid values for an empty cell."""
    if grid[row][col] != 0:
        return set()
    
    domain = set(range(1, 10))
    for r, c in get_peers(row, col):
        if grid[r][c] in domain:
            domain.remove(grid[r][c])
    return domain
