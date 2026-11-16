"""heuristics.py - Role: State Space & Heuristic Evaluation
===========================================================
Project: Mockfish AI Chess Engine
Author: Team Mockfish (Heuristics Specialist)

Responsibilities:
- Provide static evaluation functions for non-terminal board states.
- Quantify material balances, positional advantages, and board dynamics.
- Formulate heuristic scoring used by Minimax and Alpha-Beta search.
"""

import chess

# Standard chess piece material weights (P=1, N=3, B=3, R=5, Q=9)
# Positive scores favor White; negative scores favor Black.
PIECE_VALUES: dict[chess.PieceType, float] = {
    chess.PAWN: 1.0,
    chess.KNIGHT: 3.0,
    chess.BISHOP: 3.0,
    chess.ROOK: 5.0,
    chess.QUEEN: 9.0,
    chess.KING: 0.0,  # King cannot be captured; checkmate handled separately
}

# Large finite constant for terminal checkmate evaluations
CHECKMATE_SCORE = 10000.0


def evaluate_board(board: chess.Board) -> float:
    """Computes a heuristic score for the given board position.

    The score is computed from White's perspective:
      - Positive score (> 0): White has the advantage.
      - Negative score (< 0): Black has the advantage.
      - Zero score (= 0): Balanced position or draw.

    Args:
        board: The current chess.Board state to evaluate.

    Returns:
        float: The static evaluation score of the board.

    Syllabus & Coursework Extension Points for Heuristics Teammate:
    --------------------------------------------------------------
    1. Piece-Square Tables (PST):
       - Give bonuses/penalties based on piece coordinates (e.g., knights in the center,
         pawns advancing toward promotion, king safely castled).

    2. Positional Heuristics:
       - Mobility: Difference in the number of legal moves (White legal moves - Black legal moves).
       - Pawn Structure: Penalize doubled, isolated, and backward pawns; bonus for passed pawns.
       - Center Control: Count attacks/control over squares d4, d5, e4, e5.
       - Bishop Pair Bonus: Reward having both light-squared and dark-squared bishops (+0.5).

    3. King Safety & Phase of Game:
       - Tapered evaluation: Transition weights smoothly between Opening, Middlegame, and Endgame.
       - Pawn shield evaluation around the castled king.
    """
    # 1. Terminal State Evaluations (Checkmate / Draw)
    if board.is_checkmate():
        # If it's White's turn and White is checkmated -> Black wins (-CHECKMATE_SCORE)
        # If it's Black's turn and Black is checkmated -> White wins (+CHECKMATE_SCORE)
        return -CHECKMATE_SCORE if board.turn == chess.WHITE else CHECKMATE_SCORE

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0.0

    # 2. Material Difference Stub
    # Sum of White pieces - Sum of Black pieces
    score = 0.0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            value = PIECE_VALUES.get(piece.piece_type, 0.0)
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value

    return score


if __name__ == "__main__":
    # Quick self-test for development
    test_board = chess.Board()
    initial_eval = evaluate_board(test_board)
    print(f"[Heuristics Test] Initial Board Eval: {initial_eval:.2f} (Expected: 0.00)")
    assert initial_eval == 0.0, "Starting position material difference should be 0.0"

    # Simulate White winning a pawn (1. e4 d5 2. exd5)
    test_board.push_san("e4")
    test_board.push_san("d5")
    test_board.push_san("exd5")
    pawn_up_eval = evaluate_board(test_board)
    print(f"[Heuristics Test] White up a pawn: {pawn_up_eval:.2f} (Expected: +1.00)")
    assert pawn_up_eval == 1.0, "White up a pawn should evaluate to +1.0"
    print("Heuristics stub test passed successfully!")
