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

# Standard Opening Book mapping: FEN string -> Recommended UCI move
# Covers standard tournament responses to e4, d4, c4, Nf3 up to move 3
OPENING_BOOK: dict[str, str] = {
    # 1. White Opening Move
    STARTING_FEN: "e2e4",

    # 1... Responses to 1. e4, d4, c4, Nf3
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq - 0 1": "e7e5",  # 1. e4 -> 1... e5 (King's Pawn)
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR b KQkq - 0 1": "d7d5",  # 1. d4 -> 1... d5 (Queen's Pawn)
    "rnbqkbnr/pppppppp/8/8/2P5/8/PP1PPPPP/RNBQKBNR b KQkq - 0 1": "e7e5",  # 1. c4 -> 1... e5 (English Defense)
    "rnbqkbnr/pppppppp/8/8/8/5N2/PPPPPPPP/RNBQKB1R b KQkq - 1 1": "d7d5",  # 1. Nf3 -> 1... d5 (Reti Defense)

    # 2... Responses
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": "b8c6",  # 1. e4 e5 2. Nf3 -> 2... Nc6
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2": "d7d6",  # 1. e4 c5 2. Nf3 -> 2... d6 (Sicilian)
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2": "e7e6",  # 1. d4 d5 2. c4 -> 2... e6 (QGD)
    "rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR b KQkq - 0 2": "e7e6",  # 1. d4 Nf6 2. c4 -> 2... e6 (Nimzo/Queen's Indian)

    # 3... Responses
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3": "f8c5",  # 1. e4 e5 2. Nf3 Nc6 3. Bc4 -> 3... Bc5 (Italian)
    "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3": "a7a6",  # 1. e4 e5 2. Nf3 Nc6 3. Bb5 -> 3... a6 (Ruy Lopez)
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
       - Add classical gambits and responses using SQLite or JSON files.

    2. Propositional / First-Order Logic (FOL) Rules:
       - Implement safety axioms: e.g., "If opponent queen threatens unshielded king,
         generate forced evasive responses."
       - Implement endgame win conditions (K+R vs K, K+Q vs K).

    3. Endgame Tablebases:
       - Integrate Syzygy tablebases (`chess.syzygy`) for 3-5 piece endgames
         to achieve mathematically perfect play without minimax overhead.
    """
    current_fen = board.fen()

    # 1. Check if the board is in the standard starting position
    if current_fen == STARTING_FEN:
        return chess.Move.from_uci("e2e4")

    # 2. Check against the opening book table
    if current_fen in OPENING_BOOK:
        move_uci = OPENING_BOOK[current_fen]
        move = chess.Move.from_uci(move_uci)
        if move in board.legal_moves:
            return move

    # No rule/knowledge base match found -> Hand off to adversarial search
    return None


if __name__ == "__main__":
    test_board = chess.Board()
    suggested_move = query_knowledge_base(test_board)
    print(f"[Knowledge Base Test] Starting FEN query result: {suggested_move}")
    assert suggested_move == chess.Move.from_uci("e2e4"), "Should return e2e4 for starting position"

    # Test Black response to 1. e4
    test_board.push_san("e4")
    black_res = query_knowledge_base(test_board)
    print(f"[Knowledge Base Test] 1. e4 Black response: {black_res}")
    assert black_res == chess.Move.from_uci("e7e5"), "Should return e7e5 as response to 1. e4"

    print("Knowledge base tests passed successfully!")
