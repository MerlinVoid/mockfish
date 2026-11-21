"""Unit and integration tests for the Mockfish chess engine."""

import math
import tkinter as tk

import chess

from knowledge_base import query_knowledge_base
from heuristics import evaluate_board
from search import get_best_move, alpha_beta
from main import MockfishGUI, BTN_PLAY_AGAIN, BTN_REVIEW_BOARD


ITALIAN_FEN = (
    "r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/"
    "PPPP1PPP/R1BQK2R b KQkq - 5 4"
)


def test_knowledge_base():
    print("--- 1. Testing Knowledge Base ---")
    board = chess.Board()

    # Starting position
    m = query_knowledge_base(board)
    assert m == chess.Move.from_uci("e2e4"), f"Expected e2e4, got {m}"
    print("  [PASS] Starting position queries e2e4")

    # Response to 1. e4
    board.push_san("e4")
    m = query_knowledge_base(board)
    assert m == chess.Move.from_uci("e7e5"), f"Expected e7e5, got {m}"
    print("  [PASS] 1. e4 returns e7e5")

    # Response to 1. e4 e5 2. Nf3
    board.push_san("e5")
    board.push_san("Nf3")
    m = query_knowledge_base(board)
    assert m == chess.Move.from_uci("b8c6"), f"Expected b8c6, got {m}"
    print("  [PASS] 2. Nf3 returns b8c6")

    # Non-book position
    board.push_san("Nc6")
    board.push_san("h4")
    m = query_knowledge_base(board)
    assert m is None, f"Expected None for off-book line, got {m}"
    print("  [PASS] Off-book line returns None (hands off to search)")


def test_heuristics():
    print("--- 2. Testing Heuristics & PST ---")
    board = chess.Board()
    initial_score = evaluate_board(board)
    assert abs(initial_score) < 0.1, f"Starting board should be near 0, got {initial_score}"
    print(f"  [PASS] Starting board eval: {initial_score:.2f}")

    # White is up a queen
    board_queen_up = chess.Board(
        "rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
    )
    q_score = evaluate_board(board_queen_up)
    assert q_score > 8.0, f"White should be heavily winning, got {q_score}"
    print(f"  [PASS] Material imbalance (White up a Queen): {q_score:.2f}")

    # Checkmate detection
    fools_mate = chess.Board()
    for san in ("f3", "e5", "g4", "Qh4#"):
        fools_mate.push_san(san)
    assert fools_mate.is_checkmate()
    mate_score = evaluate_board(fools_mate)
    assert mate_score <= -10000.0, f"White is mated, got {mate_score}"
    print(f"  [PASS] Checkmate eval: {mate_score:.2f}")

    # Castling preference over rook shuffle
    pos = chess.Board(ITALIAN_FEN)
    pos.push_san("O-O")
    castle_eval = evaluate_board(pos)
    pos.pop()

    pos.push_san("Rg8")
    shuffle_eval = evaluate_board(pos)
    pos.pop()

    assert castle_eval < shuffle_eval, (
        f"Castling ({castle_eval}) must evaluate better for Black "
        f"than Rg8 ({shuffle_eval})"
    )
    print(f"  [PASS] Castling eval ({castle_eval:.2f}) vs Rook Shuffle eval ({shuffle_eval:.2f})")


def test_search_and_anti_shuffling():
    print("--- 3. Testing Adversarial Search & Anti-Shuffling ---")

    # Position where the previous engine shuffled its rook.
    pos = chess.Board(ITALIAN_FEN)
    best_m = get_best_move(pos, max_depth=3)
    assert isinstance(best_m, chess.Move), "Expected a move"
    assert best_m in pos.legal_moves, f"Illegal move: {best_m}"
    assert best_m != chess.Move.from_uci("h8g8"), f"Bot should not play h8g8! Got {best_m}"
    print(f"  [PASS] Italian Game position move: {best_m} (h8g8 avoided!)")

    # Scholar's Mate: White has mate in one with Qxf7#.
    mate_in_1 = chess.Board(
        "r1bqkb1r/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"
    )
    result = get_best_move(mate_in_1, max_depth=2, return_eval=True)
    assert isinstance(result, tuple), "Expected (move, score)"
    mate_move, score = result
    assert mate_move == chess.Move.from_uci("h5f7"), f"Expected Qxf7#, got {mate_move}"
    assert score > 10000, f"Checkmate score should be > 10000, got {score}"
    print(f"  [PASS] Scholar's Mate in 1 detected: {mate_move} (Eval: {score:.2f})")

    # Construct a position with twofold repetition.
    rep_board = chess.Board()
    for san in ("Nf3", "Nf6", "Ng1", "Ng8"):
        rep_board.push_san(san)
    assert rep_board.is_repetition(2)

    # Verify the recursive search's repetition policy.
    # Twofold repetition is a search heuristic, not an official draw rule.
    rep_board.push_san("Nf3")
    try:
        assert rep_board.is_repetition(2)
        score = alpha_beta(rep_board, 1, -math.inf, math.inf, False)
        assert score == 0.0, f"Expected repetition score of 0, got {score}"
    finally:
        rep_board.pop()
    print("  [PASS] Search detects and scores twofold repetition")

    # Verify that root move selection still returns a legal move.
    original_fen = rep_board.fen()
    original_stack = list(rep_board.move_stack)
    m = get_best_move(rep_board, max_depth=3)
    assert isinstance(m, chess.Move), "Expected a move after repetition"
    assert m in rep_board.legal_moves, f"Illegal move: {m}"
    assert rep_board.fen() == original_fen
    assert rep_board.move_stack == original_stack
    print(f"  [PASS] Legal move selected after repetition: {m}")


