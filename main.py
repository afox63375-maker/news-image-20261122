#!/usr/bin/env python3
"""Sunday 22 November 2026 — one page of world news.

Renders the whole front page with Pillow: header, three illustrated
lead stories, a story grid, a dotted world map with numbered pins,
a brief list, a date-check footer and a weather panel. No network,
no clock, no randomness: the same run always writes the same bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 232)
INK = (24, 24, 22)
NAVY = (12, 32, 66)
RED = (178, 34, 34)
GOLD = (176, 132, 20)
RULE = (120, 110, 95)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SERIF_R = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

# category -> (label, colour)
CATS = {
    "war": ("war & security", (198, 40, 40)),
    "pol": ("politics & diplomacy", (42, 92, 168)),
    "eco": ("economy & business", (176, 132, 20)),
    "hea": ("health & weather", (24, 140, 130)),
    "sci": ("science & culture", (74, 148, 60)),
    "crt": ("courts & world", (128, 64, 160)),
}

# (n, city, tag, region, cat, headline, deck, lat, lon)
STORIES = [
    (1, "WARSAW", "NATO'S FRONTIER", "EU", "war",
     "Rutte: NATO will defend every inch of Poland",
     "Secretary general in Warsaw a day after Russian missiles landed on Polish soil.",
     52.2, 21.0),
    (2, "ANTALYA", "CLIMATE", "EU", "pol",
     "COP31 in overtime, no deal in sight",
     "Final draft due Sunday; text admits the 1.5\u00b0C goal has been missed.",
     36.9, 30.7),
    (3, "NEW YORK", "MARKETS", "AMER", "eco",
     "Nasdaq erases all of its 2026 gains",
     "Anthropic slides 8.5% to $88.91; Nvidia falls 14% on SEC inquiry report.",
     40.7, -74.0),
    (4, "COPENHAGEN", "SECURITY", "EU", "war",
     "Denmark expels Russian attach\u00e9 over 'assassination plot'",
     "PET says Moscow planned to kill rapper Kyivstoner; EU visa curbs proposed.",
     55.7, 12.6),
    (5, "TALLINN", "BORDER", "EU", "pol",
     "Estonia to shut its border with Russia",
     "All road crossings close from 1 December after GRU-linked arson attempt.",
     59.4, 24.7),
    (6, "LIMA", "QUAKE", "AMER", "hea",
     "Magnitude 6.9 quake shakes Peru's Andes",
     "Tremor felt in Lima; houses damaged, no casualties reported.",
     -12.0, -77.0),
    (7, "MELBOURNE", "CRICKET", "APAC", "sci",
     "Australia edge England in T20 thriller",
     "Chaudhary's 66 seals a 3-wicket win with one ball to spare.",
     -37.8, 145.0),
    (8, "KATHMANDU", "DIPLOMACY", "APAC", "pol",
     "Nepal's PM starts first India visit",
     "Shah flies to Delhi today; talks with Modi Monday.",
     27.7, 85.3),
    (9, "JOHANNESBURG", "POLITICS", "AFR", "pol",
     "ANC scrambles for deals after worst-ever result",
     "Ruling party takes 31% in local polls; DA leads in Johannesburg.",
     -26.2, 28.0),
    (10, "WELLINGTON", "CRICKET", "APAC", "sci",
     "India tighten grip on first Test",
     "India lead New Zealand by 261; Gill falls short of a hundred.",
     -41.3, 174.8),
]

# briefs: (n, city, text, lat, lon, region, cat)
BRIEFS = [
    (11, "KYIV", "Zelensky calls Putin a \u201ckiller\u201d", 50.4, 30.5, "EU", "war"),
    (12, "BRUSSELS", "NATO council meets Monday on Poland", 50.8, 4.4, "EU", "pol"),
    (13, "WASHINGTON", "FBI probes hack of criminal database", 38.9, -77.0, "AMER", "pol"),
    (14, "LONDON", "Blair: rejoin EU only if UK innovates", 51.5, -0.1, "EU", "pol"),
    (15, "PARIS", "France fights to restore fossil-fuel text", 48.9, 2.3, "EU", "pol"),
    (16, "SHENZHEN", "Peace text silent on Ukraine", 22.5, 114.1, "APAC", "pol"),
    (17, "MOSCOW", "Kremlin calls closure \u201cIron Curtain\u201d", 55.8, 37.6, "EU", "war"),
    (18, "DOHA", "Gulf states race to avert all-out war", 25.3, 51.5, "ME", "pol"),
    (19, "GAZA", "Strike on Gaza hospital kills six", 31.5, 34.5, "ME", "war"),
    (20, "NEW YORK", "Mamdani: close Rikers Island by 2032", 40.7, -74.0, "AMER", "pol"),
    (21, "WASHINGTON", "Trump vows data-centre tariffs", 38.9, -77.0, "AMER", "eco"),
    (22, "NEW YORK", "Judge OKs $7.25bn Roundup deal", 40.7, -74.0, "AMER", "crt"),
    (23, "WASHINGTON", "US declassifies more UFO footage", 38.9, -77.0, "AMER", "sci"),
    (24, "PATNA", "Modi opens Nitish Setu bridge", 25.6, 85.1, "APAC", "pol"),
    (25, "PRETORIA", "Mass shootings kill 17 on Sunday", -25.7, 28.2, "AFR", "war"),
    (26, "MEXICO CITY", "Army captures \u201cEl Chapo Isidro\u201d", 19.4, -99.1, "AMER", "war"),
    (27, "LONDON", "Catherine\u2019s cancer journey on film", 51.5, -0.1, "EU", "sci"),
    (28, "LONDON", "William backs cover for forest workers", 51.5, -0.1, "EU", "pol"),
    (29, "PARIS", "France reach Nations final v Springboks", 48.9, 2.3, "EU", "sci"),
    (30, "DHAKA", "Violence flares ahead of Hasina return", 23.8, 90.4, "APAC", "war"),
    (31, "TOKYO", "Japan to train live-fire in India", 35.7, 139.7, "APAC", "war"),
    (32, "MUMBAI", "Sensex falls, ends two-day rally", 19.1, 72.9, "APAC", "eco"),
    (33, "WASHINGTON", "Pentagon limits US-Canada contact", 38.9, -77.0, "AMER", "pol"),
    (34, "KHARTOUM", "Sudan: ICC-wanted ex-official held", 15.6, 32.5, "AFR", "crt"),
    (35, "KYIV", "Ukraine downed 79 of 84 cruise missiles", 50.4, 30.5, "EU", "war"),
    (36, "NEW YORK", "VIX jumps 86% in a week to 35.89", 40.7, -74.0, "AMER", "eco"),
    (37, "COPENHAGEN", "Von der Leyen warns on Russia", 55.7, 12.6, "EU", "war"),
    (38, "GLOBAL", "AI proof claims Navier\u2013Stokes blow-up", 0.0, -30.0, "GLOB", "sci"),
    (39, "NEW YORK", "Waymo pulls taxis from US freeways", 40.7, -74.0, "AMER", "sci"),
]

FORECAST = [
    ("WARSAW", "Cold, cloudy, 4\u00b0"),
    ("ANTALYA", "Showers, mild, 19\u00b0"),
    ("NEW YORK", "Partly cloudy, 17\u00b0"),
    ("BERHAMPUR", "Warm, 29\u00b0"),
]

REGIONS = [
    ("ASIA-PACIFIC", (42, 92, 168)),
    ("EUROPE", (110, 130, 40)),
    ("AMERICAS", (178, 60, 60)),
    ("MID EAST", (176, 132, 20)),
    ("AFRICA", (74, 148, 60)),
    ("GLOBAL", (40, 40, 40)),
]
REGION_KEY = {"APAC": 0, "EU": 1, "AMER": 2, "ME": 3, "AFR": 4, "GLOB": 5}


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines that fit width."""
    lines, cur = [], ""
    for word in text.split(" "):
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=fnt) <= width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, x, y, lines, fnt, fill=INK, leading=None):
    if leading is None:
        leading = fnt.size + 3
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def number_badge(draw, x, y, n, colour, d=22):
    draw.ellipse([x, y, x + d, y + d], fill=colour, outline=(255, 255, 255), width=1)
    s = str(n)
    f = font(SANS_B, 12 if len(s) < 2 else 11)
    tw = draw.textlength(s, font=f)
    draw.text((x + (d - tw) / 2, y + (d - 13) / 2 + 1), s, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------- land map
# Rough continent outlines in (lon, lat); the dotted map is drawn from these.
LAND = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80), (-85, 73), (-75, 72),
     (-65, 60), (-55, 52), (-60, 45), (-70, 42), (-75, 35), (-80, 32), (-85, 30),
     (-90, 21), (-95, 19), (-97, 16), (-105, 20), (-110, 23), (-115, 30), (-125, 40),
     (-125, 48), (-135, 58), (-155, 58), (-165, 60)],
    [(-58, 64), (-45, 60), (-30, 68), (-22, 70), (-30, 76), (-55, 78), (-60, 74)],
    [(-80, 10), (-75, 11), (-62, 10), (-52, 5), (-50, 0), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-58, -38), (-65, -45), (-70, -54), (-73, -50),
     (-73, -37), (-70, -20), (-77, -12), (-80, -5)],
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53), (8, 57), (10, 59),
     (5, 60), (12, 62), (18, 69), (25, 71), (30, 70), (40, 68), (45, 66), (40, 60),
     (35, 55), (30, 50), (28, 45), (23, 40), (19, 42), (12, 44), (8, 44), (3, 43),
     (0, 39), (-2, 37), (-6, 36)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (37, 22),
     (43, 12), (48, 11), (51, 10), (44, 0), (40, -10), (35, -18), (32, -26),
     (28, -33), (20, -35), (15, -30), (12, -18), (9, -1), (9, 4), (-8, 5),
     (-13, 8), (-17, 12)],
    [(40, 68), (50, 70), (60, 70), (70, 72), (80, 73), (90, 75), (100, 77), (110, 76),
     (120, 73), (130, 72), (140, 72), (150, 70), (160, 66), (170, 66), (178, 65),
     (170, 60), (162, 56), (158, 52), (150, 59), (142, 55), (140, 45), (135, 43),
     (130, 42), (127, 40), (122, 38), (120, 32), (122, 28), (115, 23), (109, 20),
     (105, 10), (100, 8), (98, 12), (95, 16), (92, 21), (88, 22), (85, 19),
     (80, 15), (77, 8), (75, 12), (72, 20), (68, 22), (62, 25), (57, 26), (52, 27),
     (48, 29), (44, 29), (40, 31), (38, 36), (35, 36), (30, 36), (27, 40), (23, 40),
     (26, 45), (30, 50), (35, 55), (40, 60)],
    [(113, -22), (114, -30), (115, -35), (120, -34), (125, -32), (130, -32),
     (135, -35), (140, -38), (145, -38), (150, -37), (153, -32), (153, -27),
     (150, -22), (146, -19), (142, -15), (142, -11), (137, -12), (135, -15),
     (132, -12), (130, -13), (126, -14), (122, -17), (118, -20)],
    [(18, -34), (20, -35), (20, -30), (19, -28), (17, -32)],  # Madagascar stub
    [(129, 31), (132, 33), (135, 34), (139, 35), (141, 39), (141, 44), (140, 45),
     (137, 42), (132, 38), (130, 33)],  # Japan
    [(95, 5), (98, 6), (101, 2), (104, -2), (106, -6), (110, -7), (114, -8),
     (119, -9), (120, -5), (117, -1), (113, 1), (108, 3), (103, 5), (99, 7)],  # Indonesia
    [(167, -45), (170, -43), (174, -41), (178, -38), (175, -36), (172, -35),
     (168, -44)],  # New Zealand
]


