# Plan JSON format (v2)

The editor, `scripts/validate_plan.py` and `scripts/build_editor.py` all read this format.
Scale: **1 m = 50 px**. Grid snap: **12.5 px = 25 cm**. Origin top-left, y grows downward.

```json
{
 "format": "kasiopa-home-plans",
 "version": 2,
 "meta": {"id": "villa-ground", "rev": 1, "title": "Villa Example", "level": "Ground floor",
          "standard": "REBT", "lang": "es"},
 "elements": [
  {"id": 1, "type": "room", "x": 0, "y": 0, "w": 250, "h": 200, "label": "Salon", "notes": "redo plaster"},
  {"id": 2, "type": "room", "x": 250, "y": 0, "w": 250, "h": 200, "label": "Cocina",
   "pts": [[250,0],[500,0],[500,200],[375,200],[375,100],[250,100]]},
  {"id": 3, "type": "door", "x": 102.5, "y": 194, "w": 45, "rot": 0},
  {"id": 4, "type": "socket", "x": 20, "y": 20, "circuit": "C2"},
  {"id": 5, "type": "cable3G", "pts": [[100,100],[300,100]], "spec": "3G2.5"}
 ],
 "nextId": 6
}
```

## meta

| field | meaning |
|---|---|
| `id` | stable plan identifier, lowercase-dashes. One per project and level. |
| `rev` | integer. The browser stores edits under `khp:<id>:<rev>`. Bump it (`build_editor.py --bump`) when you deliver a new version so an older browser copy does not hide it. |
| `title`, `level` | shown in the header, exports and diagrams. In the user's language. |
| `standard` | `IEC` (generic), `NFC15100` (France), `REBT` (Spain), `BS7671` (UK). Drives the panel diagram and the checks. |
| `lang` | ISO code of the user's language (information only; the editor UI is English). |

## Element kinds

| kind | geometry | notes |
|---|---|---|
| zone | `x, y, w, h` rectangle, or `pts` polygon (3+ corners). With `pts`, x/y/w/h is the bounding box. | Rooms, terraces, plot... Area is computed (shoelace for polygons). |
| open | `x, y, w, rot`; `h` is always 12. Centre = (x + w/2, y + 6). | Put the centre exactly on the wall: horizontal wall at Y gives `y = Y - 6`; vertical wall at X with `rot: 90` gives `x = X - w/2`. Door leaf and swing are on the negative-y side before rotation. |
| sym | `x, y, rot` (centre point) | Point symbols. `circuit` (e.g. `C3`) feeds the panel diagram. |
| pipe | `pts` polyline, 2+ points | Pipes and cables. Always fill `spec` on cables (`3G2.5`, `5G6`) and ideally on pipes (`PEX 16`, `PVC 110`). |

