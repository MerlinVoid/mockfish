"""build_presentation.py - Generates an executive 16:9 PowerPoint presentation
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

# -----------------------------------------------------------------------------
# Color Definitions
# -----------------------------------------------------------------------------
PRIMARY_BLUE = RGBColor(20, 60, 110)      # #143C6E
DARK_SLATE   = RGBColor(35, 33, 30)       # #23211E
LIGHT_BG     = RGBColor(248, 249, 250)    # #F8F9FA
WHITE        = RGBColor(255, 255, 255)
ACCENT_GREEN = RGBColor(39, 174, 96)      # #27AE60
ACCENT_GOLD  = RGBColor(212, 172, 13)     # #D4AC0D
MUTED_GRAY   = RGBColor(100, 110, 120)    # #646E78
CARD_BG      = RGBColor(240, 243, 246)
BORDER_GRAY  = RGBColor(210, 215, 220)

def set_slide_background(slide, color=WHITE):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = color

def add_header(slide, title_text, category_text="INTRODUCTION TO AI WITH PYTHON (25CS2000)"):
    # Category / Super-title
    cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.35))
    tf_cat = cat_box.text_frame
    tf_cat.word_wrap = True
    p_cat = tf_cat.paragraphs[0]
    p_cat.text = category_text.upper()
    p_cat.font.size = Pt(10)
    p_cat.font.bold = True
    p_cat.font.color.rgb = ACCENT_GREEN

    # Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.7))
    tf_title = title_box.text_frame
    tf_title.word_wrap = True
    p_title = tf_title.paragraphs[0]
    p_title.text = title_text
    p_title.font.size = Pt(22)
    p_title.font.bold = True
    p_title.font.color.rgb = PRIMARY_BLUE

    # Thin dividing accent line
    line = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.45), Inches(11.7), Inches(0.02))
    line.fill.solid()
    line.fill.fore_color.rgb = BORDER_GRAY
    line.line.color.rgb = BORDER_GRAY

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen standard dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: Title Slide
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1, LIGHT_BG)

    # Accent colored top bar
    bar = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.18))
    bar.fill.solid()
    bar.fill.fore_color.rgb = PRIMARY_BLUE
    bar.line.fill.background()

    # Title container
    t_box = s1.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.333), Inches(2.2))
    tf = t_box.text_frame
    tf.word_wrap = True

    p0 = tf.paragraphs[0]
    p0.text = "MOCKFISH"
    p0.font.size = Pt(44)
    p0.font.bold = True
    p0.font.color.rgb = PRIMARY_BLUE

    p1 = tf.add_paragraph()
    p1.text = "An Intelligent Knowledge-Guided Adversarial Chess Engine & Interactive GUI"
    p1.font.size = Pt(20)
    p1.font.bold = True
    p1.font.color.rgb = DARK_SLATE
    p1.space_before = Pt(8)

    p2 = tf.add_paragraph()
    p2.text = "Course: Introduction to AI with Python  |  Course Code: 25CS2000"
    p2.font.size = Pt(13)
    p2.font.color.rgb = ACCENT_GREEN
    p2.space_before = Pt(8)

    # Team Members Card
    team_card = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), Inches(3.6), Inches(11.333), Inches(2.8))
    team_card.fill.solid()
    team_card.fill.fore_color.rgb = WHITE
    team_card.line.color.rgb = BORDER_GRAY
    team_card.line.width = Pt(1.5)

    team_title = s1.shapes.add_textbox(Inches(1.3), Inches(3.8), Inches(10.7), Inches(0.4))
    p_tt = team_title.text_frame.paragraphs[0]
    p_tt.text = "PROJECT TEAM MEMBERS & ROLES"
    p_tt.font.size = Pt(12)
    p_tt.font.bold = True
    p_tt.font.color.rgb = PRIMARY_BLUE

    # 4 Members Columns
    members = [
        ("B Sreenikesh", "CS25B2051", "Role 1: Logic & Rules", "knowledge_base.py"),
        ("Aditya Kumar", "CS25I1050", "Role 2: State Space & Eval", "heuristics.py"),
        ("Amit Kumar", "CS25I1051", "Role 3: Adversarial Search", "search.py"),
        ("Aviral Pandey", "CS25B2054", "Role 4: GUI & Benchmarks", "main.py, benchmark.py"),
    ]

    col_w = Inches(2.55)
    start_x = Inches(1.3)
    for i, (name, roll, role, module) in enumerate(members):
        box_x = start_x + i * Inches(2.7)
        mb = s1.shapes.add_textbox(box_x, Inches(4.3), col_w, Inches(1.8))
        mtf = mb.text_frame
        mtf.word_wrap = True

        mp0 = mtf.paragraphs[0]
        mp0.text = name
        mp0.font.size = Pt(13)
        mp0.font.bold = True
        mp0.font.color.rgb = DARK_SLATE

        mp1 = mtf.add_paragraph()
        mp1.text = roll
        mp1.font.size = Pt(11)
        mp1.font.color.rgb = PRIMARY_BLUE

        mp2 = mtf.add_paragraph()
        mp2.text = role
        mp2.font.size = Pt(10)
        mp2.font.bold = True
        mp2.font.color.rgb = ACCENT_GREEN
        mp2.space_before = Pt(4)

        mp3 = mtf.add_paragraph()
        mp3.text = f"Module: {module}"
        mp3.font.size = Pt(9.5)
        mp3.font.color.rgb = MUTED_GRAY

    # Footer note
    ft = s1.shapes.add_textbox(Inches(1.0), Inches(6.6), Inches(11.333), Inches(0.4))
    p_ft = ft.text_frame.paragraphs[0]
    p_ft.text = "Repository: https://github.com/unclePRO/mockfish  |  Verified & Benchmarked"
    p_ft.font.size = Pt(10)
    p_ft.font.color.rgb = MUTED_GRAY

    # =========================================================================
    # SLIDE 2: Problem Formulation & Motivation
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2, WHITE)
    add_header(s2, "Problem Formulation: Chess as an Adversarial Environment")

    # Left Card: Formal Formulation
    c1 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2))
    c1.fill.solid()
    c1.fill.fore_color.rgb = LIGHT_BG
    c1.line.color.rgb = BORDER_GRAY

    tb1 = s2.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(5.2), Inches(4.8))
    tf1 = tb1.text_frame
    tf1.word_wrap = True

    p = tf1.paragraphs[0]
    p.text = "Mathematical Formulation"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    bullets_left = [
        ("Formal 7-Tuple", "M = <S0, Actions, Result, Constraints, Terminal_Test, Utility, Heuristic>"),
        ("Initial State (S0)", "Standard 64-square FEN setup, White to move, castling rights intact."),
        ("State Space (S)", "Reachable legal chess states ~ 10^40 (Shannon Number ~ 10^120)."),
        ("Action Space", "Legal FIDE moves (sliding raycasts, leaps, castling, promotions)."),
        ("Strict Invariants", "King Safety: No move may leave friendly king in check. Must evade checks."),
        ("Terminal Utility", "Win: +20000 + depth  |  Loss: -20000 - depth  |  Draw: 0.00."),
    ]
    for title, desc in bullets_left:
        bp = tf1.add_paragraph()
        bp.text = f"• {title}: {desc}"
        bp.font.size = Pt(11)
        bp.font.color.rgb = DARK_SLATE
        bp.space_before = Pt(6)

    # Right Card: Real-World AI Transferability
    c2 = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2))
    c2.fill.solid()
    c2.fill.fore_color.rgb = LIGHT_BG
    c2.line.color.rgb = BORDER_GRAY

    tb2 = s2.shapes.add_textbox(Inches(7.0), Inches(1.9), Inches(5.3), Inches(4.8))
    tf2 = tb2.text_frame
    tf2.word_wrap = True

    p = tf2.paragraphs[0]
    p.text = "Real-World Significance & Motivation"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    bullets_right = [
        ("Adversarial Multi-Agent Systems", "Models zero-sum competition against rational adversaries (algorithmic trading, cyber defense)."),
        ("Combinatorial Optimization", "Navigates branching factor b ~ 35. Techniques mirror airline crew scheduling & logistics routing."),
        ("Hybrid Decision Architecture", "Combines instant O(1) expert knowledge with deep heuristic reasoning for rare events."),
        ("Coursework Goals", "Integrate Minimax, Alpha-Beta Pruning, Heuristics, IDDFS, and Expert Knowledge in Python."),
    ]
    for title, desc in bullets_right:
        bp = tf2.add_paragraph()
        bp.text = f"• {title}: {desc}"
        bp.font.size = Pt(11.5)
        bp.font.color.rgb = DARK_SLATE
        bp.space_before = Pt(10)

    # =========================================================================
    # SLIDE 3: System Architecture (Visualization 1)
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3, WHITE)
    add_header(s3, "System Architecture: Hybrid Decision Pipeline")

    # Insert Visualization 1 (Architecture diagram)
    arch_img_path = "viz_architecture.png"
    if os.path.exists(arch_img_path):
        s3.shapes.add_picture(arch_img_path, Inches(0.8), Inches(1.7), Inches(11.7), Inches(3.6))

    # Architecture summary card below image
    arch_card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.5))
    arch_card.fill.solid()
    arch_card.fill.fore_color.rgb = LIGHT_BG
    arch_card.line.color.rgb = BORDER_GRAY

    tb_arch = s3.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.3), Inches(1.3))
    tf_arch = tb_arch.text_frame
    tf_arch.word_wrap = True

    p = tf_arch.paragraphs[0]
    p.text = "Pipeline Highlights:"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    arch_bullets = [
        "1. Instant O(1) Knowledge Base: Checks opening table first; textbook moves executed with zero search overhead.",
        "2. Multi-Ply Search Fallback: Off-book positions hand off to Alpha-Beta search with heuristic move ordering.",
        "3. Positional Static Eval: Non-terminal horizon states evaluated using PeSTO Piece-Square Tables (PST) + King Safety.",
        "4. Non-Blocking Event Loop: Tkinter Canvas executes moves asynchronously, continuously updating the real-time telemetry HUD.",
    ]
    for ab in arch_bullets:
        bp = tf_arch.add_paragraph()
        bp.text = f"• {ab}"
        bp.font.size = Pt(10)
        bp.font.color.rgb = DARK_SLATE
        bp.space_before = Pt(2)

    # =========================================================================
    # SLIDE 4: Key AI Algorithms Implemented
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4, WHITE)
    add_header(s4, "AI Algorithms Implemented: 5 Synergistic Pillars")

    algo_cards = [
        ("1. Knowledge-Based Expert System", "knowledge_base.py", 
         "• Propositional logic opening book.\n• O(1) instant retrieval for 1.e4, 1.d4, 1.c4, 1.Nf3.\n• Guarantees principled opening play.",
         Inches(0.8), Inches(1.7)),
        ("2. Minimax with Alpha-Beta Pruning", "search.py",
         "• Branch-and-bound pruning (beta <= alpha cutoffs).\n• Produces identical decisions to Minimax in far less time.\n• Distance-to-mate scoring: +/- 20000 +/- depth.",
         Inches(6.8), Inches(1.7)),
        ("3. Tactical Move Ordering", "search.py",
         "• MVV-LVA: Most Valuable Victim - Least Attacker.\n• Prioritizes promotions (+800), castling (+300), checks (+150).\n• Maximizes early beta-cutoffs.",
         Inches(0.8), Inches(4.5)),
        ("4. State Space Heuristic Evaluation", "heuristics.py",
         "• Material balance: P=1, N=3.2, B=3.3, R=5, Q=9.\n• PeSTO Piece-Square Tables (PST) with vertical mirroring.\n• Open-file rook bonuses, castled safety, bishop pair.",
         Inches(6.8), Inches(4.5)),
    ]

    for title, module, desc, x, y in algo_cards:
        card = s4.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, Inches(5.7), Inches(2.5))
        card.fill.solid()
        card.fill.fore_color.rgb = LIGHT_BG
        card.line.color.rgb = BORDER_GRAY

        tb = s4.shapes.add_textbox(x + Inches(0.2), y + Inches(0.15), Inches(5.3), Inches(2.2))
        tframe = tb.text_frame
        tframe.word_wrap = True

        p0 = tframe.paragraphs[0]
        p0.text = title
        p0.font.size = Pt(13)
        p0.font.bold = True
        p0.font.color.rgb = PRIMARY_BLUE

        p1 = tframe.add_paragraph()
        p1.text = f"Module: {module}"
        p1.font.size = Pt(10)
        p1.font.bold = True
        p1.font.color.rgb = ACCENT_GREEN

        p2 = tframe.add_paragraph()
        p2.text = desc
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = DARK_SLATE
        p2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 5: Empirical Benchmarks & Metrics (Visualization 2)
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5, WHITE)
    add_header(s5, "Empirical Benchmarks: 99.27% Pruning & 156.6x Speedup")

    # Insert Visualization 2 (Benchmark Chart)
    bench_img_path = "viz_benchmark.png"
    if os.path.exists(bench_img_path):
        s5.shapes.add_picture(bench_img_path, Inches(0.8), Inches(1.65), Inches(11.7), Inches(3.7))

    # Metric summary stat callout cards
    stat_card = s5.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(5.5), Inches(11.7), Inches(1.5))
    stat_card.fill.solid()
    stat_card.fill.fore_color.rgb = LIGHT_BG
    stat_card.line.color.rgb = BORDER_GRAY

    tb_stat = s5.shapes.add_textbox(Inches(1.0), Inches(5.6), Inches(11.3), Inches(1.3))
    tf_stat = tb_stat.text_frame
    tf_stat.word_wrap = True

    p = tf_stat.paragraphs[0]
    p.text = "Key Empirical Takeaways (Depth 3 Tactical Position):"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    stat_bullets = [
        "• Search Tree Reduction: Pure Minimax explored 52,088 nodes vs Mockfish's 378 nodes (99.27% Pruning Efficiency).",
        "• Execution Time: Wall-clock latency slashed from 41.02s down to 0.26s (156.6x Computational Speedup).",
        "• Branching Factor (b_eff): Reduced from b = 37.35 down to 7.23, approaching the theoretical best-case bound sqrt(b) ~ 6.",
        "• Anytime Search: Iterative Deepening (IDDFS) achieved depth 3 in 0.37s with only ~30% cumulative re-search overhead.",
    ]
    for sb in stat_bullets:
        bp = tf_stat.add_paragraph()
        bp.text = sb
        bp.font.size = Pt(10)
        bp.font.color.rgb = DARK_SLATE
        bp.space_before = Pt(2)

    # =========================================================================
    # SLIDE 6: Comparative Justification (Why This Approach?)
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6, WHITE)
    add_header(s6, "Justification: Method Selection Over Other AI Techniques")

    # Table of alternatives
    alt_card = s6.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.2))
    alt_card.fill.solid()
    alt_card.fill.fore_color.rgb = LIGHT_BG
    alt_card.line.color.rgb = BORDER_GRAY

    tb_alt = s6.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(5.0))
    tf_alt = tb_alt.text_frame
    tf_alt.word_wrap = True

    p = tf_alt.paragraphs[0]
    p.text = "Why Mockfish Chose Hybrid Alpha-Beta Over Other Course Techniques:"
    p.font.size = Pt(14)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    comparisons = [
        ("Uninformed Search (BFS / DFS)", "BFS triggers catastrophic O(b^d) memory exhaustion (>10^6 states at depth 4). Cannot model adversarial minimization. DFS gets trapped in move cycles."),
        ("A* Search / Greedy Best-First", "Formulated strictly for single-agent static pathfinding. In zero-sum games, the opponent continuously alters utility; there is no static goal state."),
        ("Hill Climbing / Local Search", "Vulnerable to local maxima and plateaus. Lacks lookahead: blindly grabs a 'free' pawn, walking directly into forced checkmate on the next turn."),
        ("Constraint Satisfaction (CSP)", "Chess is an adversarial optimization problem, not a static constraint satisfaction puzzle. CSPs cannot evaluate strategic advantage or minimax horizons."),
        ("Deep RL / Neural Networks", "Requires heavy GPU clusters and weeks of training. Inference latency is non-deterministic, violating lightweight real-time execution constraints."),
        ("Mockfish Hybrid Approach", "PROVABLY OPTIMAL within horizon; runs in minimal O(bd) memory; 156.6x speedup; lightweight CPU execution; fully deterministic and explainable."),
    ]

    for tech, reason in comparisons:
        bp = tf_alt.add_paragraph()
        bp.text = f"• {tech}: {reason}"
        bp.font.size = Pt(10.5)
        bp.font.color.rgb = DARK_SLATE
        bp.space_before = Pt(5)

    # =========================================================================
    # SLIDE 7: GUI & Bug Resolution
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7, WHITE)
    add_header(s7, "Interactive GUI & Critical Bug Resolution")

    # Card 1: GUI Features
    g1 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.2))
    g1.fill.solid()
    g1.fill.fore_color.rgb = LIGHT_BG
    g1.line.color.rgb = BORDER_GRAY

    tbg1 = s7.shapes.add_textbox(Inches(1.0), Inches(1.9), Inches(5.2), Inches(4.8))
    tfg1 = tbg1.text_frame
    tfg1.word_wrap = True

    p = tfg1.paragraphs[0]
    p.text = "Tkinter GUI Architecture"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    gui_bullets = [
        ("Event-Driven Canvas", "512x512 canvas with tournament-style colors (#EEEED2 & #769656) and dual-stroke Unicode pieces."),
        ("Move Guidance", "Clicking friendly pieces displays subtle indicator dots for legal moves and hollow rings for capturable targets."),
        ("King Attack Warnings", "Highlights checked king in warning red (#E53935) and checkmated king in deep crimson (#B71C1C)."),
        ("Dynamic Board Flipping", "One-click 'Flip Board' button toggles between White and Black perspectives with mirrored coordinate mapping."),
        ("Live Telemetry HUD", "Real-time status bar reporting move UCI, depth, nodes evaluated, static eval, and decision origin."),
    ]
    for title, desc in gui_bullets:
        bp = tfg1.add_paragraph()
        bp.text = f"• {title}: {desc}"
        bp.font.size = Pt(11)
        bp.font.color.rgb = DARK_SLATE
        bp.space_before = Pt(6)

    # Card 2: Bug Resolution
    g2 = s7.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.2))
    g2.fill.solid()
    g2.fill.fore_color.rgb = LIGHT_BG
    g2.line.color.rgb = BORDER_GRAY

    tbg2 = s7.shapes.add_textbox(Inches(7.0), Inches(1.9), Inches(5.3), Inches(4.8))
    tfg2 = tbg2.text_frame
    tfg2.word_wrap = True

    p = tfg2.paragraphs[0]
    p.text = "Critical Bug Fixes & Refinements"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    fix_bullets = [
        ("Solved Windows Modal Freezing", "Native messagebox.showinfo blocked event loops on Windows. Replaced with custom in-canvas Game Over overlay card with 'Play Again' and 'Review Board' buttons."),
        ("Cured Rook-Shuffling Loop", "Pure material evaluation gave 0.0 to all quiet moves, causing rook to shuffle h8-g8-h8. Solved via PeSTO PST, castling rights bonuses, and 2-fold repetition filters."),
        ("Ply-Adjusted Checkmates", "Checkmate score factored with depth (+/-20000 +/- depth) so bot prefers fastest mates and resists longest."),
        ("Pawn Promotions", "Auto-queen promotion for both White (rank 8) and Black (rank 1) without crashes."),
    ]
    for title, desc in fix_bullets:
        bp = tfg2.add_paragraph()
        bp.text = f"• {title}: {desc}"
        bp.font.size = Pt(11)
        bp.font.color.rgb = DARK_SLATE
        bp.space_before = Pt(6)

    # =========================================================================
    # SLIDE 8: Team Division of Work
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8, WHITE)
    add_header(s8, "Team Contributions: 4 Decoupled Modular Subsystems")

    roles_data = [
        ("B Sreenikesh (CS25B2051)", "Logic & Rules Specialist (knowledge_base.py)", 
         "• Implemented opening book mapping for 1.e4, 1.d4, 1.c4, and 1.Nf3.\n• Engineered deterministic FEN pattern matching for O(1) retrieval.\n• Formulated propositional logic rules and tablebase query hooks."),
        ("Aditya Kumar (CS25I1050)", "State Space & Heuristics Specialist (heuristics.py)",
         "• Implemented PeSTO Piece-Square Tables (PST) with vertical reflection.\n• Formulated positional weights: castling (+0.20), open rook files (+0.25).\n• Engineered king safety, bishop pair bonus, and endgame transition detection."),
        ("Amit Kumar (CS25I1051)", "Adversarial Search Specialist (search.py)",
         "• Developed Minimax with Alpha-Beta pruning algorithm.\n• Engineered MVV-LVA move ordering (captures, promotions, checks).\n• Formulated ply-adjusted checkmate utility and anti-shuffling repetition filters."),
        ("Aviral Pandey (CS25B2054)", "GUI & Systems Integrator (main.py, benchmark.py)",
         "• Developed 512x512 Tkinter Canvas chessboard and move guidance dots.\n• Designed in-canvas Game Over overlay card, eliminating modal freezes.\n• Programmed empirical benchmark suite (benchmark.py) and test suite (test_suite.py)."),
    ]

    for i, (member, title, desc) in enumerate(roles_data):
        rx = Inches(0.8) if i % 2 == 0 else Inches(6.8)
        ry = Inches(1.7) if i < 2 else Inches(4.5)

        rc = s8.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, rx, ry, Inches(5.7), Inches(2.5))
        rc.fill.solid()
        rc.fill.fore_color.rgb = LIGHT_BG
        rc.line.color.rgb = BORDER_GRAY

        rtb = s8.shapes.add_textbox(rx + Inches(0.2), ry + Inches(0.15), Inches(5.3), Inches(2.2))
        rtf = rtb.text_frame
        rtf.word_wrap = True

        rp0 = rtf.paragraphs[0]
        rp0.text = member
        rp0.font.size = Pt(13)
        rp0.font.bold = True
        rp0.font.color.rgb = PRIMARY_BLUE

        rp1 = rtf.add_paragraph()
        rp1.text = title
        rp1.font.size = Pt(10)
        rp1.font.bold = True
        rp1.font.color.rgb = ACCENT_GREEN

        rp2 = rtf.add_paragraph()
        rp2.text = desc
        rp2.font.size = Pt(10.5)
        rp2.font.color.rgb = DARK_SLATE
        rp2.space_before = Pt(4)

    # =========================================================================
    # SLIDE 9: Conclusion & Summary
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9, WHITE)
    add_header(s9, "Conclusion: Key Takeaways & Coursework Outcomes")

    c_box = s9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.2))
    c_box.fill.solid()
    c_box.fill.fore_color.rgb = LIGHT_BG
    c_box.line.color.rgb = BORDER_GRAY

    tb_c = s9.shapes.add_textbox(Inches(1.1), Inches(1.9), Inches(11.1), Inches(4.8))
    tf_c = tb_c.text_frame
    tf_c.word_wrap = True

    p = tf_c.paragraphs[0]
    p.text = "Summary of Accomplishments"
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = PRIMARY_BLUE

    concl_points = [
        ("Complete AI Synthesis", "Successfully integrated Knowledge Bases (O(1)), Alpha-Beta Minimax, MVV-LVA Move Ordering, PeSTO Heuristics, and IDDFS into one cohesive Python application."),
        ("Empirically Proven Efficiency", "Achieved 99.27% tree pruning and 156.6x execution speedup (0.26s vs 41.02s), reducing effective branching factor from 37.35 to 7.23."),
        ("Robust Real-World Engineering", "Eliminated modal OS thread freezing via in-canvas overlays; cured rook-shuffling loops via PST and repetition filters; validated via test_suite.py."),
        ("Team Collaboration", "Successfully split into 4 independent modules with zero Git merge conflicts; fully documented in formal LaTeX report and committed to GitHub."),
        ("Future Research Scope", "Transposition tables (Zobrist hashing), Quiescence search (mitigating horizon effect), and dynamic tournament time budgeting."),
    ]

    for title, desc in concl_points:
        bp = tf_c.add_paragraph()
        bp.text = f"✔ {title}: {desc}"
        bp.font.size = Pt(11.5)
        bp.font.color.rgb = DARK_SLATE
        bp.space_before = Pt(8)

    # Save presentation
    output_filename = "Mockfish_Presentation.pptx"
    prs.save(output_filename)
    print(f"Presentation successfully generated and saved to {output_filename}!")

if __name__ == "__main__":
    create_deck()
