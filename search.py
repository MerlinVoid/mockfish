"""search.py - Role: Adversarial Search & Optimization
===================================================
Project: Mockfish AI Chess Engine
Author: Team Mockfish (Search Specialist)

Responsibilities:
- Implement adversarial game tree search (Minimax, Alpha-Beta pruning).
- Implement move ordering heuristics to maximize alpha-beta cutoffs.
- Provide iterative deepening (IDDFS) and time management.
- Calculate telemetry metrics (nodes visited, search depth, effective branching factor).
"""

import math
from typing import Optional, Union
import chess

from heuristics import evaluate_board

# Module-level telemetry dictionary to store metrics from the most recent search
LAST_SEARCH_TELEMETRY: dict[str, Union[int, float]] = {
    "depth": 0,
    "nodes": 0,
    "eval": 0.0,
}


def order_moves(board: chess.Board) -> list[chess.Move]:
    """Orders legal moves to maximize alpha-beta pruning efficiency.

    Good move ordering explores the strongest candidate moves first, triggering
    early beta-cutoffs and dramatically reducing the effective branching factor.

    Current Stub Heuristics:
    1. Captures first (sorted by victim value or simple capture flag)
    2. Moves that deliver check
    3. Pawn promotions
    4. Quiet moves

    Syllabus & Coursework Extension Points for Search Teammate:
    ----------------------------------------------------------
    - MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
    - Killer Move Heuristic (store 2 quiet moves per ply that caused cutoffs)
    - History Heuristic (table of moves causing cutoffs across all depths)
    - Transposition Table (hash move ordered first)
    """
    def move_priority(move: chess.Move) -> int:
        score = 0
        # Check captures
        if board.is_capture(move):
            score += 100
            # Bonus if capturing with lower-value piece or capturing higher-value piece
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                score += captured_piece.piece_type * 10

        # Check promotions
        if move.promotion:
            score += 80

        # Check giving check
        if board.gives_check(move):
            score += 50

        return score

    return sorted(board.legal_moves, key=move_priority, reverse=True)


def alpha_beta(
    board: chess.Board,
    depth: int,
    alpha: float,
    beta: float,
    is_max: bool
) -> float:
    """Minimax search algorithm with Alpha-Beta pruning.

    Args:
        board: Current chess.Board state.
        depth: Remaining search depth (plies).
        alpha: Best score the maximizing player can guarantee so far (-inf to +inf).
        beta: Best score the minimizing player can guarantee so far (-inf to +inf).
        is_max: True if currently evaluating for the maximizing player (White),
                False for minimizing player (Black).

    Returns:
        float: Heuristic evaluation of the position at the leaf or horizon node.

    Syllabus & Coursework Extension Points for Search Teammate:
    ----------------------------------------------------------
    1. Quiescence Search:
       - At depth 0, continue searching only capture moves to avoid the horizon effect.
    2. Transposition Tables (TT):
       - Store (Zobrist hash -> depth, flag, eval, best_move) to avoid re-evaluating
         identical positions reached via different move transpositions.
    3. Null-Move Pruning & Late Move Reductions (LMR):
       - Advanced pruning techniques to search deeper along promising branches.
    """
    global LAST_SEARCH_TELEMETRY
    LAST_SEARCH_TELEMETRY["nodes"] = int(LAST_SEARCH_TELEMETRY["nodes"]) + 1

    # Base case: Horizon reached or terminal game state (checkmate/draw)
    if depth == 0 or board.is_game_over():
        return evaluate_board(board)

    ordered_moves = order_moves(board)

    if is_max:
        max_eval = -math.inf
        for move in ordered_moves:
            board.push(move)
            eval_score = alpha_beta(board, depth - 1, alpha, beta, False)
            board.pop()

            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                # Beta cutoff: Minimizing player will avoid this branch
                break
        return max_eval
    else:
        min_eval = math.inf
        for move in ordered_moves:
            board.push(move)
            eval_score = alpha_beta(board, depth - 1, alpha, beta, True)
            board.pop()

            min_eval = min(min_eval, eval_score)
            beta = min(beta, eval_score)
            if beta <= alpha:
                # Alpha cutoff: Maximizing player will avoid this branch
                break
        return min_eval


def get_best_move(
    board: chess.Board,
    max_depth: int = 3,
    return_eval: bool = False
) -> Union[Optional[chess.Move], tuple[Optional[chess.Move], float]]:
    """Determines the optimal move for the current side to move using Alpha-Beta search.

    Args:
        board: The current chess.Board.
        max_depth: Maximum ply search depth (default: 3).
        return_eval: If True, returns a tuple of (best_move, eval_score).
                     If False, returns just best_move (standard interface).

    Returns:
        chess.Move | tuple[chess.Move, float] | None:
        The best legal move found, or None if no legal moves exist (game over).

    Syllabus & Coursework Extension Points for Search Teammate:
    ----------------------------------------------------------
    1. Iterative Deepening Depth-First Search (IDDFS):
       - Loop depth from 1 to max_depth (or until time limit expired).
       - Enables reliable move return within strict per-move time budgets.
    2. Principal Variation (PV) Extraction:
       - Extract the full line of anticipated play (e.g., e2e4 e7e5 g1f3 b8c6).
    """
    global LAST_SEARCH_TELEMETRY
    LAST_SEARCH_TELEMETRY["nodes"] = 0
    LAST_SEARCH_TELEMETRY["depth"] = max_depth

    legal_moves = order_moves(board)
    if not legal_moves:
        LAST_SEARCH_TELEMETRY["eval"] = 0.0
        return (None, 0.0) if return_eval else None

    # White maximizes, Black minimizes
    is_white_to_move = (board.turn == chess.WHITE)

    best_move: Optional[chess.Move] = legal_moves[0]
    best_eval = -math.inf if is_white_to_move else math.inf
    alpha = -math.inf
    beta = math.inf

    for move in legal_moves:
        board.push(move)
        # Next ply is opponent's turn: if White moved, opponent is minimizing (False)
        eval_score = alpha_beta(board, max_depth - 1, alpha, beta, not is_white_to_move)
        board.pop()

        if is_white_to_move:
            if eval_score > best_eval:
                best_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
        else:
            if eval_score < best_eval:
                best_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)

    LAST_SEARCH_TELEMETRY["eval"] = best_eval

    if return_eval:
        return best_move, best_eval
    return best_move


def get_last_telemetry() -> dict[str, Union[int, float]]:
    """Returns a snapshot of search telemetry from the most recent get_best_move call."""
    return dict(LAST_SEARCH_TELEMETRY)


if __name__ == "__main__":
    # Quick self-test for development
    test_board = chess.Board()
    print("[Search Test] Running Minimax Alpha-Beta at depth 3...")
    move, score = get_best_move(test_board, max_depth=3, return_eval=True)
    telemetry = get_last_telemetry()
    print(f"[Search Test] Selected Move: {move} | Eval: {score:.2f} | Telemetry: {telemetry}")
    assert move is not None, "Search should return a valid legal move"
    print("Search stub test passed successfully!")
