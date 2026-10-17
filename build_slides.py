"""Builds slides.pptx (8 slides) from results/summary.json. Run after the notebook:
    python build_slides.py
"""

import json

from pptx import Presentation
from pptx.chart.data import CategoryChartData, XyChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION, XL_MARKER_STYLE
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

S = json.load(open("results/summary.json"))
CORE = {r["p"]: r for r in S["core"]}
MEAS = {int(r["encoding"].split("p=")[1]): r for r in S["rows"] if r["n"] == 4 and "compact" in r["encoding"]
        and r["shots"] == 1000}
SCALE = S["scale"]

TEAL, AMBER, INK, GREY, LIGHT, WHITE = (RGBColor.from_string(h) for h in
                                        ("0E9488", "C2772A", "1B2433", "5B6575", "E8F4F3", "FFFFFF"))
DARK = RGBColor.from_string("13202B")
CUBE = [RGBColor.from_string(h) for h in ("D64545", "2FA95F", "3B82F6", "E8B400")]
HEAD, BODY = "Cambria", "Calibri"

prs = Presentation()
prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
BLANK = prs.slide_layouts[6]


def bg(slide, colour):
    f = slide.background.fill
    f.solid()
    f.fore_color.rgb = colour


def text(slide, x, y, w, h, runs, size=16, colour=INK, font=BODY, bold=False, align=PP_ALIGN.LEFT,
         anchor=MSO_ANCHOR.TOP, space=6):
    """runs: a string, or a list of paragraphs; each paragraph a string or list of (text, {opts})."""
    box = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = box.text_frame
    tf.word_wrap = True
    tf.vertical_anchor = anchor
    tf.margin_left = tf.margin_right = Inches(0)
    paras = runs if isinstance(runs, list) else [runs]
    for i, para in enumerate(paras):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.space_after = Pt(space)
        for chunk in (para if isinstance(para, list) else [(para, {})]):
            t, o = chunk if isinstance(chunk, tuple) else (chunk, {})
            r = p.add_run()
            r.text = t
            r.font.size = Pt(o.get("size", size))
            r.font.bold = o.get("bold", bold)
            r.font.italic = o.get("italic", False)
            r.font.name = o.get("font", font)
            r.font.color.rgb = o.get("colour", colour)
    return box


def tower(slide, x, y, s=0.22):
    """The motif: a mini 4-cube tower in the four puzzle colours."""
    for i, c in enumerate(CUBE):
        sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y + i * (s + 0.04)),
                                    Inches(s), Inches(s))
        sh.fill.solid()
        sh.fill.fore_color.rgb = c
        sh.line.fill.background()


def title(slide, t, sub=None):
    tower(slide, 0.6, 0.45, 0.17)
    text(slide, 1.05, 0.38, 11.5, 0.8, t, size=34, font=HEAD, bold=True)
    if sub:
        text(slide, 1.05, 1.15, 11.5, 0.5, sub, size=16, colour=GREY)


def card(slide, x, y, w, h, fill=LIGHT):
    sh = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(w), Inches(h))
    sh.adjustments[0] = 0.06
    sh.fill.solid()
    sh.fill.fore_color.rgb = fill
    sh.line.fill.background()
    return sh


def stat(slide, x, y, w, big, label, colour=TEAL):
    text(slide, x, y, w, 0.9, big, size=44, font=HEAD, bold=True, colour=colour)
    text(slide, x, y + 0.85, w, 0.7, label, size=14, colour=GREY)


def style_chart(chart, ytitle=None, xtitle=None):
    chart.font.size = Pt(12)
    chart.font.name = BODY
    chart.font.color.rgb = GREY
    va = chart.value_axis
    va.has_major_gridlines = True
    va.major_gridlines.format.line.color.rgb = RGBColor.from_string("DDDDDD")
    va.format.line.fill.background()
    for ax, t in ((va, ytitle), (chart.category_axis, xtitle)):
        if t:
            ax.has_title = True
            ax.axis_title.text_frame.text = t
            r = ax.axis_title.text_frame.paragraphs[0].runs[0]
            r.font.size, r.font.bold, r.font.color.rgb = Pt(12), False, GREY


