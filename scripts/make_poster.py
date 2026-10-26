"""Module 2 research poster (16:9, 20 x 11.25 in) -> poster/module2_poster.png (300 dpi) + .pdf.

All numbers and plots come from executed results (results/metrics, results/figures).
"""
from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from deliverables_common import (ACCENT, BLUE, FIG, GREY, LIGHT, MEND_TARGETS, NAVY, PATCH_TARGETS, REPO_URL, ROOT, SUBTITLE,
                                 TITLE, criteria, load)

W, H = 20, 11.25
SHORT = {"E1": "Surrogate beats mean baseline (all targets)", "E2": "Slot geometry adds to frequency",
         "H6": "Fusion beats image-only (pre-registered)", "E3": "Feasible n78 proposals in range"}
EDGE = "#9cc3e6"


def panel(fig, x, y, w, h, title, num=None):
    ax = fig.add_axes([x, y, w, h])
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    ax.add_patch(FancyBboxPatch((0.003, 0.003), 0.994, 0.994, boxstyle="round,pad=0,rounding_size=0.02",
                                fc="white", ec=EDGE, lw=1.2, transform=ax.transAxes))
    hh = 0.0486 / h
    ax.add_patch(Rectangle((0.003, 1 - hh), 0.994, hh - 0.003, fc=LIGHT, ec="none", transform=ax.transAxes))
    ax.text(0.02, 1 - hh / 2, (f"{num}  " if num else "") + title, fontsize=15, fontweight="bold", color=NAVY,
            va="center", transform=ax.transAxes)
    return ax, 1 - hh


def image(fig, path, x, y, w, h):
    ax = fig.add_axes([x, y, w, h])
    ax.imshow(mpimg.imread(path))
    ax.axis("off")
    return ax


def bullets(ax, items, x, y, fs=11.2, dy=0.075, color="#1b2733"):
    for it in items:
        ax.text(x, y, "• " + it, fontsize=fs, color=color, va="top", transform=ax.transAxes, linespacing=1.3)
        y -= dy * (1 + it.count("\n"))
    return y


