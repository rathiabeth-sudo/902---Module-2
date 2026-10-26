"""Module 2 data preparation (tabular only - no images are produced in this module).

* Patch (openEMS, 2,051 designs): reduce each 1,000-point S11 curve to engineering targets
  (first matched resonance, minimum S11, S11 at resonance, -10 dB bandwidth), derive the
  documented class labels and reproduce the locked design-level split shared with Module 1.
* Mendeley dual-slot patch: clean column names and types, assign design IDs, flag physically
  implausible solver rows (documented rule), save a cleaned table.
* Data dictionary: written to data/data_dictionary.csv.

Usage:  python -m src.preprocessing
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .utils import ROOT, load_config, p, save_json


# --------------------------------------------------------------------------------------
# S11 feature extraction and label rules (identical to Module 1)
# --------------------------------------------------------------------------------------
def s11_features(freq_hz: np.ndarray, s11_db: np.ndarray, thr: float = -10.0) -> dict:
    """Global minimum S11 plus the FIRST matched resonance and its -10 dB bandwidth.

    The deepest dip is often a higher-order mode, so the resonant frequency is defined as the
    lowest-frequency local minimum below `thr`. If the design is never matched, the global
    minimum is used and the bandwidth is 0.
    """
    g = int(np.argmin(s11_db))
    smin = float(s11_db[g])
    is_min = np.r_[False, (s11_db[1:-1] <= s11_db[:-2]) & (s11_db[1:-1] <= s11_db[2:]), False]
    cand = np.where(is_min & (s11_db < thr))[0]
    j = int(cand[0]) if len(cand) else g
    f_res = float(freq_hz[j] / 1e9)
    bw_mhz = 0.0
    if s11_db[j] < thr:
        lo = j
        while lo > 0 and s11_db[lo - 1] < thr:
            lo -= 1
        hi = j
        while hi < len(s11_db) - 1 and s11_db[hi + 1] < thr:
            hi += 1
        bw_mhz = float((freq_hz[hi] - freq_hz[lo]) / 1e6)
    return {"f_res_ghz": f_res, "s11_min_db": smin, "s11_at_res_db": float(s11_db[j]),
            "f_deepest_ghz": float(freq_hz[g] / 1e9), "bw10_mhz": bw_mhz,
            "fbw10_pct": 100.0 * bw_mhz / (f_res * 1e3) if bw_mhz > 0 else 0.0}


def perf_label(s11_min: float, cfg: dict) -> int:
    if s11_min > cfg["labels"]["s11_matched_db"]:
        return 0  # Poor: no -10 dB match anywhere in 1-10 GHz
    if s11_min > cfg["labels"]["s11_high_db"]:
        return 1  # Acceptable
    return 2      # High


def band_label(f_res: float, cfg: dict) -> int:
    return int(np.searchsorted(cfg["labels"]["band_edges_ghz"], f_res, side="right"))


# --------------------------------------------------------------------------------------
# Patch dataset
# --------------------------------------------------------------------------------------
def prepare_patch(cfg: dict, log: dict) -> pd.DataFrame:
    raw = pd.read_parquet(p(cfg["paths"]["raw"], "patch", "train.parquet"))
    log["patch_raw_rows"] = len(raw)
    rows, excluded = [], []
    for r in raw.itertuples(index=False):
        f = np.asarray(r.frequencies, dtype=float)
        s = np.asarray(r.s11, dtype=float)
        if len(f) != 1000 or not np.all(np.isfinite(s)):
            excluded.append({"id": int(r.id), "reason": "missing or non-finite S11"})
            continue
        feats = s11_features(f, s, cfg["labels"]["s11_matched_db"])
        rows.append({"design_id": f"P{int(r.id):04d}", "source_id": int(r.id),
                     "length_mm": float(r.length), "width_mm": float(r.width), "feed_y_mm": float(r.feed_y),
                     "s11_max_db": float(s.max()), **feats})
    df = pd.DataFrame(rows)
    log["patch_excluded"] = excluded
    log["patch_positive_s11_designs"] = int((df.s11_max_db > 0).sum())  # small passive-port solver artefact
    dup = df.duplicated(subset=["length_mm", "width_mm", "feed_y_mm"])
    log["patch_duplicate_parameter_rows"] = int(dup.sum())
    df = df[~dup].reset_index(drop=True)

    df["wl_ratio"] = df.width_mm / df.length_mm
    df["feed_ratio"] = -df.feed_y_mm / (df.length_mm / 2)  # 0 = centre, 1 = patch edge
    df["area_mm2"] = df.width_mm * df.length_mm
    df["perf_class"] = [perf_label(v, cfg) for v in df.s11_min_db]
    df["band_class"] = [band_label(v, cfg) for v in df.f_res_ghz]
    log["patch_missing_values"] = int(df.isna().sum().sum())

    # Split: OOD hold-out first, then design-level stratified 70/15/15 (same algorithm and seed as Module 1).
    ood = df.wl_ratio > cfg["split"]["ood_wl_ratio_min"]
    df["split"] = ""
    df.loc[ood, "split"] = "ood"
    pool = df[~ood]
    seed = cfg["seed"]
    tr, rest = train_test_split(pool, test_size=1 - cfg["split"]["train"], stratify=pool.perf_class, random_state=seed)
    va, te = train_test_split(rest, test_size=cfg["split"]["test"] / (cfg["split"]["val"] + cfg["split"]["test"]),
                              stratify=rest.perf_class, random_state=seed)
    for name, part in [("train", tr), ("val", va), ("test", te)]:
        df.loc[part.index, "split"] = name
    assert (df.split != "").all()

    # The split must equal the locked manifests shared with Module 1 (leakage / consistency guard).
    for name in ["train", "val", "test", "ood"]:
        f = ROOT / cfg["paths"]["splits"] / f"patch_{name}_ids.csv"
        ours = df.loc[df.split == name, ["design_id", "perf_class", "band_class"]]
        if f.exists():
            if set(pd.read_csv(f).design_id) != set(ours.design_id):
                raise RuntimeError(f"split '{name}' differs from the locked manifest {f.name}")
        else:
            ours.to_csv(p(cfg["paths"]["splits"], f.name), index=False)
    log["patch_split_matches_locked_manifests"] = True

    df.to_csv(p(cfg["paths"]["processed"], "patch_designs.csv"), index=False)
    log["patch_split_counts"] = df.split.value_counts().to_dict()
    log["patch_perf_by_split"] = pd.crosstab(df.split, df.perf_class).to_dict()
    log["patch_band_by_split"] = pd.crosstab(df.split, df.band_class).to_dict()
    return df


# --------------------------------------------------------------------------------------
# Mendeley dual-slot dataset
# --------------------------------------------------------------------------------------
MENDELEY_GEOM = ["Sub_W", "Sub_L", "Sub_H", "Patch_W", "Patch_L", "Feed_W", "Slot1_W", "Slot1_L", "Slot2_W", "Slot2_L"]


def prepare_mendeley(cfg: dict, log: dict) -> pd.DataFrame:
    x = pd.read_excel(p(cfg["paths"]["raw"], "mendeley", "Antenna_Parameters.xlsx"), sheet_name="Sheet1")
    clean = {"rows_raw": len(x)}
    x.columns = [c.strip() for c in x.columns]
    x = x.rename(columns={"S11(dB)": "S11_dB"})
    bad_txt = pd.to_numeric(x["Total_eff"], errors="coerce").isna()
    clean["total_eff_non_numeric"] = int(bad_txt.sum())
    x["Total_eff"] = pd.to_numeric(x["Total_eff"], errors="coerce")
    x["design_id"] = x.groupby(MENDELEY_GEOM, sort=False).ngroup()
    clean["unique_designs"] = int(x.design_id.nunique())
    clean["frequencies_ghz"] = sorted(x.Freq_GHz.unique().tolist())
    implausible = (x.Rad_eff > 1) | (x.Total_eff > 1) | (x.Directivity > 20) | (x.Gain > x.Directivity + 0.01)
    clean["implausible_rows_flagged"] = int(implausible.sum())
    clean["rule"] = "flag if Rad_eff>1 or Total_eff>1 or Directivity>20 dBi or Gain>Directivity (physically impossible)"
    clean["duplicate_rows"] = int(x.duplicated().sum())
    x["plausible"] = ~implausible
    clean["plausible_rows"] = int(x.plausible.sum())
    x.to_csv(p(cfg["paths"]["processed"], "mendeley_clean.csv"), index=False)
    save_json(clean, p("results", "metrics", "mendeley_cleaning.json"))
    log["mendeley"] = clean
    return x


DATA_DICTIONARY = [
    # dataset, variable, type, unit, description
    ("patch", "design_id", "string", "-", "Unique design key (P + source id)"),
    ("patch", "length_mm", "float", "mm", "Input: patch length L (resonant dimension)"),
    ("patch", "width_mm", "float", "mm", "Input: patch width W"),
    ("patch", "feed_y_mm", "float", "mm", "Input: coaxial feed offset from patch centre along L (negative toward edge)"),
    ("patch", "wl_ratio", "float", "-", "Input: W/L aspect ratio"),
    ("patch", "feed_ratio", "float", "-", "Input: feed offset normalised by L/2 (0 centre, 1 edge)"),
    ("patch", "area_mm2", "float", "mm^2", "Patch area W x L (optimisation objective)"),
    ("patch", "f_res_ghz", "float", "GHz", "Target: first matched resonance, lowest-frequency local S11 minimum below -10 dB (global minimum if never matched)"),
    ("patch", "f_deepest_ghz", "float", "GHz", "Frequency of the deepest S11 dip in 1-10 GHz (often a higher-order mode)"),
    ("patch", "s11_min_db", "float", "dB", "Target: global minimum simulated S11 over 1-10 GHz (openEMS FDTD)"),
    ("patch", "s11_at_res_db", "float", "dB", "Target: simulated S11 at f_res"),
    ("patch", "bw10_mhz", "float", "MHz", "Target: contiguous -10 dB bandwidth around f_res (0 if unmatched)"),
    ("patch", "fbw10_pct", "float", "%", "Fractional -10 dB bandwidth"),
    ("patch", "perf_class", "int", "0/1/2", "Poor (S11min > -10 dB), Acceptable (-20 < S11min <= -10), High (S11min <= -20 dB); fusion target"),
    ("patch", "band_class", "int", "0/1/2", "f_res < 5 GHz | 5-7.125 GHz | >= 7.125 GHz (3GPP FR1 / FR3 boundary)"),
    ("patch", "split", "category", "train/val/test/ood", "Locked design-level allocation shared with Module 1 (seed 42)"),
    ("mendeley", "design_id", "int", "-", "Design index (unique combination of the 10 geometry variables)"),
    ("mendeley", "Sub_W, Sub_L, Sub_H", "float", "mm", "Input: substrate width, length, height"),
    ("mendeley", "Patch_W, Patch_L", "float", "mm", "Input: patch width and length"),
    ("mendeley", "Feed_W", "float", "mm", "Input: feed-line width"),
    ("mendeley", "Slot1_W, Slot1_L, Slot2_W, Slot2_L", "float", "mm", "Input: dimensions of the two slots"),
    ("mendeley", "Freq_GHz", "float", "GHz", "Input: frequency at which outputs were extracted (16 values, 1-50 GHz)"),
    ("mendeley", "S11_dB", "float", "dB", "Target: simulated reflection coefficient"),
    ("mendeley", "Gain", "float", "dBi", "Target: simulated gain (plausible rows only)"),
    ("mendeley", "Rad_eff", "float", "ratio", "Target: radiation efficiency (plausible rows only)"),
    ("mendeley", "Directivity, Total_eff, VSWR", "float", "dBi / ratio / -", "Other simulated outputs (used for plausibility checks only)"),
    ("mendeley", "plausible", "bool", "-", "False if Rad_eff>1, Total_eff>1, Directivity>20 dBi or Gain>Directivity"),
]


def plot_target_example(cfg: dict, design_id: str = "P1768") -> None:
    """Annotated S11 curve of one test design: how the regression targets are extracted."""
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    raw = pd.read_parquet(p(cfg["paths"]["raw"], "patch", "train.parquet"))
    r = raw[raw.id == int(design_id[1:])].iloc[0]
    f, s = np.asarray(r.frequencies) / 1e9, np.asarray(r.s11, dtype=float)
    t = s11_features(f * 1e9, s, cfg["labels"]["s11_matched_db"])
    fig, ax = plt.subplots(figsize=(7.2, 3.4))
    ax.plot(f, s, color="#0b2a4a", lw=1.4, label="simulated S11 (openEMS)")
    ax.axhline(-10, color="#5f6b76", ls="--", lw=0.9)
    ax.axhline(-20, color="#5f6b76", ls=":", lw=0.9)
    ax.text(9.95, -9.2, "-10 dB (matched)", ha="right", fontsize=8, color="#5f6b76")
    ax.text(9.95, -19.2, "-20 dB (High class, assumption)", ha="right", fontsize=8, color="#5f6b76")
    ax.axvspan(3.3, 3.8, color="#9cc3e6", alpha=0.35, lw=0, label="5G NR n78 (3.3-3.8 GHz)")
    ax.plot(t["f_res_ghz"], t["s11_at_res_db"], "o", color="#e07b39", ms=7, label=f"first matched resonance {t['f_res_ghz']:.2f} GHz")
    ax.plot(t["f_deepest_ghz"], t["s11_min_db"], "v", color="#2e7d4f", ms=7, label=f"S11 min {t['s11_min_db']:.1f} dB")
    m = s < -10
    j = int(np.argmin(np.abs(f - t["f_res_ghz"])))
    lo, hi = j, j
    while lo > 0 and m[lo - 1]:
        lo -= 1
    while hi < len(s) - 1 and m[hi + 1]:
        hi += 1
    ax.annotate("", xy=(f[lo], -12.5), xytext=(f[hi], -12.5), arrowprops=dict(arrowstyle="<->", color="#e07b39"))
    ax.text(f[hi] + 0.1, -13.5, f"-10 dB bandwidth {t['bw10_mhz']:.0f} MHz", fontsize=8, color="#e07b39", va="top")
    ax.set_xlabel("frequency [GHz]")
    ax.set_ylabel("S11 [dB]")
    ax.set_title(f"Target extraction for design {design_id} (L x W = {r.length:.2f} x {r.width:.2f} mm)", fontsize=9.5)
    ax.set_xlim(1, 10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=7.5, loc="lower left")
    fig.tight_layout()
    fig.savefig(p("results", "figures", "s11_target_extraction.png"), dpi=200)
    plt.close(fig)


def main() -> None:
    cfg = load_config()
    log: dict = {}
    df = prepare_patch(cfg, log)
    print("patch:", df.shape, log["patch_split_counts"])
    md = prepare_mendeley(cfg, log)
    print("mendeley:", md.shape, "implausible rows:", log["mendeley"]["implausible_rows_flagged"])
    pd.DataFrame(DATA_DICTIONARY, columns=["dataset", "variable", "type", "unit", "description"]).to_csv(
        p("data", "data_dictionary.csv"), index=False)
    save_json(log, p(cfg["paths"]["processed"], "preprocessing_log.json"))
    plot_target_example(cfg)


if __name__ == "__main__":
    main()
