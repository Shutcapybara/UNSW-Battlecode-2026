# Porthos x05: portal-recon executor (E2) and objective-level candidates (C2)

Parent: `bots/porthos-x03-swarm`.  x05 extends ONLY the candidate/executor
side of SCOUT; policy weights, target search, state, radio and every other
executor are frozen, so **x03 vs x05 isolates the executor/candidate change**
(the executor comparison of this cycle).

## The change

An unpaired portal's exit is unknown space: the target search cannot route
through it and values only adjacent dives.  x05 adds a deliberate
reconnaissance objective:

- **Candidates (INTENTIONS_VERSION 2, dependency C2).**  `recon_portals`
  probes for unpaired portals within `recon_reach` optimistic steps and
  nominates the portal CELL — a map object, never a compass direction.
  Gated hunter-style: forager role, expendable length
  (`recon_min_len..recon_max_len`), team can spare a scout (`recon_units`),
  big enough map (`recon_min_area`), early enough to use the information
  (`recon_until`), and only when the target search finds nothing better
  than a near unseen tile (`recon_tval` — the search's own in-range dive
  nominations score higher and keep recon off, so recon never duplicates
  the legacy dive).
- **Executor (EXECUTORS_VERSION 2, E2).**  `_scout_recon` self-routes: a
  bounded reverse distance field to the nominated cell, the surviving
  first step on a shortest route, and — standing on the portal cell — the
  dive itself, predicted honestly as `dive` (unknown landing).  Status is
  `active` while approaching, `completed` on the dive; an unavailable route
  falls back with `recon-route-unavailable`.  `preview_recon` is the
  bounded executor preview the policy consults; it commits nothing.
- **Decision (POLICY_VERSION 3).**  One added branch scores recon from the
  executor preview: `recon_val x gamma^steps + recon_info_w x unseen
  fraction of the portal's sector - p_dive x V(me)/2`.  Every other
  candidate scores exactly as P0.

After a dive, `world._learn` sees the exit's edges and pairs the portal;
`share_portals` radio then broadcasts the pairing (protected traffic in
x03's reservation), so one scout's dive upgrades the whole team's geometry.

## Frozen from x03

`protocol.py`, `world.py`, `tactics.py`, `roles.py`, `targets.py`,
`comms.py`, `density.py`, `swarm.py`, `radio.py`, `diagnostics.py`,
`risk_features.py`; P0 branches of `decision.py`; E0 executors for
gather/attack/retreat/feed_ally/reproduce.

## Verification

- `tests/test_porthos_swarm.py`: recon gating (role, length, units, map
  size, target value), objective-shaped candidates (cell target, integer
  arg), self-routing and dive completion, blocked-route fallback still
  legal, preview purity, executor record interface.
- Measured comparisons: `docs/porthos-lineage.md` cycle-2 records.

## Divergence record vs x03

Intentional: recon candidates appear when the probe fires and may be
selected; everything else byte-identical.