def main():
    R = load()
    num, fu, opt, prep, clean, prov = R["num"], R["fu"], R["opt"], R["prep"], R["clean"], R["prov"]
    pt, md, sel = num["patch"], num["mendeley"], R["sel"]
    sc = prep["patch_split_counts"]
    fi, im, nu = (fu[k]["test"]["macro_f1"] for k in ["fusion_concat", "image_only", "numeric_only"])
    lo, hi = opt["band_ghz"]

    fig = plt.figure(figsize=(W, H), facecolor="white")
    hd = fig.add_axes([0, 0.885, 1, 0.115])
    hd.axis("off")
    hd.add_patch(Rectangle((0, 0), 1, 1, fc=NAVY, transform=hd.transAxes))
    hd.text(0.5, 0.70, TITLE, color="white", fontsize=25, fontweight="bold", ha="center", va="center")
    hd.text(0.5, 0.40, SUBTITLE, color="#cfe2f3", fontsize=14, ha="center", va="center")
    hd.text(0.5, 0.13, "Ms. Rathi Devadhas  |  Student ID 1737089  |  Master of Applied Artificial Intelligence  |  Applied AI Research Workshop - Module 2  |  26 October 2026",
            color="white", fontsize=11.5, ha="center", va="center", style="italic")

    # ---------------- column 1
    ax, top = panel(fig, 0.008, 0.585, 0.27, 0.29, "Research objective", "1")
    bullets(ax, ["How well do antenna parameters predict simulated\nresonance, S11, bandwidth, gain and efficiency?",
                 "Do numbers add to Module 1's ViT image features?\nCan NSGA-II on surrogates propose n78 designs?",
                 "Text summaries must never invent values.",
                 "Proof of concept on public simulation data;\nAnsys HFSS was not available and was not run."], 0.03, top - 0.04, fs=11, dy=0.085)

    ax, top = panel(fig, 0.008, 0.07, 0.27, 0.505, "Data & preparation", "2")
    bullets(ax, ["openEMS patch sweep (Hugging Face, MIT): 2,051\ndesigns; S11 curve -> 4 engineering targets",
                 f"Mendeley dual-slot patch v2 (CC BY 4.0): 103 x 16 f;\n{clean['implausible_rows_flagged']} implausible solver rows flagged by a fixed rule",
                 f"Split shared with Module 1: {sc['train']:,} / {sc['val']} / {sc['test']}\n+ OOD W/L > 1.95 (n = {sc['ood']}); GroupKFold for Mendeley",
                 "Model selection on validation only; test scored once"], 0.03, top - 0.03, fs=10.4, dy=0.04)
    image(fig, FIG / "s11_target_extraction.png", 0.012, 0.08, 0.262, 0.215)

    # ---------------- column 2
    ax, top = panel(fig, 0.285, 0.495, 0.43, 0.38, "Module 2 block diagram (implemented vs proposed)", "3")
    image(fig, FIG / "module2_architecture.png", 0.29, 0.50, 0.42, 0.33)

    ax, top = panel(fig, 0.285, 0.07, 0.43, 0.415, "Surrogate results (executed)", "4")
    image(fig, FIG / "numerical_parity_patch.png", 0.29, 0.30, 0.42, 0.11)
    tbl = [("Target (random forest)", "Test R²", "MAE", "OOD R²")]
    for k in pt:
        tbl.append((f"{PATCH_TARGETS[k][0]} [{PATCH_TARGETS[k][1]}]", f"{sel(k)['R2']:.2f}", f"{sel(k)['MAE']:.2f}", f"{sel(k, 'ood')['R2']:.2f}"))
    for t in md:
        tbl.append((f"Mendeley {MEND_TARGETS[t][0]} [{MEND_TARGETS[t][1]}]", f"{md[t]['random_forest']['R2']:.2f}",
                    f"{md[t]['random_forest']['MAE']:.2f}", "-"))
    y0 = 0.50
    for i, row in enumerate(tbl):
        w = "bold" if i == 0 else "normal"
        col = BLUE if i == 0 else NAVY
        for x, v in zip([0.03, 0.38, 0.49, 0.60], row):
            ax.text(x, y0 - i * 0.052, v, fontsize=10.3, fontweight=w, color=col, transform=ax.transAxes)
    ax.text(0.72, y0, "Takeaways", fontsize=10.5, fontweight="bold", color=BLUE, transform=ax.transAxes)
    ax.text(0.72, y0 - 0.05, "Resonance and bandwidth:\nwell predicted\n\nMatching depth: moderate\n(sharp impedance effect)\n\n"
            "Wide OOD patches: fails\n-> search kept in range\n\nSlot geometry halves the\nfrequency-only error",
            fontsize=9.6, color=NAVY, transform=ax.transAxes, va="top", linespacing=1.25)
    ax.text(0.03, 0.035, "Mendeley: out-of-fold, 5-fold GroupKFold by design; gain and efficiency on plausible rows only",
            fontsize=8.6, color=GREY, style="italic", transform=ax.transAxes)

    # ---------------- column 3
    ax, top = panel(fig, 0.722, 0.625, 0.27, 0.25, "Multimodal fusion (H6)", "5")
    image(fig, FIG / "fusion_confusion.png", 0.726, 0.70, 0.262, 0.105)
    ax.text(0.03, 0.22, f"Test macro-F1: fusion {fi:.3f} | image-only {im:.3f} | numeric-only {nu:.3f}", fontsize=10, color=NAVY,
            transform=ax.transAxes)
    ax.text(0.03, 0.09, f"H6 not supported. ViT embeddings alone beat Module 1's own head ({prov['module1_vit_linear_head_test_macro_f1']:.3f})",
            fontsize=9, color=GREY, style="italic", transform=ax.transAxes)

    ax, top = panel(fig, 0.722, 0.345, 0.27, 0.27, f"NSGA-II for 5G NR n78 ({lo}-{hi} GHz)", "6")
    image(fig, FIG / "nsga2_pareto_n78.png", 0.726, 0.352, 0.14, 0.215)
    yy = top - 0.06
    for line in [f"{opt['n_pareto']} Pareto proposals", f"area {opt['pareto_area_range_mm2'][0]:.0f}-{opt['pareto_area_range_mm2'][1]:.0f} mm²",
                 f"pred. BW {opt['pareto_pred_bw_range_mhz'][0]:.0f}-{opt['pareto_pred_bw_range_mhz'][1]:.0f} MHz",
                 f"median {opt['median_nearest_distance_std']:.2f} SD from a\nsimulated design", "Predictions only -\nNOT simulated"]:
        ax.text(0.55, yy, line, fontsize=9.8, color=NAVY if "NOT" not in line else ACCENT, transform=ax.transAxes, va="top",
                fontweight="bold" if "NOT" in line else "normal")
        yy -= 0.11 * (1 + line.count("\n"))

    ax, top = panel(fig, 0.722, 0.07, 0.27, 0.265, "Outcomes & conclusion", "7")
    yy = top - 0.05
    for cid, stmt, verdict in criteria(R):
        ok = verdict.startswith(("Supported", "Met"))
        ax.text(0.03, yy, cid, fontsize=9.6, fontweight="bold", color=NAVY, transform=ax.transAxes, va="top")
        ax.text(0.11, yy, SHORT[cid], fontsize=9.2, color=NAVY, transform=ax.transAxes, va="top")
        ax.text(0.97, yy, verdict.split(":")[0], fontsize=9.2, fontweight="bold", ha="right",
                color="#1f6f2a" if ok else ACCENT, transform=ax.transAxes, va="top")
        yy -= 0.095
    bullets(ax, ["Surrogates are only trustworthy where they were trained",
                 "Next: space-filling HFSS DGS sweep + re-simulation"], 0.03, yy - 0.01, fs=9.4, dy=0.085, color=GREY)

    ft = fig.add_axes([0, 0, 1, 0.062])
    ft.axis("off")
    ft.add_patch(Rectangle((0, 0), 1, 1, fc="#eef4fa", transform=ft.transAxes))
    ft.text(0.5, 0.66, "Fast, traceable surrogate screening of compact patch antennas for 5G / 6G - simulation evidence only, proposals not HFSS-validated",
            ha="center", fontsize=13, fontweight="bold", color=NAVY)
    ft.text(0.5, 0.33, "Data: LaBash et al. (2025) arXiv:2505.18188 [MIT]  |  Mihad, Islam & Sojib (2024) Antenna Parameters Dataset v2, doi:10.17632/3gxr2vvd9n.2 [CC BY 4.0]",
            ha="center", fontsize=8.6, color=GREY)
    ft.text(0.5, 0.08, "Random forest: Breiman (2001)  |  NSGA-II: Deb et al. (2002)  |  pymoo: Blank & Deb (2020)  |  Code: " + REPO_URL,
            ha="center", fontsize=8.6, color=GREY)

    out = ROOT / "poster"
    out.mkdir(exist_ok=True)
    fig.savefig(out / "module2_poster.png", dpi=300)
    fig.savefig(out / "module2_poster.pdf")
    plt.close(fig)
    print("poster written")


if __name__ == "__main__":
    main()
