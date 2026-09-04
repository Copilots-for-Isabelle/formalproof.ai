"""Check the things about index.html that are easy to break by hand.

Everything here is an invariant the page actually relies on, not style
policing. Each check exists because the thing it guards drifted at least
once: the title and og:title fell out of step twice while the copy was
being tuned, and neither the browser nor a linter says a word about it.

Run with `make check`. Exits non-zero if anything is wrong.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAGE = os.path.join(ROOT, "index.html")

# Google truncates by pixel width, not characters, so these are the usual
# rules of thumb: ~600px of title, and a description that survives on a
# phone, which is the tighter of the two budgets.
TITLE_MAX = 60
DESC_MAX = 120

problems = []
notes = []


def bad(msg):
    problems.append(msg)


def one(html, pattern, what):
    """Exactly one match, or it is a problem worth naming."""
    found = re.findall(pattern, html, re.S)
    if len(found) != 1:
        bad(f"expected exactly one {what}, found {len(found)}")
        return None
    return found[0]


html = open(PAGE, encoding="utf-8").read()
head = html[: html.index("</head>")]

# ---- the pairs that must agree -------------------------------------------
# Each string lives in two places because the standards demand it and the
# page has no build step to generate one from the other.
title = one(html, r"<title>(.*?)</title>", "<title>")
og_title = one(html, r'<meta property="og:title" content="(.*?)">', "og:title")
desc = one(html, r'<meta name="description" content="(.*?)">', "meta description")
og_desc = one(html, r'<meta property="og:description" content="(.*?)">', "og:description")

if title and og_title and title != og_title:
    bad(f"<title> and og:title differ:\n    title    {title!r}\n    og:title {og_title!r}")
if desc and og_desc and desc != og_desc:
    bad("meta description and og:description differ:\n"
        f"    meta {desc!r}\n    og   {og_desc!r}")

# ---- lengths -------------------------------------------------------------
if title and len(title) > TITLE_MAX:
    bad(f"title is {len(title)} chars, over {TITLE_MAX}: {title!r}")
if desc and len(desc) > DESC_MAX:
    bad(f"description is {len(desc)} chars, over {DESC_MAX}: {desc!r}")

# ---- twitter:* must stay absent -----------------------------------------
# X falls back to og:* for all of these. Adding them back just creates a
# second copy of every string to keep in step.
for tag in ("twitter:title", "twitter:description", "twitter:image", "twitter:image:alt"):
    if f'name="{tag}"' in head:
        bad(f"{tag} is back; it duplicates the og: tag it falls back to")
if 'name="twitter:card"' not in head:
    bad("twitter:card is missing; it is the one twitter tag with no og: equivalent")

# ---- one language, declared consistently ---------------------------------
lang = one(html, r'<html lang="(.*?)"', "<html lang>")
locale = one(html, r'<meta property="og:locale" content="(.*?)">', "og:locale")
if lang and locale and lang.replace("-", "_") != locale:
    bad(f"lang {lang!r} and og:locale {locale!r} disagree")

# ---- structured data -----------------------------------------------------
raw = one(html, r'<script type="application/ld\+json">(.*?)</script>', "JSON-LD block")
graph = []
if raw:
    try:
        graph = json.loads(raw)["@graph"]
    except (ValueError, KeyError) as exc:
        bad(f"JSON-LD does not parse: {exc}")

ids = {n.get("@id") for n in graph}
for node in graph:
    for key, value in node.items():
        # every internal @id reference must resolve to a node in the graph
        refs = value if isinstance(value, list) else [value]
        for ref in refs:
            if isinstance(ref, dict) and set(ref) == {"@id"}:
                target = ref["@id"]
                if target.startswith("https://formalproof.ai/#") and target not in ids:
                    bad(f"JSON-LD {node.get('@id')} -> {key} points at missing {target}")

for node in graph:
    if node.get("inLanguage") and lang and node["inLanguage"] != lang:
        bad(f"JSON-LD {node.get('@id')} inLanguage {node['inLanguage']!r} != lang {lang!r}")

# The title's opening phrase names the topic entity. If the subject of the
# site is renamed, both move together.
topic = next((n for n in graph if n.get("@id", "").endswith("#topic")), None)
if topic and title and not title.startswith(topic["name"]):
    bad(f"title {title!r} no longer opens with the topic name {topic['name']!r}")

# ---- house style, metadata only -----------------------------------------
# Dashes read as machine-written in a search result. The page copy uses them
# freely; this only covers the head.
for dash in ("–", "—"):
    if dash in head:
        bad(f"{dash!r} in the metadata; spell the sentence out instead")

# ---- US spelling in anything a reader or screen reader gets --------------
body = html[html.index("<body>"):]
body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S)
visible = re.sub(r"<[^>]+>", " ", body) + " " + " ".join(
    re.findall(r'(?:alt|aria-label|title)="([^"]*)"', body))
BRITISH = ["licence", "labelled", "formalis", "organis", "recognis", "analyse",
           "behaviour", "colour", "centre", "defence", "modelling", "grey",
           "catalogue", "programme", "whilst", "specialis", "optimis", "amongst"]
for word in BRITISH:
    # aria-labelledby is an attribute name, not prose, and must keep its spelling
    hits = [m for m in re.finditer(word, visible, re.I)]
    if hits:
        bad(f"British spelling {word!r} in user-facing text ({len(hits)}x)")

# ---- the sitemap's lastmod is the only field crawlers read ---------------
# It helps only while it is true. Google ignores changefreq and priority, so
# they are absent on purpose; if they come back, they are noise at best and a
# reason to distrust lastmod at worst.
sitemap = os.path.join(ROOT, "sitemap.xml")
if os.path.exists(sitemap):
    sm = open(sitemap, encoding="utf-8").read()
    for dead in ("changefreq", "priority"):
        if f"<{dead}>" in sm:
            bad(f"sitemap has <{dead}>, which every major crawler ignores")
    stamp = re.search(r"<lastmod>([0-9-]+)</lastmod>", sm)
    if not stamp:
        bad("sitemap has no <lastmod>, the one field that is read")
    else:
        # the page's real last change, straight from git when it is available
        try:
            import subprocess
            real = subprocess.run(
                ["git", "-C", ROOT, "log", "-1", "--format=%ad", "--date=short",
                 "--", "index.html"],
                capture_output=True, text=True, timeout=10).stdout.strip()
        except Exception:
            real = ""
        if real and stamp.group(1) < real:
            bad(f"sitemap lastmod {stamp.group(1)} predates the last change to "
                f"index.html ({real})")
        elif real:
            notes.append(f"sitemap     lastmod {stamp.group(1)}, page last changed {real}")

# ---- local assets referenced actually exist ------------------------------
for ref in sorted(set(re.findall(r'(?:href|src)="((?!https?:|#|mailto:)[^"]+)"', html))):
    if not os.path.exists(os.path.join(ROOT, ref.split("?")[0])):
        bad(f"missing file: {ref}")

# ---- report --------------------------------------------------------------
if title:
    notes.append(f"title       {len(title):3} chars  {title}")
if desc:
    notes.append(f"description {len(desc):3} chars  {desc}")
if graph:
    notes.append(f"JSON-LD     {len(graph)} nodes")
print("\n".join(notes))

if problems:
    print("\n" + "\n".join("FAIL  " + p for p in problems), file=sys.stderr)
    sys.exit(1)
print("\nall checks passed")
