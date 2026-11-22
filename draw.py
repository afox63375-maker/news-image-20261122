#!/usr/bin/env python3
"""
draw.py -- renders entry.png for the make.fun bounty news-image-20261122.

One broadsheet-style front page, 1024x1024, that sums up Sunday
22 November 2026 in 35 stories. Everything on the page -- the three
large story scenes, the ten small card scenes, the dotted world map,
the weather icons -- is drawn here with Pillow primitives, so two runs
produce byte-identical output (the only randomness is a fixed seed).

This script is a workshop tool. The repository entrypoint (main.py)
is separate and uses only the Python standard library.
"""

import math
import random

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- canvas

PAGE_W = 1024
PAGE_H = 1024
EDGE = 12                      # outer margin
INNER_W = PAGE_W - 2 * EDGE    # usable width

CREAM = (246, 242, 231)
PAPER = (250, 248, 240)
INK = (22, 22, 22)
NAVY = (17, 33, 57)
RED = (178, 33, 38)
DEEP_RED = (140, 24, 28)
GREY = (96, 92, 84)
RULE = (178, 170, 152)

REGION_COLOURS = {
    "EU": (58, 104, 158),      # Europe -- steel blue
    "ME": (168, 44, 40),       # Middle East -- brick red
    "AM": (94, 122, 54),       # Americas -- olive green
    "AP": (122, 78, 140),      # Asia-Pacific -- purple
    "AF": (196, 138, 44),      # Africa -- ochre
    "WO": (70, 70, 70),        # World -- charcoal
}
REGION_NAMES = {
    "EU": "EUROPE", "ME": "MIDDLE EAST", "AM": "AMERICAS",
    "AP": "ASIA-PACIFIC", "AF": "AFRICA", "WO": "WORLD",
}

FONT_FILES = {
    "serif_b": "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "serif": "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    "serif_i": "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
    "sans_b": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "sans": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "sans_o": "/usr/share/fonts/truetype/liberation/LiberationSans-Italic.ttf",
}
_font_cache = {}


def F(kind, size):
    key = (kind, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONT_FILES[kind], size)
    return _font_cache[key]


# ---------------------------------------------------------------- text

def text_w(d, s, fnt):
    return d.textlength(s, font=fnt)