def test_search_correctness():
    print("--- 4. Testing Search Correctness ---")

    # Test the maximizing (White) and minimizing (Black) sides.
    positions = [
        ("Starting position", chess.Board(), 2),
        ("Italian Game", chess.Board(ITALIAN_FEN), 3),
    ]

    for name, board, depth in positions:
        original_fen = board.fen()
        original_stack = list(board.move_stack)

        result = get_best_move(board, max_depth=depth, return_eval=True)
        assert isinstance(result, tuple), "Expected (move, score)"
        move, score = result

        assert board.fen() == original_fen, "Search changed the FEN"
        assert board.move_stack == original_stack, "Search changed the move history"
        assert isinstance(move, chess.Move), "Expected a move"
        assert move in board.legal_moves, f"Illegal move: {move}"

        # Obtain the root minimax value using a full search window.
        expected = alpha_beta(
            board, depth, -math.inf, math.inf, board.turn == chess.WHITE
        )
        assert math.isclose(score, expected, rel_tol=0.0, abs_tol=1e-6), (
            f"{name}: reported score {score}, expected {expected}"
        )

        # Obtain the selected move's exact value with a full search window.
        board.push(move)
        try:
            actual = alpha_beta(
                board, depth - 1, -math.inf, math.inf, board.turn == chess.WHITE
            )
        finally:
            board.pop()

        assert math.isclose(actual, expected, rel_tol=0.0, abs_tol=1e-6), (
            f"{name}: selected move {move} has score {actual}, expected {expected}"
        )
        assert board.fen() == original_fen
        assert board.move_stack == original_stack
        print(f"  [PASS] {name}: correct move value and board restoration")


def test_gui_and_game_over_screen():
    print("--- 5. Testing GUI, Coordinate Mapping & Game Over Screen ---")
    root = tk.Tk()
    root.withdraw()

    try:
        app = MockfishGUI(root)

        # Standard coordinate mapping.
        assert app.square_to_coords(chess.A1) == (0, 7)
        assert app.square_to_coords(chess.H8) == (7, 0)
        assert app.coords_to_square(0, 7) == chess.A1

        # Flipped coordinate mapping.
        app.flip_board()
        assert app.square_to_coords(chess.A1) == (7, 0)
        assert app.square_to_coords(chess.H8) == (0, 7)
        app.flip_board()
        print("  [PASS] Standard and flipped coordinate mapping")

        # Simulate Fool's Mate through the GUI's game-over handler.
        app.board.reset()
        for san in ("f3", "e5", "g4", "Qh4#"):
            app.board.push_san(san)
        assert app.board.is_checkmate()
        assert app._check_game_over(), "Game-over check should detect checkmate"
        assert bool(app.game_over_overlay_visible), "Checkmate overlay must be visible"
        game_result = app.game_over_result
        assert game_result is not None
        headline, subtitle = game_result
        assert headline == "BLACK WINS!", f"Unexpected headline: {headline}"
        print(f"  [PASS] Game Over Screen: '{headline}' - '{subtitle}'")

        # Use Tkinter Event objects instead of an untyped DummyEvent.
        ev_review = tk.Event()
        ev_review.x = (BTN_REVIEW_BOARD[0] + BTN_REVIEW_BOARD[2]) // 2
        ev_review.y = (BTN_REVIEW_BOARD[1] + BTN_REVIEW_BOARD[3]) // 2
        app.on_canvas_click(ev_review)
        assert not bool(app.game_over_overlay_visible), "Review Board should hide the overlay"
        assert app.board.is_checkmate(), "Review Board should preserve the final position"
        print("  [PASS] Review Board hides the overlay and preserves the position")

        # Play Again button.
        assert app._check_game_over()
        assert bool(app.game_over_overlay_visible)
        ev_play_again = tk.Event()
        ev_play_again.x = (BTN_PLAY_AGAIN[0] + BTN_PLAY_AGAIN[2]) // 2
        ev_play_again.y = (BTN_PLAY_AGAIN[1] + BTN_PLAY_AGAIN[3]) // 2
        app.on_canvas_click(ev_play_again)
        assert not bool(app.game_over_overlay_visible), "Play Again should clear the overlay"
        assert app.board.fen() == chess.STARTING_FEN, "Board should return to starting position"
        assert len(app.board.move_stack) == 0
        print("  [PASS] Play Again resets the game")

        # Stalemate detection.
        app.board = chess.Board("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1")
        assert app.board.is_stalemate()
        assert app._check_game_over()
        assert bool(app.game_over_overlay_visible)
        draw_result = app.game_over_result
        assert draw_result is not None, "Expected a draw result"
        assert draw_result[0] == "DRAW!", f"Expected DRAW!, got {draw_result[0]}"
        print("  [PASS] Stalemate displays DRAW! overlay")

    finally:
        root.destroy()


def run_all_tests():
    print("==================================================")
    print("        RUNNING MOCKFISH FULL TEST SUITE          ")
    print("==================================================")

    test_knowledge_base()
    test_heuristics()
    test_search_and_anti_shuffling()
    test_search_correctness()
    test_gui_and_game_over_screen()

    print("==================================================")
    print("                ALL TESTS PASSED                 ")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
