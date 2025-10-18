# main.py

from __future__ import annotations
from pathlib import Path


from .internal.board import Board, WHITE, BLACK
from .internal.cli import parse_move, display_board
from .internal.minimax import Minimax
from .internal.utils import to_algebra, from_algebra
from .internal.log import dprint, LOGGER

run = True
def main() -> None:
    board = Board.initial()
    minimax = Minimax(depth=4, alpha_beta=True, debug=True)
    log_path = (Path(__file__).resolve().parent / "debugs"/"debug.txt").as_posix()
    if minimax.debug:
        LOGGER.start(str(log_path))
        dprint(f"[debug] logging to: {log_path}")
    to_move = BLACK  # Othello traditionally starts with black
    names = {WHITE: "White (●)", BLACK: "Black (○)"}
    run = True

    dprint("Welcome to Othello!")
    dprint(
        "Select Mode:\n"
        "1. Human vs Human\n"
        "2. Human vs AI\n"
        "3. AI vs AI\n"
        "> ",
        end=""
    )
    mode = input().strip()

    if mode == "1":
        dprint("Human vs Human mode selected.")
    elif mode == "2":
        dprint("Human vs AI mode selected.")
    elif mode == "3":
        dprint("AI vs AI mode  currently broken, defaulting to Human vs AI.")
        #mode = "2"
    else:
        dprint("Invalid mode selected. Defaulting to Human vs AI.")
        mode = "2"



    # main game loop
    while not board.is_end(): 
        dprint("mode from loop: " + mode)
        display_board(board)
        moves = board.legal_moves(to_move)

        if not moves:
            # Pass turn
            dprint(f"\n{names[to_move]} has no legal moves and must pass. Press Enter to continue.")
            input()
            to_move = -to_move
            continue

        dprint(f"\n{names[to_move]} to move. Enter (e.g., d3) or type 'ai'. Type 'q' to quit:")
        dprint("Legal moves: " + ",".join(
            f"{chr(ord('a') + c)}{r + 1}" for r, c in moves # for each (row, col) in moves (list of tuples) (in worklog)
        ))

        # Handle AI vs AI mode
        if mode == "3":
            if WHITE == to_move:
                dprint("AI (White) is thinking...")
                raw = "ai"
            else:
                dprint("AI (Black) is thinking...")
                raw = "ai"

        # if mode != "3":
        #     raw = input("> ").strip()
        if mode != "3":
            raw = "ai" if (mode == "2" and to_move == WHITE) else input("> ").strip()
        if raw.lower() in {"q", "quit", "exit"}:
            break

        # Handle Human vs AI mode
        # Handle Human vs AI mode (Black = Human, White = AI)
        # if mode == "2":
        #     raw = "ai" if to_move == WHITE else input("> ").strip()
        # if mode == "2":
        #     if to_move == WHITE:
        #         raw = "ai"
        #     if (to_move == BLACK and raw.lower() == "ai") or (to_move == WHITE and raw.lower() != "ai"): # if
        #         dprint("It's the human player's turn. Please enter your move.")
                


        # Handle AI move
        if raw.lower() == "ai":
            dprint("AI is thinking...")
            ai_move = minimax.choose_move(board, to_move)
            if ai_move is None:
                dprint("AI has no legal moves and must pass. Press Enter to continue.")
                input() # wait for user to press enter
                to_move = -to_move # switch turns
                continue # go to next iteration of while loop
            # apply AI move & display
            r, c = ai_move
            dprint(f"AI chooses move: {to_algebra((r, c))}. Press Enter to continue.")
            input()
            board.apply_move(r, c, to_move)
            to_move = -to_move
            continue


        mv = parse_move(raw)
        if mv is None:
            dprint("Invalid format. Use letter+number like d3. Press Enter.")
            input()
            continue

        r, c = mv
        try:
            board.apply_move(r, c, to_move)
            to_move = -to_move
        except ValueError:
            dprint("Illegal move for current player. Press Enter.")
            input()

    display_board(board)
    s = board.score()
    if s["white"] > s["black"]:
        run = False
        dprint("\nGame over. White (●) wins!")
    elif s["black"] > s["white"]:
        run = False
        dprint("\nGame over. Black (○) wins!")
    else:
        run = False
        dprint("\nGame over. Draw!")
LOGGER.stop()
print("Reached end of main()")
if run == True:
    main()


# helpers
# Not used due to bugs in mode handling above
def is_ai_turn(mode: str, to_move: int) -> bool:
    # Mode 3: both sides are AI
    if mode == "3":
        return True
    # Mode 2: AI plays White, human plays Black
    if mode == "2":
        return to_move == WHITE
    # Mode 1: no AI
    return False