"""Extended Module 2 deck -> presentations/module2_extended_presentation.pptx.

A teaching-style walkthrough: antenna basics, why AI helps, input features, the staged pipeline (acquisition,
cleaning, vectorisation, model training, text generation), every executed output, and the engineering benefits.
Each content slide carries a note bubble on the right plus matching speaker notes. All numbers come from results/.
"""
from __future__ import annotations

import json

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from deliverables_common import (COMPANION_URL, FIG, M, MEND_TARGETS, PATCH_TARGETS, REPO_URL, ROOT, TITLE, criteria, load,
                                 test_summary)
from make_report import summaries
from make_slides import ACCENT, BLUE, EDGE, GREY, ICE, NAVY, SOFT, WHITE, background, bullets, card, text

FONT = "Calibri"
DARKCARD = RGBColor(0x14, 0x3A, 0x62)
NOTE_FILL = RGBColor(0xFF, 0xF8, 0xE6)
NOTE_EDGE = RGBColor(0xE0, 0xB4, 0x5A)
GREEN = RGBColor(0x1F, 0x6F, 0x2A)
KICK = "MODULE 2 · NUMERICAL-TEXT SURROGATE, FUSION & OPTIMISATION · EXTENDED"
AUTHOR = "Ms. Rathi Devadhas · Student ID 1737089 · Master of Applied Artificial Intelligence"
CONTENT_W = Inches(8.55)   # left content column; the note bubble sits to its right
TOTAL = 21


class Deck:
    def __init__(self):
        self.prs = Presentation()
        self.prs.slide_width, self.prs.slide_height = Inches(13.333), Inches(7.5)
        self.n = 0

    def slide(self, title, dark=False, section=None):
        s = self.prs.slides.add_slide(self.prs.slide_layouts[6])
        self.n += 1
        background(s, self.prs, NAVY if dark else WHITE)
        kick = (section.upper() + " · " if section else "") + "MODULE 2 · EXTENDED"
        text(s, Inches(0.6), Inches(0.32), Inches(9), Inches(0.35), kick, size=12, color=SOFT if dark else BLUE, bold=True)
        text(s, Inches(0.6), Inches(0.62), Inches(12.1), Inches(0.8), title, size=30, color=WHITE if dark else NAVY, bold=True)
        text(s, Inches(0.6), self.prs.slide_height - Inches(0.42), Inches(10.5), Inches(0.3),
             "Simulation evidence only (openEMS, Mendeley) · Ansys HFSS not run · AI proposals are not simulated",
             size=10, color=SOFT if dark else GREY)
        text(s, self.prs.slide_width - Inches(1.5), self.prs.slide_height - Inches(0.42), Inches(0.9), Inches(0.3),
             f"{self.n} / {TOTAL}", size=10, color=SOFT if dark else GREY, align=PP_ALIGN.RIGHT)
        return s


def note(slide, paras, y=1.55, h=None, notes_text=None):
    """Speech-bubble note on the right of the slide (tail points at the content); also copied to speaker notes."""
    if h is None:  # size the bubble to its text (about 36 characters per line at 13 pt)
        lines = sum(-(-len(t) // 33) for t in paras)
        h = min(5.3, max(1.8, 0.6 + 0.245 * lines + 0.09 * len(paras)))
    b = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGULAR_CALLOUT, Inches(9.45), Inches(y), Inches(3.3), Inches(h))
    b.adjustments[0] = -0.60   # tail tip x (relative to the shape centre, as a fraction of the width)
    b.adjustments[1] = -0.30   # tail tip y
    b.fill.solid()
    b.fill.fore_color.rgb = NOTE_FILL
    b.line.color.rgb = NOTE_EDGE
    b.line.width = Pt(1.25)
    b.shadow.inherit = False
    b.name = "Explanation bubble"
    tf = b.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = MSO_ANCHOR.TOP
    tf.margin_left = tf.margin_right = Inches(0.18)
    tf.margin_top = Inches(0.14)
    for i, t in enumerate(paras):   # no heading inside the bubble, just the explanation
        q = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        q.space_before = Pt(0 if i == 0 else 5)
        q.alignment = PP_ALIGN.LEFT
        rr = q.add_run()
        rr.text = t
        rr.font.size, rr.font.color.rgb, rr.font.name = Pt(13), NAVY, FONT
    slide.notes_slide.notes_text_frame.text = notes_text or " ".join(paras)


def grid(slide, x, y, w, rows, col_w, size=13, row_h=0.36, head=NAVY, bold_first_col=False, center_from=None):
    shp = slide.shapes.add_table(len(rows), len(rows[0]), x, y, w, Inches(row_h * len(rows)))
    t = shp.table
    for j, cw in enumerate(col_w):
        t.columns[j].width = cw
    for i, r in enumerate(rows):
        t.rows[i].height = Inches(row_h)
        for j, v in enumerate(r):
            c = t.cell(i, j)
            c.text = ""
            p = c.text_frame.paragraphs[0]
            run = p.add_run()
            run.text = str(v)
            run.font.size, run.font.name = Pt(size), FONT
            run.font.bold = i == 0 or (bold_first_col and j == 0)
            run.font.color.rgb = WHITE if i == 0 else NAVY
            p.alignment = PP_ALIGN.CENTER if (center_from is not None and j >= center_from) else PP_ALIGN.LEFT
            c.fill.solid()
            c.fill.fore_color.rgb = head if i == 0 else (ICE if i % 2 else WHITE)
            c.margin_top = c.margin_bottom = Emu(22000)
            c.margin_left = c.margin_right = Emu(60000)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    return t


def flow(slide, x, y, w, h, steps, fills, size=12, gap=0.06):
    """Chevron process flow; returns the shapes."""
    n = len(steps)
    step_w = (w - Inches(gap) * (n - 1)) / n
    out = []
    for i, (label, fill) in enumerate(zip(steps, fills)):
        shp = slide.shapes.add_shape(MSO_SHAPE.PENTAGON if i == 0 else MSO_SHAPE.CHEVRON,
                                     int(x + i * (step_w + Inches(gap))), y, int(step_w), h)
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
        shp.line.fill.background()
        shp.shadow.inherit = False
        # label in its own text box: chevron shapes reserve a large inner inset that breaks words
        notch = Inches(0.22) if i else 0
        tb = slide.shapes.add_textbox(int(x + i * (step_w + Inches(gap)) + notch), y, int(step_w - notch - Inches(0.16)), h)
        tf = tb.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.03)
        tf.vertical_anchor = MSO_ANCHOR.MIDDLE
        p = tf.paragraphs[0]
        p.alignment = PP_ALIGN.CENTER
        r = p.add_run()
        r.text = label
        r.font.size, r.font.bold, r.font.name = Pt(size), True, FONT
        r.font.color.rgb = WHITE if fill in (NAVY, BLUE, DARKCARD, GREEN, ACCENT) else NAVY
        out.append(shp)
    return out


