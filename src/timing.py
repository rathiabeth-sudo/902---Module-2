"""Measure how fast the Module 2 surrogates are (training and prediction) on this machine.

Writes results/metrics/timing.json. Used by the extended presentation to compare AI screening speed with
full-wave simulation; only measured values are stored.

Usage:  python -m src.timing        (run src.numerical_model first)
"""
from __future__ import annotations

import platform
import time

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor

from .numerical_model import PATCH_X, PATCH_Y
from .utils import ROOT, load_config, p, save_json


def main():
    cfg = load_config()
    df = pd.read_csv(ROOT / "data" / "processed" / "patch_designs.csv")
    train, test = df[df.split == "train"], df[df.split == "test"]
    bundle = joblib.load(p(cfg["paths"]["checkpoints"], "patch_surrogates.joblib"))

    # training time for one 400-tree random forest (first matched resonance)
    t0 = time.perf_counter()
    RandomForestRegressor(n_estimators=cfg["surrogate"]["random_forest_trees"], random_state=cfg["seed"], n_jobs=-1).fit(
        train[PATCH_X], train["f_res_ghz"])
    fit_s = time.perf_counter() - t0

    # batch prediction of all four targets for the 262 locked test designs (median of 5 repeats)
    X = test[PATCH_X]
    reps = []
    for _ in range(5):
        t0 = time.perf_counter()
        for t in PATCH_Y:
            bundle["models"][t].predict(X)
        reps.append(time.perf_counter() - t0)
    batch_s = float(np.median(reps))

    # single-design latency (all four targets), median of 20 repeats
    one = X.iloc[[0]]
    lat = []
    for _ in range(20):
        t0 = time.perf_counter()
        for t in PATCH_Y:
            bundle["models"][t].predict(one)
        lat.append(time.perf_counter() - t0)

    out = {"hardware": f"{platform.processor() or 'CPU'} ({platform.system()} {platform.release()})",
           "rf_fit_seconds_one_target": fit_s,
           "n_test_designs": int(len(X)),
           "batch_predict_seconds_all_targets": batch_s,
           "batch_ms_per_design_all_targets": 1000 * batch_s / len(X),
           "single_design_latency_ms_all_targets": 1000 * float(np.median(lat))}
    save_json(out, p("results", "metrics", "timing.json"))
    print(out)


if __name__ == "__main__":
    main()
