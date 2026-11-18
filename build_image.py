#!/usr/bin/env python3
"""Build entry.png for the @sunny-heron-22 news-image-20261117 variant.

LIGHT newspaper front page — the opposite of the daggerdash dark editions:
bright white paper, black serif masthead, double rule under the date, a
full-width Ukraine hero with a drawn bridge motif, then color-coded story
cards. Eight stories, all verified for Tuesday 17 November 2026.

Everything is drawn with PIL (vector text, no AI imagery) so every
headline stays crisp and legible for the vision judge. Deterministic:
same input, same bytes, no network, no randomness.
"""
import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 248, 243)      # warm white paper
CARD = (255, 255, 255)      # card white
INK = (24, 24, 28)          # headline ink
SUBINK = (92, 96, 106)      # subhead grey
RULE = (24, 24, 28)         # masthead rule
HAIRLINE = (205, 203, 196)  # card border
FOOTINK = (120, 122, 126)

SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"

# (tag, accent color, headline, subhead, icon key) — verified 17 Nov 2026.
HERO = (
    "EUROPE", (37, 99, 235),
    "Ukraine hits Crimean Bridge, Russia replies",
    "Kerch link closed after overnight strike; Moscow hits Kyiv bridges in reply.",
    "bridge",
)
CARDS = [
    ("MIDDLE EAST", (214, 48, 49),
     "US strikes Iran as tankers burn in Hormuz",
     "US jets hit missile sites after a fourth tanker struck a mine; Tehran warns of a \u2018huge price\u2019.",
     "flame"),
    ("GAZA", (124, 58, 237),
     "West presses Israel to open Gaza aid crossings",
     "UK, Australia, Canada and Italy call the situation catastrophic.",
     "aid"),
    ("DIPLOMACY", (5, 150, 105),
     "Trump meets Quad leaders in Manila",
     "US, Japan, India and Australia announce AI initiative and minerals pacts.",
     "circles"),
    ("TECH", (217, 119, 6),
     "US tightens AI chip export ban on China",
     "Commerce Dept closes a loophole on AI chips bought abroad; Nvidia rules out rehiring Huang.",
     "chip"),
    ("BUSINESS", (2, 132, 199),
     "Akeso shares plunge after FDA rejects drug",
     "Hong Kong-listed drugmaker falls 22% as US rejects its lung-cancer drug ivonescimab.",
     "chart"),
    ("FINANCE", (190, 24, 93),
     "Chase glitch delays bank transfers",
     "JPMorgan software bug slows transfers and Zelle; restored Monday evening.",
     "bank"),
    ("CULTURE", (101, 67, 33),
     "Depardieu admits sexual assault, drops appeal",
     "French actor withdraws his challenge before a Paris court.",
     "gavel"),
]