def wrap_lines(d, s, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines = []
    current = ""
    for word in s.split():
        trial = word if not current else current + " " + word
        if text_w(d, trial, fnt) <= max_w:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_wrapped(d, xy, s, fnt, fill, max_w, line_h, max_lines=None):
    lines = wrap_lines(d, s, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    x, y = xy
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += line_h
    return y


def centred(d, cx, y, s, fnt, fill):
    d.text((cx - text_w(d, s, fnt) / 2, y), s, font=fnt, fill=fill)


# ---------------------------------------------------------------- shapes

def flame(d, cx, base_y, height, palette=((232, 110, 30), (244, 164, 40), (250, 214, 90))):
    """A simple teardrop flame: layered pointed ovals."""
    for i, colour in enumerate(palette):
        h = height * (1.0 - 0.26 * i)
        w = height * 0.30 * (1.0 - 0.20 * i)
        tip_y = base_y - h
        pts = []
        for t in range(21):
            a = math.pi * t / 20.0
            pts.append((cx - w * math.sin(a) * (1 - 0.35 * t / 20.0), base_y - h * t / 20.0))
        for t in range(20, -1, -1):
            a = math.pi * t / 20.0
            pts.append((cx + w * math.sin(a) * (1 - 0.35 * t / 20.0), base_y - h * t / 20.0))
        d.polygon(pts, fill=colour)
        base_y = base_y  # flames share the same base line
        _ = tip_y


def smoke(d, cx, cy, r, colour=(120, 118, 116)):
    d.ellipse([cx - r, cy - r * 0.62, cx + r, cy + r * 0.62], fill=colour)
    d.ellipse([cx - r * 0.4, cy - r * 0.95, cx + r * 0.75, cy + r * 0.2], fill=colour)


def person(d, cx, base_y, h, shirt, skin=(222, 184, 150)):
    """Tiny standing/seated figure: round head, blocky torso."""
    head_r = h * 0.16
    d.ellipse([cx - head_r, base_y - h, cx + head_r, base_y - h + 2 * head_r], fill=skin)
    d.rectangle([cx - h * 0.20, base_y - h + 2 * head_r - 1, cx + h * 0.20, base_y], fill=shirt)


def kicker_tag(d, x, y, main, sub=None):
    """Red kicker label at a scene's top-left, optional black sub-label."""
    fnt = F("sans_b", 11)
    w = text_w(d, main, fnt) + 12
    d.rectangle([x, y, x + w, y + 17], fill=RED)
    d.text((x + 6, y + 3), main, font=fnt, fill=(255, 255, 255))
    if sub:
        fnt2 = F("sans_b", 8)
        w2 = text_w(d, sub, fnt2) + 10
        d.rectangle([x, y + 17, x + w2, y + 31], fill=(20, 20, 20))
        d.text((x + 5, y + 20), sub, font=fnt2, fill=(255, 255, 255))


def chip_tag(d, x, y, s, align_right=False, dark=False):
    """Small white (or dark) chip, e.g. a count at a scene's top-right."""
    fnt = F("sans_b", 10)
    w = text_w(d, s, fnt) + 10
    if align_right:
        x = x - w
    bg = (24, 24, 24) if dark else (250, 248, 240)
    fg = (250, 248, 240) if dark else INK
    d.rectangle([x, y, x + w, y + 16], fill=bg)
    d.text((x + 5, y + 3), s, font=fnt, fill=fg)
    return x


def foot_tag(d, x, y_bottom, s):
    """Small dark source tag at a scene's bottom-left."""
    fnt = F("sans", 8)
    w = text_w(d, s, fnt) + 10
    d.rectangle([x, y_bottom - 14, x + w, y_bottom], fill=(24, 24, 24))
    d.text((x + 5, y_bottom - 11), s, font=fnt, fill=(240, 238, 230))


def new_scene(w, h, bg):
    img = Image.new("RGB", (w, h), bg)
    return img, ImageDraw.Draw(img)


# ---------------------------------------------------------------- weather icons

def icon_sun(d, x, y, s=18, colour=(232, 164, 32)):
    cx, cy, r = x + s / 2, y + s / 2, s * 0.26
    for a in range(0, 360, 45):
        rad = math.radians(a)
        d.line([cx + (r + 2) * math.cos(rad), cy + (r + 2) * math.sin(rad),
                cx + (r + 5) * math.cos(rad), cy + (r + 5) * math.sin(rad)],
               fill=colour, width=2)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=colour)


def icon_cloud(d, x, y, s=18, colour=(120, 128, 138)):
    d.ellipse([x + 1, y + s * 0.38, x + s * 0.55, y + s * 0.82], fill=colour)
    d.ellipse([x + s * 0.32, y + s * 0.18, x + s * 0.85, y + s * 0.82], fill=colour)
    d.rectangle([x + 1, y + s * 0.62, x + s * 0.85, y + s * 0.84], fill=colour)


def icon_sun_cloud(d, x, y, s=18):
    icon_sun(d, x, y, int(s * 0.72), (232, 164, 32))
    icon_cloud(d, x + s * 0.22, y + s * 0.28, int(s * 0.78), (110, 118, 128))


def icon_snow(d, x, y, s=18):
    icon_cloud(d, x, y, s, (110, 120, 140))
    fnt = F("sans_b", 9)
    for dx in (2, 8, 14):
        d.text((x + dx, y + s * 0.78), "*", font=fnt, fill=(90, 120, 170))


WEATHER_ICONS = {"sun": icon_sun, "cloud": icon_cloud,
                 "sun_cloud": icon_sun_cloud, "snow": icon_snow}

WEATHER = [
    ("ANTALYA", "sun_cloud", "19/13"),
    ("KYIV", "snow", "1/-4"),
    ("MANAMA", "sun", "28/21"),
    ("TEHRAN", "sun_cloud", "10/2"),
    ("SINALOA", "sun", "31/19"),
    ("CANBERRA", "cloud", "24/11"),
]

# ---------------------------------------------------------------- world map
# Continents as unions of ellipses in (lon, lat, rx, ry); a dot is land
# when its centre falls inside any ellipse. Stylised, like a newspaper's.

LAND_BLOBS = [
    # North America
    (-100, 49, 36, 15), (-88, 37, 20, 9), (-152, 64, 13, 5.5),
    (-96, 60, 20, 7), (-84, 16, 9, 4.5), (-42, 73, 11, 5.5),
    (-118, 33, 10, 6), (-75, 45, 10, 7), (-105, 24, 8, 6),
    # South America
    (-61, -10, 11, 13), (-69, -24, 6.5, 13), (-52, -5, 8, 6),
    # Europe
    (14, 50, 17, 8), (16, 62, 11, 6), (-4, 40.5, 6.5, 3.5),
    (-2, 53.5, 2.8, 3.5), (28, 55, 10, 6), (13, 42.5, 3, 5),
    (22, 46, 9, 5),
    # Africa
    (17, 7, 18, 17), (21, -17, 12, 11), (47, -19, 2.8, 5.5), (8, 10, 12, 8),
    # Asia
    (60, 52, 32, 11), (105, 50, 38, 12), (140, 55, 25, 10),
    (78, 21, 8.5, 9), (45, 24.5, 9.5, 6.5), (102, 14, 7, 8),
    (108, 32, 15, 9.5), (127, 37, 4, 4), (138, 37, 4.5, 4.5),
    (113, -1.5, 13, 2.8), (100, 7, 3, 5), (90, 24, 8, 6),
    # Oceania
    (134, -25, 12.5, 7.5), (146, -28, 7, 6), (172, -42, 2.5, 4),
    (141, -13, 5, 3),
]

MAP_LON = (-180.0, 180.0)
MAP_LAT = (82.0, -58.0)


def map_project(lon, lat, mx, my, mw, mh):
    px = mx + (lon - MAP_LON[0]) / (MAP_LON[1] - MAP_LON[0]) * mw
    py = my + (MAP_LAT[0] - lat) / (MAP_LAT[0] - MAP_LAT[1]) * mh
    return px, py


def is_land(lon, lat):
    for cx, cy, rx, ry in LAND_BLOBS:
        if ((lon - cx) / rx) ** 2 + ((lat - cy) / ry) ** 2 <= 1.0:
            return True
    return False


def draw_map(d, mx, my, mw, mh, pins):
    step = 5.4
    cols = int(mw / step)
    rows = int(mh / step)
    for r in range(rows):
        for c in range(cols):
            px = mx + c * step + step / 2
            py = my + r * step + step / 2
            lon = MAP_LON[0] + (px - mx) / mw * (MAP_LON[1] - MAP_LON[0])
            lat = MAP_LAT[0] - (py - my) / mh * (MAP_LAT[0] - MAP_LAT[1])
            if is_land(lon, lat):
                d.ellipse([px - 1.5, py - 1.5, px + 1.5, py + 1.5], fill=(168, 152, 116))
    for num, lon, lat, region, dx, dy in pins:
        px, py = map_project(lon, lat, mx, my, mw, mh)
        px += dx
        py += dy
        colour = REGION_COLOURS[region]
        rad = 8 if num >= 10 else 7
        d.ellipse([px - rad, py - rad, px + rad, py + rad], fill=colour,
                  outline=(250, 248, 240), width=1)
        fnt = F("sans_b", 8)
        label = str(num)
        d.text((px - text_w(d, label, fnt) / 2, py - 4.5), label,
               font=fnt, fill=(255, 255, 255))


# ---------------------------------------------------------------- big scenes

def scene_cop31(w, h):
    """Antalya: delegates around a long table, a globe, a clock near 03:00."""
    img, d = new_scene(w, h, (168, 205, 198))
    d.rectangle([0, h * 0.62, w, h], fill=(196, 178, 148))          # floor
    # globe, left
    gx, gy, gr = 52, 46, 30
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], fill=(64, 116, 178))
    d.polygon([(gx - 18, gy - 16), (gx - 2, gy - 22), (gx + 2, gy - 8),
               (gx - 8, gy + 2), (gx - 20, gy - 4)], fill=(84, 150, 92))
    d.polygon([(gx + 8, gy + 8), (gx + 22, gy + 4), (gx + 24, gy + 16),
               (gx + 10, gy + 20)], fill=(84, 150, 92))
    d.line([gx - 6, gy + gr, gx - 12, gy + gr + 10], fill=(90, 90, 90), width=3)
    # wall clock, right, hands at 3:00
    cx, cy, cr = w - 52, 44, 27
    d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=(250, 248, 240),
              outline=(30, 30, 30), width=3)
    for a in range(0, 360, 30):
        rad = math.radians(a)
        d.line([cx + (cr - 5) * math.cos(rad), cy + (cr - 5) * math.sin(rad),
                cx + (cr - 2) * math.cos(rad), cy + (cr - 2) * math.sin(rad)],
               fill=(30, 30, 30), width=1)
    d.line([cx, cy, cx, cy - 15], fill=(30, 30, 30), width=3)        # to 12
    d.line([cx, cy, cx + 18, cy], fill=RED, width=3)                 # to 3
    d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(30, 30, 30))
    # long negotiating table with seated delegates
    tx0, tx1, ty = 66, w - 20, int(h * 0.66)
    d.rectangle([tx0, ty, tx1, ty + 12], fill=(122, 84, 50))
    d.rectangle([tx0, ty + 12, tx1, h], fill=(240, 236, 226))
    shirts = [(70, 90, 140), (150, 60, 60), (60, 110, 80), (120, 100, 40),
              (90, 70, 130), (50, 120, 130), (160, 90, 40), (80, 80, 80)]
    n = len(shirts)
    for i, shirt in enumerate(shirts):
        px = tx0 + 26 + i * (tx1 - tx0 - 52) / (n - 1)
        person(d, px, ty + 4, 34, shirt)
        d.rectangle([px - 7, ty + 14, px + 7, ty + 22], fill=(255, 255, 255))
    kicker_tag(d, 6, 6, "COP31: DEAL CLOSE", "TOP STORY")
    chip_tag(d, w - 6, 6, "~200 nations", align_right=True)
    foot_tag(d, 6, h - 4, "Antalya summit hall")
    return img


