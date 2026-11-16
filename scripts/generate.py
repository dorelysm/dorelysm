#!/usr/bin/env python3
"""Generates every SVG used by the profile README (stdlib only).

  python scripts/generate.py            # static + dynamic
  python scripts/generate.py --static   # header, typing line, link pills
  python scripts/generate.py --dynamic  # project cards + stats (needs GitHub API)

Dynamic assets read public data from the GitHub API. Set GITHUB_TOKEN to avoid
rate limits. Private and forked repositories are never included.
"""
from __future__ import annotations

import json
import os
import sys
import textwrap
import urllib.error
import urllib.request
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
USER = "dorelysm"

# Palette taken from dorelys.dev (light + dark tokens).
THEMES = {
    "light": dict(bg="#FFFFFA", ink="#44403C", strong="#292524", muted="#78706B",
                  accent="#916E6E", decor="#BC8F8F", line="#E7E5E4"),
    "dark": dict(bg="#1C1917", ink="#D6D3D1", strong="#F5F0ED", muted="#A8A29E",
                 accent="#BC8F8F", decor="#916E6E", line="#44403C"),
}

SERIF = "Georgia, 'Times New Roman', serif"
SANS = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
MONO = "ui-monospace, SFMono-Regular, Consolas, Menlo, monospace"

EXCLUDE_LANGS = {"Jupyter Notebook"}

LANG_COLORS = ["#BC8F8F", "#7C8FA6", "#8FA68A", "#C9A66B", "#9A86A4", "#6F9C9C", "#A8A29E"]

TYPING_LINES = [
    "AI Engineer",
    "M.Sc. in Artificial Intelligence",
    "Building AI tools with purpose",
    "Founder, Praeventia Technologies",
]

# Card copy is curated (English); stars and language come from the API.
PROJECTS = [
    dict(repo="naturalizacion-texto-es", title="naturalizacion-texto-es",
         desc="Claude Code skill that makes AI-generated Spanish read naturally: "
              "11 linguistic techniques, built for editorial quality, not detector evasion.",
         stack="Claude Code · NLP · Spanish", fallback_lang="Claude Code skill"),
    dict(repo="resilis", title="Resilis",
         desc="Prioritizes disaster aid and checks it reached who asked for it. "
              "2nd place in Social Impact at Rally Latinoamericano 2026 "
              "(Corporación Universitaria Americana).",
         stack="Python · FastAPI · TOPSIS · Leaflet", fallback_lang="Python"),
    dict(repo="AstroAtlas-Hackaton-NASA-2026", title="AstroAtlas",
         desc="Finds and validates Earth analogs for Moon and Mars bases. "
              "NASA Space Apps Challenge 2026.",
         stack="Python · Streamlit · Geospatial", fallback_lang="Python"),
    dict(repo="ms-lesion-segmentation", title="ms-lesion-segmentation",
         desc="2D U-Net for multiple sclerosis lesion segmentation in brain MRI "
              "(T1/T2/FLAIR). 5-fold CV, Dice 0.553.",
         stack="PyTorch · Medical imaging", fallback_lang="Jupyter Notebook"),
]

LINKS = [
    ("web", "dorelys.dev", 132),
    ("linkedin", "LinkedIn", 116),
    ("email", "Email", 100),
    ("github", "GitHub", 108),
]

GITHUB_MARK = ("M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49"
               "-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 "
               "1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59"
               ".82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 "
               "1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 "
               "3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42"
               "-3.58-8-8-8z")


# ---------------------------------------------------------------- helpers
def svg(w: int, h: int, body: str, title: str, desc: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
        f'role="img" aria-labelledby="t d">\n<title id="t">{escape(title)}</title>\n'
        f'<desc id="d">{escape(desc or title)}</desc>\n{body}\n</svg>\n'
    )


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print("wrote", path.relative_to(ROOT).as_posix())


def fmt(x: float) -> str:
    return f"{x:.4f}".rstrip("0").rstrip(".")


