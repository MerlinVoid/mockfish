"""search.py - Role: Adversarial Search & Optimization
===================================================
Project: Mockfish AI Chess Engine
Author: Team Mockfish (Search Specialist)

Responsibilities:
- Implement adversarial game tree search (Minimax, Alpha-Beta pruning).
- Implement move ordering heuristics to maximize alpha-beta cutoffs.
- Factor distance-to-mate into checkmate evaluations (faster mates preferred).
- Prevent repetitive piece shuffling via repetition detection.
- Provide telemetry metrics (nodes visited, search depth, effective branching factor).
"""

import math
from typing import Optional, Union
import chess

from heuristics import evaluate_board, CHECKMATE_SCORE

# Module-level telemetry dictionary to store metrics from the most recent search
LAST_SEARCH_TELEMETRY: dict[str, Union[int, float]] = {
    "depth": 0,
    "nodes": 0,
    "eval": 0.0,
}


def order_moves(board: chess.Board) -> list[chess.Move]:
    """Orders legal moves to maximize alpha-beta pruning efficiency.

    Explores the strongest candidate moves first, triggering early beta-cutoffs
    and dramatically reducing the effective branching factor.

    Priority Order:
      1. Captures sorted by MVV-LVA (Most Valuable Victim - Least Valuable Attacker)
      2. Pawn promotions (Queen / Knight)
      3. Castling moves (King safety & rook development)
      4. Moves delivering check
      5. Quiet positional moves
    """
    def move_priority(move: chess.Move) -> float:
        score = 0.0

        # 1. Captures (MVV-LVA)
        if board.is_capture(move):
            score += 1000.0
            victim_piece = board.piece_at(move.to_square)
            attacker_piece = board.piece_at(move.from_square)
            victim_val = victim_piece.piece_type if victim_piece else 1
            attacker_val = attacker_piece.piece_type if attacker_piece else 1
            # Victim value dominates; attacker value is tie-breaker (pawn takes queen > queen takes queen)
            score += victim_val * 100.0 - attacker_val * 10.0

        # 2. Pawn Promotions
        if move.promotion:
            if move.promotion == chess.QUEEN:
                score += 800.0
            elif move.promotion == chess.KNIGHT:
                score += 500.0
            else:
                score += 200.0

        # 3. Castling (strongly encouraged early for king safety)
        if board.is_castling(move):
            score += 300.0

        # 4. Giving Check
        if board.gives_check(move):
            score += 150.0

        # 5. Central Development (Knights and Bishops moving toward center)
        moving_piece = board.piece_at(move.from_square)
        if moving_piece and moving_piece.piece_type in (chess.KNIGHT, chess.BISHOP):
            if move.to_square in (chess.D4, chess.E4, chess.D5, chess.E5, chess.C3, chess.F3, chess.C6, chess.F6):
                score += 40.0

        return score

    return sorted(board.legal_moves, key=move_priority, reverse=True)


def alpha_beta(
    board: chess.Board,
    depth: int,
    alpha: float,
    beta: float,
    is_max: bool
) -> float:
    """Minimax search algorithm with Alpha-Beta pruning, ply-aware checkmate,
    and repetition detection.

    Args:
        board: Current chess.Board state.
        depth: Remaining search depth (plies).
        alpha: Best score the maximizing player can guarantee so far (-inf to +inf).
        beta: Best score the minimizing player can guarantee so far (-inf to +inf).
        is_max: True if currently evaluating for the maximizing player (White),
                False for minimizing player (Black).

    Returns:
        float: Heuristic evaluation of the position at the leaf or horizon node.
    """
    global LAST_SEARCH_TELEMETRY
    LAST_SEARCH_TELEMETRY["nodes"] = int(LAST_SEARCH_TELEMETRY["nodes"]) + 1

    # Checkmate: ply-adjusted so faster mates are rewarded
    if board.is_checkmate():
        # If it's White's turn, White is checkmated -> Black wins (-CHECKMATE_SCORE)
        # Higher depth remaining = fewer moves to mate = strictly stronger advantage
        return (-CHECKMATE_SCORE - depth) if board.turn == chess.WHITE else (CHECKMATE_SCORE + depth)

    # Draws: Stalemate, insufficient material, 50-move rule, or 2-fold repetition in search
    if (
        board.is_stalemate()
        or board.is_insufficient_material()
        or board.can_claim_fifty_moves()
        or board.is_repetition(2)
    ):
        return 0.0

    # Horizon reached: static evaluation
    if depth == 0:
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
                break  # Beta cutoff
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
                break  # Alpha cutoff
        return min_eval