def pct(x):
    return f"{100 * x:.0f}%" if x >= 0.1 else (f"{100 * x:.1f}%" if x >= 0.001 else f"{100 * x:.2g}%")


# ---------------------------------------------------------------- 1 title
s = prs.slides.add_slide(BLANK)
bg(s, DARK)
tower(s, 0.9, 2.0, 0.42)
text(s, 1.8, 1.85, 10.5, 1.2, "Instant Insanity on 12 qubits", size=48, font=HEAD, bold=True, colour=WHITE)
text(s, 1.8, 3.0, 10.5, 1.0, "A compact encoding and constrained QAOA, checked against brute force at every step",
     size=20, colour=RGBColor.from_string("B8C4CC"))
text(s, 1.8, 4.6, 10.5, 1.2, ["Team: [add names]",
                              "Qiskit Fall Fest CT 2026 · qBraid challenge · warm-up, core and bonus (N = 4 to 8)"],
     size=16, colour=RGBColor.from_string("B8C4CC"))
s.notes_slide.notes_text_frame.text = "Speaker 1: introduce the team and the one-line story: 3 qubits per cube, a mixer that only allows legal moves, and classical checks everywhere."

# ---------------------------------------------------------------- 2 problem
s = prs.slides.add_slide(BLANK)
title(s, "The puzzle: 8 good towers out of 331,776",
      "Stack 4 cubes so every side shows red, green, blue and yellow exactly once")
stat(s, 0.8, 1.9, 3.6, "331,776", "ways to stack 4 cubes (24 orientations each)")
stat(s, 0.8, 3.5, 3.6, "8", "solved: one tower seen from 8 angles", AMBER)
stat(s, 0.8, 5.1, 3.6, "0.14 s", "for classical brute force to find them", GREY)
card(s, 4.9, 1.9, 7.7, 4.3)
text(s, 5.25, 2.15, 7.1, 4.5, [
    [("Graph view", {"bold": True, "size": 20, "font": HEAD})],
    "Colours are nodes; each cube's 3 opposite-face pairs are edges.",
    "Front/back picks must touch every colour exactly twice (a 2-factor). So must the left/right picks, "
    "using a different pair of the same cube.",
    [("So each cube has only ", {}), ("6 choices", {"bold": True}),
     (": an ordered pair (front/back pair, left/right pair).", {})],
    [("6⁴ = 1,296 cases, of which ", {}), ("2", {"bold": True}), (" solve it (the tower and its quarter turn).", {})],
    [("The general N-cube problem is NP-complete. We do not claim a speedup.", {"italic": True, "colour": GREY})],
], size=17, space=10)
s.notes_slide.notes_text_frame.text = "Speaker 1: why it's hard by hand, why it's easy for a computer at N=4, and how the graph view shrinks it to 6 choices per cube."

# ---------------------------------------------------------------- 3 encoding
s = prs.slides.add_slide(BLANK)
title(s, "Encoding: 6 choices fit in 3 qubits", "12 qubits for 4 cubes, half the starter's 24-qubit one-hot encoding")
rows = [("code", "bits", "front/back", "left/right")] + [
    (str(k), format(k, "03b"), str(fb), str(lr)) for k, (fb, lr) in
    enumerate([(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)])] + [("6, 7", "11x", "unused", "never reached")]
tbl = s.shapes.add_table(len(rows), 4, Inches(0.8), Inches(1.9), Inches(5.6), Inches(4.6)).table
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.text = v
        p = cell.text_frame.paragraphs[0]
        p.runs[0].font.size = Pt(15)
        p.runs[0].font.name = BODY
        p.runs[0].font.bold = i == 0
        p.runs[0].font.color.rgb = WHITE if i == 0 else INK
        cell.fill.solid()
        cell.fill.fore_color.rgb = TEAL if i == 0 else (LIGHT if i % 2 else WHITE)
