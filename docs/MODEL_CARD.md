# Model card: numerical surrogates, text generator, fusion MLP and NSGA-II (Module 2)

## Model details
| Item | Value |
|---|---|
| Patch surrogates | Random forest, 400 trees (selected on validation MAE over mean baseline, ridge and histogram gradient boosting) for f_res, S11min, S11 at f_res, −10 dB bandwidth |
| Mendeley surrogates | Random forest, 400 trees, on 10 dimensions + frequency for S11, gain and radiation efficiency |
| Text generator | Deterministic template; verbalises surrogate predictions and simulated references only |
| Fusion | MLP (scikit-learn) on 384-d ViT embedding + 5 standardised numeric features; hidden size and L2 chosen on validation macro-F1 |
| Optimiser | NSGA-II (pymoo), population 100, 80 generations; variables L, W/L, feed ratio; objectives min S11 at f_res, max bandwidth, min area; constraint f_res in 3.3–3.8 GHz |
| Developed | October 2026, applied AI research workshop prototype, CPU only |

## Intended use
Research and teaching: fast **screening** of simulated patch designs and a template for the planned HFSS DGS study.
**Not** for certifying or deploying antennas. Every proposal requires full-wave verification.

## Evaluation (see `results/metrics/`)
| Target | Test R² | Test MAE | OOD R² |
|---|---|---|---|
| First matched resonance (GHz) | 0.89 | 0.35 | 0.44 |
| Minimum S11 (dB) | 0.54 | 4.81 | 0.13 |
| S11 at resonance (dB) | 0.57 | 3.27 | −1.54 |
| −10 dB bandwidth (MHz) | 0.83 | 18.06 | −3.72 |

Mendeley (GroupKFold, out-of-fold): S11 R² 0.86, gain 0.99, radiation efficiency 0.97; geometry + frequency roughly halves the
frequency-only error. Fusion (matching class, test macro-F1): fused 0.737, image-only 0.775, numeric-only 0.716.
NSGA-II: 100 n78 proposals (not simulated). Exact values for the committed run are in `results/metrics/*.json`.

## Known failure modes
* Tree surrogates cannot extrapolate: R² is negative for S11 and bandwidth on the wider OOD patches.
* Matching depth (S11) is predicted only moderately because it depends sharply on the feed impedance.
* Mendeley scores are optimistic: one-at-a-time sweeps leave near-identical designs in different folds.
* NSGA-II proposals stay close to simulated designs and do not demonstrably improve on them.

## Ethical considerations
Simulation data only, no personal data. The text generator cannot invent values by construction. Proposals are labelled
"NOT simulated" in every file. The intended scope is civilian communications research.
