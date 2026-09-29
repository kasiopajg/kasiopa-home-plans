#!/usr/bin/env python3
"""Validate a plan JSON before delivery (structure, geometry, z-order, networks).

Usage:
    python scripts/validate_plan.py PLAN.json [--json]

Exit code 0 when there is no error (warnings allowed), 1 otherwise.
Element types, legacy aliases and z-order are read from assets/editor.html,
so the editor stays the single source of truth.
"""
import json
import math
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
EDITOR = SKILL_DIR / "assets" / "editor.html"
SCALE = 50


def load_editor_tables():
    src = EDITOR.read_text(encoding="utf-8")
    types = {m.group(1): {"kind": m.group(2), "layer": m.group(3)}
             for m in re.finditer(r'^\s+(\w+):\s*\{kind:"(\w+)",\s*layer:"(\w+)"', src, re.M)}
    legacy_block = re.search(r"var LEGACY = \{(.*?)\};", src, re.S).group(1)
    legacy = dict(re.findall(r'(\w+):"(\w+)"', legacy_block))
    z_block = re.search(r"var ZORDER = \{(.*?)\};", src, re.S).group(1)
    zorder = {k: float(v) for k, v in re.findall(r"(\w+):([\d.]+)", z_block)}
    return types, legacy, zorder


TYPES, LEGACY, ZORDER = load_editor_tables()


def kind(e):
    return TYPES.get(e["type"], {}).get("kind", "sym")


def is_poly(e):
    return kind(e) == "zone" and isinstance(e.get("pts"), list) and len(e["pts"]) > 2


def area_px(z):
    if is_poly(z):
        p = z["pts"]
        return abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))) / 2
    return z["w"] * z["h"]


def bbox(z):
    if is_poly(z):
        xs = [q[0] for q in z["pts"]]; ys = [q[1] for q in z["pts"]]
        return min(xs), min(ys), max(xs), max(ys)
    return z["x"], z["y"], z["x"] + z["w"], z["y"] + z["h"]


def point_in_poly(pts, x, y):
    inside, j = False, len(pts) - 1
    for i in range(len(pts)):
        if (pts[i][1] > y) != (pts[j][1] > y) and x < (pts[j][0] - pts[i][0]) * (y - pts[i][1]) / (pts[j][1] - pts[i][1]) + pts[i][0]:
            inside = not inside
        j = i
    return inside


def point_in_zone(z, x, y, m=0.0):
    if is_poly(z):
        return point_in_poly(z["pts"], x, y)
    x0, y0, x1, y1 = bbox(z)
    return x0 - m <= x <= x1 + m and y0 - m <= y <= y1 + m


