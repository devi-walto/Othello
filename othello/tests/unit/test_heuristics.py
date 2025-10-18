# othello/tests/unit/test_heuristics.py

import pytest

from othello.internal.heuristics import (
    evaluate,
    disc_difference,
    mobility,
    corner_control,
    x_square,
    game_phase,
    get_weights,
)

from othello.internal.board import (
    WHITE,
    BLACK,
    EMPTY,
)

# ============================== helper board class ==============================
class SimpleBoard:
    """
    Minimal board implementation for heuristic tests.
    - Uses a 2D grid of ints (WHITE / BLACK / EMPTY).
    - legal_moves_map is a dict: color -> list of (r, c) moves.
    """
    def __init__(self, size=8, grid=None, legal_moves_map=None, is_end=False):
        self.size = size
        self.grid = grid if grid is not None else [
            [EMPTY for _ in range(size)] for _ in range(size)
        ]
        self.legal_moves_map = legal_moves_map or {}
        self._is_end = is_end

    def get(self, r, c):
        return self.grid[r][c]

    def set(self, r, c, value):
        self.grid[r][c] = value

    def legal_moves(self, color):
        return self.legal_moves_map.get(color, [])

    def is_end(self):
        return self._is_end


# ============================== disc_difference ==============================

def test_disc_difference_more_my_discs():
    board = SimpleBoard()
    # place 3 of my color and 1 of opponent
    board.set(0, 0, WHITE)
    board.set(0, 1, WHITE)
    board.set(0, 2, WHITE)
    board.set(1, 0, BLACK)

    result = disc_difference(board, color=WHITE)
    # my_cnt = 3, opp_cnt = 1  ->  3 - 1 = 2
    assert result == 2, "disc_difference should return my_discs - opp_discs"


def test_disc_difference_equal_discs():
    board = SimpleBoard()
    board.set(0, 0, WHITE)
    board.set(0, 1, BLACK)

    result_white = disc_difference(board, color=WHITE)
    result_black = disc_difference(board, color=BLACK)

    assert result_white == 0, "Equal discs should result in 0 for WHITE"
    assert result_black == 0, "Equal discs should result in 0 for BLACK"


# ============================== mobility ==============================

def test_mobility_diff_in_legal_moves():
    """
    mobility(board, color) = my_moves - opp_moves
    """
    legal_moves_map = {
        WHITE: [(0, 0), (1, 1), (2, 2)],   # 3 moves
        BLACK: [(3, 3)],                   # 1 move
    }
    board = SimpleBoard(legal_moves_map=legal_moves_map)

    result = mobility(board, color=WHITE)
    assert result == 2, "mobility should be my_moves - opp_moves (3 - 1 = 2)"


def test_mobility_negative_when_opponent_has_more_moves():
    legal_moves_map = {
        WHITE: [(0, 0)],                         # 1 move
        BLACK: [(1, 1), (2, 2), (3, 3)],         # 3 moves
    }
    board = SimpleBoard(legal_moves_map=legal_moves_map)

    result = mobility(board, color=WHITE)
    assert result == -2, "mobility should be negative when opponent has more moves"


# ============================== corner_control ==============================

def test_corner_control_counts_corners_by_color():
    """
    corner_control = my_corners - opp_corners
    """
    board = SimpleBoard()

    # Corners are (0,0), (0,7), (7,0), (7,7)
    board.set(0, 0, WHITE)  # my corner
    board.set(0, 7, WHITE)  # my corner
    board.set(7, 0, BLACK)  # opponent corner
    # (7, 7) stays EMPTY

    result_white = corner_control(board, WHITE)
    result_black = corner_control(board, BLACK)

    # WHITE: 2 corners, BLACK: 1 corner
    assert result_white == 1, "WHITE should have corner advantage of +1"
    assert result_black == -1, "BLACK should see the same situation as -1"


# ============================== x_square (X-square penalty) ==============================

def test_x_square_penalty_when_my_x_square_without_corner():
    """
    If I own the X-square but not the corresponding corner,
    it should count as a penalty (positive for me here, but
    it will be weighted by a negative weight in evaluate()).
    """
    board = SimpleBoard()

    # Example: X-square (1,1) and its corner (0,0)
    board.set(1, 1, WHITE)   # I own the X-square
    board.set(0, 0, EMPTY)   # Corner is not mine

    result = x_square(board, WHITE)
    # my_sq = 1 (one bad X-square), op_sq = 0 -> 1 - 0 = 1
    assert result == 1, "Should count 1 bad X-square for current player"


