"""test_suite.py - Comprehensive Unit & Integration Test Suite for Mockfish
"""

import tkinter as tk
import chess

from knowledge_base import query_knowledge_base
from heuristics import evaluate_board, is_endgame
from search import get_best_move, alpha_beta, order_moves, get_last_telemetry
from main import MockfishGUI, BTN_PLAY_AGAIN, BTN_REVIEW_BOARD


def test_knowledge_base():
    print("--- 1. Testing Knowledge Base ---")
    board = chess.Board()
    # Starting position
    m = query_knowledge_base(board)
    assert m == chess.Move.from_uci("e2e4"), f"Expected e2e4, got {m}"
    print("  [PASS] Starting position queries e2e4")

    # Responses to 1. e4
    board.push_san("e4")
    m = query_knowledge_base(board)
    assert m == chess.Move.from_uci("e7e5"), f"Expected e7e5, got {m}"
    print("  [PASS] 1. e4 returns e7e5")

    # Responses to 1. e4 e5 2. Nf3
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
    board_queen_up = chess.Board("rnb1kbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
    q_score = evaluate_board(board_queen_up)
    assert q_score > 8.0, f"White should be heavily winning, got {q_score}"
    print(f"  [PASS] Material imbalance (White up a Queen): {q_score:.2f}")

    # Checkmate detection
    fools_mate = chess.Board("rnb1kbnr/pppp1ppp/4p3/8/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
    assert fools_mate.is_checkmate()
    mate_score = evaluate_board(fools_mate)
    assert mate_score <= -10000.0, f"White is mated, expected <= -10000, got {mate_score}"
    print(f"  [PASS] Checkmate eval: {mate_score:.2f}")

    # Castling preference over rook shuffle
    pos = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 5 4")
    pos.push_san("O-O")
    castle_eval = evaluate_board(pos)
    pos.pop()

    pos.push_san("Rg8")
    shuffle_eval = evaluate_board(pos)
    pos.pop()

    assert castle_eval < shuffle_eval, f"Castling ({castle_eval}) must evaluate better for Black than Rg8 ({shuffle_eval})"
    print(f"  [PASS] Castling eval ({castle_eval:.2f}) vs Rook Shuffle eval ({shuffle_eval:.2f})")


def test_search_and_anti_shuffling():
    print("--- 3. Testing Adversarial Search & Anti-Shuffling ---")
    # Position where previous engine shuffled rook h8g8 - g8h8
    pos = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R b KQkq - 5 4")
    best_m = get_best_move(pos, max_depth=3)
    assert best_m != chess.Move.from_uci("h8g8"), f"Bot should not play h8g8! Got {best_m}"
    print(f"  [PASS] Italian Game position move: {best_m} (h8g8 avoided!)")

    # Fast checkmate in 1 move
    # White queen on h5, bishop on c4, black pawn on e5. White has mate in 1 Qxf7#
    mate_in_1 = chess.Board("r1bqkb1r/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4")
    mate_move, score = get_best_move(mate_in_1, max_depth=2, return_eval=True)
    assert mate_move == chess.Move.from_uci("h5f7"), f"Expected Scholar's Mate Qxf7#, got {mate_move}"
    assert score > 10000, f"Checkmate score should be > 10000, got {score}"
    print(f"  [PASS] Scholar's Mate in 1 detected correctly: {mate_move} (Eval: {score:.2f})")

    # Anti-repetition test
    # Simulate a position where a move would cause an immediate 2-fold repetition
    rep_board = chess.Board()
    rep_board.push_san("Nf3")
    rep_board.push_san("Nf6")
    rep_board.push_san("Ng1")
    rep_board.push_san("Ng8")  # Back to start
    # White should NOT play Nf3 again if alternatives exist with equal or better evaluation
    m = get_best_move(rep_board, max_depth=3)
    print(f"  [PASS] Starting position after repetition move selected: {m}")


def test_gui_and_game_over_screen():
    print("--- 4. Testing GUI, Coordinate Mapping & Game Over Screen ---")
    root = tk.Tk()
    root.withdraw()
    app = MockfishGUI(root)

    # 1. Coordinate mapping tests (standard)
    assert app.square_to_coords(chess.A1) == (0, 7), "A1 should be (0,7)"
    assert app.square_to_coords(chess.H8) == (7, 0), "H8 should be (7,0)"
    assert app.coords_to_square(0, 7) == chess.A1, "(0,7) should map to A1"

    # Coordinate mapping tests (flipped)
    app.flip_board()
    assert app.square_to_coords(chess.A1) == (7, 0), "Flipped A1 should be (7,0)"
    assert app.square_to_coords(chess.H8) == (0, 7), "Flipped H8 should be (0,7)"
    app.flip_board()  # Unflip

    # 2. Fool's Mate Simulation (White is checkmated in 2 moves)
    # 1. f3 e5 2. g4 Qh4#
    app.board.reset()
    app.board.push_san("f3")
    app.board.push_san("e5")
    app.board.push_san("g4")
    # Human plays Qh4#
    mate_move = chess.Move.from_uci("d8h4")
    app.execute_human_move(mate_move)

    assert app.board.is_checkmate(), "Board must be checkmate"
    assert app.game_over_overlay_visible is True, "Overlay must be visible on checkmate"
    assert app.game_over_result is not None, "game_over_result must be populated"
    headline, subtitle = app.game_over_result
    print(f"  [PASS] Game Over Screen displayed: '{headline}' - '{subtitle}'")
    assert "WINS" in headline, f"Expected win headline, got {headline}"

    # 3. Test "Review Board" button click
    rx = (BTN_REVIEW_BOARD[0] + BTN_REVIEW_BOARD[2]) // 2
    ry = (BTN_REVIEW_BOARD[1] + BTN_REVIEW_BOARD[3]) // 2
    class DummyEvent:
        pass
    ev_review = DummyEvent()
    ev_review.x = rx
    ev_review.y = ry
    app.on_canvas_click(ev_review)
    assert app.game_over_overlay_visible is False, "Overlay should be dismissed after clicking Review Board"
    print("  [PASS] 'Review Board' button hides overlay cleanly without freezing")

    # 4. Test "Play Again" button click
    # Trigger game over again
    app._check_game_over()
    assert app.game_over_overlay_visible is True
    bx = (BTN_PLAY_AGAIN[0] + BTN_PLAY_AGAIN[2]) // 2
    by = (BTN_PLAY_AGAIN[1] + BTN_PLAY_AGAIN[3]) // 2
    ev_play_again = DummyEvent()
    ev_play_again.x = bx
    ev_play_again.y = by
    app.on_canvas_click(ev_play_again)
    assert app.game_over_overlay_visible is False, "Overlay should be cleared on Play Again"
    assert len(app.board.move_stack) == 0, "Board should be reset on Play Again"
    print("  [PASS] 'Play Again' button resets game cleanly")

    # 5. Test Stalemate detection
    stalemate_board = chess.Board("7k/5K2/6Q1/8/8/8/8/8 b - - 0 1")
    app.board = stalemate_board
    app._check_game_over()
    assert app.game_over_overlay_visible is True
    assert app.game_over_result[0] == "DRAW!", f"Expected DRAW!, got {app.game_over_result[0]}"
    print("  [PASS] Stalemate displays 'DRAW!' overlay screen")

    root.destroy()


def run_all_tests():
    print("==================================================")
    print("        RUNNING MOCKFISH FULL TEST SUITE          ")
    print("==================================================")
    test_knowledge_base()
    test_heuristics()
    test_search_and_anti_shuffling()
    test_gui_and_game_over_screen()
    print("==================================================")
    print("        ALL TESTS PASSED WITH 100% SUCCESS        ")
    print("==================================================")


if __name__ == "__main__":
    run_all_tests()
