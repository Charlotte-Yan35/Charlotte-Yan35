#!/usr/bin/env python3
"""Regenerate the SVGs used by the profile README.

    python3 scripts/make_assets.py

Everything is plain SVG with CSS / SMIL animation (no scripts, no web fonts),
because that is all GitHub will render inside an <img>. Every asset carries
its own colours, so the page looks the same in GitHub's light and dark themes.

The page is a "bento" collage: every tile is drawn on a 1200-unit-wide grid,
so tiles in one row share a height and their widths add up to 1200.

Want a different name or colours? Edit NAME and C below and run it again.
"""
import math
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets"

NAME = "Yiwen Yan"          # shown on the hero; a space splits it over two lines

# Each theme is a complete look. THEME picks the one written to assets/;
# `python3 scripts/make_assets.py --all` also writes every theme to options/.
THEME = "cloud"

THEMES = {
    # violet outlines, hot-pink hard shadows, rainbow hero
    "candy": dict(
        ink="#5b2fd4", line="#5b2fd4", shadow=("hard", "#ff5fa8", "normal"), dots=0.13, hero="rainbow",
        name=("#ffffff", "#5b2fd4", "#ff5fa8"), strip=("#ff5fa8", "#ffffff"),
        C=dict(pink="#ff8cc6", orange="#ffb066", yellow="#ffe066", green="#7be0a6", cyan="#7fd6ff",
               blue="#8fa8ff", purple="#c3a1ff", red="#ff6b7a", white="#ffffff", cream="#fff9ec",
               lilac="#dccbff", peach="#ffd2a8"),
        tiles=dict(about="#fff9ec", now="#a9f0c8", readscreen="#ffb0d8", grid="#a6e2ff",
                   toolbox="#dccbff", belief="#ffe680", timeline="#ffd2a8"),
    ),
    # die-cut stickers: white borders, soft coloured shadows, pastel gradients
    "cloud": dict(
        ink="#6a4fd8", line="#ffffff", shadow=("soft", "#9b7bff", "normal"), dots=0.0, hero="blobs",
        name=("#6a4fd8", "#ffffff", None), strip=("#ffffff", "#6a4fd8"),
        C=dict(pink="#ff9fd0", orange="#ffc078", yellow="#ffe979", green="#8fe8b8", cyan="#8fd9ff",
               blue="#a3b5ff", purple="#c9adff", red="#ff7d93", white="#ffffff", cream="#fffdf7",
               lilac="#e7dcff", peach="#ffe1c7"),
        tiles=dict(about=("#fff3fa", "#ffd9ee"), now=("#e6fff3", "#bff3da"), readscreen=("#ffe6f3", "#ffc2e0"),
                   grid=("#e3f5ff", "#bfe4ff"), toolbox=("#f1e9ff", "#d9c8ff"), belief=("#fffbd6", "#ffee99"),
                   timeline=("#fff3e6", "#ffd9b8")),
    ),
    # riso print: no outlines, cobalt ink, misregistered pink shadows, paper tiles
    "riso": dict(
        ink="#2b50e8", line="none", shadow=("hard", "#ff5cab", "multiply"), dots=0.16, hero="riso",
        name=("#2b50e8", "none", "#ff5cab"), strip=("#ff5cab", "#fff6e3"),
        C=dict(pink="#ff7bbd", orange="#ff9a4d", yellow="#ffe14d", green="#3fd9a0", cyan="#6fc8ff",
               blue="#7f9bff", purple="#b18cff", red="#ff5c6c", white="#ffffff", cream="#fff6e3",
               lilac="#e2d4ff", peach="#ffd0a6"),
        tiles=dict(about="#fff6e3", now="#ffd9ec", readscreen="#ffe14d", grid="#d6eaff",
                   toolbox="#fff6e3", belief="#ffd9ec", timeline="#c9f2e0"),
    ),
}

TAGLINE = "Life is going on"   # the yellow sticker under the name

INK = LINE = ""
C, T = {}, {}


def use(theme):
    global INK, LINE, C, T
    T = THEMES[theme]
    INK, LINE, C = T["ink"], T["line"], T["C"]


RAINBOW = ["pink", "orange", "yellow", "green", "cyan", "purple"]

SERIF = "'Iowan Old Style','Palatino Linotype',Palatino,Georgia,'Times New Roman',serif"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"

REDUCED = "@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }"
def base_defs():
    """Dot pattern plus the soft drop-shadow filter (used by soft themes)."""
    return (
        '<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse">'
        f'<circle cx="4" cy="4" r="1.7" fill="{INK}" fill-opacity="{T["dots"]}"/></pattern>'
        '<filter id="soft" x="-30%" y="-30%" width="160%" height="180%">'
        f'<feDropShadow dx="0" dy="5" stdDeviation="5" flood-color="{T["shadow"][1]}" flood-opacity="0.38"/></filter>'
    )
