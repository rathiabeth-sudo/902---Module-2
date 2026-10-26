# Data card - Module 2 (numerical-text module)

| Item | Patch sweep (primary) | Mendeley dual-slot patch | Module 1 embeddings (derived input) |
|---|---|---|---|
| Source | Hugging Face `becklabash/rectangular-patch-antenna-freq-response` @ `4be72a2` | Mendeley Data 10.17632/3gxr2vvd9n.2 (v2) | Module 1 run `vit_finetune_patch_perf_class_s42` |
| Licence | MIT | CC BY 4.0 | derived from MIT data |
| Evidence type | **Simulated** (openEMS FDTD, εr = 3.68, h = 1.61 mm) | **Simulated** (solver not named by the authors; one-at-a-time sweeps) | Model output (ViT CLS embedding) |
| Unit of analysis | One design (L, W, feed offset) with a 1,000-point S11 curve | One design × one frequency (103 designs × 16 frequencies) | One design (384-d vector) |
| Samples used | 2,051 designs (0 excluded) | 1,648 rows; 245 implausible rows excluded from gain / efficiency targets | 2,051 vectors (train / val / test / OOD) |
| Inputs | L, W, feed offset, W/L, feed ratio | 10 dimensions (substrate, patch, feed, two slots) + frequency | - |
| Targets | first matched resonance f_res, S11min, S11 at f_res, −10 dB bandwidth; `perf_class` for fusion | S11 (dB), gain (dBi), radiation efficiency | - |
| Split | Locked design-level split shared with Module 1: train 1,220 / val 262 / test 262 / OOD 307 (W/L > 1.95) | 5-fold GroupKFold by design | follows the patch split |
| In repo | Derived CSV (`data/processed/patch_designs.csv`) and split manifests | Cleaned CSV with `plausible` flag (with attribution) | `.npy` files + `provenance.json` (SHA-256) |

## Target definitions

* **f_res** - first matched resonance: the lowest-frequency local minimum of S11 below −10 dB. The deepest dip is often a higher-order
  mode, so it is not used as the resonance. If a design is never matched, the global minimum is used and the bandwidth is 0.
* **S11min** - global minimum of simulated S11 over 1–10 GHz. **S11 at f_res** - S11 at the first matched resonance.
* **−10 dB bandwidth** - contiguous band around f_res where S11 < −10 dB.
* **perf_class** (fusion target): Poor if S11min > −10 dB, Acceptable if −20 dB < S11min ≤ −10 dB, High if S11min ≤ −20 dB.
  The −20 dB boundary is a **project assumption** that needs engineering confirmation.

## Cleaning and plausibility rule (Mendeley)

A row is flagged if radiation or total efficiency > 1, directivity > 20 dBi (for an antenna of about 6 mm), or gain > directivity.
245 of 1,648 rows are flagged; they are excluded from the gain and efficiency targets but kept for S11. One truncated, non-numeric
efficiency entry was set to missing. Counts are in `results/metrics/mendeley_cleaning.json`.

## Quality control performed

* Patch: 0 non-finite curves, 0 duplicate parameter triples, 0 missing values after feature extraction; 1,170 curves exceed 0 dB by at most
  0.2 dB (passive-port numerical artefact, documented, kept).
* The reproduced split is checked against the committed manifests in `data/splits/` on every preprocessing run.
* Embedding rows are checked against the split sizes; their hashes are recorded.

## Intended use and out-of-scope use

Research and teaching on surrogate-based antenna screening. **Not** for certifying antennas. The patch data contain one topology and one
substrate without slots or DGS, and the Mendeley data vary one dimension at a time around one nominal design, so the surrogates do not
transfer to hybrid-slotted DGS antennas without new HFSS data.
