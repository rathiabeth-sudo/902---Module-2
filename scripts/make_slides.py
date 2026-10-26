"""Module 2 five-slide deck -> presentations/module2_presentation.pptx (numbers from executed results)."""
from __future__ import annotations

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

from deliverables_common import FIG, MEND_TARGETS, PATCH_TARGETS, REPO_URL, ROOT, criteria, load

NAVY = RGBColor(0x0B, 0x2A, 0x4A)
BLUE = RGBColor(0x2F, 0x6F, 0xAE)
ICE = RGBColor(0xEA, 0xF2, 0xFA)
EDGE = RGBColor(0xC9, 0xDB, 0xEE)
GREY = RGBColor(0x5F, 0x6B, 0x76)
ACCENT = RGBColor(0xE0, 0x7B, 0x39)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
SOFT = RGBColor(0xCF, 0xE2, 0xF3)
GREEN = RGBColor(0x1F, 0x6F, 0x2A)
FONT = "Calibri"
KICK = "MODULE 2 · NUMERICAL-TEXT SURROGATE, FUSION & OPTIMISATION"


def text(slide, x, y, w, h, runs, size=16, color=NAVY, bold=False, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, name=None):
    """runs: str or list of paragraphs; each paragraph is str or list of (text, {bold,color,size}) tuples."""
    tb = slide.shapes.add_textbox(x, y, w, h)
    if name:
        tb.name = name
    tf = tb.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0.05)
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        for t, o in ([(para, {})] if isinstance(para, str) else para):
            r = p.add_run()
            r.text = t
            r.font.name = FONT
            r.font.size = Pt(o.get("size", size))
            r.font.bold = o.get("bold", bold)
            r.font.color.rgb = o.get("color", color)
    return tb


def bullets(slide, x, y, w, h, items, size=15, color=NAVY, space=6):
    tb = slide.shapes.add_textbox(x, y, w, h)
    tf = tb.text_frame
    tf.word_wrap = True
    for i, it in enumerate(items):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.space_after = Pt(space)
        parts = it if isinstance(it, list) else [(it, {})]
        r0 = p.add_run()
        r0.text = "▪  "
        r0.font.size, r0.font.color.rgb, r0.font.name = Pt(size), BLUE, FONT
        for t, o in parts:
            r = p.add_run()
            r.text = t
            r.font.name = FONT
            r.font.size = Pt(o.get("size", size))
            r.font.bold = o.get("bold", False)
            r.font.color.rgb = o.get("color", color)
    return tb


def card(slide, x, y, w, h, fill=ICE, line=EDGE, name=None):
    s = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, x, y, w, h)
    s.adjustments[0] = 0.06
    s.fill.solid()
    s.fill.fore_color.rgb = fill
    if line is None:
        s.line.fill.background()
    else:
        s.line.color.rgb = line
        s.line.width = Pt(1)
    s.shadow.inherit = False
    if name:
        s.name = name
    return s


def header(slide, prs, title, num, dark=False):
    c = SOFT if dark else BLUE
    text(slide, Inches(0.6), Inches(0.35), Inches(10), Inches(0.35), KICK, size=12, color=c, bold=True)
    text(slide, Inches(0.6), Inches(0.68), Inches(12.1), Inches(0.8), title, size=32, color=WHITE if dark else NAVY, bold=True)
    text(slide, Inches(0.6), prs.slide_height - Inches(0.45), Inches(10.5), Inches(0.3),
         "Proof of concept on public simulation data (openEMS, Mendeley) · Ansys HFSS not run · proposals not simulated",
         size=10, color=SOFT if dark else GREY)
    text(slide, prs.slide_width - Inches(1.4), prs.slide_height - Inches(0.45), Inches(0.8), Inches(0.3), f"{num} / 5",
         size=10, color=SOFT if dark else GREY, align=PP_ALIGN.RIGHT)


def background(slide, prs, color):
    bg = slide.background.fill
    bg.solid()
    bg.fore_color.rgb = color


def stat(slide, x, y, w, big, label, color=NAVY, sub=GREY, size=40):
    text(slide, x, y, w, Inches(0.75), big, size=size, color=color, bold=True)
    text(slide, x, y + Inches(0.72), w, Inches(0.6), label, size=13, color=sub)


