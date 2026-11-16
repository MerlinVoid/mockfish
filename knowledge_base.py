"""knowledge_base.py - Role: Logic & Knowledge Bases
===================================================
Project: Mockfish AI Chess Engine
Author: Team Mockfish (Logic & Rules Specialist)

Responsibilities:
- Maintain deterministic knowledge bases (opening books, endgame tables).
- Provide rule-based logic queries before resorting to search.
- Implement domain knowledge, tactical motifs, and propositional/FOL rule systems.
"""

from typing import Optional
import chess

# Standard chess starting position FEN:
# "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
STARTING_FEN = chess.STARTING_FEN

# Example opening book mapping: FEN string -> Recommended UCI move
# Teammates can expand this into a comprehensive opening database or load Polyglot books.
OPENING_BOOK: dict[str, str] = {
    STARTING_FEN: "e2e4",
    # 1. e4 -> 1... e5 (King's Pawn Game response)
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "e7e5",
    # 1. d4 -> 1... d5 (Queen's Pawn Game response)
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": "d7d5",
}


def query_knowledge_base(board: chess.Board) -> Optional[chess.Move]:
    """Queries the logic and knowledge base for an immediate, high-confidence move.

    Checks whether the current board state matches known theoretical positions
    (e.g., standard starting position, opening book lines, or endgame tablebases).

    Args:
        board: The current chess.Board state.

    Returns:
        chess.Move if a textbook/rule-based move is available; None otherwise,
        signaling that the search engine should take over.

    Syllabus & Coursework Extension Points for Logic Teammate:
    ---------------------------------------------------------
    1. Opening Book Expansion:
       - Integrate a Polyglot opening book (`chess.polyglot.open_reader`).
       - Add classical gambits and responses using a dictionary or SQLite DB.

    2. Propositional / First-Order Logic (FOL) Rules:
       - Implement safety axioms: e.g., "If opponent queen threatens unshielded king,
         generate forced evasive responses."
       - Implement endgame win conditions (K+R vs K, K+Q vs K).

    3. Endgame Tablebases:
       - Integrate Syzygy tablebases (`chess.syzygy`) for 3-5 piece endgames
         to achieve mathematically perfect play without minimax overhead.
    """
    current_fen = board.fen()

    # Stub requirement: Check if the board is in the starting position
    if current_fen == STARTING_FEN:
        # 1. e2e4 (King's Pawn Opening)
        return chess.Move.from_uci("e2e4")

    # Secondary check against mini opening book
    if current_fen in OPENING_BOOK:
        move_uci = OPENING_BOOK[current_fen]
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            return move

    # No rule/knowledge base match found -> Hand off to adversarial search
    return None


if __name__ == "__main__":
    # Quick self-test for development
    test_board = chess.Board()
    suggested_move = query_knowledge_base(test_board)
    print(f"[Knowledge Base Test] Starting FEN query result: {suggested_move}")
    assert suggested_move == chess.Move.from_uci("e2e4"), "Should return e2e4 for starting position"
    print("Knowledge base stub test passed successfully!")
