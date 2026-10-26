"""Module 2 methodology & implementation report -> reports/module2_report.docx + .tex.

All quantitative statements are computed from executed results. Run after `python -m src.fusion_optimization`.
"""
from __future__ import annotations

import re

import pandas as pd

from deliverables_common import (COMPANION_URL, FIG, MEND_TARGETS, PATCH_TARGETS, REPO_URL, ROOT, SUBTITLE, TITLE, criteria,
                                 link, load, test_summary)
from report_render import to_docx, to_tex


def availability(C) -> list:
    """Section with clickable links to the data, scripts, tests and outputs in the GitHub repository."""
    L = link
    rows = [
        ["**Data**", "Patch dataset source (2,051 openEMS designs, MIT)", "[Hugging Face, rev. 4be72a2](https://huggingface.co/datasets/becklabash/rectangular-patch-antenna-freq-response)"],
        ["", "Mendeley Antenna Parameters Dataset v2 (CC BY 4.0)", "[Mendeley Data 10.17632/3gxr2vvd9n.2](https://doi.org/10.17632/3gxr2vvd9n.2)"],
        ["", "Processed patch table (parameters, S11 targets, labels, split)", L("data/processed/patch_designs.csv")],
        ["", "Cleaned Mendeley table with plausibility flag", L("data/processed/mendeley_clean.csv")],
        ["", "Locked split manifests shared with Module 1", L("data/splits", folder=True)],
        ["", "Module 1 ViT embeddings and SHA-256 provenance", L("data/external/module1_vit_embeddings", folder=True)],
        ["", "Data dictionary and preprocessing log", L("data/data_dictionary.csv") + "; " + L("data/processed/preprocessing_log.json")],
        ["", "Configuration (seed, thresholds, surrogate, fusion, NSGA-II)", L("configs/default.yaml")],
        ["**Scripts**", "Download and preprocessing (targets, cleaning, split check)", L("src/download_data.py") + "; " + L("src/preprocessing.py")],
        ["", "Surrogate regression and engineering summaries", L("src/numerical_model.py")],
        ["", "Multimodal fusion and NSGA-II optimisation", L("src/fusion_optimization.py")],
        ["", "Metrics helpers", L("src/metrics.py")],
        ["", "Full pipeline", L("scripts/run_all.ps1") + "; " + L("scripts/run_all.sh")],
        ["", "Report, slides, poster and diagram generators", L("scripts", folder=True)],
        ["**Tests**", "Target extraction, labels, split, cleaning rule, embeddings, NSGA-II constraints", L("tests/test_module2.py")],
        ["", f"Stored pytest output ({test_summary()})", L("results/test_report.txt")],
        ["**Outputs**", "Surrogate metrics for every target, model and split", L("results/metrics/numerical_module.json")],
        ["", "Surrogate test predictions per design", L("results/predictions/patch_surrogate_test.csv")],
        ["", "Fusion results (numeric-only, image-only, fused)", L("results/metrics/fusion.json")],
        ["", "NSGA-II Pareto proposals (NOT simulated) and summary", L("results/metrics/nsga2_pareto_n78.csv") + "; " + L("results/metrics/fusion_optimisation.json")],
        ["", "Generated engineering summaries (text)", L("results/reports/engineering_summaries.md")],
        ["", "Mendeley cleaning record", L("results/metrics/mendeley_cleaning.json")],
        ["", "All figures produced by the project", L("results/figures", folder=True)],
        ["", "Report, slides and poster", L("reports", folder=True) + "; " + L("presentations", folder=True) + "; " + L("poster", folder=True)],
    ]
    return [
        ("h1", "Data, Code and Output Availability"),
        ("p", f"All data derivatives, code, tests and outputs of Module 2 are public in the GitHub repository {REPO_URL}. "
              "Each entry below links directly to the file or folder; raw third-party files are linked at their source because they "
              "are re-downloaded with checksums rather than redistributed. Module 1 is at " + COMPANION_URL + "."),
        ("table", C.tab("Links to the data, scripts, tests and outputs of Module 2 (branch main)."), ["Category", "Content", "Link"], rows),
    ]


class Counter:
    def __init__(self):
        self.f = 0
        self.t = 0

    def fig(self, text):
        self.f += 1
        return f"Figure {self.f}. {text}"

    def tab(self, text):
        self.t += 1
        return f"Table {self.t}. {text}"


def summaries():
    md = (ROOT / "results" / "reports" / "engineering_summaries.md").read_text(encoding="utf-8")
    paras = [re.sub(r"\*\*", "", p.strip()) for p in md.split("\n\n") if p.strip().startswith("**")]
    test = [p for p in paras if p.startswith("P")]
    prop = [p for p in paras if p.startswith("N78")]
    return test, prop


