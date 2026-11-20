"""heuristics.py - Role: State Space & Heuristic Evaluation
===========================================================
Project: Mockfish AI Chess Engine
Author: Team Mockfish (Heuristics Specialist)

Responsibilities:
- Provide static evaluation functions for non-terminal board states.
- Quantify material balance, positional advantages, piece activity, and king safety.
- Formulate heuristic scoring used by Minimax and Alpha-Beta search.
"""

import chess

# Large constant for terminal checkmate evaluations
CHECKMATE_SCORE = 20000.0

# Standard chess piece material weights (in pawn units)
# P=1.0, N=3.2, B=3.3, R=5.0, Q=9.0
PIECE_VALUES: dict[chess.PieceType, float] = {
    chess.PAWN: 1.00,
    chess.KNIGHT: 3.20,
    chess.BISHOP: 3.30,
    chess.ROOK: 5.00,
    chess.QUEEN: 9.00,
    chess.KING: 0.00,  # King cannot be captured; checkmate handled separately
}

# =============================================================================
# Piece-Square Tables (PST) - PeSTO / Simplified Evaluation Format
# Values are stored in centipawns from White's perspective (0 = a1, 63 = h8).
# For Black, square coordinates are mirrored vertically using chess.square_mirror.
# =============================================================================

# Pawns: reward center presence and advance; discourage stagnant center pawns
PAWN_PST: list[int] = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10,-20,-20, 10, 10,  5,
     5, -5,-10,  0,  0,-10, -5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
     0,  0,  0,  0,  0,  0,  0,  0,
]

# Knights: strongly reward central control; severely penalize rim/corners
KNIGHT_PST: list[int] = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

# Bishops: reward open diagonals and central scope; penalize blocked corners
BISHOP_PST: list[int] = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

# Rooks: reward central files (d, e) and 7th rank; penalize pointless shuffling
ROOK_PST: list[int] = [
      0,  0,  0,  5,  5,  0,  0,  0,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
     -5,  0,  0,  0,  0,  0,  0, -5,
      5, 10, 10, 10, 10, 10, 10,  5,
      0,  0,  0,  0,  0,  0,  0,  0,
]

# Queens: keep queen safe in early game; centralize gradually
QUEEN_PST: list[int] = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20,
]

# King (Middlegame): heavily reward castling (g1/c1); penalize early king wandering
KING_MID_PST: list[int] = [
     20, 30, 10,  0,  0, 10, 30, 20,
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
]

# King (Endgame): king must centralize and assist pawn promotions
KING_END_PST: list[int] = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50,
]

PIECE_TABLES: dict[chess.PieceType, list[int]] = {
    chess.PAWN: PAWN_PST,
    chess.KNIGHT: KNIGHT_PST,
    chess.BISHOP: BISHOP_PST,
    chess.ROOK: ROOK_PST,
    chess.QUEEN: QUEEN_PST,
}


def is_endgame(board: chess.Board) -> bool:
    """Returns True if the board has transitioned to an endgame phase (no queens or minor pieces only)."""
    white_queens = len(board.pieces(chess.QUEEN, chess.WHITE))
    black_queens = len(board.pieces(chess.QUEEN, chess.BLACK))
    if white_queens == 0 and black_queens == 0:
        return True
    white_minors = len(board.pieces(chess.KNIGHT, chess.WHITE)) + len(board.pieces(chess.BISHOP, chess.WHITE))
    black_minors = len(board.pieces(chess.KNIGHT, chess.BLACK)) + len(board.pieces(chess.BISHOP, chess.BLACK))
    return (white_minors <= 1 and black_minors <= 1)


