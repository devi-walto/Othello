# internal/minimax.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict
import math

from .board import Board, WHITE, BLACK, EMPTY, opponent  # uses existing constants
from .heuristics import evaluate        # will add a basic eval in heuristics.py
from .utils import to_algebra  # for debug printing
from .utils import from_algebra
from .log import dprint

@dataclass
class Minimax:
    depth: int = 3
    alpha_beta: bool = True
    debug : bool = False
    
    # runtime fields (set per move)
    nodes_searched: int = 0 
    root_color: int = BLACK
    move_evals: List[Tuple[Tuple[int, int], int]] = field(default_factory=list)  # [ (move, eval) ] - List of moves ((row, col), eval)

    def reset_counters(self) -> None:
        self.nodes_searched = 0
        self.move_evals = [] # list of (move, eval) tuples

    # entry point
    def choose_move(self, board: Board, color: int) -> Optional[Tuple[int, int]]: #Optional Tuple containing row and column represents a move
        """
        Root function: generate legal moves for `color`, evaluate each child
        by calling `minimax` on the position AFTER that move, then pick best.
        Returns the chosen move (row, col) or None if no moves.
        """
        self.reset_counters()
        self.root_color = color

        moves = board.legal_moves(color)
        if not moves:
            if self.debug:
                dprint("[debug] no legal moves; must pass")
            return None

        # Optional: small move ordering (corners first) to help pruning
        moves = self._inorder(board, color, moves)

        best_move = None
        # For the player at the root, we are maximizing from root_color POV
        best_eval = -math.inf

        alpha, beta = -math.inf, math.inf
        alpha = alpha
        beta = beta

        for (r, c) in moves:
            child = board.copy()
            child.apply_move(r, c, color)

            # Next ply: opponent to move
            # maximizing_player is True if opponent is root_color
            val = self.minimax(child,self.depth - 1, alpha, beta, maximizing_player=opponent(color))

            self.move_evals.append(((r, c), val))

            if val > best_eval:
                best_eval = val
                best_move = (r, c)

            if self.alpha_beta:
                alpha = max(alpha, val)
                if beta <= alpha:
                    if self.debug:
                        dprint("[debug] root alpha-beta cutoff")
                    break
        # Final debug printing
        if self.debug:
            scored = [f"{to_algebra(mv)}: {ev:+.0f}" for mv, ev in self.move_evals]
            dprint(f"[debug] nodes={self.nodes_searched} depth={self.depth} alpha-beta={'ON' if self.alpha_beta else 'OFF'}")
            dprint(f"[debug] root move scores: {scored}")
            if best_move:
                dprint(f"[debug] chosen: {to_algebra(best_move)} (eval {best_eval:+.0f})")
        return best_move

    # recursive minimax function

    # ============ V1
    def minimax(self, board: Board, depth: int, alpha: int, beta: int, maximizing_player: bool) -> int:
        """ 
        Minimax algorithm with optional alpha-beta pruning. 
        Arguments:
            board: Poition or board state to evaluate
            depth: Current depth in the game tree
            alpha: Alpha value for pruning
            beta: Beta value for pruning
            maximizing_player: True if the current layer is maximizing, False if minimizing
        """
        if depth == 0 or board.is_end():
            return evaluate(board, self.root_color)
        
        if maximizing_player:
            max_eval = -math.inf
            # for each legal move in current board state
            for (r, c) in board.legal_moves(self.root_color):
                child = board.copy()    # create an empty board state representing the legal move
                child.apply_move(r, c, self.root_color) # apply the move to the child board

                eval = self.minimax(child, depth - 1, alpha, beta, False)
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)

                if beta <= alpha and self.alpha_beta:
                    break  # prune remaining branches
            return max_eval
        
        if not maximizing_player:
            min_eval = math.inf
            # for each legal move in current board state
            for (r, c) in board.legal_moves(self.root_color):
                child = board.copy()    # create an empty board state representing the legal move
                child.apply_move(r, c, self.root_color) # apply the move to the child board

                eval = self.minimax(child, depth - 1, alpha, beta, False)
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)

                if beta <= alpha and self.alpha_beta:
                    break  # prune remaining branches
            return min_eval
        


    # ---- helper functions ----
    def _inorder(self, board: Board, color: int, moves: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """ Simple move ordering: prioritize corners, then others. """
        corners = [(0, 0), (0, board.size - 1), (board.size - 1, 0), (board.size - 1, board.size - 1)]
        corner_moves = [m for m in moves if m in corners]
        other_moves = [m for m in moves if m not in corners]
        return corner_moves + other_moves