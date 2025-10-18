### Pseudocode reference

Used pseudocode from [Pastebin: rZg1Mz9G](https://pastebin.com/rZg1Mz9G) as a reference for implementing the Othello game logic. Key areas informed by the pseudocode:

- Move generation and validation
- Flipping pieces along valid directions
- Turn handling and end-of-game conditions

Notes:
- Adapted to fit the project's data structures and coding conventions.
- Refer to the linked paste for the original algorithm outline.

### Movement Rules
After brainstorming with GPT we decided that itd be best just to use an array of directions to
determine if a rule was legal
```
DIRECTIONS = [(-1, -1), (-1, 0), (-1, 1),       # Valid directions for move checking
              (0, -1),          (0, 1),
              (1, -1),  (1, 0),  (1, 1)]
```

### Board Headers
- Had GPT show me how to create alphabetic column headers for the board (e.g., a..h).
- Example used: cols = "  " + " ".join([chr(ord('a') + i) for i in range(self.size)])

- Printing legal moves
   ```print("Legal moves: " + ",".join(
            f"{chr(ord('a') + c)}{r + 1}" for r, c in moves # for each (row, col) in moves (list of tuples) (in worklog)
        ))```
        
    -- Moved this logic into utils.py and made a to_algebra & from_algebra method per GPT recommendation


## Heuristics

- I was unfamiliar with the game of Othello before starting this program. After a short google search for 
`best Othello Strategies` I found [this](https://www.othello.nl/content/guides/comteguide/strategy.html) doc explaining some common strategy. All heuristics are based on this Document. For brevity these are the key points:

Absolutely — this is the right moment to get clear on heuristics before just plugging one in.

Let’s step back and make this intuitive.

⸻

🎯 What is a heuristic?

A heuristic is an estimate of how good a board position is right now, when the game is not finished and we don’t want to simulate all the way to the end.

Minimax only sees ahead a few moves (because looking too deep is too slow).
So when minimax reaches depth = 0, it asks:

“Is this position good for me or not?”

That answer is the heuristic score.

1) Disc Difference

#my pieces − #their pieces

* Good in late game
Misleading early (you can be ahead but losing positionally)

2) Mobility

#my legal moves − #their legal moves

 Very strong early/mid game
If you reduce your opponent’s mobility → you force them into bad moves.

3) Corner Control

+5 points for each corner you own
-5 points for each corner opponent owns

 Corners are extremely stable → consistently good signal
Very strong heuristic.

4) X-Square Penalty

(X-squares are diagonally touching corners)

If you play an X-square too early:
	•	opponent almost always gets that corner next
	•	which is strategically devastating

So penalize owning X-squares unless the corresponding corner is already secure.

5) Stability

Discs that cannot be flipped again (often along edges or forming blocks).
Hardest to compute, but very strong late game signal.

⸻

 TL;DR (plain English explanation)
	•	Minimax looks a few moves ahead.
	•	It needs a guess of how good the board is now.
	•	We build that guess based on what actually wins Othello:
	•	Don’t take lots of pieces too early.
	•	Keep mobility.
	•	Fight for corners.
	•	Avoid X-squares unless stable.
	•	We weight these signals.
	•	That weighted score is the heuristic.