def scene_ukraine(w, h):
    """Kyiv: a night sky full of drones and missile streaks over a skyline."""
    img, d = new_scene(w, h, (16, 20, 44))
    rng = random.Random(20261122)
    for _ in range(70):                                              # stars
        sx, sy = rng.uniform(0, w), rng.uniform(0, h * 0.55)
        d.point((sx, sy), fill=(210, 214, 230))
    # missile streaks: bright head, fading tail
    for mx, my, ang in [(70, 26, 0.5), (150, 14, 0.35), (238, 30, 0.55), (292, 12, 0.4)]:
        for k in range(9):
            px = mx - k * 7 * math.cos(ang)
            py = my + k * 7 * math.sin(ang)
            shade = (250, 190 - k * 14, 90)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=shade)
    # drone silhouettes: small X quadcopters
    for dx, dy, s in [(40, 58, 9), (105, 44, 11), (168, 62, 9), (205, 36, 12),
                      (262, 56, 10), (300, 40, 9), (128, 78, 8), (232, 82, 8)]:
        d.line([dx - s, dy - s * 0.5, dx + s, dy + s * 0.5], fill=(200, 204, 220), width=2)
        d.line([dx - s, dy + s * 0.5, dx + s, dy - s * 0.5], fill=(200, 204, 220), width=2)
        d.ellipse([dx - 3, dy - 2, dx + 3, dy + 2], fill=(220, 224, 238))
    # skyline with lit windows and two fire glows
    base = h
    buildings = [(0, 34), (34, 52), (74, 40), (112, 60), (156, 44), (192, 54),
                 (232, 38), (266, 56), (302, 42)]
    for bx, bh in buildings:
        bw = 36
        d.rectangle([bx, base - bh, bx + bw, base], fill=(8, 10, 22))
        for wy in range(base - bh + 6, base - 6, 9):
            for wx in range(bx + 5, bx + bw - 5, 9):
                if rng.random() < 0.4:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(240, 200, 110))
    flame(d, 128, base - 52, 30)
    flame(d, 282, base - 48, 24)
    kicker_tag(d, 6, 6, "UKRAINE: BARRAGE")
    chip_tag(d, w - 6, 6, "400+ drones", align_right=True)
    foot_tag(d, 6, h - 4, "Officials' count")
    return img


