# othello/tests/unit/test_board.py

import pytest
from othello.internal.board import (
    Board,
    opponent,
    WHITE,
    BLACK,
    EMPTY,
)

# ============================== Fixtures ==============================
@pytest.fixture
def initial_board():
    """Provide a fresh standard Othello starting board for each test."""
    return Board.initial()


# ============================== test opponent() ==============================
def test_opponent_returns_negation():
    """opponent(color) should always return the opposite color."""
    assert opponent(WHITE) == BLACK, "Opponent of WHITE should be BLACK"
    assert opponent(BLACK) == WHITE, "Opponent of BLACK should be WHITE"
    assert opponent(1) == -1
    assert opponent(-1) == 1


# ============================== test Board.initial() ==============================
def test_initial_board_piece_counts(initial_board):
    """Initial board should have exactly 2 white and 2 black pieces."""
    score = initial_board.score()
    assert score["white"] == 2, "Initial board must start with 2 white pieces"
    assert score["black"] == 2, "Initial board must start with 2 black pieces"


def test_initial_board_center_setup(initial_board):
    """Initial center 4 pieces should match standard Othello layout."""
    mid = initial_board.size // 2

    # Coordinates:
    # (mid-1, mid-1) = WHITE
    # (mid, mid)     = WHITE
    # (mid-1, mid)   = BLACK
    # (mid, mid-1)   = BLACK
    assert initial_board.get(mid - 1, mid - 1) == WHITE
    assert initial_board.get(mid,     mid)     == WHITE
    assert initial_board.get(mid - 1, mid)     == BLACK
    assert initial_board.get(mid,     mid - 1) == BLACK


# ============================== test copy() ==============================
def test_copy_creates_independent_board(initial_board):
    """Board.copy() should return a deep copy (changing one does not change the other)."""
    copied = initial_board.copy()

    # Boards should not be the same object
    assert copied is not initial_board

    # Grids should not be the same object either
    assert copied.grid is not initial_board.grid

    # But contents should start out identical
    assert copied.grid == initial_board.grid

    # Now modify the copy and ensure original does not change
    copied.set(0, 0, WHITE)
    assert copied.get(0, 0) == WHITE
    assert initial_board.get(0, 0) == EMPTY, "Original board should not be affected by changes to the copy"


# ============================== test get() and set() ==============================
def test_get_and_set_place_piece():
    board = Board()
    board.set(3, 4, WHITE)

    assert board.get(3, 4) == WHITE, "set() should place the correct color at the given position"


# ============================== test in_bounds wrapper ==============================
def test_board_in_bounds_wrapper():
    board = Board()
    # Inside
    assert board.in_bounds(0, 0) is True
    assert board.in_bounds(board.size - 1, board.size - 1) is True
    # Outside
    assert board.in_bounds(-1, 0) is False
    assert board.in_bounds(0, board.size) is False


# ============================== test score() ==============================
def test_score_counts_pieces_correctly(initial_board):
    """score() should count all WHITE and BLACK pieces correctly."""
    score = initial_board.score()
    assert score["white"] == 2
    assert score["black"] == 2

    # Add some extra pieces and re-check
    initial_board.set(0, 0, WHITE)
    initial_board.set(0, 1, BLACK)

    new_score = initial_board.score()
    assert new_score["white"] == 3
    assert new_score["black"] == 3


# ============================== test to_string() ==============================
def test_to_string_basic_format(initial_board):
    """to_string() should produce 1 header line + size board rows."""
    board_str = initial_board.to_string()
    lines = board_str.splitlines()

    # First line should start with column labels
    assert lines[0].startswith("  a"), "First line should contain column headers"

    # There should be size + 1 lines (header + each row)
    assert len(lines) == Board.size + 1

    # The number of '●' and '○' should match score()
    joined = "\n".join(lines)
    white_count = joined.count("●")
    black_count = joined.count("○")
    score = initial_board.score()
    assert white_count == score["white"]
    assert black_count == score["black"]


# ============================== test flips() ==============================
def test_flips_invalid_when_out_of_bounds_or_not_empty(initial_board):
    """flips() should return [] if move is out of bounds or square is not empty."""
    # Out of bounds
    assert initial_board.flips(-1, 0, BLACK) == []
    assert initial_board.flips(0, Board.size, BLACK) == []

    # Not empty (center spots already occupied at start)
    mid = initial_board.size // 2
    assert initial_board.flips(mid, mid, BLACK) == [], "Cannot flip when placing on a non-empty square"


def test_flips_from_initial_position_black_d3(initial_board):
    """
    From the standard starting position:
    If BLACK plays at d3 (row=2, col=3), it should flip (3,3) which is a WHITE piece.
    """
    # d3 in zero-based indices is (2, 3)
    flips = initial_board.flips(2, 3, BLACK)
    assert (3, 3) in flips, "Move at (2,3) should flip the piece at (3,3)"
    assert len(flips) == 1, "From the starting position, this move should flip exactly one piece"


# ============================== test legal_moves() ==============================
def test_legal_moves_initial_black(initial_board):
    """
    From the standard starting position, BLACK should have 4 legal moves.
    (Exact positions depend on the initial layout.)
    """
    moves = set(initial_board.legal_moves(BLACK))

    expected = {
        (2, 3),  # d3
        (3, 2),  # c4
        (4, 5),  # f5
        (5, 4),  # e6
    }

    assert moves == expected, "Initial legal moves for BLACK should be the four standard opening moves"


def test_legal_moves_initial_white(initial_board):
    """WHITE should also have legal moves from the initial board."""
    moves = initial_board.legal_moves(WHITE)
    assert len(moves) > 0, "WHITE should have at least one legal move at the start"


# ============================== test apply_move() ==============================
def test_apply_move_flips_pieces_correctly(initial_board):
    """
    Applying a valid move should place a piece and flip the correct opponent pieces.
    Using BLACK at d3 (2,3) from the initial position.
    """
    # Before the move
    assert initial_board.get(2, 3) == EMPTY
    assert initial_board.get(3, 3) == WHITE

    initial_board.apply_move(2, 3, BLACK)

    # After the move: placed piece + flipped piece
    assert initial_board.get(2, 3) == BLACK, "Move position should now be BLACK"
    assert initial_board.get(3, 3) == BLACK, "The piece at (3,3) should have flipped to BLACK"

    # Score should update accordingly (2 -> 3 or 4 pieces, depending on flips)
    score = initial_board.score()
    assert score["black"] > 2, "BLACK piece count should increase after a valid move"
    assert score["white"] < 2, "WHITE piece count should decrease after being flipped"


def test_apply_move_raises_for_invalid_move():
    """apply_move() should raise ValueError when there are no pieces to flip."""
    board = Board()

    # At the very start, placing at (0,0) will flip nothing
    with pytest.raises(ValueError, match="Invalid move"):
        board.apply_move(0, 0, BLACK)


# ============================== test hasMoves() and is_end() ==============================
def test_hasMoves_and_is_end_initial(initial_board):
    """At the start of the game, both players should have moves and the game is not over."""
    assert initial_board.hasMoves(WHITE) is True
    assert initial_board.hasMoves(BLACK) is True
    assert initial_board.is_end() is False


def test_is_end_when_board_full_no_moves():
    """
    If the board is completely full of one color, neither side has moves
    and is_end() should return True.
    """
    board = Board()
    # Fill board with WHITE
    for r in range(board.size):
        for c in range(board.size):
            board.set(r, c, WHITE)

    assert board.hasMoves(WHITE) is False
    assert board.hasMoves(BLACK) is False
    assert board.is_end() is True