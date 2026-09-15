"""Check the things about the pages that are easy to break by hand.

Everything here is an invariant a page actually relies on, not style
policing. Each check exists because the thing it guards drifted at least
once: the title and og:title fell out of step twice while the copy was
being tuned, and neither the browser nor a linter says a word about it.

Every check runs against every page. The one exception is the topic check,
which applies only where the JSON-LD names a topic entity; the home page
does and the quick start does not.

Run with `make check`. Exits non-zero if anything is wrong.
"""

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Each page carries the full set of head invariants. Order is the order the
# report prints them in.
PAGES = ["index.html", os.path.join("quick-start", "index.html")]

# The URL a page is published at, for matching sitemap entries to files.
URLS = {
    "index.html": "https://formalproof.ai/",
    os.path.join("quick-start", "index.html"): "https://formalproof.ai/quick-start/",
}

# Google truncates by pixel width, not characters, so these are the usual
# rules of thumb: ~600px of title, and a description that survives on a
# phone, which is the tighter of the two budgets.
TITLE_MAX = 60
DESC_MAX = 120

BRITISH = ["licence", "labelled", "formalis", "organis", "recognis", "analyse",
           "behaviour", "colour", "centre", "defence", "modelling", "grey",
           "catalogue", "programme", "whilst", "specialis", "optimis", "amongst"]

problems = []
notes = []


def bad(msg):
    problems.append(msg)


def one(html, pattern, what, where):
    """Exactly one match, or it is a problem worth naming."""
    found = re.findall(pattern, html, re.S)
    if len(found) != 1:
        bad(f"{where}: expected exactly one {what}, found {len(found)}")
        return None
    return found[0]


def last_change(rel):
    """The file's real last change, straight from git when it is available."""
    try:
        import subprocess
        return subprocess.run(
            ["git", "-C", ROOT, "log", "-1", "--format=%ad", "--date=short",
             "--", rel],
            capture_output=True, text=True, timeout=10).stdout.strip()
    except Exception:
        return ""


