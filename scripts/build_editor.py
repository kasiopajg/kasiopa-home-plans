#!/usr/bin/env python3
"""Build a ready-to-open editor HTML file with a plan embedded.

Usage:
    python scripts/build_editor.py PLAN.json OUTPUT.html [--bump]

- Copies assets/editor.html and replaces the embedded plan block with PLAN.json.
- Legacy v1 plans (French type identifiers) are accepted: the editor migrates them on load.
- The browser keeps edits in localStorage under "khp:<meta.id>:<meta.rev>".
  --bump increments meta.rev (and writes it back to PLAN.json) so a new delivery
  is not hidden by an older copy saved in the user's browser.
"""
import json
import re
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
EDITOR = SKILL_DIR / "assets" / "editor.html"
BLOCK = re.compile(r'(<script type="application/json" id="embedded-plan">)(.*?)(</script>)', re.S)


def embed(editor_html: str, plan: dict) -> str:
    # "<" is escaped so no plan content can close the script block or open a comment in it
    data = json.dumps(plan, ensure_ascii=False, indent=1).replace("<", "\\u003c")
    if not BLOCK.search(editor_html):
        raise SystemExit("embedded-plan block not found in editor.html")
    return BLOCK.sub(lambda m: m.group(1) + "\n" + data + "\n" + m.group(3), editor_html, count=1)


def main(argv):
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 2:
        print(__doc__)
        return 2
    plan_path, out_path = Path(args[0]), Path(args[1])
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    if isinstance(plan, list):
        plan = {"elements": plan}
    meta = plan.setdefault("meta", {})
    meta.setdefault("id", re.sub(r"[^a-z0-9]+", "-", str(meta.get("title", "plan")).lower()).strip("-") or "plan")
    meta.setdefault("rev", 1)
    if "--bump" in argv:
        meta["rev"] = int(meta["rev"]) + 1
        plan_path.write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    html = embed(EDITOR.read_text(encoding="utf-8"), plan)
    out_path.write_text(html, encoding="utf-8")
    print(f"Wrote {out_path} (plan id={meta['id']} rev={meta['rev']}, {len(plan.get('elements', []))} elements)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
