# Porthos x03: swarm state/radio layer (matched control for the x04 feature comparison)

Parent: `bots/porthos-x02-intentions`.  x03 adds the shared density evidence
layers and the v2 feature construction, with **policy P0 and executors E0
frozen**: behaviour differs from x02 only through sonar packet content
(what allies hear changes what they know).  This is the state/radio control
the x04 (policy) and x05 (executor) experiments are measured against.

## What changed (communication v2, state v2, features v2)

- `comms.py` adds two packet types in the existing envelope (tag/type/payload/
  checksum unchanged):
  - `T_DENSITY = 6`: aggregate dragon COUNTS near a sensor centre
    (`x:6 y:6 round:9 ally:5 enemy:5 sender:13`), from the
    monte_christo-v07 radio study (x12-selected configuration).
  - `T_SWARM = 7`: directional visible LENGTHS in ONE sender-relative
    quadrant (`x:6 y:6 round:9 ally:4 enemy:4 quadrant:2 sender:13`).
    Senders rotate quadrants each turn; while any enemy is in evidence the
    enemy-heaviest quadrant is reported instead (scenario-tagged rotation).
    One sender's full directional picture arrives over four turns.
- `density.py` (from v07): EWMA local counts, per-sender report dedup with
  TTL, triangular-kernel `field(cell) -> (ally, enemy, confidence)` with a
  spatial-only denominator (no evidence = zero confidence, never proof of
  safety), `resource_factor(cell)` with the direct-vision bypass.  v07's
  `schedule()`/`trace()`/`gradient_score()` are not carried: message
  selection lives in `radio.py`, relay was not load-bearing (mc-x08), and
  the gradient tie-break was rejected (mc-x06).
- `swarm.py` (new): the same machinery per (sender, quadrant) for visible
  lengths.  `field(cell) -> (ally_len, enemy_len, confidence)`,
  `balance(a, e) = (e - a)/(a + e + damp)`, `gain(cell) = balance(cell) -
  balance(HEAD)` -- the game-relative directional feature.
- `radio.py`: `_reserve` adds both reports after the legacy content.  Idle
  rays first; only FOOD rays may be displaced -- CROWN, PREY and PORTAL are
  never displaced (portal pairings feed the topology line), and the split
  handoff stays a final override in `main.py`.  With one free ray the two
  reports alternate by round parity.
- `features.py` (FEATURES_VERSION 2) adds named facts, computed but UNUSED
  by P0: `phase` (round/500), `early` (round < aggro_until), `sat`
  (units/limit), `area_here`/`room_ratio` (topology-aware confinement from
  the credited flood fill), `counts`/`lengths` (density evidence at our
  head), per-candidate `child_room` (graded room at the child's head) and
  `swarm_gain` (balance change toward the post-move head).
- `main.py` wires `density.init/observe`, `swarm.init/observe` into the
  state stage.  Nothing else moves.

## Frozen from x02

`protocol.py`, `world.py`, `tactics.py`, `roles.py`, `targets.py`
(TARGETS_VERSION 1), `intentions.py` (v1), `decision.py` (POLICY_VERSION 1),
`executors.py` (EXECUTORS_VERSION 1), `diagnostics.py`, `risk_features.py`.

## Verification

- 20 scenario/contract checks: `tests/test_porthos_swarm.py` (packet
  round-trips and bounds, quadrant partition, dedup/TTL, field confidence,
  directional gain ordering, contact vs rotation reporting, ray reservation
  rules, feature keys/units, preview purity, executor interface, traces
  disabled, protocol byte-identical).
- Screens and judge budget: see `docs/porthos-lineage.md` cycle-2 records.

## Divergence record vs x02

Sonar packet content differs by construction (new report types on reserved
rays).  Any behavioural divergence flows only through what allies hear.
Measured comparisons live in the lineage doc.