def check_page(rel):
    """Every invariant that lives inside one page."""
    path = os.path.join(ROOT, rel)
    html = open(path, encoding="utf-8").read()
    head = html[: html.index("</head>")]

    # ---- the pairs that must agree ---------------------------------------
    # Each string lives in two places because the standards demand it and the
    # site has no build step to generate one from the other.
    title = one(html, r"<title>(.*?)</title>", "<title>", rel)
    og_title = one(html, r'<meta property="og:title" content="(.*?)">', "og:title", rel)
    desc = one(html, r'<meta name="description" content="(.*?)">', "meta description", rel)
    og_desc = one(html, r'<meta property="og:description" content="(.*?)">', "og:description", rel)

    if title and og_title and title != og_title:
        bad(f"{rel}: <title> and og:title differ:\n"
            f"    title    {title!r}\n    og:title {og_title!r}")
    if desc and og_desc and desc != og_desc:
        bad(f"{rel}: meta description and og:description differ:\n"
            f"    meta {desc!r}\n    og   {og_desc!r}")

    # ---- lengths ---------------------------------------------------------
    if title and len(title) > TITLE_MAX:
        bad(f"{rel}: title is {len(title)} chars, over {TITLE_MAX}: {title!r}")
    if desc and len(desc) > DESC_MAX:
        bad(f"{rel}: description is {len(desc)} chars, over {DESC_MAX}: {desc!r}")

    # ---- twitter:* must stay absent --------------------------------------
    # X falls back to og:* for all of these. Adding them back just creates a
    # second copy of every string to keep in step.
    for tag in ("twitter:title", "twitter:description", "twitter:image", "twitter:image:alt"):
        if f'name="{tag}"' in head:
            bad(f"{rel}: {tag} is back; it duplicates the og: tag it falls back to")
    if 'name="twitter:card"' not in head:
        bad(f"{rel}: twitter:card is missing; it is the one twitter tag with no og: equivalent")

    # ---- one language, declared consistently -----------------------------
    lang = one(html, r'<html lang="(.*?)"', "<html lang>", rel)
    locale = one(html, r'<meta property="og:locale" content="(.*?)">', "og:locale", rel)
    if lang and locale and lang.replace("-", "_") != locale:
        bad(f"{rel}: lang {lang!r} and og:locale {locale!r} disagree")

    # ---- structured data -------------------------------------------------
    raw = one(html, r'<script type="application/ld\+json">(.*?)</script>', "JSON-LD block", rel)
    graph = []
    if raw:
        try:
            graph = json.loads(raw)["@graph"]
        except (ValueError, KeyError) as exc:
            bad(f"{rel}: JSON-LD does not parse: {exc}")

    ids = {n.get("@id") for n in graph}
    for node in graph:
        for key, value in node.items():
            # every internal @id reference must resolve to a node in the graph
            refs = value if isinstance(value, list) else [value]
            for ref in refs:
                if isinstance(ref, dict) and set(ref) == {"@id"}:
                    target = ref["@id"]
                    if target.startswith("https://formalproof.ai/#") and target not in ids:
                        bad(f"{rel}: JSON-LD {node.get('@id')} -> {key} "
                            f"points at missing {target}")

    for node in graph:
        if node.get("inLanguage") and lang and node["inLanguage"] != lang:
            bad(f"{rel}: JSON-LD {node.get('@id')} inLanguage "
                f"{node['inLanguage']!r} != lang {lang!r}")

    # The title's opening phrase names the topic entity, where there is one.
    # If the subject of the page is renamed, both move together.
    topic = next((n for n in graph if n.get("@id", "").endswith("#topic")), None)
    if topic and title and not title.startswith(topic["name"]):
        bad(f"{rel}: title {title!r} no longer opens with the topic name {topic['name']!r}")

    # ---- house style, metadata only --------------------------------------
    # Dashes read as machine-written in a search result. The page copy uses
    # them freely; this only covers the head.
    for dash in ("–", "—"):
        if dash in head:
            bad(f"{rel}: {dash!r} in the metadata; spell the sentence out instead")

    # ---- US spelling in anything a reader or screen reader gets -----------
    body = html[html.index("<body>"):]
    body = re.sub(r"<script.*?</script>|<style.*?</style>", " ", body, flags=re.S)
    visible = re.sub(r"<[^>]+>", " ", body) + " " + " ".join(
        re.findall(r'(?:alt|aria-label|title)="([^"]*)"', body))
    for word in BRITISH:
        # aria-labelledby is an attribute name, not prose, and keeps its spelling
        hits = [m for m in re.finditer(word, visible, re.I)]
        if hits:
            bad(f"{rel}: British spelling {word!r} in user-facing text ({len(hits)}x)")

    # ---- every image says what it is -------------------------------------
    # Crawlers read alt and nothing else about an image, and a reader with
    # images off or a screen reader gets the same text. An empty alt is the
    # right answer for genuinely decorative art, but only when the image is
    # also hidden from assistive tech, so say so explicitly.
    for tag in re.findall(r"<img\b[^>]*>", html, re.S):
        flat = " ".join(tag.split())
        alt = re.search(r'\salt="([^"]*)"', flat)
        if alt is None:
            bad(f"{rel}: <img> with no alt: {flat[:90]}")
        elif not alt.group(1).strip() and 'aria-hidden="true"' not in flat:
            bad(f"{rel}: <img> with an empty alt and no aria-hidden: {flat[:90]}")

    # ---- local assets referenced actually exist --------------------------
    # Resolved against the page, not the root: the quick start reaches assets
    # through "../assets/", and a path that escapes the checkout is a bug in
    # its own right.
    # A ref that starts with "/" is resolved against the site root instead.
    # The shared artwork uses those on purpose: a block copied between pages
    # at different depths cannot carry a relative path that works in both.
    here = os.path.dirname(path)
    for ref in sorted(set(re.findall(r'(?:href|src)="((?!https?:|#|mailto:)[^"]+)"', html))):
        clean = ref.split("?")[0].split("#")[0]
        base = ROOT if clean.startswith("/") else here
        target = os.path.normpath(os.path.join(base, clean.lstrip("/")))
        if not target.startswith(ROOT):
            bad(f"{rel}: {ref} resolves outside the checkout")
        elif not os.path.exists(target):
            bad(f"{rel}: missing file: {ref}")

    if title:
        notes.append(f"{rel:22} title       {len(title):3} chars  {title}")
    if desc:
        notes.append(f"{rel:22} description {len(desc):3} chars  {desc}")
    if graph:
        notes.append(f"{rel:22} JSON-LD     {len(graph)} nodes")


