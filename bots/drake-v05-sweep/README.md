# drake-v05-sweep

**Lineage**: Drake. **Parent**: `bots/drake-v04-beacon/`.
No new borrowings (v04's credits apply).

## Hypothesis

v03/v04 capped the anti-dither visit penalty everywhere (`min(visits, 8)`),
which lets dragons linger near camps.  Map history suggested that hurt open
maps (v02's trauma record was 15-7 before the cap, 6-16 after): cap the
penalty only where camping matters (NC <= 650) and restore the full sweep
pressure on larger maps.

## Change from v04

One branch: the visit penalty is capped at 8 only on compact maps;
open maps pay `w_visit * visits[cell]` as in v02 and earlier.

## Measured results

Full frozen-roster screen (11 opponents x 11 maps x 2 sides = 242 games,
`drake-eval.toml`):
run `experiment_data/drake-v05-sweep_20260925121321478301`.

**Total: 85 W - 1 D - 156 L, score 0.353** — a small regression vs v04
(0.366).  trauma did not recover (6-16, same as v04), while kraken
(13 -> 10) and hunter-v14 (14 -> 13) slipped.  The visit cap was not the
trauma variable; the earlier v02->v03 trauma drop is more likely from the
nearest-food override or dispersion missions on mid maps.

**Not promoted.**  v04-beacon remains the Drake candidate.

## Sandbox / judge checks

Not separately run (the change removes a `min()` on open maps only);
v04's sandbox numbers (max 62.2M of 100M pts/turn) bound this variant.