def scene_bahrain(w, h):
    """Manama: an industrial shore site and a tanker burning at sea."""
    img, d = new_scene(w, h, (74, 44, 40))
    d.rectangle([0, int(h * 0.66), w, h], fill=(30, 48, 66))         # sea
    for sx in range(6, w, 26):                                       # wave ticks
        d.line([sx, h * 0.78, sx + 10, h * 0.78], fill=(70, 100, 124), width=2)
    # shore plant, left: tanks and stacks with flames
    gy = int(h * 0.66)
    d.rectangle([0, gy - 6, 150, gy], fill=(40, 36, 34))
    for tx in (16, 52, 88):
        d.rectangle([tx, gy - 30, tx + 26, gy - 6], fill=(96, 92, 88))
        d.ellipse([tx, gy - 35, tx + 26, gy - 26], fill=(120, 116, 110))
    d.rectangle([126, gy - 52, 132, gy - 6], fill=(70, 66, 62))
    smoke(d, 60, gy - 62, 17, (96, 90, 88))
    smoke(d, 96, gy - 70, 21, (110, 104, 100))
    flame(d, 42, gy - 28, 34)
    flame(d, 84, gy - 28, 42)
    flame(d, 129, gy - 50, 26)
    # tanker, right, fire amidships
    hx0, hx1, hy = 178, w - 14, int(h * 0.74)
    d.polygon([(hx0, hy), (hx1, hy), (hx1 - 16, hy + 16), (hx0 + 10, hy + 16)],
              fill=(22, 22, 26))
    d.rectangle([hx0 + 16, hy - 10, hx1 - 30, hy], fill=(120, 44, 36))
    d.rectangle([hx1 - 26, hy - 18, hx1 - 14, hy], fill=(200, 196, 188))
    smoke(d, 252, hy - 34, 15, (100, 94, 92))
    flame(d, 232, hy - 8, 30)
    flame(d, 258, hy - 8, 22)
    kicker_tag(d, 6, 6, "BAHRAIN: STRUCK")
    chip_tag(d, w - 6, 6, "2 bases", align_right=True)
    foot_tag(d, 6, h - 4, "Bahrain govt")
    return img


# ---------------------------------------------------------------- card scenes

def scene_ship(w, h):
    """Gulf of Finland: a cargo ship with fire on deck."""
    img, d = new_scene(w, h, (38, 58, 84))
    d.rectangle([0, h - 14, w, h], fill=(26, 44, 62))
    d.polygon([(14, h - 22), (w - 20, h - 22), (w - 34, h - 12), (24, h - 12)],
              fill=(24, 24, 28))
    for i, c in enumerate([(168, 52, 44), (52, 96, 150), (70, 130, 80)]):
        d.rectangle([44 + i * 30, h - 36, 68 + i * 30, h - 22], fill=c)
    d.rectangle([w - 52, h - 42, w - 40, h - 22], fill=(206, 200, 190))
    smoke(d, 108, 10, 10, (110, 106, 102))
    flame(d, 84, h - 34, 24)
    flame(d, 112, h - 34, 17)
    return img


def scene_kryvyi(w, h):
    """Kryvyi Rih: apartment blocks, an explosion burst, drifting smoke."""
    img, d = new_scene(w, h, (52, 48, 58))
    for bx, bh, bw in [(4, 34, 34), (44, 44, 30), (120, 38, 34), (160, 30, 30)]:
        d.rectangle([bx, h - bh, bx + bw, h], fill=(16, 16, 22))
        for wy2 in range(h - bh + 5, h - 6, 9):
            for wx2 in range(bx + 4, bx + bw - 4, 9):
                if (wx2 + wy2) % 3 == 0:
                    d.rectangle([wx2, wy2, wx2 + 3, wy2 + 4], fill=(240, 200, 110))
    for i in range(9):                                                # burst rays
        a = math.radians(i * 40 + 8)
        d.line([94, 20, 94 + 15 * math.cos(a), 20 + 15 * math.sin(a)],
               fill=(246, 178, 70), width=2)
    d.ellipse([86, 12, 102, 28], fill=(250, 214, 110))
    smoke(d, 108, 12, 9, (104, 100, 98))
    flame(d, 58, h - 2, 20)
    return img


def scene_boat(w, h):
    """Bayelsa: a passenger boat tipping over in the swell."""
    img, d = new_scene(w, h, (70, 118, 140))
    d.rectangle([0, h - 16, w, h], fill=(34, 78, 104))
    for sx in range(2, w, 22):
        d.arc([sx, h - 20, sx + 16, h - 8], 180, 360, fill=(150, 190, 205), width=2)
    cx, cy = w // 2, h - 24
    d.polygon([(cx - 42, cy - 8), (cx + 38, cy - 20), (cx + 26, cy - 2),
               (cx - 30, cy + 4)], fill=(110, 74, 44))                # tilted hull
    d.line([cx - 6, cy - 12, cx + 2, cy - 34], fill=(60, 44, 30), width=2)
    for i, shirt in enumerate([(180, 60, 50), (60, 110, 170), (220, 180, 60), (90, 150, 90)]):
        person(d, cx - 26 + i * 17, cy - 12 + (i % 2) * 3, 17, shirt)
    d.arc([cx + 30, cy - 12, cx + 58, cy + 10], 270, 60, fill=(230, 240, 244), width=2)
    return img


