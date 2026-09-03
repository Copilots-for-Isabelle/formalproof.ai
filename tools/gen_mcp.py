# One-shot generator for the MCP band: four agent cells around a centre editor.
import os, re, io

SC   = 0.34                       # robot scale in the cells
CX   = 7.05                        # cell centre, x
CY   = 1.75                       # cell centre, y
EW, EH = 5.4, 2.3                 # editor box
# the cells hang their name plates below the robots, so their optical centre
# sits lower than the robot centres -- drop the editor to match
EOY = 0.44
EX, EY = -EW/2, -EH/2 + EOY
HEAD = 0.55
ROW  = [0.14, 0.56]               # code baselines
SEP  = 0.86
STY  = 1.23                       # status baseline

def cell(key, name, x, y, aria, mini=False):
    """One agent: robot (calm/glad), name plate, wire to the editor, two packets."""
    left  = x < 0
    sx    = -1 if left else 1
    inner = x - sx * -4.93 if False else (x + sx*(-1.67))     # robot edge facing the editor
    ex    = EX if left else EX + EW                            # editor edge
    ey    = EOY - 0.6 if y < 0 else EOY + 0.6
    CS = 0.28                     # tin-can scale, matched to the robot
    LIP = 0.6 * CS                # mouth / string offsets inside the can
    u  = 1 if left else -1        # direction from this cell towards the editor
    # a can at each end, mouth towards its owner, string towards the other side
    can_r = inner + u * (0.10 + LIP)          # centre of the robot-side can
    can_e = ex - u * (0.22 + LIP)             # centre of the editor-side can
    wx0, wx1 = can_r + u * LIP, can_e - u * LIP
    o = io.StringIO()
    w = o.write
    w(f'    <g class="agent {key}" role="img" aria-label="{aria}" tabindex="0">\n')
    # the whole cell, plate included: the mini plate is wider than the robots
    # and has no fill, so its ends were not catching the pointer
    hw = 2.15 if mini else 1.9
    w(f'    <rect class="hit" x="{x-hw:.2f}" y="{y-1.15:.2f}" width="{2*hw:.2f}" height="2.95" rx="0.3"/>\n')
    # -- connection: wire, then the two messages that ride it
    w(f'    <g class="conn">\n')
    w(f'    <path class="wire-c" d="M{wx0:.2f},{y:.2f} Q{(wx0+wx1)/2:.2f},{y:.2f} {wx1:.2f},{ey:.2f}"/>\n')
    w(f'    <g transform="translate({can_r:.2f},{y:.2f}) scale({-u*CS:.3f},{CS})"><use href="#pm-can"/></g>\n')
    w(f'    <g transform="translate({can_e:.2f},{ey:.2f}) scale({u*CS:.3f},{CS})"><use href="#pm-can"/></g>\n')
    # the pills ride between the two cans
    ax, ay = wx0 + 0.30 * u, y
    bx, by = wx1 - 0.30 * u, ey
    dx, dy = bx - ax, by - ay
    for cls, label, kind, sgn in (("pk-out", "initialize", "k-out", 1), ("pk-in", "response", "k-ok", -1)):
        px, py = (ax, ay) if sgn > 0 else (bx, by)
        hw = (len(label) * 0.126 + 0.26) / 2
        w(f'    <g transform="translate({px:.2f},{py:.2f})">'
          f'<g class="pk {cls}" style="--dx:{sgn*dx:.2f}px;--dy:{sgn*dy:.2f}px">'
          f'<rect class="pk-box {kind}" x="{-hw:.3f}" y="-0.19" width="{2*hw:.3f}" height="0.38" rx="0.19"/>'
          f'<text class="pk-text {kind}">{label}</text></g></g>\n')
    w('    </g>\n')
    # -- the robot itself
    if mini:
        for mx, my, s in ((-0.62, -0.18, 0.17), (0.62, -0.18, 0.17), (0.0, 0.30, 0.17)):
            w(f'    <g transform="translate({x+mx:.2f},{y+my:.2f}) scale({s})">\n'
              f'    <use class="r-calm" href="#pm-robot-calm"/>\n'
              f'    <use class="r-glad" href="#pm-robot-glad"/>\n    </g>\n')
    else:
        w(f'    <g transform="translate({x:.2f},{y:.2f}) scale({SC})">\n'
          f'    <use class="r-calm" href="#pm-robot-calm"/>\n'
          f'    <use class="r-glad" href="#pm-robot-glad"/>\n    </g>\n')
    cls = "plate mini" if mini else "plate"
    tcl = "plate-text mini" if mini else "plate-text"
    pw  = 3.9 if mini else 3.4
    w(f'    <rect class="{cls}" x="{x-pw/2:.2f}" y="{y+0.95:.2f}" width="{pw}" height="0.6" rx="0.3"/>\n')
    w(f'    <text class="{tcl}" x="{x:.2f}" y="{y+1.25:.2f}" text-anchor="middle">{name}</text>\n')
    w('    </g>\n')
    return o.getvalue()