def table(slide, x, y, w, rows, col_w, size=14, bold_rows=(), row_h=0.38):
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
            run.font.bold = i == 0 or i in bold_rows
            run.font.color.rgb = WHITE if i == 0 else NAVY
            p.alignment = PP_ALIGN.LEFT if j == 0 else PP_ALIGN.CENTER
            c.fill.solid()
            c.fill.fore_color.rgb = NAVY if i == 0 else (ICE if i % 2 else WHITE)
            c.margin_top = c.margin_bottom = Emu(25000)
            c.vertical_anchor = MSO_ANCHOR.MIDDLE
    return t


def main():
    R = load()
    num, fu, opt, prep, clean, prov = R["num"], R["fu"], R["opt"], R["prep"], R["clean"], R["prov"]
    pt, md, sel = num["patch"], num["mendeley"], R["sel"]
    CR = criteria(R)
    sc = prep["patch_split_counts"]
    fi, im, nu = (fu[k]["test"]["macro_f1"] for k in ["fusion_concat", "image_only", "numeric_only"])
    DARKCARD = RGBColor(0x14, 0x3A, 0x62)

    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    blank = prs.slide_layouts[6]

    # ---------------------------------------------------------------- 1 problem and objective (dark)
    s = prs.slides.add_slide(blank)
    background(s, prs, NAVY)
    header(s, prs, "Can antenna parameters stand in for slow sweeps?", 1, dark=True)
    text(s, Inches(0.6), Inches(1.5), Inches(7.4), Inches(0.9),
         "Numerical-text surrogate modelling, multimodal fusion and NSGA-II optimisation for compact patch antennas (5G / 6G)",
         size=16, color=SOFT)
    card(s, Inches(0.6), Inches(2.45), Inches(7.4), Inches(4.3), fill=DARKCARD, line=None)
    text(s, Inches(0.85), Inches(2.6), Inches(7.0), Inches(0.4), "Problem, gap and objective", size=18, color=WHITE, bold=True)
    bullets(s, Inches(0.85), Inches(3.1), Inches(7.0), Inches(3.6), [
        "Every design iteration of a slotted / DGS patch needs a slow full-wave run (HFSS)",
        "A fast surrogate can screen thousands of candidates, if its errors are known",
        "Gap: surrogates rarely report out-of-range behaviour, or explain outputs in plain text",
        "Objective: predict resonance, S11, bandwidth, gain and efficiency; summarise them; fuse with ViT features; optimise for n78",
        "Scope: HFSS unavailable → proof of concept on open simulations",
    ], size=15, color=WHITE)
    card(s, Inches(8.3), Inches(1.5), Inches(4.45), Inches(5.25), fill=WHITE, line=None)
    text(s, Inches(8.55), Inches(1.65), Inches(4.0), Inches(0.4), "Hypothesis and criteria", size=18, color=NAVY, bold=True)
    bullets(s, Inches(8.55), Inches(2.15), Inches(4.0), Inches(3.0), [
        [("H6 ", {"bold": True}), ("(pre-registered): image + numeric fusion beats image-only", {})],
        [("E1 ", {"bold": True}), ("surrogate beats the mean baseline on every target", {})],
        [("E2 ", {"bold": True}), ("slot geometry adds to frequency (Mendeley)", {})],
        [("E3 ", {"bold": True}), ("NSGA-II finds feasible n78 designs", {})],
    ], size=15)
    card(s, Inches(8.55), Inches(4.75), Inches(3.95), Inches(1.4), fill=ICE, line=EDGE)
    text(s, Inches(8.7), Inches(4.82), Inches(3.7), Inches(1.65),
         [[("Real generated summary", {"bold": True, "size": 12})],
          "“Predicted first matched resonance 3.57 GHz, inside 5G NR n78 … Simulated reference 3.54 GHz … requires full-wave verification.”"],
         size=12, color=GREY)
    s.notes_slide.notes_text_frame.text = (
        "Module 2 is the numerical-text branch of the framework. It replaces the slow simulator by a fast surrogate for screening, "
        "writes short engineering summaries that only restate computed numbers, tests whether numbers add to Module 1's image "
        "features, and uses the surrogate in an NSGA-II search for the 5G n78 band. H6 was pre-registered with the Module 1 "
        "hypotheses; E1 to E3 are evaluation criteria from the analysis plan.")

    # ---------------------------------------------------------------- 2 data and preprocessing
    s = prs.slides.add_slide(blank)
    background(s, prs, WHITE)
    header(s, prs, "Two simulation datasets, targets extracted from S11", 2)
    for i, (big, lab) in enumerate([("2,051", "openEMS patch designs\nHugging Face · MIT"),
                                    ("103 × 16", "dual-slot designs × frequencies\nMendeley v2 · CC BY 4.0"),
                                    (str(clean["implausible_rows_flagged"]), "implausible solver rows\nflagged by a fixed rule"),
                                    ("70 / 15 / 15", f"{sc['train']:,} · {sc['val']} · {sc['test']} + {sc['ood']} OOD\nsplit shared with Module 1")]):
        x = Inches(0.6 + i * 3.1)
        card(s, x, Inches(1.6), Inches(2.85), Inches(1.55))
        stat(s, x + Inches(0.2), Inches(1.68), Inches(2.6), big, lab, size=36)
    text(s, Inches(0.6), Inches(3.4), Inches(5.6), Inches(0.4), "Preparation", size=17, bold=True)
    bullets(s, Inches(0.6), Inches(3.85), Inches(5.6), Inches(3.0), [
        [("Targets: ", {"bold": True}), ("first matched resonance, S11 min, S11 at resonance, −10 dB bandwidth", {})],
        [("Mendeley: ", {"bold": True}), ("S11, gain, radiation efficiency at 16 frequencies", {})],
        [("Cleaning: ", {"bold": True}), ("efficiency > 1, gain > directivity, D > 20 dBi → excluded from gain / efficiency", {})],
        [("Leakage control: ", {"bold": True}), ("locked manifests; GroupKFold keeps a design's frequencies together", {})],
    ], size=14)
    s.shapes.add_picture(str(FIG / "s11_target_extraction.png"), Inches(6.45), Inches(3.4), width=Inches(6.3))
    s.notes_slide.notes_text_frame.text = (
        "The patch data give full S11 curves, which are reduced to four targets. The first matched resonance is used because the "
        "deepest dip is often a higher-order mode, as in this example. The Mendeley dataset adds slots, substrate and gain and "
        "efficiency outputs, but 245 rows are physically impossible and were flagged by a documented rule. References: LaBash et "
        "al. 2025 (arXiv:2505.18188); Mihad, Islam and Sojib 2024 (doi:10.17632/3gxr2vvd9n.2).")

    # ---------------------------------------------------------------- 3 architecture
    s = prs.slides.add_slide(blank)
    background(s, prs, WHITE)
    header(s, prs, "Surrogate, text, fusion and NSGA-II in one pipeline", 3)
    s.shapes.add_picture(str(FIG / "module2_architecture.png"), Inches(0.6), Inches(1.5), width=Inches(9.2))
    card(s, Inches(10.05), Inches(1.5), Inches(2.7), Inches(4.75))
    text(s, Inches(10.2), Inches(1.6), Inches(2.45), Inches(0.4), "Key settings", size=16, bold=True)
    bullets(s, Inches(10.2), Inches(2.05), Inches(2.5), Inches(4.1), [
        "Random forest (400 trees) vs ridge vs gradient boosting",
        "Selected on validation MAE",
        "Template text: numbers only, never invented",
        "Fusion MLP: 384-d ViT + 5 numeric",
        f"NSGA-II: {opt['pop_size']} × {opt['generations']} gen, 3 objectives",
    ], size=14, space=4)
    text(s, Inches(0.6), Inches(6.35), Inches(12.1), Inches(0.6),
         [[("Input from Module 1: ", {"bold": True}), ("only the 384-d embedding per design (with SHA-256 provenance). Dashed boxes need HFSS.", {})]],
         size=14)
    s.notes_slide.notes_text_frame.text = (
        "Four candidate regressors are compared per target and the best on validation MAE is kept. A deterministic template "
        "turns predictions into a paragraph, so it cannot invent numbers. Fusion concatenates the ViT embedding from Module 1 with "
        "five numeric features. NSGA-II (Deb et al. 2002, pymoo) minimises predicted S11 and area and maximises bandwidth with "
        "the predicted resonance constrained to n78.")

    # ---------------------------------------------------------------- 4 results
    s = prs.slides.add_slide(blank)
    background(s, prs, WHITE)
    header(s, prs, "Resonance is easy, matching depth is hard", 4)
    rows = [["Target (random forest)", "Test R²", "OOD R²"]]
    for k in pt:
        rows.append([f"{PATCH_TARGETS[k][0]} ({PATCH_TARGETS[k][1]})", f"{sel(k)['R2']:.2f}", f"{sel(k, 'ood')['R2']:.2f}"])
    for t in md:
        rows.append([f"Mendeley {MEND_TARGETS[t][0]} (grouped CV)", f"{md[t]['random_forest']['R2']:.2f}", "–"])
    table(s, Inches(0.6), Inches(1.5), Inches(6.2), rows, [Inches(3.8), Inches(1.2), Inches(1.2)], size=13, row_h=0.34)
    card(s, Inches(0.6), Inches(4.65), Inches(6.2), Inches(1.65))
    bullets(s, Inches(0.8), Inches(4.72), Inches(5.9), Inches(1.9), [
        [("E1, E2 met: ", {"bold": True}), ("geometry halves the frequency-only error", {})],
        [("H6 not supported: ", {"bold": True}), (f"fusion {fi:.3f} < image-only {im:.3f} (numeric {nu:.3f})", {})],
        [("E3 met: ", {"bold": True}), (f"{opt['n_pareto']} n78 proposals, {opt['pareto_area_range_mm2'][0]:.0f}–{opt['pareto_area_range_mm2'][1]:.0f} mm², not simulated", {})],
        [("Caveat: ", {"bold": True}), ("surrogates fail outside the training range (OOD)", {})],
    ], size=14, space=3)
    s.shapes.add_picture(str(FIG / "numerical_parity_patch.png"), Inches(7.05), Inches(1.5), width=Inches(5.7))
    s.shapes.add_picture(str(FIG / "nsga2_pareto_n78.png"), Inches(8.15), Inches(3.15), height=Inches(3.45))
    s.notes_slide.notes_text_frame.text = (
        "All values come from saved metric files. Outcomes: " + "; ".join(f"{c[0]} {c[2]}" for c in CR) + ". Resonance follows "
        "patch length smoothly; matching depth depends sharply on feed impedance, so it is predicted only moderately. On the "
        "wider OOD patches the surrogates break down, which is why NSGA-II is bounded to the training ranges. The image-only MLP "
        f"({im:.3f}) beats Module 1's own ViT head ({prov['module1_vit_linear_head_test_macro_f1']:.3f}).")

    # ---------------------------------------------------------------- 5 conclusion (dark)
    s = prs.slides.add_slide(blank)
    background(s, prs, NAVY)
    header(s, prs, "A traceable surrogate pipeline, ready for HFSS data", 5, dark=True)
    cols = [("Contribution", [
        "Executed surrogate, text, fusion and NSGA-II pipeline",
        "Every summary number traceable to a model or simulation",
        "OOD test exposes where surrogates cannot be trusted",
        "Embeddings show Module 1's features are strong"]),
        ("Limitations", [
            "No slots / DGS in the patch data; Mendeley is one-at-a-time",
            "Simulation only; no HFSS, no measurement",
            "Matching-depth R² only about 0.5",
            "Proposals unverified and close to existing designs"]),
        ("Next: HFSS validation", [
            "Space-filling DGS sweep via PyAEDT",
            "Uncertainty-aware surrogate for NSGA-II",
            "Re-simulate proposals; active learning",
            "Fabricate and measure a shortlist"])]
    for i, (t, items) in enumerate(cols):
        x = Inches(0.6 + i * 4.1)
        card(s, x, Inches(1.6), Inches(3.85), Inches(3.45), fill=DARKCARD, line=None)
        text(s, x + Inches(0.2), Inches(1.72), Inches(3.5), Inches(0.4), t, size=18, color=WHITE, bold=True)
        bullets(s, x + Inches(0.2), Inches(2.2), Inches(3.5), Inches(2.8), items, size=15, color=WHITE)
    card(s, Inches(0.6), Inches(5.4), Inches(12.15), Inches(0.95), fill=WHITE, line=None)
    text(s, Inches(0.85), Inches(5.5), Inches(11.7), Inches(0.8), [
        [("Deliverables: ", {"bold": True}), ("code, configs, 10 passing tests, data and model cards, Word/PDF/LaTeX report, this deck, poster", {})],
        [("GitHub: ", {"bold": True}), (REPO_URL, {"color": BLUE})]], size=14)
    s.notes_slide.notes_text_frame.text = (
        "Module 2 shows that parameter-based surrogates are fast and accurate for resonance and bandwidth, weaker for matching "
        "depth, and unreliable outside their training range. The optimised designs are hypotheses for full-wave verification. "
        "References: Breiman (2001) random forests; Deb et al. (2002) NSGA-II; Blank and Deb (2020) pymoo; 3GPP TS 38.101-1.")

    out = ROOT / "presentations"
    out.mkdir(exist_ok=True)
    prs.save(out / "module2_presentation.pptx")
    print("slides written")


if __name__ == "__main__":
    main()
