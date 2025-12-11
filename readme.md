*** AI/ GPT Summarized Summary of my Raw Developer Notes ***

⸻

🕹️ Othello AI (Minimax with Heuristics)

A fully playable Othello/Reversi game built in Python, featuring:
	•	Human vs Human
	•	Human vs AI
	•	AI vs AI
	•	Weighted heuristic evaluation
	•	Optional alpha-beta pruning for faster search
	•	Debug logging to debug.txt

⸻

🚀 How to Run (RUN FROM TOP LEVEL  "OTHELLO/")

# Run with explicit Python path
python3 -m othello.main

# or if your Python path is set:
python -m othello.main

💡 Run from the project root directory (where the othello/ folder resides).

⸻

🎮 Game Modes

Mode	Description
1	Human vs Human
2	Human (Black) vs AI (White)
3	AI vs AI (auto-plays with pauses)


⸻

⚙️ Project Structure

othello/
├── main.py              # Game entrypoint and loop logic  
├── internal/  
│   ├── board.py         # Board representation, rules, and move logic  
│   ├── minimax.py       # Minimax + alpha-beta pruning AI  
│   ├── heuristics.py    # Evaluation heuristics (disk diff, mobility, corners, etc.)  
│   ├── cli.py           # Input/output, board rendering  
│   ├── log.py           # Debug logger to file and stdout  
│   └── utils.py         # Helper functions (coord conversions, bounds, etc.)  
└── debug.txt            # Created automatically when debug mode is active  



⸻

🧠 Heuristics Implemented

Each heuristic contributes to the AI’s evaluation function:

Heuristic	Description
Disk Difference	Counts the difference between your pieces and your opponent’s
Mobility	Measures how many legal moves each player has
Corner Control	Rewards owning corners, which can’t be flipped
X-Square Penalty	Penalizes owning diagonally adjacent squares to unclaimed corners
(Planned) Stable Disks	Will estimate permanently safe disks later in development


⸻

⚡ Alpha-Beta Pruning

Alpha-Beta pruning is an optimization built on top of Minimax.
It skips exploring branches that cannot possibly influence the final decision — effectively reducing the number of evaluated nodes without changing the result.

How it works (simplified):
	•	alpha = the best value the maximizing player can guarantee so far
	•	beta  = the best value the minimizing player can guarantee so far
	•	If at any point beta <= alpha, the algorithm stops exploring that branch (“cutoff”), since it won’t affect the final decision.

This pruning drastically speeds up deeper searches, especially when good move ordering is used (e.g., corners first).

⸻

🔧 Enabling / Disabling Alpha-Beta Pruning

You can control pruning from the Minimax constructor inside main.py:

# With pruning (default and recommended)
minimax = Minimax(depth=4, alpha_beta=True, debug=True)

# Without pruning (explores all nodes, slower but exhaustive)
minimax = Minimax(depth=4, alpha_beta=False, debug=True)

💡 When debug=True, pruning events will appear in debug.txt (e.g. [debug] root alpha-beta cutoff).

⸻

🪵 Debug Logging

When debug mode is enabled:
	•	All dprint() output is mirrored to debug.txt
	•	The log file is created automatically next to main.py
	•	It includes move selections, heuristic evaluations, and game results

⸻

🧩 Notes
	•	Default AI depth is 4, adjustable in the Minimax constructor.
	•	The terminal view clears between turns but logs remain fully preserved.
	•	Requires Python ≥ 3.8.

