"""Illustrative antenna schematics for the extended presentation (not to scale, not simulation output).

Writes results/figures/antenna_types.png: (a) microstrip patch antenna, (b) slotted patch antenna,
(c) hybrid-slotted DGS antenna (slots in the patch + defected ground structure etched in the ground plane).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch, Polygon, Rectangle

from deliverables_common import FIG, NAVY

COPPER, SUB, GROUND, BG, SLOT = "#c48634", "#9fc7a3", "#b9bec5", "#ffffff", "#ffffff"


def label(ax, x, y, tx, ty, text):
    ax.add_patch(FancyArrowPatch((tx, ty), (x, y), arrowstyle="-|>", mutation_scale=8, color="#40505e", lw=0.8))
    ax.text(tx, ty, text, fontsize=8.5, color=NAVY, ha="center", va="center",
            bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.9))


def patch_antenna(ax):
    ax.set_title("(a) Microstrip patch antenna", fontsize=11, color=NAVY, fontweight="bold")
    # side cross-section (bottom half)
    ax.add_patch(Rectangle((0.5, 0.6), 9, 0.25, fc=GROUND, ec="k", lw=0.6))
    ax.add_patch(Rectangle((0.5, 0.85), 9, 0.9, fc=SUB, ec="k", lw=0.6))
    ax.add_patch(Rectangle((2.8, 1.75), 4.4, 0.18, fc=COPPER, ec="k", lw=0.6))
    ax.plot([4.2, 4.2], [0.1, 1.75], color="k", lw=2)
    label(ax, 5.0, 1.85, 8.3, 2.8, "radiating patch")
    label(ax, 8.6, 1.3, 9.0, 0.15, "substrate (εr, h)")
    label(ax, 1.4, 0.72, 1.5, 0.05, "ground plane")
    label(ax, 4.2, 0.4, 6.4, 0.1, "coax feed")
    ax.text(5, 2.45, "side view", fontsize=8, color="#5f6b76", ha="center")
    # top view
    ax.add_patch(Rectangle((1.5, 3.4), 7, 4.6, fc=SUB, ec="k", lw=0.6))
    ax.add_patch(Rectangle((3.0, 4.3), 4.0, 2.8, fc=COPPER, ec="k", lw=0.6))
    ax.add_patch(Circle((4.2, 5.7), 0.16, fc="k"))
    ax.annotate("", xy=(3.0, 7.35), xytext=(7.0, 7.35), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(5.0, 7.55, "W", fontsize=9, ha="center", color=NAVY)
    ax.annotate("", xy=(7.3, 4.3), xytext=(7.3, 7.1), arrowprops=dict(arrowstyle="<->", lw=0.8))
    ax.text(7.55, 5.7, "L", fontsize=9, va="center", color=NAVY)
    ax.text(4.2, 5.3, "feed", fontsize=7.5, ha="center", color="white")
    ax.text(5, 8.3, "top view", fontsize=8, color="#5f6b76", ha="center")


def slotted_antenna(ax):
    ax.set_title("(b) Slot / slotted patch antenna", fontsize=11, color=NAVY, fontweight="bold")
    ax.add_patch(Rectangle((1.5, 1.2), 7, 6.8, fc=SUB, ec="k", lw=0.6))
    ax.add_patch(Rectangle((2.6, 2.4), 4.8, 4.6, fc=COPPER, ec="k", lw=0.6))
    u = Polygon([(3.6, 6.2), (3.9, 6.2), (3.9, 3.7), (6.1, 3.7), (6.1, 6.2), (6.4, 6.2), (6.4, 3.4), (3.6, 3.4)],
                closed=True, fc=SLOT, ec="k", lw=0.6)
    ax.add_patch(u)
    ax.add_patch(Rectangle((2.9, 6.45), 1.6, 0.22, fc=SLOT, ec="k", lw=0.6))
    ax.add_patch(Rectangle((5.5, 6.45), 1.6, 0.22, fc=SLOT, ec="k", lw=0.6))
    ax.add_patch(Circle((5.0, 2.9), 0.16, fc="k"))
    label(ax, 6.25, 4.6, 8.0, 0.55, "U-slot")
    label(ax, 6.9, 6.56, 8.6, 7.65, "rectangular\nslots")
    label(ax, 5.0, 2.9, 2.6, 0.55, "feed")
    ax.text(5, 8.3, "slots lengthen the current path:\nlower resonance, wider / multiple bands", fontsize=8, color="#5f6b76",
            ha="center", va="bottom")


def hybrid_dgs(ax):
    ax.set_title("(c) Hybrid-slotted DGS antenna", fontsize=11, color=NAVY, fontweight="bold")
    # top layer
    ax.add_patch(Rectangle((0.6, 4.6), 4.2, 3.4, fc=SUB, ec="k", lw=0.6))
    ax.add_patch(Rectangle((1.4, 5.3), 2.6, 2.0, fc=COPPER, ec="k", lw=0.6))
    ax.add_patch(Rectangle((1.8, 6.6), 1.8, 0.16, fc=SLOT, ec="k", lw=0.5))
    ax.add_patch(Polygon([(2.2, 6.2), (2.35, 6.2), (2.35, 5.7), (3.05, 5.7), (3.05, 6.2), (3.2, 6.2), (3.2, 5.55), (2.2, 5.55)],
                         closed=True, fc=SLOT, ec="k", lw=0.5))
    ax.add_patch(Rectangle((2.55, 4.6), 0.3, 0.7, fc=COPPER, ec="k", lw=0.5))
    ax.text(2.7, 8.25, "top: slotted patch", fontsize=8, color="#5f6b76", ha="center")
    # bottom layer: ground with dumbbell DGS + slot
    ax.add_patch(Rectangle((5.2, 4.6), 4.2, 3.4, fc=GROUND, ec="k", lw=0.6))
    for cx in (6.1, 8.5):
        ax.add_patch(Rectangle((cx - 0.35, 5.6), 0.7, 0.7, fc=SLOT, ec="k", lw=0.5))
    ax.add_patch(Rectangle((6.45, 5.88), 1.7, 0.14, fc=SLOT, ec="k", lw=0.5))
    ax.add_patch(Rectangle((5.8, 7.05), 3.0, 0.18, fc=SLOT, ec="k", lw=0.5))
    ax.text(7.3, 8.25, "bottom: defected ground", fontsize=8, color="#5f6b76", ha="center")
    label(ax, 6.1, 5.95, 6.0, 3.6, "dumbbell DGS")
    label(ax, 7.3, 7.14, 8.8, 3.6, "ground slot")
    label(ax, 2.7, 5.6, 2.3, 3.6, "patch slots")
    ax.text(5.0, 1.6, "Slots in the patch + defects etched in the ground\nplane reshape currents on both layers:\n"
            "compact size, multiband, wider bandwidth -\nbut a large, coupled design space", fontsize=8.3, color=NAVY,
            ha="center", va="center", bbox=dict(boxstyle="round,pad=0.4", fc="#eaf2fa", ec="#9cc3e6"))


def main():
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.6))
    for ax, f in zip(axs, [patch_antenna, slotted_antenna, hybrid_dgs]):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 9)
        ax.set_aspect("equal")
        ax.axis("off")
        f(ax)
    fig.text(0.5, 0.01, "Illustrative schematics, not to scale (drawn for explanation; not simulation output)", ha="center",
             fontsize=8.5, color="#5f6b76", style="italic")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(FIG / "antenna_types.png", dpi=220, facecolor=BG)
    plt.close(fig)
    print("antenna_types.png written")


if __name__ == "__main__":
    main()
