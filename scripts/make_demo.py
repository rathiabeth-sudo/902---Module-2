"""Build the data files for the Module 2 web demo (docs/demo, served by GitHub Pages).

The demo runs in the browser with no server, so the trained random-forest surrogates are evaluated here
on a dense grid over the simulated design space and saved as JSON. Every number the demo shows is either
a simulated value from the datasets or a surrogate prediction from results/checkpoints/patch_surrogates.joblib.

    python scripts/make_demo.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.numerical_model import PATCH_X, PATCH_Y  # noqa: E402

OUT = ROOT / "docs" / "demo" / "data"
OUT.mkdir(parents=True, exist_ok=True)


def dump(name: str, obj) -> None:
    (OUT / name).write_text(json.dumps(obj, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {name}: {(OUT / name).stat().st_size / 1024:.0f} KB")


def r(x, n=3):
    return [round(float(v), n) for v in x]


def main() -> None:
    bundle = joblib.load(ROOT / "results" / "checkpoints" / "patch_surrogates.joblib")
    models = bundle["models"]

    # 1. surrogate grid: length x (W/L) x feed ratio, the same three numbers that define every design
    L = np.round(np.arange(7.5, 47.5 + 1e-9, 0.25), 3)
    WL = np.round(np.arange(0.80, 2.00 + 1e-9, 0.05), 3)
    FR = np.round(np.linspace(0.0, 0.6667, 21), 4)
    g = np.array(np.meshgrid(L, WL, FR, indexing="ij")).reshape(3, -1).T
    X = pd.DataFrame({"length_mm": g[:, 0], "width_mm": g[:, 0] * g[:, 1], "feed_y_mm": -g[:, 2] * g[:, 0] / 2,
                      "wl_ratio": g[:, 1], "feed_ratio": g[:, 2]})[PATCH_X]
    pred = {t: r(models[t].predict(X), 2) for t in PATCH_Y}
    dump("grid.json", {"L": L.tolist(), "WL": WL.tolist(), "FR": FR.tolist(), "order": "L,WL,FR", **pred})

    # 2. simulated designs + S11 curves reduced from 1,000 to 200 points (minimum of each 5-point bin keeps the dips)
    d = pd.read_csv(ROOT / "data" / "processed" / "patch_designs.csv")
    for t in PATCH_Y:  # exact surrogate prediction for every simulated design (used by the presets)
        d[f"pred_{t}"] = models[t].predict(d[PATCH_X])
    dump("designs.json", {c: (r(d[c], 3) if d[c].dtype.kind == "f" else d[c].tolist()) for c in
                          ["design_id", "length_mm", "width_mm", "feed_y_mm", "wl_ratio", "feed_ratio", "f_res_ghz",
                           "s11_min_db", "s11_at_res_db", "bw10_mhz", "perf_class", "split",
                           *[f"pred_{t}" for t in PATCH_Y]]})
    raw = ROOT / "data" / "raw" / "patch" / "train.parquet"
    if raw.exists():
        p = pd.read_parquet(raw).set_index("id")
        freqs = np.asarray(p.iloc[0]["frequencies"]).reshape(-1, 5).mean(1) / 1e9
        curves = [r(np.asarray(p.loc[int(s), "s11"]).reshape(-1, 5).min(1), 1) for s in d.source_id]
        dump("s11_curves.json", {"f_ghz": r(freqs, 3), "s11": curves})

    # 3. test-set predictions, NSGA-II proposals, Mendeley dual-slot data
    t = pd.read_csv(ROOT / "results" / "predictions" / "patch_surrogate_test.csv")
    dump("test_predictions.json", {c: (r(t[c], 3) if t[c].dtype.kind == "f" else t[c].tolist()) for c in t.columns})
    n = pd.read_csv(ROOT / "results" / "metrics" / "nsga2_pareto_n78.csv")
    dump("nsga2.json", {c: (r(n[c], 3) if n[c].dtype.kind == "f" else n[c].tolist()) for c in
                        ["proposal_id", "length_mm", "width_mm", "feed_y_mm", "pred_f_res_ghz", "pred_s11_at_res_db",
                         "pred_s11_min_db", "pred_bw10_mhz", "area_mm2", "nearest_sim_design", "nearest_distance_std"]})
    m = pd.read_csv(ROOT / "data" / "processed" / "mendeley_clean.csv")
    m = m[m.plausible]
    dump("mendeley.json", {c: (r(m[c], 4) if m[c].dtype.kind == "f" else m[c].tolist()) for c in
                           ["design_id", "Freq_GHz", "S11_dB", "Gain", "Rad_eff", "Patch_W", "Patch_L",
                            "Slot1_L", "Slot2_L"]})

    # 4. headline metrics
    num = json.loads((ROOT / "results" / "metrics" / "numerical_module.json").read_text())
    fus = json.loads((ROOT / "results" / "metrics" / "fusion.json").read_text())
    patch = {}
    for tgt, v in num["patch"].items():
        sel = v["selected_on_val_MAE"]
        patch[tgt] = {"unit": v["unit"], "model": sel, "test": v["models"][sel]["test"], "ood": v["models"][sel]["ood"],
                      "baseline_test_mae": v["models"]["mean_baseline"]["test"]["MAE"]}
    mend = {k: {"rf_r2": v["random_forest"]["R2"], "rf_mae": v["random_forest"]["MAE"],
                "freq_only_mae": v["random_forest_frequency_only"]["MAE"]} for k, v in num["mendeley"].items()}
    fusion = {k: {"test_macro_f1": v["test"]["macro_f1"], "ood_macro_f1": v["ood"]["macro_f1"]}
              for k, v in fus.items() if isinstance(v, dict) and "test" in v}
    dump("metrics.json", {"patch": patch, "mendeley": mend, "fusion": fusion})


if __name__ == "__main__":
    main()
