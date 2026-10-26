"""Module 2 - numerical surrogate regression + rule-based engineering summaries.

A. Patch (openEMS, 2,051 designs): (L, W, feed offset, W/L, feed ratio) -> first matched resonance,
   minimum S11, S11 at resonance, -10 dB bandwidth. Locked design-level split shared with Module 1;
   the OOD hold-out (W/L > 1.95) is reported separately. The model is selected per target on
   validation MAE; the test split is scored once.
B. Mendeley dual-slot patch (103 designs x 16 frequencies): 10 dimensions + frequency -> S11, gain
   and radiation efficiency, 5-fold GroupKFold by design. Physically implausible solver rows are
   excluded from the gain and efficiency targets (rule in results/metrics/mendeley_cleaning.json).

The text component only verbalises numbers produced by the surrogate or read from the dataset;
it never invents values.

Usage:  python -m src.numerical_model        (run src.preprocessing first)
"""
from __future__ import annotations

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance
from sklearn.linear_model import Ridge
from sklearn.model_selection import GroupKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from .metrics import reg_metrics
from .preprocessing import MENDELEY_GEOM
from .utils import ROOT, load_config, p, save_json

PATCH_X = ["length_mm", "width_mm", "feed_y_mm", "wl_ratio", "feed_ratio"]
PATCH_Y = {"f_res_ghz": "GHz", "s11_min_db": "dB", "s11_at_res_db": "dB", "bw10_mhz": "MHz"}
MENDELEY_Y = {"S11_dB": "dB", "Gain": "dBi", "Rad_eff": "ratio"}
NAVY, BLUE, ACCENT, GREY = "#0b2a4a", "#2f6fae", "#e07b39", "#9aa3ad"


def candidates(cfg: dict) -> dict:
    s, c = cfg["seed"], cfg["surrogate"]
    return {
        "mean_baseline": DummyRegressor(),
        "ridge": make_pipeline(StandardScaler(), Ridge(alpha=c["ridge_alpha"])),
        "random_forest": RandomForestRegressor(n_estimators=c["random_forest_trees"], random_state=s, n_jobs=-1),
        "hist_gbr": HistGradientBoostingRegressor(max_iter=c["hist_gbr_iterations"], learning_rate=c["hist_gbr_learning_rate"],
                                                  random_state=s),
    }


def band_text(f: float, cfg: dict) -> str:
    edges = cfg["labels"]["band_edges_ghz"]
    if 3.3 <= f <= 3.8:
        return "inside 5G NR n78 (3.3-3.8 GHz, FR1)"
    if f < edges[0]:
        return "below 5 GHz (FR1 mid-band region)"
    if f < edges[1]:
        return "5-7.125 GHz (upper FR1)"
    return "above 7.125 GHz (FR3, 6G candidate range)"


def match_text(s11: float, cfg: dict) -> str:
    if s11 > cfg["labels"]["s11_matched_db"]:
        return "does not meet the -10 dB matching criterion"
    if s11 > cfg["labels"]["s11_high_db"]:
        return "meets the -10 dB criterion (Acceptable class)"
    return "meets the -20 dB project threshold (High class)"


def engineering_summary(r: pd.Series, pr: dict, cfg: dict) -> str:
    """Verbalise surrogate predictions next to the simulated reference. Every number is computed, none is invented."""
    return (f"**{r.design_id}** - patch L x W = {r.length_mm:.2f} x {r.width_mm:.2f} mm (W/L {r.wl_ratio:.2f}), feed offset "
            f"{r.feed_y_mm:.2f} mm. Predicted first matched resonance {pr['f_res_ghz']:.2f} GHz, {band_text(pr['f_res_ghz'], cfg)}; "
            f"predicted minimum S11 {pr['s11_min_db']:.1f} dB, which {match_text(pr['s11_min_db'], cfg)}; predicted -10 dB bandwidth "
            f"{max(pr['bw10_mhz'], 0):.0f} MHz. Simulated reference (openEMS): {r.f_res_ghz:.2f} GHz, {r.s11_min_db:.1f} dB, "
            f"{r.bw10_mhz:.0f} MHz. Status: surrogate screening only - requires full-wave verification.")