MOTION = f"""
  .bob  {{ animation: bob 4.2s ease-in-out infinite; }}
  .bob2 {{ animation: bob 5.1s ease-in-out -1.7s infinite; }}
  .bob3 {{ animation: bob 3.6s ease-in-out -0.9s infinite; }}
  @keyframes bob {{ 0%, 100% {{ transform: translateY(-5px); }} 50% {{ transform: translateY(6px); }} }}
  {REDUCED}
"""


# ------------------------------------------------------------ sticker pieces
def _shadow_attrs():
    mode, colour, blend = T["shadow"]
    return mode, colour, (f' style="mix-blend-mode:{blend}"' if blend != "normal" else "")


def srect(x, y, w, h, r, fill, sh=6, sw=3):
    """Rounded rectangle sticker; the theme decides hard or soft shadow."""
    mode, colour, blend = _shadow_attrs()
    main = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{LINE}" stroke-width="{sw}"'
    if mode == "soft":
        return main + ' filter="url(#soft)"/>'
    return f'<rect x="{x + sh}" y="{y + sh}" width="{w}" height="{h}" rx="{r}" fill="{colour}"{blend}/>' + main + "/>"


def scirc(cx, cy, r, fill, sh=5, sw=3):
    mode, colour, blend = _shadow_attrs()
    main = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{LINE}" stroke-width="{sw}"'
    if mode == "soft":
        return main + ' filter="url(#soft)"/>'
    return f'<circle cx="{cx + sh}" cy="{cy + sh}" r="{r}" fill="{colour}"{blend}/>' + main + "/>"


def star(x, y, s, fill, dur=14, cls=""):
    """Four-point sparkle that spins around its own centre."""
    k = s * 0.2
    d = f"M0,{-s} Q{k},{-k} {s},0 Q{k},{k} 0,{s} Q{-k},{k} {-s},0 Q{-k},{-k} 0,{-s} Z"
    return (
        f'<g transform="translate({x},{y}) rotate({(x * 7 + y * 3) % 40 - 20})">'
        f'<path d="{d}" fill="{fill}" stroke="{LINE}" stroke-width="2.6" stroke-linejoin="round"/></g>'
    )


def flower(x, y, petal, centre, dur=18):
    petals = "".join(
        f'<circle cx="{15 * math.cos(a):.1f}" cy="{15 * math.sin(a):.1f}" r="11" fill="{petal}" stroke="{LINE}" stroke-width="2.6"/>'
        for a in [i * math.pi / 3 for i in range(6)]
    )
    return (
        f'<g transform="translate({x},{y}) rotate(12)">'
        f'{petals}<circle r="10" fill="{centre}" stroke="{LINE}" stroke-width="2.6"/></g>'
    )


def plus(x, y, s=9):
    return f'<path d="M{x - s},{y} h{2 * s} M{x},{y - s} v{2 * s}" stroke="{INK}" stroke-width="4" stroke-linecap="round"/>'


def rings(cx, cy, spacing, width, count, stroke):
    circles = "".join(
        f'<circle cx="{cx}" cy="{cy}" r="{spacing * i:.1f}"/>' for i in range(1, count + 1)
    )
    return f'<g fill="none" stroke="{stroke}" stroke-width="{width}">{circles}</g>'


def rainbow_gradient(gid, period):
    """Horizontal rainbow that repeats every `period` px, so a rect filled
    with it can slide by one period and loop without a seam."""
    names = RAINBOW + [RAINBOW[0]]
    stops = "".join(
        f'<stop offset="{i / (len(names) - 1):.3f}" stop-color="{C[n]}"/>' for i, n in enumerate(names)
    )
    return (
        f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="0" x2="{period}" y2="0" '
        f'spreadMethod="repeat">{stops}</linearGradient>'
    )


# ----------------------------------------------------------------- tile shell
PAD, SHADOW = 8, 8


def tile(W, H, fill, label, content, defs="", css="", dots=True):
    """One bento tile: a sticker card drawn inside a transparent margin so
    neighbouring tiles line up with even gaps. `fill` is a colour or a
    (from, to) pair for a diagonal gradient."""
    cw, ch = W - 2 * PAD - SHADOW, H - 2 * PAD - SHADOW
    if isinstance(fill, tuple):
        defs += (f'<linearGradient id="tg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{fill[0]}"/>'
                 f'<stop offset="1" stop-color="{fill[1]}"/></linearGradient>')
        fill = "url(#tg)"
    mode, colour, blend = _shadow_attrs()
    if mode == "soft":
        shadow = f'<rect x="{PAD}" y="{PAD}" width="{cw}" height="{ch}" rx="24" fill="#fff" filter="url(#soft)"/>'
    else:
        shadow = f'<rect x="{PAD + SHADOW}" y="{PAD + SHADOW}" width="{cw}" height="{ch}" rx="24" fill="{colour}"{blend}/>'
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{label}">
<defs>
  {base_defs()}
  <clipPath id="card"><rect width="{cw}" height="{ch}" rx="24"/></clipPath>
  {defs}
  <style>{MOTION}{css}</style>
