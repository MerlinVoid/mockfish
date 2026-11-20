"""main.py - Role: GUI & System Integrator
===========================================
Project: Mockfish AI Chess Engine
Author: Team Mockfish (GUI & Integrator Specialist)

Responsibilities:
- Provide an interactive, responsive Tkinter graphical user interface.
- Render 8x8 chessboard with rank/file indicators and Unicode chess pieces.
- Handle mouse click-to-play human moves, square selections, and move highlighting.
- Highlight King in Check / Checkmate with vivid warning colors.
- Display a dedicated, non-freezing in-canvas Game Over screen with "Play Again" and "Review Board" options.
- Support board flipping and playing as either White or Black.
- Implement the overarching game loop:
    1. Human move -> Validate legality.
    2. Query knowledge_base.py (Opening book / Logic rules).
    3. If None -> Call search.py (Alpha-Beta adversarial search).
    4. Execute bot move -> Redraw board.
- Display telemetry (Bot move, Search Depth, Nodes Evaluated, Static Eval).
"""

import tkinter as tk
from typing import Optional
import chess

# Project module imports
from knowledge_base import query_knowledge_base
from search import get_best_move, get_last_telemetry
from heuristics import evaluate_board

# Board visual appearance constants
BOARD_SIZE = 512              # 512x512 pixels canvas (64x64 px per square)
SQUARE_SIZE = BOARD_SIZE // 8  # 64 pixels per square

# Color palette (Modern tournament style)
COLOR_LIGHT_SQ = "#EEEED2"       # Pale warm cream
COLOR_DARK_SQ = "#769656"        # Forest green
COLOR_HIGHLIGHT = "#F7F769"      # Highlighted selected square
COLOR_LAST_MOVE = "#BACA44"      # Highlighted from/to squares for last move
COLOR_LEGAL_DOT = "#555555"      # Subtle indicator dot for legal destinations
COLOR_CHECK = "#E53935"          # Red square highlight for King in Check
COLOR_CHECKMATE = "#B71C1C"      # Dark crimson highlight for Checkmate
COLOR_STATUS_BG = "#262421"      # Dark slate background for telemetry bar
COLOR_STATUS_FG = "#FFFFFF"      # White text for telemetry

# Standard Unicode chess piece glyphs
UNICODE_PIECES: dict[chess.Piece, str] = {
    # White pieces
    chess.Piece(chess.PAWN, chess.WHITE): "♙",
    chess.Piece(chess.KNIGHT, chess.WHITE): "♘",
    chess.Piece(chess.BISHOP, chess.WHITE): "♗",
    chess.Piece(chess.ROOK, chess.WHITE): "♖",
    chess.Piece(chess.QUEEN, chess.WHITE): "♕",
    chess.Piece(chess.KING, chess.WHITE): "♔",
    # Black pieces
    chess.Piece(chess.PAWN, chess.BLACK): "♟",
    chess.Piece(chess.KNIGHT, chess.BLACK): "♞",
    chess.Piece(chess.BISHOP, chess.BLACK): "♝",
    chess.Piece(chess.ROOK, chess.BLACK): "♜",
    chess.Piece(chess.QUEEN, chess.BLACK): "♛",
    chess.Piece(chess.KING, chess.BLACK): "♚",
}

# Button bounding boxes on the canvas Game Over overlay
BTN_PLAY_AGAIN = (100, 260, 245, 305)
BTN_REVIEW_BOARD = (267, 260, 412, 305)


