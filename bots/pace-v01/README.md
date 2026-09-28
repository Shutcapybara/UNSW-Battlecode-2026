# pace-v01 (lineage `pace`, claude/pace/session-01YYPUhB)

Host: `chaewon-y04-probe` (copied with attribution; yuna-v05 + atlas + newborn-neck fix + portal probe).
The only new policy is `pace.py` (+ 3 lines in `main.py`, 8 in `policy.py::split_option`, `pace_*` keys in `params.py`).
Arms: `pace-v01-nolimit` (survival checks off, opening production path extended to r60), `pace-v02` (per-map curve via
atlas name), `pace-v03` (v01 + no pocket-farm discount to r250). Findings: `docs/findings/2026-09-29-pace-v01.md`.

**Result:** 360 exact pairs vs host (10 live maps × 2 sides × seeds 1–3 × 6 opponents, unswbc 1.2.2): **−0.008**
(45 better / 48 worse, p 0.84); compact +0.049, open −0.046. Pace attainment unchanged (u100 13 compact / 18 open).

Six-line report
- **Strategy:** λ_unit via a unit-pace controller against the corpus class curve (compact 6/9/18/80, open 6/11/19/100
  for u25/u50/u100/t250); hold production when ≥ 3 units ahead from r60; food ×1.3 below the per-dragon r250 share.
- **Execution:** one option changed (`produce`): +1.5 split value per missing unit (cap 6), granted only when the child
  has ≥ 6 cells of room, no enemy head reaches the child or parent head, and the parent pocket is not a trap. Activation:
  ACT:pace+ 9.4 per game in r0–100, ACT:pace- 469 per game. The push is inert (the host splits anyway); the hold is what changes games.
- **Implementation:** metered, 4 fixtures vs sinbad-v07: zero faults, zero MC_ERROR. 1.2.2 max 70.2/70.2/71.2/65.4 M,
  p99 60.5/58.0/60.3/54.0 M; 1.0.0 max 69.8/68.9/79.4/61.7 M, p99 59.3/56.8/61.0/54.4 M (Schooltime A, Portals B,
  Slithery A, Trauma B). **p99 misses the < 60 M gate by ≤ 1.0 M on Schooltime/Slithery**; this is host cost (child boot turns with the atlas load; pace.update is O(1)).
- **State:** none added (the controller reads UNIT_COUNT, round, map size/atlas name, own length).
- **Messaging:** none added.
- **Momentum:** none added. Constraint cost (nolimit vs v01, seed 1, 120 pairs): +0.008 (8/7) — nothing measurable.
