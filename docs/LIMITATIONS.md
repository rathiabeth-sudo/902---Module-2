# Known limitations - Module 2

## Scope and evidence
1. **No HFSS.** Ansys HFSS was not available and was not run. No result in this repository is an HFSS result.
2. **Topology mismatch.** The patch data are plain coax-fed rectangular patches on one substrate; the Mendeley data vary one dimension at a
   time around one nominal dual-slot design. Conclusions do **not** transfer to hybrid-slotted DGS antennas without new data.
3. **Simulation-only evidence.** No measurements, fabrication tolerances, connector losses or material variability.

## Surrogates
4. **No extrapolation.** Random forests fail outside the training range (negative OOD R² for S11 at resonance and bandwidth).
5. **Matching depth** is predicted only moderately (R² ≈ 0.54), which limits the S11 objective in the optimisation.
6. **Mendeley scores are optimistic**: a frequency-only model already reaches R² ≈ 0.98 for gain, and near-identical designs fall in different folds.
7. No hyperparameter search beyond the four candidate models; no predictive uncertainty.

## Fusion
8. One embedding run (Module 1 seed 42) and one MLP seed; the embeddings were fitted on the same training labels, so training features are
   optimistic. Confirm with cross-fitted embeddings and several seeds.

## Optimisation
9. NSGA-II proposals are **surrogate predictions, not simulations**. They are close to existing designs and ignore gain, efficiency and
   fabrication constraints. Repeated runs give slightly different Pareto sets (thread-level non-determinism).

## Text generation
10. Template-based: it cannot invent numbers, but it also cannot explain *why* a design behaves as it does.

## Labels
11. The **−20 dB** boundary between "Acceptable" and "High" is a project assumption and needs engineering confirmation.

## What full validation requires
* A space-filling HFSS sweep of hybrid-slotted DGS designs (PyAEDT), with gain and efficiency exported for every design.
* Uncertainty-aware surrogates and active learning with re-simulated proposals.
* Fabrication and VNA / anechoic-chamber measurement of a shortlist.
