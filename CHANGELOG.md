# Changelog

## 2.0.0 (2026-09-29)

First open-source release, renamed from `plans-maison-reseaux` to `kasiopa-home-plans`.

- Skill instructions rewritten in English; Claude adapts to the user's language and country.
- All former runtime patches are now built into `assets/editor.html`: area-based z-order, plot without fill, extended openings (double window, French doors, sliding door, gates, open passage), sanitary fixtures, junction box, auto-adjust of neighbouring rooms, polygon rooms, wall dragging, undo/redo, resizable openings, target areas view.
- Editor UI in English, neutral design, no external fonts, works fully offline.
- New elements: hob, EV charger, sensor, alarm panel, smoke detector, irrigation line, text note.
- Electrical standard per plan (IEC, NF C 15-100, REBT, BS 7671) driving the panel diagram and circuit limits.
- Built-in checks in the Overview, CSV export, element search, smart relay wiring diagram.
- Plan format v2 with `meta` (id, rev, title, level, standard, lang); browser storage per plan and revision, so a new delivery is never hidden by an old saved copy.
- v1 plans with French type identifiers load unchanged.
- New scripts: `build_editor.py`, `validate_plan.py`, `render_plan.py`. References split into `references/`.
- Security: every field of a loaded or embedded plan is type-checked before use (no markup or script injection from a crafted plan file), CSV export neutralises spreadsheet formulas, embedded plan data is escaped.
