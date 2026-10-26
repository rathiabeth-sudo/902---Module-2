"""Multimodal fusion and surrogate-based multi-objective optimisation.

Fusion: 384-d ViT image embeddings exported by Module 1 (pre-registered fine-tuned ViT-S/16, seed 42)
are concatenated with the standardised numerical design features and classified by an MLP. The
fused model is compared with image-only and numeric-only MLPs on the same locked split (matching
class). Hidden size and L2 penalty are chosen on validation macro-F1; the test split is scored once.

Optimisation (SURROGATE ONLY): NSGA-II (pymoo) over (L, W/L, feed ratio) using the Module 2
random-forest surrogates, bounded by the observed training ranges. Constraint: predicted first
matched resonance inside 5G NR band n78 (3.3-3.8 GHz). Objectives: minimise predicted S11 at
resonance, maximise predicted -10 dB bandwidth, minimise patch area. Proposals are NOT simulated;
each is reported with its nearest simulated design for context.

Usage:  python -m src.fusion_optimization      (run src.numerical_model first)
"""
from __future__ import annotations

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler

from .metrics import classification_metrics
from .numerical_model import band_text, match_text
from .utils import ROOT, load_config, p, save_json

NUM = ["length_mm", "width_mm", "feed_y_mm", "wl_ratio", "feed_ratio"]


def fusion(cfg):
    fc = cfg["fusion"]
    run = fc["embedding_run"]
    print("fusion uses Module 1 embeddings from", run)
    df = pd.read_csv(ROOT / "data" / "processed" / "patch_designs.csv")
    names = cfg["labels"]["perf_names"]
    splits = ["train", "val", "test", "ood"]
    parts = {s: df[df.split == s].reset_index(drop=True) for s in splits}
    emb = {s: np.load(ROOT / fc["embedding_dir"] / f"{run}_{s}.npy") for s in splits}
    for s in splits:
        if len(emb[s]) != len(parts[s]):
            raise RuntimeError(f"embedding rows ({len(emb[s])}) != designs ({len(parts[s])}) for split {s}")
    y = {s: parts[s].perf_class.to_numpy() for s in splits}
    sc_n = StandardScaler().fit(parts["train"][NUM])   # statistics from the training split only
    sc_e = StandardScaler().fit(emb["train"])
    X = {
        "numeric_only": {s: sc_n.transform(parts[s][NUM]) for s in splits},
        "image_only": {s: sc_e.transform(emb[s]) for s in splits},
        "fusion_concat": {s: np.hstack([sc_e.transform(emb[s]), sc_n.transform(parts[s][NUM])]) for s in splits},
    }
    out = {}
    for variant, feats in X.items():
        best = (-1, None, None)
        for hidden in fc["hidden_grid"]:
            for alpha in fc["alpha_grid"]:
                clf = MLPClassifier(tuple(hidden), alpha=alpha, max_iter=800, early_stopping=False, random_state=cfg["seed"])
                clf.fit(feats["train"], y["train"])
                f1 = f1_score(y["val"], clf.predict(feats["val"]), average="macro")
                if f1 > best[0]:
                    best = (f1, (hidden, alpha), clf)
        clf = best[2]
        out[variant] = {"selected": {"hidden": best[1][0], "alpha": best[1][1]}, "val_macro_f1": best[0],
                        "n_features": int(feats["train"].shape[1]),
                        "test": classification_metrics(y["test"], clf.predict_proba(feats["test"]), names),
                        "ood": classification_metrics(y["ood"], clf.predict_proba(feats["ood"]), names)}
        print(f"[fusion] {variant}: val={best[0]:.3f} test macroF1={out[variant]['test']['macro_f1']:.3f} "
              f"ood={out[variant]['ood']['macro_f1']:.3f}")
    out["_embedding_run"] = run

    fig, axs = plt.subplots(1, 3, figsize=(10.8, 3.5))
    for ax, v in zip(axs, ["numeric_only", "image_only", "fusion_concat"]):
        cm = np.array(out[v]["test"]["confusion_matrix"])
        cmn = cm / cm.sum(1, keepdims=True)
        ax.imshow(cmn, cmap="Blues", vmin=0, vmax=1)
        for i in range(3):
            for j in range(3):
                ax.text(j, i, f"{cm[i, j]}\n{cmn[i, j]:.0%}", ha="center", va="center", fontsize=8,
                        color="white" if cmn[i, j] > 0.55 else "black")
        ax.set_xticks(range(3), names, fontsize=8)
        ax.set_yticks(range(3), names, fontsize=8)
        ax.set_xlabel("predicted")
        ax.set_ylabel("true")
        ax.set_title(f"{v.replace('_', ' ')}\ntest macro-F1 {out[v]['test']['macro_f1']:.3f}", fontsize=9)
    fig.tight_layout()
    fig.savefig(p("results", "figures", "fusion_confusion.png"), dpi=200)
    plt.close(fig)
    save_json(out, p("results", "metrics", "fusion.json"))
    return out