def scene_talks(w, h):
    """Jerusalem: two leaders shake hands across a small table."""
    img, d = new_scene(w, h, (196, 186, 158))
    d.rectangle([0, h - 10, w, h], fill=(150, 128, 96))
    person(d, 62, h - 12, 34, (44, 62, 110))
    person(d, 132, h - 12, 34, (96, 54, 54))
    d.line([76, h - 26, 118, h - 26], fill=(40, 34, 28), width=3)     # joined hands
    d.rectangle([86, h - 18, 108, h - 12], fill=(122, 84, 50))        # table
    d.rectangle([16, 6, 20, 26], fill=(52, 92, 160))
    d.rectangle([20, 6, 34, 12], fill=(52, 92, 160))                  # flag 1
    d.rectangle([160, 6, 164, 26], fill=(240, 238, 230))
    d.rectangle([164, 6, 178, 12], fill=(240, 238, 230), outline=(52, 92, 160))
    return img


def scene_aid(w, h):
    """Gaza: an aid truck under a burst of fire."""
    img, d = new_scene(w, h, (104, 92, 78))
    d.rectangle([0, h - 12, w, h], fill=(70, 60, 50))
    d.rectangle([30, h - 34, 108, h - 14], fill=(232, 228, 218))      # cargo box
    d.rectangle([108, h - 28, 132, h - 14], fill=(70, 96, 130))       # cab
    d.rectangle([114, h - 26, 126, h - 20], fill=(170, 200, 220))
    d.rectangle([58, h - 30, 80, h - 18], fill=RED)                   # cross arms
    d.rectangle([66, h - 33, 72, h - 15], fill=RED)
    for wx in (48, 118):
        d.ellipse([wx - 8, h - 16, wx + 8, h], fill=(22, 22, 22))
    for i in range(7):
        a = math.radians(200 + i * 22)
        d.line([160, 12, 160 + 13 * math.cos(a), 12 + 13 * math.sin(a)],
               fill=(246, 178, 70), width=2)
    d.ellipse([154, 6, 166, 18], fill=(250, 214, 110))
    smoke(d, 138, 10, 8, (96, 90, 86))
    return img


def scene_fugitive(w, h):
    """Sinaloa: a held man, hands up, between two officers."""
    img, d = new_scene(w, h, (60, 64, 74))
    d.rectangle([0, h - 10, w, h], fill=(40, 42, 48))
    person(d, 97, h - 12, 36, (186, 60, 44))
    d.line([88, h - 34, 76, h - 46], fill=(222, 184, 150), width=3)   # raised arms
    d.line([106, h - 34, 118, h - 46], fill=(222, 184, 150), width=3)
    person(d, 52, h - 12, 36, (36, 52, 92))
    person(d, 142, h - 12, 36, (36, 52, 92))
    d.rectangle([40, h - 44, 64, h - 40], fill=(24, 32, 52))         # caps
    d.rectangle([130, h - 44, 154, h - 40], fill=(24, 32, 52))
    return img


def scene_power(w, h):
    """Tehran: a pylon and dark houses under a crescent moon."""
    img, d = new_scene(w, h, (26, 30, 52))
    d.ellipse([w - 44, 4, w - 20, 28], fill=(232, 226, 190))
    d.ellipse([w - 36, 2, w - 14, 26], fill=(26, 30, 52))
    px = 52
    d.line([px, 6, px, h - 8], fill=(150, 154, 164), width=3)
    d.line([px - 20, 14, px + 20, 14], fill=(150, 154, 164), width=3)
    d.line([px - 14, 24, px + 14, 24], fill=(150, 154, 164), width=2)
    d.line([px - 20, 14, px + 20, 30], fill=(110, 114, 124), width=1)
    d.line([px + 20, 14, px - 20, 30], fill=(110, 114, 124), width=1)
    for hx, hw in [(96, 40), (142, 46)]:
        d.rectangle([hx, h - 24, hx + hw, h], fill=(12, 14, 24))
        d.polygon([(hx - 3, h - 24), (hx + hw + 3, h - 24), (hx + hw / 2, h - 34)],
                  fill=(8, 10, 18))
    d.rectangle([156, h - 18, 162, h - 12], fill=(244, 196, 92))      # one lit window
    return img


def scene_probe(w, h):
    """Washington: a falling chart line under a magnifying glass."""
    img, d = new_scene(w, h, (238, 240, 242))
    for gx in range(10, w, 18):
        d.line([gx, 4, gx, h - 4], fill=(214, 218, 222), width=1)
    pts = [(8, 12), (48, 18), (84, 30), (118, 28), (150, 42), (184, 48)]
    d.line(pts, fill=RED, width=3)
    for px, py in pts:
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    d.ellipse([104, 6, 148, 46], outline=(30, 30, 30), width=4)
    d.line([142, 40, 162, 52], fill=(30, 30, 30), width=5)
    return img


def scene_icu(w, h):
    """Brasilia: a hospital bed and a heart monitor trace."""
    img, d = new_scene(w, h, (196, 220, 222))
    d.rectangle([104, 6, 186, 34], fill=(24, 34, 40))                 # monitor
    trace = [(108, 20), (118, 20), (123, 10), (128, 28), (133, 20),
             (146, 20), (151, 12), (156, 26), (161, 20), (182, 20)]
    d.line(trace, fill=(80, 230, 140), width=2)
    d.rectangle([16, h - 18, 120, h - 10], fill=(240, 242, 244), outline=(120, 130, 134))
    d.rectangle([16, h - 26, 44, h - 10], fill=(250, 250, 250), outline=(120, 130, 134))
    d.ellipse([24, h - 24, 36, h - 14], fill=(222, 184, 150))         # patient's head
    d.rectangle([36, h - 20, 96, h - 12], fill=(96, 140, 190))        # blanket
    return img


