# Porthos x04: policy P1 — game-relative feature consumers

Parent: `bots/porthos-x03-swarm`.  x04 replaces ONLY the decision layer
(POLICY_VERSION 2); candidate construction, target search, previews,
weights defaults, state and executors are frozen, so **x03 vs x04 isolates
the policy feature change** (the feature comparison of this cycle).

## P1 adjustments over P0 (all directions from evidence, no compass constants)

1. **Early-saturation aggression** (`aggro_until`, `aggro_sat`,
   `aggro_relax`, `aggro_push`).  In the opening with a near-saturated team,
   extra dragons cannot become children, so their marginal value is the
   space they contest: the strike margin relaxes (even-ish trades become
   deliberate) and surviving forager moves gain `aggro_push x swarm_gain` —
   a push toward enemy LENGTH density.  The crown and feeders never push.
2. **Confinement-gated production** (`split_room_norm`, `split_room_floor`,
   `split_sat_w`).  A split's base value scales with the GRADED room
   available to both bodies (`child_room + parent_area`, floored): the same
   length in a pocket is not the same as in the open.  A scarce team
   (low saturation) values children more: `+ split_sat_w x (0.5 - sat)`.
3. **Density-discounted progress** (v07's selected hook).  The positional
   term toward the nominated target is multiplied by the target's
   `resource_factor`: pushing toward ally-crowded or enemy-contested cells
   is worth less; direct vision still takes precedence inside
   `resource_factor`.

## Frozen from x03

Everything except `decision.py`, one call-site line in `main.py`
(`choose(cands, tf, gf)` instead of `gf["threat"]`), and the P1 parameter
defaults in `params.py`.

## Verification

- `tests/test_porthos_swarm.py`: margin relaxation gating (early AND
  saturated AND forager), confinement scaling monotone with a floor,
  res_factor applied to the progress term exactly.
- Measured comparisons: `docs/porthos-lineage.md` cycle-2 records.

## Divergence record vs x03

Intentional: the three P1 consumers above.  Everything else byte-identical.
