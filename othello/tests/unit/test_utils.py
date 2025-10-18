# othello/tests/unit/test_utils.py

import pytest
from othello.internal.utils import (
    to_algebra,
    from_algebra,
    in_bounds,
    BOARD_SIZE,
)

# ============================= to_algebra Tests =============================

# parametrize test cases for reusable testing
@pytest.mark.parametrize( 
    "move, expected",
    [
        ((0, 0), "a1"),    # top-left corner
        ((7, 7), "h8"),    # bottom-right corner
        ((2, 3), "d3"),    # random middle cell
    ],
)
def test_to_algebra_valid_positions(move, expected):
    assert to_algebra(move) == expected, f"to_algebra({move}) should be '{expected}'"


# ============================= from_algebra Tests =============================

# parametrize test cases for reusable testing
@pytest.mark.parametrize(
    "token, expected",
    [
        ("a1", (0, 0)),
        ("H8", (7, 7)),      # uppercase allowed
        ("C2", (1, 2)),
    ],
)
def test_from_algebra_valid_inputs(token, expected):
    assert from_algebra(token) == expected


@pytest.mark.parametrize(
    "token",
    ["z3", "i1", "11", "", None, "a", "a100", "3b"]  # invalid letters, too short/long, non-letter starts
)
def test_from_algebra_invalid_inputs(token):
    assert from_algebra(token) is None


@pytest.mark.parametrize("token", ["a0", "a9", "h0", "h10"])
def test_from_algebra_out_of_range_rows(token):
    assert from_algebra(token) is None


@pytest.mark.parametrize("token", ["ab", "a1x", "a1b"])
def test_from_algebra_non_numeric_row_part(token):
    assert from_algebra(token) is None


def test_from_algebra_to_algebra_round_trip():
    """Every valid (row, col) should convert to algebra and back."""
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            algebra = to_algebra((row, col))
            assert from_algebra(algebra) == (row, col)


# ============================= in_bounds Tests =============================

@pytest.mark.parametrize(
    "r, c",
    [
        (0, 0),
        (7, 7),
        (3, 4),
        (5, 2),
    ],
)
def test_in_bounds_valid_coordinates(r, c):
    assert in_bounds(r, c) is True


@pytest.mark.parametrize(
    "r, c",
    [
        (-1, 0),
        (0, -1),
        (-2, -2),
    ],
)
def test_in_bounds_negative_indices(r, c):
    assert in_bounds(r, c) is False


@pytest.mark.parametrize(
    "r, c",
    [
        (8, 0),
        (0, 8),
        (10, 10),
    ],
)
def test_in_bounds_out_of_range(r, c):
    assert in_bounds(r, c) is False


def test_in_bounds_custom_size():
    assert in_bounds(4, 4, size=5) is True       # inside custom board
    assert in_bounds(5, 0, size=5) is False      # row too large
    assert in_bounds(0, 5, size=5) is False      # col too large