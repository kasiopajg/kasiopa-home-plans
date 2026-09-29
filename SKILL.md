---
name: kasiopa-home-plans
description: Create, digitize or edit 2D home floor plans and their technical networks, delivered as an interactive offline HTML editor. Covers rooms, doors and windows, electrical points and cables, consumer unit single-line diagrams (NF C 15-100, REBT, BS 7671, IEC), smart home (Shelly, Sonoff), IT and security, plumbing, drainage and inspection chambers, irrigation, pool, solar, kitchen and decor. Use for any home plan, domestic wiring, panel, plumbing or network layout request, or when the user shares a photo or hand-drawn sketch of a plan. Works in the user's language; triggers also on plan maison, schéma électrique, tableau électrique, plano de vivienda, cuadro eléctrico, fontanería, arqueta, Grundriss, pianta, impianto elettrico.
license: MIT
---

# Kasiopa Home Plans

Turn a description, a photo or a hand sketch of a home into a clean 2D plan with its technical
networks, then deliver it as a single offline HTML editor the user can keep editing, plus
derived outputs (panel diagram, element list, PNG/SVG). Open source, MIT, by Damien Moras, [kasiopa.com](https://kasiopa.com).

## Speak the user's language

Detect the user's language from their messages and use it for **everything they read**:
questions, explanations, room and element labels (`label`), notes, `meta.title`, diagram captions
you write yourself. Use their local vocabulary (arqueta, tableau, consumer unit): see
`references/glossary.md` for FR, ES, DE, IT and EN. The JSON type identifiers and the editor
interface stay in English. Pick the electrical standard from the country, not the language
(a French speaker living in Spain gets REBT).

## Safety and scope

Plans and diagrams from this skill are working documents for understanding, planning and talking
to professionals. Say so once, briefly, when you deliver electrical or gas content: fixed wiring,
panels and gas must be designed, installed and certified by qualified people under local rules.
Never present indicative ratings as a compliant design.

## Files

| Path | Role |
|---|---|
| `assets/editor.html` | The canonical editor. Self-contained, offline, no dependencies. Never rewrite it from memory: copy it or build from it. |
| `assets/example-plan.json` | Complete example (house, plot, pool, all networks). Good starting point and format reference. |
| `scripts/build_editor.py PLAN.json OUT.html [--bump]` | Embeds a plan into a copy of the editor. |
| `scripts/validate_plan.py PLAN.json` | Structure, z-order, overlaps, openings on walls, symbols outside rooms, cables without spec, drains. Exit 1 on error. |
| `scripts/render_plan.py PLAN.json OUT [--view elec] [--panel]` | PNG/SVG render through headless Chromium (identical to the editor) and the editor's own checks; simplified fallback without a browser. |
| `references/json-format.md` | Full JSON format, geometry rules, all element types, v1 aliases. |
| `references/electrical.md` | Standards tables per country, panel composition, colours, smart home. |
| `references/networks.md` | Plumbing, drainage, pits, irrigation, pool, solar, IT, security. |
| `references/glossary.md` | Multilingual terminology. |

Read a reference file when the task touches its topic; do not load all of them by default.

## Workflow

### 0. Scope first (short)

Ask only what you cannot infer, in the user's language, at most 4 questions per round and 2
rounds. Use the structured question tool when the environment has one, otherwise plain text.

Round 1: goal (renovation, new build, brief for an electrician or plumber, sale or rental,
documenting what exists, smart home project); house or flat and country (sets the standard);
whole home or some rooms or networks; starting point (sketch or photo upload, description, or
the example plan to modify).

Round 2 if needed: number of levels (one plan per level); exterior (plot, terrace, pool,
irrigation, buried networks, solar); networks wanted (electrical only, smart home, IT and
cameras, plumbing and drainage, irrigation); supply and special equipment (single or three
phase, gas or induction, boiler or electric water heater, air conditioning, EV charger,
PV with or without battery, pool).

If the user has not thought of it, offer the sketch route: a freehand drawing with room names
and one or two dimensions is enough.

### 1. Digitize a photo or sketch

1. Read the image carefully: rooms, walls, doors, windows, drawn equipment, handwritten notes and dimensions.
2. **Number everything**: rooms P1, P2..., elements E1, E2... Render a quick annotated version
   (numbers on each zone and element) and show it.
3. For each uncertain number ask a **concrete, located** question with likely options:
   "P4, the small room between bedroom P2 and bathroom P3: WC, dressing or cupboard?"
4. Dimensions: use visible dimensions; otherwise estimate from proportions and ask for **one** reference dimension.
5. Produce the plan JSON, render a control PNG, list what you assumed.
6. Describe the plan back room by room (with the numbers) and get confirmation before deriving networks and diagrams.

### 2. Build the plan JSON

Start from `assets/example-plan.json` or from scratch following `references/json-format.md`. Essentials:

- 1 m = 50 px, snap 12.5 px (25 cm). Set `meta`: `id` (stable per project and level), `rev`, `title`, `level`, `standard`, `lang`.
- Rooms are **adjacent, never stacked**: shared walls use identical coordinates. L-shaped or
  irregular rooms use `pts`.
- The plot (`garden`) is the only container; it has no fill. Never set `fill` unless the user asks.
- Openings are centred on a wall (`y = wallY - 6`; vertical wall: `rot: 90`, `x = wallX - w/2`).
- Every electrical point gets a `circuit` when networks are in scope; every cable gets a `spec`
  (`3G2.5`); pipes get material and diameter (`PEX 16`, `PVC 110`). Put models and remarks in `notes`.
- Apply the conventions of `references/electrical.md` (points per circuit, dedicated circuits,
  RCD types) and `references/networks.md` (a drain for every water point, a pit at every change
  of direction, cameras toward accesses...).
- Leave room around symbols (20 to 40 px) and keep the upper part of large rooms free for the room label.

### 3. Validate and look at it

```bash
python scripts/validate_plan.py plan.json          # must end with 0 error
python scripts/render_plan.py plan.json out/plan --panel
```

Fix every error. Treat warnings as questions: fix them or tell the user why they stay.
Then **look at the PNG** before delivering: overlapping labels, symbols outside rooms, odd geometry.
Re-check against the standard: points per circuit, cross-section vs breaker, every circuit on the
panel, drains and pits, neutral available for smart relays.

### 4. Deliver

```bash
python scripts/build_editor.py plan.json out/plan-editor.html          # first delivery
python scripts/build_editor.py plan.json out/plan-editor.html --bump   # any later version
```

`--bump` increments `meta.rev`: the browser keeps edits under `khp:<id>:<rev>`, so a new version is
never hidden by an older copy saved in the user's browser. Deliver the HTML (and the JSON, PNG and
panel SVG when useful) the way the environment allows: file download, artifact or published page.
Explain in two or three lines how to use it (see below), in the user's language.

