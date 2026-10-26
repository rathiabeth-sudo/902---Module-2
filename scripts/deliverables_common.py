"""Load executed Module 2 results for the diagram / poster / slides / report generators.

Every number shown in a deliverable comes from results/metrics/*.json|csv written by the pipeline.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
M = ROOT / "results" / "metrics"
FIG = ROOT / "results" / "figures"

NAVY = "#0b2a4a"
BLUE = "#2f6fae"
LIGHT = "#dbe9f6"
MID = "#9cc3e6"
ACCENT = "#e07b39"
GREEN = "#2e7d4f"
GREY = "#5f6b76"

MODULE = "Module 2 - Numerical-Text Module, Multimodal Fusion and NSGA-II Optimisation"
TITLE = "Numerical-Text Surrogate Modelling and Multi-Objective Optimisation of Compact Patch Antennas"
SUBTITLE = "Module 2 of the Applied Vision Transformer Framework for Hybrid-Slotted DGS Antennas in 5G and Emerging 6G Networks - Proof-of-Concept Prototype"
# Set these once after creating the GitHub repositories; every deliverable reads them from here.
REPO_URL = "https://github.com/rathiabeth/module2-numerical-surrogate-antenna-design"
COMPANION_URL = "https://github.com/rathiabeth/module1-vit-antenna-image-classification"

PATCH_TARGETS = {"f_res_ghz": ("First matched resonance", "GHz"), "s11_min_db": ("Minimum S11", "dB"),
                 "s11_at_res_db": ("S11 at resonance", "dB"), "bw10_mhz": ("−10 dB bandwidth", "MHz")}
MEND_TARGETS = {"S11_dB": ("S11", "dB"), "Gain": ("Gain", "dBi"), "Rad_eff": ("Radiation efficiency", "ratio")}


def j(name):
    with open(M / name, encoding="utf-8") as f:
        return json.load(f)


def load() -> dict:
    R = {"num": j("numerical_module.json"), "clean": j("mendeley_cleaning.json"), "fusion": j("fusion.json"),
         "opt": j("fusion_optimisation.json")["optimisation"],
         "prep": json.load(open(ROOT / "data" / "processed" / "preprocessing_log.json", encoding="utf-8")),
         "pareto": pd.read_csv(M / "nsga2_pareto_n78.csv"),
         "prov": json.load(open(ROOT / "data" / "external" / "module1_vit_embeddings" / "provenance.json", encoding="utf-8"))}
    pt = R["num"]["patch"]
    R["sel"] = lambda k, split="test": pt[k]["models"][pt[k]["selected_on_val_MAE"]][split]
    R["fu"] = {k: v for k, v in R["fusion"].items() if not k.startswith("_")}
    return R


def criteria(R) -> list[tuple[str, str, str]]:
    """(id, statement, verdict-with-evidence). H6 was pre-registered; E1-E3 are evaluation criteria stated in the plan."""
    pt, md, fu, opt, par = R["num"]["patch"], R["num"]["mendeley"], R["fu"], R["opt"], R["pareto"]
    out = []
    ok = all(R["sel"](k)["MAE"] < pt[k]["models"]["mean_baseline"]["test"]["MAE"] for k in pt)
    worst = max(pt, key=lambda k: R["sel"](k)["MAE"] / pt[k]["models"]["mean_baseline"]["test"]["MAE"])
    out.append(("E1", "Surrogate beats the mean baseline on every patch target (test MAE)",
                f"{'Met' if ok else 'Not met'}: all four targets; weakest {worst} "
                f"({R['sel'](worst)['MAE']:.2f} vs {pt[worst]['models']['mean_baseline']['test']['MAE']:.2f})"))
    ok = all(md[t]["random_forest"]["MAE"] < md[t]["random_forest_frequency_only"]["MAE"] for t in md)
    out.append(("E2", "Geometry + frequency beats frequency-only (Mendeley, GroupKFold)",
                f"{'Met' if ok else 'Not met'}: " + "; ".join(
                    f"{t} {md[t]['random_forest']['MAE']:.3f} vs {md[t]['random_forest_frequency_only']['MAE']:.3f}" for t in md)))
    fi, im, nu = fu["fusion_concat"]["test"]["macro_f1"], fu["image_only"]["test"]["macro_f1"], fu["numeric_only"]["test"]["macro_f1"]
    out.append(("H6", "Fusion (ViT embedding + numeric) > image-only (pre-registered)",
                f"{'Supported' if fi > im else 'Not supported'}: {fi:.3f} vs {im:.3f} (numeric-only {nu:.3f})"))
    lo, hi = opt["band_ghz"]
    ok = opt["n_pareto"] > 0 and par.pred_f_res_ghz.between(lo, hi).all()
    out.append(("E3", "NSGA-II returns feasible n78 proposals inside the training ranges",
                f"{'Met' if ok else 'Not met'}: {opt['n_pareto']} proposals, median distance to nearest simulated design "
                f"{opt['median_nearest_distance_std']:.2f} SD (surrogate only, not simulated)"))
    return out


BRANCH = "main"


def gh(path: str, folder: bool = False) -> str:
    """Clickable GitHub link to a file (blob) or folder (tree) in this repository."""
    return f"{REPO_URL}/{'tree' if folder else 'blob'}/{BRANCH}/{path}"


def link(path: str, folder: bool = False, label: str | None = None) -> str:
    """Report markup [label](url) that report_render turns into a hyperlink."""
    return f"[{label or path}]({gh(path, folder)})"


def test_summary() -> str:
    """Last line of the stored pytest output, e.g. '18 passed in 4.18s'."""
    lines = [l.strip() for l in (ROOT / "results" / "test_report.txt").read_text(encoding="utf-8").splitlines() if l.strip()]
    return lines[-1] if lines else "not run"