def edges(z):
    if is_poly(z):
        p = z["pts"]
    else:
        x0, y0, x1, y1 = bbox(z)
        p = [[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
    return [(p[i], p[(i + 1) % len(p)]) for i in range(len(p))]


def seg_dist(px, py, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L2 = dx * dx + dy * dy
    t = 0 if L2 == 0 else max(0, min(1, ((px - a[0]) * dx + (py - a[1]) * dy) / L2))
    return math.hypot(px - a[0] - t * dx, py - a[1] - t * dy)


def zrank(e):
    k = kind(e)
    if k == "sym": return 10
    if k == "pipe": return 8
    if k == "open": return 6
    return ZORDER.get(e["type"], 5)


def validate(plan):
    errors, warnings = [], []
    E, W = errors.append, warnings.append
    if isinstance(plan, list):
        plan = {"elements": plan}
    els = plan.get("elements")
    if not isinstance(els, list):
        return ["No 'elements' array"], []
    ids = set()
    for e in els:
        if e.get("type") in LEGACY:
            e["type"] = LEGACY[e["type"]]
        t, i = e.get("type"), e.get("id")
        tag = f"#{i} {t}"
        if t not in TYPES:
            E(f"{tag}: unknown type (the editor would turn it into a text note)")
            continue
        if i in ids:
            E(f"{tag}: duplicate id")
        ids.add(i)
        k = kind(e)
        if k == "zone" and not is_poly(e) and not all(isinstance(e.get(f), (int, float)) for f in ("x", "y", "w", "h")):
            E(f"{tag}: zone needs numeric x, y, w, h (or pts)")
        if k == "zone" and not is_poly(e) and (e.get("w", 1) <= 0 or e.get("h", 1) <= 0):
            E(f"{tag}: zone with zero or negative size")
        if k == "pipe" and not (isinstance(e.get("pts"), list) and len(e["pts"]) >= 2):
            E(f"{tag}: pipe/cable needs pts with at least 2 points")
        if k == "open" and not all(isinstance(e.get(f), (int, float)) for f in ("x", "y", "w")):
            E(f"{tag}: opening needs x, y, w")
        if k == "sym" and not all(isinstance(e.get(f), (int, float)) for f in ("x", "y")):
            E(f"{tag}: symbol needs x, y")
        if e.get("fill"):
            W(f"{tag}: 'fill' is set. Keep default colours unless the user asked for one")
    if errors:
        return errors, warnings
    if plan.get("nextId") is not None and ids and plan["nextId"] <= max(x for x in ids if isinstance(x, (int, float))):
        W("nextId is not greater than the highest id (the editor will fix it on load)")

    zones = [e for e in els if kind(e) == "zone"]
    order = sorted(zones, key=lambda z: (zrank(z), -area_px(z)))
    for a_i, a in enumerate(order):
        ax0, ay0, ax1, ay1 = bbox(a)
        for b in order[a_i + 1:]:
            bx0, by0, bx1, by1 = bbox(b)
            if (ax0, ay0, ax1, ay1) == (bx0, by0, bx1, by1):
                E(f"zones #{a['id']} and #{b['id']} are exactly stacked: one hides the other")
            elif b["type"] != "garden" and bx0 <= ax0 and by0 <= ay0 and bx1 >= ax1 and by1 >= ay1:
                E(f"zone #{b['id']} {b['type']} is drawn above #{a['id']} {a['type']} and fully covers it. "
                  f"Fix the geometry or the type (a contained zone must be smaller and of equal or higher z-order)")
    rooms = [z for z in zones if z["type"] in ("room", "garage") and not is_poly(z)]
    for i, a in enumerate(rooms):
        for b in rooms[i + 1:]:
            ox = min(a["x"] + a["w"], b["x"] + b["w"]) - max(a["x"], b["x"])
            oy = min(a["y"] + a["h"], b["y"] + b["h"]) - max(a["y"], b["y"])
            if ox > 1 and oy > 1 and ox * oy / SCALE ** 2 > 0.1:
                W(f"rooms #{a['id']} '{a.get('label', '')}' and #{b['id']} '{b.get('label', '')}' overlap by {ox * oy / SCALE ** 2:.1f} m2 (rooms should be adjacent)")

    for e in els:
        t, k = e["type"], kind(e)
        if k == "sym" and TYPES[t]["layer"] != "deco" and t != "note":
            if not any(point_in_zone(z, e["x"], e["y"]) for z in zones):
                W(f"#{e['id']} {t} at ({e['x']}, {e['y']}) is outside every room or area")
        if k == "open":
            cx, cy = e["x"] + e["w"] / 2, e["y"] + 6
            d = min((seg_dist(cx, cy, p, q) for z in zones for p, q in edges(z)), default=1e9)
            if d > 12:
                W(f"#{e['id']} {t} is not on a wall (nearest edge {d / SCALE:.2f} m away)")
        if t.startswith("cable") and not e.get("spec"):
            W(f"#{e['id']} {t}: cable without spec (type and cross-section, e.g. 3G2.5)")

    wet = {"sink", "basin", "wc", "shower", "bathtub", "washer", "dishwasher"}
    drains = [e for e in els if e["type"] == "pipeDrain"]
    wps = [e for e in els if e["type"] in wet]
    if drains:
        for w in wps:
            if not any(math.hypot(q[0] - w["x"], q[1] - w["y"]) < 2 * SCALE for d in drains for q in d["pts"]):
                W(f"#{w['id']} {w['type']}: no drain pipe ends within 2 m")
    return errors, warnings


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    plan = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    errors, warnings = validate(plan)
    if "--json" in argv:
        print(json.dumps({"errors": errors, "warnings": warnings}, indent=1))
    else:
        for m in errors:
            print("ERROR   " + m)
        for m in warnings:
            print("WARNING " + m)
        n = len(plan["elements"] if isinstance(plan, dict) else plan)
        print(f"\n{n} elements, {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
