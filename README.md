# formalproof.ai

The static one-page site published at **https://formalproof.ai**. It makes the
case for agentic formal proof: AI writes proofs, a proof assistant checks every
step, and Isabelle is the one to reach for. The server it points at,
[`isabelle-pide-mcp`](https://github.com/kappelmann/isabelle-pide-mcp), lives in
its own repository.

```
index.html                the whole page, including one inline script
assets/style.css          light + dark, responsive
assets/isabelle.svg       Isabelle logo (-dark: wordmark lightened)
assets/og.png             social card, 1200x630
assets/favicon.svg  assets/apple-touch-icon.png
CNAME  .nojekyll  robots.txt  sitemap.xml
Makefile                  the chores; there is no build
tools/check.py            invariants that break silently
tools/gen_scene.py        illustration generator
tools/gen_mcp.py          the "It speaks MCP" band
```

No build step and no dependencies. `index.html` **is** the artifact: edit it,
save, reload. Nothing compiles it and nothing generates it from anything else.

## Working on it

```bash
make serve      # http://localhost:8000, PORT=... to move it
make check      # before you push
make help       # the list
```

`make check` reads `index.html` and fails on what nothing else notices:

- `<title>` and `og:title`, or the two descriptions, drifting apart — each
  string lives in two places because the standards require it, and no browser
  complains when they disagree
- a title over 60 characters or a description over 120, the mobile budget
- `twitter:title`/`twitter:description`/`twitter:image` reappearing; X falls
  back to `og:*`, so they are pure duplication
- `lang`, `og:locale` and JSON-LD `inLanguage` disagreeing
- JSON-LD that does not parse, or an `@id` pointing at no node
- a dash in the metadata, or a British spelling anywhere a reader or screen
  reader reaches
- `href`/`src` pointing at a file that is not there

### Search and social copy

The title and description sit together at the top of `<head>` under a comment
naming each. Both are mirrored once as `og:` tags; change the pair. Google shows
the title as the blue link and the description as the snippet, and rewrites the
description about half the time anyway, usually lifting a sentence off the page
— so the hero copy does search work too.

## The page

The order is the argument. Keep it in order:

1. **AI can do the mathematics. Certainty needs a checker.** — the problem
2. **Isabelle is that checker, and it is already frontier.** — seL4, the AWS
   Nitro Isolation Engine, the AFP
3. **So put your agent on the line with Isabelle.** — what PIDE MCP is, the
   animated figure, the four things it does
4. **It speaks MCP.** — whichever agent you already use
5. **Let it work on its own, or work beside it.**
6. **Point it at the hard things.** — what people use Isabelle for
7. **Get started today.** — Isabelle · PIDE MCP · preprint · support

### Claims to re-check if you edit them

- **seL4** — first OS kernel with a machine-checked functional-correctness
  proof. The card names air-traffic and maritime control, from
  [seL4 in use](https://sel4.systems/use.html). Defense deployments are left
  out on purpose: civil examples only.
- **AWS Nitro Isolation Engine** — first formally verified hypervisor in a
  commercial cloud, verified in Isabelle/HOL.
- **Apple corecrypto** — ML-KEM and ML-DSA proved correct; Isabelle is in the
  chain via Galois's `cryptol-to-isabelle` translator, alongside SAW and Cryptol.
- **AFP** — "more than 950 refereed developments" is a floor, not a snapshot:
  the April 2026 release has 967 entries, devel 1012.

Proof-size figures are kept off the cards: they invite comparison and go stale.

### The Isabelle examples are real

Every proof on the page was run against a live Isabelle, and the entity lookup
quotes real source:

| shown | checked |
|---|---|
| `by auto` on `"(∑i<n. 2*i+1) = (n::nat)^2"` | fails — *Failed to finish proof* |
| `by (induct n) auto` | fails — the `Suc` step is left |
| `by (induct n) (auto simp: power2_eq_square)` | succeeds |
| `by simp` on `"continuous_on S (λx::real. x * sin x)"` | fails — *Failed to apply initial proof method* |
| `by (intro continuous_intros)` | succeeds |
| `Cauchy X = cauchy_filter (filtermap X sequentially)` at `HOL.Topological_Spaces:3557` | verbatim, via `find_entities` |

Check any example you change. The plausible-looking ones bite: a lemma that
looks like it needs work often closes on the spot because the library already
marks the key fact `[simp]`.

## The illustrations

The robot, the tin cans and the twine are transcribed by hand from the TikZ
`pic`s in the AI4Math convening slides (`slides/ai4math_convening/preamble.tex`
in `copilots-isabelle`) — same geometry, same palette.

The generators are one-shot. The committed HTML and CSS are the source of truth,
so the page cannot be regenerated as a whole, and is not meant to be:

- **`make scene`** writes `.svgfrag` and `*_keyframes.css` into the repo root
  for you to paste. Its output has fallen behind the committed HTML, so read the
  diff before pasting.
- **`make mcp`** rewrites the *It speaks MCP* band inside `index.html` in place
  — the one target that edits the page. Commit first, then read `git diff`.

Both resolve paths from their own location: they run from any directory and
never write outside the checkout. When you change a scene by hand, change the
generator too if the value lives there.

`esc()` in the generator matters: Isabelle source is full of `<` and `&`, and
SVG text is markup. Without it `"(∑i<n. 2*i+1)"` truncates at the `<`.

### Constraints that will bite

- CSS descendant selectors cannot reach into a `<use>` shadow tree, so a
  per-instance mood needs its own `<defs>` entry (`#pm-robot-calm`,
  `#pm-robot-glum`, `#pm-robot-glad`).
- For the same reason `.saw { animation-name: saw-spin }` cannot be scoped to
  one scene: it drives every robot on the page off the main scene's timeline.
  The story robot's tools carry `saw-story`/`flutes-story`.
- An `animation:` shorthand after an `animation-name:` on the same element
  silently resets the name to `none`. The lane-three block uses longhand
  throughout for that reason.
- `dominant-baseline` is set on both `text` and `tspan` in the panels. WebKit
  does not inherit it into `<tspan>`, so a line with a keyword in a tspan and
  the rest bare splits across two baselines in Safari.

### The main scene: 24 seconds

One agent, three sessions. Two are proving; the third does not exist yet.

**Isabelle checks on its own clock.** The verdicts land at 21%, 24%, 59% and
62% — each while the matching `get_state` is still in flight. The `get_state`
legs leave before the verdict exists and arrive after it. That is the point;
preserve it if you retime anything.

| cycle | lane 1 — HOL | lane 2 — HOL-Analysis | lane 3 — HOL-Probability | face |
|---|---|---|---|---|
| 2–13% | `edit` → `by auto` | `edit` → `by simp` | | |
| 12–20% | | | `start_session`, comes up empty | |
| 18–29% | `get_state` → | `get_state` → | | |
| 21/24% | prover: **error** | prover: **error** | | |
| 24–32% | | | `read` — a theory lands | |
| 28–39% | ← `1 error` | ← `1 error` | | |
| 39% | | | | 🙁 |
| 38–52% | | | `find_entities` → **7 entities** | |
| 40–51% | `edit` → `(induct n)` | `edit` → `(intro …)` | | |
| 52–60% | | | ← the hits; Cauchy's snippet | |
| 54–65% | `get_state` → | `get_state` → | | |
| 59/62% | prover: **finished** | prover: **finished** | | |
| 64–75% | ← `✓ 0 errors` | ← `✓ 0 errors` | | |
| 66–82% | | | `stop_session`, string reeled in | |
| 75–98% | | | | 🙂 + saw and drill |
| 98% | reset | reset | | |

Reading time is the binding constraint: the third session is alive for 13s, its
snippet is up for 5.3s, the smile holds 5.5s. Check those first if you retime.
The wires, the face and the three panels share one timeline (`--beat`), so
changing one lane means changing the others.

Lane three is the whole session lifecycle. Its wire animates
`stroke-dashoffset`, so the string is genuinely thrown and reeled back in; the
can, the panel and the tag's third bullet fade with it.

`find_entities` on a whole line returns everything in it — seven entities across
four files for that statement. The panel says `7 entities` and previews the
interesting one rather than pretending the tool is more surgical than it is.

The saw and the drill run only while the robot is smiling: a lap of honor, not
idle fidgeting. Both sit on the 18s cycle, and 1440° / ten flute pitches land
where they started so the wrap is invisible.

Under `prefers-reduced-motion` nothing moves: messages park on their wires, the
tools stop, the face stays straight, every panel shows its starting state.

### The MCP band

Four agent cells around a center Isabelle editor. One cell holds the line at a
time and the editor names it, chosen by a three-tier CSS cascade written out per
property because a `:has()` tier cannot be factored: the cell being pointed at,
else the cell with `:focus`, else `.a-cc` as the resting default. `:focus` is
what makes a choice stick after the pointer leaves, since CSS has no memory of
"last hovered".

Taking the line runs the handshake: wire and cans appear, `initialize` travels
at 0.15s, `response` returns at 1.35s, and at 2.35s the robot smiles and the
status flips. Mood and status share that delay so they cross-fade. The delay
sits on the lit rule only, so an agent that loses the line drops the smile at
once.

Each cell carries its own wire and packets, because each client starts its own
PIDE MCP with its own sessions. Nothing is shared between them: do not draw them
running into a single hub.

The tools spin only while a robot is engaged. That cannot be scoped with a
descendant selector, so it rides on inherited custom properties (`--tool-spin`,
`--tool-flute`).

### Side by side

The robot at one end of a wire, a woman in glasses at the other, and **one**
file panel between them. Over 12s the agent replaces `sorry` with a real proof
and she types into the same buffer; the point is one file, not two views of two
files. `human()` draws her in the robot's vocabulary — same stroke weights,
joints and rounded torso — so the two read as a pair.

The typing is a `clipPath` rect whose `width` is animated with `steps(n)`, with
a caret rect translating to match. SVG geometry properties are CSS-animatable in
current browsers; if that regresses, reveal the note in word-sized `<tspan>`
chunks instead.

## Layout and motion

### One chapter to a screen

Four chapters — hero, Isabelle, PIDE MCP, Get started — each `height: 100svh`
and centered. The three subsections under PIDE MCP (`.mcp`, `.beside`, `.uses`)
are deliberately *not* screens: they flow, because snapping between them jumps
the reader through what should read as one stretch.

Snapping is `mandatory`, so a chapter arrives decisively. What makes that safe
is `.pide-block`, the wrapper around the PIDE MCP chapter *and* its subsections:
it is the snap target, so the reader snaps into the chapter and is then left
alone for the whole stretch below. A snap area taller than the viewport does not
trap. Remove that wrapper and mandatory snapping has nothing to hold between
PIDE MCP and Get started.

Three things this depends on:

- The height must be *definite* (`height`, not `min-height`). Flex children only
  give up space when their box has a height to divide.
- `main > section` is two type selectors, specificity 0-0-2, which any class
  rule beats. The chapter rule is written `main > .hero, main > .why, ...`.
- The main scene is capped with `max-height` in `svh` rather than grown. A
  growing box eats leftover space and pushes the scene to the bottom; capping
  keeps it centered, and it is what keeps the PIDE MCP chapter inside its
  screen. Re-check it if the scene or the copy grows.

Below 620px tall or 700px wide this reverts to an ordinary scrolling page and
the rail and cues are hidden.

The reveal is `animation-timeline: view()` on each chapter's children, declared
with no duration, so a browser without scroll timelines runs it in 0s and shows
the end state — nothing is ever left invisible. `.scroll-cue` is excluded: the
reveal ends on `transform: none`, which would undo the cue's positioning.

### Finding your way

`nav.rail` is four dots fixed to the right edge, one per chapter, labeled on
hover. Chevrons carry the reader forward: a full-size bobbing `.scroll-cue`
between chapters, a smaller still `.cue-sub` into the subsections, and
`.cue-flow` out of them — `.uses` is not a screen, so it sits in the flow.

Marking *which* chapter you are in is the one thing CSS cannot do: it has no
cross-element scroll position, and `timeline-scope` is not honored by Firefox
155. So the page carries one small inline script that finds the chapter owning
the point a third of the way down the viewport and puts `.is-here` on its dot.
The subsections have no dot, so PIDE MCP keeps the mark throughout them.

The same script measures the footer and publishes `--footer-h`. The closing
chapter is `calc(100svh - var(--footer-h))` and snaps to `start`, so the snap
position holds chapter and footer together.

Everything else runs without script; the `:target` rules are the fallback.

### Headings and narrow screens

Three `h2`s — *Meet Isabelle*, *Meet PIDE MCP*, *Get started today* — with
everything between the second and third an `h3` under PIDE MCP, set smaller so
the nesting reads. Each chapter opens with `<hr class="chapter">`, a length of
twine with a knot in it. The HTML rendering spec gives `hr` `overflow: hidden`,
which clips the knot, so the rule sets `overflow: visible`.

All three scenes carry code that would shrink past legibility, so below their
own breakpoint each wrapper scrolls sideways: main scene 820px, side scene
780px, MCP band 700px. Each has its own `.cap-hint-*` shown at that width. Keep
the class per scene — a bare `.cap-hint` rule lights all three at whichever
breakpoint fires first.

## Publishing

- `assets/og.png` is the social card, rendered headless from the page's own
  artwork. Regenerate it if the headline changes; the card should match `<h1>`.
- `assets/apple-touch-icon.png` is the 180x180 raster fallback for crawlers and
  home screens that will not take the SVG favicon.
- `robots.txt` points at `sitemap.xml`; bump its `lastmod` on substantial
  changes.
- The fonts come from Google Fonts and are render-blocking. Self-hosting Inter
  and JetBrains Mono is the next real speed win.

GitHub Pages, from the repository root:

1. Repository → Settings → Pages
2. *Source*: **Deploy from a branch**
3. *Branch*: `main`, folder `/ (root)`
4. *Custom domain*: `formalproof.ai` (already recorded in `CNAME`)

Pages will not publish from a private repository unless the organization is on a
paid plan, so this one stays public.

DNS for the apex domain needs `A` records at GitHub's Pages addresses
(`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`)
plus the matching `AAAA` set, or an `ALIAS`/`ANAME` to
`copilots-for-isabelle.github.io`. Enable *Enforce HTTPS* once the certificate
is issued.

## Keeping the copy honest

The page names the supported Isabelle version and the agents PIDE MCP ships
configuration for. Those live in the server repository, so when they change
there, update the `.works` line in `index.html`.