def chip(slide, x, y, w, h, title, body, fill=ICE, title_color=BLUE, size=13):
    card(slide, x, y, w, h, fill=fill, line=EDGE)
    text(slide, x + Inches(0.15), y + Inches(0.08), w - Inches(0.3), Inches(0.4), title, size=15, color=title_color, bold=True)
    text(slide, x + Inches(0.15), y + Inches(0.48), w - Inches(0.3), h - Inches(0.55), body, size=size, color=NAVY)


def pic(slide, path, x, y, w=None, h=None):
    return slide.shapes.add_picture(str(path), x, y, width=w, height=h)


def main():
    R = load()
    num, fu, opt, prep, clean, par, prov = R["num"], R["fu"], R["opt"], R["prep"], R["clean"], R["pareto"], R["prov"]
    pt, md, sel = num["patch"], num["mendeley"], R["sel"]
    tm = json.load(open(M / "timing.json", encoding="utf-8"))
    CR = criteria(R)
    sc = prep["patch_split_counts"]
    fi, im, nu = (fu[k]["test"]["macro_f1"] for k in ["fusion_concat", "image_only", "numeric_only"])
    lo, hi = opt["band_ghz"]
    test_s, prop_s = summaries()
    D = Deck()
    I = Inches

    # ================================================================ 1 title (dark)
    s = D.slide("", dark=True)
    text(s, I(0.6), I(0.7), I(12.1), I(1.3), TITLE, size=32, color=WHITE, bold=True)   # paper title
    text(s, I(0.6), I(2.05), I(12.1), I(0.9),
         "Module 2 of the Applied Vision Transformer Framework for Hybrid-Slotted DGS Compact Patch Antenna Design: "
         "HFSS-Driven Multi-Objective Optimization for 5G and Emerging 6G Networks", size=17, color=SOFT)
    for i, (big, lab) in enumerate([("2,051", "simulated patch designs"), ("103 × 16", "slotted designs × frequencies"),
                                    (f"R² {sel('f_res_ghz')['R2']:.2f}", "resonance prediction (test)"),
                                    (str(opt["n_pareto"]), "AI design proposals for 5G n78")]):
        x = I(0.6 + i * 3.1)
        card(s, x, I(3.1), I(2.85), I(1.45), fill=DARKCARD, line=None)
        text(s, x + I(0.2), I(3.17), I(2.6), I(0.7), big, size=32, color=WHITE, bold=True)
        text(s, x + I(0.2), I(3.88), I(2.6), I(0.6), lab, size=14, color=SOFT)
    text(s, I(0.6), I(4.9), I(11.8), I(1.2), [[("Ms. Rathi Devadhas", {"bold": True, "size": 20, "color": WHITE})],
                                              [("Student ID 1737089  ·  Master of Applied Artificial Intelligence  ·  28 October 2026", {"size": 15, "color": SOFT})],
                                              [(REPO_URL, {"size": 13, "color": SOFT})]], size=15)
    s.notes_slide.notes_text_frame.text = (
        "This extended deck explains Module 2 from first principles: what antennas and slot / DGS antennas are, why AI helps, "
        "which inputs the models use, the stage-by-stage pipeline, every executed output, and what it means for engineers. "
        "All numbers come from the executed runs in the GitHub repository.")

    # ================================================================ 2 agenda
    s = D.slide("Agenda", section="Overview")
    items = [("1", "Antenna basics", "antenna, slot antenna, hybrid-slotted DGS antenna"),
             ("2", "Why AI for antenna design", "conventional loop vs AI-assisted screening"),
             ("3", "Pipeline stages", "acquisition → cleaning → vectorisation → training → text"),
             ("4", "Inputs and features", "what the AI sees, and why each parameter matters"),
             ("5", "Outputs", "surrogate accuracy, text summaries, fusion, NSGA-II designs"),
             ("6", "Value for engineers", "benefits, limits and the path to HFSS validation")]
    for i, (k, t, d) in enumerate(items):
        col, rowi = i % 2, i // 2
        x, y = I(0.6 + col * 4.35), I(1.6 + rowi * 1.6)
        card(s, x, y, I(4.1), I(1.38))
        circ = s.shapes.add_shape(MSO_SHAPE.OVAL, x + I(0.2), y + I(0.3), I(0.75), I(0.75))
        circ.fill.solid()
        circ.fill.fore_color.rgb = NAVY
        circ.line.fill.background()
        circ.text_frame.text = k
        circ.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        circ.text_frame.paragraphs[0].runs[0].font.size = Pt(20)
        circ.text_frame.paragraphs[0].runs[0].font.bold = True
        text(s, x + I(1.15), y + I(0.2), I(2.85), I(0.45), t, size=17, bold=True)
        text(s, x + I(1.15), y + I(0.65), I(2.85), I(0.7), d, size=13, color=GREY)
    note(s, ["The deck moves from physics to data to AI to engineering value.",
             "Yellow bubbles like this one explain each slide in plain words.",
             "Every number shown later is read from the executed results, not typed by hand."])

    # ================================================================ 3 antenna definitions
    s = D.slide("What is an antenna, and how is it judged?", section="1 · Antenna basics")
    chip(s, I(0.6), I(1.55), CONTENT_W, I(1.25), "Definition",
         "An antenna converts guided electrical signals into radiated electromagnetic waves (and back). A microstrip patch "
         "antenna is a flat copper patch on a dielectric substrate above a ground plane - cheap, thin and easy to print on a PCB.")
    grid(s, I(0.6), I(3.0), CONTENT_W, [
        ["Performance term", "What it means", "Used in this project as"],
        ["Resonant frequency f_res", "frequency where the antenna is matched and radiates best", "regression target (GHz)"],
        ["S11 / return loss", "share of power reflected back; lower dB = better match", "target (dB) + class label"],
        ["−10 dB bandwidth", "frequency range with S11 < −10 dB (VSWR ≈ 1.9)", "regression target (MHz)"],
        ["Gain", "radiated power in the best direction vs an isotropic source", "target (dBi), Mendeley"],
        ["Radiation efficiency", "radiated power / accepted power (0–1)", "target, Mendeley"],
        ["Band (5G / 6G)", "n78 3.3–3.8 GHz; FR1 ≤ 7.125 GHz; FR3 above", "label and NSGA-II constraint"],
    ], [I(2.3), I(3.85), I(2.4)], size=12, row_h=0.43, bold_first_col=True)
    note(s, ["Engineers judge an antenna by where it resonates, how well it is matched (S11), how wide its usable band is, and "
             "how much power it radiates (gain, efficiency).",
             "These same quantities are what Module 2's AI learns to predict from the design dimensions.",
             "−10 dB S11 is the standard matching criterion; the −20 dB 'High' class is a project assumption."])

    # ================================================================ 4 slot and hybrid DGS
    s = D.slide("Slot antennas and hybrid-slotted DGS antennas", section="1 · Antenna basics")
    pic(s, FIG / "antenna_types.png", I(0.6), I(1.45), w=CONTENT_W)
    y0 = I(4.6)
    for i, (t, b) in enumerate([("Slot antenna", "Slots cut in the patch (or a slot as the radiator) lengthen the current path: lower "
                                                  "resonance for the same size, and extra or wider bands."),
                                ("Defected ground (DGS)", "Shapes etched into the ground plane (dumbbell, slot) change the "
                                                          "ground current: better matching, filtering, smaller size."),
                                ("Hybrid-slotted DGS", "Both together - slotted patch plus DGS. Very compact and multiband, "
                                                       "but dozens of coupled dimensions to tune.")]):
        chip(s, I(0.6 + i * 2.88), y0, I(2.75), I(2.05), t, b, size=12)
    note(s, ["A plain patch has three main dimensions; a hybrid-slotted DGS antenna has dozens (slot lengths, widths, offsets, DGS shape).",
             "Every extra dimension multiplies the number of full-wave simulations needed to explore the design.",
             "That combinatorial growth is exactly where a fast AI surrogate earns its place.",
             "The target topology here is hybrid-slotted DGS; the executed prototype uses public patch and dual-slot data."])

    # ================================================================ 5 why AI
    s = D.slide("Why AI helps: from slow loops to fast screening", section="2 · Why AI")
    text(s, I(0.6), I(1.5), CONTENT_W, I(0.4), "Conventional design loop", size=16, bold=True, color=GREY)
    flow(s, I(0.6), I(1.95), CONTENT_W, I(0.8), ["Pick sizes", "Full-wave run", "Read S11", "Tweak", "Repeat"], [ICE] * 5, size=12)
    text(s, I(0.6), I(2.85), CONTENT_W, I(0.4), "Each candidate typically costs minutes to hours of solver time; sweeps grow "
         "exponentially with the number of dimensions.", size=13, color=GREY)
    text(s, I(0.6), I(3.45), CONTENT_W, I(0.4), "AI-assisted loop (Module 2)", size=16, bold=True, color=BLUE)
    flow(s, I(0.6), I(3.9), CONTENT_W, I(0.8), ["Simulate once", "Train", "Screen 1000s", "NSGA-II", "HFSS check"], [NAVY, BLUE, BLUE, BLUE, ACCENT], size=12)
    for i, (big, lab) in enumerate([(f"{tm['batch_predict_seconds_all_targets']:.1f} s", f"to predict all 4 outputs for {tm['n_test_designs']} test designs"),
                                    (f"≈{tm['batch_ms_per_design_all_targets']:.0f} ms", "per design in a batch (measured, laptop CPU)"),
                                    (f"{tm['rf_fit_seconds_one_target']:.1f} s", "to train one 400-tree random forest")]):
        x = I(0.6 + i * 2.88)
        card(s, x, I(5.0), I(2.75), I(1.45))
        text(s, x + I(0.15), I(5.05), I(2.5), I(0.65), big, size=30, bold=True)
        text(s, x + I(0.15), I(5.7), I(2.5), I(0.7), lab, size=12, color=GREY)
    note(s, ["The AI does not replace the solver: it learns from solver results, then screens new candidates almost instantly.",
             "Speeds on this slide were measured on the project laptop (src/timing.py).",
             "Only the short-listed designs go back to full-wave simulation, so fewer expensive runs are needed.",
             "The orange step is required: AI proposals are hypotheses until simulated and measured."])

    # ================================================================ 6 pipeline overview
    s = D.slide("The Module 2 pipeline: seven stages", section="3 · Pipeline")
    stages = ["1 Data acquisition", "2 Cleaning & noise removal", "3 Feature engineering & vectorisation",
              "4 Model building & training", "5 Evaluation", "6 Text generation", "7 Fusion & optimisation"]
    flow(s, I(0.6), I(1.6), CONTENT_W, I(1.05), ["1 Acquisition", "2 Cleaning", "3 Vectorisation", "4 Training"],
         [NAVY, BLUE, BLUE, BLUE], size=13)
    flow(s, I(0.6), I(2.85), CONTENT_W, I(1.05), ["5 Evaluation", "6 Text generation", "7 Fusion & NSGA-II"],
         [BLUE, GREEN, ACCENT], size=13)
    grid(s, I(0.6), I(4.15), CONTENT_W, [
        ["Stage", "Code", "Main output"],
        ["1-2 Acquisition, cleaning", "src/download_data.py, src/preprocessing.py", "clean tables, targets, locked split"],
        ["3-5 Features, training, evaluation", "src/numerical_model.py", "surrogates, metrics, parity plots"],
        ["6 Text generation", "src/numerical_model.py, src/fusion_optimization.py", "engineering summaries (.md)"],
        ["7 Fusion & NSGA-II", "src/fusion_optimization.py", "fusion metrics, Pareto proposals"],
    ], [I(2.6), I(3.35), I(2.6)], size=12, row_h=0.4, bold_first_col=True)
    note(s, ["The work is a fixed sequence of stages, each a script in the repository, so anyone can rerun it end to end.",
             "Stages 1-5 are classic supervised machine learning on tabular data.",
             "Stage 6 is where text enters: the AI's numbers are turned into readable engineering sentences.",
             "Stage 7 links to Module 1 (image features) and searches for new designs."])

    # ================================================================ 7 mapping to text-AI stages
    s = D.slide("How the classic text-AI stages map onto this project", section="3 · Pipeline")
    grid(s, I(0.6), I(1.5), CONTENT_W, [
        ["Text-AI stage", "Used?", "What Module 2 does"],
        ["1 Data acquisition", "Yes", "Downloads two public simulation datasets with pinned versions and SHA-256 checks"],
        ["2 Text cleaning & noise removal", "Adapted", "Cleans numeric data: names, types, a corrupt entry, solver artefacts, 245 impossible rows"],
        ["3 Linguistic & semantic analysis", "Output side", "No text is read as input. Semantic rules map numbers to meaning (band, match class) when writing text"],
        ["4 Vectorisation", "Yes (numeric)", "Design parameters → standardised feature vectors; images → 384-d ViT vectors (from Module 1)"],
        ["5 Model building & training", "Yes", "Random forest, gradient boosting, ridge, MLP; NSGA-II search on the trained surrogates"],
        ["Text generation", "Yes", "Data-to-text templates write one summary per design; no language model, no invented values"],
    ], [I(2.55), I(1.25), I(4.75)], size=12, row_h=0.62, bold_first_col=True)
    note(s, ["Module 2 is a numerical-text module: its inputs are numbers and its text is an output.",
             "So linguistic analysis of input text (tokenising, parsing, sentiment) is not used - there is no input text to analyse.",
             "The 'semantic' step happens when writing: rules decide what a number means for an engineer (in n78? matched?).",
             "Vectorisation is numeric: each design becomes a vector the models can learn from."])

    # ================================================================ 8 data acquisition
    s = D.slide("Stage 1 - Data acquisition", section="3 · Pipeline")
    chip(s, I(0.6), I(1.55), I(4.15), I(2.6), "openEMS patch sweep",
         "2,051 coax-fed rectangular patches (Hugging Face, MIT, rev 4be72a2). Inputs: L, W, feed offset. Output: a 1,000-point "
         "S11 curve from 1 to 10 GHz per design (full-wave FDTD).", size=13)
    chip(s, I(4.95), I(1.55), I(4.2), I(2.6), "Mendeley dual-slot patch",
         "103 slotted designs × 16 frequencies, 1–50 GHz (Mendeley Data v2, CC BY 4.0). Inputs: 10 dimensions incl. two slots. "
         "Outputs: S11, gain, directivity, efficiency, VSWR.", size=13)
    chip(s, I(0.6), I(4.35), I(4.15), I(2.15), "Module 1 image embeddings",
         "384-d ViT vector per patch design, exported by Module 1; SHA-256 hashes recorded in provenance.json.", size=13)
    chip(s, I(4.95), I(4.35), I(4.2), I(2.15), "Locked split (shared)",
         f"{sc['train']:,} train · {sc['val']} validation · {sc['test']} test · {sc['ood']} out-of-distribution (W/L > 1.95), seed 42.",
         size=13)
    note(s, ["No public HFSS dataset of hybrid-slotted DGS antennas exists, so two verified public simulation datasets stand in.",
             "The patch sweep gives full S11 curves; the Mendeley set adds slots, gain and efficiency.",
             "Raw files are re-downloaded by script with checksums, so the data trail is reproducible.",
             "Module 2 uses the same locked split as Module 1, so test results refer to the same designs."])

    # ================================================================ 9 cleaning and noise removal
    s = D.slide("Stage 2 - Cleaning and noise removal", section="3 · Pipeline")
    bullets(s, I(0.6), I(1.5), I(4.3), I(4.9), [
        [("Column names and types: ", {"bold": True}), ("stripped, renamed, cast to numbers", {})],
        [("Corrupt entry: ", {"bold": True}), (f"{clean['total_eff_non_numeric']} truncated efficiency value set to missing", {})],
        [("Solver artefacts: ", {"bold": True}), (f"{prep['patch_positive_s11_designs']:,} curves rise ≤ 0.2 dB above 0 dB - documented, kept", {})],
        [("Physically impossible rows: ", {"bold": True}), (f"{clean['implausible_rows_flagged']} of {clean['rows_raw']:,} (efficiency > 1, gain > directivity, D > 20 dBi) removed from gain / efficiency", {})],
        [("Duplicates / missing: ", {"bold": True}), (f"{prep['patch_duplicate_parameter_rows']} duplicate designs, {prep['patch_missing_values']} missing values", {})],
        [("Curve → targets: ", {"bold": True}), ("the noisy S11 curve is reduced to 4 robust numbers", {})],
    ], size=14, space=6)
    pic(s, FIG / "s11_target_extraction.png", I(5.0), I(1.6), w=I(4.15))
    text(s, I(5.0), I(3.65), I(4.15), I(1.6), "The first matched resonance is used, not the deepest dip: the deepest dip "
         "(here near 7.8 GHz) is often a higher-order mode.", size=12, color=GREY)
    note(s, ["For numeric data, 'noise removal' means finding values that cannot be physical and handling them by a fixed, documented rule.",
             "Rows are flagged rather than silently deleted, so the decision can be audited.",
             "Reducing each 1,000-point curve to four engineering targets removes ripple and keeps what engineers care about."])

    # ================================================================ 10 input features
    s = D.slide("Inputs: the features the AI learns from", section="4 · Features")
    grid(s, I(0.6), I(1.5), CONTENT_W, [
        ["Feature (input)", "Unit", "Why it matters physically"],
        ["Patch length L", "mm", "sets the half-wavelength resonance → main driver of f_res"],
        ["Patch width W", "mm", "changes radiation resistance, bandwidth and gain"],
        ["Feed offset (from centre)", "mm", "sets input impedance → controls the S11 match"],
        ["Aspect ratio W/L", "-", "captures shape effects; defines the OOD hold-out"],
        ["Normalised feed position", "0–1", "feed offset relative to L/2: centre (0) to edge (1)"],
        ["Slot 1 / slot 2 width & length", "mm", "slotted antenna: lengthen current paths, add bands"],
        ["Substrate W, L, h; feed width", "mm", "dielectric volume and feed-line impedance"],
        ["Frequency", "GHz", "Mendeley outputs are given at 16 frequencies"],
        ["ViT image embedding (fusion only)", "384-d", "learned picture of the geometry from Module 1"],
    ], [I(3.0), I(0.9), I(4.65)], size=12, row_h=0.47, bold_first_col=True)
    note(s, ["These are the features in the machine-learning sense: the numbers the model receives.",
             "Patch models use 5 inputs; the slotted (Mendeley) models use 10 dimensions plus frequency.",
             "Engineered ratios (W/L, feed ratio) encode physics the trees would otherwise have to discover.",
             "The image embedding is used only in the fusion experiment."])

    # ================================================================ 11 vectorisation
    s = D.slide("Stage 3 - Feature engineering and vectorisation", section="3 · Pipeline")
    flow(s, I(0.6), I(1.55), CONTENT_W, I(0.95), ["Design record", "Features", "Scaled x ∈ R⁵", "Model"], [ICE, BLUE, NAVY, GREEN], size=12)
    flow(s, I(0.6), I(2.7), CONTENT_W, I(0.95), ["Image (Module 1)", "ViT-S/16", "e ∈ R³⁸⁴", "[e, x] ∈ R³⁸⁹"], [ICE, BLUE, NAVY, ACCENT], size=12)
    pic(s, FIG / "surrogate_comparison_importance.png", I(0.6), I(3.9), w=CONTENT_W)
    note(s, ["Vectorisation turns each design into a fixed-length list of numbers.",
             "Linear models and the MLP need standardised inputs (mean 0, SD 1, fitted on training data only); trees do not.",
             "For fusion, the 384 image numbers and 5 design numbers are joined into one 389-number vector.",
             "Right chart: permutation importance - every input matters, length most for resonance."])

    # ================================================================ 12 model building
    s = D.slide("Stage 4 - Model building and training", section="3 · Pipeline")
    algos = [("Random forest (selected)", "400 decision trees on bootstrap samples; prediction = average. Captures non-linear, "
                                           "interacting effects; robust on small data."),
             ("Gradient boosting", "Trees added one at a time, each fixing the previous errors (500 rounds, lr 0.05)."),
             ("Ridge regression", "Linear baseline with L2 penalty - shows how non-linear the physics is."),
             ("MLP (fusion)", "Small neural network on the 389-d fusion vector; size and L2 chosen on validation."),
             ("NSGA-II (search)", "Evolutionary multi-objective optimiser; uses the trained forests as a fast simulator.")]
    for i, (t, b) in enumerate(algos):
        col, rowi = i % 2, i // 2
        chip(s, I(0.6 + col * 4.35), I(1.5 + rowi * 1.68), I(4.2), I(1.55), t, b, size=12)
    chip(s, I(4.95), I(4.86), I(4.2), I(1.55), "Training protocol",
         "Fit on train only · choose the model on validation MAE · score the test split once · GroupKFold for Mendeley.", size=12,
         fill=RGBColor(0xEA, 0xF5, 0xEE))
    note(s, ["Several model families compete; the one with the lowest validation error wins - here the random forest for every target.",
             "The test split is used once, after the choice, so the reported accuracy is not tuned to it.",
             "GroupKFold keeps all 16 frequencies of a Mendeley design in the same fold, preventing leakage.",
             "NSGA-II is not trained: it searches using the trained surrogates."])

    # ================================================================ 13 output: patch surrogate
    s = D.slide("Output 1 - Patch surrogate accuracy", section="5 · Outputs")
    rows = [["Target", "Test R²", "Test MAE", "Mean-baseline MAE", "OOD R²"]]
    for k in pt:
        rows.append([f"{PATCH_TARGETS[k][0]} ({PATCH_TARGETS[k][1]})", f"{sel(k)['R2']:.2f}", f"{sel(k)['MAE']:.2f}",
                     f"{pt[k]['models']['mean_baseline']['test']['MAE']:.2f}", f"{sel(k, 'ood')['R2']:.2f}"])
    grid(s, I(0.6), I(1.5), CONTENT_W, rows, [I(3.05), I(1.15), I(1.3), I(1.85), I(1.2)], size=12, row_h=0.4, center_from=1)
    pic(s, FIG / "numerical_parity_patch.png", I(0.6), I(3.7), w=CONTENT_W)
    note(s, [f"Resonance is predicted well (R² {sel('f_res_ghz')['R2']:.2f}, error {sel('f_res_ghz')['MAE']:.2f} GHz) and "
             f"bandwidth well (R² {sel('bw10_mhz')['R2']:.2f}).",
             f"Matching depth (S11) is harder (R² {sel('s11_min_db')['R2']:.2f}) because it changes sharply with feed impedance.",
             "On wider, unseen patches (OOD) accuracy collapses - surrogates are only trustworthy inside their training range.",
             "Dots close to the red line = accurate predictions."])

    # ================================================================ 14 output: Mendeley
    s = D.slide("Output 2 - Slotted antenna: S11, gain and efficiency", section="5 · Outputs")
    rows = [["Target (random forest)", "R²", "MAE", "Frequency-only MAE"]]
    for t in md:
        rows.append([f"{MEND_TARGETS[t][0]} ({MEND_TARGETS[t][1]})", f"{md[t]['random_forest']['R2']:.2f}",
                     f"{md[t]['random_forest']['MAE']:.3f}", f"{md[t]['random_forest_frequency_only']['MAE']:.3f}"])
    grid(s, I(0.6), I(1.5), CONTENT_W, rows, [I(3.4), I(1.3), I(1.55), I(2.3)], size=13, row_h=0.42, center_from=1)
    pic(s, FIG / "numerical_parity_mendeley.png", I(0.6), I(3.45), w=CONTENT_W)
    note(s, ["On the slotted antenna the forests predict S11, gain and radiation efficiency from the 10 dimensions and frequency.",
             "Adding the slot and substrate dimensions roughly halves the error of a frequency-only model - the geometry matters.",
             "Scores are optimistic: the data vary one dimension at a time around one design (grouped 5-fold cross-validation)."])

    # ================================================================ 15 role of text
    s = D.slide("Stage 6 - How text plays its role", section="5 · Outputs")
    flow(s, I(0.6), I(1.5), CONTENT_W, I(0.95), ["Select", "Interpret", "Write", "Caveat"], [NAVY, BLUE, BLUE, ACCENT], size=12)
    grid(s, I(0.6), I(2.6), CONTENT_W, [
        ["Step", "What happens"],
        ["Content selection", "pick predicted f_res, S11, bandwidth and the simulated reference for the same design"],
        ["Semantic interpretation", "rules give meaning: 3.3–3.8 GHz → 'inside 5G NR n78'; ≤ −20 dB → 'High class'"],
        ["Template realisation", "fixed sentence patterns, so wording is consistent and every number is copied, not invented"],
    ], [I(2.4), I(6.15)], size=12, row_h=0.42, bold_first_col=True)
    card(s, I(0.6), I(4.45), CONTENT_W, I(1.65), fill=RGBColor(0xF4, 0xF6, 0xF8), line=EDGE)
    text(s, I(0.8), I(4.52), I(8.2), I(2.0), [[("Generated example (unedited)", {"bold": True, "size": 13, "color": BLUE})],
                                              [(test_s[1] if len(test_s) > 1 else test_s[0], {"size": 12})]], size=12, color=NAVY)
    note(s, ["Engineers read sentences faster than tables, so each prediction is also written as a short summary.",
             "This is data-to-text generation with rules and templates - deliberately not a large language model, which could "
             "invent values.",
             "Each summary puts prediction and simulation side by side and ends by asking for full-wave verification."])

    # ================================================================ 16 fusion
    s = D.slide("Output 3 - Multimodal fusion (numbers + images)", section="5 · Outputs")
    rows = [["Input to the MLP", "Features", "Val macro-F1", "Test macro-F1", "OOD macro-F1"]]
    for k, lab in [("numeric_only", "Numeric only"), ("image_only", "Image embedding only"), ("fusion_concat", "Fusion (both)")]:
        v = fu[k]
        rows.append([lab, v["n_features"], f"{v['val_macro_f1']:.3f}", f"{v['test']['macro_f1']:.3f}", f"{v['ood']['macro_f1']:.3f}"])
    grid(s, I(0.6), I(1.5), CONTENT_W, rows, [I(2.85), I(1.2), I(1.45), I(1.55), I(1.5)], size=13, row_h=0.42, center_from=1)
    pic(s, FIG / "fusion_confusion.png", I(0.6), I(3.35), w=CONTENT_W)
    note(s, [f"Task: predict the matching class (Poor / Acceptable / High). Fusion scored {fi:.3f}, below the image embedding "
             f"alone ({im:.3f}), so the pre-registered hypothesis H6 is not supported.",
             f"The image-only MLP beats Module 1's own ViT head ({prov['module1_vit_linear_head_test_macro_f1']:.3f}): "
             "the ViT features are better than its classifier suggested.",
             "Adding 5 numbers to 384 image numbers added redundancy rather than new information."])

    # ================================================================ 17 NSGA-II
    s = D.slide("Output 4 - AI-proposed designs for 5G NR n78", section="5 · Outputs")
    pic(s, FIG / "nsga2_pareto_n78.png", I(0.6), I(1.45), h=I(3.3))
    chip(s, I(5.65), I(1.5), I(3.5), I(2.3), "Search set-up",
         f"Variables: L, W/L, feed position. Goals: deepest match, widest band, smallest area. Constraint: predicted resonance "
         f"in {lo}–{hi} GHz. {opt['pop_size']} candidates × {opt['generations']} generations.", size=12)
    small, wide, deep = par.loc[par.area_mm2.idxmin()], par.loc[par.pred_bw10_mhz.idxmax()], par.loc[par.pred_s11_at_res_db.idxmin()]
    rows = [["Proposal", "L × W (mm)", "f_res (GHz)", "S11 (dB)", "BW (MHz)"]]
    for why, r in [("smallest", small), ("widest band", wide), ("deepest match", deep)]:
        rows.append([f"{r.proposal_id} ({why})", f"{r.length_mm:.1f} × {r.width_mm:.1f}", f"{r.pred_f_res_ghz:.2f}",
                     f"{r.pred_s11_at_res_db:.1f}", f"{r.pred_bw10_mhz:.0f}"])
    grid(s, I(0.6), I(4.95), CONTENT_W, rows, [I(2.9), I(1.6), I(1.35), I(1.3), I(1.4)], size=12, row_h=0.38, center_from=1)
    note(s, [f"NSGA-II found {opt['n_pareto']} trade-off designs, from {opt['pareto_area_range_mm2'][0]:.0f} to "
             f"{opt['pareto_area_range_mm2'][1]:.0f} mm².",
             "Each dot is a compromise: smaller area costs bandwidth or match depth.",
             f"All proposals sit close to simulated designs (median {opt['median_nearest_distance_std']:.2f} SD) - "
             "interpolations, not miracles.",
             "These are predictions only: NOT simulated. They are a shortlist for HFSS."])

    # ================================================================ 18 value for engineers
    s = D.slide("What this means for engineers", section="6 · Value")
    grid(s, I(0.6), I(1.5), CONTENT_W, [
        ["Aspect", "Conventional (full-wave only)", "With the AI surrogate (Module 2)"],
        ["Time per candidate", "minutes to hours of solver time (typical)", f"≈{tm['batch_ms_per_design_all_targets']:.0f} ms in a batch (measured)"],
        ["Design-space coverage", "a few dozen hand-picked runs", "thousands of candidates screened, Pareto trade-offs"],
        ["Insight", "engineer reads plots one by one", "feature importance + plain-language summaries"],
        ["Accuracy", "physics-exact within the model", "good for resonance / bandwidth, weaker for S11 depth"],
        ["Trust boundary", "valid everywhere it is meshed", "only inside the training range (OOD drops sharply)"],
        ["Role", "final verification", "screening and shortlisting before verification"],
    ], [I(2.0), I(3.15), I(3.4)], size=12, row_h=0.6, bold_first_col=True)
    note(s, ["AI changes where the engineer spends time: less waiting for sweeps, more judging a ranked shortlist.",
             "It complements, not replaces, HFSS - every promising design is still simulated and measured.",
             "The out-of-distribution test shows engineers exactly when not to trust the surrogate.",
             "Text summaries make results readable for non-specialists and reports."])

    # ================================================================ 19 outcomes and limitations
    s = D.slide("Outcomes and limitations", section="6 · Value")
    rows = [["ID", "Statement", "Outcome"]]
    for cid, stmt, verdict in CR:
        rows.append([cid, stmt, verdict.split(":")[0]])
    grid(s, I(0.6), I(1.5), CONTENT_W, rows, [I(0.7), I(6.05), I(1.8)], size=12, row_h=0.44)
    bullets(s, I(0.6), I(3.95), CONTENT_W, I(2.6), [
        "No HFSS: all evidence is openEMS or Mendeley simulation, no measurements",
        "Patch data have no slots / DGS; Mendeley varies one dimension at a time",
        "Surrogates do not extrapolate; S11 depth only moderately predicted",
        "Fusion: one embedding run, one seed; NSGA-II proposals unverified",
    ], size=14, space=4)
    note(s, ["E1-E3 are the planned evaluation criteria; H6 was pre-registered before any fusion result existed.",
             "Three criteria met, one hypothesis not supported - reported as found, not adjusted.",
             "The limitations define the next step: a proper HFSS hybrid-slotted DGS dataset."])

    # ================================================================ 20 conclusion (dark)
    s = D.slide("Conclusion and next steps", dark=True)
    cols = [("What was achieved", ["Working 7-stage numerical-text pipeline", "Accurate resonance and bandwidth surrogates",
                                   "Readable, traceable engineering summaries", f"{opt['n_pareto']} n78 design proposals"]),
            ("What it shows", ["AI screens designs in milliseconds", "Geometry features carry the physics", "ViT features help more than raw numbers",
                               "Trust ends at the training range"]),
            ("Next steps", ["Space-filling HFSS DGS sweep (PyAEDT)", "Uncertainty-aware surrogate", "Re-simulate the Pareto shortlist",
                            "Fabricate and measure the best"])]
    for i, (t, its) in enumerate(cols):
        x = I(0.6 + i * 4.1)
        card(s, x, I(1.55), I(3.85), I(3.4), fill=DARKCARD, line=None)
        text(s, x + I(0.2), I(1.67), I(3.5), I(0.4), t, size=18, color=WHITE, bold=True)
        bullets(s, x + I(0.2), I(2.15), I(3.5), I(2.75), its, size=15, color=WHITE)
    card(s, I(0.6), I(5.25), I(12.15), I(1.2), fill=WHITE, line=None)
    text(s, I(0.85), I(5.33), I(11.7), I(1.1), [
        [("Module 2 code, data, tests and outputs: ", {"bold": True}), (REPO_URL, {"color": BLUE})],
        [("Module 1 (Vision Transformer): ", {"bold": True}), (COMPANION_URL, {"color": BLUE})],
        [("Tests: ", {"bold": True}), (test_summary(), {})]], size=14)
    s.notes_slide.notes_text_frame.text = (
        "Module 2 shows that parameter-based AI surrogates can screen antenna designs in milliseconds, explain themselves in "
        "plain text, and propose candidates for a 5G band - with clear limits. The next step is the HFSS hybrid-slotted DGS dataset.")

    # ================================================================ 21 references
    s = D.slide("References", section="Sources")
    refs = ["LaBash et al. (2025) Rectangular patch antenna frequency-response dataset, arXiv:2505.18188 (MIT)",
            "Mihad, Islam & Sojib (2024) Antenna Parameters Dataset v2, Mendeley Data, doi:10.17632/3gxr2vvd9n.2 (CC BY 4.0)",
            "Balanis, C. A. (2016) Antenna Theory: Analysis and Design, 4th ed., Wiley",
            "3GPP TS 38.101-1 - NR user equipment radio transmission and reception, Range 1",
            "Breiman, L. (2001) Random forests, Machine Learning 45(1)",
            "Ke, G. et al. (2017) LightGBM: a highly efficient gradient boosting decision tree, NeurIPS",
            "Pedregosa, F. et al. (2011) Scikit-learn: machine learning in Python, JMLR 12",
            "Deb, K. et al. (2002) NSGA-II, IEEE Trans. Evolutionary Computation 6(2)",
            "Blank, J. & Deb, K. (2020) pymoo: multi-objective optimization in Python, IEEE Access 8",
            "Dosovitskiy, A. et al. (2021) An image is worth 16x16 words (ViT), ICLR",
            "Reiter, E. & Dale, R. (2000) Building Natural Language Generation Systems, Cambridge University Press"]
    bullets(s, I(0.6), I(1.5), CONTENT_W, I(5.2), refs, size=13, space=4)
    note(s, ["Datasets are cited with their licences, as their terms require.",
             "Reiter & Dale describe the data-to-text pipeline (content selection, realisation) used for the summaries.",
             "Full reference list and DOIs are in the Module 2 report."])

    assert D.n == TOTAL, D.n
    out = ROOT / "presentations"
    out.mkdir(exist_ok=True)
    D.prs.save(out / "module2_extended_presentation.pptx")
    print("extended slides written:", D.n)


if __name__ == "__main__":
    main()
