# maelle-02-features

Maelle lineage (SF-1 Part 1 platform). Parent `maelle-01-nodevil`.

- `state.hpp` (new): per-dragon decayed grids over the cell index — `food` (+1 per pearl instance first known),
  `ally`/`enemy` (+1 per visible part per round), `threat` (+1 within Chebyshev `threat_k` of a visible enemy head),
  `death` (+1 where a visible dragon vanished and left a corpse pearl); `seen_age` read from `World::seen`.
  Read at query time through a (2·blur+1)² box mean and a saturation B/(B+s), so every feature is in [0, 1].
  Scalars: local pearl sparsity (pearls known inside the last search horizon), units in view, clock.
- `params.hpp` `Tun`: decays, scales, target weights `wt_*`, move weights `wm_*`, the L02 cap selector `capsel*`;
  all overridable at boot from `MAELLE_PARAMS="name=value,..."` (local games; the contest sandbox has no env).
- Target score: `value · γ^t · exp(Σ wt_i f_i(cell))`, with the value-bound prune scaled by `exp(Σ max(0, wt_i))`
  (exact). Move score: `existing + Σ wm_j g_j(final head)`.
- `MAELLE_DUMP=<file>`: per decision, the top-k target candidates' and every legal move's feature rows plus the
  choice (reader: `tools/maelle/dump.py`). Behaviour-neutral.

With every weight 0 the bot is behaviour-identical to `maelle-01-nodevil`: golden replay of maelle-01's transcripts
(schooltime A, portals B, trauma B, devil A, big_empty B; seed 1) 61,667 turns, 0 divergent; with the dump on,
0 divergent (trauma, schooltime).