def scene_aukus(w, h):
    """Canberra: a submarine running just under the surface."""
    img, d = new_scene(w, h, (44, 84, 110))
    d.rectangle([0, 10, w, 13], fill=(150, 190, 205))
    for sx in range(4, w, 24):
        d.arc([sx, 2, sx + 14, 12], 180, 360, fill=(190, 220, 232), width=2)
    d.ellipse([22, 26, 172, 44], fill=(26, 30, 36))                   # hull
    d.polygon([(22, 35), (6, 28), (6, 42)], fill=(26, 30, 36))        # tail fin
    d.rectangle([86, 16, 108, 28], fill=(26, 30, 36))                 # sail
    d.line([97, 16, 97, 9], fill=(26, 30, 36), width=2)               # periscope
    for wx in (52, 74, 120, 142):
        d.ellipse([wx, 31, wx + 7, 36], fill=(190, 214, 226))
    return img


# ---------------------------------------------------------------- story data

TOP3 = [
    dict(num=1, region="EU", loc="ANTALYA, TURKEY · CLIMATE",
         headline="COP31 climate talks close in on a final deal",
         summary="A new package lands after a fight over fossil fuels; delegations "
                 "have until 03:00 GMT to object before a final plenary. (Reuters, BBC)",
         scene=scene_cop31),
    dict(num=2, region="EU", loc="KYIV, UKRAINE · WAR",
         headline="Russia fires 400 drones and 110 missiles",
         summary="One of the war's largest overnight attacks; at least seven "
                 "people are killed in Kyiv. (Al Jazeera)",
         scene=scene_ukraine),
    dict(num=3, region="ME", loc="MANAMA, BAHRAIN · IRAN WAR",
         headline="Iran strikes US bases in Bahrain",
         summary="An industrial site burns, no injuries; tankers are hit "
                 "in Hormuz. (Al Jazeera, CNA)",
         scene=scene_bahrain),
]

CARDS = [
    dict(num=4, region="EU", loc="GULF OF FINLAND", kicker="SHIP ABLAZE",
         headline="Russian cargo ship burns after drone strike",
         summary="Finland says Ukraine was likely behind it. (BBC)",
         scene=scene_ship),
    dict(num=5, region="EU", loc="KRYVYI RIH", kicker="2 DEAD, 60 HURT",
         headline="Strike hits Zelensky's home city",
         summary="Russian strike on the central Ukrainian city. (Officials)",
         scene=scene_kryvyi),
    dict(num=6, region="AF", loc="BAYELSA, NIGERIA", kicker="24 DEAD",
         headline="Boat carrying mourners capsizes",
         summary="Passengers were going to a funeral. (Emergency agency)",
         scene=scene_boat),
    dict(num=7, region="ME", loc="JERUSALEM", kicker="COALITION TALKS",
         headline="Eisenkot invites Likud to talks",
         summary="He seeks the broadest possible government. (Straits Times)",
         scene=scene_talks),
    dict(num=8, region="ME", loc="GAZA", kicker="3 KILLED",
         headline="Strike hits food aid vehicle",
         summary="Three Palestinians die in an air attack. (Al Jazeera, Reuters)",
         scene=scene_aid),
    dict(num=9, region="AM", loc="SINALOA, MEXICO", kicker="11 DEAD",
         headline="'El Chapo Isidro' caught; violence follows",
         summary="FBI top-ten fugitive held after a shoot-out. (Sky News, BBC)",
         scene=scene_fugitive),
    dict(num=10, region="ME", loc="TEHRAN, IRAN", kicker="POWER CUTS",
         headline="Iran to ration electricity",
         summary="War damage hits the energy network. (Straits Times)",
         scene=scene_power),
    dict(num=11, region="AM", loc="WASHINGTON", kicker="SEC PROBE",
         headline="Nvidia faces US accounting probe",
         summary="The SEC inquiry is at an early stage. (Media report)",
         scene=scene_probe),
    dict(num=12, region="AM", loc="BRASILIA, BRAZIL", kicker="BOLSONARO: ICU",
         headline="Bolsonaro in intensive care",
         summary="Ex-president stable, breathing on his own. (Al Jazeera, Reuters)",
         scene=scene_icu),
    dict(num=13, region="AP", loc="CANBERRA", kicker="AUKUS ROW",
         headline="Marles rejects US report on AUKUS subs",
         summary="He says the budget office is wrong. (ABC, Reuters)",
         scene=scene_aukus),
]

# (number, bold prefix, rest of line)
BRIEFS_LEFT = [
    (14, "US:", " FBI probes hack of its crime database (BBC)"),
    (15, "US:", " Teen gamer helps FBI rescue a girl (BBC)"),
    (16, "US:", " Midterm loss widens Vance's 2028 field (BBC)"),
    (17, "Saudi Arabia:", " Air defences down a missile (Investing.com)"),
    (18, "Lebanon:", " Aoun demands Israel pull out (Al Jazeera)"),
    (19, "Iran:", " Warns of a 'silent economic war' (Al Jazeera)"),
    (20, "Hormuz:", " Tanker struck in the strait (BBC)"),
    (21, "Moldova:", " Russian airspace breach (Kyiv Independent)"),
    (22, "Belgium:", " Air traffic halts, 23 Nov strike (ST)"),
    (23, "Germany:", " IG Metall widens strikes (Reuters)"),
    (24, "Portugal:", " Lisbon march on living costs (Reuters)"),
]
BRIEFS_RIGHT = [
    (25, "Denmark:", " Expels Russian attache (Guardian)"),
    (26, "Bangladesh:", " 30 Awami League offices torched (TOI)"),
    (27, "Australia:", " Ex-NSW MP Fred Nile dies, 92 (ABC)"),
    (28, "Australia:", " Driver pulled from burning car (ABC)"),
    (29, "Melbourne:", " 70 years since 1956 Olympics (ABC)"),
    (30, "Trade:", " EU-Indonesia deal after 10 years (DW)"),
    (31, "Rugby:", " England beat New Zealand 37-12 (Reuters)"),
    (32, "Rugby:", " France beat Argentina, reach final (Reuters)"),
    (33, "Football:", " Arsenal 2-2 Newcastle; Leeds win (BBC)"),
    (34, "Tennis:", " Zverev v Alcaraz, ATP final (TOI)"),
    (35, "Football:", " Liverpool host Man United (Al Jazeera)"),
]

