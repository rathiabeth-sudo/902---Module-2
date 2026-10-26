"""Module 2 block diagram (implemented vs proposed), in the style of the framework figure.

Writes results/figures/module2_architecture.png.
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

from deliverables_common import ACCENT, BLUE, FIG, NAVY

IMPL, PROP, TAB, OUT, FUS = "#e8f1fa", "#fdf1e7", "#fff6e0", "#eaf5ee", "#eef0fb"
GOLD, VIOLET, GREENE = "#d7a33b", "#7b7fc4", "#5e9e6e"


def box(ax, x, y, w, h, text="", fc=IMPL, ec=BLUE, fs=8.2, bold=False, dashed=False, tc=NAVY):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.01", fc=fc, ec=ec,
                                lw=1.2, ls="--" if dashed else "-"))
    if text:
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
                fontweight="bold" if bold else "normal", linespacing=1.3)


def group(ax, x, y, w, h, title, ec, fc="white"):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.004,rounding_size=0.015", fc=fc, ec=ec, lw=1.6))
    ax.text(x + 0.008, y + h - 0.014, title, fontsize=9.5, fontweight="bold", color=NAVY, va="top")


def arrow(ax, x1, y1, x2, y2, color=NAVY, dashed=False):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=11, lw=1.2, color=color,
                                 ls="--" if dashed else "-"))


def main():
    fig = plt.figure(figsize=(13, 6.6))
    ax = fig.add_axes([0.005, 0.01, 0.99, 0.98])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(Rectangle((0, 0.94), 1, 0.06, fc=NAVY, ec="none"))
    ax.text(0.5, 0.97, "Module 2 - Numerical-Text Module, Multimodal Fusion and NSGA-II Optimisation", color="white",
            fontsize=13, fontweight="bold", ha="center", va="center")

    # 1 numerical inputs
    group(ax, 0.008, 0.40, 0.19, 0.52, "1  Numerical inputs", "#7fb37f")
    box(ax, 0.018, 0.70, 0.17, 0.17, "openEMS patch sweep (MIT)\n2,051 designs: L, W, feed\noffset, W/L, feed ratio\n+ 1,000-point S11 curve")
    box(ax, 0.018, 0.52, 0.17, 0.15, "Mendeley dual-slot patch\n(CC BY 4.0): 103 designs ×\n16 f; 10 dimensions incl.\nslots, substrate, feed")
    box(ax, 0.018, 0.42, 0.17, 0.08, "HFSS DGS parameters\n(proposed)", fc=PROP, ec=ACCENT, dashed=True, fs=7.8)

    # 2 preparation
    group(ax, 0.21, 0.40, 0.17, 0.52, "2  Preparation", "#7fb37f")
    box(ax, 0.22, 0.70, 0.15, 0.17, "S11 curve → targets:\nfirst matched f_res,\nS11 min, S11 at f_res,\n−10 dB bandwidth")
    box(ax, 0.22, 0.555, 0.15, 0.12, "Plausibility rules:\n245 solver rows flagged\n(eff > 1, gain > D, …)")
    box(ax, 0.22, 0.42, 0.15, 0.11, "Locked split shared\nwith Module 1 (seed 42)\n+ OOD W/L > 1.95")

    # 3 tabular surrogate + text
    group(ax, 0.393, 0.40, 0.33, 0.52, "3  Tabular encoder / regression + text generation", GOLD, fc="#fffdf6")
    box(ax, 0.403, 0.68, 0.145, 0.19, "Candidate surrogates\nmean baseline · ridge\nhist. gradient boosting\nrandom forest (400)\nselected on val MAE", fc=TAB, ec=GOLD)
    arrow(ax, 0.548, 0.775, 0.566, 0.775)
    box(ax, 0.568, 0.68, 0.145, 0.19, "Predictions\nf_res · S11 · BW (patch)\nS11 · gain · radiation\nefficiency (Mendeley,\nGroupKFold by design)", fc=TAB, ec=GOLD)
    box(ax, 0.403, 0.45, 0.285, 0.19, "", fc=TAB, ec=GOLD)
    ax.text(0.5455, 0.618, "Rule-based engineering summary (text)", fontsize=8.4, ha="center", va="top", color=NAVY, fontweight="bold")
    ax.text(0.5455, 0.588, "\"Predicted first matched resonance 3.57 GHz, inside\n5G NR n78; predicted minimum S11 −26.1 dB (High\n"
            "class); predicted bandwidth 45 MHz … requires\nfull-wave verification.\"  (computed numbers only)",
            fontsize=7.4, ha="center", va="top", color="#40505e", style="italic", linespacing=1.35)
    arrow(ax, 0.60, 0.68, 0.60, 0.64)

    # 4 outputs of the numerical module
    group(ax, 0.738, 0.40, 0.254, 0.52, "4  Module 2 outputs", GREENE)
    for t, y in [("Resonant frequency (GHz)\n+ band (n78 / FR1 / FR3)", 0.765), ("S11 and −10 dB bandwidth", 0.665),
                 ("Gain, radiation efficiency\n(Mendeley slotted patch)", 0.555), ("Engineering summaries (text)", 0.445)]:
        box(ax, 0.748, y, 0.234, 0.085, t, fc=OUT, ec=GREENE, fs=8)

    # 5 fusion and optimisation
    group(ax, 0.008, 0.06, 0.984, 0.315, "5  Multimodal fusion and multi-objective optimisation", VIOLET, fc="#fbfbff")
    box(ax, 0.02, 0.22, 0.15, 0.09, "Image features from Module 1\n384-d ViT CLS embedding", fc="#dceafa", ec=BLUE, fs=7.8)
    box(ax, 0.02, 0.10, 0.15, 0.09, "Numerical features\n(5 standardised parameters)", fc=TAB, ec=GOLD, fs=7.8)
    box(ax, 0.21, 0.13, 0.15, 0.15, "Feature fusion\nconcatenate → MLP\n(hidden size, L2 on val)\nvs image-only, numeric-only", fc=FUS, ec=VIOLET, fs=7.8)
    box(ax, 0.39, 0.13, 0.13, 0.15, "Matching class\n(Poor / Acceptable /\nHigh) - tests H6", fc=OUT, ec=GREENE, fs=7.8)
    box(ax, 0.55, 0.11, 0.17, 0.19, "NSGA-II (pymoo)\nvariables: L, W/L, feed ratio\nmin S11 at f_res · max BW\nmin area\ns.t. predicted f_res in n78\npop 100 × 80 generations", fc=FUS, ec=VIOLET, fs=7.6)
    box(ax, 0.745, 0.17, 0.115, 0.13, "Pareto proposals\n+ nearest simulated\ndesign (NOT\nsimulated)", fc=OUT, ec=GREENE, fs=7.6)
    box(ax, 0.875, 0.17, 0.107, 0.13, "HFSS re-simulation,\nfabrication &\nmeasurement\n(proposed)", fc=PROP, ec=ACCENT, dashed=True, fs=7.6)
    ax.add_patch(FancyBboxPatch((0.30, 0.075), 0.02, 0.022, boxstyle="round,pad=0.002", fc=IMPL, ec=BLUE))
    ax.text(0.325, 0.086, "implemented & executed", fontsize=8, va="center", color=NAVY)
    ax.add_patch(FancyBboxPatch((0.49, 0.075), 0.02, 0.022, boxstyle="round,pad=0.002", fc=PROP, ec=ACCENT, ls="--"))
    ax.text(0.515, 0.086, "proposed future work (requires Ansys HFSS)", fontsize=8, va="center", color=NAVY)

    # arrows
    arrow(ax, 0.188, 0.785, 0.22, 0.785)
    arrow(ax, 0.188, 0.595, 0.22, 0.615)
    arrow(ax, 0.188, 0.46, 0.22, 0.47, color=ACCENT, dashed=True)
    arrow(ax, 0.37, 0.785, 0.403, 0.775)
    arrow(ax, 0.37, 0.475, 0.403, 0.70)
    arrow(ax, 0.713, 0.80, 0.748, 0.80)
    arrow(ax, 0.713, 0.72, 0.748, 0.70)
    arrow(ax, 0.713, 0.70, 0.748, 0.595)
    arrow(ax, 0.688, 0.53, 0.748, 0.49)
    arrow(ax, 0.17, 0.265, 0.21, 0.235)
    arrow(ax, 0.17, 0.145, 0.21, 0.175)
    arrow(ax, 0.36, 0.205, 0.39, 0.205)
    arrow(ax, 0.703, 0.68, 0.665, 0.30)       # surrogates drive NSGA-II
    ax.text(0.672, 0.40, "surrogates", fontsize=7.2, color=VIOLET, rotation=84, ha="center", va="center")
    arrow(ax, 0.72, 0.235, 0.745, 0.235)
    arrow(ax, 0.86, 0.235, 0.875, 0.235, color=ACCENT, dashed=True)

    fig.savefig(FIG / "module2_architecture.png", dpi=220, bbox_inches="tight", pad_inches=0.05)
    plt.close(fig)
    print("module2_architecture.png written")


if __name__ == "__main__":
    main()