Optional on every element: `label` (free text, user's language), `notes` (free comment), `rot` (0, 90, 180, 270).
`fill` (hex colour) exists on zones but is reserved for an explicit user request.

## Rules for generated plans

1. Rooms are **adjacent, never stacked**: a shared wall is the same coordinate on both rooms.
2. The only legitimate container is the plot (`garden`, drawn without fill) and its sub-areas (path, terrace, pool, plant room). A contained zone must be smaller **and** of equal or higher z-order.
3. Z-order used by the editor: garden 0, path 1, terrace 2, pool/solar 3, garage/techroom 4, room 5, countertop 5.5, openings 6, pipes/cables 8, symbols 10. Within a level, larger zones are drawn first.
4. Openings sit on a wall (validator warns when an opening is more than 25 cm from any zone edge).
5. Every symbol except decor and notes sits inside a zone (the list view attaches it to the smallest zone containing it).
6. Ids are unique integers; `nextId` > highest id.
7. Keep 20 to 40 px between neighbouring symbols so labels stay readable; keep lights away from the upper part of large rooms, where the room label sits.

## v1 compatibility

Plans made with the first French version (types such as `prise`, `dcl`, `tableau`, `jardin`, `pipeEvac`) load unchanged: the editor and the validator map them to v2 identifiers (column "v1 alias" below). Unknown types become a `note` carrying the original type in its notes.

## All element types

| id | kind | layer | name | v1 alias |
|---|---|---|---|---|
| `room` | zone | structure | Room |  |
| `garage` | zone | structure | Garage |  |
| `countertop` | zone | structure | Countertop | plandetravail |
| `door` | open | structure | Door | porte |
| `slidingdoor` | open | structure | Sliding door | portecoul |
| `opening` | open | structure | Open passage | ouverture |
| `window` | open | structure | Window | fenetre |
| `window2` | open | structure | Double window | fenetredbl |
| `frenchdoor` | open | structure | French door | portefen |
| `frenchdoor2` | open | structure | Double French door | portefendbl |
| `terrace` | zone | ext | Terrace | terrasse |
| `garden` | zone | ext | Plot / garden | jardin |
| `pool` | zone | ext | Pool | piscine |
| `path` | zone | ext | Path / drive | allee |
| `techroom` | zone | ext | Plant room | localtech |
| `solar` | zone | ext | Solar panels | solaire |
| `gate1` | open | ext | Gate, single | portail1 |
| `gate2` | open | ext | Gate, double | portail2 |
| `slidinggate` | open | ext | Sliding gate | portailcoul |
| `socket` | sym | elec | Socket 16A | prise |
| `socket32` | sym | elec | Socket 32A | prise32 |
| `switch` | sym | elec | Switch | inter |
| `twoway` | sym | elec | Two-way switch | vv |
| `pushbutton` | sym | elec | Push button | bp |
| `ceilinglight` | sym | elec | Ceiling light | dcl |
| `walllight` | sym | elec | Wall light | applique |
| `spot` | sym | elec | Spotlight |  |
| `outdoorlight` | sym | elec | Outdoor light | eclext |
| `panel` | sym | elec | Consumer unit | tableau |
| `junctionbox` | sym | elec | Junction box | boitederiv |
| `elecmeter` | sym | elec | Electricity meter | linky |
| `doorbell` | sym | elec | Doorbell | sonnette |
| `ventilation` | sym | elec | Ventilation fan | vmc |
| `elecpit` | sym | elec | Electrical pit | arqelec |
| `cableL` | pipe | elec | Line conductor | cablePH |
| `cableN` | pipe | elec | Neutral conductor |  |
| `cablePE` | pipe | elec | Earth conductor | cableT |
| `cable2G` | pipe | elec | Cable 2G |  |
| `cable3G` | pipe | elec | Cable 3G |  |
| `cable4G` | pipe | elec | Cable 4G |  |
| `cable5G` | pipe | elec | Cable 5G |  |
| `boiler` | sym | elec | Boiler | chaudiere |
| `waterheater` | sym | elec | Water heater | chauffeeau |
| `oven` | sym | elec | Oven | four |
| `hob` | sym | elec | Hob |  |
| `washer` | sym | elec | Washing machine | lavelinge |
| `dishwasher` | sym | elec | Dishwasher | lavevaisselle |
| `fridge` | sym | elec | Fridge | frigo |
| `aircon` | sym | elec | Air conditioning | clim |
| `inverter` | sym | elec | PV inverter | onduleur |
| `battery` | sym | elec | Battery | batterie |
| `evcharger` | sym | elec | EV charger |  |
| `shelly` | sym | domo | Shelly |  |
| `sonoff` | sym | domo | Sonoff |  |
| `hub` | sym | domo | Smart home hub |  |
| `thermostat` | sym | domo | Thermostat |  |
| `sensor` | sym | domo | Sensor |  |
| `netcabinet` | sym | it | Network cabinet | coffretcom |
| `rj45` | sym | it | RJ45 outlet |  |
| `tvsocket` | sym | it | TV outlet | tvprise |
| `router` | sym | it | Router | box |
| `wifi` | sym | it | Wi-Fi access point |  |
| `camera` | sym | it | Camera |  |
| `intercom` | sym | it | Intercom | interphone |
| `alarm` | sym | it | Alarm panel |  |
| `smoke` | sym | it | Smoke detector |  |
| `tvantenna` | sym | it | TV antenna | antennetv |
| `satellite` | sym | it | Satellite dish |  |
| `fiber` | sym | it | Fiber entry | fibre |
| `server` | sym | it | Server / NAS | serveur |
| `watermeter` | sym | plumb | Water meter | cptreau |
| `gasmeter` | sym | plumb | Gas meter | gaz |
| `valve` | sym | plumb | Valve | vanne |
| `manifold` | sym | plumb | Manifold | nourrice |
| `waterpit` | sym | plumb | Water pit | arqeau |
| `drainpit` | sym | plumb | Inspection chamber | arqevac |
| `tap` | sym | plumb | Tap | robinet |
| `sink` | sym | plumb | Kitchen sink | evier |
| `basin` | sym | plumb | Washbasin | lavabo |
| `wc` | sym | plumb | WC |  |
| `shower` | sym | plumb | Shower | douche |
| `bathtub` | sym | plumb | Bathtub | baignoire |
| `irrigctrl` | sym | plumb | Irrigation controller | programmateur |
| `sprinkler` | sym | plumb | Sprinkler | asperseur |
| `poolpump` | sym | plumb | Pool pump / filter | pompefilt |
| `skimmer` | sym | plumb | Skimmer |  |
| `poolreturn` | sym | plumb | Pool return inlet | refoul |
| `poollight` | sym | plumb | Pool light | projpisc |
| `pipeCold` | pipe | plumb | Cold water pipe | pipeEF |
| `pipeHot` | pipe | plumb | Hot water pipe | pipeEC |
| `pipeDrain` | pipe | plumb | Drain pipe | pipeEvac |
| `pipeIrrig` | pipe | plumb | Irrigation line |  |
| `tree` | sym | deco | Tree | arbre |
| `shrub` | sym | deco | Shrub | arbuste |
| `plant` | sym | deco | Plant | plante |
| `flowers` | sym | deco | Flowers | fleur |
| `note` | sym | structure | Text note |  |