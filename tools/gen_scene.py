"""Emit the robot / tin-can-telephone / Isabelle scene as SVG.

Geometry is transcribed from the TikZ pics in the ai4math_convening slides
(preamble.tex): robot, tincan, canphone. TikZ is y-up, SVG is y-down, so every
y is negated. TikZ line widths are in pt; 1 unit = 1cm = 28.4527pt.
"""
import math
import os

PT = 1 / 28.4527  # pt -> tikz units

C = dict(
    body="#7C838D", dark="#2C2F35", light="#9AA1AB", metal="#C3C8CE",
    screen="#EEF1F5", red="#901A1E", twine="#D8B87E", twine_dark="#9C7A44",
)

out = []
def e(s): out.append(s)


# the repo root, from this file: fragments land here whatever the working
# directory is, and never outside the checkout
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def emit(name, text):
    """Write a generated fragment into the repo root."""
    open(os.path.join(ROOT, name), "w").write(text)


def esc(s):
    """Isabelle source is full of < and &; SVG text is markup."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def hammer_pic(x, y, size=1.15, cls="b-hammer"):
    """The Sledgehammer icon from the prose, at scene scale."""
    s = size / 48
    e(f'<g class="{cls}" transform="translate({x:.4g},{y:.4g}) scale({s:.5g}) '
      f'translate(-24,-24)">')
    e('<g transform="rotate(-38 24 24)">')
    e(f'<rect x="21.6" y="15" width="4.8" height="27" rx="2.4" fill="{C["twine_dark"]}"/>')
    e(f'<rect x="9.5" y="5" width="29" height="12.4" rx="2.6" fill="{C["metal"]}" '
      f'stroke="{C["dark"]}" stroke-width="1.7"/>')
    e(f'<rect x="19.6" y="5" width="8.8" height="12.4" fill="{C["light"]}"/>')
    e('</g></g>')


def isa_badge(x, y, size=0.42):
    """The Isabelle logo, top-left of an editor panel; light and dark copies."""
    e(f'<image class="isa-badge badge-light" href="assets/isabelle.svg" '
      f'x="{x:.4g}" y="{y - size/2:.4g}" width="{size}" height="{size}" '
      f'preserveAspectRatio="xMidYMid meet"/>')
    e(f'<image class="isa-badge badge-dark" href="assets/isabelle-dark.svg" '
      f'x="{x:.4g}" y="{y - size/2:.4g}" width="{size}" height="{size}" '
      f'preserveAspectRatio="xMidYMid meet"/>')


def rounded_poly(pts, r):
    """Path for a polygon with uniformly rounded corners."""
    n = len(pts)
    d = []
    for i in range(n):
        p0, p1, p2 = pts[(i - 1) % n], pts[i], pts[(i + 1) % n]
        v0 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l0 = math.hypot(*v0) or 1
        l2 = math.hypot(*v2) or 1
        rr = min(r, l0 / 2, l2 / 2)
        a = (p1[0] + v0[0] / l0 * rr, p1[1] + v0[1] / l0 * rr)
        b = (p1[0] + v2[0] / l2 * rr, p1[1] + v2[1] / l2 * rr)
        d.append(("M" if i == 0 else "L") + f"{a[0]:.4g},{a[1]:.4g}")
        d.append(f"Q{p1[0]:.4g},{p1[1]:.4g} {b[0]:.4g},{b[1]:.4g}")
    d.append("Z")
    return " ".join(d)


# ---------------------------------------------------------------- robot ----
def robot(mode='story'):
    e('<g class="robot">')
    # torso
    e(f'<path fill="{C["body"]}" d="{rounded_poly([(-2,1.6),(2,1.6),(1.6,3.0),(-1.6,3.0)], 12*PT)}"/>')
    e(f'<path stroke="{C["dark"]}" stroke-width="{1*PT:.4g}" d="M-1.5,1.75H1.5"/>')
    # neck
    e(f'<rect fill="{C["dark"]}" x="-0.42" y="1.0" width="0.84" height="0.75"/>')
    # arms
    aw = 15 * PT
    for pts in [[(-1.8,1.68),(-3.05,1.8),(-3.4,-0.15)], [(1.8,1.68),(3.05,1.8),(3.4,-0.15)]]:
        d = "M" + " L".join(f"{x:.4g},{y:.4g}" for x, y in pts)
        e(f'<path fill="none" stroke="{C["body"]}" stroke-width="{aw:.4g}" '
          f'stroke-linecap="round" stroke-linejoin="round" d="{d}"/>')
    # joints
    for x, y in [(-1.8,1.68),(-3.05,1.8),(-3.4,-0.15),(1.8,1.68),(3.05,1.8),(3.4,-0.15)]:
        e(f'<circle fill="{C["dark"]}" cx="{x}" cy="{y}" r="0.23"/>')
        e(f'<circle fill="{C["light"]}" cx="{x}" cy="{y}" r="0.09"/>')
    # chest core
    e(f'<circle fill="{C["dark"]}" cx="0" cy="2.25" r="0.34"/>')
    e(f'<circle class="core" fill="{C["red"]}" cx="0" cy="2.25" r="0.26" '
      f'stroke="{C["light"]}" stroke-width="{1*PT:.4g}"/>')
    # head + screen
    e(f'<rect fill="{C["body"]}" x="-1.55" y="-1.05" width="3.1" height="2.1" rx="{10*PT:.4g}"/>')
    e(f'<rect fill="{C["screen"]}" stroke="{C["dark"]}" stroke-width="{1*PT:.4g}" '
      f'x="-1.3" y="-0.8" width="2.6" height="1.6" rx="{6*PT:.4g}"/>')
    # face
    e('<g class="eyes">')
    for x in (-0.55, 0.55):
        e(f'<circle fill="{C["dark"]}" cx="{x}" cy="-0.2" r="0.16"/>')
    e('</g>')
    # The story robot carries all three mouths and cross-fades them. The other
    # two are fixed: CSS cannot reach into a <use> shadow tree with a descendant
    # selector, so a per-instance mood has to be a separate <defs> entry.
    FLAT  = "M-0.45,0.35H0.45"
    SAD   = "M-0.46,0.46 Q0,0.12 0.46,0.46"
    HAPPY = "M-0.46,0.24 Q0,0.58 0.46,0.24"
    mouths = {"story": (("m-flat", FLAT), ("m-sad", SAD), ("m-happy", HAPPY)),
              "calm":  (("m-fixed", FLAT),),
              "glum":  (("m-fixed", SAD),),
              "glad":  (("m-fixed", HAPPY),)}[mode]
    for cls, d in mouths:
        e(f'<path class="mouth {cls}" fill="none" stroke="{C["dark"]}" '
          f'stroke-width="{2.2*PT:.4g}" stroke-linecap="round" stroke-linejoin="round" d="{d}"/>')
    # antenna
    e(f'<path fill="none" stroke="{C["body"]}" stroke-width="{3.5*PT:.4g}" '
      f'stroke-linecap="round" d="M0,-1.05V-1.45"/>')
    e(f'<circle class="blip" fill="{C["red"]}" cx="0" cy="-1.52" r="0.1"/>')

    # circular saw (left hand)
    e(f'<path fill="none" stroke="{C["dark"]}" stroke-width="{13*PT:.4g}" '
      f'stroke-linecap="round" d="M-3.4,-0.15L-3.72,-0.58"/>')
    saw_cls = "saw saw-live" if mode == "glad" else "saw"
    e(f'<g transform="translate(-3.82,-0.9)"><g class="{saw_cls}">')
    e(f'<circle fill="{C["metal"]}" cx="0" cy="0" r="0.5"/>')
    teeth = []
    for a in range(0, 360, 18):
        p = [(0.5 * math.cos(math.radians(a)), -0.5 * math.sin(math.radians(a))),
             (0.63 * math.cos(math.radians(a + 5)), -0.63 * math.sin(math.radians(a + 5))),
             (0.5 * math.cos(math.radians(a + 11)), -0.5 * math.sin(math.radians(a + 11)))]
        teeth.append("M" + " L".join(f"{x:.4g},{y:.4g}" for x, y in p) + "Z")
    e(f'<path fill="{C["metal"]}" d="{" ".join(teeth)}"/>')
    e(f'<circle fill="none" stroke="{C["dark"]}" stroke-width="{0.8*PT:.4g}" cx="0" cy="0" r="0.5"/>')
    spokes = []
    for a in (30, 150, 270):
        r0 = (0.2 * math.cos(math.radians(a)), -0.2 * math.sin(math.radians(a)))
        r1 = (0.38 * math.cos(math.radians(a)), -0.38 * math.sin(math.radians(a)))
        spokes.append(f"M{r0[0]:.4g},{r0[1]:.4g}L{r1[0]:.4g},{r1[1]:.4g}")
    e(f'<path fill="none" stroke="{C["dark"]}" stroke-width="{2.5*PT:.4g}" '
      f'stroke-linecap="round" d="{" ".join(spokes)}"/>')
    e(f'<circle fill="{C["dark"]}" cx="0" cy="0" r="0.12"/>')
    e(f'<circle fill="{C["metal"]}" cx="0" cy="0" r="0.05"/>')
    e('</g></g>')

    # drill (right hand)
    e('<g transform="translate(3.4,-0.15) rotate(-52)">')
    e(f'<rect fill="{C["dark"]}" x="-0.2" y="-0.05" width="0.4" height="0.83" rx="{4*PT:.4g}"/>')
    e(f'<rect fill="{C["body"]}" x="-0.33" y="-0.95" width="0.66" height="1.07" rx="{7*PT:.4g}"/>')
    e(f'<rect fill="{C["light"]}" x="-0.22" y="-0.45" width="0.44" height="0.33" rx="{3*PT:.4g}"/>')
    e(f'<rect fill="{C["dark"]}" x="-0.17" y="-1.12" width="0.34" height="0.17"/>')
    e(f'<clipPath id="pm-bit-{mode}"><path d="M-0.07,-1.12L0.07,-1.12L0,-1.78Z"/></clipPath>')
    e(f'<path fill="{C["metal"]}" d="M-0.07,-1.12L0.07,-1.12L0,-1.78Z"/>')
    e(f'<g clip-path="url(#pm-bit-{mode})">')
    fl_cls = "flutes flutes-live" if mode == "glad" else "flutes"
    e(f'<path class="{fl_cls}" fill="none" stroke="{C["dark"]}" '
      f'stroke-width="{0.6*PT:.4g}" d="M-0.05,1.3L0.045,1.16 M-0.05,1.08L0.045,0.94 M-0.05,0.86L0.045,0.72 M-0.05,0.64L0.045,0.5 M-0.05,0.42L0.045,0.28 M-0.05,0.2L0.045,0.06 M-0.05,-0.02L0.045,-0.16 M-0.05,-0.24L0.045,-0.38 M-0.05,-0.46L0.045,-0.6 M-0.05,-0.68L0.045,-0.82 M-0.05,-0.9L0.045,-1.04 M-0.05,-1.12L0.045,-1.26 M-0.05,-1.34L0.045,-1.48 M-0.05,-1.56L0.045,-1.7 M-0.05,-1.78L0.045,-1.92 M-0.05,-2L0.045,-2.14"/>')
    e('</g>')
    e('</g>')
    e('</g>')


# --------------------------------------------------------------- tin can ----
LH, RR, EE = 0.6, 0.6, 0.22
EH, RH = EE * 0.55, RR * 0.66
RIB_IN = (1.2 / 2 + 0.9 / 2) * PT
RRY = RR - RIB_IN


def tincan(cx, cy, scale, direction, cls=""):
    e(f'<g class="{cls}" transform="translate({cx},{cy}) scale({scale*direction},{scale})">')
    e(f'<path fill="{C["metal"]}" stroke="{C["dark"]}" stroke-width="{1.2*PT:.4g}" '
      f'stroke-linejoin="round" d="M{-LH},{-RR}H{LH}A{EE},{RR} 0 0 1 {LH},{RR}H{-LH}Z"/>')
    for x in (-0.2, 0.2):
        e(f'<path fill="none" stroke="{C["dark"]}" stroke-opacity="0.55" '
          f'stroke-width="{0.9*PT:.4g}" d="M{x},{-RRY:.4g}A{EE},{RRY:.4g} 0 0 1 {x},{RRY:.4g}"/>')
    e(f'<ellipse fill="{C["light"]}" stroke="{C["dark"]}" stroke-width="{1.2*PT:.4g}" '
      f'cx="{-LH}" cy="0" rx="{EE}" ry="{RR}"/>')
    e(f'<ellipse fill="{C["dark"]}" cx="{-LH}" cy="0" rx="{EH:.4g}" ry="{RH:.4g}"/>')
    e(f'<circle fill="{C["dark"]}" cx="{LH}" cy="0" r="0.05"/>')
    e('</g>')


# ---- Human pic --------------------------------------------------------------
# Same flat vocabulary as the robot -- same stroke weights, same joints, same
# rounded torso -- so the two read as a pair. She faces left, towards her
# editor: the glasses and pupils sit off-centre that way.
C["skin"] = "#E0AE86"
C["skin_dark"] = "#C08F6B"
C["hair"] = "#3A2F2B"
C["shirt"] = "#6E7C99"
C["shirt_dark"] = "#5A6680"


def human(mood='calm'):
    e('<g class="human">')
    # torso
    e(f'<path fill="{C["shirt"]}" d="{rounded_poly([(-2.0,1.55),(2.0,1.55),(1.65,3.0),(-1.65,3.0)], 12*PT)}"/>')
    e(f'<path stroke="{C["shirt_dark"]}" stroke-width="{1*PT:.4g}" d="M-1.5,1.72H1.5"/>')
    # arms: one reaching left to the keyboard, one resting
    e(f'<path fill="none" stroke="{C["shirt"]}" stroke-width="{15*PT:.4g}" '
      f'stroke-linecap="round" stroke-linejoin="round" d="M-1.75,1.62L-2.95,1.9L-3.75,1.35"/>')
    e(f'<path fill="none" stroke="{C["shirt"]}" stroke-width="{15*PT:.4g}" '
      f'stroke-linecap="round" stroke-linejoin="round" d="M1.75,1.62L2.9,1.95L3.3,2.6"/>')
    for x, y in [(-1.75,1.62),(-2.95,1.9),(1.75,1.62),(2.9,1.95)]:
        e(f'<circle fill="{C["shirt_dark"]}" cx="{x}" cy="{y}" r="0.2"/>')
    # hands
    e(f'<circle fill="{C["skin"]}" cx="-3.75" cy="1.35" r="0.34"/>')
    e(f'<circle fill="{C["skin"]}" cx="3.3" cy="2.6" r="0.34"/>')
    # neck
    e(f'<rect fill="{C["skin_dark"]}" x="-0.34" y="0.8" width="0.68" height="0.85"/>')
    # hair behind the head
    e(f'<path fill="{C["hair"]}" d="M-1.5,-0.15 a1.5,1.62 0 0 1 3,0 L1.5,1.15 '
      f'q-0.12,-0.9 -0.42,-1.25 L-1.08,-0.1 q-0.3,0.35 -0.42,1.25 Z"/>')
    # face
    e(f'<ellipse fill="{C["skin"]}" cx="0" cy="-0.1" rx="1.2" ry="1.32"/>')
    # fringe
    e(f'<path fill="{C["hair"]}" d="M-1.24,-0.28 a1.26,1.4 0 0 1 2.48,0 '
      f'q-0.55,-0.62 -1.32,-0.42 q-0.62,0.16 -1.16,0.42 Z"/>')
    # glasses, sat towards the side she is looking
    e('<g class="specs">')
    for cx in (-0.66, 0.52):
        e(f'<rect fill="{C["screen"]}" fill-opacity="0.55" stroke="{C["dark"]}" '
          f'stroke-width="{2.2*PT:.4g}" x="{cx-0.42:.4g}" y="-0.52" width="0.84" '
          f'height="0.72" rx="0.24"/>')
    e(f'<path fill="none" stroke="{C["dark"]}" stroke-width="{2.2*PT:.4g}" '
      f'd="M-0.24,-0.2 q0.11,-0.12 0.22,0"/>')
    e(f'<path fill="none" stroke="{C["dark"]}" stroke-width="{2*PT:.4g}" '
      f'd="M-1.08,-0.26 L-1.24,-0.34"/>')
    e('</g>')
    # eyes, looking left
    e('<g class="eyes">')
    e(f'<circle fill="{C["dark"]}" cx="-0.78" cy="-0.16" r="0.15"/>')
    e(f'<circle fill="{C["dark"]}" cx="0.4" cy="-0.16" r="0.15"/>')
    e('</g>')
    # mouth
    smile = ("M-0.32,0.46 q0.32,0.42 0.64,-0.06" if mood == "glad"
             else "M-0.3,0.52 q0.3,0.26 0.6,-0.04")
    e(f'<path class="mouth" fill="none" stroke="{C["skin_dark"]}" '
      f'stroke-width="{2.4*PT:.4g}" stroke-linecap="round" d="{smile}"/>')
    e('</g>')

def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
            u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1])


# ============================================================== the scene ====
# One agent, one PIDE MCP, three live Isabelle sessions. Everything -- wires,
# cans, session panels, code -- lives in one SVG so the wire ends and the
# panels cannot drift apart at any width.

VB = "-10.35 -4.28 22.05 8.56"
RS, RPOS = 0.62, (-7.15, 0.15)
HUB, HUB_S = (-4.05, 0.05), 0.5
CAN_S = 0.42
PANEL_X, PANEL_W, PANEL_H = 0.55, 10.9, 2.42
ROWS = [-2.74, 0.0, 2.74]
BUS_X = -2.00                     # where the PIDE MCP tag taps the wires

CYCLE = 24                        # seconds; percentages below are of this

# Every proof below was run against a live Isabelle before it went on the page:
# `by auto` really does fail on the first with "Failed to finish proof", `by
# simp` really does fail on the second with "Failed to apply initial proof
# method", and both repaired proofs really do go through. power2_eq_square
# really is a fact at HOL.Power line 83, and its snippet is quoted verbatim --
# which is also exactly what the first proof was missing.
SESSIONS = [
    dict(logic="HOL", file="Scratch.thy", kind="proof",
         code=[[("lemma", "#kw"), (" ", ""),
                ('"(∑i<n. 2*i+1) = (n::nat)^2"', "#str")]],
         attempts=["sorry", "by auto",
                   "by (induct n) (auto simp: power2_eq_square)"],
         err="Failed to finish proof",
         done="finished · 0 errors"),
    dict(logic="HOL-Analysis", file="Cont.thy", kind="proof",
         code=[[("lemma", "#kw"), (" ", ""),
                ('"continuous_on S (λx::real. x * sin x)"', "#str")]],
         attempts=["sorry", "by simp", "by (intro continuous_intros)"],
         err="Failed to apply initial proof method",
         done="finished · 0 errors"),
    # Session three is not there when the page loads. The agent starts it,
    # reads a file into it, asks where Cauchy comes from -- a notion defined on
    # uniform spaces, via filters, nowhere near this file, which is exactly
    # what find_entities is for -- and then shuts it down again. Statement and
    # snippet both came out of a live session; see README.
    dict(logic="HOL-Probability", file="Cauchy.thy", kind="query",
         empty=[("(no theories loaded)", "#dim")],
         code=[[("lemma", "#kw"), (" ", ""),
                ('"Cauchy X ⟹ convergent (X::nat ⇒ real)"', "#str")]],
         reveal=[("  ↳ ", "#dim"), ("Cauchy X = cauchy_filter (filtermap X sequentially)",
                                    "#str")],
         ready="session ready · no theories",
         loaded="Cauchy.thy · 1 theory loaded",
         searching="find_entities · line 4",
         hits="7 entities · Cauchy · HOL.Topological_Spaces:3557"),
]

# (wire, label, kind, from %, to %)
LEGS = [
    (0, "edit",          "out",  2, 10),
    (1, "edit",          "out",  5, 13),
    (2, "start_session", "out", 12, 20),
    (0, "get_state",     "out", 18, 26),
    (1, "get_state",     "out", 21, 29),
    (0, "1 error",       "err", 28, 36),
    (2, "read",          "out", 24, 32),
    (1, "1 error",       "err", 31, 39),
    (2, "find_entities", "out", 38, 46),
    (0, "edit",          "out", 40, 48),
    (1, "edit",          "out", 43, 51),
    (2, "7 entities",    "info", 52, 60),
    (0, "get_state",     "out", 54, 62),
    (1, "get_state",     "out", 57, 65),
    (2, "stop_session",  "out", 66, 74),
    (0, "✓ 0 errors",    "ok",  64, 72),
    (1, "✓ 0 errors",    "ok",  67, 75),
]

# Per-session moments. Isabelle checks on its own clock: `fail`/`ok` are when
# the prover is done, NOT when a get_state turns up -- the get_state legs above
# leave before those moments and land after them, which is the whole point of
# asynchronous processing.
BEATS = [
    dict(land1=10, fail=21, land2=48, ok=59),
    dict(land1=13, fail=24, land2=51, ok=62),
]
# Session three's lifecycle, in % of the cycle.
Q_WIRE, Q_UP = 12, 20        # the string is thrown / the session is up
Q_READ = 32                  # the file lands in it
Q_SEARCH, Q_HITS = 46, 52    # the query goes in / the session has the answer
Q_DOWN, Q_GONE = 74, 82      # stop_session lands / the string is reeled in

SAD, SAD_END = 39, 50
HAPPY, HAPPY_END = 75, 98
RESET = 98


def wire(row_y):
    a = (HUB[0] + HUB_S * LH, HUB[1])
    b = (PANEL_X - 0.6 - CAN_S * LH, row_y)
    c1 = (a[0] + (b[0] - a[0]) * 0.42, a[1] + (b[1] - a[1]) * 0.16 + 0.26)
    c2 = (a[0] + (b[0] - a[0]) * 0.64, b[1] + 0.18)
    return a, c1, c2, b


def at(row, t):
    return bezier(*wire(ROWS[row]), t)


def wire_len(row):
    total, prev = 0.0, at(row, 0)
    for i in range(1, 401):
        cur = at(row, i / 400)
        total += math.dist(prev, cur)
        prev = cur
    return total


def y_at_x(row, x):
    """The wire is monotone in x, so bisect for the crossing."""
    lo, hi = 0.0, 1.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if at(row, mid)[0] < x:
            lo = mid
        else:
            hi = mid
    return at(row, (lo + hi) / 2)[1]


def wire_path(row):
    a, c1, c2, b = wire(ROWS[row])
    return (f"M{a[0]:.4g},{a[1]:.4g} C{c1[0]:.4g},{c1[1]:.4g} "
            f"{c2[0]:.4g},{c2[1]:.4g} {b[0]:.4g},{b[1]:.4g}")


# --------------------------------------------------------------- markup -----
out.clear()
e('<svg class="pm-defs" width="0" height="0" aria-hidden="true" focusable="false">')
e('<defs>')
for _mode, _id in (("story", "pm-robot"), ("calm", "pm-robot-calm"),
                   ("glum", "pm-robot-glum"), ("glad", "pm-robot-glad")):
    e(f'<g id="{_id}">')
    robot(_mode)
    e('</g>')
e('<g id="pm-can">')
tincan(0, 0, 1, 1)
e('</g>')
for i in range(3):
    e(f'<path id="pm-w{i}" fill="none" d="{wire_path(i)}"/>')
e('</defs>')
e('</svg>')
defs = "\n".join(out)

out.clear()
e(f'<svg class="scene" viewBox="{VB}" role="img" aria-labelledby="scT scD">')
e('<title id="scT">One coding agent wired to three live Isabelle sessions</title>')
e('<desc id="scD">A robot holds a tin can with three strings running from it, labelled '
  'PIDE MCP, to three Isabelle sessions: HOL, HOL-Analysis and HOL-Library. It edits two '
  'proofs and searches the third session for a definition. Both proofs come back with an '
  'error and the robot looks glum; it edits them again using what the search turned up, and '
  'this time both check clean, so it smiles.</desc>')
e(f'<g transform="translate({RPOS[0]},{RPOS[1]}) scale({RS})"><use href="#pm-robot"/></g>')

# wires, then cans on top of their ends
e('<g class="wires">')   # not "line": the page uses .line for the chapter
for i in range(3):
    e(f'<g class="wire w{i}">')
    e(f'<use href="#pm-w{i}" class="twine" stroke="{C["twine"]}" '
      f'stroke-width="{3*CAN_S*PT:.4g}" stroke-linecap="round"/>')
    ticks = []
    n = int(wire_len(i) * 13)
    for k in range(1, n):
        t = k / n
        x, y = at(i, t)
        x2, y2 = at(i, min(1, t + 0.004))
        ang = math.atan2(y2 - y, x2 - x)
        dx, dy = math.cos(ang + 1.15) * 0.05, math.sin(ang + 1.15) * 0.05
        ticks.append(f"M{x-dx:.4g},{y-dy:.4g}L{x+dx:.4g},{y+dy:.4g}")
    e(f'<path class="twist" fill="none" stroke="{C["twine_dark"]}" '
      f'stroke-width="{1*CAN_S*PT:.4g}" stroke-linecap="round" d="{" ".join(ticks)}"/>')
    e('</g>')
for j, (row, _, kind, _, _) in enumerate(LEGS):
    e(f'<use href="#pm-w{row}" class="pulse pulse-{j} k-{kind}" '
      f'stroke-width="{5*CAN_S*PT:.4g}" stroke-linecap="round"/>')
e(f'<g transform="translate({HUB[0]},{HUB[1]}) scale({HUB_S})"><use href="#pm-can"/></g>')
for i, y in enumerate(ROWS):
    e(f'<g class="can-r c{i}" transform="translate({PANEL_X - 0.6:.4g},{y}) '
      f'scale({-CAN_S},{CAN_S})"><use href="#pm-can"/></g>')
e('</g>')

# the label: one chip, a stem down the fan, a bullet on every wire
bus_ys = [y_at_x(i, BUS_X) for i in range(3)]
chip_h, chip_w = 0.66, 2.6
# the chip must not sit on top of the wire it is labelling
top_edge = min(y_at_x(0, BUS_X - chip_w / 2), y_at_x(0, BUS_X + chip_w / 2))
chip_y = top_edge - 0.58 - chip_h / 2
e('<g class="wire-tag">')
# the stem only reaches as far as there are sessions to tap
e(f'<path class="tag-stem" d="M{BUS_X},{chip_y + chip_h/2:.4g}V{bus_ys[1]:.4g}"/>')
e(f'<path class="tag-stem s2-stem" d="M{BUS_X},{bus_ys[1]:.4g}V{bus_ys[2]:.4g}"/>')
for i, by in enumerate(bus_ys):
    e(f'<circle class="tag-bullet b{i}" cx="{BUS_X}" cy="{by:.4g}" r="0.13"/>')
e(f'<rect class="tag-chip" x="{BUS_X - chip_w/2:.4g}" y="{chip_y - chip_h/2:.4g}" '
  f'width="{chip_w}" height="{chip_h}" rx="{chip_h/2:.4g}"/>')
e(f'<text class="tag-text" x="{BUS_X}" y="{chip_y:.4g}">PIDE MCP</text>')
e('</g>')

# the three session panels
for i, (y, s) in enumerate(zip(ROWS, SESSIONS)):
    top = y - PANEL_H / 2
    e(f'<g class="panel s{i}">')
    e(f'<rect class="pane" x="{PANEL_X}" y="{top:.4g}" width="{PANEL_W}" '
      f'height="{PANEL_H}" rx="0.22"/>')
    e(f'<rect class="pane-head" x="{PANEL_X}" y="{top:.4g}" width="{PANEL_W}" '
      f'height="0.6" rx="0.22"/>')
    e(f'<path class="pane-sep" d="M{PANEL_X},{top + 0.6:.4g}h{PANEL_W}"/>')
    e(f'<path class="pane-sep" d="M{PANEL_X},{top + PANEL_H - 0.6:.4g}h{PANEL_W}"/>')
    isa_badge(PANEL_X + 0.28, top + 0.3)
    e(f'<text class="pane-logic" x="{PANEL_X + 0.86:.4g}" y="{top + 0.3:.4g}">'
      f'{esc(s["logic"])}</text>')
    # a session with nothing in it has no theory to name yet
    file_cls = "pane-file q-file" if s["kind"] == "query" else "pane-file"
    e(f'<text class="{file_cls}" x="{PANEL_X + PANEL_W - 0.32:.4g}" y="{top + 0.3:.4g}" '
      f'text-anchor="end">{esc(s["file"])}</text>')

    line_y = [top + 0.96 + k * 0.45 for k in range(3)]
    if s["kind"] == "proof":
        # wash rectangles sit behind the attempt that is showing
        for cls in ("w-run", "w-err"):
            e(f'<rect class="wash {cls}" x="{PANEL_X + 0.12:.4g}" '
              f'y="{line_y[1] - 0.2:.4g}" width="{PANEL_W - 0.24:.4g}" height="0.42" '
              f'rx="0.07"/>')
    else:
        e(f'<rect class="wash w-found" x="{PANEL_X + 0.12:.4g}" '
          f'y="{line_y[1] - 0.2:.4g}" width="{PANEL_W - 0.24:.4g}" height="0.42" rx="0.07"/>')

    code_cls = " q-code" if s["kind"] == "query" else ""
    for k, parts in enumerate(s["code"]):
        spans = "".join(
            f'<tspan class="{cls[1:]}">{esc(txt)}</tspan>' if cls else esc(txt)
            for txt, cls in parts)
        e(f'<text class="pane-code{code_cls}" x="{PANEL_X + 0.32:.4g}" '
          f'y="{line_y[k]:.4g}">{spans}</text>')

    if s["kind"] == "query":
        def row(parts, cls, y):
            spans = "".join(
                f'<tspan class="{c[1:]}">{esc(t)}</tspan>' if c else esc(t)
                for t, c in parts)
            e(f'<text class="pane-code {cls}" x="{PANEL_X + 0.32:.4g}" '
              f'y="{y:.4g}">{spans}</text>')
        row(s["empty"], "q-empty", line_y[0])
        row(s["reveal"], "q-snip", line_y[1])

    if s["kind"] == "proof":
        for k, a in enumerate(s["attempts"]):
            cls = "warn" if k == 0 else "kw"
            kw, rest = (a, "") if k == 0 else (a.split(" ", 1) + [""])[:2]
            body = (f'<tspan class="{cls}">{esc(kw)}</tspan>' if k == 0
                    else f'<tspan class="kw">{esc(kw)}</tspan> {esc(rest)}')
            e(f'<text class="pane-code pv pv{k+1}" x="{PANEL_X + 0.55:.4g}" '
              f'y="{line_y[1]:.4g}">{body}</text>')

    sy = top + PANEL_H - 0.3
    states = ([("idle", "1 subgoal left", "warn"), ("run", "checking…", "run"),
               ("err", "error · " + s["err"], "err"), ("done", s["done"], "ok")]
              if s["kind"] == "proof" else
              [("ready", s["ready"], "dim"), ("loaded", s["loaded"], "ok"),
               ("run", s["searching"], "run"), ("done", s["hits"], "ok")])
    for key, text, tone in states:
        e(f'<g class="pst pst-{key} tone-{tone}">')
        e(f'<circle class="pane-dot" cx="{PANEL_X + 0.48:.4g}" cy="{sy:.4g}" r="0.11"/>')
        e(f'<text class="pane-status" x="{PANEL_X + 0.76:.4g}" y="{sy:.4g}">'
          f'{esc(text)}</text>')
        e('</g>')
    e('</g>')

e('<g class="packets" aria-hidden="true">')
for j, (row, word, kind, _, _) in enumerate(LEGS):
    w = 0.168 * len(word) + 0.42
    e(f'<g class="pkt m{j} k-{kind}">'
      f'<rect x="{-w/2:.4g}" y="-0.19" width="{w:.4g}" height="0.38" rx="0.19"/>'
      f'<text>{esc(word)}</text></g>')
e('</g>')
e('</svg>')
scene = "\n".join(out)

# ------------------------------------------------------------ keyframes -----
def windows(name, spans, prop="opacity"):
    """steps(1) cross-fade: `spans` are the [from%, to%) the element is shown."""
    pts, cur = [], 0.0
    for a, bb in spans:
        if a > cur:
            pts.append((cur, 0))
        pts.append((a, 1))
        pts.append((bb - 0.1, 1))
        cur = bb
    if cur < 100:
        pts.append((cur, 0))
        pts.append((100, 0))
    seen, ks = set(), [f"@keyframes {name} {{"]
    for pct, v in pts:
        p = round(max(0.0, min(100.0, pct)), 2)
        if p in seen:
            continue
        seen.add(p)
        ks.append(f"  {p:g}% {{ {prop}: {v}; }}")
    ks.append("}")
    return "\n".join(ks)


css = []
for j, (row, _, kind, a, bb) in enumerate(LEGS):
    rev = kind != "out"
    ln = wire_len(row)
    seg = ln * 0.19
    px, py = at(row, 1 if rev else 0)
    ex, ey = at(row, 0 if rev else 1)
    ks = [f"@keyframes msg-{j} {{",
          f"  0%, {a}% {{ transform: translate({px:.4g}px, {py:.4g}px); opacity: 0; }}"]
    for i in range(9):
        f = i / 8
        x, y = at(row, 1 - f if rev else f)
        pct = a + (bb - a) * f
        op = 0 if i in (0, 8) else 1
        ks.append(f"  {pct:.4g}% {{ transform: translate({x:.4g}px, {y:.4g}px); opacity: {op}; }}")
    ks.append(f"  {bb}%, 100% {{ transform: translate({ex:.4g}px, {ey:.4g}px); opacity: 0; }}")
    ks.append("}")
    ks.append(f"@keyframes pulse-{j} {{")
    ks.append(f"  0%, {a}% {{ stroke-dashoffset: {seg if not rev else -ln:.4g}px; opacity: 0; }}")
    ks.append(f"  {a+1}%, {bb-1}% {{ opacity: 1; }}")
    ks.append(f"  {bb}%, 100% {{ stroke-dashoffset: {-ln if not rev else seg:.4g}px; opacity: 0; }}")
    ks.append("}")
    ks.append(f".pkt.m{j} {{ animation-name: msg-{j}; }}")
    ks.append(f".pulse-{j} {{ animation-name: pulse-{j}; "
              f"stroke-dasharray: {seg:.4g}px {ln + 2*seg:.4g}px; }}")
    x0, y0 = at(row, 0.45)
    ks.append(f".pkt.m{j} {{ --rx: {x0:.4g}px; --ry: {y0:.4g}px; }}")
    css.append("\n".join(ks))

for i, bt in enumerate(BEATS):
    css.append(windows(f"s{i}-pv1", [(0, bt["land1"]), (RESET, 100)]))
    css.append(windows(f"s{i}-pv2", [(bt["land1"], bt["land2"])]))
    css.append(windows(f"s{i}-pv3", [(bt["land2"], RESET)]))
    css.append(windows(f"s{i}-run", [(bt["land1"], bt["fail"]), (bt["land2"], bt["ok"])]))
    css.append(windows(f"s{i}-err", [(bt["fail"], bt["land2"])]))
    css.append(windows(f"s{i}-idle", [(0, bt["land1"]), (RESET, 100)]))
    css.append(windows(f"s{i}-done", [(bt["ok"], RESET)]))
    css.append(
        f".s{i} .pv1 {{ animation-name: s{i}-pv1; }}\n"
        f".s{i} .pv2 {{ animation-name: s{i}-pv2; }}\n"
        f".s{i} .pv3 {{ animation-name: s{i}-pv3; }}\n"
        f".s{i} .w-run {{ animation-name: s{i}-run; }}\n"
        f".s{i} .w-err {{ animation-name: s{i}-err; }}\n"
        f".s{i} .pst-idle {{ animation-name: s{i}-idle; }}\n"
        f".s{i} .pst-run {{ animation-name: s{i}-run; }}\n"
        f".s{i} .pst-err {{ animation-name: s{i}-err; }}\n"
        f".s{i} .pst-done {{ animation-name: s{i}-done; }}")

# --- session three: thrown out, used, reeled back in ------------------------
w2len = wire_len(2)
css.append(f"""@keyframes w2-throw {{
  0%, {Q_WIRE}% {{ stroke-dashoffset: {w2len:.4g}px; }}
  {Q_UP}%, {Q_DOWN}% {{ stroke-dashoffset: 0; }}
  {Q_GONE}%, 100% {{ stroke-dashoffset: {w2len:.4g}px; }}
}}""")

css.append(windows("s2-live", [(Q_UP, Q_DOWN)]))       # can, panel, bullet
css.append(windows("s2-twist", [(Q_UP, Q_DOWN)]))
css.append(windows("s2-empty", [(Q_UP, Q_READ)]))
css.append(windows("s2-code", [(Q_READ, Q_DOWN)]))
css.append(windows("s2-found", [(Q_HITS, Q_DOWN)]))
css.append(windows("s2-ready", [(Q_UP, Q_READ)]))
css.append(windows("s2-loaded", [(Q_READ, Q_SEARCH)]))
css.append(windows("s2-run", [(Q_SEARCH, Q_HITS)]))
css.append(windows("s2-done", [(Q_HITS, Q_DOWN)]))
# longhand on purpose: an `animation:` shorthand here would reset the
# animation-name set on the individual selectors below it
LANE3 = (".c2, .panel.s2, .tag-bullet.b2, .s2-stem, .w2 .twist, "
         ".s2 .q-empty, .s2 .q-code, .s2 .q-file, .s2 .q-snip")
css.append(f""".w2 .twine, {LANE3} {{
  animation-duration: var(--beat);
  animation-iteration-count: infinite;
}}
.w2 .twine {{
  stroke-dasharray: {w2len:.4g}px;
  animation-name: w2-throw;
  animation-timing-function: linear;
}}
{LANE3} {{
  opacity: 0;
  animation-timing-function: steps(1);
}}
.w2 .twist {{ animation-name: s2-twist; }}
.c2, .panel.s2, .tag-bullet.b2, .s2-stem {{ animation-name: s2-live; }}
.s2 .q-empty {{ animation-name: s2-empty; }}
.s2 .q-code, .s2 .q-file {{ animation-name: s2-code; }}
.s2 .q-snip, .s2 .w-found {{ animation-name: s2-found; }}
.s2 .pst-ready {{ animation-name: s2-ready; }}
.s2 .pst-loaded {{ animation-name: s2-loaded; }}
.s2 .pst-run {{ animation-name: s2-run; }}
.s2 .pst-done {{ animation-name: s2-done; }}""")

# the tools only run once it has something to celebrate; 1440deg and 10 flute
# pitches both land back where they started, so the cycle wraps cleanly
css.append(f"""@keyframes saw-spin {{
  0%, {HAPPY}% {{ transform: rotate(0deg); }}
  {HAPPY_END}%, 100% {{ transform: rotate(1440deg); }}
}}
@keyframes flute-run {{
  0%, {HAPPY}% {{ transform: translateY(0); }}
  {HAPPY_END}%, 100% {{ transform: translateY(-2.2px); }}
}}
.saw, .flutes {{
  animation-duration: var(--beat);
  animation-timing-function: linear;
  animation-iteration-count: infinite;
}}
.saw {{ transform-origin: 0 0; animation-name: saw-spin; }}
.flutes {{ animation-name: flute-run; }}""")

css.append(windows("face-sad", [(SAD, SAD_END)]))
css.append(windows("face-happy", [(HAPPY, HAPPY_END)]))
css.append(windows("face-flat", [(0, SAD), (SAD_END, HAPPY), (HAPPY_END, 100)]))

x0, y0 = at(0, 0.45)
css.append(f"/* one cycle is {CYCLE}s */\n:root {{ --beat: {CYCLE}s; }}")

emit("scene_defs.svgfrag", defs)
emit("scene.svgfrag", scene)
emit("scene_keyframes.css", "\n\n".join(css) + "\n")
print(f"defs {len(defs)}B  scene {len(scene)}B  css {sum(map(len, css))}B")
print("wires:", ", ".join(f"{wire_len(i):.2f}" for i in range(3)))
print("bus ys:", ", ".join(f"{y_at_x(i, BUS_X):.2f}" for i in range(3)))

# ============================================== any client speaks to it =====
# The robot above is not a particular agent. It is whichever one you use: each
# runs its own PIDE MCP, with its own sessions. Three by name, then a huddle of
# little ones for everything else. No shared hub -- that would be a lie.

C_VB = "-10.5 -1.35 21.0 4.6"
C_RS, C_MINI = 0.44, 0.21
NAMED = [("Claude Code", -8.05), ("Codex", -3.55), ("OpenCode", 0.95)]
HUDDLE = [(4.9, -0.28), (6.5, 0.16), (8.1, -0.34), (5.7, 0.62), (7.4, 0.66)]
HUDDLE_X = 6.5
PLATE_H, PLATE_Y = 0.66, 1.62
PLATE_W, MINI_PLATE_W = 4.3, 4.9

out.clear()
e(f'<svg class="mcp-svg" viewBox="{C_VB}" role="img" aria-labelledby="mcT mcD">')
e('<title id="mcT">Coding agents that speak MCP</title>')
e('<desc id="mcD">Three robots labelled Claude Code, Codex and OpenCode, then a huddle '
  'of smaller ones for any other MCP client. Each runs its own PIDE MCP server with its own '
  'Isabelle sessions.</desc>')


def plate(x, y, w, text, mini=False):
    cls = "plate mini" if mini else "plate"
    e(f'<rect class="{cls}" x="{x - w/2:.4g}" y="{y - PLATE_H/2:.4g}" width="{w:.4g}" '
      f'height="{PLATE_H}" rx="{PLATE_H/2:.4g}"/>')
    e(f'<text class="plate-text{" mini" if mini else ""}" x="{x:.4g}" y="{y:.4g}" '
      f'text-anchor="middle">{esc(text)}</text>')


for name, x in NAMED:
    e(f'<g class="agent" role="img" aria-label="{esc(name)}">')
    e(f'<rect class="hit" x="{x - PLATE_W/2:.4g}" y="-0.95" width="{PLATE_W}" '
      f'height="{PLATE_Y + PLATE_H/2 + 1.05:.4g}" rx="0.3"/>')
    e(f'<g transform="translate({x},0) scale({C_RS})">')
    e('<use class="r-calm" href="#pm-robot-calm"/>')
    e('<use class="r-glad" href="#pm-robot-glad"/>')
    e('</g>')
    plate(x, PLATE_Y, PLATE_W, name)
    e('</g>')

e('<g class="agent huddle" role="img" aria-label="and many other MCP clients">')
e(f'<rect class="hit" x="{HUDDLE_X - MINI_PLATE_W/2:.4g}" y="-0.95" width="{MINI_PLATE_W:.4g}" '
  f'height="{PLATE_Y + PLATE_H/2 + 1.05:.4g}" rx="0.3"/>')
for hx, hy in HUDDLE:
    e(f'<g transform="translate({hx},{hy}) scale({C_MINI})">')
    e('<use class="r-calm" href="#pm-robot-calm"/>')
    e('<use class="r-glad" href="#pm-robot-glad"/>')
    e('</g>')
plate(HUDDLE_X, PLATE_Y, MINI_PLATE_W, "…and many others", mini=True)
e('</g>')
e('</svg>')
emit("mcp.svgfrag", "\n".join(out))
print("client band", len("\n".join(out)), "B")

# ================================================ working side by side ======
# One file, two of you. The agent gets close and misses; it is not pleased. She
# leans in, runs Sledgehammer, and the missing lemma turns up. Then everyone is
# happy. The two proofs are the verified pair: `by (induct n) auto` really does
# fail here, and adding power2_eq_square really does close it.

B_VB = "-11.8 -2.55 20.65 4.9"
B_RS, B_HS = 0.46, 0.50
B_ROBOT, B_HUMAN = (-9.48, 0.35), (6.75, 0.35)
B_CAN, B_CAN_S = (-7.1, 0.9), 0.4
BP_X, BP_W, BP_H, BP_Y = -4.15, 8.6, 3.1, 0.15
BEAT_B = 20                        # seconds

E_GO, E_LAND = 5, 14               # the agent's edit travels, lands
G_GO = 17                          # the agent asks for the state...
E_FAIL = 20                        # ... and only then does the prover say no
G_LAND = 26                        # so the answer it gets is already the error
R_BACK_A, R_BACK_B = 28, 37        # the error travels home
SAD_B = 37                         # ... and it sulks
BUBBLE = 43                        # "let me help"
HAM_A, HAM_B = 48, 56              # she types sledgehammer
FIXED = 68                         # the method turns up, proof replaced
OK_B = 76                          # checked
GLAD_B = 76
RESET_B = 94

bp_top = BP_Y - BP_H / 2
b_line = [bp_top + 0.98 + k * 0.5 for k in range(3)]
b_sy = bp_top + BP_H - 0.31
_a = (B_CAN[0] + B_CAN_S * LH, B_CAN[1])
_d = (BP_X - 0.06, B_CAN[1] - 0.35)
_b = (_a[0] + (_d[0] - _a[0]) * 0.4, _a[1] + 0.12)
_c = (_a[0] + (_d[0] - _a[0]) * 0.72, _d[1] + 0.1)
b_wire = (f"M{_a[0]:.4g},{_a[1]:.4g} C{_b[0]:.4g},{_b[1]:.4g} "
          f"{_c[0]:.4g},{_c[1]:.4g} {_d[0]:.4g},{_d[1]:.4g}")


def b_at(t):
    return bezier(_a, _b, _c, _d, t)


blen = 0.0
_prev = b_at(0)
for _i in range(1, 301):
    _cur = b_at(_i / 300)
    blen += math.dist(_prev, _cur)
    _prev = _cur

out.clear()
e(f'<svg class="side-svg" viewBox="{B_VB}" role="img" aria-labelledby="sbT sbD">')
e('<title id="sbT">An agent and a person fixing the same proof together</title>')
e('<desc id="sbD">The robot is wired into a file and tries a proof that almost works; '
  'Isabelle reports an error and the robot looks glum. The woman at the same file says "let '
  'me help", runs Sledgehammer, and the missing lemma turns up – then both are smiling.</desc>')

for cls, ref in (("b-calm", "pm-robot-calm"), ("b-glum", "pm-robot-glum"),
                 ("b-glad", "pm-robot-glad")):
    e(f'<g class="{cls}" transform="translate({B_ROBOT[0]},{B_ROBOT[1]}) scale({B_RS})">'
      f'<use href="#{ref}"/></g>')

e(f'<path class="twine" fill="none" stroke="{C["twine"]}" '
  f'stroke-width="{3*B_CAN_S*PT:.4g}" stroke-linecap="round" d="{b_wire}"/>')
e(f'<use href="#pm-wire-b" class="pulse b-pulse-out k-out" '
  f'stroke-width="{5*B_CAN_S*PT:.4g}" stroke-linecap="round"/>')
e(f'<use href="#pm-wire-b" class="pulse b-pulse-state k-out" '
  f'stroke-width="{5*B_CAN_S*PT:.4g}" stroke-linecap="round"/>')
e(f'<use href="#pm-wire-b" class="pulse b-pulse-back k-err" '
  f'stroke-width="{5*B_CAN_S*PT:.4g}" stroke-linecap="round"/>')
e(f'<g transform="translate({B_CAN[0]},{B_CAN[1]}) scale({B_CAN_S})"><use href="#pm-can"/></g>')

# the shared file
e('<g class="panel side-panel">')
e(f'<rect class="pane" x="{BP_X}" y="{bp_top:.4g}" width="{BP_W}" height="{BP_H}" rx="0.24"/>')
e(f'<rect class="pane-head" x="{BP_X}" y="{bp_top:.4g}" width="{BP_W}" height="0.58" rx="0.24"/>')
e(f'<path class="pane-sep" d="M{BP_X},{bp_top + 0.58:.4g}h{BP_W}"/>')
e(f'<path class="pane-sep" d="M{BP_X},{bp_top + BP_H - 0.6:.4g}h{BP_W}"/>')
isa_badge(BP_X + 0.28, bp_top + 0.29)
e(f'<text class="pane-logic" x="{BP_X + 0.86:.4g}" y="{bp_top + 0.29:.4g}">HOL</text>')
e(f'<text class="pane-file" x="{BP_X + BP_W - 0.32:.4g}" y="{bp_top + 0.29:.4g}" '
  f'text-anchor="end">Scratch.thy</text>')

e(f'<text class="pane-code" x="{BP_X + 0.32:.4g}" y="{b_line[0]:.4g}">'
  f'<tspan class="kw">lemma</tspan> <tspan class="str">{esc(chr(34))}(∑i&lt;n. 2*i+1) '
  f'= (n::nat)^2{esc(chr(34))}</tspan></text>')
for cls in ("b-wash-run", "b-wash-err"):
    e(f'<rect class="wash {cls}" x="{BP_X + 0.13:.4g}" y="{b_line[1] - 0.21:.4g}" '
      f'width="{BP_W - 0.26:.4g}" height="0.44" rx="0.08"/>')
e(f'<text class="pane-code b-v1" x="{BP_X + 0.54:.4g}" y="{b_line[1]:.4g}">'
  f'<tspan class="warn">sorry</tspan></text>')
e(f'<text class="pane-code b-v2" x="{BP_X + 0.54:.4g}" y="{b_line[1]:.4g}">'
  f'<tspan class="kw">by</tspan> (induct n) auto</text>')
e(f'<text class="pane-code b-v3" x="{BP_X + 0.54:.4g}" y="{b_line[1]:.4g}">'
  f'<tspan class="kw">by</tspan> (induct n) (auto simp: power2_eq_square)</text>')

# she types `sledgehammer` on the next line, then it is replaced by the answer
ham = "sledgehammer"
ham_x = BP_X + 0.54
ham_w = 0.171 * len(ham)   # 0.6em of the .285px panel font
e(f'<clipPath id="pm-type"><rect class="type-rect" x="{ham_x:.4g}" '
  f'y="{b_line[2] - 0.3:.4g}" width="0" height="0.6"/></clipPath>')
e('<g clip-path="url(#pm-type)">')
e(f'<text class="pane-code b-ham" x="{ham_x:.4g}" y="{b_line[2]:.4g}">'
  f'<tspan class="cmd">{esc(ham)}</tspan></text>')
e('</g>')
e(f'<rect class="caret" x="{ham_x:.4g}" y="{b_line[2] - 0.22:.4g}" width="0.075" height="0.44"/>')

for key, text, tone in (("idle", "1 subgoal left", "warn"),
                        ("run", "checking…", "run"),
                        ("err", "error · Failed to finish proof", "err"),
                        ("ham", "sledgehammer: (auto simp: power2_eq_square)", "run"),
                        ("done", "finished · 0 errors", "ok")):
    e(f'<g class="pst b-st-{key} tone-{tone}">')
    e(f'<circle class="pane-dot" cx="{BP_X + 0.46:.4g}" cy="{b_sy:.4g}" r="0.1"/>')
    e(f'<text class="pane-status" x="{BP_X + 0.72:.4g}" y="{b_sy:.4g}">{esc(text)}</text>')
    e('</g>')
e('</g>')

# the message pills
for cls, word, kind in (("b-msg-out", "edit", "out"),
                        ("b-msg-state", "get_state", "out"),
                        ("b-msg-back", "1 error", "err")):
    w = 0.168 * len(word) + 0.42
    e(f'<g class="pkt {cls} k-{kind}">'
      f'<rect x="{-w/2:.4g}" y="-0.19" width="{w:.4g}" height="0.38" rx="0.19"/>'
      f'<text>{esc(word)}</text></g>')

# her, and what she says
for cls, mood in (("h-calm", "calm"), ("h-glad", "glad")):
    e(f'<g class="{cls}" transform="translate({B_HUMAN[0]},{B_HUMAN[1]}) scale({B_HS})">')
    human(mood)
    e('</g>')
# her near hand, in scene units: local (-3.75, 1.35) at B_HS
hand = (B_HUMAN[0] - 3.75 * B_HS, B_HUMAN[1] + 1.35 * B_HS)
hammer_pic(hand[0] - 0.28, hand[1] - 0.30, 1.05)

bx, by = B_HUMAN[0] - 0.35, B_HUMAN[1] - 1.62
e('<g class="bubble">')
e(f'<rect x="{bx - 1.5:.4g}" y="{by - 0.42:.4g}" width="3.0" height="0.84" rx="0.42"/>')
e(f'<path d="M{bx + 0.5:.4g},{by + 0.34:.4g} l0.34,0.5 l-0.02,-0.52 Z"/>')
e(f'<text x="{bx:.4g}" y="{by:.4g}" text-anchor="middle">let me help</text>')
e('</g>')

e('</svg>')
side = "\n".join(out)
wire_def = f'<path id="pm-wire-b" fill="none" d="{b_wire}"/>'


def bwin(name, spans):
    return windows(name, spans)


def btravel(name, a, bb, reverse=False):
    ks = [f"@keyframes {name} {{"]
    px, py = b_at(1 if reverse else 0)
    ks.append(f"  0%, {a}% {{ transform: translate({px:.4g}px, {py:.4g}px); opacity: 0; }}")
    for i in range(9):
        f = i / 8
        x, y = b_at(1 - f if reverse else f)
        pct = a + (bb - a) * f
        op = 0 if i in (0, 8) else 1
        ks.append(f"  {pct:.4g}% {{ transform: translate({x:.4g}px, {y:.4g}px); opacity: {op}; }}")
    ex, ey = b_at(0 if reverse else 1)
    ks.append(f"  {bb}%, 100% {{ transform: translate({ex:.4g}px, {ey:.4g}px); opacity: 0; }}")
    ks.append("}")
    return "\n".join(ks)


def bpulse(name, a, bb, reverse=False):
    seg = blen * 0.2
    o0 = seg if not reverse else -blen
    o1 = -blen if not reverse else seg
    return "\n".join([
        f"@keyframes {name} {{",
        f"  0%, {a}% {{ stroke-dashoffset: {o0:.4g}px; opacity: 0; }}",
        f"  {a + 1}%, {bb - 1}% {{ opacity: 1; }}",
        f"  {bb}%, 100% {{ stroke-dashoffset: {o1:.4g}px; opacity: 0; }}",
        "}"])


bcss = [f":root {{ --beat-b: {BEAT_B}s; }}"]
bcss.append(btravel("b-msg-out", E_GO, E_LAND))
bcss.append(btravel("b-msg-state", G_GO, G_LAND))
bcss.append(btravel("b-msg-back", R_BACK_A, R_BACK_B, reverse=True))
bcss.append(bpulse("b-pulse-out", E_GO, E_LAND))
bcss.append(bpulse("b-pulse-state", G_GO, G_LAND))
bcss.append(bpulse("b-pulse-back", R_BACK_A, R_BACK_B, reverse=True))
bcss.append(bwin("b-sorry", [(0, E_LAND), (RESET_B, 100)]))
bcss.append(bwin("b-near", [(E_LAND, FIXED)]))
bcss.append(bwin("b-good", [(FIXED, RESET_B)]))
bcss.append(bwin("b-run", [(E_LAND, E_FAIL), (FIXED, OK_B)]))
bcss.append(bwin("b-err", [(E_FAIL, FIXED)]))          # the red wash
bcss.append(bwin("b-errst", [(E_FAIL, HAM_B)]))        # ... its status yields sooner
bcss.append(bwin("b-idle", [(0, E_LAND), (RESET_B, 100)]))
bcss.append(bwin("b-hamst", [(HAM_B, FIXED)]))
bcss.append(bwin("b-done", [(OK_B, RESET_B)]))
bcss.append(bwin("b-hamtext", [(HAM_A, FIXED)]))
bcss.append(bwin("b-bubble", [(BUBBLE, FIXED)]))
bcss.append(bwin("b-hammer", [(HAM_A, FIXED)]))
bcss.append(bwin("bot-calm", [(0, SAD_B), (RESET_B, 100)]))
bcss.append(bwin("bot-glum", [(SAD_B, GLAD_B)]))
bcss.append(bwin("bot-glad", [(GLAD_B, RESET_B)]))
bcss.append(bwin("her-calm", [(0, GLAD_B), (RESET_B, 100)]))
bcss.append(bwin("her-glad", [(GLAD_B, RESET_B)]))
bcss.append(f"""@keyframes b-type {{
  0%, {HAM_A}% {{ width: 0; }}
  {HAM_B}%, {FIXED - 0.1}% {{ width: {ham_w:.4g}px; }}
  {FIXED}%, 100% {{ width: 0; }}
}}
@keyframes b-caret {{
  0%, {HAM_A - 0.1}% {{ opacity: 0; transform: translateX(0); }}
  {HAM_A}% {{ opacity: 1; transform: translateX(0); }}
  {HAM_B}% {{ opacity: 1; transform: translateX({ham_w:.4g}px); }}
  {FIXED - 0.1}% {{ opacity: 1; transform: translateX({ham_w:.4g}px); }}
  {FIXED}%, 100% {{ opacity: 0; transform: translateX(0); }}
}}""")
bcss.append(""".side-svg .pulse, .side-svg .pkt, .side-svg .wash, .side-svg .pst,
.side-svg .b-v1, .side-svg .b-v2, .side-svg .b-v3, .side-svg .b-ham,
.side-svg .type-rect, .side-svg .caret, .side-svg .bubble, .side-svg .b-hammer,
.side-svg .b-calm, .side-svg .b-glum, .side-svg .b-glad,
.side-svg .h-calm, .side-svg .h-glad {
  animation-duration: var(--beat-b);
  animation-iteration-count: infinite;
  animation-timing-function: steps(1);
}
.side-svg .pulse, .side-svg .pkt { animation-timing-function: linear; }
.side-svg .type-rect { animation-timing-function: steps(12, end); }
.side-svg .caret { animation-timing-function: steps(12, end); }
.side-svg .pulse, .side-svg .pkt, .side-svg .wash, .side-svg .pst,
.side-svg .b-v1, .side-svg .b-v2, .side-svg .b-v3, .side-svg .b-ham,
.side-svg .caret, .side-svg .bubble,
.side-svg .b-glum, .side-svg .b-glad, .side-svg .h-glad { opacity: 0; }
.side-svg .b-msg-out { animation-name: b-msg-out; }
.side-svg .b-msg-state { animation-name: b-msg-state; }
.side-svg .b-msg-back { animation-name: b-msg-back; }
.side-svg .b-pulse-out { animation-name: b-pulse-out; }
.side-svg .b-pulse-state { animation-name: b-pulse-state; }
.side-svg .b-pulse-back { animation-name: b-pulse-back; }
.side-svg .b-v1 { animation-name: b-sorry; }
.side-svg .b-v2 { animation-name: b-near; }
.side-svg .b-v3 { animation-name: b-good; }
.side-svg .b-wash-run { animation-name: b-run; }
.side-svg .b-wash-err { animation-name: b-err; }
.side-svg .b-st-idle { animation-name: b-idle; }
.side-svg .b-st-run { animation-name: b-run; }
.side-svg .b-st-err { animation-name: b-errst; }
.side-svg .b-st-ham { animation-name: b-hamst; }
.side-svg .b-st-done { animation-name: b-done; }
.side-svg .b-ham { animation-name: b-hamtext; }
.side-svg .type-rect { animation-name: b-type; }
.side-svg .caret { animation-name: b-caret; }
.side-svg .bubble { animation-name: b-bubble; }
.side-svg .b-hammer { animation-name: b-hammer; }
.side-svg .b-calm { animation-name: bot-calm; }
.side-svg .b-glum { animation-name: bot-glum; }
.side-svg .b-glad { animation-name: bot-glad; }
.side-svg .h-calm { animation-name: her-calm; }
.side-svg .h-glad { animation-name: her-glad; }""")

emit("side.svgfrag", side)
emit("side_wiredef.svgfrag", wire_def)
emit("side_keyframes.css", "\n\n".join(bcss) + "\n")
print(f"side scene {len(side)}B, wire {blen:.2f}")

# ==================================================== the PIDE MCP glyph ====
# Two cans and a bit of string: the thing itself, not the agent holding it.

out.clear()
_gl, _gr, _sag = -1.95, 1.95, 0.42
_a = (_gl + LH, 0)
_d = (_gr - LH, 0)
e('<svg class="start-logo wire-logo" viewBox="-2.95 -0.95 5.9 2.1" aria-hidden="true">')
e(f'<path fill="none" stroke="{C["twine"]}" stroke-width="{3.4*PT:.4g}" stroke-linecap="round" '
  f'd="M{_a[0]:.4g},{_a[1]} C{_a[0] + 1.0:.4g},{_sag:.4g} {_d[0] - 1.0:.4g},{_sag:.4g} '
  f'{_d[0]:.4g},{_d[1]}"/>')
tincan(_gl, 0, 1, 1)
tincan(_gr, 0, 1, -1)
e('</svg>')
emit("wire_glyph.svgfrag", "\n".join(out))
print("wire glyph", len("\n".join(out)), "B")
