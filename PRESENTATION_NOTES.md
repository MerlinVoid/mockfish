# Mockfish Presentation & Speaker Notes
## Course: Introduction to AI with Python (25CS2000)
## Slides File: `Mockfish_Presentation.pptx`

---

### Slide 1: Title & Team Introductions
* **Title**: MOCKFISH: An Intelligent Knowledge-Guided Adversarial Chess Engine & Interactive GUI
* **Course**: Introduction to AI with Python (25CS2000)
* **Team Members**:
  1. **B Sreenikesh** (`CS25B2051`) --- Logic & Rules Specialist
  2. **Aditya Kumar** (`CS25I1050`) --- State Space & Heuristics Specialist
  3. **Amit Kumar** (`CS25I1051`) --- Adversarial Search Specialist
  4. **Aviral Pandey** (`CS25B2054`) --- GUI, Systems Integrator & Benchmarking Specialist
* **Speaker Script (Aviral Pandey)**:
  > "Good morning/afternoon, Professor and peers. Today, our 4-person team is presenting **Mockfish**, a modular, tournament-capable AI chess engine and interactive graphical user interface built from the ground up in Python. In this presentation, we will walk you through our formal state-space formulation, the five AI algorithms we implemented from the course, our empirical benchmark metrics showing a 156x speedup, and a live demonstration of our application."

---

### Slide 2: Problem Formulation & AI Motivation
* **Key Visual**: Formal 7-Tuple $\mathcal{M} = \langle S_0, Actions, Result, Constraints, Terminal\_Test, Utility, Heuristic \rangle$.
* **Speaker Script (Aditya Kumar)**:
  > "Why chess? Chess is the classical benchmark for strategic decision-making in adversarial multi-agent environments. With an average branching factor of $b \approx 35$ and a theoretical state space exceeding $10^{120}$ configurations, exhaustive search is computationally impossible. We formulated chess as a zero-sum, perfect-information game with strict invariants—specifically King safety and check evasion. Our utility function incorporates distance-to-mate ply adjustments, ensuring the agent prioritizes the fastest checkmates when winning and maximum survival delays when defending."

---

### Slide 3: System Architecture & Workflow (Visualization 1)
* **Embedded Image**: `viz_architecture.png` (Decision Pipeline Diagram).
* **Speaker Script (B Sreenikesh)**:
  > "As shown in our architecture diagram, Mockfish employs a hybrid decision pipeline. When the human moves, the board state is first routed to the **Knowledge Base** (`knowledge_base.py`). If the position matches textbook opening theory, it returns an instant $O(1)$ move with zero search latency. When moving off-book, control passes to **Adversarial Search** (`search.py`), which executes Minimax with Alpha-Beta pruning and move ordering. At the search horizon, leaf states are evaluated by our **Heuristic Engine** (`heuristics.py`), and the optimal move is dispatched back to the Tkinter GUI."

---

### Slide 4: Key AI Algorithms Implemented
* **Key Pillars**:
  1. Knowledge-Based Expert System (Opening Book $O(1)$)
  2. Minimax with Alpha-Beta Pruning (Branch-and-Bound cutoffs)
  3. Heuristic Move Ordering (MVV-LVA, promotions, castling, checks)
  4. State Space Heuristic Evaluation (PeSTO Piece-Square Tables + King Safety)
  5. Iterative Deepening Depth-First Search (IDDFS Anytime Algorithm)
* **Speaker Script (Amit Kumar)**:
  > "To exceed syllabus requirements, we implemented five distinct AI algorithms. Our search engine uses Alpha-Beta pruning to discard branches where $\beta \le \alpha$. To maximize early cutoffs, we designed a tactical move ordering heuristic prioritizing captures using MVV-LVA (Most Valuable Victim, Least Valuable Attacker), pawn promotions, castling, and checks. Non-terminal leaf nodes are evaluated using PeSTO Piece-Square Tables with vertical reflection symmetry, rewarding king safety and central piece activity."

---