text(s, 7.0, 1.9, 5.6, 4.8, [
    [("Same pair twice? ", {"bold": True}), ("Cannot be written down.", {})],
    [("One pick per cube? ", {"bold": True}), ("Automatic.", {})],
    [("Only rule left: ", {"bold": True}), ("every colour has degree 2 on each side pair.", {})],
    [("Cost  C = Σ (d − 2)²", {"bold": True, "font": HEAD, "size": 20, "colour": TEAL})],
    "Written with Z operators: “cube c holds code k” is a product of (1 ± Z)/2 on its 3 qubits. "
    "Terms touch at most 6 qubits (two cubes). 164 terms at N = 4.",
    [("Codes 6 and 7 need no penalty: the circuit never creates them.", {"italic": True})],
], size=17, space=12)
s.notes_slide.notes_text_frame.text = "Speaker 2: bit order — qubit 0 is the rightmost character in a Qiskit key; cube 1 is the last 3 characters. We tested the decoder on the known answer."

# ---------------------------------------------------------------- 4 algorithm
s = prs.slides.add_slide(BLANK)
title(s, "Algorithm: QAOA that only makes legal moves",
      "Start in all legal choices, then alternate a cost layer and a per-cube mixer, p times")
s.shapes.add_picture("results/circuit_one_cube.png", Inches(0.8), Inches(1.9), width=Inches(7.3))
steps = [("1  Start", "each cube in an equal mix of its 6 codes (RY, controlled-H, H)"),
         ("2  Cost layer", "exp(−iγH): each Z string is a CNOT ladder + one RZ"),
         ("3  Mixer", "exp(−iβ|u⟩⟨u|) per cube: any legal choice can become any other, never an illegal one"),
         ("4  Tune", "pick γ, β by minimising the average cost on a simulator, never using the answer"),
         ("5  Measure", "decode every shot and check it with solves()")]
for i, (h, d) in enumerate(steps):
    y = 1.9 + i * 1.0
    card(s, 8.5, y, 4.3, 0.88)
    text(s, 8.7, y + 0.08, 4.0, 0.8, [[(h, {"bold": True, "colour": TEAL, "size": 16})], [(d, {"size": 13})]],
         space=2)
text(s, 0.8, 5.6, 7.3, 1.2, "Above: one cube's start state, then one mixer step (undo the start, phase on |000⟩, redo). "
     f"One full layer at N = 4 is about 550 CNOTs after transpiling to rz, sx, x, cx.", size=14, colour=GREY)
s.notes_slide.notes_text_frame.text = "Speaker 2: the mixer is the 'complete graph' mixer over 6 codes. Tuning: layer by layer, each depth starts from the previous angles stretched (INTERP)."

# ---------------------------------------------------------------- 5 checks
s = prs.slides.add_slide(BLANK)
title(s, "Classical checks before any claim", "Every check is an assert in the notebook; all pass")
checks = [("H = classical cost", "N = 4 to 6: every valid state; N = 7, 8: 3,000 random ones. Largest gap 0."),
          ("Lowest energy = the answer", "exactly 2 zero-cost states = count_answers = graph method; no ties (next cost is 2)."),
          ("Independent cost agrees", "the starter's 24-qubit QUBO is zero on the same 2 states."),
          ("Circuit stays legal", "start state is 1/6 on each valid code; leakage to codes 6, 7 is 7e-15; 0 invalid shots."),
          ("Fast simulator = Qiskit", "our 6^N simulator matches Statevector of the real circuit to 5e-17."),
          ("Every tower checked", "each measured shot is decoded (qubit 0 = rightmost bit) and passed to solves().")]
for i, (h, d) in enumerate(checks):
    col, row = i % 2, i // 2
    x, y = 0.8 + col * 6.1, 1.9 + row * 1.6
    card(s, x, y, 5.8, 1.4)
    tick = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(x + 0.25), Inches(y + 0.4), Inches(0.55), Inches(0.55))
    tick.fill.solid()
    tick.fill.fore_color.rgb = TEAL
    tick.line.fill.background()
    tf = tick.text_frame
    tf.text = "✓"
    tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    tf.paragraphs[0].runs[0].font.size = Pt(18)
    tf.paragraphs[0].runs[0].font.color.rgb = WHITE
    tf.paragraphs[0].runs[0].font.bold = True
    text(s, x + 1.05, y + 0.15, 4.55, 1.2, [[(h, {"bold": True, "size": 16})], [(d, {"size": 13, "colour": GREY})]],
         space=3)
