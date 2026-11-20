"""generate_visualizations.py - Generates clean graphics for the presentation
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Set global styles
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'

# -----------------------------------------------------------------------------
# Visualization 1: Empirical Benchmark Comparison Chart
# -----------------------------------------------------------------------------
def create_benchmark_chart():
    algorithms = [
        'Pure Minimax\n(Exhaustive)',
        'Alpha-Beta\n(Unordered)',
        'Iterative\nDeepening (IDDFS)',
        'Alpha-Beta +\nMove Ordering\n(Mockfish)'
    ]
    nodes = [52088, 3253, 518, 378]
    times = [41.02, 2.30, 0.37, 0.26]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.5), dpi=300)
    fig.patch.set_facecolor('#F8F9FA')

    # Color palette
    colors = ['#C0392B', '#E67E22', '#2980B9', '#27AE60']

    # Subplot 1: Nodes Explored (Logarithmic)
    bars1 = ax1.bar(algorithms, nodes, color=colors, width=0.55, edgecolor='#2C3E50', linewidth=1.2)
    ax1.set_yscale('log')
    ax1.set_ylabel('Nodes Explored (Log Scale)', fontsize=11, fontweight='bold', color='#2C3E50')
    ax1.set_title('Search Tree Size at Depth 3\n(99.27% Pruned by Mockfish)', fontsize=12, fontweight='bold', color='#1A365D')
    ax1.grid(axis='y', linestyle='--', alpha=0.4, color='#7F8C8D')
    ax1.set_facecolor('#FFFFFF')
    ax1.tick_params(axis='x', labelsize=8.5)

    for bar, val in zip(bars1, nodes):
        y = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2, y * 1.25, f'{val:,}', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#2C3E50')

    # Subplot 2: Execution Time in Seconds
    bars2 = ax2.bar(algorithms, times, color=colors, width=0.55, edgecolor='#2C3E50', linewidth=1.2)
    ax2.set_ylabel('Execution Time (Seconds)', fontsize=11, fontweight='bold', color='#2C3E50')
    ax2.set_title('Execution Time at Depth 3\n(156.6x Speedup by Mockfish)', fontsize=12, fontweight='bold', color='#1A365D')
    ax2.grid(axis='y', linestyle='--', alpha=0.4, color='#7F8C8D')
    ax2.set_facecolor('#FFFFFF')
    ax2.tick_params(axis='x', labelsize=8.5)

    for bar, val in zip(bars2, times):
        y = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2, y + 1.0, f'{val:.2f}s', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#2C3E50')

    plt.tight_layout()
    plt.savefig('viz_benchmark.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Saved viz_benchmark.png successfully!")


# -----------------------------------------------------------------------------
# Visualization 2: Architecture & Decision Flow Diagram
# -----------------------------------------------------------------------------
def create_architecture_diagram():
    fig, ax = plt.subplots(figsize=(11, 4.5), dpi=300)
    fig.patch.set_facecolor('#F8F9FA')
    ax.set_facecolor('#F8F9FA')
    ax.axis('off')

    # Define box coordinates and styling
    boxes = [
        {"text": "1. Human Move\n(Click-to-Play GUI)\nmain.py", "x": 0.05, "y": 0.5, "w": 0.17, "h": 0.45, "fc": "#EBF5FB", "ec": "#2980B9", "tc": "#1A5276"},
        {"text": "2. Knowledge Base\n(Opening Book O(1))\nknowledge_base.py", "x": 0.29, "y": 0.5, "w": 0.18, "h": 0.45, "fc": "#FEF9E7", "ec": "#F1C40F", "tc": "#7D6608"},
        {"text": "3. Adversarial Search\n(Alpha-Beta + MVV-LVA)\nsearch.py", "x": 0.53, "y": 0.5, "w": 0.19, "h": 0.45, "fc": "#EAFAF1", "ec": "#27AE60", "tc": "#1E8449"},
        {"text": "4. Heuristic Eval\n(PeSTO PST + Safety)\nheuristics.py", "x": 0.78, "y": 0.5, "w": 0.17, "h": 0.45, "fc": "#FDEDEC", "ec": "#E74C3C", "tc": "#922B21"},
    ]

    for b in boxes:
        bbox = mpatches.FancyBboxPatch((b["x"], b["y"] - b["h"]/2), b["w"], b["h"], 
                                      boxstyle="round,pad=0.02,rounding_size=0.03", 
                                      facecolor=b["fc"], edgecolor=b["ec"], linewidth=2.0)
        ax.add_patch(bbox)
        ax.text(b["x"] + b["w"]/2, b["y"], b["text"], ha='center', va='center', fontsize=9.5, fontweight='bold', color=b["tc"])

    # Connecting arrows
    ax.annotate("", xy=(0.29, 0.5), xytext=(0.22, 0.5),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color="#2C3E50", lw=2.5))
    ax.text(0.255, 0.54, "Legal Move", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#5D6D7E')

    ax.annotate("", xy=(0.53, 0.5), xytext=(0.47, 0.5),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color="#2C3E50", lw=2.5))
    ax.text(0.50, 0.54, "Off-Book", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#5D6D7E')

    ax.annotate("", xy=(0.78, 0.5), xytext=(0.72, 0.5),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color="#2C3E50", lw=2.5))
    ax.text(0.75, 0.54, "Leaf Eval", ha='center', va='bottom', fontsize=8, fontweight='bold', color='#5D6D7E')

    # Return feedback arrow
    ax.annotate("", xy=(0.13, 0.22), xytext=(0.62, 0.22),
                arrowprops=dict(arrowstyle="->,head_width=0.35,head_length=0.5", color="#27AE60", lw=2.5))
    ax.text(0.38, 0.15, "Optimal Bot Move Dispatched to GUI (Real-Time Telemetry HUD Updated)", ha='center', va='top', fontsize=9, fontweight='bold', color='#27AE60')

    # Title
    ax.text(0.5, 0.88, "Mockfish System Architecture & Decision Pipeline", ha='center', va='center', fontsize=14, fontweight='bold', color='#1A365D')

    ax.set_xlim(0, 1)
    ax.set_ylim(0.05, 0.95)
    plt.tight_layout()
    plt.savefig('viz_architecture.png', dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print("Saved viz_architecture.png successfully!")


if __name__ == "__main__":
    create_benchmark_chart()
    create_architecture_diagram()