def patch_regression(cfg: dict) -> dict:
    df = pd.read_csv(ROOT / "data" / "processed" / "patch_designs.csv")
    parts = {s: df[df.split == s] for s in ["train", "val", "test", "ood"]}
    out, best_models, preds = {}, {}, {}
    for target, unit in PATCH_Y.items():
        res = {}
        for name, mdl in candidates(cfg).items():
            mdl.fit(parts["train"][PATCH_X], parts["train"][target])
            res[name] = {s: reg_metrics(parts[s][target], mdl.predict(parts[s][PATCH_X])) for s in ["val", "test", "ood"]}
            res[name]["_model"] = mdl
        chosen = min((n for n in res if n != "mean_baseline"), key=lambda n: res[n]["val"]["MAE"])
        best_models[target] = res[chosen]["_model"]
        preds[target] = best_models[target].predict(parts["test"][PATCH_X])
        imp = permutation_importance(best_models[target], parts["val"][PATCH_X], parts["val"][target],
                                     n_repeats=10, random_state=cfg["seed"], scoring="neg_mean_absolute_error")
        out[target] = {"unit": unit, "selected_on_val_MAE": chosen,
                       "permutation_importance_val_MAE": dict(zip(PATCH_X, imp.importances_mean.tolist())),
                       "models": {n: {k: v for k, v in r.items() if k != "_model"} for n, r in res.items()}}
        print(f"[patch] {target}: selected {chosen}  test MAE={res[chosen]['test']['MAE']:.3f} R2={res[chosen]['test']['R2']:.3f}")
    joblib.dump({"features": PATCH_X, "models": best_models}, p(cfg["paths"]["checkpoints"], "patch_surrogates.joblib"))
    pd.DataFrame({"design_id": parts["test"].design_id.to_numpy(),
                  **{f"true_{t}": parts["test"][t].to_numpy() for t in PATCH_Y},
                  **{f"pred_{t}": preds[t] for t in PATCH_Y}}).to_csv(p("results", "predictions", "patch_surrogate_test.csv"), index=False)

    # parity plots (test split)
    fig, axs = plt.subplots(1, 4, figsize=(15, 3.8))
    for ax, (t, unit) in zip(axs, PATCH_Y.items()):
        y = parts["test"][t].to_numpy()
        ax.scatter(y, preds[t], s=9, alpha=0.6, color="#1f4e79")
        lo, hi = min(y.min(), preds[t].min()), max(y.max(), preds[t].max())
        ax.plot([lo, hi], [lo, hi], "--", color="#c0504d", lw=1)
        m = out[t]["models"][out[t]["selected_on_val_MAE"]]["test"]
        ax.set_title(f"{t}  (R² = {m['R2']:.2f}, MAE = {m['MAE']:.2f} {unit})", fontsize=9)
        ax.set_xlabel(f"openEMS simulated [{unit}]")
        ax.set_ylabel(f"surrogate predicted [{unit}]")
        ax.grid(alpha=0.3)
    fig.suptitle("Module 2 - numerical surrogate, locked test split (n = %d designs)" % len(parts["test"]), fontsize=10)
    fig.tight_layout()
    fig.savefig(p("results", "figures", "numerical_parity_patch.png"), dpi=200)
    plt.close(fig)

    # model comparison (test MAE relative to the mean baseline) + permutation importance
    fig, axs = plt.subplots(1, 2, figsize=(13, 3.8))
    names = ["mean_baseline", "ridge", "hist_gbr", "random_forest"]
    cols = [GREY, "#9cc3e6", BLUE, NAVY]
    w = 0.2
    for j, n in enumerate(names):
        rel = [out[t]["models"][n]["test"]["MAE"] / out[t]["models"]["mean_baseline"]["test"]["MAE"] for t in PATCH_Y]
        axs[0].bar(np.arange(4) + (j - 1.5) * w, rel, w, color=cols[j], label=n.replace("_", " "))
    axs[0].set_xticks(range(4), list(PATCH_Y), fontsize=8)
    axs[0].set_ylabel("test MAE / mean-baseline MAE")
    axs[0].set_title("Surrogate candidates (lower is better)", fontsize=9)
    axs[0].legend(fontsize=7)
    axs[0].grid(axis="y", alpha=0.3)
    imp = pd.DataFrame({t: out[t]["permutation_importance_val_MAE"] for t in PATCH_Y})
    imp = imp / imp.sum()
    imp.T.plot(kind="barh", stacked=True, ax=axs[1], color=[NAVY, BLUE, "#9cc3e6", ACCENT, GREY], width=0.6)
    axs[1].set_xlabel("share of permutation importance (validation MAE)")
    axs[1].set_title("Which design parameters drive each prediction", fontsize=9)
    axs[1].legend(fontsize=7, loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)
    fig.tight_layout()
    fig.savefig(p("results", "figures", "surrogate_comparison_importance.png"), dpi=200)
    plt.close(fig)

    # engineering summaries for a few test designs (values come only from data / surrogate)
    sample = parts["test"].sample(4, random_state=cfg["seed"])
    lines = ["# Engineering summaries (auto-generated from surrogate predictions)", "",
             "Values labelled *predicted* come from the Module 2 surrogate; values labelled *simulated* are the "
             "openEMS reference from the dataset. The text generator only verbalises computed numbers; it never invents values.", "",
             "## Locked test-split designs", ""]
    for _, r in sample.iterrows():
        x = r[PATCH_X].to_frame().T.astype(float)
        pr = {t: float(best_models[t].predict(x)[0]) for t in PATCH_Y}
        lines += [engineering_summary(r, pr, cfg), ""]
    p("results", "reports", "engineering_summaries.md").write_text("\n".join(lines), encoding="utf-8")
    return out