def check_shared():
    """The site has no build step, so anything both pages show is a copy: the
    inline illustrations, and the footer. Copies rot silently, and this is the
    only thing that would notice."""
    shared = [
        (r'<svg class="pm-defs".*?</svg>', "the pm-defs block"),
        (r'<div class="side-wrap">.*?</div>', "the side-by-side scene"),
        (r"<footer>.*?</footer>", "the footer"),
    ]
    home = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    tut = open(os.path.join(ROOT, "quick-start", "index.html"), encoding="utf-8").read()
    for pattern, what in shared:
        a = re.search(pattern, home, re.S)
        b = re.search(pattern, tut, re.S)
        if not a or not b:
            bad(f"{what} is missing from {'index.html' if not a else 'quick-start/index.html'}")
        elif a.group(0) != b.group(0):
            bad(f"{what} differs between index.html and quick-start/index.html; "
                "both pages show a copy of it, so the two have to stay identical")


# Tags that describe the site rather than the page: both pages must agree, or
# a social card or a crawler sees two different sites.
SHARED_TAGS = [
    r'<meta name="author" content="(.*?)">',
    r'<meta name="robots" content="(.*?)">',
    r'<meta property="og:site_name" content="(.*?)">',
    r'<meta property="og:locale" content="(.*?)">',
    r'<meta name="twitter:card" content="(.*?)">',
    r'<meta property="og:image" content="(.*?)">',
    r'<meta property="og:image:alt" content="(.*?)">',
]


def check_shared_metadata():
    """Per-page copy differs on purpose; the site-wide tags must not."""
    heads = {}
    for rel in PAGES:
        html = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        heads[rel] = html[: html.index("</head>")]
    first = PAGES[0]
    for pattern in SHARED_TAGS:
        want = re.search(pattern, heads[first])
        for rel in PAGES[1:]:
            got = re.search(pattern, heads[rel])
            if (want is None) != (got is None):
                bad(f"{pattern} is on one page but not the other")
            elif want and got and want.group(1) != got.group(1):
                bad(f"site-wide tag differs between {first} and {rel}:\n"
                    f"    {first}: {want.group(1)!r}\n    {rel}: {got.group(1)!r}")


def check_sitemap():
    """lastmod is the only field crawlers read, and it helps only while it is
    true. Google ignores changefreq and priority, so they are absent on
    purpose; if they come back, they are noise at best and a reason to
    distrust lastmod at worst."""
    sitemap = os.path.join(ROOT, "sitemap.xml")
    if not os.path.exists(sitemap):
        return
    sm = open(sitemap, encoding="utf-8").read()
    for dead in ("changefreq", "priority"):
        if f"<{dead}>" in sm:
            bad(f"sitemap has <{dead}>, which every major crawler ignores")

    entries = dict(re.findall(
        r"<loc>(.*?)</loc>\s*<lastmod>([0-9-]+)</lastmod>", sm, re.S))
    if not entries:
        bad("sitemap has no <lastmod>, the one field that is read")
        return

    for rel in PAGES:
        url = URLS[rel]
        if url not in entries:
            bad(f"sitemap does not list {url}")
            continue
        real = last_change(rel)
        if real and entries[url] < real:
            bad(f"sitemap lastmod {entries[url]} for {url} predates the last "
                f"change to {rel} ({real})")
        elif real:
            notes.append(f"{rel:22} lastmod {entries[url]}, page last changed {real}")

    for url in entries:
        if url not in URLS.values():
            bad(f"sitemap lists {url}, which is not one of the pages checked here")


for page in PAGES:
    check_page(page)
check_shared()
check_shared_metadata()
check_sitemap()

# ---- report --------------------------------------------------------------
print("\n".join(notes))

if problems:
    print("\n" + "\n".join("FAIL  " + p for p in problems), file=sys.stderr)
    sys.exit(1)
print("\nall checks passed")