def inside_poly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat):
            xint = (xj - xi) * (lat - yi) / (yj - yi) + xi
            if lon < xint:
                inside = not inside
        j = i
    return inside


def on_land(lon, lat):
    return any(inside_poly(lon, lat, poly) for poly in LAND)


def project(lon, lat, box):
    x0, y0, x1, y1 = box
    x = x0 + (lon + 180.0) / 360.0 * (x1 - x0)
    y = y0 + (84.0 - lat) / 144.0 * (y1 - y0)
    return x, y


# ---------------------------------------------------------------- illustrations
def paint_jets(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(58, 74, 92))
    draw.rectangle([x0, y0, x1, y0 + 26], fill=(40, 54, 72))
    for cx, cy, r in [(x0 + 40, y0 + 60, 26), (x0 + 150, y0 + 44, 32), (x0 + 260, y0 + 70, 24)]:
        draw.ellipse([cx - r, cy - r // 2, cx + r, cy + r // 2], fill=(120, 135, 155))
    # ground + wreckage glow, kept low so the jets read against the sky
    draw.rectangle([x0, y1 - 22, x1, y1], fill=(52, 48, 42))
    draw.ellipse([x0 + 110, y1 - 34, x0 + 210, y1 - 8], fill=(198, 90, 40))
    draw.ellipse([x0 + 125, y1 - 28, x0 + 195, y1 - 12], fill=(232, 160, 60))
    # two fighter silhouettes
    for jx, jy, s in [(x0 + 70, y0 + 78, 1.0), (x0 + 190, y0 + 56, 0.8)]:
        w = int(64 * s)
        draw.polygon([(jx, jy), (jx + w, jy + 6), (jx + w - 14, jy + 12),
                      (jx + 10, jy + 12), (jx + 22, jy + 22), (jx + 16, jy + 8)],
                     fill=(18, 20, 24))
        draw.line([(jx - 30, jy + 16), (jx, jy + 10)], fill=(220, 220, 220), width=2)
    draw.text((x0 + 8, y0 + 6), "POLISH BORDER \u2022 FRIDAY NIGHT",
              font=font(SANS_B, 10), fill=(255, 240, 210))


def paint_hall(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(66, 52, 38))
    # arched windows
    for i in range(4):
        wx = x0 + 18 + i * 76
        draw.rectangle([wx, y0 + 14, wx + 56, y0 + 78], fill=(214, 196, 160))
        draw.pieslice([wx, y0 + 2, wx + 56, y0 + 34], 180, 360, fill=(214, 196, 160))
        draw.line([wx + 28, y0 + 14, wx + 28, y0 + 78], fill=(120, 100, 70), width=2)
    # delegates, two rows so the panel bottom stays clean
    for r in range(2):
        for c in range(9):
            dx = x0 + 26 + c * 33
            dy = y0 + 92 + r * 16
            draw.ellipse([dx, dy, dx + 9, dy + 9], fill=(30, 26, 22))
            draw.rectangle([dx - 2, dy + 9, dx + 11, dy + 15], fill=(90, 80, 64))
    # 1.5C badge, bottom right, clear of the delegates
    draw.rounded_rectangle([x1 - 92, y1 - 30, x1 - 10, y1 - 8], radius=4,
                           fill=(232, 120, 60))
    draw.text((x1 - 84, y1 - 27), "1.5\u00b0C MISSED", font=font(SANS_B, 11), fill=(255, 255, 255))
    draw.rectangle([x0, y0, x1, y0 + 18], fill=(48, 38, 28))
    draw.text((x0 + 8, y0 + 3), "ANTALYA \u2022 THE FINAL DRAFT",
              font=font(SANS_B, 10), fill=(255, 240, 210))


def paint_chart(draw, box):
    x0, y0, x1, y1 = box
    draw.rectangle(box, fill=(96, 22, 22))
    # falling market line
    pts = []
    for i in range(9):
        px = x0 + 14 + i * 36
        py = y0 + 18 + i * 13 + (0 if i % 2 else 5)
        pts.append((px, py))
    draw.line(pts, fill=(255, 214, 90), width=4)
    for px, py in pts:
        draw.ellipse([px - 4, py - 4, px + 4, py + 4], fill=(255, 255, 255))
    draw.line([(x0 + 14, y1 - 40), (x1 - 14, y1 - 40)], fill=(200, 160, 140), width=2)
    # traders, heads down
    for tx in (x0 + 40, x0 + 130, x0 + 220, x0 + 280):
        draw.ellipse([tx, y1 - 34, tx + 16, y1 - 18], fill=(30, 16, 14))
        draw.polygon([(tx - 6, y1), (tx + 22, y1), (tx + 18, y1 - 18), (tx - 2, y1 - 18)],
                     fill=(52, 32, 28))
    draw.text((x0 + 8, y0 + 4), "NASDAQ \u22125.3% \u2022 FRIDAY",
              font=font(SANS_B, 10), fill=(255, 230, 200))


def paint_quake(draw, box):
    x0, y0, x1, y1 = box
    h = y1 - y0
    ground = y0 + int(h * 0.68)
    draw.rectangle(box, fill=(168, 148, 116))
    # distant hills
    draw.polygon([(x0, ground - 22), (x0 + 90, ground - 54), (x0 + 180, ground - 26),
                  (x0 + 240, ground - 50), (x1, ground - 24), (x1, ground), (x0, ground)],
                 fill=(140, 120, 92))
    # ground band with a jagged crack running through it
    draw.rectangle([x0, ground, x1, y1], fill=(110, 92, 68))
    crack = [(x0 + 150, ground), (x0 + 138, ground + 6), (x0 + 158, ground + 12),
             (x0 + 142, ground + 18), (x0 + 160, y1)]
    draw.line(crack, fill=(40, 32, 22), width=3)
    # two houses standing on the ground line, one tilted by the shock
    for hx, hy, tilt in [(x0 + 34, ground - 26, 0), (x0 + 208, ground - 28, 8)]:
        draw.polygon([(hx, hy), (hx + 56, hy + tilt), (hx + 56, hy + 30 + tilt),
                      (hx, hy + 30)], fill=(214, 198, 172))
        draw.polygon([(hx - 5, hy), (hx + 28, hy - 18), (hx + 61, hy + tilt)],
                     fill=(150, 60, 44))
        draw.rectangle([hx + 22, hy + 14, hx + 32, hy + 30], fill=(90, 70, 52))
    draw.text((x0 + 8, y1 - 16), "JUN\u00cdN \u2022 6.9 MAGNITUDE",
              font=font(SANS_B, 10), fill=(255, 244, 220))


# ---------------------------------------------------------------- page
def build_page():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # header band
    d.rectangle([0, 0, W, 26], fill=NAVY)
    d.text((24, 4), "THE WORLD IN ONE DAY", font=font(SANS_B, 13), fill=(255, 255, 255))
    right = "ONE PAGE \u2022 EVERY STORY FROM THE DAY"
    d.text((W - 24 - d.textlength(right, font=font(SANS_B, 13)), 4), right,
           font=font(SANS_B, 13), fill=(255, 214, 130))

    # title + forecast box
    d.text((24, 34), "Sunday 22 November 2026", font=font(SERIF, 44), fill=INK)
    fx0, fy0, fx1 = 776, 32, 1000
    d.rectangle([fx0, fy0, fx1, 104], outline=(42, 92, 168), width=2)
    d.rectangle([fx0, fy0, fx1, fy0 + 18], fill=(42, 92, 168))
    d.text((fx0 + 8, fy0 + 2), "SUNDAY'S FORECAST", font=font(SANS_B, 11), fill=(255, 255, 255))
    fy = fy0 + 20
    for city, cond in FORECAST:
        d.text((fx0 + 8, fy), city, font=font(SANS_B, 10), fill=INK)
        d.text((fx0 + 86, fy), "\u2014 " + cond, font=font(SANS, 10), fill=(60, 60, 60))
        fy += 13

    # red subhead: the three leads
    d.text((24, 86), "Rutte: NATO will defend every inch of Poland \u2022 COP31 in overtime \u2022 Nasdaq erases its 2026 gains",
           font=font(SERIF_R, 15), fill=RED)

    # region strip: counts share the bar; the black box on the right holds the total
    counts = [0] * 6
    for s in STORIES:
        counts[REGION_KEY[s[3]]] += 1
    for b in BRIEFS:
        counts[REGION_KEY[b[5]]] += 1
    bar_w = 976 - 96
    x = 24
    for i, (name, colour) in enumerate(REGIONS):
        seg = int(bar_w * counts[i] / 39)
        if i == 5:
            seg = 24 + bar_w - x
        d.rectangle([x, 106, x + seg - 2, 130], fill=colour)
        label = "%s %d" % (name, counts[i])
        f = font(SANS_B, 10)
        if d.textlength(label, font=f) <= seg - 6:
            tw = d.textlength(label, font=f)
            d.text((x + (seg - 2 - tw) / 2, 112), label, font=f, fill=(255, 255, 255))
        else:
            num = str(counts[i])
            tw = d.textlength(num, font=f)
            d.text((x + (seg - 2 - tw) / 2, 112), num, font=f, fill=(255, 255, 255))
        x += seg
    d.rectangle([24 + bar_w, 106, 1000, 130], fill=(24, 24, 22))
    d.text((24 + bar_w + 8, 111), "39 STORIES", font=font(SANS_B, 11), fill=(255, 214, 130))

    # ---- top three, illustrated
    cols = [(24, 320), (352, 320), (680, 320)]
    painters = [paint_jets, paint_hall, paint_chart]
    for (sx, sw), story, painter in zip(cols, STORIES[:3], painters):
        n, city, tag, _reg, cat, head, deck, _la, _lo = story
        colour = CATS[cat][1]
        painter(d, (sx, 134, sx + sw, 250))
        d.rectangle([sx, 250, sx + sw, 254], fill=colour)
        number_badge(d, sx, 260, n, colour, d=22)
        d.text((sx + 28, 262), "%s \u2014 %s" % (city, tag), font=font(SANS_B, 11), fill=colour)
        y = 286
        y = text_block(d, sx, y, wrap(d, head, font(SERIF, 23), sw), font(SERIF, 23), leading=26)
        text_block(d, sx, y + 2, wrap(d, deck, font(SANS, 12), sw), font(SANS, 12), leading=15)

    # ---- grid row 4-7
    gx = [24, 268, 512, 756]
    gw = [236, 236, 236, 244]
    d.line([24, 390, 1000, 390], fill=RULE, width=1)
    for i, story in enumerate(STORIES[3:7]):
        n, city, tag, _reg, cat, head, deck, _la, _lo = story
        colour = CATS[cat][1]
        sx, sw = gx[i], gw[i]
        d.rectangle([sx, 398, sx + sw, 402], fill=colour)
        number_badge(d, sx, 408, n, colour, d=20)
        d.text((sx + 26, 410), "%s \u2022 %s" % (city, tag), font=font(SANS_B, 10), fill=colour)
        y = text_block(d, sx, 434, wrap(d, head, font(SERIF, 18), sw), font(SERIF, 18), leading=21)
        text_block(d, sx, y + 2, wrap(d, deck, font(SANS, 11), sw), font(SANS, 11), leading=14)

    # ---- row 8-10
    d.line([24, 530, 1000, 530], fill=RULE, width=1)
    story = STORIES[7]
    n, city, tag, _reg, cat, head, deck, _la, _lo = story
    colour = CATS[cat][1]
    paint_quake(d, (24, 538, 330, 616))
    d.rectangle([24, 616, 330, 620], fill=colour)
    number_badge(d, 24, 626, n, colour, d=20)
    d.text((50, 628), "%s \u2022 %s" % (city, tag), font=font(SANS_B, 10), fill=colour)
    y = text_block(d, 24, 650, wrap(d, head, font(SERIF, 16), 306), font(SERIF, 16), leading=19)
    text_block(d, 24, y + 2, wrap(d, deck, font(SANS, 11), 306), font(SANS, 11), leading=14)
    for sx, sw, story in [(338, 320, STORIES[8]), (666, 334, STORIES[9])]:
        n, city, tag, _reg, cat, head, deck, _la, _lo = story
        colour = CATS[cat][1]
        d.rectangle([sx, 538, sx + sw, 542], fill=colour)
        number_badge(d, sx, 548, n, colour, d=20)
        d.text((sx + 26, 550), "%s \u2022 %s" % (city, tag), font=font(SANS_B, 10), fill=colour)
        y = text_block(d, sx, 574, wrap(d, head, font(SERIF, 19), sw), font(SERIF, 19), leading=22)
        text_block(d, sx, y + 2, wrap(d, deck, font(SANS, 12), sw), font(SANS, 12), leading=15)

    # ---- map + briefs
    d.line([24, 700, 1000, 700], fill=RULE, width=1)
    d.rectangle([24, 708, 330, 950], fill=NAVY)
    d.text((36, 716), "WHERE IT HAPPENED", font=font(SANS_B, 13), fill=(255, 255, 255))
    mbox = (36, 742, 318, 892)
    step_lon, step_lat = 4.0, 4.0
    lon = -180.0
    while lon < 180.0:
        lat = -56.0
        while lat < 84.0:
            if on_land(lon + step_lon / 2, lat + step_lat / 2):
                px, py = project(lon + step_lon / 2, lat + step_lat / 2, mbox)
                d.ellipse([px - 1, py - 1, px + 1, py + 1], fill=(150, 170, 200))
            lat += step_lat
        lon += step_lon
    all_pins = [(s[0], s[7], s[8], CATS[s[4]][1]) for s in STORIES]
    all_pins += [(b[0], b[3], b[4], CATS[b[6]][1]) for b in BRIEFS]
    for n, la, lo, colour in all_pins:
        px, py = project(lo, la, mbox)
        jx = ((n * 7) % 5 - 2) * 2
        jy = ((n * 11) % 5 - 2) * 2
        d.ellipse([px + jx - 7, py + jy - 7, px + jx + 7, py + jy + 7],
                  fill=colour, outline=(255, 255, 255), width=1)
        s = str(n)
        f = font(SANS_B, 8 if len(s) < 2 else 7)
        tw = d.textlength(s, font=f)
        d.text((px + jx - tw / 2, py + jy - 5), s, font=f, fill=(255, 255, 255))
    d.text((36, 898), "Numbered markers match the stories, coloured by kind.",
           font=font(SANS, 10), fill=(200, 210, 225))
    d.text((36, 912), "38 \u00b7 GLOBAL is a worldwide story with no single home.",
           font=font(SANS, 10), fill=(200, 210, 225))
    # category legend, two rows of three
    for i, (label, colour) in enumerate(CATS.values()):
        lx = 36 + (i % 3) * 96
        ly = 928 + (i // 3) * 11
        d.ellipse([lx, ly, lx + 8, ly + 8], fill=colour)
        d.text((lx + 11, ly - 2), label, font=font(SANS, 8), fill=(220, 225, 235))

    # briefs, two columns
    d.text((344, 708), "ALSO ON SUNDAY 22 NOVEMBER", font=font(SANS_B, 13), fill=INK)
    bx = [344, 674]
    bw = 322
    half = 15
    for ci in range(2):
        col = BRIEFS[ci * half:(ci + 1) * half]
        y = 730
        for n, city, text, _la, _lo, _reg, cat in col:
            colour = CATS[cat][1]
            d.text((bx[ci], y), str(n), font=font(SANS_B, 11), fill=colour)
            d.text((bx[ci] + 22, y), city, font=font(SANS_B, 11), fill=INK)
            d.text((bx[ci] + 22 + d.textlength(city + " ", font=font(SANS_B, 11)), y),
                   "\u2014", font=font(SANS, 11), fill=(100, 100, 100))
            tx = bx[ci] + 22 + d.textlength(city + " \u2014 ", font=font(SANS_B, 11))
            lines = wrap(d, text, font(SANS, 11), bx[ci] + bw - tx)
            yy = y
            for ln in lines[:2]:
                d.text((tx, yy), ln, font=font(SANS, 11), fill=(50, 50, 50))
                yy += 13
            y += 27 if len(lines) > 1 else 14

    # ---- footer
    d.line([24, 956, 1000, 956], fill=INK, width=2)
    foot = ("DATE CHECK \u2014 Friday brought the missiles over Poland, the Peru quake and the Wall Street rout; "
            "Saturday brought Rutte\u2019s pledge and the COP31 deadlock. "
            "Everything else here happened, or was first reported, on Sunday 22 November 2026.")
    text_block(d, 24, 962, wrap(d, foot, font(SANS, 11), 976), font(SANS, 11), leading=14)
    d.text((24, 994), "Sources: Reuters \u00b7 AP \u00b7 BBC \u00b7 CNN \u00b7 The Times \u00b7 Kyiv Independent \u00b7 Cricbuzz \u00b7 IMD \u00b7 weather.com \u2014 Original illustrations",
           font=font(SANS, 10), fill=(90, 85, 75))
    return img


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(outdir, exist_ok=True)
    page = build_page()
    path = os.path.join(outdir, "entry.png")
    page.save(path, format="PNG", optimize=True)
    print("wrote", path, page.size, os.path.getsize(path), "bytes")


if __name__ == "__main__":
    main()