def test_x_square_penalty_for_opponent():
    """
    If opponent owns the X-square and the corner is not theirs,
    op_sq should increase.
    """
    board = SimpleBoard()

    # X-square (1,6) and its corner (0,7)
    board.set(1, 6, BLACK)   # Opponent owns X-square
    board.set(0, 7, EMPTY)   # Corner is not opponent's

    result = x_square(board, WHITE)
    # my_sq = 0, op_sq = 1  ->  0 - 1 = -1
    assert result == -1, "Should reflect opponent bad X-square as negative for current player"


def test_x_square_no_penalty_when_corner_matches_owner():
    """
    If the X-square and its corner are the same color,
    there should be no penalty.
    """
    board = SimpleBoard()

    # X-square (6,6) and its corner (7,7)
    board.set(6, 6, WHITE)
    board.set(7, 7, WHITE)  # corner matches owner

    result = x_square(board, WHITE)
    assert result == 0, "No penalty when corner and X-square match color"


# ============================== game_phase ==============================

def _make_board_with_piece_count(count):
    """
    Helper for game_phase tests:
    create a board with exactly `count` non-EMPTY cells.
    """
    board = SimpleBoard()
    placed = 0
    for r in range(board.size):
        for c in range(board.size):
            if placed < count:
                board.set(r, c, WHITE)  # any non-EMPTY value
                placed += 1
    return board


def test_game_phase_early():
    board = _make_board_with_piece_count(10)  # <= 20
    assert game_phase(board) == "early"


def test_game_phase_mid():
    board = _make_board_with_piece_count(40)  # 21–58
    assert game_phase(board) == "mid"


def test_game_phase_late():
    board = _make_board_with_piece_count(60)  # > 58
    assert game_phase(board) == "late"


# ============================== get_weights ==============================

def test_get_weights_for_early_phase():
    w = get_weights("early")
    assert w["disk_difference"] == 1.0
    assert w["mobility"] == 5.0
    assert w["corner_control"] == 10.0
    assert w["x_square_penalty"] == -8.0


def test_get_weights_for_mid_phase():
    w = get_weights("mid")
    assert w["disk_difference"] == 2.0
    assert w["mobility"] == 4.0
    assert w["corner_control"] == 12.0
    assert w["x_square_penalty"] == -6.0


def test_get_weights_for_late_phase():
    w = get_weights("late")
    assert w["disk_difference"] == 5.0
    assert w["mobility"] == 2.0
    assert w["corner_control"] == 15.0
    assert w["x_square_penalty"] == -4.0


# ============================== evaluate (terminal states) ==============================

def test_evaluate_terminal_win_for_white():
    """
    If board.is_end() is True, evaluate() should return
    1000 * (piece_diff_for_color).
    """
    # Create a board where WHITE has more pieces
    grid = [[EMPTY for _ in range(8)] for _ in range(8)]
    grid[0][0] = WHITE
    grid[0][1] = WHITE
    grid[0][2] = BLACK

    board = SimpleBoard(grid=grid, is_end=True)

    value = evaluate(board, color=WHITE)
    # w = 2, b = 1 -> diff = 1 -> 1000 * 1 = 1000
    assert value == 1000, "Terminal win for WHITE should give positive large score"


def test_evaluate_terminal_win_for_black():
    grid = [[EMPTY for _ in range(8)] for _ in range(8)]
    grid[0][0] = BLACK
    grid[0][1] = BLACK
    grid[0][2] = WHITE

    board = SimpleBoard(grid=grid, is_end=True)

    value = evaluate(board, color=BLACK)
    # w = 1, b = 2 -> diff = (b - w) = 1 -> 1000
    assert value == 1000, "Terminal win for BLACK should give positive large score for BLACK"


# ============================== evaluate (non-terminal weighted sum) ==============================

def test_evaluate_non_terminal_uses_weighted_sum(mocker):
    """
    For non-terminal boards, evaluate() should:
    - call game_phase(board) to get phase
    - get weights for that phase
    - combine the heuristic values with those weights
    """
    # Dummy board that is not terminal
    board = SimpleBoard(is_end=False)

    # Patch game_phase and get_weights to keep things simple
    mocker.patch("othello.internal.heuristics.game_phase", return_value="custom")
    mocker.patch(
        "othello.internal.heuristics.get_weights",
        return_value={
            "disk_difference": 1.0,
            "mobility": 1.0,
            "corner_control": 1.0,
            "x_square_penalty": 1.0,
            "stable_disks": 0.0,
        },
    )

    # Patch individual heuristics to known values
    mocker.patch("othello.internal.heuristics.disc_difference", return_value=1)
    mocker.patch("othello.internal.heuristics.mobility", return_value=2)
    mocker.patch("othello.internal.heuristics.corner_control", return_value=3)
    mocker.patch("othello.internal.heuristics.x_square", return_value=-1)

    value = evaluate(board, color=WHITE)
    # score = 1*1 + 1*2 + 1*3 + 1*(-1) = 5
    assert value == 5, "evaluate() should combine heuristics using the weight schedule"