def mendeley_regression(cfg: dict) -> dict:
    x = pd.read_csv(ROOT / "data" / "processed" / "mendeley_clean.csv")
    feats = MENDELEY_GEOM + ["Freq_GHz"]
    res = {}
    oof = {}
    for target in MENDELEY_Y:
        rows = x if target == "S11_dB" else x[x.plausible].reset_index(drop=True)
        gkf = GroupKFold(n_splits=cfg["surrogate"]["mendeley_folds"])
        res[target] = {"n_rows": int(len(rows)), "n_designs": int(rows.design_id.nunique())}
        for name, mdl in candidates(cfg).items():
            yh = np.zeros(len(rows))
            for tr, te in gkf.split(rows, groups=rows.design_id):
                mdl.fit(rows.iloc[tr][feats], rows.iloc[tr][target])
                yh[te] = mdl.predict(rows.iloc[te][feats])
            res[target][name] = reg_metrics(rows[target], yh)
            if name == "random_forest":
                oof[target] = (rows[target].to_numpy(), yh)
        # frequency-only control: how much do the geometry variables add?
        yh = np.zeros(len(rows))
        rf = RandomForestRegressor(n_estimators=cfg["surrogate"]["random_forest_trees"], random_state=cfg["seed"], n_jobs=-1)
        for tr, te in gkf.split(rows, groups=rows.design_id):
            rf.fit(rows.iloc[tr][["Freq_GHz"]], rows.iloc[tr][target])
            yh[te] = rf.predict(rows.iloc[te][["Freq_GHz"]])
        res[target]["random_forest_frequency_only"] = reg_metrics(rows[target], yh)
        print(f"[mendeley] {target}: RF MAE={res[target]['random_forest']['MAE']:.3f} "
              f"vs freq-only {res[target]['random_forest_frequency_only']['MAE']:.3f}")

    fig, axs = plt.subplots(1, 3, figsize=(12, 3.7))
    for ax, (t, unit) in zip(axs, MENDELEY_Y.items()):
        y, yh = oof[t]
        ax.scatter(y, yh, s=7, alpha=0.5, color="#1f4e79")
        lo, hi = min(y.min(), yh.min()), max(y.max(), yh.max())
        ax.plot([lo, hi], [lo, hi], "--", color="#c0504d", lw=1)
        m = res[t]["random_forest"]
        ax.set_title(f"{t}  (R² = {m['R2']:.2f}, MAE = {m['MAE']:.2f} {unit})", fontsize=9)
        ax.set_xlabel(f"simulated [{unit}]")
        ax.set_ylabel(f"predicted (out-of-fold) [{unit}]")
        ax.grid(alpha=0.3)
    fig.suptitle("Module 2 - Mendeley dual-slot patch, random forest, 5-fold GroupKFold by design", fontsize=10)
    fig.tight_layout()
    fig.savefig(p("results", "figures", "numerical_parity_mendeley.png"), dpi=200)
    plt.close(fig)
    return res


def main():
    cfg = load_config()
    out = {"patch": patch_regression(cfg), "mendeley": mendeley_regression(cfg)}
    save_json(out, p("results", "metrics", "numerical_module.json"))


if __name__ == "__main__":
    main()