When the user sends back an edited JSON (Save JSON in the editor), treat it as the new source of
truth: validate, apply the requested changes, bump, rebuild.

### 5. Derived outputs on request

- **Panel single-line diagram**: editor Diagrams button, or `render_plan.py --panel`. Follows `meta.standard`.
- **Wiring of an arrangement**: two-way switching and smart relay are built into the editor;
  for others (intermediate switch, latching relay, switched socket, three-phase) draw an SVG with
  coloured conductors, sections and a legend, or use Python `schemdraw` for schematics.
- **Element list and quantities**: editor List (with CSV export) and Overview (areas, counts,
  cable and pipe lengths, circuits with limits, checks).
- **Area targets**: editor Areas view scales rooms to target m².
- **Views per trade**: All, House, Electrical, Plumbing, IT / Security (`--view` in `render_plan.py`).

## Editor cheat sheet (to explain to the user)

Palette on the left (search box, views, layers), properties on the right, plan in the middle.
Click to select, drag to move, double-click to rename, R to rotate, Delete to remove,
Cmd/Ctrl+D to duplicate, arrows to nudge 25 cm, Cmd/Ctrl+Z / Shift+Z to undo and redo.
On a selected room: the filled square on a wall moves that wall (neighbours follow when
Auto-adjust is ON), the + adds a corner for L-shapes, round corner handles move and
double-click removes a corner. On a pipe or cable: hollow squares add bends. Save JSON / Load JSON
to exchange with Claude, SVG and PNG to share, everything also auto-saved in the browser.

## Final checklist

- [ ] Language: labels, notes, title and explanations in the user's language
- [ ] `validate_plan.py`: 0 error, warnings handled
- [ ] PNG looked at: no hidden element, no unreadable overlap
- [ ] Circuits: point counts and sections within the standard, each circuit on the panel, dedicated circuits where required
- [ ] Networks: every water point drained, pits at changes of direction, cameras oriented, neutral checked for smart relays
- [ ] `meta.rev` bumped for any new version of an existing plan
- [ ] Short safety note given with electrical or gas content