# ---------------------------------------------------------------- header
def header(theme: str) -> str:
    c = THEMES[theme]
    nodes = [(52, 52), (96, 120), (150, 70), (70, 160), (130, 150)]
    edges = [(0, 1), (0, 2), (1, 2), (1, 3), (1, 4), (2, 4), (3, 4)]
    parts = [f'<rect x="1" y="1" width="698" height="198" rx="16" fill="{c["bg"]}" stroke="{c["line"]}"/>']
    for side in (0, 1):
        def pt(n):
            x, y = nodes[n]
            return (x if side == 0 else 700 - x, y)
        for a, b in edges:
            (x1, y1), (x2, y2) = pt(a), pt(b)
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c["decor"]}" '
                         f'stroke-opacity=".35" stroke-width="1"/>')
        for i in range(len(nodes)):
            x, y = pt(i)
            parts.append(f'<circle cx="{x}" cy="{y}" r="{4 if i in (0, 2) else 3}" fill="{c["decor"]}" '
                         f'fill-opacity=".7"/>')
    parts += [
        f'<text x="350" y="94" text-anchor="middle" font-family="{SERIF}" font-size="38" '
        f'font-weight="700" fill="{c["strong"]}">Dorelys Martinez Suarez</text>',
        f'<line x1="320" y1="112" x2="380" y2="112" stroke="{c["accent"]}" stroke-width="2" '
        f'stroke-linecap="round"/>',
        f'<text x="350" y="141" text-anchor="middle" font-family="{SANS}" font-size="13" '
        f'letter-spacing="4" fill="{c["accent"]}" font-weight="600">AI ENGINEER</text>',
        f'<text x="350" y="170" text-anchor="middle" font-family="{SERIF}" font-size="17" '
        f'font-style="italic" fill="{c["muted"]}">AI with purpose. Always.</text>',
    ]
    return svg(700, 200, "\n".join(parts), "Dorelys Martinez Suarez, AI Engineer",
               "Header with the name Dorelys Martinez Suarez, the title AI Engineer and the motto "
               "AI with purpose. Always.")


# ---------------------------------------------------------------- typing line
def anim(attr: str, points: list[tuple[float, float]], total: float, discrete: bool = False) -> str:
    """SMIL animation from (seconds, value) points over a looping timeline of `total` seconds."""
    pts = sorted(points)
    if pts[0][0] > 0:
        pts.insert(0, (0.0, pts[0][1] if discrete else pts[0][1]))
    if pts[-1][0] < total:
        pts.append((total, pts[-1][1]))
    kt = ";".join(fmt(t / total) for t, _ in pts)
    vals = ";".join(fmt(v) for _, v in pts)
    mode = ' calcMode="discrete"' if discrete else ""
    return (f'<animate attributeName="{attr}" dur="{fmt(total)}s" repeatCount="indefinite" '
            f'keyTimes="{kt}" values="{vals}"{mode}/>')


def typing(theme: str) -> str:
    c = THEMES[theme]
    char_w, size, cy = 12, 20, 33
    slots, t = [], 0.0
    for text in TYPING_LINES:
        type_t, hold, erase, gap = max(0.9, 0.055 * len(text)), 1.9, 0.5, 0.25
        slots.append((text, t, type_t, hold, erase))
        t += type_t + hold + erase + gap
    total = t
    defs, body = [], []
    for i, (text, s, type_t, hold, erase) in enumerate(slots):
        w = len(text) * char_w
        left = (700 - w) / 2
        end = s + type_t + hold + erase
        width_pts = [(s, 0), (s + type_t, w), (s + type_t + hold, w), (end, 0)]
        if s > 0:
            width_pts.insert(0, (0, 0))
        if end < total:
            width_pts.append((total, 0))
        cur_x_pts = [(t_, left + v) for t_, v in width_pts]
        opacity_pts = [(0, 0), (s, 1), (end, 0), (total, 0)] if s > 0 else [(0, 1), (end, 0), (total, 0)]
        defs.append(f'<clipPath id="c{i}"><rect x="{fmt(left)}" y="0" width="0" height="56">'
                    f'{anim("width", width_pts, total)}</rect></clipPath>')
        body.append(f'<text clip-path="url(#c{i})" x="{fmt(left)}" y="{cy}" font-family="{MONO}" '
                    f'font-size="{size}" textLength="{w}" lengthAdjust="spacingAndGlyphs" '
                    f'fill="{c["strong"]}">{escape(text)}</text>')
        body.append(f'<rect x="{fmt(left)}" y="12" width="2.5" height="26" fill="{c["accent"]}" opacity="0">'
                    f'{anim("x", cur_x_pts, total)}{anim("opacity", opacity_pts, total, discrete=True)}</rect>')
    desc = "Rotating text: " + "; ".join(TYPING_LINES) + "."
    return svg(700, 56, "<defs>" + "".join(defs) + "</defs>\n" + "\n".join(body), "Dorelys' roles", desc)


