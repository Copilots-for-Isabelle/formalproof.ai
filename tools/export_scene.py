#!/usr/bin/env python3
"""Export the main scene as one standalone animated SVG: assets/pide-ai-scene.svg.

The scene in index.html leans on the page: the pm-defs sprite sheet, style.css (palette,
keyframes, dark mode), the Isabelle badges and the web fonts. An SVG used as an image may load
none of these, so this inlines all of them: the sprites as <defs>, the stylesheet as <style>,
the badges once as data URIs, and the fonts as subsets holding just the characters the scene
shows (fetched from Google Fonts, hence the network). Light and dark come from the stylesheet's
own prefers-color-scheme blocks, so one file serves both; the background stays transparent, so the
scene sits on whatever page embeds it.
"""
import base64, html, pathlib, re, sys, urllib.parse, urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "pide-ai-scene.svg"
WIDTH = 1200
FONTS = "family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) " \
     "Chrome/120.0 Safari/537.36"


def block(text, start):
    i = text.index(start)
    return text[i:text.index("</svg>", i) + len("</svg>")]


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=10) as response:
        return response.read()


def font_faces(chars):
    query = FONTS + "&text=" + urllib.parse.quote("".join(sorted(chars)))
    css = fetch("https://fonts.googleapis.com/css2?" + query).decode()
    def inline(m):
        data = base64.b64encode(fetch(m.group(1))).decode()
        return f'url(data:font/woff2;base64,{data}) format("woff2")'
    return re.sub(r'url\((https://[^)]+)\) format\([\'"]woff2[\'"]\)', inline, css)


def data_uri(path):
    return "data:image/svg+xml;base64," + base64.b64encode(path.read_bytes()).decode()


page = (ROOT / "index.html").read_text(encoding="utf-8")
css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")

defs = block(page, '<svg class="pm-defs"')
defs = defs[defs.index(">") + 1:-len("</svg>")]
scene = block(page, '<svg class="scene"')
scene_tag = scene[:scene.index(">") + 1]
scene = scene[len(scene_tag):-len("</svg>")]
view_box = re.search(r'viewBox="([^"]+)"', scene_tag).group(1)
_, _, w, h = (float(v) for v in view_box.split())

badges = {}
def badge(m):
    attrs, src = m.group(1) + m.group(3), m.group(2)
    key = "pm-badge-" + pathlib.Path(src).stem
    badges[key] = src
    attrs = re.sub(r'\s(width|height|preserveAspectRatio)="[^"]*"', "", attrs)
    return f'<use{attrs} href="#{key}"/>'
scene = re.sub(r'<image([^>]*?)\shref="(assets/[^"]+\.svg)"([^>]*?)/>', badge, scene)
badge_defs = "".join(
    f'<image id="{key}" href="{data_uri(ROOT / src)}" width="0.42" height="0.42" '
    f'preserveAspectRatio="xMidYMid meet"/>' for key, src in badges.items())

text = html.unescape(" ".join(re.findall(r">([^<]*)<", scene)))
chars = set(text) - set("\n\t")

svg = (
    scene_tag.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" '
                      f'width="{WIDTH}" height="{round(WIDTH * h / w)}" ', 1) + "\n"
    f'<style><![CDATA[\n{font_faces(chars)}\n{css}\n]]></style>\n'
    f'<defs>{defs}{badge_defs}</defs>\n'
    f'{scene}</svg>\n')
OUT.write_text(svg, encoding="utf-8")
print(f"{OUT.relative_to(ROOT)}: {len(svg.encode()) // 1024} KB", file=sys.stderr)