PINS = [
    (1, 30.7, 36.9, "EU", 0, 0), (2, 30.5, 50.4, "EU", -6, -4),
    (3, 50.6, 26.2, "ME", 4, 6), (4, 25.0, 60.0, "EU", 0, -6),
    (5, 33.4, 47.9, "EU", 9, 3), (6, 6.0, 5.0, "AF", 0, 0),
    (7, 35.2, 31.8, "ME", 6, -7), (8, 34.3, 31.4, "ME", -8, 7),
    (9, -107.4, 24.8, "AM", 0, 0), (10, 51.4, 35.7, "ME", 10, -4),
    (11, -77.0, 38.9, "AM", 0, 0), (12, -47.9, -15.8, "AM", 0, 0),
    (13, 149.1, -35.3, "AP", 0, 0),
]

STATS = [
    ("~200", "nations at the COP31 talks"),
    ("03:00", "GMT deadline for objections"),
    ("400+", "drones fired at Ukraine"),
    ("110", "missiles in the same night"),
    ("7+", "people killed in Kyiv"),
    ("2", "US bases targeted in Bahrain"),
]

# ---------------------------------------------------------------- renderers

def draw_top_panel(page, x, y, w, story):
    d = ImageDraw.Draw(page)
    scene = story["scene"](w, 122)
    page.paste(scene, (x, y))
    ty = y + 128
    d.text((x, ty), str(story["num"]), font=F("sans_b", 12), fill=RED)
    d.text((x + 16, ty + 1), story["loc"], font=F("sans_b", 10), fill=RED)
    hy = draw_wrapped(d, (x, ty + 17), story["headline"], F("serif_b", 20),
                      INK, w, 24, max_lines=3)
    draw_wrapped(d, (x, hy + 2), story["summary"], F("sans", 10), (52, 50, 46),
                 w, 13, max_lines=3)


def draw_card(page, x, y, w, story):
    d = ImageDraw.Draw(page)
    scene = story["scene"](w, 54)
    sd = ImageDraw.Draw(scene)
    kicker_tag(sd, 4, 4, story["kicker"])
    num = str(story["num"])
    nf = F("sans_b", 10)
    nw = text_w(sd, num, nf) + 9
    sd.rectangle([w - nw - 3, 3, w - 3, 19], fill=(250, 248, 240))
    sd.text((w - nw + 1, 6), num, font=nf, fill=INK)
    page.paste(scene, (x, y))
    ty = y + 58
    d.text((x, ty), story["loc"], font=F("sans_b", 9), fill=RED)
    hy = draw_wrapped(d, (x, ty + 12), story["headline"], F("serif_b", 13),
                      INK, w, 15, max_lines=2)
    draw_wrapped(d, (x, hy + 1), story["summary"], F("sans", 9), (52, 50, 46),
                 w, 11.5, max_lines=2)


def draw_briefs(d, x, y, w, items):
    """Numbered brief list; number in red bold, place prefix bold."""
    nf = F("sans_b", 9)
    bf = F("sans_b", 9.5)
    rf = F("sans", 9.5)
    cy = y
    for num, prefix, rest in items:
        num_s = str(num)
        d.text((x, cy), num_s, font=nf, fill=RED)
        nx = x + text_w(d, num_s, nf) + 4
        full = prefix + rest
        # wrap across the bold prefix + regular rest as one string measured
        # with the regular font (close enough at this size), then draw the
        # first line in two segments.
        lines = wrap_lines(d, full, rf, w - (nx - x))
        if not lines:
            continue
        first = lines[0]
        cut = min(len(prefix), len(first))
        d.text((nx, cy), first[:cut], font=bf, fill=INK)
        seg_w = text_w(d, first[:cut], bf)
        d.text((nx + seg_w, cy), first[cut:], font=rf, fill=(52, 50, 46))
        cy += 12
        for extra in lines[1:]:
            d.text((nx, cy), extra, font=rf, fill=(52, 50, 46))
            cy += 12
        cy += 1.5
    return cy


# ---------------------------------------------------------------- page assembly