class MockfishGUI:
    """Main Tkinter GUI and Game Orchestrator for the Mockfish Chess Engine."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Mockfish AI Chess Engine")
        self.root.resizable(False, False)

        # Chess game logic state
        self.board = chess.Board()
        self.selected_square: Optional[chess.Square] = None
        self.legal_destinations: list[chess.Square] = []
        self.last_move: Optional[chess.Move] = None
        self.human_color = chess.WHITE  # Default: Human plays White
        self.flipped = False            # True when Black is at the bottom
        self.is_bot_thinking = False

        # Game Over Overlay state
        self.game_over_result: Optional[tuple[str, str]] = None  # (Headline, Subtitle)
        self.game_over_overlay_visible = False

        # Build UI layout
        self._build_widgets()
        self.draw_board()

        # Telemetry initial message
        self.update_telemetry("Ready. Human plays White. Click a piece to move.")

    def _build_widgets(self) -> None:
        """Constructs the GUI widgets: Toolbar, Board Canvas, and Telemetry Bar."""
        # Top Toolbar
        toolbar = tk.Frame(self.root, bg="#312E2B", pady=6, padx=8)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        title_label = tk.Label(
            toolbar,
            text="Mockfish 1.0",
            font=("Segoe UI", 12, "bold"),
            fg="#81B64C",
            bg="#312E2B",
        )
        title_label.pack(side=tk.LEFT, padx=6)

        self.turn_indicator = tk.Label(
            toolbar,
            text="Turn: White (Human)",
            font=("Segoe UI", 10),
            fg="#CCCCCC",
            bg="#312E2B",
        )
        self.turn_indicator.pack(side=tk.LEFT, padx=12)

        # Flip Board Button
        flip_btn = tk.Button(
            toolbar,
            text="Flip Board",
            font=("Segoe UI", 9),
            bg="#4A4744",
            fg="#FFFFFF",
            activebackground="#5E5B58",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=8,
            command=self.flip_board,
        )
        flip_btn.pack(side=tk.RIGHT, padx=4)

        # New Game Button
        new_game_btn = tk.Button(
            toolbar,
            text="New Game",
            font=("Segoe UI", 9, "bold"),
            bg="#81B64C",
            fg="#FFFFFF",
            activebackground="#A3D160",
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            padx=10,
            command=self.reset_game,
        )
        new_game_btn.pack(side=tk.RIGHT, padx=4)

        # Main 8x8 Chessboard Canvas
        self.canvas = tk.Canvas(
            self.root,
            width=BOARD_SIZE,
            height=BOARD_SIZE,
            bg=COLOR_LIGHT_SQ,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(side=tk.TOP)
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Bottom Telemetry & Status Bar
        status_frame = tk.Frame(self.root, bg=COLOR_STATUS_BG, pady=6, padx=10)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.telemetry_label = tk.Label(
            status_frame,
            text="Initializing engine...",
            font=("Consolas", 10),
            bg=COLOR_STATUS_BG,
            fg=COLOR_STATUS_FG,
            anchor="w",
        )
        self.telemetry_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # -------------------------------------------------------------------------
    # Board Coordinate Mapping (supports standard and flipped views)
    # -------------------------------------------------------------------------
    def square_to_coords(self, square: chess.Square) -> tuple[int, int]:
        """Maps a chess.Square (0-63) to canvas (col, row) where (0,0) is top-left."""
        file = chess.square_file(square)  # 0 (a) to 7 (h)
        rank = chess.square_rank(square)  # 0 (1) to 7 (8)
        if self.flipped:
            col = 7 - file
            row = rank
        else:
            col = file
            row = 7 - rank
        return col, row

    def coords_to_square(self, col: int, row: int) -> chess.Square:
        """Maps canvas (col, row) to a chess.Square (0-63)."""
        if self.flipped:
            file = 7 - col
            rank = row
        else:
            file = col
            rank = 7 - row
        return chess.square(file, rank)

    # -------------------------------------------------------------------------
    # Board Rendering
    # -------------------------------------------------------------------------
    def draw_board(self) -> None:
        """Renders the 8x8 chessboard, highlights, pieces, check indicators,
        and Game Over overlay."""
        self.canvas.delete("all")

        # Determine if either king is in check or checkmate
        in_check_sq: Optional[chess.Square] = None
        is_mated = self.board.is_checkmate()
        if self.board.is_check():
            in_check_sq = self.board.king(self.board.turn)

        # 1. Draw Squares & Highlights
        for rank_idx in range(8):
            for file_idx in range(8):
                square = self.coords_to_square(file_idx, rank_idx)
                x1 = file_idx * SQUARE_SIZE
                y1 = rank_idx * SQUARE_SIZE
                x2 = x1 + SQUARE_SIZE
                y2 = y1 + SQUARE_SIZE

                # Base square color
                is_light = (file_idx + rank_idx) % 2 == 0
                bg_color = COLOR_LIGHT_SQ if is_light else COLOR_DARK_SQ

                # Apply highlights: Selected square, Last move, and Check / Checkmate
                if square == in_check_sq:
                    bg_color = COLOR_CHECKMATE if is_mated else COLOR_CHECK
                elif self.selected_square == square:
                    bg_color = COLOR_HIGHLIGHT
                elif self.last_move and (square == self.last_move.from_square or square == self.last_move.to_square):
                    bg_color = COLOR_LAST_MOVE

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg_color, outline="")

        # 2. Draw Rank and File Notation Indicators
        font_notation = ("Segoe UI", 8, "bold")
        for i in range(8):
            file_char = chr(ord('h') - i) if self.flipped else chr(ord('a') + i)
            rank_char = str(i + 1) if self.flipped else str(8 - i)

            is_light_file = (i + 7) % 2 == 0
            label_fg_file = COLOR_DARK_SQ if is_light_file else COLOR_LIGHT_SQ
            self.canvas.create_text(
                i * SQUARE_SIZE + SQUARE_SIZE - 6,
                7 * SQUARE_SIZE + SQUARE_SIZE - 7,
                text=file_char,
                font=font_notation,
                fill=label_fg_file,
            )

            is_light_rank = i % 2 == 0
            label_fg_rank = COLOR_DARK_SQ if is_light_rank else COLOR_LIGHT_SQ
            self.canvas.create_text(
                6,
                i * SQUARE_SIZE + 8,
                text=rank_char,
                font=font_notation,
                fill=label_fg_rank,
            )

        # 3. Draw Legal Move Destination Indicators
        for dest_sq in self.legal_destinations:
            col, row = self.square_to_coords(dest_sq)
            cx = col * SQUARE_SIZE + SQUARE_SIZE // 2
            cy = row * SQUARE_SIZE + SQUARE_SIZE // 2
            dest_piece = self.board.piece_at(dest_sq)

            if dest_piece is None:
                # Small circle for empty squares
                r = 6
                self.canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill=COLOR_LEGAL_DOT, outline="", stipple="gray50"
                )
            else:
                # Hollow ring around capturable enemy piece
                r = SQUARE_SIZE // 2 - 4
                self.canvas.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    outline=COLOR_LEGAL_DOT, width=4
                )

        # 4. Draw Pieces with High-Contrast Outlines
        piece_font = ("Segoe UI Symbol", 36)
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece is not None:
                col, row = self.square_to_coords(square)
                cx = col * SQUARE_SIZE + SQUARE_SIZE // 2
                cy = row * SQUARE_SIZE + SQUARE_SIZE // 2

                symbol = UNICODE_PIECES.get(piece, "")
                if piece.color == chess.WHITE:
                    # White piece: subtle dark stroke for contrast on light squares, then white glyph
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        self.canvas.create_text(cx + dx, cy + dy, text=symbol, font=piece_font, fill="#333333")
                    self.canvas.create_text(cx, cy, text=symbol, font=piece_font, fill="#FFFFFF")
                else:
                    # Black piece: solid dark glyph with subtle light outline for contrast on dark squares
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        self.canvas.create_text(cx + dx, cy + dy, text=symbol, font=piece_font, fill="#FFFFFF")
                    self.canvas.create_text(cx, cy, text=symbol, font=piece_font, fill="#1A1A1A")

        # 5. Draw Game Over Overlay Screen if active
        if self.game_over_overlay_visible and self.game_over_result:
            self._render_game_over_overlay()

    def _render_game_over_overlay(self) -> None:
        """Renders the prominent in-canvas Game Over screen banner and action buttons."""
        headline, subtitle = self.game_over_result

        # Dimmed backdrop
        # Tkinter canvas doesn't have true alpha rectangles, so we draw a crisp card in center
        card_x1, card_y1, card_x2, card_y2 = 66, 116, 446, 396
        # Drop shadow
        self.canvas.create_rectangle(card_x1 + 4, card_y1 + 4, card_x2 + 4, card_y2 + 4, fill="#151413", outline="")
        # Card Body
        border_color = "#81B64C" if "WHITE" in headline or "BLACK" in headline else "#D4AC0D"
        self.canvas.create_rectangle(card_x1, card_y1, card_x2, card_y2, fill="#1E1E1E", outline=border_color, width=2)

        # Trophy / Icon
        icon = "🏆" if "WINS" in headline else "🤝"
        self.canvas.create_text(256, 160, text=icon, font=("Segoe UI Emoji", 26))

        # Headline
        head_color = "#81B64C" if "WHITE WINS" in headline else ("#E67E22" if "BLACK WINS" in headline else "#F1C40F")
        self.canvas.create_text(256, 198, text=headline, font=("Segoe UI", 20, "bold"), fill=head_color)

        # Subtitle / Reason
        self.canvas.create_text(256, 230, text=subtitle, font=("Segoe UI", 11), fill="#CCCCCC")

        # Play Again Button
        bx1, by1, bx2, by2 = BTN_PLAY_AGAIN
        self.canvas.create_rectangle(bx1, by1, bx2, by2, fill="#81B64C", outline="", tags="play_again_btn")
        self.canvas.create_text((bx1 + bx2) // 2, (by1 + by2) // 2, text="Play Again", font=("Segoe UI", 10, "bold"), fill="#FFFFFF", tags="play_again_btn")

        # Review Board Button
        rx1, ry1, rx2, ry2 = BTN_REVIEW_BOARD
        self.canvas.create_rectangle(rx1, ry1, rx2, ry2, fill="#4A4744", outline="", tags="review_board_btn")
        self.canvas.create_text((rx1 + rx2) // 2, (ry1 + ry2) // 2, text="Review Board", font=("Segoe UI", 10, "bold"), fill="#FFFFFF", tags="review_board_btn")

        # Hint text
        self.canvas.create_text(256, 350, text="Click 'Play Again' or 'New Game' to restart", font=("Segoe UI", 9), fill="#888888")

    # -------------------------------------------------------------------------
    # User Interaction & Move Handling
    # -------------------------------------------------------------------------
    def on_canvas_click(self, event: tk.Event) -> None:
        """Handles mouse clicks on the chessboard and game-over overlay buttons."""
        # Check overlay button clicks if overlay is displayed
        if self.game_over_overlay_visible:
            # Play Again Button Click
            bx1, by1, bx2, by2 = BTN_PLAY_AGAIN
            if bx1 <= event.x <= bx2 and by1 <= event.y <= by2:
                self.reset_game()
                return

            # Review Board Button Click
            rx1, ry1, rx2, ry2 = BTN_REVIEW_BOARD
            if rx1 <= event.x <= rx2 and ry1 <= event.y <= ry2:
                self.game_over_overlay_visible = False
                self.draw_board()
                return
            return

        # Ignore board clicks when bot is computing or game is completed
        if self.is_bot_thinking or self.board.is_game_over(claim_draw=True):
            return

        # Restrict human input to human's turn
        if self.board.turn != self.human_color:
            return

        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        if not (0 <= col < 8 and 0 <= row < 8):
            return

        clicked_square = self.coords_to_square(col, row)
        piece = self.board.piece_at(clicked_square)

        # Case 1: No square currently selected -> Select if piece belongs to human
        if self.selected_square is None:
            if piece and piece.color == self.human_color:
                self.selected_square = clicked_square
                # Calculate legal destinations for the selected piece
                self.legal_destinations = [
                    m.to_square for m in self.board.legal_moves if m.from_square == clicked_square
                ]
                self.draw_board()
            return

        # Case 2: Square already selected
        # Clicked the same square again -> Deselect
        if clicked_square == self.selected_square:
            self.selected_square = None
            self.legal_destinations = []
            self.draw_board()
            return

        # Clicked another friendly piece -> Switch selection
        if piece and piece.color == self.human_color:
            self.selected_square = clicked_square
            self.legal_destinations = [
                m.to_square for m in self.board.legal_moves if m.from_square == clicked_square
            ]
            self.draw_board()
            return

        # Case 3: Attempting a move from selected_square to clicked_square
        # Support both standard move and Queen pawn promotion
        is_pawn_promotion = False
        moving_piece = self.board.piece_at(self.selected_square)
        if moving_piece and moving_piece.piece_type == chess.PAWN:
            target_rank = chess.square_rank(clicked_square)
            if (moving_piece.color == chess.WHITE and target_rank == 7) or (moving_piece.color == chess.BLACK and target_rank == 0):
                is_pawn_promotion = True

        candidate_move = chess.Move(self.selected_square, clicked_square, promotion=chess.QUEEN if is_pawn_promotion else None)

        if candidate_move in self.board.legal_moves:
            self.execute_human_move(candidate_move)
        else:
            # Illegal destination clicked -> Clear selection
            self.selected_square = None
            self.legal_destinations = []
            self.draw_board()

    def execute_human_move(self, move: chess.Move) -> None:
        """Executes a validated human move, updates UI, and triggers the bot loop."""
        self.board.push(move)
        self.last_move = move
        self.selected_square = None
        self.legal_destinations = []
        self.draw_board()

        human_uci = move.uci()
        current_eval = evaluate_board(self.board)
        self.update_telemetry(f"Human played {human_uci} | Static Eval: {current_eval:+.2f}")

        # Check for game termination after human move
        if self._check_game_over():
            return

        # Trigger Bot Turn asynchronously so Tkinter redraws human move first
        self.is_bot_thinking = True
        self.canvas.config(cursor="watch")
        bot_color_name = "Black" if self.human_color == chess.WHITE else "White"
        self.turn_indicator.config(text=f"Turn: {bot_color_name} (Mockfish thinking...)")
        self.root.after(50, self.bot_turn)

    # -------------------------------------------------------------------------
    # Bot Game Loop & Integration
    # -------------------------------------------------------------------------
    def bot_turn(self) -> None:
        """Bot decision pipeline:

        Step 1: Query Knowledge Base (Opening book / Logic rules).
        Step 2: If None, fall back to Adversarial Search (Minimax + Alpha-Beta).
        Step 3: Apply move, redraw board, update telemetry, and check game over.
        """
        try:
            if self.board.is_game_over(claim_draw=True):
                self._check_game_over()
                return

            bot_move: Optional[chess.Move] = None
            source_tag = ""
            telemetry_str = ""

            # Step 1: Query Knowledge Base (Role: Logic & Rules)
            bot_move = query_knowledge_base(self.board)
            if bot_move is not None and bot_move in self.board.legal_moves:
                source_tag = "Knowledge Base"
                telemetry_str = f"Bot played {bot_move.uci()} | Source: {source_tag} | Opening Book"
            else:
                # Step 2: Adversarial Search (Role: Adversarial Search & Heuristics)
                source_tag = "Minimax Alpha-Beta"
                search_depth = 3
                search_res = get_best_move(self.board, max_depth=search_depth)

                # Accommodate both return signatures: chess.Move or (chess.Move, float)
                if isinstance(search_res, tuple):
                    bot_move = search_res[0]
                else:
                    bot_move = search_res

                stats = get_last_telemetry()
                nodes = stats.get("nodes", 0)
                depth = stats.get("depth", search_depth)
                score = stats.get("eval", 0.0)

                if bot_move:
                    telemetry_str = (
                        f"Bot played {bot_move.uci()} | Depth: {depth} | Nodes: {nodes} | Eval: {score:+.2f}"
                    )
                else:
                    telemetry_str = f"Bot found no legal moves | Depth: {depth}"

            # Step 3: Execute Bot Move
            if bot_move is not None and bot_move in self.board.legal_moves:
                self.board.push(bot_move)
                self.last_move = bot_move
                self.draw_board()
                self.update_telemetry(telemetry_str)
            else:
                self.update_telemetry("Bot produced no legal moves.")

            # Update turn indicator
            if not self._check_game_over():
                human_turn_str = "White" if self.human_color == chess.WHITE else "Black"
                check_alert = " (CHECK!)" if self.board.is_check() else ""
                self.turn_indicator.config(text=f"Turn: {human_turn_str} (Human){check_alert}")

        except Exception as e:
            self.update_telemetry(f"Engine Exception: {e}")
            self.turn_indicator.config(text="Turn: White (Human)")
        finally:
            self.is_bot_thinking = False
            self.canvas.config(cursor="hand2")

    # -------------------------------------------------------------------------
    # Game Over Checks & Telemetry
    # -------------------------------------------------------------------------
    def _check_game_over(self) -> bool:
        """Checks for checkmate, stalemate, or draw conditions.
        Activates the non-freezing in-canvas Game Over overlay."""
        # Detect checkmate, stalemate, insufficient material, 3-fold repetition, 50-move rule
        is_over = (
            self.board.is_game_over(claim_draw=True)
            or self.board.can_claim_threefold_repetition()
            or self.board.can_claim_fifty_moves()
        )
        if not is_over:
            return False

        headline = ""
        subtitle = ""

        if self.board.is_checkmate():
            # If current turn is White, White is checkmated -> Black won
            if self.board.turn == chess.WHITE:
                headline = "BLACK WINS!"
                winner_name = "Human" if self.human_color == chess.BLACK else "Mockfish"
                subtitle = f"{winner_name} won by Checkmate"
            else:
                headline = "WHITE WINS!"
                winner_name = "Human" if self.human_color == chess.WHITE else "Mockfish"
                subtitle = f"{winner_name} won by Checkmate"
        elif self.board.is_stalemate():
            headline = "DRAW!"
            subtitle = "Drawn by Stalemate"
        elif self.board.is_insufficient_material():
            headline = "DRAW!"
            subtitle = "Drawn by Insufficient Material"
        elif self.board.can_claim_threefold_repetition() or self.board.is_fivefold_repetition():
            headline = "DRAW!"
            subtitle = "Drawn by Threefold Repetition"
        elif self.board.can_claim_fifty_moves() or self.board.is_seventyfive_moves():
            headline = "DRAW!"
            subtitle = "Drawn by 50-Move Rule"
        else:
            headline = "GAME OVER!"
            subtitle = "Game Concluded"

        self.game_over_result = (headline, subtitle)
        self.game_over_overlay_visible = True

        self.update_telemetry(f"GAME OVER: {headline} - {subtitle}. Click 'Play Again' to restart.")
        self.turn_indicator.config(text=f"Game Over ({headline})")
        self.draw_board()
        return True

    def update_telemetry(self, text: str) -> None:
        """Updates the telemetry status label at the bottom of the window."""
        self.telemetry_label.config(text=text)

    def flip_board(self) -> None:
        """Toggles board perspective between White at bottom and Black at bottom."""
        self.flipped = not self.flipped
        self.draw_board()

    def reset_game(self) -> None:
        """Resets the chessboard to the initial starting position and clears overlays."""
        if self.is_bot_thinking:
            return
        self.board.reset()
        self.selected_square = None
        self.legal_destinations = []
        self.last_move = None
        self.game_over_result = None
        self.game_over_overlay_visible = False
        self.turn_indicator.config(text="Turn: White (Human)")
        self.draw_board()
        self.update_telemetry("New game started. White to move.")


def main() -> None:
    """Application entry point."""
    root = tk.Tk()
    app = MockfishGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