E = io.StringIO(); w = E.write
w('    <g class="mcp-editor">\n')
w(f'    <rect class="pane" x="{EX}" y="{EY}" width="{EW}" height="{EH}" rx="0.22"/>\n')
w(f'    <rect class="pane-head" x="{EX}" y="{EY}" width="{EW}" height="{HEAD}" rx="0.22"/>\n')
w(f'    <path class="pane-sep" d="M{EX},{EY+HEAD}h{EW}"/>\n')
w(f'    <path class="pane-sep" d="M{EX},{SEP}h{EW}"/>\n')
for cl, src in (("badge-light", "assets/isabelle.svg"), ("badge-dark", "assets/isabelle-dark.svg")):
    w(f'    <image class="isa-badge {cl}" href="{src}" x="{EX+0.18:.2f}" y="{EY+0.07:.2f}" '
      f'width="0.42" height="0.42" preserveAspectRatio="xMidYMid meet"/>\n')
w(f'    <text class="pane-logic" x="{EX+0.76:.2f}" y="{EY+HEAD/2:.2f}">HOL</text>\n')
w(f'    <text class="pane-file" x="{EX+EW-0.18:.2f}" y="{EY+HEAD/2:.2f}" text-anchor="end">Scratch.thy</text>\n')
# every run in its own tspan: Safari puts a bare text node and a tspan
# sibling on different baselines
code = [('<tspan class="kw">theorem</tspan><tspan> </tspan>'
         '<tspan class="str">"sqrt 2 \u2209 \u211a"</tspan>', 0.30),
        ('<tspan>  </tspan><tspan class="warn">sorry</tspan>', 0.30)]
for (txt, px), y in zip(code, ROW):
    w(f'    <text class="pane-code" x="{EX+px:.2f}" y="{y:.2f}">{txt}</text>\n')
# one status per client: the editor names whoever currently holds the line
w(f'    <g class="st-none tone-dim"><circle class="pane-dot" cx="{EX+0.30:.2f}" cy="{STY}" r="0.1"/>'
  f'<text class="pane-status" x="{EX+0.54:.2f}" y="{STY}">no client connected</text></g>\n')
for cls, who in (("st-cc", "Claude Code"), ("st-codex", "Codex"),
                 ("st-oc", "OpenCode"), ("st-more", "your agent")):
    w(f'    <g class="st {cls} tone-ok"><circle class="pane-dot" cx="{EX+0.30:.2f}" cy="{STY}" r="0.1"/>'
      f'<text class="pane-status" x="{EX+0.54:.2f}" y="{STY}">connected \u00b7 {who}</text></g>\n')
w('    </g>\n')

body = (
'    <svg class="mcp-svg" viewBox="-9.25 -2.9 18.5 6.4" role="img" aria-labelledby="mcT mcD">\n'
'    <title id="mcT">Coding agents that speak MCP</title>\n'
'    <desc id="mcD">Four coding agents around an Isabelle editor. Point at one and it opens its own '
'connection: an initialize message goes out, a response comes back, and the editor names it. Claude Code holds the line until another agent takes it.</desc>\n'
  + E.getvalue()
  + cell("a-cc",    "Claude Code", -CX, -CY, "Claude Code")
  + cell("a-codex", "Codex",       -CX,  CY, "Codex")
  + cell("a-oc",    "OpenCode",     CX, -CY, "OpenCode")
  + cell("a-more",  "…and many others", CX, CY, "and many other MCP clients", mini=True)
  + '    </svg>\n')

# the repo root, from this file: never depends on the working directory,
# and never reaches outside the checkout
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
p = os.path.join(ROOT, "index.html")

h = open(p).read()
i = h.index('    <svg class="mcp-svg"')
j = h.index('    </svg>\n', i) + len('    </svg>\n')
open(p, "w").write(h[:i] + body + h[j:])
print(body[:1200])
