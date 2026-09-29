# Electrical reference

Indicative values for domestic installations. Standards are revised regularly: when figures matter
(quote, works, inspection) and web search is available, check the current edition, and always
tell the user that the final design and the works belong to a qualified electrician.

The editor applies the table of the standard chosen in plan settings (`meta.standard`) to the
panel diagram and to the per-circuit point limits.

## Choosing the standard

| Country | Standard | `meta.standard` | Who signs off |
|---|---|---|---|
| France | NF C 15-100 | `NFC15100` | Consuel certificate when a new or renewed supply connection is needed |
| Spain | REBT, ITC-BT-25 for dwellings | `REBT` | Instalador autorizado, Certificado de Instalación Eléctrica (boletín) |
| UK | BS 7671 (IET Wiring Regulations, 18th edition and amendments) | `BS7671` | Part P notification in England and Wales, Electrical Installation Certificate |
| Elsewhere | IEC 60364 family, then local rules | `IEC` | Local licensed electrician |

## France, NF C 15-100

| Circuit | Breaker | Section | Limit |
|---|---|---|---|
| Lighting | 10 or 16A | 1.5 mm² | 8 light points |
| Sockets | 16A | 1.5 mm² | 8 sockets |
| Sockets | 20A | 2.5 mm² | 12 sockets |
| Kitchen worktop sockets | 20A | 2.5 mm² | 6, dedicated circuit |
| Washing machine, dishwasher, oven, dryer, freezer | 20A | 2.5 mm² | 1 appliance per circuit |
| Hob / cooker | 32A | 6 mm² | dedicated, RCD type A |
| Water heater | 20A + day/night contactor | 2.5 mm² | dedicated |
| Boiler (supply and control) | 10 to 16A | 1.5 mm² | dedicated |
| Ventilation (VMC) | 2A | 1.5 mm² | dedicated |
| Doorbell | 2A via 230/8-12V transformer | 1.5 mm² | |
| PV inverter | per inverter, typically 20 to 32A | 4 to 6 mm² | dedicated 30mA RCD type A, SPD, DC isolator |
| EV charger 7.4 kW | 40A | 10 mm² | dedicated 30mA RCD type A or F (or charger with DC 6mA detection) |

Panel: AGCP (utility main breaker, 500mA) first, then at least two 30mA RCDs (type A for hob,
washing machine, EV and PV), surge protector depending on the lightning zone, latching relay
when push buttons are used, day/night contactor, busbars. At least one smoke detector (DAAF) per dwelling.
Bathrooms: volumes 0 to 3 restrict what can be installed near a bath or shower.

## Spain, REBT ITC-BT-25

| Circuit | Use | Breaker | Section | Max points |
|---|---|---|---|---|
| C1 | Lighting | 10A | 1.5 mm² | 30 |
| C2 | General sockets and fridge | 16A | 2.5 mm² | 20 |
| C3 | Cooker and oven | 25A | 6 mm² | 2 |
| C4 | Washing machine, dishwasher, water heater | 20A (or 3 x 16A, 2.5 mm²) | 4 mm² | 3 |
| C5 | Bathroom and kitchen sockets | 16A | 2.5 mm² | 6 |
| C6 / C7 | Extra C1 / C2 (more than 30 lights, more than 20 sockets or over 160 m²) | as C1 / C2 | | |
| C8 | Electric heating | 25A | 6 mm² | |
| C9 | Air conditioning | 25A | 6 mm² | |
| C10 | Dryer | 16A | 2.5 mm² | 1 |
| C11 | Home automation and security | 10A | 1.5 mm² | |
| C12 | Extra C3, C4 or C5 | | | |
| C13 | EV charging (ITC-BT-52) | per charger | | dedicated |

Electrification grade: basic (5,750 W at 230 V, circuits C1 to C5) or high (9,200 W; required
above 160 m² or with C8, C9, C10 or more circuits). Panel: IGA main breaker, then 30mA RCDs,
at least one RCD per five circuits. Colours: line brown, black or grey; neutral blue; earth
green/yellow. Bathrooms follow ITC-BT-27 volumes. Buried networks use arquetas (pits).

## UK, BS 7671

| Circuit | Protective device | Cable (twin and earth, typical) | Notes |
|---|---|---|---|
| Lighting | 6A | 1.0 or 1.5 mm² | |
| Ring final (sockets) | 32A | 2.5 mm² | floor area up to 100 m² |
| Radial (sockets) | 20A / 32A | 2.5 / 4 mm² | up to 50 / 75 m² |
| Cooker | 32 to 40A | 6 to 10 mm² | cooker control unit |
| Electric shower | 40 to 45A | 10 mm² | |
| Immersion heater | 16A | 2.5 mm² | |
| Boiler | fused spur 3A | 1.5 mm² | |
| EV charger | 32A | 6 to 10 mm² | RCD type A plus 6mA DC detection, PEN fault protection |

30mA RCD protection on socket circuits up to 32A, on lighting circuits and on cables buried less
than 50 mm in walls; RCBOs are common. Notifiable work in England and Wales goes through Part P.

## Generic (IEC 60364)

Without a national standard, the editor uses: lighting 10A / 1.5 mm² / 8 points; sockets 16A /
2.5 mm² / 12; cooking 32A / 6 mm²; dedicated appliances 20A / 2.5 mm²; EV 32A / 6 mm²; several
30mA RCDs with type A on cooking, washing machine, EV and PV.

## Cable notation and colours

`3G2.5` means 3 conductors including earth, 2.5 mm² each (G = with green/yellow earth, X = without).
Harmonised colours: line brown (also black, grey; red on older French installations), neutral blue,
earth green/yellow. On wiring diagrams: strappers orange, switched line violet.
Always fill `spec` on traced cables.

## Smart home (Shelly, Sonoff and similar)

- The module goes behind the switch or in the junction box of the controlled point. Put its circuit
  in `circuit` and the exact model in `notes`.
- Check the neutral at the control point. Without neutral use a no-neutral variant (e.g. Shelly 1L)
  and check the minimum load (LED lamps may need a bypass).
- Hub or gateway near the router or network cabinet; connected thermostat on the boiler or heat pump control.
- The editor's Diagrams view includes a typical wiring for a relay behind a switch.

## Diagrams you can produce

1. **Panel, single-line**: from the plan's circuits (editor Diagrams, or `render_plan.py --panel`).
2. **Wiring of one arrangement** (two-way switching, intermediate switching, latching relay, switched socket,
   smart relay): SVG with coloured wires, cross-sections and a legend. Two-way and smart relay are built in.
3. **Schematic** for anything more technical: Python `schemdraw` (`pip install schemdraw`), export SVG.