# ---------------------------------------------------------------- link pills
def glyph(kind: str, c: dict) -> str:
    a = c["accent"]
    if kind == "web":
        return (f'<g fill="none" stroke="{a}" stroke-width="1.5" stroke-linecap="round">'
                f'<circle cx="9" cy="9" r="8"/><ellipse cx="9" cy="9" rx="3.6" ry="8"/>'
                f'<line x1="1" y1="9" x2="17" y2="9"/></g>')
    if kind == "linkedin":
        return (f'<rect x="1" y="1" width="16" height="16" rx="3" fill="none" stroke="{a}" stroke-width="1.5"/>'
                f'<text x="9" y="13.2" text-anchor="middle" font-family="{SANS}" font-size="9.5" '
                f'font-weight="700" fill="{a}">in</text>')
    if kind == "email":
        return (f'<g fill="none" stroke="{a}" stroke-width="1.5" stroke-linejoin="round">'
                f'<rect x="1" y="3" width="16" height="12" rx="2"/><polyline points="1.5,4.5 9,10 16.5,4.5"/></g>')
    return f'<path transform="scale(1.125)" fill="{a}" d="{GITHUB_MARK}"/>'


def pill(kind: str, label: str, w: int, theme: str) -> str:
    c = THEMES[theme]
    body = (f'<rect x="1" y="1" width="{w - 2}" height="38" rx="19" fill="{c["bg"]}" stroke="{c["decor"]}"/>'
            f'<g transform="translate(16 11)">{glyph(kind, c)}</g>'
            f'<text x="42" y="25" font-family="{SANS}" font-size="14" font-weight="600" '
            f'fill="{c["strong"]}">{escape(label)}</text>')
    return svg(w, 40, body, label)


