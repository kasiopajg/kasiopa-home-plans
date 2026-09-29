#!/usr/bin/env python3
"""Render a plan JSON to SVG/PNG for visual checking, and print the editor's checks.

Usage:
    python scripts/render_plan.py PLAN.json OUT_PREFIX [--view all|house|elec|plumb|it] [--panel]

Writes OUT_PREFIX.svg and OUT_PREFIX.png (and OUT_PREFIX-panel.svg/.png with --panel).

Preferred path: headless Chromium through Playwright drives assets/editor.html, so the
render is pixel-identical to what the user sees, and the editor's own checks are printed.
Fallback (no Playwright): a simplified pure-Python SVG (zones, openings, networks and
symbol codes), converted to PNG with cairosvg when installed. Good enough to check
geometry, overlaps and positions, not a faithful rendering.
"""
import json
import os
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
EDITOR = SKILL_DIR / "assets" / "editor.html"
SCALE = 50


def parse_args(argv):
    pos = [a for a in argv if not a.startswith("--")]
    view = "all"
    if "--view" in argv:
        i = argv.index("--view")
        view = argv[i + 1]
        pos = [a for a in pos if a != view]
    return pos, view, "--panel" in argv


def render_browser(plan, prefix, view, panel):
    from playwright.sync_api import sync_playwright
    exe = None
    for cand in ("/opt/pw-browsers/chromium", os.environ.get("CHROMIUM_PATH", "")):
        if cand and Path(cand).exists() and Path(cand).is_file():
            exe = cand
    with sync_playwright() as p:
        kw = {"executable_path": exe} if exe else {}
        browser = p.chromium.launch(**kw)
        page = browser.new_page(viewport={"width": 1600, "height": 1000}, device_scale_factor=2)
        page.goto(EDITOR.as_uri())
        page.wait_for_function("window.KHP !== undefined")
        page.evaluate("s => { try{localStorage.clear()}catch(e){}; KHP.setState(s) }", plan)
        page.evaluate("v => KHP.preset(v)", view)
        svg = page.evaluate("() => KHP.svg()")
        checks = page.evaluate("() => KHP.checks()")
        outputs = [(prefix, svg)]
        if panel:
            psvg = page.evaluate("() => KHP.panelSVG()")
            if psvg:
                outputs.append((prefix + "-panel", psvg))
        for name, content in outputs:
            Path(name + ".svg").write_text(content, encoding="utf-8")
            page.set_content('<html><body style="margin:0;background:#fff">' + content + "</body></html>")
            page.locator("svg").first.screenshot(path=name + ".png")
            print(f"Wrote {name}.svg and {name}.png")
        browser.close()
    return checks


def esc(t):
    return str(t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def clean(elements):
    """Coerce geometry to numbers so a crafted plan cannot inject markup into the SVG."""
    out = []
    for e in elements:
        if not isinstance(e, dict):
            continue
        c = {"type": str(e.get("type", "")), "label": str(e.get("label", ""))}
        try:
            for f in ("x", "y", "w", "h", "rot"):
                if f in e:
                    c[f] = float(e[f])
            if isinstance(e.get("pts"), list):
                c["pts"] = [[float(q[0]), float(q[1])] for q in e["pts"]]
        except (TypeError, ValueError, IndexError):
            continue
        out.append(c)
    return out


def render_fallback(plan, prefix):
    els = clean(plan["elements"])
    xs, ys = [], []
    for e in els:
        pts = e.get("pts") or [[e.get("x", 0), e.get("y", 0)]]
        if "w" in e and not e.get("pts"):
            pts = pts + [[e["x"] + e["w"], e["y"] + e["h"]]]
        for q in pts:
            xs.append(q[0]); ys.append(q[1])
    x0, y0 = min(xs) - 60, min(ys) - 60
    W, H = max(xs) - x0 + 60, max(ys) - y0 + 60
    zones = [e for e in els if "w" in e and e.get("h", 12) != 12 and not e.get("pts") or (e.get("pts") and "w" in e)]
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {W} {H}" width="{int(W)}" height="{int(H)}" font-family="Helvetica">',
           f'<rect x="{x0}" y="{y0}" width="{W}" height="{H}" fill="#fff"/>']
    zones.sort(key=lambda z: -(z["w"] * z["h"]))
    for z in zones:
        stroke = "#1B1C1F" if z["type"] in ("room", "garage") else "#A6ABB2"
        sw = 5 if z["type"] in ("room", "garage") else 2
        if z.get("pts"):
            pa = " ".join(f"{q[0]},{q[1]}" for q in z["pts"])
            out.append(f'<polygon points="{pa}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>')
        else:
            out.append(f'<rect x="{z["x"]}" y="{z["y"]}" width="{z["w"]}" height="{z["h"]}" fill="none" stroke="{stroke}" stroke-width="{sw}"/>')
        out.append(f'<text x="{z["x"] + z["w"] / 2}" y="{z["y"] + z["h"] / 2}" text-anchor="middle" font-size="13" font-weight="600">{esc(z.get("label") or z["type"])}</text>')
    colors = {"pipeCold": "#1565C0", "pipeHot": "#C62828", "pipeDrain": "#6F747C", "pipeIrrig": "#2E7D32"}
    for e in els:
        if e.get("pts") and "w" not in e:
            pa = " ".join(f"{q[0]},{q[1]}" for q in e["pts"])
            out.append(f'<polyline points="{pa}" fill="none" stroke="{colors.get(e["type"], "#1B1C1F")}" stroke-width="3"/>')
        elif e.get("h") == 12 and "w" in e:
            out.append(f'<rect x="{e["x"]}" y="{e["y"]}" width="{e["w"]}" height="12" fill="#fff" stroke="#1B1C1F" transform="rotate({e.get("rot", 0)} {e["x"] + e["w"] / 2} {e["y"] + 6})"/>')
        elif "w" not in e and "x" in e:
            code = esc(e["type"][:4].upper())
            out.append(f'<circle cx="{e["x"]}" cy="{e["y"]}" r="9" fill="#fff" stroke="#1B1C1F" stroke-width="1.6"/>'
                       f'<text x="{e["x"]}" y="{e["y"] + 3}" text-anchor="middle" font-size="6.5">{code}</text>')
    out.append("</svg>")
    svg = "".join(out)
    Path(prefix + ".svg").write_text(svg, encoding="utf-8")
    print(f"Wrote {prefix}.svg (simplified fallback render)")
    try:
        import cairosvg
        cairosvg.svg2png(bytestring=svg.encode(), write_to=prefix + ".png", output_width=int(W) * 2)
        print(f"Wrote {prefix}.png")
    except ImportError:
        print("cairosvg not installed: PNG skipped (pip install cairosvg)")
    return None


def main(argv):
    pos, view, panel = parse_args(argv)
    if len(pos) != 2:
        print(__doc__)
        return 2
    plan = json.loads(Path(pos[0]).read_text(encoding="utf-8"))
    if isinstance(plan, list):
        plan = {"elements": plan}
    try:
        checks = render_browser(plan, pos[1], view, panel)
    except Exception as exc:  # no playwright or no browser available
        print(f"Browser render unavailable ({exc.__class__.__name__}: {exc}); using fallback renderer.")
        checks = render_fallback(plan, pos[1])
    if checks is not None:
        print(f"\nEditor checks ({len(checks)}):")
        for c in checks:
            print(f"  [{c['level']}] {c['message']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