</defs>
{shadow}
<g transform="translate({PAD},{PAD})">
  <g clip-path="url(#card)">
    <rect width="{cw}" height="{ch}" fill="{fill}"/>
    {f'<rect width="{cw}" height="{ch}" fill="url(#dots)"/>' if dots else ''}
    {content}
  </g>
  <rect x="1.5" y="1.5" width="{cw - 3}" height="{ch - 3}" rx="22.5" fill="none" stroke="{LINE}" stroke-width="3"/>
</g>
</svg>
"""


def label(x, y, text, fill, rot=-3, size=17):
    w = len(text) * size * 0.62 + 44
    return (
        f'<g transform="rotate({rot} {x + w / 2:.0f} {y + 20})">{srect(x, y, round(w), 40, 20, fill, sh=4)}'
        f'<text x="{x + w / 2:.1f}" y="{y + 26}" text-anchor="middle" textLength="{len(text) * size * 0.62:.0f}" lengthAdjust="spacing" '
        f'font-family="{MONO}" font-size="{size}" font-weight="700" fill="{INK}">{text}</text></g>'
    )


# ----------------------------------------------------------------------- hero
def hero():
    W, H = 1200, 360
    cw, ch = W - 2 * PAD - SHADOW, H - 2 * PAD - SHADOW
    strip_y = ch - 56

    fs = min(96, 520 / (0.6 * len(NAME)))
    nf, ns, nsh = T["name"]
    name = ""
    if nsh:
        blend = _shadow_attrs()[2]
        name += f'<text x="71" y="166" fill="{nsh}" stroke="{nsh if ns != "none" else "none"}"{blend}>{NAME}</text>'
    soft = "" if nsh else ' filter="url(#soft)"'
    name += f'<text x="63" y="158" fill="{nf}" stroke="{ns}"{soft}>{NAME}</text>'

    sw_, sh_ = 330, 220
    bars = [(64, 150, INK), (64, 70, C["purple"]), (92, 240, INK), (120, 110, C["pink"]),
            (120, 90, INK), (148, 210, INK), (176, 130, INK)]
    lines, used = "", {}
    for y, w, col in bars:
        x = 24 + used.get(y, 0)
        lines += f'<rect x="{x}" y="{y}" width="{w}" height="13" rx="6.5" fill="{col}"/>'
        used[y] = used.get(y, 0) + w + 12
    sweep = 'keyTimes="0;0.12;0.62;1" dur="6.5s" repeatCount="indefinite"'
    screen = f"""
    <g transform="translate(704,30) rotate(5) scale(0.84)"><g class="bob">
      {srect(0, 0, sw_, sh_, 18, C['white'], sh=9)}
      <path d="M1.5,40 V18 a16.5,16.5 0 0 1 16.5,-16.5 H{sw_ - 18} a16.5,16.5 0 0 1 16.5,16.5 V40 Z" fill="{C['yellow']}"/>
      <path d="M0,40 H{sw_}" stroke="{LINE}" stroke-width="3"/>
      <circle cx="24" cy="21" r="6.5" fill="{C['pink']}" stroke="{LINE}" stroke-width="2"/>
      <circle cx="46" cy="21" r="6.5" fill="{C['green']}" stroke="{LINE}" stroke-width="2"/>
      <circle cx="68" cy="21" r="6.5" fill="{C['cyan']}" stroke="{LINE}" stroke-width="2"/>
      {lines}
      <g clip-path="url(#scr)"><g clip-path="url(#raw)" style="mix-blend-mode:multiply" opacity="0.6">
        {rings(430, -90, 12.0, 6, 46, C['pink'])}
        {rings(414, -70, 12.9, 6, 44, C['green'])}
      </g></g>
      <g clip-path="url(#scr)"><g>
        <animateTransform attributeName="transform" type="translate" values="0,0;0,0;{sw_ - 6},0;{sw_ - 6},0" {sweep}/>
        <rect x="-6" y="42" width="18" height="{sh_ - 44}" fill="{C['yellow']}" opacity="0.75"/>
        <rect x="1" y="42" width="4" height="{sh_ - 44}" fill="{INK}"/>
      </g></g>
    </g></g>"""

    pts = [(38 * math.cos(2 * math.pi * i / 5 - math.pi / 2), 38 * math.sin(2 * math.pi * i / 5 - math.pi / 2)) for i in range(5)]
    edges = [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 4)]
    net = "".join(
        f'<path d="M{pts[a][0]:.1f},{pts[a][1]:.1f} L{pts[b][0]:.1f},{pts[b][1]:.1f}" stroke="{INK}" stroke-width="2.6"/>'
        for a, b in edges
    ) + "".join(
        f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9.5" fill="{C[col]}" stroke="{LINE}" stroke-width="2.6"/>'
        for (x, y), col in zip(pts, ["yellow", "pink", "white", "green", "orange"])
    )
    badge = f'<g transform="translate(1074,82) scale(0.84)"><g>{scirc(0, 0, 66, C["cyan"], sh=7)}{net}</g></g>'
    sigma = (
        f'<g transform="translate(646,54) rotate(-10) scale(0.84)"><g>{srect(-42, -42, 84, 84, 20, C["purple"], sh=7)}'
        f'<text x="0" y="21" text-anchor="middle" font-family="{SERIF}" font-size="60" font-weight="700" fill="{INK}">∑</text></g></g>'
    )

    phrase = "COMPUTER VISION ✦ DYNAMICAL SYSTEMS ✦ SCIENTIFIC COMPUTING ✦ LIFE IS GOING ON ✦ "
    period = round(len(phrase) * 14.77)   # one repetition, so the ticker loops without a seam
    seps = [C["yellow"], C["pink"], C["cyan"], C["green"]]
    parts = phrase.split("✦")
    spans = "".join(
        f'{p.replace(" ", "&#160;")}<tspan fill="{seps[i % 4]}">✦</tspan>' for i, p in enumerate(parts[:-1])
    ) + "&#160;"
    marquee = "".join(
        f'<text x="{i * period}" y="{strip_y + 36}" textLength="{period}" lengthAdjust="spacing" font-family="{MONO}" '
        f'font-size="21" font-weight="700" fill="{T["strip"][1]}">{spans}</text>' for i in range(3)
    )

    if T["hero"] == "rainbow":
        bg = f'<g transform="skewX(-18)"><rect class="slide" x="-100" y="0" width="3200" height="{ch}" fill="url(#rb)"/></g>'
        bg_defs = rainbow_gradient("rb", 1400)
    elif T["hero"] == "blobs":
        spots = [("pink", 180, 60, 320, "d1"), ("yellow", 520, 290, 290, "d2"), ("cyan", 860, 40, 330, "d3"),
                 ("purple", 1090, 250, 310, "d1"), ("green", 300, 310, 250, "d3"), ("orange", 700, 170, 230, "d2")]
        bg = f'<rect width="{cw}" height="{ch}" fill="#fff7fc"/>' + "".join(
            f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}" fill="url(#b-{c})"/>' for c, x, y, r, cls in spots)
        bg_defs = "".join(
            f'<radialGradient id="b-{c}"><stop offset="0" stop-color="{C[c]}" stop-opacity="0.95"/>'
            f'<stop offset="1" stop-color="{C[c]}" stop-opacity="0"/></radialGradient>' for c, *_ in spots)
    else:  # riso: flat paper with big overprinted shapes
        m = 'style="mix-blend-mode:multiply"'
        bg = (f'<rect width="{cw}" height="{ch}" fill="{C["cream"]}"/>'
              f'<circle class="d1" cx="930" cy="110" r="230" fill="{C["pink"]}" {m}/>'
              f'<circle class="d2" cx="760" cy="330" r="190" fill="{C["yellow"]}" {m}/>'
              f'<circle class="d3" cx="1110" cy="320" r="150" fill="{C["cyan"]}" {m}/>'
              f'<rect class="d2" x="-40" y="250" width="330" height="330" rx="40" fill="{C["yellow"]}" transform="rotate(-12 120 400)" {m}/>'
              f'<circle class="d3" cx="470" cy="40" r="90" fill="{C["green"]}" {m}/>')
        bg_defs = ""
    tag_w = round(len(TAGLINE) * 11.95)
    content = f"""
  {bg}
  <rect width="{cw}" height="{ch}" fill="url(#dots)"/>
  {star(548, 222, 18, C['white'], 11)}
  {star(1004, 30, 14, C['yellow'], 9)}
  {star(1142, 188, 14, C['white'], 13)}
  {flower(1104, 232, C['pink'], C['yellow'])}
  {plus(612, 150)}{plus(1150, 26, 7)}{plus(668, 250, 7)}
  <path d="M884,256 l14,-12 l14,12 l14,-12 l14,12 l14,-12 l14,12" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round" stroke-linejoin="round"/>
  {sigma}{screen}{badge}
  {label(62, 26, "HELLO, I'M", C['white'])}
  <g font-family="{SANS}" font-size="{fs:.0f}" font-weight="900" letter-spacing="{-fs * 0.012:.1f}" stroke-width="6" stroke-linejoin="round" paint-order="stroke fill">{name}</g>
  <g>
    {srect(62, 190, tag_w + 52, 52, 26, C['yellow'], sh=6)}
    <text x="{88 + tag_w / 2:.0f}" y="224" text-anchor="middle" textLength="{tag_w}" lengthAdjust="spacing" font-family="{SANS}" font-size="24" font-weight="700" fill="{INK}">{TAGLINE}</text>
  </g>
  <rect x="0" y="{strip_y}" width="{cw}" height="56" fill="{T['strip'][0]}"/>
  <g class="ticker">{marquee}</g>"""
    defs = f"""<clipPath id="scr"><rect x="3" y="42" width="324" height="175"/></clipPath>
  <clipPath id="raw"><rect x="3" y="0" width="330" height="220">
    <animate attributeName="x" values="3;3;327;327" {sweep}/>
  </rect></clipPath>
  {bg_defs}"""
    css = """
    .slide { animation: slide 26s linear infinite; }
    @keyframes slide { to { transform: translateX(-1400px); } }
    .ticker { animation: tick 22s linear infinite; }
    @keyframes tick { to { transform: translateX(-1300px); } }
    .d1 { animation: drift 17s ease-in-out infinite alternate; }
    .d2 { animation: drift 23s ease-in-out -6s infinite alternate-reverse; }
    .d3 { animation: drift 19s ease-in-out -11s infinite alternate; }
    @keyframes drift { from { transform: translate(-36px, -14px); } to { transform: translate(40px, 18px); } }
