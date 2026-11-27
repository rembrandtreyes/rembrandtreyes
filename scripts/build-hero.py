#!/usr/bin/env python3
"""Render the profile hero: assets/hero-light.svg and assets/hero-dark.svg.

Sedona at sundown. The Mogollon Rim and a line of far mesas sit in the haze.
Courthouse Butte, Cathedral Rock and Bell Rock stand in banded red sandstone,
side-lit by a sun setting in the west. Juniper flats, small saguaros and Oak
Creek run along the front, framed by dark ledges planted with saguaro,
ocotillo and cholla. A hawk circles overhead, the ocotillo sways, and the rocks
redden as the sun sinks. Light and dark share one drawing and differ only in
palette. Randomness is seeded, so reruns produce identical files.

    python3 scripts/build-hero.py
"""

from __future__ import annotations

import math
import random
from pathlib import Path

W, H = 1200, 400
SUN = (700, 272)  # resting position of the sun's center
LIGHT = (-1.0, -0.18)  # direction from the rocks toward the sun
BASE = 345  # where the rock formations meet the valley floor
CREEK = (380, 1020)  # Oak Creek's visible span

ROOT = Path(__file__).resolve().parent.parent

THEMES = {
    "light": {
        "sky": [(0, "#edeff3"), (0.36, "#f8f0e6"), (0.6, "#f8dbbf"), (0.75, "#f2b68c")],
        "glow": "#ffc48a", "glow_op": 0.8,
        "scrim": "#fbf5ee", "scrim_op": 0.55,
        "sun_core": "#fff6e6", "sun_edge": "#f9a862", "halo": "#ffcf98", "halo_op": 0.75,
        "rays_op": 0.14, "stars": False,
        "cloud_top": "#e6d3cf", "cloud_lit": "#f4a27e", "cloud_op": 0.85,
        "rim": "#ebbda2", "mid": "#e6ae8f", "range": "#df9f80",
        "butte": ["#d48461", "#c97553", "#d98f6c", "#c26c4b"], "cap": "#f0d3b2",
        "rock": ["#d8673a", "#c95a32", "#e07a4a", "#c04f2c", "#d26238", "#b9492a"], "spire": "#e8a273",
        "warm": "#ffd9a8", "warm_op": 0.3, "talus": "#8c4a2a",
        "shade": "#86301b", "shade_op": 0.5,
        "rimlight": "#ffd7a3", "rim_w": 3.2,
        "haze": "#f5c4a0", "haze_op": 0.6,
        "floor_top": "#ad5d38", "floor_bot": "#7b3a22", "soil": ("#c6744c", "#8a4026"),
        "tree_far": "#7d7650", "tree": "#5f5c3a", "tree_near": "#3f3f29", "tree_lit": "#a8a06a",
        "cast": "#4a1d10", "cast_op": 0.3,
        "creek_lo": "#eeae86", "creek_hi": "#fff3de", "bank": "#5a2a18",
        "near": "#4a2a1c", "near_top": "#6b3b24", "near_lit": "#d08452", "near_tree": "#262818",
        "cactus": "#2f3320", "spine": "#ffe2b0", "bloom": "#d63f24",
        "alpen": "#ff5a2c", "alpen_op": 0.2, "hawk": "#4a2c1e",
        "fg": "#24180f", "muted": "#74574a", "accent": "#c2502a", "border": "#ead9c6",
    },
    "dark": {
        "sky": [(0, "#09090f"), (0.34, "#141227"), (0.55, "#2b1833"), (0.67, "#5c2430"), (0.75, "#a7452a")],
        "glow": "#f2743a", "glow_op": 0.55,
        "scrim": "#0b0a10", "scrim_op": 0.5,
        "sun_core": "#ffdcb0", "sun_edge": "#f27a3c", "halo": "#f58a4c", "halo_op": 0.5,
        "rays_op": 0.08, "stars": True,
        "cloud_top": "#2d1a33", "cloud_lit": "#d6633a", "cloud_op": 0.75,
        "rim": "#4f2333", "mid": "#3b1a27", "range": "#3e1a24",
        "butte": ["#4f1f1f", "#461b1b", "#57241f", "#3f1818"], "cap": "#7d4636",
        "rock": ["#8a3420", "#7b2d1b", "#983d25", "#6f2818", "#873320", "#652416"], "spire": "#a8492a",
        "warm": "#ff8a4a", "warm_op": 0.2, "talus": "#1a0c08",
        "shade": "#160806", "shade_op": 0.62,
        "rimlight": "#ff9d5a", "rim_w": 3.4,
        "haze": "#6e2b2b", "haze_op": 0.45,
        "floor_top": "#3a1810", "floor_bot": "#170a07", "soil": ("#4c2116", "#0e0604"),
        "tree_far": "#221d14", "tree": "#17140e", "tree_near": "#0d0b07", "tree_lit": "#5c4128",
        "cast": "#000000", "cast_op": 0.35,
        "creek_lo": "#7e3424", "creek_hi": "#ffb67c", "bank": "#0c0604",
        "near": "#0f0907", "near_top": "#1f120c", "near_lit": "#8a4322", "near_tree": "#070604",
        "cactus": "#0a0705", "spine": "#ffa560", "bloom": "#ff6a3a",
        "alpen": "#ff4a1f", "alpen_op": 0.22, "hawk": "#120a10",
        "fg": "#f5efe6", "muted": "#b2a396", "accent": "#f08a4b", "border": "#2c2420",
    },
}

# Ticker lines under the tagline: (name, gloss).
TICKER = [
    ("timbre", "one idea, five platforms, your voice"),
    ("ariadne", "dependency graphs for coding agents"),
    ("mjolnir", "a native command center for agents"),
    ("on the tip", "the word's right there"),
    ("magistrate", "budgets for fleets of agents"),
    ("oras", "quality signals, not ad spend"),
    ("qc water", "your 2027 water bill, before it arrives"),
]


# ---------------------------------------------------------------- geometry

def num(v: float) -> str:
    s = f"{v:.1f}"
    return s[:-2] if s.endswith(".0") else s


def line(pts) -> str:
    return "M" + "L".join(f"{num(x)} {num(y)}" for x, y in pts)


def poly(pts) -> str:
    return line(pts) + "Z"


def circle(cx: float, cy: float, r: float) -> str:
    return (f"M{num(cx - r)} {num(cy)}a{num(r)} {num(r)} 0 1 0 {num(2 * r)} 0"
            f"a{num(r)} {num(r)} 0 1 0 {num(-2 * r)} 0")


def catmull(points, samples: int = 6):
    """Densify a polyline into a smooth curve through every point."""
    out, n = [], len(points)
    for i in range(n - 1):
        p0 = points[max(i - 1, 0)]
        p1, p2 = points[i], points[i + 1]
        p3 = points[min(i + 2, n - 1)]
        for s in range(samples):
            t = s / samples
            out.append(tuple(
                0.5 * (2 * p1[k] + (p2[k] - p0[k]) * t
                       + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * t * t
                       + (3 * p1[k] - p0[k] - 3 * p2[k] + p3[k]) * t ** 3)
                for k in (0, 1)))
    out.append(points[-1])
    return out


