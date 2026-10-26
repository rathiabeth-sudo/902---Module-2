"""Tests for Module 2: label rules, S11 target extraction, split integrity, cleaning rules and surrogate outputs."""
import json

import numpy as np
import pandas as pd
import pytest

from src.preprocessing import band_label, perf_label, s11_features
from src.utils import ROOT, load_config

CFG = load_config()
PATCH = ROOT / "data" / "processed" / "patch_designs.csv"
MEND = ROOT / "data" / "processed" / "mendeley_clean.csv"
PARETO = ROOT / "results" / "metrics" / "nsga2_pareto_n78.csv"


# ------------------------------------------------------------------ target extraction and label rules
def test_s11_features_first_matched_resonance():
    f = np.linspace(1e9, 10e9, 1000)
    s = -1 - 14 * np.exp(-((f - 3e9) / 0.05e9) ** 2) - 29 * np.exp(-((f - 8e9) / 0.05e9) ** 2)
    r = s11_features(f, s)
    assert abs(r["f_res_ghz"] - 3.0) < 0.02          # first matched dip, not the deepest
    assert abs(r["f_deepest_ghz"] - 8.0) < 0.02
    assert r["s11_min_db"] < -29.5 and r["bw10_mhz"] > 0


def test_s11_features_unmatched():
    f = np.linspace(1e9, 10e9, 1000)
    s = -1 - 5 * np.exp(-((f - 5e9) / 0.2e9) ** 2)
    r = s11_features(f, s)
    assert r["bw10_mhz"] == 0 and r["fbw10_pct"] == 0
    assert abs(r["f_res_ghz"] - 5.0) < 0.02


def test_label_thresholds():
    assert perf_label(-9.99, CFG) == 0
    assert perf_label(-10.0, CFG) == 1
    assert perf_label(-20.0, CFG) == 2
    assert band_label(4.99, CFG) == 0 and band_label(5.0, CFG) == 1 and band_label(7.125, CFG) == 2


# ------------------------------------------------------------------ processed data
@pytest.fixture(scope="module")
def patch():
    if not PATCH.exists():
        pytest.skip("run `python -m src.preprocessing` first")
    return pd.read_csv(PATCH)


def test_split_is_disjoint_and_matches_locked_manifests(patch):
    assert patch.design_id.is_unique
    for name in ["train", "val", "test", "ood"]:
        locked = set(pd.read_csv(ROOT / "data" / "splits" / f"patch_{name}_ids.csv").design_id)
        assert locked == set(patch.loc[patch.split == name, "design_id"])


def test_ood_rule(patch):
    assert (patch.loc[patch.split == "ood", "wl_ratio"] > CFG["split"]["ood_wl_ratio_min"]).all()
    assert (patch.loc[patch.split != "ood", "wl_ratio"] <= CFG["split"]["ood_wl_ratio_min"]).all()


def test_targets_are_physical(patch):
    assert patch[["f_res_ghz", "s11_min_db", "bw10_mhz"]].notna().all().all()
    assert patch.f_res_ghz.between(1, 10).all()
    assert (patch.bw10_mhz >= 0).all()
    assert (patch.s11_min_db <= patch.s11_at_res_db + 1e-9).all()
    assert (patch.perf_class == [perf_label(v, CFG) for v in patch.s11_min_db]).all()


def test_mendeley_plausibility_rule():
    if not MEND.exists():
        pytest.skip("run `python -m src.preprocessing` first")
    m = pd.read_csv(MEND)
    ok = m[m.plausible]
    assert (ok.Rad_eff <= 1).all() and (ok.Directivity <= 20).all()
    assert (ok.Gain <= ok.Directivity + 0.01).all()
    assert m.design_id.nunique() == 103 and m.Freq_GHz.nunique() == 16


def test_module1_embeddings_align_with_split(patch):
    d = ROOT / CFG["fusion"]["embedding_dir"]
    for s in ["train", "val", "test", "ood"]:
        e = np.load(d / f"{CFG['fusion']['embedding_run']}_{s}.npy")
        assert e.shape == ((patch.split == s).sum(), 384)
        assert np.isfinite(e).all()


# ------------------------------------------------------------------ results
def test_pareto_proposals_satisfy_constraints():
    if not PARETO.exists():
        pytest.skip("run `python -m src.fusion_optimization` first")
    par = pd.read_csv(PARETO)
    lo, hi = CFG["nsga2"]["band_ghz"]
    assert par.pred_f_res_ghz.between(lo - 1e-6, hi + 1e-6).all()
    assert (par.status.str.contains("NOT simulated")).all()
    train = pd.read_csv(PATCH).query("split == 'train'")
    assert par.length_mm.between(train.length_mm.min() - 1e-6, train.length_mm.max() + 1e-6).all()


def test_surrogate_beats_mean_baseline():
    f = ROOT / "results" / "metrics" / "numerical_module.json"
    if not f.exists():
        pytest.skip("run `python -m src.numerical_model` first")
    num = json.load(open(f))
    for t, v in num["patch"].items():
        sel = v["models"][v["selected_on_val_MAE"]]["test"]["MAE"]
        assert sel < v["models"]["mean_baseline"]["test"]["MAE"], t
