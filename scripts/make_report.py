"""Module 2 project report (submission version) -> reports/module2_report.docx.

Format required by the brief: about 2,000 words of body text, Times New Roman 12 pt, double-spaced, 1-inch margins.
The full-detail version with appendices is built by make_extended_report.py.

The prose is written by hand, but every number in it is checked against results/metrics at build time
(see check_numbers), so the report cannot drift away from the executed results.

    python scripts/make_report.py
    powershell -File scripts\\docx_to_pdf.ps1 reports\\module2_report.docx
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

sys.path.insert(0, str(Path(__file__).resolve().parent))
from deliverables_common import COMPANION_URL, DEMO_URL, REPO_URL, ROOT, TITLE, load  # noqa: E402

FONT = "Times New Roman"
LINK_RE = re.compile(r"(https?://[^\s)]*[^\s).,;:])")

HEADER = [
    ("Student name", "Ms. Rathi Devadhas"),
    ("Student ID", "1737089"),
    ("Programme", "Master of Applied Artificial Intelligence"),
    ("Course", "Applied AI Research Workshop, Module 2"),
    ("Code repository", REPO_URL),
    ("Interactive demo", DEMO_URL),
]

# ("h", heading) | ("p", paragraph) | ("table",) ; the body word count covers "h" and "p" only
BODY = [
    ("h", "Abstract"),
    ("p", "Designing a compact patch antenna usually means running one full-wave simulation after another, and each run can "
          "take minutes to hours. In this project I built the numerical half of a two-module framework: models that predict "
          "antenna performance from a handful of dimensions, a short text summary for every prediction, a test of whether these "
          "numbers add anything to the image features from Module 1, and a multi-objective search for 5G NR n78 designs. Ansys "
          "HFSS was not available, so everything was trained and tested on two public simulation datasets. A random forest "
          "predicted resonance with R² = 0.89 and bandwidth with R² = 0.83, but matching depth only with R² = 0.54. Combining "
          "numbers with image features did not help (macro-F1 0.737 against 0.775 for images alone). The 100 designs proposed "
          "by the optimiser are predictions that still need full-wave checks. An interactive demo of the models is available "
          f"online at {DEMO_URL}."),

    ("h", "1. Introduction"),
    ("p", "Patch antennas for 5G and future 6G devices have to be small, well matched and tuned to the right band. Cutting slots "
          "into the patch or etching a defected ground structure (DGS) gives the designer more freedom, but it also makes the "
          "response sensitive to tiny changes in geometry, so a parameter sweep in a full-wave solver such as HFSS can run for "
          "days [4]. The wider research framework tackles this in two parts. Module 1, in its own repository, is a Vision "
          "Transformer [1] that classifies images of antenna layouts. Module 2, which this report covers, works with numbers "
          "instead of pictures."),
    ("p", "My starting question was simple: if I only know an antenna's dimensions, how well can I predict what the simulator "
          "would say? From there I wanted to find out whether those numbers improve on the image features from Module 1, and "
          "whether a fast surrogate is good enough to steer an optimiser towards sensible designs for the n78 band "
          "(3.3–3.8 GHz). I also set myself one rule for the whole project. Every number and every sentence the system "
          "produces has to be traceable to a model output or a simulated value. A tool that sounds confident but invents "
          "results would be worse than useless to an antenna engineer."),

    ("h", "2. Data and Preparation"),
    ("p", "I searched Hugging Face, Kaggle, Mendeley Data, IEEE DataPort, GitHub and Zenodo for usable data. Of eleven "
          "candidates, only two met my requirements: clear geometric inputs, simulated electromagnetic outputs, a licence that "
          "allows reuse, and enough designs to keep some aside for testing. I could not find any public HFSS sweep of "
          "hybrid-slotted DGS antennas, and that gap shapes everything that follows."),
    ("p", "The first dataset holds 2,051 coax-fed rectangular patches simulated in openEMS [10]. Each design is described by "
          "its length, width and feed offset, and comes with a 1,000-point S11 curve from 1 to 10 GHz [2]. The second is the "
          "Mendeley Antenna Parameters Dataset: 103 dual-slot patch designs, each simulated at 16 frequencies, with S11, gain "
          "and efficiency [3]."),
    ("p", "Neither dataset was ready to use as it came. For the patch data I reduced each S11 curve to four targets: the first "
          "matched resonance (the lowest-frequency dip below −10 dB), the minimum S11, the S11 at that resonance and the "
          "−10 dB bandwidth. I chose the first matched resonance on purpose, because the deepest dip is often a higher-order "
          "mode; a 22.5 mm patch, for example, has its deepest dip at 9.6 GHz. The Mendeley data needed more work. One "
          "efficiency value was a truncated text string, and 245 of the 1,648 rows were physically impossible, with "
          "efficiencies above 1 or gain higher than directivity. I flagged these rows with a written rule instead of tuning a "
          "filter until the numbers looked good. They stayed in for S11, which they do not affect, and were left out of the "
          "gain and efficiency targets."),
    ("p", "To keep the comparison with Module 1 fair, I reused its locked split: 1,220 training, 262 validation and 262 test "
          "designs, plus the 307 widest patches (W/L above 1.95) held back as an out-of-distribution (OOD) set. For the "
          "Mendeley data I used five-fold cross-validation grouped by design, so the 16 frequencies of one antenna never ended "
          "up on both sides of a split."),

    ("h", "3. Methods"),
    ("p", "For each target I trained four models with scikit-learn [7]: a mean predictor as a floor, ridge regression, "
          "histogram gradient boosting and a random forest of 400 trees [6]. The model with the lowest validation error was "
          "kept, and the test set was scored only once, at the very end. I expected the tree models to win because the physics "
          "is non-linear. Resonance depends mostly on length, while matching depends on where the feed sits relative to the "
          "edge of the patch. The inputs were length, width, feed offset, the W/L ratio and a normalised feed position."),
    ("p", "The text part is deliberately low-tech. Instead of a language model, a template reads the predictions and the "
          "simulated reference for the same design, places the resonance in a 3GPP band [5], applies the matching rule and "
          "writes one paragraph. It cannot make up a number because it only copies computed values, and every summary ends by "
          "saying that the design still needs full-wave verification."),
    ("p", "For the fusion experiment I joined the 384-dimensional embedding exported by Module 1 with the five numerical "
          "features and trained a small neural network to predict a three-level matching class (Poor, Acceptable or High). I "
          "compared it against the same network given only the embedding or only the numbers. Before any results existed, I "
          "registered hypothesis H6: fusion would beat the image-only model."),
    ("p", "Finally, I used NSGA-II [8] from the pymoo library [9] to search over length, W/L and feed position. The search "
          "tried to deepen the predicted match, widen the bandwidth and shrink the patch area, while keeping the predicted "
          "resonance inside n78. It ran with 100 candidates for 80 generations. I then compared each final design with its "
          "nearest simulated neighbour to see how far the surrogate was being pushed beyond its data."),

    ("h", "4. Results"),
    ("p", "Table 1 summarises the patch surrogate. The random forest was selected for all four targets and beat the mean "
          "baseline every time. Resonance was predicted well, with an average error of 0.35 GHz, and so was bandwidth, at "
          "18 MHz. Matching depth was much harder (R² = 0.54). That makes physical sense. Resonance shifts smoothly as the patch "
          "gets longer, but the depth of the S11 dip depends on how close the input impedance gets to 50 Ω, and a small move of "
          "the feed can change it by many decibels."),
    ("table",),
    ("p", "The OOD results were the most sobering part of the project. On the wide patches the model had never seen, R² for "
          "resonance dropped to 0.44, and for bandwidth and S11 at resonance it fell below zero. Tree models simply cannot "
          "extrapolate past their training range. This changed how I set up the rest of the work: I limited the optimiser to "
          "the training ranges and checked every proposal against real simulated designs."),
    ("p", "On the slotted Mendeley antenna the forests reached R² = 0.86 for S11, 0.99 for gain and 0.97 for radiation "
          "efficiency. Adding the ten geometry variables roughly halved the error of a model that only knew the frequency "
          "(0.53 dB against 1.09 dB for S11). I would not read too much into the very high gain score, though. The "
          "frequency-only model already reaches R² = 0.98, and because the dataset changes one dimension at a time around a "
          "single nominal design, the test folds still contain near-identical antennas."),
    ("p", "Fusion did not work out the way I had hoped. The combined model scored a test macro-F1 of 0.737, below the "
          "image-only model at 0.775 and above the numbers-only model at 0.716, so H6 is not supported. The more interesting "
          "finding was the image-only score itself. Module 1's own ViT classifier reached only 0.581, so a simple network on "
          "the same embeddings did far better. This supports Module 1's diagnosis that its classifier head underfitted while "
          "the representation underneath had already learned the geometry. Adding five numbers to 384 image dimensions mostly "
          "gave a small training set more redundant inputs to deal with."),
    ("p", "NSGA-II returned 100 proposals covering 299–2,754 mm², with predicted bandwidths of 51–103 MHz. They fell into two "
          "groups that make physical sense: 71 compact patches about 19–23 mm long that use the fundamental mode, and 29 larger "
          "patches about 39–41 mm long whose first matched resonance is a higher-order mode, trading size for a deeper match. "
          "Their median distance to the nearest simulated design was only 0.08 standard deviations, so they are "
          "interpolations rather than discoveries. The widest predicted bandwidth beats the best simulated n78 design (99 MHz) "
          "by less than the model's own bandwidth error, so I cannot claim that any proposal is a real improvement. For a dense "
          "sweep of a simple patch, that is what I expected. The approach should pay off when the design space is much larger "
          "than what has been simulated, as it will be with a DGS sweep."),
    ("p", "The summaries did what I wanted. For test design P1768 the generator reported a predicted resonance of 3.57 GHz, "
          "inside n78, next to the simulated 3.54 GHz. Putting the prediction and the reference side by side lets a reader see "
          "the error straight away. The weakness is that a template can restate numbers but cannot explain why a design "
          "behaves the way it does."),

    ("h", "5. Interactive Demo"),
    ("p", f"To make the models easier to explore, I built a browser demo, available at {DEMO_URL}. It uses the same two "
          "datasets and the same trained random forests as this report. In the design explorer you move sliders for length, "
          "W/L and feed position and see the predicted resonance, S11 and bandwidth, the matching class, a check against the "
          "n78, n77 or n79 band, a generated engineering summary and the simulated S11 curve of the nearest real design. Other "
          "tabs compare predictions with openEMS on the 262 test designs, plot the 100 NSGA-II proposals, show the Mendeley S11 "
          "and gain curves and list the model scores. Because the page has no server behind it, I pre-computed the forest's "
          "predictions on a grid of 84,525 designs. The script that builds this grid is in the repository."),

    ("h", "6. Limitations and Responsible Use"),
    ("p", "The biggest limitation is the topology gap. The patch data has no slots or DGS, and the Mendeley data varies one "
          "dimension at a time, so these surrogates will not transfer directly to hybrid-slotted DGS antennas. All targets come "
          "from openEMS or the Mendeley authors' solver rather than HFSS, and nothing was fabricated or measured. The −20 dB "
          "boundary for the High class is my own assumption and needs confirmation from an antenna engineer. The fusion test "
          "also used only one embedding run and one seed."),
    ("p", "Both datasets are public under MIT and CC BY 4.0 licences, contain no personal data, and are cited as their terms "
          "require. A script downloads the raw files and checks their checksums, the settings live in one configuration file "
          "with fixed seeds, and ten automated tests cover the target extraction, the split, the cleaning rule and the "
          "optimiser constraints. All ten pass. Every prediction, summary and proposal is labelled as a screening result that "
          "needs full-wave verification."),

    ("h", "7. Conclusion"),
    ("p", "Module 2 shows that a few antenna dimensions are enough to predict simulated resonance and bandwidth well, and "
          "matching depth only moderately. On a slotted patch, adding the geometry roughly halves the error of a frequency-only "
          "model. Combining numbers with ViT embeddings did not beat the embeddings alone, but it did reveal that Module 1's "
          "representation is stronger than its own classifier suggested. The optimiser produced sensible n78 candidates, all "
          "close to existing designs and all unverified. The main lesson for the full HFSS study is that a surrogate is only as "
          "good as its coverage. The DGS sweep should be space-filling rather than one-at-a-time, the surrogate should report "
          "its own uncertainty, and every optimised design should be treated as a hypothesis to test in the simulator. My next "
          "steps are to generate that sweep with PyAEDT, add uncertainty estimates, and feed re-simulated proposals back into "
          "training."),
]

AVAILABILITY = [
    ("Code, data, tests and results", REPO_URL),
    ("Interactive demo", DEMO_URL),
    ("Module 1 (Vision Transformer)", COMPANION_URL),
]

REFERENCES = [
    "A. Dosovitskiy et al., “An image is worth 16x16 words: Transformers for image recognition at scale,” in Proc. ICLR, 2021.",
    "B. LaBash et al., “Improving generative inverse design of rectangular patch antennas with test time optimization,” "
    "arXiv:2505.18188, 2025. Dataset: huggingface.co/datasets/becklabash/rectangular-patch-antenna-freq-response (MIT).",
    "M. F. H. Mihad, M. M. Islam and F. H. Sojib, “Antenna Parameters Dataset,” Mendeley Data, v2, 2024, "
    "doi:10.17632/3gxr2vvd9n.2 (CC BY 4.0).",
    "C. A. Balanis, Antenna Theory: Analysis and Design, 4th ed. Hoboken, NJ, USA: Wiley, 2016.",
    "3GPP, “NR; User Equipment (UE) radio transmission and reception; Part 1: Range 1 Standalone,” TS 38.101-1.",
    "L. Breiman, “Random forests,” Machine Learning, vol. 45, no. 1, pp. 5–32, 2001.",
    "F. Pedregosa et al., “Scikit-learn: Machine learning in Python,” J. Mach. Learn. Res., vol. 12, pp. 2825–2830, 2011.",
    "K. Deb, A. Pratap, S. Agarwal and T. Meyarivan, “A fast and elitist multiobjective genetic algorithm: NSGA-II,” "
    "IEEE Trans. Evol. Comput., vol. 6, no. 2, pp. 182–197, 2002.",
    "J. Blank and K. Deb, “pymoo: Multi-objective optimization in Python,” IEEE Access, vol. 8, pp. 89497–89509, 2020.",
    "T. Liebig et al., openEMS: a free and open electromagnetic field solver. [Online]. Available: https://openems.de",
]


# ------------------------------------------------------------------ number check
def check_numbers(R) -> list[list[str]]:
    """Fail the build if a number quoted in the prose no longer matches results/metrics. Returns Table 1 rows."""
    pt, md, fu, par = R["num"]["patch"], R["num"]["mendeley"], R["fu"], R["pareto"]
    s = R["sel"]
    expect = {
        "0.89": s("f_res_ghz")["R2"], "0.83": s("bw10_mhz")["R2"], "0.54": s("s11_min_db")["R2"],
        "0.35": s("f_res_ghz")["MAE"], "18": s("bw10_mhz")["MAE"], "0.44": s("f_res_ghz", "ood")["R2"],
        "0.86": md["S11_dB"]["random_forest"]["R2"], "0.99": md["Gain"]["random_forest"]["R2"],
        "0.97": md["Rad_eff"]["random_forest"]["R2"], "0.53": md["S11_dB"]["random_forest"]["MAE"],
        "1.09": md["S11_dB"]["random_forest_frequency_only"]["MAE"],
        "0.98": md["Gain"]["random_forest_frequency_only"]["R2"],
        "0.737": fu["fusion_concat"]["test"]["macro_f1"], "0.775": fu["image_only"]["test"]["macro_f1"],
        "0.716": fu["numeric_only"]["test"]["macro_f1"], "0.08": par.nearest_distance_std.median(),
        "299": par.area_mm2.min(), "2754": par.area_mm2.max(), "51": par.pred_bw10_mhz.min(), "103": par.pred_bw10_mhz.max(),
    }
    for txt, val in expect.items():
        nd = len(txt.split(".")[1]) if "." in txt else 0
        assert f"{val:.{nd}f}" == txt, f"report says {txt}, metrics say {val}"
    assert len(par) == 100 and (par.length_mm < 30).sum() == 71
    assert all(s(k)["MAE"] < pt[k]["models"]["mean_baseline"]["test"]["MAE"] for k in pt)
    assert s("bw10_mhz", "ood")["R2"] < 0 and s("s11_at_res_db", "ood")["R2"] < 0
    names = {"f_res_ghz": ("First matched resonance", "GHz", 2), "bw10_mhz": ("−10 dB bandwidth", "MHz", 1),
             "s11_min_db": ("Minimum S11", "dB", 1), "s11_at_res_db": ("S11 at resonance", "dB", 1)}
    rows = []
    for k, (n, u, d) in names.items():
        t, o = s(k), s(k, "ood")
        rows.append([n, f"{t['R2']:.2f}", f"{t['MAE']:.{d}f} {u}", f"{pt[k]['models']['mean_baseline']['test']['MAE']:.{d}f} {u}",
                     f"{o['R2']:.2f}"])
    return rows


# ------------------------------------------------------------------ docx helpers
def _font(run, size=12, bold=False, italic=False, color=None):
    run.font.name = FONT
    run._element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    run.font.size = Pt(size)
    run.bold, run.italic = bold, italic
    if color:
        run.font.color.rgb = color


def _link(paragraph, url):
    rid = paragraph.part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
                                   is_external=True)
    h = OxmlElement("w:hyperlink")
    h.set(qn("r:id"), rid)
    r = OxmlElement("w:r")
    rpr = OxmlElement("w:rPr")
    fonts = OxmlElement("w:rFonts")
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(a), FONT)
    rpr.append(fonts)
    c = OxmlElement("w:color")
    c.set(qn("w:val"), "1F4E99")
    rpr.append(c)
    u = OxmlElement("w:u")
    u.set(qn("w:val"), "single")
    rpr.append(u)
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "24")
    rpr.append(sz)
    r.append(rpr)
    t = OxmlElement("w:t")
    t.text = url
    t.set(qn("xml:space"), "preserve")
    r.append(t)
    h.append(r)
    paragraph._p.append(h)


def _text(paragraph, text, **kw):
    """Write text, turning bare URLs into clickable links."""
    for part in LINK_RE.split(text):
        if not part:
            continue
        if LINK_RE.fullmatch(part):
            _link(paragraph, part)
        else:
            _font(paragraph.add_run(part), **kw)


def _spacing(p, double=True, first_indent=True, after=0):
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.DOUBLE if double else WD_LINE_SPACING.SINGLE
    pf.space_before, pf.space_after = Pt(0), Pt(after)
    pf.first_line_indent = Inches(0.5) if first_indent else None


def _page_number(section):
    p = section.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run()
    for tag, val in [("begin", None), (None, "PAGE"), ("separate", None), ("end", None)]:
        if tag:
            el = OxmlElement("w:fldChar")
            el.set(qn("w:fldCharType"), tag)
        else:
            el = OxmlElement("w:instrText")
            el.set(qn("xml:space"), "preserve")
            el.text = val
        r._r.append(el)
    _font(r)


def build_docx(table_rows, out: Path) -> int:
    doc = Document()
    st = doc.styles["Normal"]
    st.font.name, st.font.size = FONT, Pt(12)
    st.element.rPr.rFonts.set(qn("w:eastAsia"), FONT)
    sec = doc.sections[0]
    sec.page_width, sec.page_height = Inches(8.5), Inches(11)
    for side in ("left_margin", "right_margin", "top_margin", "bottom_margin"):
        setattr(sec, side, Inches(1))
    _page_number(sec)
    doc.core_properties.author = "Rathi Devadhas"
    doc.core_properties.title = TITLE

    # title block (double-spaced, centred)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(p, first_indent=False)
    _font(p.add_run(TITLE), bold=True)
    for k, v in HEADER:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        _spacing(p, first_indent=False)
        _font(p.add_run(f"{k}: "), bold=True)
        _text(p, v)

    words = 0
    for block in BODY:
        if block[0] == "h":
            p = doc.add_paragraph()
            _spacing(p, first_indent=False)
            if block[1] == "Abstract":
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            _font(p.add_run(block[1]), bold=True)
            words += len(block[1].split())
        elif block[0] == "p":
            p = doc.add_paragraph()
            _spacing(p)
            _text(p, block[1])
            words += len(block[1].split())
        else:  # Table 1, single-spaced inside the cells
            cap = doc.add_paragraph()
            _spacing(cap, first_indent=False)
            cap.paragraph_format.keep_with_next = True
            _font(cap.add_run("Table 1. "), bold=True)
            _font(cap.add_run("Patch surrogate (random forest) on the locked test split (262 designs) and the OOD hold-out "
                              "(307 designs)."), italic=True)
            head = ["Target", "Test R²", "Test MAE", "Mean-baseline MAE", "OOD R²"]
            t = doc.add_table(rows=1, cols=5)
            t.style = "Table Grid"
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for row_cells, vals, bold in [(t.rows[0].cells, head, True)] + [(None, r, False) for r in table_rows]:
                cells = row_cells or t.add_row().cells
                for i, (c, v) in enumerate(zip(cells, vals)):
                    cp = c.paragraphs[0]
                    _spacing(cp, double=False, first_indent=False)
                    cp.alignment = WD_ALIGN_PARAGRAPH.LEFT if i == 0 else WD_ALIGN_PARAGRAPH.CENTER
                    cp.paragraph_format.keep_with_next = True  # keep caption and table on one page
                    _font(cp.add_run(v.replace("-", "−") if v[:1] == "-" else v), bold=bold)
            for row in t.rows:
                for i, w in enumerate([2.1, 0.9, 1.25, 1.65, 0.9]):
                    row.cells[i].width = Inches(w)
            gap = doc.add_paragraph()
            _spacing(gap, double=False, first_indent=False)

    # availability and references (not counted)
    p = doc.add_paragraph()
    _spacing(p, first_indent=False)
    _font(p.add_run("Data, Code and Demo Availability"), bold=True)
    for k, v in AVAILABILITY:
        p = doc.add_paragraph()
        _spacing(p, first_indent=False)
        _font(p.add_run(f"{k}: "))
        _text(p, v)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _spacing(p, first_indent=False)
    _font(p.add_run("References"), bold=True)
    for i, ref in enumerate(REFERENCES, 1):
        p = doc.add_paragraph()
        _spacing(p, first_indent=False)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        _text(p, f"[{i}]\t{ref}")
    doc.save(out)
    return words


def main():
    R = load()
    rows = check_numbers(R)
    out = ROOT / "reports" / "module2_report.docx"
    out.parent.mkdir(exist_ok=True)
    n = build_docx(rows, out)
    print(f"report written: {out.name}, body text {n} words (title block, table, availability and references excluded)")


if __name__ == "__main__":
    main()
