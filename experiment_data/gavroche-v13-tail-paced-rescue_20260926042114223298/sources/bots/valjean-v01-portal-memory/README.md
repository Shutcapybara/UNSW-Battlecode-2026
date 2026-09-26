# valjean-v01-portal-memory

Lineage: **valjean** (Claude, French line). Built from `monte_christo-v01-core`
with the Aramis intention vocabulary. Design, contract and full ledger:
[docs/valjean.md](../../docs/valjean.md).

Decision rule: `Q(objective) = objective_value(features) + executor_value(preview)`.
With every feature off it reproduces Monte Christo v01 exactly (54/54 identical
fixtures). Release settings are the `RELEASE` block in `params.py`:

* `blind_mem=1` — a portal exit outside vision is charged risk from remembered
  occupancy near the exit (0.15 floor, 0.5 if unseen recently, 1 if a body was
  seen near it within 12 rounds) instead of a full dragon value. Fixes dragons
  parking forever in portal boxes (dilemma/autarky).
* Sinbad v06 ports: arrival-only bed values, soft trap weight 5, strike search
  up to 6 steps, small-forager hunting up to length 8, crown threat reach 3.

Measured (native, both sides, 13 maps x 6 refs: ouroboros-v13, leviathan-v09,
hunter-v22, aramis-v02, sinbad-v06, avery-v08): **101-55** vs Monte Christo v01
**94-62** on the identical fixtures. Largest gains: dilemma 1-11 -> 7-5, autarky
2-10 -> 5-7; vs sinbad-v06 10-16 -> 16-10. Not yet run: judge sandbox on the
release source (an all-features dev build peaked at 81.6M CPU points on
stronghold), fresh-map validation (`tools/valjean/fresh`, frozen, unplayed).
Every other implemented feature is off (default = parity); see the ledger.