def get_best_move(
    board: chess.Board,
    max_depth: int = 3,
    return_eval: bool = False
) -> Union[Optional[chess.Move], tuple[Optional[chess.Move], float]]:
    """Determines the optimal move for the current side to move using Alpha-Beta search.

    Includes intelligent tie-breaking:
      - Penalizes moves that immediately repeat a recent position (avoiding rook shuffle loops).
      - Prefers moves with higher positional initiative when scores tie.

    Args:
        board: The current chess.Board.
        max_depth: Maximum ply search depth (default: 3).
        return_eval: If True, returns a tuple of (best_move, eval_score).
                     If False, returns just best_move (standard interface).

    Returns:
        chess.Move | tuple[chess.Move, float] | None:
        The best legal move found, or None if no legal moves exist.
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

    best_eval = -math.inf if is_white_to_move else math.inf
    alpha = -math.inf
    beta = math.inf

    scored_moves: list[tuple[chess.Move, float]] = []

    for move in legal_moves:
        board.push(move)
        eval_score = alpha_beta(board, max_depth - 1, alpha, beta, not is_white_to_move)
        board.pop()

        scored_moves.append((move, eval_score))

        if is_white_to_move:
            if eval_score > best_eval:
                best_eval = eval_score
            alpha = max(alpha, eval_score)
        else:
            if eval_score < best_eval:
                best_eval = eval_score
            beta = min(beta, eval_score)

    LAST_SEARCH_TELEMETRY["eval"] = best_eval

    # Filter all moves that achieve best_eval (within tiny epsilon 0.01)
    epsilon = 0.01
    if is_white_to_move:
        top_candidates = [m for m, s in scored_moves if s >= best_eval - epsilon]
    else:
        top_candidates = [m for m, s in scored_moves if s <= best_eval + epsilon]

    # Tie-breaking against rook shuffling:
    # If a candidate move repeats a position (causes repetition) and other non-repeating
    # candidate moves exist, filter out the repeating moves!
    non_repeating_candidates = []
    for move in top_candidates:
        board.push(move)
        is_rep = board.is_repetition(2)
        board.pop()
        if not is_rep:
            non_repeating_candidates.append(move)

    if non_repeating_candidates:
        # Pick the best non-repeating move (first in ordered priority)
        best_move = non_repeating_candidates[0]
    else:
        best_move = top_candidates[0] if top_candidates else legal_moves[0]

    if return_eval:
        return best_move, best_eval
    return best_move


def get_last_telemetry() -> dict[str, Union[int, float]]:
    """Returns a snapshot of search telemetry from the most recent get_best_move call."""
    return dict(LAST_SEARCH_TELEMETRY)


if __name__ == "__main__":
    # Test 1: Starting position move
    test_board = chess.Board()
    print("[Search Test] Running Minimax Alpha-Beta on starting position...")
    move, score = get_best_move(test_board, max_depth=3, return_eval=True)
    telemetry = get_last_telemetry()
    print(f"[Search Test] Selected Move: {move} | Eval: {score:.2f} | Telemetry: {telemetry}")
    assert move is not None, "Search should return a valid legal move"

    # Test 2: Verify Rook Shuffling is Eliminated
    # In Italian Game, Black should Castle (e8g8) or develop (d7d6/Nf6), NOT shuffle rook (h8g8)
    shuffling_test_board = chess.Board('r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 5 4')
    chosen_move = get_best_move(shuffling_test_board, max_depth=3)
    print(f"[Search Test] Move chosen in Italian Game position: {chosen_move} (UCI)")
    assert chosen_move != chess.Move.from_uci("h8g8"), "Bot MUST NOT shuffle rook to g8 when castling/developing!"

    print("Search stub tests passed successfully!")