def optimise(cfg):
    from pymoo.algorithms.moo.nsga2 import NSGA2
    from pymoo.core.problem import Problem
    from pymoo.optimize import minimize

    oc = cfg["nsga2"]
    bundle = joblib.load(p(cfg["paths"]["checkpoints"], "patch_surrogates.joblib"))
    mods = bundle["models"]
    df = pd.read_csv(ROOT / "data" / "processed" / "patch_designs.csv")
    train = df[df.split == "train"]
    lo_band, hi_band = oc["band_ghz"]

    def featurise(Xv):
        # decision variables: L [mm], W/L ratio, feed ratio (0 = centre, 1 = edge); bounds = observed training ranges
        L, r, fr = Xv[:, 0], Xv[:, 1], Xv[:, 2]
        return pd.DataFrame({"length_mm": L, "width_mm": L * r, "feed_y_mm": -fr * L / 2, "wl_ratio": r, "feed_ratio": fr})

    class PatchProblem(Problem):
        def __init__(self):
            super().__init__(n_var=3, n_obj=3, n_ieq_constr=2,
                             xl=np.array([train.length_mm.min(), train.wl_ratio.min(), train.feed_ratio.min()]),
                             xu=np.array([train.length_mm.max(), train.wl_ratio.max(), train.feed_ratio.max()]))

        def _evaluate(self, Xv, out, *a, **k):
            F = featurise(Xv)
            fr = mods["f_res_ghz"].predict(F)
            s11 = mods["s11_at_res_db"].predict(F)
            bw = mods["bw10_mhz"].predict(F)
            area = F.length_mm * F.width_mm
            out["F"] = np.column_stack([s11, -bw, area])
            out["G"] = np.column_stack([lo_band - fr, fr - hi_band])

    res = minimize(PatchProblem(), NSGA2(pop_size=oc["pop_size"]), ("n_gen", oc["generations"]), seed=cfg["seed"], verbose=False)
    if res.X is None:
        print("no feasible solution found")
        return {}
    F = featurise(np.atleast_2d(res.X))
    F["pred_f_res_ghz"] = mods["f_res_ghz"].predict(F[bundle["features"]])
    F["pred_s11_at_res_db"] = mods["s11_at_res_db"].predict(F[bundle["features"]])
    F["pred_s11_min_db"] = mods["s11_min_db"].predict(F[bundle["features"]])
    F["pred_bw10_mhz"] = mods["bw10_mhz"].predict(F[bundle["features"]])
    F["area_mm2"] = F.length_mm * F.width_mm
    # nearest simulated design (standardised parameter space) as a support / plausibility check
    sc = StandardScaler().fit(df[["length_mm", "width_mm", "feed_y_mm"]])
    A = sc.transform(df[["length_mm", "width_mm", "feed_y_mm"]])
    B = sc.transform(F[["length_mm", "width_mm", "feed_y_mm"]])
    d = ((B[:, None, :] - A[None, :, :]) ** 2).sum(-1) ** 0.5
    j = d.argmin(1)
    F["nearest_sim_design"] = df.design_id.to_numpy()[j]
    F["nearest_distance_std"] = d.min(1)
    for c in ["f_res_ghz", "s11_at_res_db", "bw10_mhz"]:
        F[f"nearest_sim_{c}"] = df[c].to_numpy()[j]
    F["status"] = "surrogate proposal - NOT simulated, requires full-wave verification"
    F = F.sort_values("area_mm2").reset_index(drop=True)
    F.insert(0, "proposal_id", [f"N78-{i + 1:03d}" for i in range(len(F))])
    F.to_csv(p("results", "metrics", "nsga2_pareto_n78.csv"), index=False)

    sim = df[(df.f_res_ghz >= lo_band) & (df.f_res_ghz <= hi_band)]
    fig, ax = plt.subplots(figsize=(6.4, 4.3))
    ax.scatter(sim.area_mm2, sim.bw10_mhz, s=14, c="#b0b7c3", label=f"simulated designs in n78 (n={len(sim)})")
    s = ax.scatter(F.area_mm2, F.pred_bw10_mhz, c=F.pred_s11_at_res_db, cmap="viridis_r", s=34, edgecolor="k", lw=0.4,
                   label=f"NSGA-II surrogate proposals (n={len(F)})")
    plt.colorbar(s, ax=ax, label="predicted S11 at resonance [dB]")
    ax.set_xlabel("patch area [mm²]")
    ax.set_ylabel("-10 dB bandwidth [MHz]")
    ax.set_title(f"Surrogate Pareto set for 5G NR n78 ({lo_band}-{hi_band} GHz)\nproposals are predictions, not simulations", fontsize=10)
    ax.legend(fontsize=8, loc="upper right")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(p("results", "figures", "nsga2_pareto_n78.png"), dpi=200)
    plt.close(fig)

    # text summaries for three representative proposals: smallest area, widest bandwidth, deepest match
    picks = {"smallest area": F.area_mm2.idxmin(), "widest predicted bandwidth": F.pred_bw10_mhz.idxmax(),
             "deepest predicted match": F.pred_s11_at_res_db.idxmin()}
    lines = ["", "## NSGA-II surrogate proposals for 5G NR n78 (not simulated)", ""]
    for why, i in picks.items():
        r = F.loc[i]
        lines += [f"**{r.proposal_id}** ({why}) - patch L x W = {r.length_mm:.2f} x {r.width_mm:.2f} mm "
                  f"(area {r.area_mm2:.0f} mm², W/L {r.wl_ratio:.2f}), feed offset {r.feed_y_mm:.2f} mm. Predicted first matched "
                  f"resonance {r.pred_f_res_ghz:.2f} GHz, {band_text(r.pred_f_res_ghz, cfg)}; predicted S11 at resonance "
                  f"{r.pred_s11_at_res_db:.1f} dB, which {match_text(r.pred_s11_at_res_db, cfg)}; predicted -10 dB bandwidth "
                  f"{r.pred_bw10_mhz:.0f} MHz. Nearest simulated design {r.nearest_sim_design} ({r.nearest_distance_std:.2f} standard "
                  f"units away) resonates at {r.nearest_sim_f_res_ghz:.2f} GHz with {r.nearest_sim_s11_at_res_db:.1f} dB and "
                  f"{r.nearest_sim_bw10_mhz:.0f} MHz. Status: surrogate proposal - NOT simulated; requires full-wave verification.", ""]
    rep = p("results", "reports", "engineering_summaries.md")
    base = rep.read_text(encoding="utf-8").split("\n## NSGA-II")[0].rstrip("\n") if rep.exists() else ""
    rep.write_text(base + "\n" + "\n".join(lines), encoding="utf-8")

    summary = {"n_pareto": len(F), "band_ghz": [lo_band, hi_band], "pop_size": oc["pop_size"], "generations": oc["generations"],
               "n_simulated_designs_in_band": int(len(sim)),
               "pareto_area_range_mm2": [float(F.area_mm2.min()), float(F.area_mm2.max())],
               "pareto_pred_bw_range_mhz": [float(F.pred_bw10_mhz.min()), float(F.pred_bw10_mhz.max())],
               "pareto_pred_s11_range_db": [float(F.pred_s11_at_res_db.min()), float(F.pred_s11_at_res_db.max())],
               "pareto_length_range_mm": [float(F.length_mm.min()), float(F.length_mm.max())],
               "median_nearest_distance_std": float(F.nearest_distance_std.median()),
               "best_simulated_in_band_bw_mhz": float(sim.bw10_mhz.max()) if len(sim) else None,
               "smallest_simulated_in_band_area_mm2": float(sim.area_mm2.min()) if len(sim) else None}
    print("[nsga2]", summary)
    return summary


def main():
    cfg = load_config()
    out = {"fusion": fusion(cfg), "optimisation": optimise(cfg)}
    save_json(out, p("results", "metrics", "fusion_optimisation.json"))


if __name__ == "__main__":
    main()