"""
    css = css.replace("-1300px", f"-{period}px")
    return tile(W, H, C["pink"], f"{NAME}. {TAGLINE.rstrip('.')}. Computer vision, dynamical systems, scientific computing.",
                content, defs, css, dots=False)


# ---------------------------------------------------------------------- about
def about():
    W, H = 700, 360
    big = [("Grad student at Penn.", "yellow"), ("Maths background.", "cyan"), ("Now: computer vision.", "pink")]
    fs = 38
    lines = ""
    for i, (s, col) in enumerate(big):
        y = 128 + i * 50
        w = len(s) * fs * 0.535
        lines += (
            f'<rect x="28" y="{y - 31}" width="{w + 14:.0f}" height="42" rx="8" fill="{C[col]}" transform="rotate({(-0.8, 0.6, -0.5)[i]} 34 {y})"/>'
            f'<text x="35" y="{y}" textLength="{w:.0f}" lengthAdjust="spacing" font-family="{SANS}" font-size="{fs}" font-weight="800" fill="{INK}">{s}</text>'
        )
    content = f"""
  {label(30, 26, "ABOUT ME", C['green'])}
  {lines}
  <g font-family="{SANS}" font-size="20.5" fill="{INK}" fill-opacity="0.85">
    <text x="34" y="278">I like problems where a tidy model</text>
    <text x="34" y="305">runs into messy, real-world data.</text>
  </g>
  {star(610, 60, 20, C['pink'], 10)}{star(556, 108, 11, C['cyan'], 15)}
  {flower(606, 264, C['purple'], C['yellow'], 17)}
  {plus(520, 290, 8)}"""
    return tile(W, H, T["tiles"]["about"], "About me. Grad student at Penn. Maths background. Now: computer vision. I like problems where a tidy model runs into messy, real-world data.", content)


# ------------------------------------------------------------------------ now
def now():
    W, H = 500, 360
    rows = [("🔭", "Building ReadScreen", -1.4, "bob"), ("📚", "Vision · AI · big data", 1.2, "bob2"), ("🌈", "Making every plot colourful", -0.8, "bob3")]
    pills = ""
    for i, (emoji, text, rot, cls) in enumerate(rows):
        y = 82 + i * 78
        pills += (
            f'<g transform="rotate({rot} 238 {y + 28})"><g class="{cls}">{srect(28, y, 416, 56, 28, C["white"], sh=5)}'
            f'<text x="50" y="{y + 37}" font-size="24">{emoji}</text>'
            f'<text x="90" y="{y + 36}" font-family="{SANS}" font-size="21" font-weight="700" fill="{INK}">{text}</text></g></g>'
        )
    content = f"""
  <circle cx="44" cy="46" r="8" fill="{C['red']}" stroke="{LINE}" stroke-width="2.5"/>
  <circle cx="44" cy="46" r="8" fill="none" stroke="{C['red']}" stroke-width="3">
    <animate attributeName="r" values="8;22" dur="1.6s" repeatCount="indefinite"/>
    <animate attributeName="opacity" values="0.9;0" dur="1.6s" repeatCount="indefinite"/>
  </circle>
  <text x="64" y="53" font-family="{MONO}" font-size="19" font-weight="700" letter-spacing="3" fill="{INK}">RIGHT NOW</text>
  {pills}"""
    return tile(W, H, T["tiles"]["now"], "Right now: building ReadScreen; studying vision, AI and big data; making every plot colourful.", content)


# ---------------------------------------------------------- figure: ReadScreen
def fig_readscreen():
    W, H = 600, 352
    sx, sy, sw, sh = 38, 30, 500, 220
    body_y = sy + 38
    col = dict(kw="#7c3aed", fn="#db2777", ink=INK, cm="#7a7390")
    code_lines = [
        (0, [("def ", "kw"), ("read", "fn"), ("(photo):", "ink")]),
        (1, [("clean = ", "ink"), ("demoire", "fn"), ("(photo)", "ink")]),
        (1, [("text  = ", "ink"), ("ocr", "fn"), ("(clean)", "ink")]),
        (1, [("return ", "kw"), ("text", "ink"), ('  # not "t3xt"', "cm")]),
    ]
    code = ""
    for i, (indent, parts) in enumerate(code_lines):
        spans = "".join(f'<tspan fill="{col[c]}">{s.replace(" ", "&#160;")}</tspan>' for s, c in parts)
        code += (
            f'<text x="{sx + 28 + indent * 44}" y="{body_y + 44 + i * 38}" '
            f'font-family="{MONO}" font-size="19" font-weight="600">{spans}</text>'
        )
    sweep = 'keyTimes="0;0.1;0.6;1" dur="7s" repeatCount="indefinite"'
    x0, x1 = sx, sx + sw
    content = f"""
  {star(552, 16, 11, C['yellow'], 10)}
  {srect(sx, sy, sw, sh, 18, C['white'], sh=8)}
  <path d="M{sx + 1.5},{body_y} V{sy + 18} a16.5,16.5 0 0 1 16.5,-16.5 H{sx + sw - 18} a16.5,16.5 0 0 1 16.5,16.5 V{body_y} Z" fill="{C['yellow']}"/>
  <path d="M{sx},{body_y} H{sx + sw}" stroke="{LINE}" stroke-width="3"/>
  <circle cx="{sx + 24}" cy="{sy + 20}" r="6.5" fill="{C['pink']}" stroke="{LINE}" stroke-width="2"/>
  <circle cx="{sx + 46}" cy="{sy + 20}" r="6.5" fill="{C['green']}" stroke="{LINE}" stroke-width="2"/>
  <circle cx="{sx + 68}" cy="{sy + 20}" r="6.5" fill="{C['cyan']}" stroke="{LINE}" stroke-width="2"/>
  <text x="{sx + sw / 2}" y="{sy + 25}" text-anchor="middle" font-family="{MONO}" font-size="13.5" font-weight="700" fill="{INK}">photo_of_my_screen.jpg</text>
  {code}
  <g clip-path="url(#body)">
    <g clip-path="url(#raw)"><g style="mix-blend-mode:multiply" opacity="0.62">
      <animate attributeName="opacity" values="0;0.62;0.62;0.62" keyTimes="0;0.08;0.6;1" dur="7s" repeatCount="indefinite"/>
      {rings(700, -120, 13.0, 6.4, 66, C['pink'])}
      {rings(682, -96, 13.9, 6.4, 62, C['green'])}
    </g></g>
    <g>
      <animateTransform attributeName="transform" type="translate" values="0,0;0,0;{sw},0;{sw},0" {sweep}/>
      <rect x="{x0 - 16}" y="{body_y}" width="26" height="{sh - 38}" fill="{C['yellow']}" opacity="0.8"/>
      <rect x="{x0 - 2}" y="{body_y}" width="4.5" height="{sh - 38}" fill="{INK}"/>
    </g>
  </g>
  <g font-family="{MONO}" font-size="14.5" font-weight="700" fill="{INK}">
    <text x="{sx + 2}" y="293">readability</text>
    <text x="{sx + sw}" y="293" text-anchor="end">judged by OCR</text>
    {srect(sx + 116, 278, 240, 18, 9, C['white'], sh=3, sw=2.5)}
    <rect x="{sx + 119}" y="281" width="96" height="12" rx="6" fill="{C['green']}">
      <animate attributeName="width" values="96;96;228;228" {sweep}/>
    </rect>
  </g>
