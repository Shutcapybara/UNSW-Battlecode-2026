# drake-v08-density

**Lineage**: Drake. **Parent**: `bots/drake-v07-soft-missions/`.
No new borrowings; the density layer is Drake's own design.

## Hypothesis (user-suggested)

The messaging system should carry a smoothed territory model: EWMA
density maps of allied and enemy heads over space, an EWMA of own
position, transmitted constantly with timestamps and folded into
receivers' maps with the same decay.  Features from the maps (raw,
ally-minus-enemy) then shape targeting.  Halflife is a model choice to
validate, not assume.

## What was built

- **EWMA density maps** `dens_a`/`dens_e` per 8x8 zone (heads seen in
  vision bump +1; received packets fold in with age weights; values
  saturate at `dens_cap=8` so repeated sends give occupancy semantics
  instead of inflation).
- **Own-position EWMA** as a torus-safe vector average (`home_cell()`).
- **K_DENS packet** `[check 8 | kind 4 | round 9 | anchor 12 | (zone 6,
  ally 4, enemy 4) x2]`: team-salted checksum (foreign packets fail),
  round stamp bounds replay; anchor bumps the sender's ally presence.
- **Constant messaging**: all four rays fire every turn (sonar costs
  nothing beyond the batched write already made).
- **Gated features** (`dens_features`): zone_danger from the enemy map,
  waypoint de-congestion from the ally map, an ally-minus-enemy territory
  term for foragers (hunters inverted), an enemy-density hunter pull.

## Halflife validation (the clean experiment)

`dens_features=0` makes the layer passive, so halflife variants play
**byte-identical deterministic games** - only the smoothing differs.  On
default-vs-fry-v14 and big_empty-vs-ouroboros-v10 (2 games, 77,089
zone-round samples per variant):

| halflife e/a | enemy corr | enemy brier | ally corr | ally brier |
| --- | --- | --- | --- | --- |
| 40 / 90 | +0.280 | 0.418 | +0.261 | 0.551 |
| 20 / 45 | +0.327 | 0.341 | +0.290 | 0.530 |
| 10 / 25 | +0.408 | 0.247 | +0.321 | 0.508 |
| **5 / 12** | **+0.422** | **0.190** | **+0.367** | **0.463** |

Shorter is strictly better on both metrics: dragons move fast enough
that recent sightings dominate.  Defaults set to 5/12.

## Full-roster result: REGRESSION

286-game screen (11 opponents x 13 maps - two community maps,
autarky/dilemma, appeared mid-session):
run `experiment_data/drake-v08-density_20260925134231176555`.

**Total 76-1-209 (0.267); common 11-map subset 70-1-171 (0.291)**
vs v07's 0.370.  fry 16-6 -> 8-18, big_empty 2-20 -> 0-22.

Diagnosis: the ray schedule sent **two density packets and only one
self packet** (v07 sent ~two), starving the ally tracking that crown
coordination, feeding and de-congestion depend on; and zone_danger on a
5-round memory was too twitchy for avoidance (the validated halflife
predicts *sightings*, not *safe routing*).  Fix in drake-v09.

## What this version established

- The halflife validation methodology (passive layer on deterministic
  games) works and gives a clean answer: 5/12.
- Constant messaging is right; the open question is slot allocation,
  not whether to send.
- Prediction-optimal smoothing and decision-useful smoothing are
  different objectives - zone_danger wants the longer memory.

## Sandbox / judge checks

Density adds O(zones) decay per turn, one packet pack, and O(1) folds;
bounded by the v07 family measurement (max 59.5M of 100M pts/turn).
