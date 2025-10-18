# internal/board.py

# board state + rule mechanics (pure logic)

from __future__ import annotations # This is needed for Python 3.7 and 3.8 compatibility
from typing import List, Tuple, Dict 

from .utils import in_bounds, to_algebra, from_algebra, BOARD_SIZE

WHITE = 1
BLACK = -1
EMPTY = 0

SYMBOLS = { WHITE: "●", BLACK: "○", EMPTY: "." } # UNICODE symbols for pieces
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),       # Valid directions for move checking
              (0, -1),          (0, 1),
              (1, -1),  (1, 0),  (1, 1)]

# @param color: int - color of the player

def opponent(color: int) -> int: 
    """
    Return the opponent's color for a given player color.
    Args:
        color (int): The player's color (commonly 1 or -1).
    Returns:
        int: The opponent's color (the negation of `color`). For example, if `color` is 1, returns -1.
    """
    return -color

class Board:
    size = BOARD_SIZE # Standard Othello board size
    def __init__(self) -> None:
        self.grid: List[List[int]] = [[EMPTY for _ in range(self.size)] for _ in range(self.size)] # 8x8 board initialized to EMPTY
        
    @staticmethod
    def initial() -> Board:
        board = Board()
        mid = Board.size // 2
        # Set up the initial four pieces in the center
        board.grid[mid - 1][mid - 1] = WHITE
        board.grid[mid][mid] = WHITE
        board.grid[mid - 1][mid] = BLACK
        board.grid[mid][mid - 1] = BLACK

        # Set rest of the board to EMPTY
        for r in range(board.size):
            for c in range(board.size):
                if (r, c) not in [(mid - 1, mid - 1), (mid, mid), (mid - 1, mid), (mid, mid - 1)]:
                    board.grid[r][c] = EMPTY
        return board
    
    def copy(self) -> Board:
        new_board = Board()
        new_board.grid = [row[:] for row in self.grid] # ':' is the slice operator to copy lists in 1 dimension
        return new_board

    def get(self, row: int, col: int) -> int:
        """Return the piece at the specified row and column."""
        return self.grid[row][col]
    def set(self, row: int, col: int, color: int) -> None:
        """Set the piece at the specified row and column to the given color."""
        self.grid[row][col] = color
        
        # sync accidental duplicate method
    def in_bounds(self, row: int, col: int) -> bool:
        return in_bounds(row, col, self.size)
    
    def score(self) -> Dict[str, int]:
        """Count the number of pieces for each color on the board"""
        w = sum(cell == WHITE for row in self.grid for cell in row) # shorthand for loop through rows then columns and += 1 if cell matches WHITE
        b = sum(cell == BLACK for row in self.grid for cell in row) # shorthand for loop through rows then columns and += 1 if cell matches BLACK
        return {"white": w, "black": b}

    def to_string(self, symbols: Dict[int, str] = SYMBOLS) -> str:
        """
        Coordinate-based string representation of the board.
        Ex: d4 -> column d(3), row 4(3)
        """
        cols = f"  " + " ".join([chr(ord('a') + i) for i in range(self.size)]) # Column labels a-h (referenced in worklog)
        lines = [cols] # Start with column headers
        for r in range(self.size):
            row_syms = " ".join(symbols[self.grid[r][c]] for c in range(self.size))
            # Add row number and row symbols
            lines.append(f"{r + 1} {row_syms}")
        return "\n".join(lines)
    

    def flips(self, row: int, col: int, color: int) -> List[Tuple[int, int]]:
        """
        If (r,c) is a legal placement for `color`, return the list of opponent squares to flip. Otherwise return [].
        Args:
            row (int): The row index where the piece is placed.
            col (int): The column index where the piece is placed.
            color (int): The color of the piece being placed (WHITE or BLACK).
        """
        if not self.in_bounds(row, col) or self.get(row, col) != EMPTY:
            return [] # Out of bounds or not empty
        flips_list: List[Tuple[int, int]] = [] # To store all pieces to flip

        # Loop through all directions and check if there are any opponent pieces in the line
        
        for drow, dcol in DIRECTIONS: # Check valid directions list
            rr, cc = row + drow, col + dcol # Step in the direction (rr = row row delta, cc = col col delta)
            line: List[Tuple[int, int]] = [] # To store potential flips in this direction
            while self.in_bounds(rr, cc) and self.get(rr, cc) == opponent(color): # While in bounds and opponent's piece
                line.append((rr, cc)) # Potential flip
                rr += drow
                cc += dcol
            # Check if we ended on a piece of the current player's color by following the direction until we hit a different color or go out of bounds
            if self.in_bounds(rr, cc) and self.get(rr, cc) == color: # if we found a piece of the current player's color
                flips_list.extend(line) # Valid direction, add to flips (extend to add multiple items)
        return flips_list # Return all pieces to flip


    def legal_moves(self, color: int) -> List[Tuple[int, int]]:
        """
        loop through all board positions and return a list of valid moves for the given color.
        Returns:
            List[Tuple[int, int]]: A list of (row, col) tuples representing valid moves.
        """
        moves: List[Tuple[int, int]] = []
        for r in range(self.size):
            for c in range(self.size):
                if self.get(r, c) == EMPTY and self.flips(r, c, color): # If empty and has flips
                    moves.append((r, c))
        return moves
    
            
    
    def apply_move(self, row: int, col: int, color: int) -> None:
        """
        Apply a move for the given color at (row, col), flipping the appropriate pieces.
        Args:
            row (int): The row index where the piece is placed.
            col (int): The column index where the piece is placed.
            color (int): The color of the piece being placed (WHITE or BLACK).
        """
        flips = self.flips(row, col, color)
        if not flips:
            raise ValueError("Invalid move: no pieces to flip.")
        self.set(row, col, color) # Place the piece
        for fr, fc in flips: # fr is flip row, fc is flip col
            self.set(fr, fc, color) # Flip the pieces to the current color
    
    def hasMoves(self, color: int) -> bool:
        """ Check if there are any valid moves for the given color. """
        return any(self.legal_moves(color)) # any returns True if any element of the iterable is true
    
    def is_end(self) -> bool:
        """ Check if the game has ended (no valid moves for either player). """
        return not self.hasMoves(WHITE) and not self.hasMoves(BLACK)