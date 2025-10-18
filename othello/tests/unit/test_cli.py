import pytest
from othello.internal.cli import (
    clear_screen,
    parse_move,
    display_board,
)

# =================================== test_clear_screen (had to ask GPT for help)  =========================
def test_clear_screen_captures_output(capsys):
    clear_screen()
    captured = capsys.readouterr()

    assert "\033[H\033[J" in captured.out, "clear_screen should write the clear-screen escape code"
# =================================== test parse_move (valid inputs) ===================================
@pytest.mark.parametrize("token, expected", [
    ("a1", (0, 0)), # top-left corner
    ("a8", (7, 0)), # top-right corner
    ("h8", (7, 7)), # bottom-right corner (uppercase input)
    ("c2", (1, 2)), # middle-left
    ],
)

def test_parse_move_valid(token, expected):
    """ parse_move should return a tuple of (row, col) for valid move inputs. 
    Replaces to_algebra() in othello/internal/cli.py."""
    assert parse_move(token) == expected, f"parse_move({token!r}) == {expected}" # !r is for string representation of the input

# =================================== test parse_move (invalid inputs) ===================================
@pytest.mark.parametrize(
    "token",
    [
        "",        # empty
        "a",       # too short
        "abcd",    # too long
        "z1",      # column out of range
        "i3",      # column out of range
        "11",      # does not start with letter
        "1a",      # letter not first
    ],
)
def test_parse_move_invalid_shape_or_column(token):
    """
    Invalid shapes or invalid column letters should return None.
    """
    assert parse_move(token) is None, f"parse_move({token!r}) == None"

@pytest.mark.parametrize(
    "token",
    [
        "a0",      # row out of range
        "a9",      # row out of range
        "a10",     # row out of range
        "a-1",     # row out of range
    ],
)
def test_parse_move_out_of_range_row(token):
    """ Invalid row numbers should return None."""
    assert parse_move(token) is None, f"parse_move({token!r}) == None"


@pytest.mark.parametrize(
    "token",
    [
        "ax",
        "b1x",
        "c1d",
    ],
)
def test_parse_move_non_numeric(token):
    """ Non-numeric characters in the row part should return None."""
    assert parse_move(token) is None, f"parse_move({token!r}) == None"

# ============================== test display_board ==============================

def test_display_board_calls_clear_and_dprint(mocker):
    """
    display_board should:
    - call clear_screen()
    - call dprint(board.to_string())
    - call dprint() again for the score line
    """
    # Patch clear_screen and dprint so we can inspect the calls
    clear_mock = mocker.patch("othello.internal.cli.clear_screen")
    dprint_mock = mocker.patch("othello.internal.cli.dprint")

    # Create a simple fake Board with the minimal API
    class FakeBoard:
        def to_string(self):
            return "BOARD ASCII"

        def score(self):
            return {"white": 10, "black": 8}

    board = FakeBoard()

    # Call the function under test
    display_board(board)

    # clear_screen should be called once
    clear_mock.assert_called_once()

    # dprint should be called at least twice:
    # 1) with the board ASCII
    # 2) with the score line
    assert dprint_mock.call_count >= 2, "display_board should call dprint at least twice"

    # First call: board ASCII
    first_call_args = dprint_mock.call_args_list[0].args
    assert first_call_args[0] == "BOARD ASCII", "First dprint call should be board.to_string() output"

    # Second call: score line (we just check it mentions white/black scores)
    second_call_args = dprint_mock.call_args_list[1].args
    score_line = second_call_args[0]
    assert "white" in score_line.lower(), "Score line should mention white"
    assert "black" in score_line.lower(), "Score line should mention black"
    assert "10" in score_line, "Score line should include white score"
    assert "8" in score_line, "Score line should include black score"