def inside(pts, x: float, y: float) -> bool:
    hit, j = False, len(pts) - 1
    for i, (xi, yi) in enumerate(pts):
        xj, yj = pts[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            hit = not hit
        j = i
    return hit


def surface_y(pts, x: float) -> float:
    """Highest point of a formation at x."""
    y = min(p[1] for p in pts)
    while y < BASE and not inside(pts, x, y):
        y += 1
    return y


def y_on(pts, x: float) -> float:
    """Height of an x-monotonic edge at x."""
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if min(x1, x2) <= x <= max(x1, x2) and x1 != x2:
            return y1 + (y2 - y1) * (x - x1) / (x2 - x1)
    return pts[-1][1]


def floor_y(x: float) -> float:
    return 343 + 2.5 * math.sin(x / 97) + 1.6 * math.sin(x / 41 + 1.3)


def creek_mid(x: float) -> float:
    return 372 + 4 * math.sin((x - CREEK[0]) / 80)


def creek_half(x: float) -> float:
    a, b = CREEK
    return 3.6 * math.sin(math.pi * (x - a) / (b - a)) if a <= x <= b else 0.0


# ---------------------------------------------------------------- landforms
# Outlines run from the left foot, over the top, to the right foot.

MOGOLLON_RIM = [
    (0, 304), (90, 302), (150, 299), (210, 300), (260, 296), (330, 294), (380, 291),
    (430, 292), (470, 288), (520, 287), (560, 284), (600, 282), (640, 277), (690, 274),
    (740, 272), (760, 268), (820, 267), (840, 263), (905, 262), (930, 258), (1000, 257),
    (1020, 253), (1090, 252), (1110, 256), (1150, 255), (1170, 250), (1200, 249),
]

# A line of flat-topped mesas in the haze below the rim.
FAR_MESAS = [
    (0, 318), (40, 317), (54, 312), (120, 311), (132, 316), (176, 318), (204, 319),
    (214, 313), (226, 308), (296, 307), (312, 312), (340, 318), (392, 321), (426, 322),
    (438, 316), (450, 310), (500, 309), (516, 303), (560, 302), (572, 309), (590, 318),
    (640, 322), (700, 326), (760, 330),
]

BACK_RANGE = [
    (690, BASE), (700, 318), (712, 306), (724, 300), (736, 288), (748, 284), (770, 283),
    (782, 276), (800, 274), (830, 276), (846, 270), (870, 268), (890, 262), (930, 260),
    (950, 252), (966, 248), (990, 250), (1010, 244), (1040, 242), (1060, 236),
    (1090, 234), (1200, 236), (1200, BASE),
]

LITTLE_MESA = [
    (548, BASE), (556, 318), (566, 304), (574, 291), (582, 287), (600, 286), (612, 283),
    (628, 284), (636, 291), (646, 301), (656, 316), (664, BASE),
]

COURTHOUSE = [
    (1105, BASE), (1114, 336), (1124, 326), (1130, 312), (1134, 298), (1140, 292),
    (1144, 276), (1147, 258), (1152, 252), (1155, 236), (1158, 218), (1160, 204),
    (1164, 196), (1168, 184), (1172, 180), (1180, 178), (1192, 177), (1204, 178),
    (1204, BASE),
]

CATHEDRAL = [
    (915, BASE), (926, 338), (936, 330), (942, 320), (946, 306), (952, 300), (955, 286),
    (957, 272), (964, 268), (966, 254), (968, 240), (972, 232), (975, 222), (977, 206),
    (979, 194), (981, 186), (983, 182), (985, 186), (987, 198), (989, 212), (993, 222),
    (998, 226), (1001, 214), (1003, 196), (1006, 180), (1008, 164), (1010, 150),
    (1012, 132), (1014, 118), (1016, 110), (1018, 108), (1020, 114), (1022, 130),
    (1024, 140), (1026, 124), (1028, 104), (1030, 96), (1032, 94), (1034, 98),
    (1036, 112), (1038, 128), (1040, 136), (1042, 124), (1044, 116), (1046, 114),
    (1048, 120), (1050, 134), (1053, 150), (1056, 160), (1060, 158), (1064, 166),
    (1068, 182), (1072, 196), (1080, 200), (1084, 214), (1088, 230), (1096, 234),
    (1100, 250), (1104, 266), (1114, 270), (1118, 284), (1124, 300), (1134, 306),
    (1142, 320), (1154, 334), (1166, BASE),
]

# A bell: a domed crown with a small summit knob, steep sides, and a wide ledged skirt.
BELL_ROCK = catmull([
    (758, BASE), (772, 340), (788, 337), (796, 331), (810, 329), (816, 322), (828, 319),
    (834, 311), (844, 307), (849, 298), (857, 294), (861, 285), (865, 276), (868, 264),
    (871, 252), (874, 240), (878, 229), (883, 219), (888, 211), (893, 206), (897, 199),
    (899, 193), (901, 193), (903, 199), (907, 205), (912, 211), (917, 219), (921, 229),
    (924, 240), (927, 252), (930, 264), (933, 276), (938, 283), (946, 286), (950, 295),
    (958, 299), (968, 302), (972, 311), (984, 314), (988, 322), (1000, 325), (1006, 332),
    (1020, 338), (1032, BASE),
], samples=3)

# Where each formation turns from sunlit to shaded, top to bottom.
TERMINATORS = {
    "mesa": [(612, 283), (616, 310), (620, BASE + 5)],
    "courthouse": [(1176, 180), (1178, 240), (1182, 300), (1186, BASE + 5)],
    "cathedral": [(1033, 94), (1036, 140), (1044, 200), (1052, 260), (1060, BASE + 5)],
    "bell": [(900, 193), (903, 230), (908, 270), (912, 310), (916, BASE + 5)],
}

# The shaded east faces of spires that stand left of the main terminator.
SLIVERS = {
    "cathedral": [
        [(984, 182), (985, 186), (987, 198), (989, 212), (993, 222), (985, 222)],
        [(1018, 108), (1020, 114), (1022, 130), (1024, 140), (1024, 170), (1019, 170)],
    ],
}

# Foreground ledges, stepped like eroded sandstone.
LEFT_TOP = [
    (0, 326), (26, 324), (58, 327), (92, 332), (118, 333), (124, 340), (160, 343),
    (196, 347), (214, 348), (220, 356), (262, 364), (300, 374), (318, 376), (324, 384),
    (352, 394), (372, 401),
]
RIGHT_TOP = [
    (900, 401), (924, 392), (950, 382), (978, 374), (984, 366), (1020, 360), (1060, 354),
    (1066, 346), (1110, 341), (1150, 338), (1176, 334), (1200, 333),
]

# A red-tailed hawk seen from below, wings flat, tail fanned.
HAWK = ("M0-3C1.2-3 1.6-2 1.8-1.2L5-1.6C8-2 11-1.6 13-.4L12.4.2 13 .6 11.8.8C9 1.6 5 1.6 2 1.6"
        "L2.6 4.4C1.6 5.2-1.6 5.2-2.6 4.4L-2 1.6C-5 1.6-9 1.6-11.8.8L-13 .6-12.4.2-13-.4"
        "C-11-1.6-8-2-5-1.6L-1.8-1.2C-1.6-2-1.2-3 0-3Z")

CLOUDS = [  # cx, cy, width, height
    (1120, 58, 300, 10), (1010, 94, 360, 13), (1160, 120, 200, 7), (830, 110, 280, 10),
    (930, 140, 220, 7), (722, 164, 240, 7), (1010, 178, 170, 5), (648, 204, 170, 5),
]


# ---------------------------------------------------------------- drawing

class Svg:
    def __init__(self) -> None:
        self.defs: list[str] = []
        self.body: list[str] = []

    def grad(self, gid: str, stops, *, x1=0, y1=0, x2=0, y2=1, user=False) -> str:
        units = ' gradientUnits="userSpaceOnUse"' if user else ""
        s = "".join(
            f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a != 1 else "") + "/>"
            for o, c, a in stops)
        self.defs.append(f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{units}>{s}</linearGradient>')
        return f"url(#{gid})"

    def radial(self, gid: str, stops, **attrs) -> str:
        a = "".join(f' {k}="{v}"' for k, v in attrs.items())
        s = "".join(
            f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{op}"' if op != 1 else "") + "/>"
            for o, c, op in stops)
        self.defs.append(f'<radialGradient id="{gid}"{a}>{s}</radialGradient>')
        return f"url(#{gid})"

    def add(self, s: str) -> None:
        self.body.append(s)

    def mark(self) -> int:
        return len(self.body)

    def rise(self, start: int, delay: float) -> None:
        """Wrap everything added since start in a group that settles into place on load."""
        inner = self.body[start:]
        del self.body[start:]
        style = f' style="animation-delay:{delay}s"' if delay else ""
        self.body.append(f'<g class="rise"{style}>' + "\n".join(inner) + "</g>")


def rim_light(pts, color: str, width: float, floor: float = BASE, light=LIGHT) -> str:
    """Stroke the edges that face the sun, brightest where they face it squarely."""
    lx, ly = light
    ln = math.hypot(lx, ly)
    lx, ly = lx / ln, ly / ln
    buckets: dict[int, list[str]] = {0: [], 1: [], 2: []}
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        if y1 >= floor - 0.5 and y2 >= floor - 0.5:
            continue
        dx, dy = x2 - x1, y2 - y1
        length = math.hypot(dx, dy)
        if not length:
            continue
        face = (dy * lx - dx * ly) / length  # outward normal is (dy, -dx)
        bucket = 0 if face > 0.7 else 1 if face > 0.4 else 2 if face > 0.15 else None
        if bucket is not None:
            buckets[bucket].append(f"M{num(x1)} {num(y1)}L{num(x2)} {num(y2)}")
    out = []
    for bucket, op in zip(buckets, (0.95, 0.6, 0.28)):
        if buckets[bucket]:
            out.append(f'<path d="{"".join(buckets[bucket])}" stroke="{color}" stroke-width="{width}"'
                       f' stroke-opacity="{op}" stroke-linecap="round" fill="none"/>')
    return "".join(out)


def wavy(x0: float, x1: float, y: float, rng, step: int = 28):
    phase, amp, tilt = rng.uniform(0, 6.28), rng.uniform(0.3, 1.2), rng.uniform(-0.012, 0.012)
    return [(x, y + amp * math.sin(x * 0.05 + phase) + tilt * (x - x0))
            for x in range(int(x0), int(x1) + step, step)]


def bands(x0: float, x1: float, y0: float, rng, colors, first: str | None, first_h: float):
    """Sandstone beds: wide horizontal bands, each a slightly different red."""
    fills, edges = [], []
    if first:
        fills.append(f'<rect x="{num(x0)}" y="{num(y0 - 2)}" width="{num(x1 - x0)}" height="{num(BASE - y0 + 12)}" fill="{first}"/>')
    y, prev = (y0 + first_h) if first else y0 - 4, None
    while y < BASE:
        color = rng.choice([c for c in colors if c != prev])
        prev = color
        edge = wavy(x0, x1, y, rng)
        fills.append(f'<path d="{poly(edge + [(edge[-1][0], BASE + 10), (edge[0][0], BASE + 10)])}" fill="{color}"/>')
        edges.append(edge)
        y += rng.uniform(6, 15)
    return fills, edges[1:] if not first else edges


def fins(pts, rng, count: int, t: dict) -> str:
    """Vertical ribs: a lit sliver on the sun side and a tapering shadow beside it."""
    xs = [p[0] for p in pts]
    dark, lit = [], []
    for _ in range(count):
        x = rng.uniform(min(xs) + 4, max(xs) - 4)
        top = surface_y(pts, x) + rng.uniform(3, 24)
        if top > BASE - 14:
            continue
        bottom = min(BASE + 6, top + rng.uniform(26, 110))
        wt, wb, drift = rng.uniform(0.6, 1.5), rng.uniform(2.5, 6.5), rng.uniform(-2.5, 2.5)
        dark.append(poly([(x, top), (x + wt, top), (x + wb + drift, bottom), (x + drift, bottom)]))
        lit.append(poly([(x - 1.2, top + 3), (x, top), (x + drift, bottom), (x - 1.6 + drift, bottom)]))
    return (f'<path d="{"".join(dark)}" fill="{t["shade"]}" fill-opacity=".3"/>'
            f'<path d="{"".join(lit)}" fill="{t["rimlight"]}" fill-opacity=".22"/>')


def scrub(pts, rng, count: int, color: str) -> str:
    """Sparse brush on the talus at the foot of a formation."""
    xs = [p[0] for p in pts]
    blobs, tries = [], 0
    while len(blobs) < count and tries < count * 40:
        tries += 1
        x, y = rng.uniform(min(xs), max(xs)), rng.uniform(BASE - 22, BASE - 2)
        if inside(pts, x, y - 3):
            blobs.append(circle(x, y, rng.uniform(0.9, 1.7)))
    return f'<path d="{"".join(blobs)}" fill="{color}" fill-opacity=".5"/>'


def formation(svg: Svg, t: dict, fid: str, pts, rng, *, palette, first: str | None = None,
              first_h: float = 0, fin_count: int = 0, scrub_count: int = 0, haze: float = 0) -> None:
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    x0, x1, y0 = min(xs), max(xs), min(ys)
    d = poly(pts)
    svg.defs.append(f'<clipPath id="c-{fid}"><path d="{d}"/></clipPath>')
    svg.add(f'<path d="{d}" fill="{palette[0]}"/>')

    fills, edges = bands(x0 - 8, x1 + 8, y0, rng, palette, first, first_h)
    inner = fills
    ledges = [e for e in edges if rng.random() < 0.75]
    if ledges:
        ld = "".join(line(e) for e in ledges)
        inner.append(f'<path d="{ld}" transform="translate(0 1.4)" stroke="{t["shade"]}" stroke-opacity=".28" stroke-width="1.6" fill="none"/>')
        inner.append(f'<path d="{ld}" stroke="{t["rimlight"]}" stroke-opacity=".32" stroke-width="1" fill="none"/>')
    if fin_count:
        inner.append(fins(pts, rng, fin_count, t))

    tone = svg.grad(f"o-{fid}", [(0, t["warm"], t["warm_op"]), (0.3, t["warm"], 0),
                                 (0.72, t["shade"], 0), (1, t["talus"], 0.55)], y1=y0, y2=BASE, user=True)
    inner.append(f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(x1 - x0)}" height="{num(BASE - y0 + 4)}" fill="{tone}"/>')
    inner.append(f'<g opacity="{t["alpen_op"]}"><rect class="alpen" x="{num(x0)}" y="{num(y0)}" width="{num(x1 - x0)}"'
                 f' height="{num(BASE - y0 + 4)}" fill="{t["alpen"]}"/></g>')

    shade = []
    term = TERMINATORS.get(fid)
    if term:
        right = x1 + 40
        shade.append(poly(term + [(right, BASE + 10), (right, y0 - 40), (term[0][0], y0 - 40)]))
    shade += [poly(s) for s in SLIVERS.get(fid, [])]
    if shade:
        inner.append(f'<path d="{"".join(shade)}" fill="{t["shade"]}" fill-opacity="{t["shade_op"]}"/>')
    if haze:
        inner.append(f'<rect x="{num(x0)}" y="{num(y0)}" width="{num(x1 - x0)}" height="{num(BASE - y0 + 4)}"'
                     f' fill="{t["haze"]}" fill-opacity="{haze}"/>')
    rim = rim_light(pts, t["rimlight"], t["rim_w"])
    inner.append(f'<g opacity="{round(1 - haze, 2)}">{rim}</g>' if haze else rim)
    if scrub_count:
        inner.append(scrub(pts, rng, scrub_count, t["tree_far"]))
    svg.add(f'<g clip-path="url(#c-{fid})">{"".join(inner)}</g>')


def juniper(x: float, y: float, r: float, rng, fill: str, *, cast: str | None = None,
            lit: str | None = None) -> str:
    out = []
    if cast:
        out.append(f'<ellipse cx="{num(x + r * 2.4)}" cy="{num(y + 0.4)}" rx="{num(r * 2.8)}"'
                   f' ry="{num(max(0.7, r * 0.26))}" fill="{cast}"/>')
    blobs = [(x, y - r * 0.85, r)]
    for _ in range(rng.randint(2, 4)):
        blobs.append((x + rng.uniform(-0.8, 0.8) * r, y - r * rng.uniform(0.7, 1.6), r * rng.uniform(0.45, 0.72)))
    out.append(f'<path d="{"".join(circle(*b) for b in blobs)}" fill="{fill}"/>')
    if lit:
        hl = "".join(circle(cx - cr * 0.3, cy - cr * 0.25, cr * 0.55) for cx, cy, cr in blobs)
        out.append(f'<path d="{hl}" fill="{lit}" fill-opacity=".45"/>')
    return "".join(out)


def saguaro(svg: Svg, t: dict, x: float, y: float, h: float, color: str, arms, *,
            rim: bool = False, sid: str = "", ribs: bool = False) -> str:
    """A saguaro: a round-topped column whose arms bend up toward the sky.

    Each arm is (side, height up the trunk, reach in trunk widths, rise as a
    fraction of the height). With rim, a fringe of backlit spines and a lit
    stripe run along the side that faces the sun.
    """
    w = max(1.1, h * 0.09)
    aw = w * 0.78
    sun = 1 if x < SUN[0] else -1
    trunk = f"M{num(x)} {num(y)}V{num(y - h + w / 2)}"
    limbs = []
    for side, at, reach, rise in arms:
        ya, ax = y - h * at, x + side * reach * w
        r = min(reach * w * 0.6, aw * 1.3)
        limbs.append(f"M{num(x)} {num(ya)}H{num(ax - side * r)}Q{num(ax)} {num(ya)} {num(ax)} {num(ya - r)}"
                     f"V{num(ya - h * rise)}")
    arm_d = "".join(limbs)

    def body(k: float = 1, add: float = 0) -> str:
        out = f'<path d="{trunk}" stroke-width="{num(w * k + add)}"/>'
        if arm_d:
            out += f'<path d="{arm_d}" stroke-width="{num(aw * k + add)}"/>'
        return out

    out = [f'<ellipse cx="{num(x)}" cy="{num(y + 0.4)}" rx="{num(w * 1.5)}" ry="{num(max(0.6, w * 0.22))}"'
           f' fill="{color}" fill-opacity=".45"/>']
    if rim:
        out.append(f'<g transform="translate({num(sun * 0.8)} 0)" stroke="{t["spine"]}" stroke-dasharray=".5 1.2"'
                   f' stroke-linecap="butt" fill="none" opacity=".85">{body(1, 1.6)}</g>')
    out.append(f'<g stroke="{color}" stroke-linecap="round" fill="none">{body()}</g>')
    if ribs:
        rd = "".join(f"M{num(x + o * w)} {num(y)}V{num(y - h + w * 0.8)}" for o in (-0.3, -0.12, 0.12, 0.3))
        out.append(f'<path d="{rd}" stroke="#000" stroke-opacity=".22" stroke-width="{num(max(0.6, w * 0.06))}" fill="none"/>')
    if rim:
        svg.defs.append(f'<mask id="m-{sid}" maskUnits="userSpaceOnUse" x="{num(x - h)}" y="{num(y - h - 10)}"'
                        f' width="{num(2 * h)}" height="{num(h + 20)}">'
                        f'<g stroke="#fff" stroke-linecap="round" fill="none">{body()}</g></mask>')
        out.append(f'<g mask="url(#m-{sid})"><g transform="translate({num(sun * w * 0.34)} 0)" stroke="{t["rimlight"]}"'
                   f' stroke-linecap="round" fill="none" opacity=".7">{body(0.28)}</g></g>')
    return "".join(out)


def ocotillo(t: dict, x: float, y: float, h: float, rng) -> str:
    """An ocotillo: a fan of thin, thorny canes, most of them tipped with red blooms."""
    k = h / 70
    out = []
    for i in range(13):
        s = (i - 6) / 6
        a = math.radians(-90 + s * 30 + rng.uniform(-4, 4))
        length = h * rng.uniform(0.72, 1) * (1 - 0.15 * abs(s))
        bx = x + s * 2.2 * k + rng.uniform(-0.6, 0.6) * k
        tx, ty = bx + math.cos(a) * length, y + math.sin(a) * length
        cx, cy = bx + (tx - bx) * 0.7, y - length * 0.4
        left, right = [], []
        for j in range(11):
            u = j / 10
            px = (1 - u) ** 2 * bx + 2 * (1 - u) * u * cx + u * u * tx
            py = (1 - u) ** 2 * y + 2 * (1 - u) * u * cy + u * u * ty
            dx = 2 * (1 - u) * (cx - bx) + 2 * u * (tx - cx)
            dy = 2 * (1 - u) * (cy - y) + 2 * u * (ty - cy)
            dl = math.hypot(dx, dy) or 1
            hw = (1.1 * (1 - u) + 0.3 * u) * k
            nx, ny = -dy / dl * hw, dx / dl * hw
            left.append((px + nx, py + ny))
            right.append((px - nx, py - ny))
        parts = [f'<path d="{poly(left + right[::-1])}"/>',
                 f'<path d="M{num(bx)} {num(y)}Q{num(cx)} {num(cy)} {num(tx)} {num(ty)}" stroke="{t["cactus"]}"'
                 f' stroke-width="{num(2.6 * k)}" stroke-dasharray=".5 2.2" fill="none"/>']
        if rng.random() < 0.75:
            ex, ey = tx - cx, ty - cy
            el = math.hypot(ex, ey) or 1
            parts.append(f'<path d="M{num(tx)} {num(ty)}l{num(ex / el * 4.5 * k)} {num(ey / el * 4.5 * k)}"'
                         f' stroke="{t["bloom"]}" stroke-width="{num(2.2 * k)}" stroke-linecap="round"/>')
        out.append(f'<g class="sway" style="transform-origin:{num(bx)}px {num(y)}px;'
                   f'animation-delay:-{rng.uniform(0, 4.8):.1f}s">{"".join(parts)}</g>')
    return f'<g fill="{t["cactus"]}">{"".join(out)}</g>'


def cholla(svg: Svg, t: dict, x: float, y: float, h: float, rng, cid: str) -> str:
    """A teddy-bear cholla: stubby jointed arms wrapped in a halo of backlit spines."""
    sun = 1 if x < SUN[0] else -1
    top = (x, y - h * 0.38)
    rx, ry = h * 0.13, h * 0.085
    n = rng.randint(10, 13)
    branches = 4 if n < 12 else 5
    tips = [[top[0], top[1], -90 + (b - (branches - 1) / 2) * 34 + rng.uniform(-8, 8)] for b in range(branches)]
    joints = []
    for side in (-1, 1):  # fallen joints piled around the base
        fx = x + side * rng.uniform(0.22, 0.42) * h
        joints.append(f'<ellipse cx="{num(fx)}" cy="{num(y - ry * 0.5)}" rx="{num(rx * 0.85)}" ry="{num(ry * 0.75)}"'
                      f' transform="rotate({num(rng.uniform(-20, 20))} {num(fx)} {num(y - ry * 0.5)})"/>')
    for j in range(n):
        tip = tips[j % branches]
        px, py, ang = tip
        a = math.radians(ang)
        joints.append(f'<ellipse cx="{num(px + math.cos(a) * rx * 0.85)}" cy="{num(py + math.sin(a) * rx * 0.85)}"'
                      f' rx="{num(rx)}" ry="{num(ry)}" transform="rotate({num(ang)} {num(px + math.cos(a) * rx * 0.85)}'
                      f' {num(py + math.sin(a) * rx * 0.85)})"/>')
        tip[0], tip[1] = px + math.cos(a) * rx * 1.45, py + math.sin(a) * rx * 1.45
        tip[2] = ang + (-90 - ang) * 0.4 + rng.uniform(-14, 14)
    svg.defs.append(f'<g id="j-{cid}">{"".join(joints)}</g>')
    fuzz = max(0.7, h * 0.05)
    return (f'<circle class="warm" cx="{num(x)}" cy="{num(y - h * 0.62)}" r="{num(h * 0.8)}" fill="url(#chglow)"/>'
            f'<use href="#j-{cid}" class="spines" transform="translate({num(sun * 0.6)} 0)" fill="none"'
            f' stroke="{t["spine"]}" stroke-width="{num(fuzz * 2)}" stroke-dasharray=".45 .8" stroke-linecap="butt"/>'
            f'<path d="M{num(x)} {num(y + 0.5)}V{num(top[1])}" stroke="{t["cactus"]}" stroke-width="{num(h * 0.12)}"'
            f' stroke-linecap="round"/>'
            f'<use href="#j-{cid}" fill="{t["cactus"]}"/>'
            f'<use href="#j-{cid}" fill="none" stroke="{t["spine"]}" stroke-width="{num(fuzz)}"'
            f' stroke-dasharray=".45 .8" opacity=".45"/>')


def brush(x: float, y: float, r: float, rng, fill: str, lit: str) -> str:
    """A low desert shrub: a dome edged with small leaf clusters."""
    sun = 1 if x < SUN[0] else -1
    dome = f"M{num(x - r * 1.5)} {num(y)}A{num(r * 1.5)} {num(r)} 0 0 1 {num(x + r * 1.5)} {num(y)}Z"
    dots, glints = [], []
    for _ in range(int(8 + r * 3)):
        a = rng.uniform(math.pi * 1.04, math.pi * 1.96)
        cx, cy = x + math.cos(a) * r * 1.5, y + math.sin(a) * r
        cr = rng.uniform(0.5, 0.9) * (0.4 + r * 0.12)
        dots.append(circle(cx, cy, cr))
        if math.cos(a) * sun > 0.2:
            glints.append(circle(cx, cy - cr * 0.3, cr * 0.6))
    return (f'<path d="{dome}" fill="{fill}"/><path d="{"".join(dots)}" fill="{fill}"/>'
            f'<path d="{"".join(glints)}" fill="{lit}" fill-opacity=".5"/>')


def lens(cx: float, cy: float, w: float, h: float, lift: float) -> str:
    """A thin, flat-bottomed cloud: fuller on the left, tapering to the right."""
    x0, x1 = cx - w / 2, cx + w / 2
    return (f"M{num(x0)} {num(cy)}Q{num(cx - w * 0.15)} {num(cy - h * 1.5)} {num(x1)} {num(cy - h * lift)}"
            f"Q{num(cx + w * 0.05)} {num(cy + h * 0.7)} {num(x0)} {num(cy)}Z")


def ledge(svg: Svg, t: dict, gid: str, top, rng, light=LIGHT) -> None:
    """A dark foreground outcrop with a sunlit lip and bedding lines."""
    closed = top + ([(0, H + 1)] if top[0][0] == 0 else [(W, H + 1)])
    d = poly(closed)
    svg.defs.append(f'<clipPath id="c-{gid}"><path d="{d}"/></clipPath>')
    fill = svg.grad(f"g-{gid}", [(0, t["near_top"], 1), (0.45, t["near"], 1)], y1=340, y2=H, user=True)
    svg.add(f'<path d="{d}" fill="{fill}"/>')
    beds = []
    for k in range(1, 7):
        off = k * rng.uniform(5.5, 8)
        beds.append(line([(x, y + off + rng.uniform(-0.6, 0.6)) for x, y in top]))
    svg.add(f'<g clip-path="url(#c-{gid})"><path d="{"".join(beds)}" stroke="{t["near_lit"]}" stroke-opacity=".14"'
            f' stroke-width="1" fill="none"/>{rim_light(top, t["near_lit"], 1.8, floor=H + 10, light=light)}</g>')


# ---------------------------------------------------------------- the scene

STYLE = """
    .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
    .serif { font-family: "Iowan Old Style", "Palatino Linotype", Palatino, Georgia, serif; }
    .in { opacity: 0; animation: in 1.2s ease-out forwards; }
    @keyframes in { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: none; } }
    .sun { animation: set 16s ease-in-out infinite alternate; }
    @keyframes set { from { transform: translateY(-16px); } to { transform: translateY(10px); } }
    .rays { animation: breathe 9s ease-in-out infinite alternate; }
    @keyframes breathe { from { opacity: .5; } to { opacity: 1; } }
    .drift { animation: drift 80s ease-in-out infinite alternate; }
    .drift.slow { animation-duration: 110s; animation-direction: alternate-reverse; }
    @keyframes drift { to { transform: translateX(-48px); } }
    .star { animation: twinkle 4s ease-in-out infinite; }
    @keyframes twinkle { 50% { opacity: .15; } }
    .glint { animation: glint 3.4s ease-in-out infinite; }
    @keyframes glint { 0%, 100% { opacity: .15; } 50% { opacity: 1; } }
    .alpen { animation: alpen 16s ease-in-out infinite alternate; }
    @keyframes alpen { from { opacity: 0; } to { opacity: 1; } }
    .warm, .spines { animation: warm 16s ease-in-out infinite alternate; }
    @keyframes warm { from { opacity: .62; } to { opacity: 1; } }
    .sway { animation: sway 4.8s ease-in-out infinite alternate; }
    @keyframes sway { from { transform: rotate(-1.4deg); } to { transform: rotate(1.8deg); } }
    .hawk-x { animation: hawkx 13s ease-in-out infinite alternate; }
    @keyframes hawkx { from { transform: translateX(-64px); } to { transform: translateX(64px); } }
    .hawk-y { animation: hawky 13s ease-in-out -6.5s infinite alternate; }
    @keyframes hawky { from { transform: translateY(-11px); } to { transform: translateY(11px); } }
    .hawk { transform-box: fill-box; transform-origin: center; animation: bank 13s ease-in-out infinite alternate; }
    @keyframes bank { 0% { transform: rotate(-8deg) scaleX(.82); } 50% { transform: none; } 100% { transform: rotate(8deg) scaleX(.82); } }
    .meteor { opacity: 0; animation: meteor 12s linear 4s infinite; }
    @keyframes meteor { 0%, 88% { opacity: 0; transform: none; } 90% { opacity: 1; } 95%, 100% { opacity: 0; transform: translate(-130px, 48px); } }
    .rise { animation: rise 1.6s cubic-bezier(.2,.7,.2,1) backwards; }
    @keyframes rise { from { opacity: 0; transform: translateY(8px); } }
    .r { opacity: 0; animation: cycle 21s infinite backwards; }
    @keyframes cycle { 0% { opacity: 0; } 1.7% { opacity: 1; } 12.9% { opacity: 1; } 14.6% { opacity: 0; } 100% { opacity: 0; } }
    .caret { animation: blink 1.1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }
    @media (prefers-reduced-motion: reduce) {
      * { animation: none !important; }
      .in, .r1 { opacity: 1; }
      .alpen { opacity: .5; }
    }"""


def render(t: dict) -> str:
    rng = random.Random(1688)
    svg = Svg()
    svg.defs.append(f'<clipPath id="card"><rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18"/></clipPath>')

    # Sky, the glow around the sun, and a soft wash behind the words.
    sky = svg.grad("sky", [(o, c, 1) for o, c in t["sky"]])
    svg.add(f'<rect width="{W}" height="{H}" fill="{sky}"/>')
    glow = svg.radial("glow", [(0, t["glow"], t["glow_op"]), (0.45, t["glow"], round(t["glow_op"] * 0.4, 2)), (1, t["glow"], 0)])
    svg.add(f'<ellipse class="warm" cx="{SUN[0]}" cy="300" rx="640" ry="300" fill="{glow}"/>')

    if t["stars"]:
        stars = []
        while len(stars) < 90:
            x, y = rng.uniform(10, W - 10), (rng.random() ** 1.4) * 235 + 8
            if math.hypot(x - SUN[0], (y - SUN[1]) * 1.6) < 300:
                continue
            op = round(max(0.15, 1 - y / 250) * rng.uniform(0.5, 1), 2)
            cls = ' class="star"' if rng.random() < 0.3 else ""
            delay = f' style="animation-delay:{rng.uniform(0, 4):.1f}s"' if cls else ""
            stars.append(f'<circle{cls} cx="{num(x)}" cy="{num(y)}" r="{num(rng.uniform(0.45, 1.35))}" opacity="{op}"{delay}/>')
        svg.add(f'<g fill="#fff6ea">{"".join(stars)}</g>')
        # Now and then a meteor streaks down toward the rim.
        trail = svg.grad("meteor", [(0, "#fff6ea", 1), (1, "#fff6ea", 0)], x1=1070, y1=52, x2=1118, y2=34, user=True)
        svg.add(f'<path class="meteor" d="M1070 52L1118 34" stroke="{trail}" stroke-width="1.4"'
                f' stroke-linecap="round" fill="none"/>')

    # The sun, its halo and its rays travel together. The rays fade out
    # before they reach the words.
    halo = svg.radial("halo", [(0, t["halo"], t["halo_op"]), (1, t["halo"], 0)])
    disk = svg.radial("disk", [(0, t["sun_core"], 1), (0.7, t["sun_core"], 1), (1, t["sun_edge"], 1)])
    ray = svg.radial("ray", [(0, t["sun_core"], 1), (1, t["sun_core"], 0)],
                     gradientUnits="userSpaceOnUse", cx=SUN[0], cy=SUN[1], r=720)
    fade = svg.grad("rayfade", [(0, "#000", 1), (1, "#fff", 1)], x1=470, y1=0, x2=690, y2=0, user=True)
    svg.defs.append(f'<mask id="raymask"><rect width="{W}" height="{H}" fill="{fade}"/></mask>')
    wedges = []
    for deg in (-168, -150, -131, -112, -94, -75, -56, -38, -20):
        a, b = math.radians(deg - 1.3), math.radians(deg + 1.3)
        wedges.append(poly([SUN, (SUN[0] + 760 * math.cos(a), SUN[1] + 760 * math.sin(a)),
                            (SUN[0] + 760 * math.cos(b), SUN[1] + 760 * math.sin(b))]))
    svg.add(f'<g mask="url(#raymask)"><g class="sun"><g opacity="{t["rays_op"]}">'
            f'<path class="rays" d="{"".join(wedges)}" fill="{ray}"/></g></g></g>')
    svg.add(f'<g class="sun"><circle cx="{SUN[0]}" cy="{SUN[1]}" r="120" fill="{halo}"/>'
            f'<circle cx="{SUN[0]}" cy="{SUN[1]}" r="34" fill="{disk}"/></g>')

    # Long evening clouds, lit from underneath.
    cloud = svg.grad("cloud", [(0, t["cloud_top"], 1), (0.55, t["cloud_top"], 1), (1, t["cloud_lit"], 1)])
    fast, slow = [], []
    for i, (cx, cy, w, h) in enumerate(CLOUDS):
        d = lens(cx, cy, w, h, rng.uniform(0, 0.3))
        for _ in range(2):
            d += lens(cx + rng.uniform(-0.3, 0.3) * w, cy + rng.uniform(-0.5, 0.8) * h,
                      w * rng.uniform(0.35, 0.6), h * rng.uniform(0.5, 0.8), rng.uniform(0, 0.3))
        (fast if i % 2 else slow).append(f'<path d="{d}"/>')
    svg.add(f'<g fill="{cloud}" opacity="{t["cloud_op"]}"><g class="drift">{"".join(fast)}</g>'
            f'<g class="drift slow">{"".join(slow)}</g></g>')

    scrim = svg.grad("scrim", [(0, t["scrim"], t["scrim_op"]), (0.55, t["scrim"], round(t["scrim_op"] * 0.5, 2)), (1, t["scrim"], 0)],
                     x1=0, y1=0, x2=640, y2=0, user=True)
    svg.add(f'<rect width="640" height="330" fill="{scrim}"/>')

    # A red-tailed hawk circling above Bell Rock, banking at each end of its loop.
    svg.add(f'<g transform="translate(860 160) scale(1.2)"><g class="hawk-x"><g class="hawk-y">'
            f'<path class="hawk" d="{HAWK}" fill="{t["hawk"]}"/></g></g></g>')

    # Distant layers, each catching a little of the light along its top.
    m = svg.mark()
    for pts, key in ((MOGOLLON_RIM, "rim"), (FAR_MESAS, "mid")):
        svg.add(f'<path d="{poly(pts + [(W, H), (0, H)])}" fill="{t[key]}"/>')
        svg.add(f'<g opacity=".45">{rim_light(pts, t["rimlight"], 1.2)}</g>')
    svg.add(f'<path d="{poly(BACK_RANGE)}" fill="{t["range"]}"/>')
    svg.add(f'<g opacity=".5">{rim_light(BACK_RANGE, t["rimlight"], 1.4)}</g>')
    svg.rise(m, 0)

    # The red rocks, back to front.
    m = svg.mark()
    formation(svg, t, "mesa", LITTLE_MESA, rng, palette=t["butte"], fin_count=4, scrub_count=6, haze=0.3)
    formation(svg, t, "courthouse", COURTHOUSE, rng, palette=t["butte"], first=t["cap"], first_h=14,
              fin_count=8, scrub_count=8, haze=0.18)
    formation(svg, t, "cathedral", CATHEDRAL, rng, palette=t["rock"], first=t["spire"], first_h=34,
              fin_count=20, scrub_count=16)
    formation(svg, t, "bell", BELL_ROCK, rng, palette=t["rock"], first=t["spire"], first_h=24,
              fin_count=16, scrub_count=16)

    haze = svg.grad("haze", [(0, t["haze"], 0), (1, t["haze"], t["haze_op"])], y1=272, y2=BASE, user=True)
    svg.add(f'<rect y="272" width="{W}" height="{BASE - 272 + 4}" fill="{haze}"/>')
    svg.rise(m, 0.15)

    # The valley floor, Oak Creek, juniper flats and young saguaros.
    m = svg.mark()
    floor_pts = [(x, floor_y(x)) for x in range(0, W + 1, 20)] + [(W, H + 1), (0, H + 1)]
    floor = svg.grad("floor", [(0, t["floor_top"], 1), (1, t["floor_bot"], 1)], y1=338, y2=H, user=True)
    svg.add(f'<path d="{poly(floor_pts)}" fill="{floor}"/>')

    soil = {0: [], 1: []}
    for _ in range(32):
        x, y = rng.uniform(0, W), 347 + (rng.random() ** 1.2) * 50
        depth = (y - 342) / 58
        soil[rng.randint(0, 1)].append(
            f'<ellipse cx="{num(x)}" cy="{num(y)}" rx="{num(rng.uniform(14, 40) * (0.6 + depth))}" ry="{num(0.6 + depth * 1.8)}"/>')
    for k, color in enumerate(t["soil"]):
        svg.add(f'<g fill="{color}" fill-opacity=".4">{"".join(soil[k])}</g>')

    def open_ground(x: float, y: float) -> bool:
        if not floor_y(x) + 1.5 < y < H - 3:
            return False
        if abs(y - creek_mid(x)) < creek_half(x) + 3:
            return False
        return not ((x < LEFT_TOP[-1][0] and y > y_on(LEFT_TOP, x) + 4)
                    or (x > RIGHT_TOP[0][0] and y > y_on(RIGHT_TOP, x) + 4))

    # Each plant is (y, x, kind, data) so the whole floor can be drawn back to front.
    plants = []
    for _ in range(12):  # stands of juniper
        cx = rng.uniform(0, W)
        cy = floor_y(cx) + 3 + (rng.random() ** 1.3) * 48
        depth = (cy - 342) / 58
        for _ in range(rng.randint(3, 8)):
            x, y = cx + rng.gauss(0, 7 + depth * 20), cy + rng.gauss(0, 1 + depth * 2.5)
            if open_ground(x, y):
                plants.append((y, x, "j", None))
    while len(plants) < 84:  # and loners between them
        x = rng.uniform(-10, W + 10)
        y = floor_y(x) + 2 + (rng.random() ** 1.5) * 52
        if open_ground(x, y):
            plants.append((y, x, "j", None))
    placed = 0
    while placed < 18:  # young saguaros scattered across the flats
        x = rng.uniform(20, W - 20)
        y = floor_y(x) + 2 + (rng.random() ** 1.3) * 50
        if abs(x - SUN[0]) < 80 or not open_ground(x, y):
            continue
        depth = (y - 342) / 58
        h = (7 + depth * 34) * rng.uniform(0.75, 1.25)
        arms, side = [], rng.choice((-1, 1))
        for _ in range(rng.choice((0, 1, 1, 2, 2, 3))):
            arms.append((side, rng.uniform(0.35, 0.62), rng.uniform(1.4, 2.1), rng.uniform(0.14, 0.3)))
            side = -side
        plants.append((y, x, "s", (h, arms)))
        placed += 1
    # One taller saguaro standing out against the haze beneath the sun.
    sx = 742
    plants.append((floor_y(sx) + 3, sx, "S", (58, [(-1, 0.48, 1.9, 0.26), (1, 0.6, 1.6, 0.2)])))
    plants.sort(key=lambda p: (p[0], p[1]))

    def tree_color(y: float) -> str:
        return t["tree_far"] if y < 356 else t["tree"] if y < 378 else t["tree_near"]

    def tree_size(y: float) -> float:
        return (1.1 + (y - 342) * 0.13) * rng.uniform(0.7, 1.25)

    def plant(y: float, x: float, kind: str, data, front: bool) -> None:
        if kind == "j":
            r = tree_size(y)
            svg.add(juniper(x, y, r, rng, tree_color(y), cast=t["cast"] if r > 2.6 else None,
                            lit=t["tree_lit"] if front and r > 4.5 else None))
        elif kind == "s":
            h, arms = data
            svg.add(saguaro(svg, t, x, y, h, tree_color(y), arms))
        else:
            h, arms = data
            svg.add(saguaro(svg, t, x, y, h, t["tree_near"], arms, rim=True, sid="s"))

    for y, x, kind, data in plants:
        if y < creek_mid(x):
            plant(y, x, kind, data, False)

    creek_x = list(range(CREEK[0], CREEK[1] + 1, 10))
    upper = [(x, creek_mid(x) - creek_half(x)) for x in creek_x]
    lower = [(x, creek_mid(x) + creek_half(x)) for x in reversed(creek_x)]
    water = svg.grad("creek", [(0, t["creek_lo"], 1), (0.5, t["creek_hi"], 1), (1, t["creek_lo"], 1)],
                     x1=CREEK[0], y1=0, x2=CREEK[1], y2=0, user=True)
    svg.add(f'<path d="{poly(upper + lower)}" fill="{water}"/>')
    svg.add(f'<path d="{line([(x, y + 0.8) for x, y in reversed(lower)])}" stroke="{t["bank"]}"'
            f' stroke-opacity=".5" stroke-width="1.2" fill="none"/>')
    glints = []
    for k in range(7):
        x = 652 + k * 15 + rng.uniform(-4, 4)
        y = creek_mid(x) + rng.uniform(-1, 1)
        glints.append(f'<path class="glint" d="M{num(x)} {num(y)}h{num(rng.uniform(5, 11))}"'
                      f' style="animation-delay:{k * 0.45:.2f}s"/>')
    svg.add(f'<g stroke="{t["creek_hi"]}" stroke-width="1.3" stroke-linecap="round">{"".join(glints)}</g>')

    for y, x, kind, data in plants:
        if y >= creek_mid(x):
            plant(y, x, kind, data, True)
    svg.rise(m, 0.3)

    # Foreground ledges framing the corners, with the cacti that grow on them.
    m = svg.mark()
    ledge(svg, t, "left", LEFT_TOP, rng, light=(1, -0.18))
    ledge(svg, t, "right", RIGHT_TOP, rng)
    svg.radial("chglow", [(0, t["spine"], 0.45), (1, t["spine"], 0)])

    def on(top, x: float) -> float:
        return y_on(top, x) + 1.5

    for x, r in ((70, 4), (122, 3), (204, 5), (290, 3.5)):
        svg.add(brush(x, on(LEFT_TOP, x), r, rng, t["near_tree"], t["tree_lit"]))
    svg.add(saguaro(svg, t, 30, on(LEFT_TOP, 30), 112, t["cactus"], [(-1, 0.44, 1.7, 0.3), (1, 0.58, 1.6, 0.2)],
                    rim=True, sid="l"))
    svg.add(cholla(svg, t, 92, on(LEFT_TOP, 92), 28, rng, "a"))
    svg.add(ocotillo(t, 158, on(LEFT_TOP, 158), 70, rng))
    svg.add(cholla(svg, t, 238, on(LEFT_TOP, 238), 36, rng, "b"))
    svg.add(cholla(svg, t, 318, on(LEFT_TOP, 318), 21, rng, "c"))

    svg.add(cholla(svg, t, 958, on(RIGHT_TOP, 958), 23, rng, "d"))
    svg.add(ocotillo(t, 1012, on(RIGHT_TOP, 1012), 56, rng))
    svg.add(cholla(svg, t, 1080, on(RIGHT_TOP, 1080), 33, rng, "e"))
    svg.add(saguaro(svg, t, 1146, on(RIGHT_TOP, 1146), 178, t["cactus"], [(-1, 0.4, 2.0, 0.36), (1, 0.55, 1.7, 0.26)],
                    rim=True, ribs=True, sid="r"))
    svg.add(cholla(svg, t, 1186, on(RIGHT_TOP, 1186), 24, rng, "f"))
    svg.rise(m, 0.45)

    ticker = []
    for i, (name, gloss) in enumerate(TICKER):
        cls = "r r1" if i == 0 else "r"
        delay = f' style="animation-delay:{i * 3}s"' if i else ""
        ticker.append(f'    <text class="{cls}" x="88" y="256"{delay}>{name} <tspan fill="{t["muted"]}">— {gloss}</tspan></text>')

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
  <title id="t">Rembrandt Reyes</title>
  <desc id="d">Lorem LLC, Phoenix, Arizona. Most software is disposable. Ours is not. Sunset over the red rocks of Sedona, with saguaro, ocotillo and cholla in the foreground and a hawk circling overhead.</desc>
  <style>{STYLE}
  </style>
  <defs>{"".join(svg.defs)}</defs>
  <g clip-path="url(#card)">
{chr(10).join(svg.body)}
  </g>
  <rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="18" fill="none" stroke="{t["border"]}"/>

  <text class="mono in" x="64" y="78" font-size="13" letter-spacing="3" fill="{t["muted"]}">LOREM LLC  ·  PHOENIX, ARIZONA</text>
  <text class="serif in" x="62" y="154" font-size="62" fill="{t["fg"]}" style="animation-delay:.2s">Rembrandt Reyes</text>
  <text class="serif in" x="64" y="200" font-size="23" font-style="italic" fill="{t["muted"]}" style="animation-delay:.45s">Most software is disposable. Ours is not.</text>

  <g class="mono" font-size="15" fill="{t["fg"]}">
    <text class="in" x="64" y="256" fill="{t["accent"]}" style="animation-delay:.7s">›<tspan class="caret">_</tspan></text>
{chr(10).join(ticker)}
  </g>
</svg>
"""


def main() -> None:
    for name, theme in THEMES.items():
        out = ROOT / "assets" / f"hero-{name}.svg"
        out.write_text(render(theme))
        print(f"wrote {out.relative_to(ROOT)} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