def build_page():
    page = Image.new("RGB", (PAGE_W, PAGE_H), CREAM)
    d = ImageDraw.Draw(page)

    # masthead band
    d.rectangle([0, 0, PAGE_W, 26], fill=NAVY)
    d.text((EDGE, 6), "THE WORLD IN ONE DAY", font=F("sans_b", 12),
           fill=(250, 248, 240))
    right = "35 STORIES · 6 REGIONS · EVERY ONE DATED SUNDAY 22 NOVEMBER 2026"
    rf = F("sans_b", 10)
    d.text((PAGE_W - EDGE - text_w(d, right, rf), 7), right, font=rf,
           fill=(232, 205, 120))

    # giant date + red sub-headline
    d.text((EDGE, 32), "Sunday 22 November 2026", font=F("serif_b", 63), fill=INK)
    d.text((EDGE, 104),
           "Climate deal in sight at COP31 · Russia's 400-drone barrage on "
           "Ukraine · Iran hits US bases in Bahrain",
           font=F("serif_i", 16), fill=RED)

    # stat strip
    d.line([EDGE, 128, PAGE_W - EDGE, 128], fill=RULE, width=1)
    col_w = INNER_W / 6
    for i, (big, label) in enumerate(STATS):
        cx = EDGE + i * col_w
        d.text((cx + 2, 133), big, font=F("serif_b", 34), fill=RED)
        draw_wrapped(d, (cx + 2, 174), label, F("sans", 9), (52, 50, 46),
                     col_w - 10, 11, max_lines=2)
        if i:
            d.line([cx, 134, cx, 192], fill=RULE, width=1)
    d.line([EDGE, 196, PAGE_W - EDGE, 196], fill=RULE, width=1)

    # regional count bar (widths proportional to story counts)
    counts = [("EU", 9), ("ME", 8), ("AM", 6), ("AP", 5), ("AF", 1), ("WO", 6)]
    bx = EDGE
    by = 200
    segments = []
    for key, n in counts:
        seg_w = INNER_W * n / 35.0
        d.rectangle([bx, by, bx + seg_w, by + 21], fill=REGION_COLOURS[key])
        segments.append((bx, seg_w, "%s %d" % (REGION_NAMES[key], n)))
        bx += seg_w
    lf = F("sans_b", 10)
    for sx, seg_w, label in segments:
        if text_w(d, label, lf) < seg_w - 6:
            d.text((sx + (seg_w - text_w(d, label, lf)) / 2, by + 5), label,
                   font=lf, fill=(255, 255, 255))
        else:
            # too narrow to centre (Africa): run the label across the seam,
            # drawn last so no later segment paints over it
            d.text((sx + 2, by + 5), label, font=lf, fill=(255, 255, 255))

    # weather strip
    wy = 225
    d.rectangle([EDGE, wy, PAGE_W - EDGE, wy + 30], fill=PAPER,
                outline=RULE, width=1)
    d.text((EDGE + 8, wy + 4), "SUNDAY WEATHER", font=F("sans_b", 10), fill=RED)
    d.text((EDGE + 8, wy + 16), "Forecast, high/low", font=F("sans", 8), fill=GREY)
    wx = EDGE + 118
    cell = (INNER_W - 118) / len(WEATHER)
    for i, (city, icon, temps) in enumerate(WEATHER):
        cx = wx + i * cell
        WEATHER_ICONS[icon](d, int(cx + 2), wy + 6, 18)
        d.text((cx + 24, wy + 4), city, font=F("sans_b", 9), fill=INK)
        d.text((cx + 24, wy + 16), temps + " C", font=F("sans", 9),
               fill=(52, 50, 46))

    # top three stories
    gap = 8
    pw = (INNER_W - 2 * gap) / 3
    for i, story in enumerate(TOP3):
        draw_top_panel(page, int(EDGE + i * (pw + gap)), 262, int(pw), story)

    # cards 4-13, five across, two rows
    cgap = 6
    cw = (INNER_W - 4 * cgap) / 5
    for i, story in enumerate(CARDS):
        row, col = divmod(i, 5)
        draw_card(page, int(EDGE + col * (cw + cgap)), 516 + row * 128,
                  int(cw), story)

    # bottom section: map left, briefs right
    d.line([EDGE, 770, PAGE_W - EDGE, 770], fill=RULE, width=1)
    d.text((EDGE, 776), "WHERE IT HAPPENED", font=F("sans_b", 11), fill=INK)
    d.text((EDGE + 148, 778), "pins match story numbers", font=F("sans_o", 9),
           fill=GREY)
    draw_map(d, EDGE, 796, 336, 140, PINS)
    bx = 372
    d.text((bx, 776), "ALSO ON SUNDAY 22 NOVEMBER — 22 MORE STORIES",
           font=F("sans_b", 11), fill=INK)
    draw_briefs(d, bx, 796, 300, BRIEFS_LEFT)
    draw_briefs(d, bx + 322, 796, 300, BRIEFS_RIGHT)

    # date check box
    d.rectangle([EDGE, 950, PAGE_W - EDGE, 992], outline=RED, width=2)
    d.text((EDGE + 8, 956), "DATE CHECK", font=F("sans_b", 10), fill=RED)
    check = ("Wires read up to 07:30 UTC, Sunday 22 November 2026; every story was reported "
             "or still developing on 22 November in at least one time zone. Left out as other "
             "days' news: Peru earthquake (20 Nov), Poland missiles (19 Nov), Kerch Bridge "
             "strikes, Shenzhen summit (19 Nov).")
    draw_wrapped(d, (EDGE + 8, 970), check, F("sans", 9), (52, 50, 46),
                 INNER_W - 16, 11, max_lines=2)

    # footer
    d.text((EDGE, 997),
           "Sources: Reuters, BBC, Al Jazeera, DW, The Straits Times, Sky News, CNA, ABC "
           "Australia, Times of India, The Guardian, Kyiv Independent. Every story names its "
           "outlet. Pictures and map: original, drawn in code.",
           font=F("sans", 8), fill=GREY)
    d.text((EDGE, 1012), "THE WORLD IN ONE DAY", font=F("sans_b", 8), fill=INK)
    tail = "SUNDAY 22 NOVEMBER 2026 · ONE PAGE"
    tf = F("sans_b", 8)
    d.text((PAGE_W - EDGE - text_w(d, tail, tf), 1012), tail, font=tf, fill=INK)
    return page


def main():
    page = build_page()
    page.save("entry.png", optimize=True)
    print("wrote entry.png", page.size)


if __name__ == "__main__":
    main()