### Slide 5: Empirical Benchmarks & Performance Metrics (Visualization 2)
* **Embedded Image**: `viz_benchmark.png` (Search Tree Size & Execution Time Bar Charts).
* **Speaker Script (Aviral Pandey)**:
  > "To evaluate algorithm effectiveness, we wrote a dedicated benchmarking engine (`benchmark.py`). In this tactical exchange position at depth 3, Pure Minimax evaluated 52,088 nodes and took 41 seconds. With Alpha-Beta and our heuristic move ordering, node count dropped to just **378 nodes**—a **99.27% pruning efficiency**! Wall-clock execution time plummeted from 41 seconds to **0.26 seconds**, representing a **156.6x computational speedup**, while reducing the effective branching factor from $b_{eff} = 37.35$ down to $7.23$."

---

### Slide 6: Algorithmic Justification (Why This Approach?)
* **Comparison Matrix**:
  * *Uninformed Search (BFS/DFS)*: Rejected due to catastrophic $O(b^d)$ memory explosion and inability to model adversary.
  * *A\* Search*: Rejected because A* is designed for single-agent pathfinding toward static goals; in chess, the opponent actively alters the utility landscape.
  * *Hill Climbing / Local Search*: Rejected due to fatal local traps (grabs a free pawn, gets checkmated next ply).
  * *Deep Reinforcement Learning*: Rejected due to massive compute/GPU training requirements and lack of deterministic explainability.
  * *Mockfish Approach*: Provably optimal, $O(bd)$ minimal memory footprint, $156.6\times$ speedup, and transparently explainable.
* **Speaker Script (Amit Kumar)**:
  > "A core requirement was justifying our technique over alternatives studied in class. Uninformed BFS crashes due to exponential memory exhaustion. A* cannot model adversarial counter-play where the opponent minimizes our score. Local search like Hill Climbing blunders into checkmate because it lacks lookahead. Our hybrid Alpha-Beta approach delivers provably optimal play within the horizon, requires minimal memory, and runs in real time on any consumer CPU."

---

### Slide 7: Interactive GUI & Bug Resolution
* **Highlights**:
  * Event-driven 512x512 Tkinter Canvas with coordinate mapping and board flipping.
  * Fixed Windows modal thread freezes by replacing OS dialogs with a custom in-canvas Game Over overlay card ("Play Again" / "Review Board").
  * Cured the rook-shuffling loop via PeSTO PST positional penalties and 2-fold repetition filters.
* **Speaker Script (Aviral Pandey)**:
  > "During gameplay testing, we resolved two critical software glitches. First, native OS message boxes froze the event loop on Windows; we eliminated this by engineering an in-canvas Game Over overlay card with interactive 'Play Again' and 'Review Board' buttons. Second, we resolved an issue where the bot shuffled its rook back and forth by integrating PeSTO positional tables and 2-fold repetition filters."

---

### Slide 8: Team Roles & Contributions
* **Breakdown**:
  * **B Sreenikesh**: `knowledge_base.py` --- Opening book, FEN pattern matching, propositional logic.
  * **Aditya Kumar**: `heuristics.py` --- Material weighting, PeSTO PST, castling & king safety bonuses.
  * **Amit Kumar**: `search.py` --- Minimax, Alpha-Beta pruning, MVV-LVA move ordering, repetition filters.
  * **Aviral Pandey**: `main.py`, `benchmark.py`, `test_suite.py` --- Tkinter Canvas, Game Over overlay, automated testing, benchmarking.
* **Speaker Script (B Sreenikesh)**:
  > "To ensure seamless collaboration, our codebase was partitioned into four decoupled modules. Each member owned a specific file with locked interfaces, resulting in zero Git merge conflicts and complete unit-test coverage verified by `test_suite.py`."

---

### Slide 9: Conclusion & Summary
* **Highlights**:
  * Successful synthesis of Knowledge Bases, Minimax, Alpha-Beta, Move Ordering, PST Heuristics, and IDDFS.
  * 99.27% pruning efficiency and 156.6x speedup.
  * Future enhancements: Quiescence Search (mitigating horizon effect), Transposition Tables (Zobrist hashing), Dynamic Time Management.
* **Speaker Script (All Members / Aviral Pandey)**:
  > "In conclusion, Mockfish demonstrates how classical Artificial Intelligence principles can be synthesized into an effective, high-performance real-world application. The entire project—source code, test suite, benchmark runner, formal LaTeX report, and this presentation—is publicly available on GitHub. Thank you, and we welcome your questions!"