"""
    defs = f"""<clipPath id="body"><rect x="{sx + 1.5}" y="{body_y + 1.5}" width="{sw - 3}" height="{sh - 41}"/></clipPath>
  <clipPath id="raw"><rect x="{x0}" y="{sy}" width="{sw}" height="{sh}">
    <animate attributeName="x" values="{x0};{x0};{x1};{x1}" {sweep}/>
  </rect></clipPath>"""
    return tile(W, H, T["tiles"]["readscreen"], "ReadScreen: teaching models to read text through moire. A scan line sweeps across a striped screen and leaves readable code behind. PyTorch, OpenCV, ESDNet, DBNet, Tesseract.", content, defs)


# ---------------------------------------------------------------- figure: grid
def sub(base, s, size=13):
    return f'{base}<tspan dy="5" font-size="{size}">{s}</tspan><tspan dy="-5">&#8203;</tspan>'


def fig_grid():
    W, H = 600, 352
    cx, cy, R, N = 288, 138, 100, 12
    pts = [
        (cx + R * math.cos(2 * math.pi * i / N - math.pi / 2),
         cy + R * math.sin(2 * math.pi * i / N - math.pi / 2))
        for i in range(N)
    ]
    edges = [(i, (i + 1) % N) for i in range(N)] + [(0, 5), (2, 8), (4, 10), (7, 11)]
    outlier = 2
    fills = ["yellow", "pink", "green", "purple", "orange", "white", "blue"]
    lines = ""
    for k, (a, b) in enumerate(edges):
        (x1, y1), (x2, y2) = pts[a], pts[b]
        lines += (
            f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke="{INK}" stroke-width="2.6"/>'
            f'<path class="flow" style="animation-delay:-{k * 0.37:.2f}s" d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" '
            f'stroke="{C["white"]}" stroke-width="2.6" stroke-dasharray="4 20" stroke-linecap="round"/>'
        )
    nodes = ""
    for i, (x, y) in enumerate(pts):
        is_out = i == outlier
        fill = C["red"] if is_out else C[fills[i % len(fills)]]
        dur = "3.1s" if is_out else "4.6s"
        if is_out:
            nodes += (
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="17" fill="none" stroke="{C["red"]}" stroke-width="3">'
                '<animate attributeName="r" values="17;34" dur="1.8s" repeatCount="indefinite"/>'
                '<animate attributeName="opacity" values="0.9;0" dur="1.8s" repeatCount="indefinite"/></circle>'
            )
        nodes += (
            f'{scirc(round(x, 1), round(y, 1), 17, fill, sh=3, sw=2.8)}'
            f'<g stroke="{INK}" stroke-width="3" stroke-linecap="round">'
            f'<path d="M{x:.1f},{y:.1f} v-11.5"/>'
            f'<animateTransform attributeName="transform" type="rotate" from="0 {x:.1f} {y:.1f}" to="360 {x:.1f} {y:.1f}" dur="{dur}" repeatCount="indefinite"/></g>'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.8" fill="{INK}"/>'
        )
    w, th, A = sub("ω", "i"), sub("θ", "i"), sub("A", "ij")
    eq = f'I&#160;d{w}/dt = {sub("P", "i")} − D{w} − κ&#160;Σ&#160;{A}&#160;sin({th} − {sub("θ", "j")})'
    content = f"""
  {star(44, 44, 15, C['yellow'], 10)}{star(534, 226, 13, C['white'], 14)}
  <g fill="none">{lines}</g>
  {nodes}
  {srect(66, 268, 444, 46, 23, C['white'], sh=5)}
  <text x="{cx}" y="298" text-anchor="middle" font-family="{SERIF}" font-style="italic" font-weight="600" font-size="20" fill="{INK}">{eq}</text>
