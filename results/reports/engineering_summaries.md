# Engineering summaries (auto-generated from surrogate predictions)

Values labelled *predicted* come from the Module 2 surrogate; values labelled *simulated* are the openEMS reference from the dataset. The text generator only verbalises computed numbers; it never invents values.

## Locked test-split designs

**P1966** - patch L x W = 46.15 x 80.87 mm (W/L 1.75), feed offset -4.51 mm. Predicted first matched resonance 2.85 GHz, below 5 GHz (FR1 mid-band region); predicted minimum S11 -27.6 dB, which meets the -20 dB project threshold (High class); predicted -10 dB bandwidth 1 MHz. Simulated reference (openEMS): 2.58 GHz, -22.8 dB, 0 MHz. Status: surrogate screening only - requires full-wave verification.

**P1768** - patch L x W = 42.35 x 78.50 mm (W/L 1.85), feed offset -1.89 mm. Predicted first matched resonance 3.57 GHz, inside 5G NR n78 (3.3-3.8 GHz, FR1); predicted minimum S11 -26.1 dB, which meets the -20 dB project threshold (High class); predicted -10 dB bandwidth 45 MHz. Simulated reference (openEMS): 3.54 GHz, -28.7 dB, 36 MHz. Status: surrogate screening only - requires full-wave verification.

**P1629** - patch L x W = 39.43 x 50.96 mm (W/L 1.29), feed offset -7.84 mm. Predicted first matched resonance 1.94 GHz, below 5 GHz (FR1 mid-band region); predicted minimum S11 -28.9 dB, which meets the -20 dB project threshold (High class); predicted -10 dB bandwidth 16 MHz. Simulated reference (openEMS): 1.92 GHz, -26.2 dB, 18 MHz. Status: surrogate screening only - requires full-wave verification.

**P1473** - patch L x W = 35.18 x 33.05 mm (W/L 0.94), feed offset -6.89 mm. Predicted first matched resonance 2.49 GHz, below 5 GHz (FR1 mid-band region); predicted minimum S11 -24.6 dB, which meets the -20 dB project threshold (High class); predicted -10 dB bandwidth 32 MHz. Simulated reference (openEMS): 2.16 GHz, -24.9 dB, 18 MHz. Status: surrogate screening only - requires full-wave verification.

## NSGA-II surrogate proposals for 5G NR n78 (not simulated)

**N78-001** (smallest area) - patch L x W = 19.31 x 15.48 mm (area 299 mm², W/L 0.80), feed offset -2.89 mm. Predicted first matched resonance 3.79 GHz, inside 5G NR n78 (3.3-3.8 GHz, FR1); predicted S11 at resonance -26.6 dB, which meets the -20 dB project threshold (High class); predicted -10 dB bandwidth 64 MHz. Nearest simulated design P0564 (0.07 standard units away) resonates at 3.82 GHz with -28.6 dB and 63 MHz. Status: surrogate proposal - NOT simulated; requires full-wave verification.

**N78-066** (widest predicted bandwidth) - patch L x W = 22.08 x 23.08 mm (area 509 mm², W/L 1.05), feed offset -4.25 mm. Predicted first matched resonance 3.72 GHz, inside 5G NR n78 (3.3-3.8 GHz, FR1); predicted S11 at resonance -22.0 dB, which meets the -20 dB project threshold (High class); predicted -10 dB bandwidth 103 MHz. Nearest simulated design P1152 (0.14 standard units away) resonates at 3.43 GHz with -18.9 dB and 63 MHz. Status: surrogate proposal - NOT simulated; requires full-wave verification.

**N78-098** (deepest predicted match) - patch L x W = 40.75 x 67.09 mm (area 2734 mm², W/L 1.65), feed offset -1.96 mm. Predicted first matched resonance 3.68 GHz, inside 5G NR n78 (3.3-3.8 GHz, FR1); predicted S11 at resonance -34.6 dB, which meets the -20 dB project threshold (High class); predicted -10 dB bandwidth 51 MHz. Nearest simulated design P1701 (0.00 standard units away) resonates at 3.68 GHz with -39.6 dB and 54 MHz. Status: surrogate proposal - NOT simulated; requires full-wave verification.