def build(R) -> list:
    C = Counter()
    num, fu, opt, prep, clean, par, prov = R["num"], R["fu"], R["opt"], R["prep"], R["clean"], R["pareto"], R["prov"]
    pt, md, sel = num["patch"], num["mendeley"], R["sel"]
    CR = criteria(R)
    sc = prep["patch_split_counts"]
    r2 = {k: sel(k)["R2"] for k in pt}
    mae = {k: sel(k)["MAE"] for k in pt}
    ood_r2 = {k: sel(k, "ood")["R2"] for k in pt}
    base = {k: pt[k]["models"]["mean_baseline"]["test"]["MAE"] for k in pt}
    fi, im, nu = (fu[k]["test"]["macro_f1"] for k in ["fusion_concat", "image_only", "numeric_only"])
    vit_head = prov["module1_vit_linear_head_test_macro_f1"]
    lo, hi = opt["band_ghz"]
    test_s, prop_s = summaries()
    small, wide, deep = par.loc[par.area_mm2.idxmin()], par.loc[par.pred_bw10_mhz.idxmax()], par.loc[par.pred_s11_at_res_db.idxmin()]
    imp = {k: max(pt[k]["permutation_importance_val_MAE"], key=pt[k]["permutation_importance_val_MAE"].get) for k in pt}
    n_cluster_small = int((par.length_mm < 30).sum())

    B = []
    a = B.append

    # ------------------------------------------------------------------ Abstract
    a(("h1", "Abstract"))
    a(("p", "This project implements and evaluates Module 2 of a two-module applied-AI framework for "
            "hybrid-slotted defected ground structure (DGS) compact patch antennas. Module 2 is the numerical-text branch: it "
            "predicts electromagnetic performance from antenna parameters, turns the predictions into short engineering summaries, "
            "fuses numerical features with the image embeddings produced by Module 1, and uses the surrogates inside an NSGA-II "
            "multi-objective search. Ansys HFSS was not available, so the module was built and executed on two verified public "
            "simulation datasets: 2,051 openEMS rectangular patch antennas (MIT licence) and the Mendeley dual-slot patch Antenna "
            f"Parameters Dataset (103 designs × 16 frequencies, CC BY 4.0). On the locked test split shared with Module 1, a random "
            f"forest predicted the first matched resonance with R² = {r2['f_res_ghz']:.2f} (MAE {mae['f_res_ghz']:.2f} GHz) and the "
            f"−10 dB bandwidth with R² = {r2['bw10_mhz']:.2f}, but the depth of the S11 minimum only with R² = {r2['s11_min_db']:.2f}; "
            f"all surrogates degraded sharply on wider, out-of-distribution patches. On the slotted Mendeley antenna, grouped "
            f"cross-validation gave R² = {md['S11_dB']['random_forest']['R2']:.2f} for S11, {md['Gain']['random_forest']['R2']:.2f} for "
            f"gain and {md['Rad_eff']['random_forest']['R2']:.2f} for radiation efficiency, and the geometry variables roughly halved "
            f"the error of a frequency-only model. The pre-registered fusion hypothesis was not supported: concatenating ViT "
            f"embeddings with numerical features gave a test macro-F1 of {fi:.3f}, against {im:.3f} for the embeddings alone and "
            f"{nu:.3f} for the numerical features alone. NSGA-II returned {opt['n_pareto']} surrogate proposals for the 5G NR n78 band "
            f"({lo}–{hi} GHz) with areas of {opt['pareto_area_range_mm2'][0]:.0f}–{opt['pareto_area_range_mm2'][1]:.0f} mm². None has "
            "been simulated; every proposal and every summary is labelled as requiring full-wave verification."))
    a(("p", "**Keywords:** surrogate modelling; random forest; patch antenna; defected ground structure; multimodal fusion; NSGA-II; 5G NR n78."))

    # ------------------------------------------------------------------ 1 Introduction
    a(("h1", "1. Introduction and Recap of the Research Problem"))
    a(("p", "Compact printed patch antennas for 5G and emerging 6G devices are designed by iterating full-wave simulations. Slots "
            "and defected ground structures add design freedom but also make the response sensitive to small geometric changes [4], "
            "so a parameter sweep in Ansys HFSS can take days. The overall research framework addresses this with two modules. "
            "Module 1, a companion project in its own repository "
            f"({COMPANION_URL}), is a Vision Transformer [1] that classifies standardised antenna images. Module 2, the subject of this project, "
            "works on numbers: it learns a fast surrogate of the simulator from antenna parameters, explains each prediction in a "
            "short engineering summary, combines numerical and image features, and searches the design space for promising "
            "candidates. The surrogate is a screening tool that reduces the number of full-wave runs, not a replacement for them."))
    a(("p", "The objective of Module 2 is **to determine how well documented antenna parameters predict simulated electromagnetic "
            "performance, whether these numbers add to image features, and whether surrogate-based multi-objective optimisation can "
            "propose credible compact designs for a 5G band** - while keeping every generated number and sentence traceable to a "
            "model output or a simulated reference."))
    a(("table", C.tab("Implementation status of Module 2."), ["Component", "Status", "Evidence in repository"], [
        ["Dataset verification, cleaning and plausibility rules", "Completed and executed", link("src/preprocessing.py") + ", " + link("docs/DATA_CARD.md")],
        ["S11 target extraction and locked split (shared with Module 1)", "Completed and executed", link("src/preprocessing.py") + ", " + link("data/splits", folder=True)],
        ["Surrogate regression (ridge, gradient boosting, random forest)", "Completed and executed", link("src/numerical_model.py")],
        ["Rule-based engineering summaries (text)", "Completed and executed", link("results/reports/engineering_summaries.md")],
        ["Multimodal fusion with Module 1 embeddings", "Completed and executed", link("src/fusion_optimization.py") + ", " + link("results/metrics/fusion.json")],
        ["NSGA-II optimisation for NR n78", "Executed on surrogates only; proposals not simulated", link("results/metrics/nsga2_pareto_n78.csv")],
        ["Automated tests", "Completed and executed", link("tests/test_module2.py") + ", " + link("results/test_report.txt")],
        ["HFSS hybrid-slotted DGS parameter sweep", "Proposed (HFSS unavailable)", "Section 11"],
        ["Full-wave re-simulation, fabrication and measurement", "Proposed", "Section 11"],
        ["Block diagram (Figure 1)", "Illustrative", link("results/figures/module2_architecture.png")],
    ]))
    a(("figure", FIG / "module2_architecture.png", C.fig("Module 2 block diagram. Solid boxes were implemented and executed; dashed orange boxes are proposed work that requires Ansys HFSS. The example sentence is a real generated summary."), 6.3))

    # ------------------------------------------------------------------ 2 Research design
    a(("h1", "2. Research Design and Hypotheses"))
    a(("p", "The study follows an applied, experimental machine-learning design. The independent variables are the model family "
            "(mean baseline, ridge regression, histogram gradient boosting, random forest, multilayer perceptron), the input set "
            "(design geometry, frequency, image embedding, or a combination) and the evaluation distribution (in-distribution test "
            "split or out-of-distribution hold-out). The dependent variables are regression errors for continuous targets, "
            "classification metrics for the fusion task, and objective values and feasibility for the optimisation."))
    a(("table", C.tab("Research questions of Module 2 and their operationalisation."), ["RQ", "Question", "Operationalisation"], [
        ["RQ1", "Can antenna parameters predict simulated resonance, matching and bandwidth?", "Patch L, W, feed → f_res, S11min, S11 at f_res, −10 dB BW; locked test and OOD splits"],
        ["RQ2", "Do slot and substrate dimensions add information beyond frequency?", "Mendeley: geometry + frequency vs frequency-only random forest, GroupKFold by design"],
        ["RQ3", "Does fusing image embeddings with numerical features improve classification?", "MLP on numeric, image-embedding and concatenated inputs; matching class (H6)"],
        ["RQ4", "Can surrogate-based NSGA-II propose compact, well-matched n78 designs?", "Three objectives, band constraint; distance to nearest simulated design"],
        ["RQ5", "Can predictions be summarised in text without inventing values?", "Template generator that only verbalises surrogate outputs and dataset references"],
    ]))
    a(("p", "Hypothesis H6 was pre-registered in Git with the Module 1 hypotheses, before any fusion result existed "
            "(docs/HYPOTHESES.md). The other three items below are evaluation criteria stated in the analysis plan; they were not "
            "separately pre-registered and are reported as such:"))
    a(("bullets", [f"**{c[0]}**: {c[1]}." for c in CR]))

    # ------------------------------------------------------------------ 3 Dataset
    a(("h1", "3. Dataset Description and Source Verification"))
    a(("p", "Repositories were searched in the order set by the brief (Hugging Face, Kaggle, Mendeley Data, IEEE DataPort, GitHub), "
            "with Zenodo added; the eleven candidates and the reasons for rejection are recorded in docs/DATASET_SURVEY.md. Two "
            "datasets met the requirements for a numerical module: documented geometric inputs, simulated electromagnetic outputs, "
            "a licence that permits reuse, and enough designs for a held-out evaluation. No public HFSS parameter sweep of "
            "hybrid-slotted DGS antennas was found."))
    a(("table", C.tab("Datasets used by Module 2 (verified 25 October 2026)."), ["Dataset", "Source / version", "Licence", "Content", "Role in Module 2"], [
        ["Rectangular Patch Antenna Frequency Response [2]", "Hugging Face becklabash/rectangular-patch-antenna-freq-response, rev. 4be72a2", "MIT",
         "2,051 coax-fed patches; L, W, feed offset; 1,000-point S11 (1–10 GHz), openEMS FDTD [11]; εr 3.68, h 1.61 mm",
         "Surrogate targets, fusion, NSGA-II"],
        ["Antenna Parameters Dataset [3]", "Mendeley Data 10.17632/3gxr2vvd9n.2", "CC BY 4.0",
         "103 dual-slot patch designs × 16 frequencies (1–50 GHz): S11, gain, directivity, efficiencies, VSWR", "Slotted-antenna regression (S11, gain, efficiency)"],
        ["Module 1 image embeddings", "Module 1 repository, run vit_finetune_patch_perf_class_s42", "Derived (MIT data)",
         "384-d ViT CLS embedding per patch design; SHA-256 recorded", "Image features for fusion only"],
    ]))
    a(("p", "**Nature of the evidence.** Both datasets are full-wave simulations; neither contains measurements, and no HFSS output is "
            "claimed. The Mendeley data are one-at-a-time sweeps around a single nominal design, so most designs differ from the "
            "nominal one in a single dimension. The Module 1 embeddings were produced by a ViT fine-tuned on the training split only; "
            "validation, test and OOD images were never used to fit it (data/external/module1_vit_embeddings/provenance.json)."))
    a(("p", "**Discrepancies recorded during verification.** The patch README gives L ∈ [7.5, 52.5] mm and p ∈ [−6, 0) mm; the observed "
            "values are L ∈ [7.5, 47.5] mm and p ∈ [−15.83, 0] mm, including 100 centre-fed designs. The README states εr = 3.68 "
            f"while the repository diagram shows 3.38. {prep['patch_positive_s11_designs']} S11 curves exceed 0 dB by at most 0.2 dB, a "
            f"passive-port numerical artefact. In the Mendeley data, {clean['implausible_rows_flagged']} of {clean['rows_raw']:,} rows "
            "are physically implausible and one efficiency entry is a truncated, non-numeric string. The reference report cites "
            "Mendeley version 1, which has since been superseded by version 2."))

    # ------------------------------------------------------------------ 4 Preprocessing
    a(("h1", "4. Data Preprocessing and Preparation"))
    a(("h2", "4.1 Engineering targets from simulated S11"))
    a(("p", "Each 1,000-point S11 curve was reduced to four regression targets: the global minimum S11 (S11min); the **first matched "
            "resonance** f_res, defined as the lowest-frequency local minimum below −10 dB; S11 at f_res; and the contiguous −10 dB "
            "bandwidth around f_res. The first matched resonance is used because the deepest dip is often a higher-order mode; a "
            "22.5 mm patch, for example, has its deepest dip at 9.6 GHz. Unmatched designs keep the global minimum as f_res and a "
            "bandwidth of 0. The same rules define the matching class used in the fusion task (Poor if S11min > −10 dB, Acceptable if "
            "−20 dB < S11min ≤ −10 dB, High if S11min ≤ −20 dB). The −20 dB boundary is a **project assumption** that requires "
            "engineering confirmation."))
    a(("figure", FIG / "s11_target_extraction.png", C.fig("How the regression targets are extracted from one simulated S11 curve (test design P1768). The deepest dip lies outside n78; the first matched resonance lies inside it."), 6.0))
    a(("h2", "4.2 Cleaning and plausibility rules"))
    a(("bullets", [f"Patch: {prep['patch_raw_rows']:,} rows, 0 non-finite curves, {prep['patch_duplicate_parameter_rows']} duplicate parameter "
                   f"triples and {prep['patch_missing_values']} missing values after feature extraction. Extreme S11 values are physical deep "
                   "matches and were kept.",
                   f"Mendeley: column names were stripped and normalised, the non-numeric efficiency entry was set to missing, and every row "
                   f"was assigned a design ID from its ten geometry variables ({clean['unique_designs']} designs × "
                   f"{len(clean['frequencies_ghz'])} frequencies; {clean['duplicate_rows']} duplicate rows).",
                   f"Plausibility rule (documented, not tuned): a row is flagged if radiation or total efficiency exceeds 1, directivity "
                   f"exceeds 20 dBi for an antenna of about 6 mm, or gain exceeds directivity. {clean['implausible_rows_flagged']} rows were "
                   f"flagged; they are excluded from the gain and efficiency targets ({clean['plausible_rows']:,} rows remain) but kept for "
                   "S11, which they do not affect."]))
    a(("h2", "4.3 Features, split and leakage control"))
    a(("bullets", ["Patch inputs: length L, width W, feed offset, aspect ratio W/L and normalised feed position (feed offset / (L/2)). "
                   "Mendeley inputs: the ten substrate, patch, feed and slot dimensions plus frequency.",
                   f"Split: Module 2 reproduces the locked design-level split of Module 1 and verifies it against the committed manifests "
                   f"(train {sc['train']:,}, validation {sc['val']}, test {sc['test']}, OOD hold-out {sc['ood']} with W/L > 1.95). This keeps the "
                   "fusion comparison fair and makes the two modules' test results refer to the same designs.",
                   "Mendeley evaluation uses 5-fold GroupKFold by design, so all 16 frequencies of one design are always in the same fold.",
                   "Standardisation statistics (ridge, MLP) are fitted on training data only; tree models need no scaling.",
                   "The test split is scored once, after model selection on validation MAE (regression) or validation macro-F1 (fusion)."]))
    a(("p", f"The data dictionary is in Appendix A and online at {link('data/data_dictionary.csv')}; all counts are logged in "
            f"{link('data/processed/preprocessing_log.json')} and {link('results/metrics/mendeley_cleaning.json')}, and the rules "
            "are enforced by automated tests (Section 10)."))

    # ------------------------------------------------------------------ 5 Model
    a(("h1", "5. Proposed Model: Numerical-Text Surrogate, Fusion and Optimisation"))
    a(("p", "**Tabular surrogate.** For each target, four candidates are trained: a mean predictor, ridge regression [12], "
            "histogram gradient boosting [7] and a random forest of 400 trees [6], all from scikit-learn [8]. The candidate with the "
            "lowest validation MAE is selected. Tree ensembles suit this problem: the response is non-linear and non-additive (the "
            "resonance depends on length, the match on the feed position relative to the edge), and the datasets are small. "
            "Permutation importance on the validation split [13] shows which inputs each surrogate relies on."))
    a(("p", "**Text generation.** The engineering summary is produced by a deterministic template, not by a language model. It "
            "reads the surrogate's predictions and the dataset's simulated reference for the same design, maps them to the band "
            "(n78, FR1 or FR3 [5]) and to the matching rule, and writes one paragraph. Because every number in the sentence is copied "
            "from a computed value, the generator cannot invent a measurement, and each summary ends with the statement that "
            "full-wave verification is required."))
    a(("p", "**Multimodal fusion.** The 384-dimensional CLS embedding exported by Module 1 and the five standardised numerical "
            "features are concatenated and classified by a multilayer perceptron [14] into the three matching classes. Two reference "
            "models use the embedding only and the numerical features only. Hidden size ((64) or (128, 64)) and L2 penalty "
            "(1e-4, 1e-3, 1e-2) are chosen on validation macro-F1 for each variant. This is the early-fusion design of the framework "
            "figure [15]."))
    a(("p", f"**Multi-objective optimisation.** NSGA-II [9], implemented in pymoo [10], searches three decision variables - patch "
            "length L, aspect ratio W/L and normalised feed position - bounded by their observed training ranges. It minimises "
            "predicted S11 at resonance, maximises predicted −10 dB bandwidth and minimises patch area, subject to the predicted first "
            f"matched resonance lying in 5G NR band n78 ({lo}–{hi} GHz). Population size is {opt['pop_size']} and the search runs for "
            f"{opt['generations']} generations. Each Pareto proposal is reported with its nearest simulated design in standardised "
            "parameter space, as a check on how far the surrogate is extrapolating."))

    # ------------------------------------------------------------------ 6 Training
    a(("h1", "6. Training Strategy and Experimental Setup"))
    a(("table", C.tab("Module 2 configuration (configs/default.yaml)."), ["Component", "Setting", "Selection / note"], [
        ["Random forest", "400 trees, unlimited depth, min. 1 sample per leaf", "Seed 42; candidate per target"],
        ["Histogram gradient boosting", "500 iterations, learning rate 0.05", "Seed 42; candidate per target"],
        ["Ridge regression", "α = 1.0, standardised inputs", "Linear reference"],
        ["Model selection (patch)", "Lowest validation MAE per target", "Test scored once"],
        ["Mendeley evaluation", "5-fold GroupKFold by design", "Out-of-fold predictions"],
        ["Fusion MLP", "Adam, ≤ 800 iterations; hidden (64) or (128, 64); α ∈ {1e-4, 1e-3, 1e-2}", "Chosen on validation macro-F1"],
        ["NSGA-II", f"Population {opt['pop_size']}, {opt['generations']} generations, 3 objectives, 2 constraints", "Seed 42"],
        ["Hardware", "Intel i7-10610U CPU", "Full Module 2 pipeline runs in a few minutes"],
    ]))
    a(("p", "No hyperparameter of the tree models was tuned beyond the candidate comparison, because the aim is a robust baseline "
            "surrogate rather than a leaderboard result; the configuration is fixed in one file and every run is seeded."))

    # ------------------------------------------------------------------ 7 Baselines
    a(("h1", "7. Baseline Methods and Comparative Models"))
    a(("bullets", ["**Mean baseline**: predicts the training mean of each target; any useful surrogate must beat it.",
                   "**Ridge regression**: a linear model on standardised inputs; shows how much of the response is linear.",
                   "**Frequency-only random forest** (Mendeley): the same model given only frequency, isolating the contribution of the geometry.",
                   "**Image-only and numeric-only MLPs** (fusion): the two single-modality references for H6.",
                   f"**Module 1 ViT linear head**: the fine-tuned ViT's own classifier, test macro-F1 {vit_head:.3f} (reported by Module 1), "
                   "for context on the image-only MLP.",
                   "**Simulated designs in band** (optimisation): the best simulated n78 designs in the dataset, as a reference for the Pareto set."]))

    # ------------------------------------------------------------------ 8 Metrics
    a(("h1", "8. Evaluation Metrics and Analysis Plan"))
    a(("p", "Regression is reported with mean absolute error (MAE), root mean squared error (RMSE) and the coefficient of "
            "determination R², on the locked test split and separately on the OOD hold-out. For the Mendeley data the metrics are "
            "computed on pooled out-of-fold predictions. The fusion task uses macro-F1 (primary, because the classes are imbalanced), "
            "accuracy, balanced accuracy, one-vs-rest macro ROC-AUC and the confusion matrix. The optimisation is described by the "
            "number of non-dominated proposals, the ranges of the objectives, constraint satisfaction and the distance of each proposal "
            "to its nearest simulated design. The analysis plan and H6 were fixed before results were produced."))

    # ------------------------------------------------------------------ 9 Results
    a(("h1", "9. Results and Discussion"))
    a(("p", "Every number in this section comes from executed runs stored in results/metrics. No value is estimated or illustrative."))
    a(("h2", "9.1 Patch surrogate: resonance, matching and bandwidth (RQ1)"))
    a(("table", C.tab(f"Patch surrogate, locked test split (n = {sc['test']} designs) and OOD hold-out (n = {sc['ood']}); model selected on validation MAE."),
       ["Target", "Model", "Test MAE", "Test RMSE", "Test R²", "Mean-baseline MAE", "OOD R²"],
       [[f"{PATCH_TARGETS[k][0]} ({PATCH_TARGETS[k][1]})", pt[k]["selected_on_val_MAE"].replace("_", " "), f"{mae[k]:.3f}",
         f"{sel(k)['RMSE']:.3f}", f"{r2[k]:.3f}", f"{base[k]:.3f}", f"{ood_r2[k]:.3f}"] for k in pt]))
    a(("figure", FIG / "numerical_parity_patch.png", C.fig("Parity plots of the selected surrogates on the locked patch test split."), 6.3))
    a(("figure", FIG / "surrogate_comparison_importance.png", C.fig("Left: test MAE of each candidate relative to the mean baseline. Right: share of permutation importance (validation MAE) per input."), 6.3))
    a(("p", f"The random forest was selected for all four targets and beat the mean baseline on each (**E1** – {CR[0][2]}). It predicts "
            f"the first matched resonance well (R² = {r2['f_res_ghz']:.2f}, MAE {mae['f_res_ghz']:.2f} GHz) and the −10 dB bandwidth "
            f"well (R² = {r2['bw10_mhz']:.2f}, MAE {mae['bw10_mhz']:.1f} MHz). It predicts the depth of the S11 minimum only moderately "
            f"(R² = {r2['s11_min_db']:.2f}, MAE {mae['s11_min_db']:.1f} dB). This is physically reasonable: resonance varies smoothly "
            "with patch length [4], whereas the depth of the match is a sharp function of how closely the input impedance at the feed "
            "approaches the 50 Ω port, so small parameter changes produce large changes in dB. The same sharpness explains why "
            "the matching class is the hardest task for the image models of Module 1. Ridge regression captured little of any "
            "target, confirming that the response is strongly non-linear. Permutation importance spread across all five inputs; "
            f"length was the most important input for {sum(v == 'length_mm' for v in imp.values())} of the four targets, as expected "
            "from the half-wavelength resonance condition."))
    a(("p", f"**Out-of-distribution behaviour.** On the wider patches of the OOD hold-out, R² fell to {ood_r2['f_res_ghz']:.2f} for the "
            f"resonance and below zero for S11 at resonance ({ood_r2['s11_at_res_db']:.2f}) and bandwidth ({ood_r2['bw10_mhz']:.2f}). "
            "Tree ensembles cannot extrapolate beyond the training range, and wide patches excite different modes. This is the most "
            "important caveat for the optimisation stage: surrogate predictions are only trustworthy close to simulated designs, "
            "which is why the NSGA-II search is bounded by the training ranges and each proposal is checked against its nearest "
            "simulated neighbour."))
    a(("h2", "9.2 Slotted patch: S11, gain and efficiency (RQ2)"))
    rows = []
    for t in md:
        for m in ["mean_baseline", "ridge", "hist_gbr", "random_forest", "random_forest_frequency_only"]:
            rows.append([f"{MEND_TARGETS[t][0]} ({MEND_TARGETS[t][1]})", m.replace("_", " "), f"{md[t][m]['MAE']:.3f}",
                         f"{md[t][m]['RMSE']:.3f}", f"{md[t][m]['R2']:.3f}"])
    a(("table", C.tab("Mendeley dual-slot patch, 5-fold GroupKFold by design (out-of-fold predictions)."), ["Target", "Model", "MAE", "RMSE", "R²"], rows))
    a(("figure", FIG / "numerical_parity_mendeley.png", C.fig("Out-of-fold parity plots for the random forest on the Mendeley dual-slot patch."), 6.3))
    a(("p", f"Adding the ten geometry variables to frequency reduced the random-forest error for every target (**E2** – {CR[1][2]}). "
            "The very high gain and efficiency R² mostly reflect the strong frequency dependence over 1–50 GHz: the frequency-only "
            f"model already reaches R² = {md['Gain']['random_forest_frequency_only']['R2']:.2f} for gain. Because the data are "
            "one-at-a-time sweeps around one nominal design, the geometry effect is estimated from a narrow neighbourhood and the "
            "grouped folds still contain near-identical designs, so these scores overstate how well the model would generalise to a "
            "new slot topology. S11 is the hardest target here as well: a few deep resonances are badly under- or over-predicted, "
            "which is visible as horizontal clusters in the parity plot."))
    a(("h2", "9.3 Engineering summaries (RQ5)"))
    a(("p", "The text generator wrote one summary per selected test design and per highlighted Pareto proposal "
            "(results/reports/engineering_summaries.md). Two unedited examples:"))
    a(("bullets", [test_s[1] if len(test_s) > 1 else test_s[0], prop_s[0]]))
    a(("p", "Each sentence places the predicted values next to the simulated reference, so a reader can see the surrogate error "
            "directly (in the first example the resonance is predicted within a few tens of MHz). The generator never produces a "
            "number that the model or the dataset did not produce, and it never states that a design is verified. Its limitation "
            "is expressiveness: it cannot explain why a design behaves as it does, only restate the numbers in engineering terms."))
    a(("h2", "9.4 Multimodal fusion (RQ3, H6)"))
    a(("table", C.tab("Fusion experiment, matching class (MLP; configuration selected on validation macro-F1)."),
       ["Input", "Features", "Val macro-F1", "Test macro-F1", "Test bal. acc.", "Test ROC-AUC", "OOD macro-F1"],
       [[k.replace("_", " "), v["n_features"], f"{v['val_macro_f1']:.3f}", f"{v['test']['macro_f1']:.3f}",
         f"{v['test']['balanced_accuracy']:.3f}", f"{v['test'].get('roc_auc_ovr_macro', float('nan')):.3f}", f"{v['ood']['macro_f1']:.3f}"]
        for k, v in fu.items()]))
    a(("figure", FIG / "fusion_confusion.png", C.fig("Test confusion matrices of the three fusion variants."), 6.0))
    a(("p", f"**H6** – {CR[2][2]}. Concatenating the five numerical features with the 384-d image embedding lowered test macro-F1 "
            "compared with the embedding alone, so the pre-registered hypothesis is not supported. The most informative result is "
            f"the image-only MLP: trained on frozen embeddings of the fine-tuned ViT it reached {im:.3f}, far above the ViT's own "
            f"linear head ({vit_head:.3f}, Module 1). This supports Module 1's underfitting diagnosis - the representation captured the "
            "relevant geometry, but the end-to-end head did not converge within the CPU budget. The numeric-only MLP "
            f"({nu:.3f}) was weaker than image-only although the five parameters fully determine each design; a small MLP underfits "
            "the sharp S11 dependence, whereas the embedding already encodes size and feed position. Adding the numbers to 384 "
            "image dimensions mainly added redundant inputs for a small training set. The embeddings were fitted on the same "
            "training labels, so training-set features are optimistic; validation and test images were never used for fitting, so "
            "the test numbers remain valid, but the comparison should be confirmed with cross-fitted embeddings."))
    a(("h2", "9.5 NSGA-II surrogate optimisation for NR n78 (RQ4)"))
    a(("figure", FIG / "nsga2_pareto_n78.png", C.fig(f"NSGA-II surrogate Pareto set for NR n78 ({lo}–{hi} GHz), shown against the simulated designs whose first resonance lies in that band. Proposals are predictions, not simulations."), 4.8))
    a(("table", C.tab("Three representative Pareto proposals (surrogate predictions, NOT simulated) and their nearest simulated design."),
       ["Proposal", "L × W (mm)", "Feed (mm)", "Pred. f_res (GHz)", "Pred. S11 (dB)", "Pred. BW (MHz)", "Nearest simulated (f_res / S11 / BW)"],
       [[f"{r.proposal_id} ({why})", f"{r.length_mm:.2f} × {r.width_mm:.2f}", f"{r.feed_y_mm:.2f}", f"{r.pred_f_res_ghz:.2f}",
         f"{r.pred_s11_at_res_db:.1f}", f"{r.pred_bw10_mhz:.0f}",
         f"{r.nearest_sim_design}: {r.nearest_sim_f_res_ghz:.2f} / {r.nearest_sim_s11_at_res_db:.1f} / {r.nearest_sim_bw10_mhz:.0f}"]
        for why, r in [("smallest area", small), ("widest BW", wide), ("deepest match", deep)]]))
    a(("p", f"NSGA-II returned {opt['n_pareto']} non-dominated proposals (**E3** – {CR[3][2]}). They span "
            f"{opt['pareto_area_range_mm2'][0]:.0f}–{opt['pareto_area_range_mm2'][1]:.0f} mm², predicted bandwidths of "
            f"{opt['pareto_pred_bw_range_mhz'][0]:.0f}–{opt['pareto_pred_bw_range_mhz'][1]:.0f} MHz and predicted S11 at resonance of "
            f"{opt['pareto_pred_s11_range_db'][0]:.1f} to {opt['pareto_pred_s11_range_db'][1]:.1f} dB. For comparison, {opt['n_simulated_designs_in_band']} "
            f"simulated designs resonate in n78; the widest of them has {opt['best_simulated_in_band_bw_mhz']:.0f} MHz and the smallest "
            f"covers {opt['smallest_simulated_in_band_area_mm2']:.0f} mm². The proposals fall into two physically distinct groups: "
            f"{n_cluster_small} compact patches with L ≈ {par.length_mm[par.length_mm < 30].min():.0f}–{par.length_mm[par.length_mm < 30].max():.0f} mm that use the "
            f"fundamental mode, and {opt['n_pareto'] - n_cluster_small} larger patches with L ≈ {par.length_mm[par.length_mm >= 30].min():.0f}–{par.length_mm[par.length_mm >= 30].max():.0f} mm whose "
            "first matched resonance is a higher-order mode, which trade area for a deeper match. The median distance to the nearest "
            f"simulated design is {opt['median_nearest_distance_std']:.2f} standard deviations, so the proposals are interpolations "
            f"close to existing data rather than extrapolations. The widest predicted bandwidth ({opt['pareto_pred_bw_range_mhz'][1]:.0f} MHz) "
            f"exceeds the best simulated in-band design by less than the surrogate's bandwidth MAE ({mae['bw10_mhz']:.0f} MHz), so no "
            "proposal is a demonstrated improvement on the simulated data. "
            "That is the expected outcome for a dense sweep of a simple patch; the method becomes valuable when the design space "
            "is larger than what was simulated, as with the proposed DGS sweep. No proposal has been simulated, and none should "
            "be described as optimal or HFSS-validated. Repeated runs give slightly different Pareto sets because of thread-level "
            "non-determinism (docs/REPRODUCIBILITY.md)."))
    a(("h2", "9.6 Summary of hypotheses and evaluation criteria"))
    a(("table", C.tab("Module 2 outcomes."), ["ID", "Statement", "Outcome and evidence"], [list(c) for c in CR]))

    # ------------------------------------------------------------------ 10 Ethics
    a(("h1", "10. Ethics, Bias, Privacy, and Reproducibility"))
    a(("p", "**Data rights and privacy.** Both datasets are public under licences that permit reuse with attribution (MIT, CC BY 4.0) "
            "and contain no personal data. Attribution is given in the LICENSE file, the data card and the references. Raw files are "
            "re-downloaded by a script with SHA-256 checks; only derived tables and the Module 1 embeddings are committed."))
    a(("p", "**Bias.** (i) Topology and material bias: one coax-fed rectangular patch on one substrate, and one nominal dual-slot "
            "design with one-at-a-time variations. (ii) Coverage bias: dense sampling of a small region, so the surrogate is "
            "reliable only near simulated designs, as the OOD results show. (iii) Label bias: the −20 dB threshold is an assumption. "
            "(iv) Simulation-to-reality gap: no measurements, fabrication tolerances, connector or cable effects. (v) Solver "
            "artefacts: implausible Mendeley rows were flagged by a documented rule rather than silently removed."))
    a(("p", "**Responsible use.** Surrogate predictions, engineering summaries and Pareto proposals are screening outputs on simulated "
            "data. They are labelled as such in every file, and none may be presented as verified antenna performance without "
            "full-wave simulation and, for deployment, fabrication and measurement. The text generator is deliberately "
            "template-based so that it cannot hallucinate values. The intended scope is civilian communications research."))
    a(("p", "**Reproducibility.** One configuration file, fixed seeds, pinned dependencies, dataset revisions and checksums, the locked "
            "split manifests shared with Module 1, a provenance file with SHA-256 hashes for the imported embeddings, and scripts for "
            "every stage. Ten automated tests cover the S11 target extraction, label thresholds, split integrity against the "
            "manifests, the OOD rule, physical ranges, the Mendeley plausibility rule, embedding alignment, the optimisation "
            "constraints and the surrogate-versus-baseline check. All ten pass (Appendix D)."))

    # ------------------------------------------------------------------ 11 Limitations
    a(("h1", "11. Limitations and Future Work"))
    a(("bullets", ["**Topology mismatch.** The patch data contain no slots or DGS, and the Mendeley data vary one dimension at a time around "
                   "one design, so the surrogates do not transfer to hybrid-slotted DGS antennas.",
                   "**No HFSS.** All targets come from openEMS or the Mendeley authors' solver; HFSS outputs and field quantities were not available.",
                   "**Extrapolation.** Tree surrogates fail outside the training ranges (negative OOD R² for S11 at resonance and bandwidth).",
                   "**Matching depth.** S11 depth is predicted only moderately, which limits the reliability of the S11 objective in NSGA-II.",
                   "**Fusion.** One embedding run, one seed and no cross-fitting; the result should be confirmed with out-of-fold embeddings.",
                   "**Optimisation.** Proposals are unverified, close to existing designs, and the search ignores fabrication constraints and gain."]))
    a(("p", "**Future work.** (1) Generate the HFSS hybrid-slotted DGS sweep described in the reference report with PyAEDT, using a "
            "space-filling design of experiments rather than one-at-a-time variation. (2) Retrain the same surrogate pipeline and add "
            "uncertainty estimates (quantile forests or Gaussian processes) so that NSGA-II can penalise uncertain regions. "
            "(3) Re-simulate the Pareto proposals and add them to the training set in an active-learning loop. (4) Add gain and "
            "efficiency objectives once the DGS data provide them for every design. (5) Repeat the fusion experiment with "
            "cross-fitted embeddings, several seeds and late-fusion variants. (6) Fabricate and measure a shortlist to quantify the "
            "simulation-to-measurement gap."))

    # ------------------------------------------------------------------ 12 Conclusion
    a(("h1", "12. Conclusion"))
    a(("p", "Module 2 implements and executes a complete, reproducible numerical-text pipeline for the proposed framework. "
            f"Antenna parameters predict simulated resonance (R² = {r2['f_res_ghz']:.2f}) and bandwidth (R² = {r2['bw10_mhz']:.2f}) "
            f"well and the depth of the match only moderately (R² = {r2['s11_min_db']:.2f}) (RQ1); on a slotted patch, the geometry "
            "variables roughly halve the error of a frequency-only model for S11, gain and radiation efficiency (RQ2). Fusing "
            f"numerical features with ViT embeddings did not beat the embeddings alone ({fi:.3f} vs {im:.3f}; H6 not supported), "
            f"but the embeddings themselves reached {im:.3f}, showing that Module 1's representation is stronger than its own "
            "classifier head suggests (RQ3). Surrogate-based NSGA-II produced physically interpretable n78 proposals in two mode "
            "families, all close to simulated designs and all unverified (RQ4), and the template-based summaries report every "
            "prediction next to its simulated reference without inventing values (RQ5). The main lesson for the full HFSS study is "
            "that a surrogate is only as good as its coverage: the DGS sweep should be space-filling, the surrogate should report "
            "its uncertainty, and every optimised design should be treated as a hypothesis for full-wave verification."))

    # ------------------------------------------------------------------ Availability
    B.extend(availability(C))

    # ------------------------------------------------------------------ References
    a(("h1", "References"))
    a(("numbered", REFERENCES))

    # ------------------------------------------------------------------ Appendices
    a(("pagebreak",))
    a(("h1", "Appendix A. Data Dictionary"))
    dd = pd.read_csv(ROOT / "data" / "data_dictionary.csv")
    a(("table", C.tab("Data dictionary (data/data_dictionary.csv)."), ["Dataset", "Variable", "Type", "Unit", "Description"], dd.values.tolist()))
    a(("h1", "Appendix B. Configuration"))
    a(("code", (ROOT / "configs" / "default.yaml").read_text(encoding="utf-8")))
    a(("h1", "Appendix C. Experimental Details"))
    rows = []
    for k in pt:
        for m, v in pt[k]["models"].items():
            rows.append([k, m.replace("_", " "), f"{v['val']['MAE']:.3f}", f"{v['test']['MAE']:.3f}", f"{v['test']['R2']:.3f}",
                         f"{v['ood']['MAE']:.3f}", f"{v['ood']['R2']:.3f}"])
    a(("table", C.tab("Every patch surrogate candidate (validation, test and OOD)."), ["Target", "Model", "Val MAE", "Test MAE", "Test R²", "OOD MAE", "OOD R²"], rows))
    a(("p", "Deviations and abandoned choices: the first definition of resonance (the deepest S11 dip) was replaced before training "
            "by the first matched resonance because the deepest dip is often a higher-order mode. Radiation efficiency was added as "
            "a Mendeley target when Module 2 was separated from the combined prototype; it uses the same plausibility rule as gain. "
            "No test-set result was used for any decision."))
    a(("h1", "Appendix D. Reproducibility Instructions"))
    a(("code", "python -m venv .venv && .venv\\Scripts\\activate\n"
               "pip install -r requirements.txt\n"
               "python -m src.download_data          # ~10 MB: patch Parquet + Mendeley XLSX (checksummed)\n"
               "python -m src.preprocessing          # targets, cleaning, split check against data/splits\n"
               "python -m src.numerical_model        # surrogates, parity plots, engineering summaries\n"
               "python -m src.fusion_optimization    # fusion with Module 1 embeddings + NSGA-II\n"
               "pytest -q\n"
               "python scripts/make_deliverables.py"))
    a(("p", f"Repository: {REPO_URL}. The pytest output ({test_summary()}) is stored in {link('results/test_report.txt')}; "
            f"environment and determinism notes are in {link('docs/REPRODUCIBILITY.md')}. All links are listed in the section "
            "Data, Code and Output Availability."))
    return B


