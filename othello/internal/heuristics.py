# internal/heuristics.py

# evaluation functions and weight schedules
# Heuristics are based on info from: (https://www.othello.nl/content/guides/comteguide/strategy.html)
from __future__ import annotations
from typing import Dict, Tuple
from math import copysign

from .board import Board, WHITE, BLACK, EMPTY

# Constants
CORNERS = [(0,0), (0,7), (7,0), (7,7)] # Board corner positions
X_SQUARES = [(1,1), (1,6), (6,1), (6,6)] # The diagonal squares next to corners [ex: (1,1) next to (0,0)] (these are bad to take early)
# map each X-square to its corner
_X_TO_CORNER = {(1,1):(0,0), (1,6):(0,7), (6,1):(7,0), (6,6):(7,7)}

# ======= Public evaluation function =======
def evaluate(board: Board, color: int):
    """ Return a weighted sum of heuristics for the given board and player color. (+ is good for `color`, - is bad) """
    phase = game_phase(board) # early, mid, late
    weights = get_weights(phase) # get weights based on phase
    
    # Magnify win states
    if board.is_end(): # if game is over
        w = sum(1 for r in range(board.size) for c in range(board.size) if board.get(r, c) == WHITE) # count white pieces
        b = sum(1 for r in range(board.size) for c in range(board.size) if board.get(r, c) == BLACK) # count black pieces
        diff = (w - b) if color == WHITE else (b - w) # compute difference
        # magnify so wins outrank any non-terminal eval
        return 1000 * diff
    
    # Compute individual heuristics
    disc_diff = disc_difference(board, color)
    mob = mobility(board, color)
    corners = corner_control(board, color)
    x_sq = x_square(board, color)
    # stable_disks = stable_disks(board, color)  # Skipping for now

    # Weighted sum
    score = (
        weights['disk_difference'] * disc_diff + # look up weight for disk difference and multiply by disc_diff
        weights['mobility'] * mob +              # look up weight for mobility and multiply by mobility
        weights['corner_control'] * corners +   # look up weight for corner control and multiply by corner control
        weights['x_square_penalty'] * x_sq      # look up weight for x-square penalty and multiply by x-square penalty
        # + weights['stable_disks'] * stable_disks  # Skipping for now
    )
    return int(round(score))

# --------------------------------- INDIVIDUAL HEURISTICS ---------------------------------
# 1.) Disk Difference Heuristic
def disc_difference(board: Board, color: int) -> int:
    """ 
    return the differnces between current player & opponent disk
    Arguments:
        board(Board): Current board state (player position)
        color(int): Color of current player 
    """
    my_cnt = sum(1 for r in range(board.size) for c in range(board.size) if board.get(r,c) == color) #loop through rows then columns; sum all disks that are player color
    opp_cnt = sum(1 for r in range(board.size) for c in range(board.size) if board.get(r,c) == -color) #loop through rows then columns; sum all disks that are opponent color
    return my_cnt - opp_cnt

# 2.) Mobility Heuristic
def mobility(board: Board, color: int) -> int:
    my_moves = len(board.legal_moves(color))
    opp_moves = len(board.legal_moves(-color))
    return my_moves - opp_moves

# 3.) Corner Control Heuristic
def corner_control(board: Board, color: int) -> int:
    my_corners = sum(1 for (r,c) in CORNERS if board.get(r,c) == color)
    opp_corners = sum(1 for (r,c) in CORNERS if board.get(r,c) == -color)
    return my_corners - opp_corners

# 4.) X-Square Penalty Heuristic
def x_square(board: Board, color: int) -> int:
    my_sq = 0
    op_sq = 0
    for xr, xc in X_SQUARES:
        cr, cc = _X_TO_CORNER[(xr, xc)] # get corresponding corner
        corner_owner = board.get(cr, cc)
        x_owner = board.get(xr, xc)
        # penalize if corresponding corner is not same color
        if x_owner == color and corner_owner != color:
            my_sq += 1
        elif x_owner == -color and corner_owner != -color:
            op_sq += 1
    return my_sq - op_sq  # penalty for owning x-square (will be negative when calling evaluate() function)
# 5.) Stable Disks Heuristic

    # Too complex for now; skipping implementation
    # A stable disk is one that cannot be flipped for the rest of the game



# --------------------------------- HELPER FUNCTIONS ---------------------------------
# Game phase helper
def game_phase(board: Board) -> str:
    """Determine the current phase of the game based on the number of pieces on the board."""
    total_pieces = sum(1 for r in range(board.size) for c in range(board.size) if board.get(r, c) != EMPTY)
    if total_pieces <= 20:
        return 'early'
    elif total_pieces <= 58:
        return 'mid'
    else:
        return 'late'
    
# Weight schedule helper
def get_weights(phase: str) -> Dict[str, float]:
    """Return heuristic weights based on the game phase."""
    if phase == 'early':
        return {
            'disk_difference': 1.0,
            'mobility': 5.0,
            'corner_control': 10.0,
            'x_square_penalty': -8.0,
            'stable_disks': 2.0
        }
    elif phase == 'mid':
        return {
            'disk_difference': 2.0,
            'mobility': 4.0,
            'corner_control': 12.0,
            'x_square_penalty': -6.0,
            'stable_disks': 4.0
        }
    else:  # late game
        return {
            'disk_difference': 5.0,
            'mobility': 2.0,
            'corner_control': 15.0,
            'x_square_penalty': -4.0,
            'stable_disks': 6.0
        }