# Other networks: plumbing, drainage, irrigation, pool, solar, IT, security

## Water supply

- Draw cold (`pipeCold`, blue) and hot (`pipeHot`, red) runs from the meter or the manifold to each point.
- `spec` gives material and diameter: `PEX 16`, `PEX 20`, `Multilayer 20`, `PPR 25`, `Copper 15`.
- Manifold (`manifold`) with one branch per point is the usual layout for PEX; stop valve (`valve`) after the meter.

## Drainage

- Every water point (sink, basin, WC, shower, bathtub, washing machine, dishwasher) needs a drain
  (`pipeDrain`, grey dashed) to a collector, then to the sewer or septic tank.
- Typical diameters: basin and shower 40 mm, bath and sink 40 to 50 mm, WC 100 to 110 mm, main collector 110 mm or more.
- Slope 1 to 3 cm per metre (2 cm/m is a safe default for 40 to 50 mm, 1 cm/m minimum for 100 mm and above).
- Inspection chamber (`drainpit`, called arqueta in Spain, regard in France) at every change of direction,
  junction and at the property boundary. Number them (`label`: IC1, IC2...).
- The validator flags water points with no drain ending within 2 m.

## Pits (buried networks)

`elecpit` (buried electrical), `waterpit` (water), `drainpit` (inspection). Very common in Spain
(arquetas) for every buried run and at every branch. Label and number them.

## Irrigation

- Controller (`irrigctrl`) near a tap or in the plant room; one solenoid valve per zone.
- Sprinklers (`sprinkler`) with head-to-head coverage; drip lines for beds. Lines as `pipeIrrig` (`spec`: `PE 25`, `PE 16 drip`).
- Put zone numbers and flow rates in `notes`.

## Pool

- Plant room (`techroom`) with pump and filter (`poolpump`); skimmer(s) to the pump; return inlets (`poolreturn`) back to the pool; main drain if any.
- Electrical: dedicated circuit and 30mA RCD; pool lights (`poollight`) in SELV 12 V through a safety transformer located outside the restricted zones.

## Solar

- Array as a `solar` zone (on the roof or ground), inverter (`inverter`) near the panel, battery (`battery`) next to it.
- DC isolator and surge protection on the DC side, dedicated RCD and breaker on the AC side, labelling on the panel.

## IT and telephony

- Network cabinet (`netcabinet`) near the consumer unit. Fiber entry (`fiber`) up to the cabinet.
- At least one RJ45 per main room (more in the office and behind the TV). Wi-Fi access points (`wifi`) wired back to the cabinet, ideally PoE.
- TV antenna and dish on the roof with coax back to the cabinet. Server or NAS near the cabinet with a dedicated socket.

## Security

- Cameras (`camera`) in corners, oriented toward accesses (use `rot`), PoE from the cabinet; intercom (`intercom`) at the gate.
- Alarm panel (`alarm`) near the entrance, sensors (`sensor`) at openings. Smoke detectors (`smoke`) in circulation areas and bedrooms (mandatory in France: at least one).