s.notes_slide.notes_text_frame.text = "Speaker 3: this is the slide for the tie-break criterion. Say how each check would catch a bug."

# ---------------------------------------------------------------- 6 results N = 4
s = prs.slides.add_slide(BLANK)
p12 = MEAS[12]["p"]
title(s, f"Four cubes: {pct(p12)} of shots are the solved tower",
      "Constrained QAOA, 12 qubits, 1000 shots per circuit; random legal guess = 0.15%")
cd = CategoryChartData()
cd.categories = [str(p) for p in sorted(CORE)]
cd.add_series("exact (simulator)", [CORE[p]["P"] for p in sorted(CORE)])
ch = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(0.7), Inches(1.8), Inches(7.4), Inches(5.0), cd).chart
style_chart(ch, "P(correct tower)", "layers p")
ch.has_title = False
ch.has_legend = False
ch.value_axis.maximum_scale = 1.0
ch.value_axis.tick_labels.number_format = "0%"
ch.value_axis.tick_labels.number_format_is_linked = False
ser = ch.plots[0].series[0]
ser.format.line.color.rgb = TEAL
ser.format.line.width = Pt(2.5)
ser.marker.style = XL_MARKER_STYLE.CIRCLE
ser.marker.format.fill.solid()
ser.marker.format.fill.fore_color.rgb = TEAL
ser.smooth = False
rows = [("p", "CX", "depth", "shots", "exact")] + [
    (str(p), f"{MEAS[p]['cx']:,}", f"{MEAS[p]['depth']:,}", pct(MEAS[p]["p"]), pct(CORE[p]["P"])) for p in sorted(MEAS)]
tbl = s.shapes.add_table(len(rows), 5, Inches(8.5), Inches(1.9), Inches(4.3), Inches(2.6)).table
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.text = v
        r = cell.text_frame.paragraphs[0].runs[0]
        r.font.size, r.font.name, r.font.bold = Pt(13), BODY, i == 0
        r.font.color.rgb = WHITE if i == 0 else INK
        cell.fill.solid()
        cell.fill.fore_color.rgb = TEAL if i == 0 else (LIGHT if i % 2 else WHITE)
device = MEAS[12]["device"]
text(s, 8.5, 4.75, 4.3, 2.0, [
    [("Device: ", {"bold": True}), (device, {})],
    [(f"Measured at p = 12: about {p12 / (2 / 1296):,.0f}× a random legal guess. ", {}),
     ("Measured shots match the exact value within shot noise.", {})],
    [("Warm-up (front/back only, starter): ", {"bold": True}),
     (f"{pct(S['rows'][0]['p'])} good picks at p = 2.", {})]], size=14, space=8)
s.notes_slide.notes_text_frame.text = "Speaker 3: the line is the exact simulation; the table is shots. Point out the baseline and that no shot was an illegal code."

# ---------------------------------------------------------------- 7 bonus
s = prs.slides.add_slide(BLANK)
title(s, "Bonus: same method for N cubes and N colours",
      "make_puzzle seeds {5: 16, 6: 86, 7: 68, 8: 4}, each with exactly one tower; depth fixed at p = 10")
