# internal/utils.py

# small helpers (no imports from other project files to avoid cycles)
from __future__ import annotations
from typing import Optional, Tuple

BOARD_SIZE = 8  # keep a single source of truth for coord conversions

def to_algebra(move: Tuple[int, int]) -> str:
    """(row, col) zero-based -> 'd3' style string (col letter, row 1-based)."""
    r, c = move
    return f"{chr(ord('a') + c)}{r + 1}"

def from_algebra(token: str) -> Optional[Tuple[int, int]]:
    """'d3' or 'A8' -> (row, col) zero-based. Returns None if invalid/out of range."""
    if not token or len(token) < 2 or len(token) > 3:
        return None
    t = token.strip().lower()
    col_ch = t[0]
    if not ('a' <= col_ch <= 'h'):
        return None
    try:
        row_num = int(t[1:])
    except ValueError:
        return None
    if not (1 <= row_num <= BOARD_SIZE):
        return None
    row_idx = row_num - 1
    col_idx = ord(col_ch) - ord('a')
    return (row_idx, col_idx)

def in_bounds(r: int, c: int, size: int = BOARD_SIZE) -> bool:
    return 0 <= r < size and 0 <= c < size # if row is between 0 and size-1 and col is between 0 and size-1