def evaluate_board(board: chess.Board) -> float:
    """Computes an advanced heuristic score for the given board position.

    The score is computed from White's perspective (in pawn units):
      - Positive score (> 0): White has the advantage.
      - Negative score (< 0): Black has the advantage.
      - Zero score (= 0): Balanced position or draw.

    Includes:
      1. Material balance (P=1.0, N=3.2, B=3.3, R=5.0, Q=9.0)
      2. Piece-Square Tables (PST) for positional placement
      3. Castling rights incentives and castled safety bonuses
      4. Rook open/semi-open file and 7th rank bonuses
      5. Bishop pair advantage
      6. Terminal state evaluations (Checkmate / Draw claims)

    Args:
        board: The current chess.Board state to evaluate.

    Returns:
        float: The static evaluation score in pawn units (e.g., +1.25).
    """
    # 1. Terminal State Evaluations (Checkmate / Draw)
    if board.is_checkmate():
        # If it's White's turn and White is checkmated -> Black wins (-CHECKMATE_SCORE)
        # If it's Black's turn and Black is checkmated -> White wins (+CHECKMATE_SCORE)
        return -CHECKMATE_SCORE if board.turn == chess.WHITE else CHECKMATE_SCORE

    if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_draw():
        return 0.0

    endgame = is_endgame(board)
    king_table = KING_END_PST if endgame else KING_MID_PST

    score = 0.0

    # 2. Material and Piece-Square Table (PST) Evaluation
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is None:
            continue

        ptype = piece.piece_type
        base_val = PIECE_VALUES.get(ptype, 0.0)

        # Get PST value (converted from centipawns to pawn units: / 100.0)
        if ptype == chess.KING:
            table = king_table
        else:
            table = PIECE_TABLES.get(ptype, None)

        if table is not None:
            if piece.color == chess.WHITE:
                pst_val = table[square] / 100.0
            else:
                pst_val = table[chess.square_mirror(square)] / 100.0
        else:
            pst_val = 0.0

        piece_score = base_val + pst_val
        if piece.color == chess.WHITE:
            score += piece_score
        else:
            score -= piece_score

    # 3. Castling Rights and Castled King Safety
    # Reward preserving castling rights; penalize losing them through unnecessary king/rook moves
    if board.has_kingside_castling_rights(chess.WHITE):
        score += 0.20
    if board.has_queenside_castling_rights(chess.WHITE):
        score += 0.15
    if board.has_kingside_castling_rights(chess.BLACK):
        score -= 0.20
    if board.has_queenside_castling_rights(chess.BLACK):
        score -= 0.15

    # Castled King Bonus (White king on g1/c1, Black king on g8/c8 with preserved pawn shield)
    white_king_sq = board.king(chess.WHITE)
    black_king_sq = board.king(chess.BLACK)
    if white_king_sq in (chess.G1, chess.C1, chess.B1):
        score += 0.35
    if black_king_sq in (chess.G8, chess.C8, chess.B8):
        score -= 0.35

    # 4. Rook Activity: Open Files, Semi-Open Files, and 7th Rank
    white_rooks = board.pieces(chess.ROOK, chess.WHITE)
    black_rooks = board.pieces(chess.ROOK, chess.BLACK)
    white_pawns = board.pieces(chess.PAWN, chess.WHITE)
    black_pawns = board.pieces(chess.PAWN, chess.BLACK)

    for r_sq in white_rooks:
        f = chess.square_file(r_sq)
        rank = chess.square_rank(r_sq)
        file_mask = chess.BB_FILES[f]
        # 7th rank bonus
        if rank == 6:  # 0-indexed rank 6 = 7th rank
            score += 0.30
        # Open / Semi-open file
        has_w_pawn = bool(white_pawns & file_mask)
        has_b_pawn = bool(black_pawns & file_mask)
        if not has_w_pawn and not has_b_pawn:
            score += 0.25  # Open file
        elif not has_w_pawn:
            score += 0.15  # Semi-open file

    for r_sq in black_rooks:
        f = chess.square_file(r_sq)
        rank = chess.square_rank(r_sq)
        file_mask = chess.BB_FILES[f]
        # 7th rank bonus (rank 1 for Black = 2nd rank on board)
        if rank == 1:
            score -= 0.30
        # Open / Semi-open file
        has_w_pawn = bool(white_pawns & file_mask)
        has_b_pawn = bool(black_pawns & file_mask)
        if not has_w_pawn and not has_b_pawn:
            score -= 0.25  # Open file
        elif not has_b_pawn:
            score -= 0.15  # Semi-open file

    # 5. Bishop Pair Bonus
    if len(board.pieces(chess.BISHOP, chess.WHITE)) >= 2:
        score += 0.30
    if len(board.pieces(chess.BISHOP, chess.BLACK)) >= 2:
        score -= 0.30

    return score


if __name__ == "__main__":
    test_board = chess.Board()
    initial_eval = evaluate_board(test_board)
    print(f"[Heuristics Test] Initial Board Eval: {initial_eval:.2f} (Expected near 0.00)")
    assert abs(initial_eval) < 0.2, "Starting position should be balanced"

    # Test rook shuffling position
    test_pos = chess.Board('r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 5 4')
    # Compare castling (e8g8) vs rook shuffle (h8g8)
    test_pos.push_san("O-O")
    eval_castle = evaluate_board(test_pos)
    test_pos.pop()

    test_pos.push_san("Rg8")
    eval_rook_shuffle = evaluate_board(test_pos)
    test_pos.pop()

    print(f"[Heuristics Test] Castling Eval: {eval_castle:.2f} vs Rook Shuffle Eval: {eval_rook_shuffle:.2f}")
    assert eval_castle < eval_rook_shuffle, "Castling should be strictly better for Black (more negative) than Rg8"
    print("Heuristics advanced evaluation tests passed successfully!")
