# internal/cli.py

# ASCII renderer + input parsing + debug toggles

from __future__ import annotations # This is needed for Python 3.7 and 3.8 compatibility
import sys
from typing import Tuple, Optional

from .log import dprint
from .board import Board

def clear_screen() -> None:
    """Clears the terminal screen."""
    sys.stdout.write("\033[H\033[J")
    sys.stdout.flush()

def parse_move(token: str) -> Optional[Tuple[int, int]]:
    """
    Expect classic Othello input: letter+number (e.g., 'd3').
    Letter = column (a-h), Number = row (1-8).
    Returns (row_idx, col_idx) zero-based, or None if invalid.
    """
    token = token.strip().lower() # Normalize input
    if len(token) < 2 or len(token) > 3:
        return None
    col_ch = token[0] # First character is column
    if not ('a' <= col_ch <= 'h'):
        return None
    try:
        row_num = int(token[1:]) # Remaining characters are row
    
    # Handle invalid integer conversion
    except ValueError:
        return None
    if not (1 <= row_num <= 8):
        return None

    row_idx = row_num - 1
    col_idx = ord(col_ch) - ord('a')
    return (row_idx, col_idx)


def display_board(board: Board) -> None:
    """Renders the board to the terminal using ASCII characters."""
    clear_screen()
    dprint(board.to_string())
    s = board.score()
    dprint(f"\nScore  ● (white): {s['white']}   ○ (black): {s['black']}")