cd = CategoryChartData()
cd.categories = [str(r["n"]) for r in SCALE]
cd.add_series("QAOA p = 10", [r["exact"] for r in SCALE])
cd.add_series("random legal guess", [r["rand_valid"] for r in SCALE])
ch = s.shapes.add_chart(XL_CHART_TYPE.LINE_MARKERS, Inches(0.7), Inches(1.8), Inches(6.6), Inches(5.0), cd).chart
style_chart(ch, "P(correct tower), log scale", "N cubes")
va = ch.value_axis
va.tick_labels.number_format = "0.000%"
va.tick_labels.number_format_is_linked = False
from lxml import etree
scaling = va._element.find("{http://schemas.openxmlformats.org/drawingml/2006/chart}scaling")
lb = etree.SubElement(scaling, "{http://schemas.openxmlformats.org/drawingml/2006/chart}logBase")
lb.set("val", "10")
scaling.remove(lb)
scaling.insert(0, lb)
ch.has_title = False
ch.has_legend = True
ch.legend.position = XL_LEGEND_POSITION.BOTTOM
ch.legend.include_in_layout = False
for ser, col in zip(ch.plots[0].series, (TEAL, GREY)):
    ser.format.line.color.rgb = col
    ser.format.line.width = Pt(2.5)
    ser.marker.style = XL_MARKER_STYLE.CIRCLE
    ser.marker.format.fill.solid()
    ser.marker.format.fill.fore_color.rgb = col
    ser.smooth = False
rows = [("N", "qubits", "CX", "P(correct)", "× random")] + [
    (str(r["n"]), str(r["qubits"]), f"{r['cx']:,}", pct(r["exact"]), f"{r['exact'] / r['rand_valid']:,.0f}")
    for r in SCALE]
tbl = s.shapes.add_table(len(rows), 5, Inches(7.7), Inches(1.9), Inches(5.1), Inches(3.0)).table
for i, row in enumerate(rows):
    for j, v in enumerate(row):
        cell = tbl.cell(i, j)
        cell.text = v
        r = cell.text_frame.paragraphs[0].runs[0]
        r.font.size, r.font.name, r.font.bold = Pt(13), BODY, i == 0
        r.font.color.rgb = WHITE if i == 0 else INK
        cell.fill.solid()
        cell.fill.fore_color.rgb = TEAL if i == 0 else (LIGHT if i % 2 else WHITE)
text(s, 7.7, 5.15, 5.1, 1.7, [
    "Qubits grow as 3N; CNOTs per layer grow about linearly here (550 → 2,100).",
    "At fixed depth success falls with N, but more slowly than random guessing: "
    "the advantage over guessing grows. Keeping success high would need more layers."], size=14, space=8)
s.notes_slide.notes_text_frame.text = "Speaker 4: angles for N=5-8 were tuned offline with the same function and reloaded; the notebook recomputes their success. N=7,8 local shots come from the exact distribution unless run on SV1."

# ---------------------------------------------------------------- 8 takeaways
s = prs.slides.add_slide(BLANK)
bg(s, DARK)
tower(s, 0.9, 0.7, 0.2)
text(s, 1.4, 0.55, 11, 0.9, "What we learned, and what we'd try next", size=34, font=HEAD, bold=True, colour=WHITE)
soft = RGBColor.from_string("C9D3DA")
text(s, 0.9, 1.8, 5.6, 5, [
    [("Learned", {"bold": True, "size": 22, "colour": RGBColor.from_string("5FD4C8"), "font": HEAD})],
    "Building the rules into the encoding (3 qubits per cube) beat penalty terms: fewer qubits, nothing to tune, no wasted shots.",
    "QAOA really concentrates probability on the answer, and checks show it is the right answer.",
    "No speedup: brute force takes 0.14 s, and tuning needed a full classical simulation.",
    "Success at fixed depth falls with N; gates grow with N.",
], size=16, colour=soft, space=12)
text(s, 7.0, 1.8, 5.6, 5, [
    [("Next step", {"bold": True, "size": 22, "colour": RGBColor.from_string("F0B070"), "font": HEAD})],
    [("Measure how many layers keep success at 50% as N grows, ", {"bold": True, "colour": WHITE}),
     ("using a CVaR objective and angles transferred from smaller N.", {})],
    "Also: reorder cost terms to cancel CNOTs; a Grover search with a reversible degree-counting oracle; "
    "one shallow run on real hardware next to SV1.",
    [("AI use: Claude Code wrote code and docs; every model was checked against brute force.",
      {"italic": True})],
], size=16, colour=soft, space=12)
s.notes_slide.notes_text_frame.text = "Speaker 4: close with honesty — what works, what doesn't scale, and the one next experiment."

prs.save("slides.pptx")
print("wrote slides.pptx with", len(prs.slides), "slides")