"""
    css = """
    .flow { animation: flow 2.4s linear infinite; }
    @keyframes flow { to { stroke-dashoffset: -24; } }"""
    return tile(W, H, T["tiles"]["grid"], "Grid stability: when does a power grid fall out of step? A network of colourful oscillators turning in step, one red node drifting. NumPy, SciPy, NetworkX, pandas.", content, css=css)


# -------------------------------------------------------------------- toolbox
def toolbox():
    W, H = 760, 300
    rows = [["Python", "PyTorch", "NumPy", "SciPy", "OpenCV"], ["Jupyter", "R", "MATLAB", "NetworkX", "pandas"]]
    cw_, pad, gap, ph = 13.4, 23, 13, 46
    out, n = "", 0
    for r, row in enumerate(rows):
        x, y = 30, 92 + r * (ph + 22)
        for s in row:
            w = len(s) * cw_ + 2 * pad
            col = C[["yellow", "pink", "cyan", "green", "orange", "white"][n % 6]]
            rot = (-2.2, 1.6, -1.2, 2.4, -1.8)[n % 5]
            cls = ("bob", "bob2", "bob3")[n % 3]
            out += (
                f'<g transform="rotate({rot} {x + w / 2:.0f} {y + ph / 2:.0f})"><g class="{cls}">'
                f'{srect(round(x, 1), y, round(w, 1), ph, ph / 2, col, sh=5)}'
                f'<text x="{x + w / 2:.1f}" y="{y + 31}" text-anchor="middle" textLength="{len(s) * cw_:.0f}" lengthAdjust="spacing" '
                f'font-family="{MONO}" font-size="21.5" font-weight="700" fill="{INK}">{s}</text></g></g>'
            )
            x += w + gap
            n += 1
    content = f"""
  {label(30, 26, "TOOLBOX", C['white'], rot=-2)}
  {out}
  <text x="34" y="250" font-family="{MONO}" font-size="15" font-weight="700" fill="{INK}" fill-opacity="0.8">…plus whatever the problem asks for.</text>
  {star(690, 50, 18, C['yellow'], 9)}{star(640, 244, 12, C['pink'], 13)}"""
    css = """
    .bob, .bob2, .bob3 { animation-name: bobsmall; }
    @keyframes bobsmall { 0%, 100% { transform: translateY(-2px); } 50% { transform: translateY(3px); } }"""
    return tile(W, H, T["tiles"]["toolbox"], "Toolbox: Python, PyTorch, NumPy, SciPy, OpenCV, Jupyter, R, MATLAB, NetworkX, pandas.", content, css=css)


# --------------------------------------------------------------------- belief
def belief():
    W, H = 440, 300
    content = f"""
  <text x="24" y="118" font-family="{SERIF}" font-size="120" font-weight="700" fill="{C['pink']}" stroke="{LINE}" stroke-width="3" paint-order="stroke fill">“</text>
  <g font-family="{SANS}" font-size="31" font-weight="900" fill="{INK}">
    <text x="96" y="80">Measure</text>
    <text x="32" y="120">the thing you</text>
    <text x="32" y="160">care about.</text>
  </g>
  <g font-family="{SANS}" font-size="17" font-weight="600" fill="{INK}" fill-opacity="0.8">
    <text x="32" y="206">A higher PSNR never helped</text>
    <text x="32" y="229">anyone read a blurry digit.</text>
  </g>
  {star(356, 52, 17, C['white'], 10)}{flower(360, 214, C['cyan'], C['white'], 15)}"""
    return tile(W, H, T["tiles"]["belief"], "Measure the thing you care about. A higher PSNR never helped anyone read a blurry digit.", content)


# ------------------------------------------------------------------- timeline
def timeline():
    W, H = 1200, 290
    y = 80
    stops = [
        (147, "’24", "pink", ["mathematical modelling", "CFD · a first ML course"]),
        (441, "’25", "yellow", ["scientific computation", "statistics in R"]),
        (735, "’26", "green", ["power-grid dynamics", "small-world networks"]),
        (1029, "now", "purple", ["computer vision at Penn", "reading text through moiré"]),
    ]
    marks = ""
    for x, year, col, desc in stops:
        is_now = year == "now"
        inner = (
            f'{scirc(0, 0, 40, C[col], sh=6)}'
            f'<text x="0" y="10" text-anchor="middle" font-family="{SANS}" font-size="{26 if is_now else 30}" font-weight="900" fill="{INK}">{year}</text>'
        )
        marks += f'<g transform="translate({x},{y})"><g class="{"hop" if is_now else ""}">{inner}</g></g>'
        marks += (
            f'<text x="{x}" y="172" text-anchor="middle" font-family="{SANS}" font-size="20" font-weight="800" fill="{INK}">{desc[0]}</text>'
            f'<text x="{x}" y="198" text-anchor="middle" font-family="{SANS}" font-size="17.5" font-weight="500" fill="{INK}" fill-opacity="0.75">{desc[1]}</text>'
        )
    content = f"""
  <path class="dash" d="M147,{y} H1029" stroke="{INK}" stroke-width="4" stroke-dasharray="4 10" stroke-linecap="round"/>
  {star(294, y, 13, C['white'], 9)}{star(588, y, 13, C['cyan'], 11)}{star(882, y, 13, C['pink'], 13)}
  {marks}
  {star(1118, 40, 14, C['yellow'], 8)}
  <text x="588" y="244" text-anchor="middle" font-family="{MONO}" font-size="14" font-weight="700" letter-spacing="4" fill="{INK}">THE STORY SO FAR</text>"""
    css = """
    .dash { animation: dash 1.6s linear infinite; }
    @keyframes dash { to { stroke-dashoffset: -28; } }
    .hop { animation: hop 1.5s cubic-bezier(.3,0,.3,1) infinite; }
    @keyframes hop { 0%, 100% { transform: translateY(0); } 45% { transform: translateY(-13px); } }"""
    return tile(W, H, T["tiles"]["timeline"], "The story so far. 2024: mathematical modelling, CFD, a first ML course. 2025: scientific computation, statistics in R. 2026: power-grid dynamics, small-world networks. Now: computer vision at Penn, reading text through moire.", content, css=css)


# --------------------------------------------------------------------- footer
def footer():
    W, H = 1200, 120
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="To be continued">
<defs>{base_defs()}</defs>
<style>
  .arrow {{ animation: nudge 1.6s ease-in-out infinite; }}
  @keyframes nudge {{ 0%, 100% {{ transform: translateX(0); }} 50% {{ transform: translateX(12px); }} }}
  {REDUCED}
</style>
{star(352, 44, 18, C['yellow'], 9)}{star(862, 84, 14, C['cyan'], 12)}{flower(300, 86, C['purple'], C['yellow'], 16)}{flower(908, 38, C['orange'], C['white'], 20)}
{srect(398, 24, 400, 64, 32, C['yellow'], sh=8)}
<text x="556" y="66" text-anchor="middle" textLength="212" lengthAdjust="spacing" font-family="{SANS}" font-size="27" font-weight="800" fill="{INK}">To be continued</text>
<g class="arrow" fill="none" stroke="{INK}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
  <path d="M700,56 h56"/><path d="M742,43 l14,13 l-14,13"/>
</g>
</svg>
"""


# The README uses these five. about(), now(), toolbox() and belief() are spare
# tiles for an all-image collage layout; add them here to generate them too.
ASSETS = {
    "hero": hero,
    "readscreen": fig_readscreen,
    "grid": fig_grid,
    "timeline": timeline,
    "footer": footer,
}


def write(theme, folder):
    use(theme)
    folder.mkdir(parents=True, exist_ok=True)
    for old in folder.glob("*.svg"):
        old.unlink()
    for name, draw in ASSETS.items():
        (folder / f"{name}.svg").write_text(draw())


def main():
    import sys
    if "--all" in sys.argv:
        for theme in THEMES:
            write(theme, OUT.parent / "options" / theme)
            print("options/" + theme)
    write(THEME, OUT)
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.name:18s} {f.stat().st_size / 1024:5.1f} KB")


if __name__ == "__main__":
    main()
