import pytest
from othello.internal.minimax import (
    Minimax,
    # other necessary imports later
)

# ============================== test reset_counters ==============================
def test_reset_counters():
    minimax = Minimax()
    minimax.nodes_searched = 42
    minimax.move_evals = [((0,0), 10), ((1,1), -5)]
    
    minimax.reset_counters()
    
    assert minimax.nodes_searched == 0, "nodes_searched should be reset to 0"
    assert minimax.move_evals == [], "move_evals should be reset to empty list"

# ============================== test choose_move ==============================
def test_choose_move_no_legal_moves():
    minimax = Minimax()
    
    class MockBoard:
        def __init__(self):
            self.size = 8  # standard board size
        def legal_moves(self, color):
            return []  # No legal moves
    
    board = MockBoard()
    move = minimax.choose_move(board, color=1)
    
    assert move is None, "choose_move should return None when there are no legal moves"

# ============================== test choose_move with legal moves (mocked minimax) ==============================
def test_choose_move_picks_best_move(mocker):
    """
    choose_move should call minimax() once per legal move and return the move
    with the highest evaluation score.
    """
    minimax = Minimax(depth=2, alpha_beta=True, debug=False)
    
    # Simple board with 3 legal moves
    class MockBoard:
        def __init__(self):
            self.calls = []
            self.size = 8  # standard board size
        
        def legal_moves(self, color):
            return [(0,0), (1,1), (2,2)]
        
        def copy(self):
            return self  # Not used deeply in this test
        
        def apply_move(self, r, c, color):
            pass  # No-op
    
    board = MockBoard()
    
    # Patch minimax.minimax to return predictable scores for each move
    # Order matches legal_moves above
    mocker.patch.object(minimax, "minimax", side_effect=[5, 10, -3])
    
    best_move = minimax.choose_move(board, color=1)
    
    assert best_move == (1,1), "choose_move should select the move with the highest evaluation"
    
    # move_evals should store all move-eval pairs
    assert minimax.move_evals == [
        ((0,0), 5),
        ((1,1), 10),
        ((2,2), -3),
    ], "move_evals should record each legal move and its returned minimax value"

# ============================== test minimax base case ==============================
def test_minimax_base_case_calls_evaluate(mocker):
    """
    If depth == 0 or board.is_end() returns True,
    minimax should immediately call evaluate() and return that value.
    """
    minimax = Minimax()
    minimax.root_color = 1  # Required for the evaluate(board, root_color) call
    
    class MockTerminalBoard:
        def is_end(self):
            return True  # Force immediate base case
    
    board = MockTerminalBoard()
    
    # Patch evaluate() to return a predictable value
    mock_eval = mocker.patch(
        "othello.internal.minimax.evaluate",
        return_value=123
    )
    
    result = minimax.minimax(
        board=board,
        depth=5,            # depth > 0 shouldn't matter because is_end() stops early
        alpha=float('-inf'),
        beta=float('inf'),
        maximizing_player=True,
    )
    
    assert result == 123, "minimax should return the evaluate() result during the base case"
    mock_eval.assert_called_once_with(board, minimax.root_color)

# ============================== test alpha-beta pruning ==============================
def test_alpha_beta_pruning_stops_early(mocker):
    """
    When alpha >= beta, minimax should prune remaining branches and
    avoid calling minimax() for later moves.
    """
    minimax = Minimax(depth=3, alpha_beta=True, debug=False)

    # Mock board with 3 legal moves
    class MockBoard:
        def legal_moves(self, color):
            return [(0,0), (1,1), (2,2)]
        
        def copy(self):
            return self
        
        def apply_move(self, r, c, color):
            pass
        size = 8  # standard board size

    board = MockBoard()

    # Mock the minimax method to simulate pruning:
    # - First move returns a HIGH value (forcing alpha to rise)
    # - Second move returns a value that causes beta <= alpha
    # - Third move SHOULD NEVER be evaluated (pruned)
    mock_minimax = mocker.patch.object(
        minimax,
        "minimax",
        side_effect=[float("inf"), 0, 0]  # third call should not happen
    )

    # Run choose_move to trigger the minimax loop/pruning
    minimax.choose_move(board, color=1)

    # Should only call minimax twice, NOT three times
    assert mock_minimax.call_count == 1, ( # call_count is a built-in attribute of mock objects that tracks how many times the mock was called
        "Alpha-beta pruning should skip evaluating later moves after cutoff. Instead it got {} calls.".format(mock_minimax.call_count)
    )

# ============================== test _inorder (move ordering) ==============================
def test_inorder_prioritizes_corners():
    minimax = Minimax()
    
    # MockBoard only needs a .size attribute for _inorder behavior
    class MockBoard:
        def __init__(self):
            self.size = 8  # Standard Othello board size
    
    board = MockBoard()
    
    # Mix of corner and non-corner moves
    moves = [
        (3, 3),   # Center
        (0, 0),   # Corner
        (7, 7),   # Corner
        (2, 5),   # Edge / other
    ]
    
    ordered = minimax._inorder(board, color=1, moves=moves)
    
    # The first two should be corners
    assert ordered[0] in [(0,0), (7,7)]
    assert ordered[1] in [(0,0), (7,7)]
    
    # All moves should still be present (no loss or duplication)
    assert set(ordered) == set(moves), "All moves must be preserved by _inorder"