# ---------------------------------------------------------------- GitHub API
def api(path: str):
    req = urllib.request.Request(f"https://api.github.com{path}", headers={
        "Accept": "application/vnd.github+json", "User-Agent": "profile-readme-generator"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


# ---------------------------------------------------------------- project cards
CARD_W, CARD_H = 340, 188


def card(p: dict, stars: int, lang: str, theme: str) -> str:
    c = THEMES[theme]
    lines = textwrap.wrap(p["desc"], 48)[:4]
    parts = [
        f'<rect x="1" y="1" width="{CARD_W - 2}" height="{CARD_H - 2}" rx="12" fill="{c["bg"]}" stroke="{c["line"]}"/>',
        f'<rect x="1" y="1" width="4" height="{CARD_H - 2}" rx="2" fill="{c["decor"]}"/>',
        f'<text x="22" y="36" font-family="{SERIF}" font-size="18" font-weight="700" '
        f'fill="{c["strong"]}">{escape(p["title"])}</text>',
    ]
    for i, line in enumerate(lines):
        parts.append(f'<text x="22" y="{62 + i * 19}" font-family="{SANS}" font-size="13" '
                     f'fill="{c["ink"]}">{escape(line)}</text>')
    parts += [
        f'<text x="22" y="{CARD_H - 50}" font-family="{SANS}" font-size="12" font-weight="600" '
        f'fill="{c["accent"]}">{escape(p["stack"])}</text>',
        f'<line x1="22" y1="{CARD_H - 38}" x2="{CARD_W - 22}" y2="{CARD_H - 38}" stroke="{c["line"]}"/>',
        f'<circle cx="28" cy="{CARD_H - 19}" r="5" fill="{c["decor"]}"/>',
        f'<text x="40" y="{CARD_H - 14}" font-family="{SANS}" font-size="12" '
        f'fill="{c["muted"]}">{escape(lang)}</text>',
        f'<text x="{CARD_W - 22}" y="{CARD_H - 14}" text-anchor="end" font-family="{SANS}" '
        f'font-size="12" fill="{c["muted"]}">&#9733; {stars}</text>',
    ]
    return svg(CARD_W, CARD_H, "\n".join(parts), f'{p["title"]} project card',
               f'{p["title"]}: {p["desc"]} Stack: {p["stack"]}. {stars} stars.')


# ---------------------------------------------------------------- stats
def stats(langs: list[tuple[str, int]], repos: int, stars: int, theme: str) -> str:
    c = THEMES[theme]
    total = sum(v for _, v in langs) or 1
    top = langs[:6]
    rest = sum(v for _, v in langs[6:])
    if rest:
        top.append(("Other", rest))
    bar_x, bar_w, bar_y = 28, 644, 62
    parts = [
        f'<defs><clipPath id="bar"><rect x="{bar_x}" y="{bar_y}" width="{bar_w}" height="12" rx="6"/></clipPath></defs>',
        f'<rect x="1" y="1" width="698" height="208" rx="16" fill="{c["bg"]}" stroke="{c["line"]}"/>',
        f'<text x="28" y="40" font-family="{SERIF}" font-size="18" font-weight="700" '
        f'fill="{c["strong"]}">Languages across my public repositories</text>',
        f'<g clip-path="url(#bar)">',
    ]
    x = float(bar_x)
    for i, (_, v) in enumerate(top):
        w = bar_w * v / total
        parts.append(f'<rect x="{fmt(x)}" y="{bar_y}" width="{fmt(w + 0.5)}" height="12" '
                     f'fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>')
        x += w
    parts.append("</g>")
    for i, (name, v) in enumerate(top):
        col, row = i % 4, i // 4
        lx, ly = 28 + col * 162, 104 + row * 26
        pct = 100 * v / total
        parts.append(f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{LANG_COLORS[i % len(LANG_COLORS)]}"/>'
                     f'<text x="{lx + 16}" y="{ly}" font-family="{SANS}" font-size="13" fill="{c["ink"]}">'
                     f'{escape(name)} <tspan fill="{c["muted"]}">{pct:.1f}%</tspan></text>')
    parts.append(f'<line x1="28" y1="160" x2="672" y2="160" stroke="{c["line"]}"/>')
    parts.append(f'<text x="672" y="190" text-anchor="end" font-family="{SANS}" font-size="11" '
                 f'fill="{c["muted"]}">Jupyter notebooks excluded: their output bytes skew the share.</text>')
    for i, (num, label) in enumerate([(repos, "original public repos"), (stars, "stars earned")]):
        bx = 28 + i * 200
        parts.append(f'<text x="{bx}" y="190" font-family="{SERIF}" font-size="22" font-weight="700" '
                     f'fill="{c["accent"]}">{num}</text>'
                     f'<text x="{bx + 14 + 14 * len(str(num))}" y="190" font-family="{SANS}" font-size="13" '
                     f'fill="{c["muted"]}">{label}</text>')
    desc = "Language share by bytes of code: " + ", ".join(
        f"{n} {100 * v / total:.1f}%" for n, v in top) + f". {repos} public repositories, {stars} stars."
    return svg(700, 210, "\n".join(parts), "Language statistics", desc)


# ---------------------------------------------------------------- build steps
def build_static() -> None:
    for theme in THEMES:
        write(ASSETS / f"header-{theme}.svg", header(theme))
        write(ASSETS / f"typing-{theme}.svg", typing(theme))
        for kind, label, w in LINKS:
            write(ASSETS / "links" / f"{kind}-{theme}.svg", pill(kind, label, w, theme))


def build_dynamic() -> None:
    for p in PROJECTS:
        info = api(f"/repos/{USER}/{p['repo']}")
        if info.get("private"):
            raise SystemExit(f"{p['repo']} is private; cards must only use public repos")
        stars, lang = info["stargazers_count"], info.get("language") or p["fallback_lang"]
        for theme in THEMES:
            write(ASSETS / "cards" / f"{p['repo']}-{theme}.svg", card(p, stars, lang, theme))

    repos = [r for r in api(f"/users/{USER}/repos?per_page=100&type=owner")
             if not r["private"] and not r["fork"] and not r["archived"] and r["name"] != USER]
    totals: dict[str, int] = {}
    for r in repos:
        for name, n in api(f"/repos/{USER}/{r['name']}/languages").items():
            totals[name] = totals.get(name, 0) + n
    # Notebook JSON (outputs, images) inflates byte counts and hides the real code mix.
    langs = sorted(((k, v) for k, v in totals.items() if k not in EXCLUDE_LANGS),
                   key=lambda kv: kv[1], reverse=True)
    stars = sum(r["stargazers_count"] for r in repos)
    for theme in THEMES:
        write(ASSETS / f"stats-{theme}.svg", stats(langs, len(repos), stars, theme))


def main(argv: list[str]) -> None:
    only_static, only_dynamic = "--static" in argv, "--dynamic" in argv
    if not only_dynamic:
        build_static()
    if not only_static:
        try:
            build_dynamic()
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            raise SystemExit(f"GitHub API error: {e}")


if __name__ == "__main__":
    main(sys.argv[1:])