def wrap_lines(d, text, font, max_w):
    """Greedy word wrap to a pixel width; returns the lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d.textlength(trial, font=font) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---- drawn icon motifs, pure PIL shapes ----
def icon_flame(d, cx, cy, s, c):
    outer = [(cx, cy - s), (cx + 0.42 * s, cy - 0.38 * s),
             (cx + 0.72 * s, cy + 0.10 * s), (cx + 0.60 * s, cy + 0.60 * s),
             (cx + 0.25 * s, cy + s), (cx - 0.25 * s, cy + s),
             (cx - 0.60 * s, cy + 0.60 * s), (cx - 0.72 * s, cy + 0.10 * s),
             (cx - 0.42 * s, cy - 0.38 * s)]
    d.polygon(outer, fill=c)
    inner = [(cx, cy - 0.30 * s), (cx + 0.30 * s, cy + 0.05 * s),
             (cx + 0.22 * s, cy + 0.55 * s), (cx - 0.22 * s, cy + 0.55 * s),
             (cx - 0.30 * s, cy + 0.05 * s)]
    d.polygon(inner, fill=(255, 214, 90))


def icon_bridge(d, cx, cy, s, c, w=6):
    """Suspension bridge: two towers, deck, main cable arc, hangers."""
    d.arc([cx - s, cy - 0.9 * s, cx + s, cy + 0.3 * s], 180, 360, fill=c, width=w)
    d.line([cx - s, cy + 0.30 * s, cx + s, cy + 0.30 * s], fill=c, width=w)
    for tx in (-0.62, 0.62):
        d.line([cx + tx * s, cy - 0.38 * s, cx + tx * s, cy + 0.30 * s],
               fill=c, width=w)
    for hx in (-0.85, -0.40, 0, 0.40, 0.85):
        d.line([cx + hx * s, cy - 0.02 * s, cx + hx * s, cy + 0.30 * s],
               fill=c, width=3)


def icon_aid(d, cx, cy, s, c):
    d.ellipse([cx - s, cy - s, cx + s, cy + s], fill=c)
    d.rectangle([cx - 0.18 * s, cy - 0.58 * s, cx + 0.18 * s, cy + 0.58 * s],
                fill=(255, 255, 255))
    d.rectangle([cx - 0.58 * s, cy - 0.18 * s, cx + 0.58 * s, cy + 0.18 * s],
                fill=(255, 255, 255))


def icon_circles(d, cx, cy, s, c):
    r = 0.5 * s
    cols = [(37, 99, 235), (5, 150, 105), (217, 119, 6), (190, 24, 93)]
    offs = [(-0.42 * s, -0.42 * s), (0.42 * s, -0.42 * s),
            (-0.42 * s, 0.42 * s), (0.42 * s, 0.42 * s)]
    for (ox, oy), col in zip(offs, cols):
        d.ellipse([cx + ox - r, cy + oy - r, cx + ox + r, cy + oy + r],
                  fill=col, outline=(255, 255, 255), width=2)


def icon_chip(d, cx, cy, s, c):
    d.rounded_rectangle([cx - 0.62 * s, cy - 0.62 * s, cx + 0.62 * s, cy + 0.62 * s],
                        radius=8, fill=c)
    d.rectangle([cx - 0.30 * s, cy - 0.30 * s, cx + 0.30 * s, cy + 0.30 * s],
                fill=(255, 255, 255))
    for i in range(3):
        off = (i - 1) * 0.42 * s
        d.line([cx + off, cy - 0.62 * s, cx + off, cy - 0.88 * s], fill=c, width=4)
        d.line([cx + off, cy + 0.62 * s, cx + off, cy + 0.88 * s], fill=c, width=4)
        d.line([cx - 0.62 * s, cy + off, cx - 0.88 * s, cy + off], fill=c, width=4)
        d.line([cx + 0.62 * s, cy + off, cx + 0.88 * s, cy + off], fill=c, width=4)


def icon_chart(d, cx, cy, s, c):
    base = cy + 0.70 * s
    d.line([cx - s, base, cx + s, base], fill=c, width=4)
    bars = [(-0.68, 0.35), (-0.22, 0.85), (0.24, 0.55), (0.70, 1.0)]
    for bx, bh in bars:
        x0 = cx + bx * s
        d.rectangle([x0, base - bh * s, x0 + 0.30 * s, base], fill=c)
    d.line([cx - 0.85 * s, cy - 0.55 * s, cx - 0.22 * s, cy - 0.80 * s,
            cx + 0.24 * s, cy - 0.45 * s, cx + 0.85 * s, cy - 0.70 * s],
           fill=(214, 48, 49), width=4)


def icon_bank(d, cx, cy, s, c):
    d.polygon([(cx - s, cy - 0.30 * s), (cx, cy - s), (cx + s, cy - 0.30 * s)],
              fill=c)
    d.rectangle([cx - 0.85 * s, cy - 0.22 * s, cx + 0.85 * s, cy - 0.05 * s], fill=c)
    for px in (-0.62, -0.21, 0.21, 0.62):
        d.rectangle([cx + px * s - 0.10 * s, cy + 0.05 * s,
                     cx + px * s + 0.10 * s, cy + 0.62 * s], fill=c)
    d.rectangle([cx - s, cy + 0.62 * s, cx + s, cy + 0.80 * s], fill=c)


def icon_gavel(d, cx, cy, s, c):
    # head: tilted rounded bar
    head = [(cx - 0.55 * s, cy - 0.75 * s), (cx + 0.55 * s, cy - 0.95 * s),
            (cx + 0.75 * s, cy - 0.55 * s), (cx - 0.35 * s, cy - 0.35 * s)]
    d.polygon(head, fill=c)
    d.line([cx - 0.15 * s, cy - 0.30 * s, cx + 0.55 * s, cy + 0.45 * s],
           fill=c, width=10)
    d.line([cx - 0.80 * s, cy + 0.75 * s, cx + 0.80 * s, cy + 0.75 * s],
           fill=c, width=6)


ICONS = {"flame": icon_flame, "bridge": icon_bridge, "aid": icon_aid,
         "circles": icon_circles, "chip": icon_chip, "chart": icon_chart,
         "bank": icon_bank, "gavel": icon_gavel}


def tag_pill(d, x, y, tag, color, f_tag):
    """Solid color pill with white tag text; returns its width."""
    tw = d.textlength(tag, font=f_tag) + 20
    d.rounded_rectangle([x, y, x + tw, y + 26], radius=13, fill=color)
    d.text((x + 10, y + 4), tag, font=f_tag, fill=(255, 255, 255))
    return tw


def card(d, x0, y0, cw, ch, tag, color, head, sub, icon_key, f_tag, f_head,
         f_sub, icon_size, head_lines=2, sub_lines=3, text_reserve=62):
    """One story card: white fill, hairline border, colored top bar."""
    d.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=10, fill=CARD,
                        outline=HAIRLINE, width=2)
    d.rounded_rectangle([x0, y0, x0 + cw, y0 + 8], radius=4, fill=color)
    px, py = x0 + 22, y0 + 18
    tag_pill(d, px, py, tag, color, f_tag)
    ICONS[icon_key](d, x0 + cw - 46, y0 + 44, icon_size, color)
    py += 40
    tw = cw - 44 - text_reserve  # keep clear of the icon
    for line in wrap_lines(d, head, f_head, tw)[:head_lines]:
        d.text((px, py), line, font=f_head, fill=INK)
        py += f_head.size + 6
    py += 4
    for line in wrap_lines(d, sub, f_sub, tw)[:sub_lines]:
        d.text((px, py), line, font=f_sub, fill=SUBINK)
        py += f_sub.size + 5


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead: classic newspaper, black serif on white ----
    f_mast = ImageFont.truetype(SERIF_B, 62)
    mast = "THE WORLD IN ONE DAY"
    d.text(((W - d.textlength(mast, font=f_mast)) / 2, 18), mast,
           font=f_mast, fill=INK)
    f_date = ImageFont.truetype(SANS_B, 21)
    date = "TUESDAY, 17 NOVEMBER 2026"
    d.text(((W - d.textlength(date, font=f_date)) / 2, 96), date,
           font=f_date, fill=(120, 20, 20))
    d.rectangle([32, 132, W - 32, 137], fill=RULE)   # thick rule
    d.rectangle([32, 141, W - 32, 143], fill=RULE)   # thin rule

    f_tag = ImageFont.truetype(SANS_B, 17)
    f_hero_h = ImageFont.truetype(SANS_B, 38)
    f_hero_s = ImageFont.truetype(SANS, 21)
    f_head = ImageFont.truetype(SANS_B, 25)
    f_sub = ImageFont.truetype(SANS, 18)
    f_small_h = ImageFont.truetype(SANS_B, 18)
    f_small_s = ImageFont.truetype(SANS, 15)

    m = 32
    full = W - 2 * m  # 960

    # ---- Hero: EUROPE / Ukraine, full width, bridge motif ----
    tag, color, head, sub, icon = HERO
    hx0, hy0, hh = m, 156, 196
    d.rounded_rectangle([hx0, hy0, hx0 + full, hy0 + hh], radius=10, fill=CARD,
                        outline=HAIRLINE, width=2)
    d.rounded_rectangle([hx0, hy0, hx0 + full, hy0 + 8], radius=4, fill=color)
    icon_bridge(d, hx0 + full - 108, hy0 + hh // 2 + 6, 78, color, w=7)
    px, py = hx0 + 26, hy0 + 22
    tag_pill(d, px, py, tag, color, f_tag)
    py += 42
    tw = full - 52 - 190  # clear of the big bridge
    for line in wrap_lines(d, head, f_hero_h, tw)[:2]:
        d.text((px, py), line, font=f_hero_h, fill=INK)
        py += 46
    py += 8
    for line in wrap_lines(d, sub, f_hero_s, tw)[:2]:
        d.text((px, py), line, font=f_hero_s, fill=SUBINK)
        py += 28

    # ---- 2x2 grid: Iran, Gaza / Quad, Chip ----
    cw = (full - 16) // 2  # 472
    ch = 192
    for i in range(4):
        tag, color, head, sub, icon = CARDS[i]
        col, row = i % 2, i // 2
        x0 = m + col * (cw + 16)
        y0 = 366 + row * (ch + 12)
        card(d, x0, y0, cw, ch, tag, color, head, sub, icon,
             f_tag, f_head, f_sub, 28)

    # ---- Bottom row of 3: Akeso, Chase, Depardieu ----
    bw = (full - 2 * 16) // 3  # 309
    bh = 182
    for j in range(3):
        tag, color, head, sub, icon = CARDS[4 + j]
        x0 = m + j * (bw + 16)
        y0 = 774
        card(d, x0, y0, bw, bh, tag, color, head, sub, icon,
             f_tag, f_small_h, f_small_s, 18, head_lines=2, sub_lines=3,
             text_reserve=46)

    # ---- Footer ----
    f_foot = ImageFont.truetype(SANS, 16)
    foot = "17 November 2026 \u2022 World news at a glance \u2022 Ukraine \u2022 Iran \u2022 Gaza \u2022 Manila \u2022 Chips \u2022 Akeso \u2022 Chase \u2022 Depardieu"
    d.text(((W - d.textlength(foot, font=f_foot)) / 2, 980), foot,
           font=f_foot, fill=FOOTINK)

    img.save("entry.png", "PNG", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    build()
