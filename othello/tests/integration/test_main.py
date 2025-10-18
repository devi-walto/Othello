# othello/tests/integration/test_main.py

import pytest
import importlib


# ========================== helpers for safe import ==========================
def _safe_import_main(monkeypatch, input_values):
    """
    Helper to import `othello.main` safely:
    - Patches builtins.input to use provided values
    - Patches LOGGER.start/stop to avoid file I/O
    - Then imports the module (which may call main() at import time)
    """
    # Turn the list of inputs into an iterator
    inputs = iter(input_values)

    # Patch input() so the main loop never blocks waiting for real user input
    monkeypatch.setattr(
        "builtins.input",
        lambda prompt="": next(inputs),
    )

    # Patch LOGGER to avoid writing real debug files during tests
    import othello.internal.log as logmod
    monkeypatch.setattr(logmod.LOGGER, "start", lambda filename="debug.txt": None)
    monkeypatch.setattr(logmod.LOGGER, "stop", lambda: None)

    # Import othello.main AFTER patches so any top-level main() call is safe
    main_module = importlib.import_module("othello.main")
    return main_module


# ========================== test is_ai_turn helper ==========================
def test_is_ai_turn_logic(monkeypatch):
    """
    Test the is_ai_turn() helper to make sure it decides correctly
    based on mode and which color is to move.
    """
    # Inputs for any main() that might run at import-time:
    # - First input: mode selection (e.g., '2' for Human vs AI)
    # - Second input: 'q' so the game loop exits immediately
    main_module = _safe_import_main(monkeypatch, input_values=["2", "q"])

    # Get WHITE/BLACK from the main module (main.py re-exports them)
    WHITE = main_module.WHITE
    BLACK = main_module.BLACK

    # Sanity check: function exists
    assert hasattr(main_module, "is_ai_turn"), "main module should expose is_ai_turn()"

    is_ai_turn = main_module.is_ai_turn

    # Mode 3: AI vs AI -> always AI's turn
    assert is_ai_turn("3", WHITE) is True, "In mode 3, WHITE should always be AI"
    assert is_ai_turn("3", BLACK) is True, "In mode 3, BLACK should always be AI"

    # Mode 2: Human vs AI (AI plays WHITE)
    assert is_ai_turn("2", WHITE) is True, "In mode 2, WHITE should be AI"
    assert is_ai_turn("2", BLACK) is False, "In mode 2, BLACK should be human"

    # Mode 1: Human vs Human -> never AI
    assert is_ai_turn("1", WHITE) is False, "In mode 1, WHITE should never be AI"
    assert is_ai_turn("1", BLACK) is False, "In mode 1, BLACK should never be AI"


# ========================== test main quick-run ==========================
def test_main_quick_quit_human_vs_human(monkeypatch):
    """
    Integration-style smoke test:
    - Start in Human vs Human mode (mode '1')
    - Immediately enter 'q' on the first turn to exit
    - Test passes if no exceptions are raised during import / main execution.
    """
    # '1' -> Human vs Human
    # 'q' -> quit immediately on the first move prompt
    main_module = _safe_import_main(monkeypatch, input_values=["1", "q"])

    # We don't assert game result here, just that main() exists and import didn't crash
    assert hasattr(main_module, "main"), "main module should define a main() function"