# yeji-s03-compactfield

**Lineage:** Yeji. **Parent:** `yeji-s02-mapfield`. **Status:** frozen; superseded by `yeji-s04-compactprior`.

Changes from s02:
- **CPU-cheap map prior.** `mapprior.py` (built by `tools/yeji/build_prior.py --compact`) stores edge kinds as bytes, portal ids, bed rates, zone rates and the bed field as constants. The map is recognised from the 112 edges of the first view (one exact candidate only); loading is slice copies. Schooltime turn 0: 57–62M in the sandbox (s02: > 100M, dead; no prior: 34–36M; the import alone ≈ 6M).
- **Bed field on compact maps only** (`field_compact_cells` 625, `w_field_open` 0).

Metered (unswbc 1.2.2 `--sandbox -v`, vs sinbad-v07-divecap): Schooltime as A max **74.3M**, p99 46.1M (5,569 turns, eliminated r375); Portals as B max **79.8M**, p99 57.9M (12,271 turns). Zero `exceeded`. Passes the 80M/60M local gate with no margin on Portals.

Panel (160 paired fixtures, seed 1): **0.481** (v10 0.494: −0.013, 20/22). By class: **compact 0.531** (v10 0.391, P 0.469), **open 0.448** (v10 0.562, P 0.573). The prior keeps its compact-map gain, but even without the field it costs open maps (Default −0.12, QoS −0.25, Slithery −0.19, Trauma −0.19 vs v10) → s04 uses the prior only on compact maps.

> **Out-of-sample caveat (added 29 Sep).** The map prior only fires on the ten public maps it was built from; tournament maps are out of sample, so on them this bot plays without it. The in-sample gains above are not evidence of tournament strength. Held-out evaluation: see `yeji-s06-onlinebeds`.