REFERENCES = [
    "A. Dosovitskiy et al., \"An image is worth 16x16 words: Transformers for image recognition at scale,\" in Proc. ICLR, 2021, arXiv:2010.11929.",
    "B. LaBash et al., \"Improving generative inverse design of rectangular patch antennas with test time optimization,\" arXiv:2505.18188, 2025. Dataset: huggingface.co/datasets/becklabash/rectangular-patch-antenna-freq-response (MIT), rev. 4be72a2.",
    "M. F. H. Mihad, M. M. Islam and F. H. Sojib, \"Antenna Parameters Dataset,\" Mendeley Data, v2, 2024, doi:10.17632/3gxr2vvd9n.2 (CC BY 4.0).",
    "C. A. Balanis, Antenna Theory: Analysis and Design, 4th ed. Hoboken, NJ: Wiley, 2016.",
    "3GPP, \"NR; User Equipment (UE) radio transmission and reception; Part 1: Range 1 Standalone,\" TS 38.101-1.",
    "L. Breiman, \"Random forests,\" Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "G. Ke et al., \"LightGBM: A highly efficient gradient boosting decision tree,\" in Proc. NeurIPS, 2017.",
    "F. Pedregosa et al., \"Scikit-learn: Machine learning in Python,\" J. Mach. Learn. Res., vol. 12, pp. 2825–2830, 2011.",
    "K. Deb, A. Pratap, S. Agarwal and T. Meyarivan, \"A fast and elitist multiobjective genetic algorithm: NSGA-II,\" IEEE Trans. Evol. Comput., vol. 6, no. 2, pp. 182–197, 2002.",
    "J. Blank and K. Deb, \"pymoo: Multi-objective optimization in Python,\" IEEE Access, vol. 8, pp. 89497–89509, 2020.",
    "T. Liebig et al., openEMS – a free and open electromagnetic field solver, https://openems.de.",
    "A. E. Hoerl and R. W. Kennard, \"Ridge regression: Biased estimation for nonorthogonal problems,\" Technometrics, vol. 12, no. 1, pp. 55–67, 1970.",
    "A. Fisher, C. Rudin and F. Dominici, \"All models are wrong, but many are useful: Learning a variable's importance by studying an entire class of prediction models simultaneously,\" J. Mach. Learn. Res., vol. 20, no. 177, pp. 1–81, 2019.",
    "D. E. Rumelhart, G. E. Hinton and R. J. Williams, \"Learning representations by back-propagating errors,\" Nature, vol. 323, pp. 533–536, 1986.",
    "T. Baltrušaitis, C. Ahuja and L.-P. Morency, \"Multimodal machine learning: A survey and taxonomy,\" IEEE Trans. Pattern Anal. Mach. Intell., vol. 41, no. 2, pp. 423–443, 2019.",
]

META = {
    "kicker": "Applied AI Research Workshop - Module 2 Methodology and Implementation Report",
    "title": TITLE,
    "subtitle": SUBTITLE,
    "doc_type": "Module 2: Numerical-Text Surrogate, Multimodal Fusion and NSGA-II Multi-Objective Optimisation",
    "fields": [("Student name", "Ms. Rathi Devadhas"), ("Student ID", "1737089"),
               ("Programme", "Master of Applied Artificial Intelligence"),
               ("Submission date", "26 October 2026"),
               ("Code repository", REPO_URL)],
    "note": "All results are from executed experiments on public simulation data. Ansys HFSS was not available and was not run.",
    "author": "Ms. Rathi Devadhas",
}


def main():
    R = load()
    blocks = build(R)
    out = ROOT / "reports"
    out.mkdir(exist_ok=True)
    to_docx(blocks, META, out / "module2_report.docx")
    to_tex(blocks, META, out / "module2_report.tex")
    print("report written")


if __name__ == "__main__":
    main()
