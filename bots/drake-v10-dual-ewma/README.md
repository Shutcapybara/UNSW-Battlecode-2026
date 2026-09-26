# drake-v10-dual-ewma

**Lineage**: Drake. **Parent**: `bots/drake-v09-density-tuned/`.
No new borrowings.

## Hypothesis (user-suggested)

Add time as an explicit variable in the decision function, and track
TWO EWMAs per signal: broadcast the SHORT one; build the LONG one from
the same evidence (vision + received short broadcasts) with slower
decay, giving a stable occupancy baseline.  Use both as features -
difference (surge), log-ratio (multiplicative surprise) - and shape
their weights by game time.

## Implementation

- `densL_a`/`densL_e` long maps (halflifes 40/90 initially), folded in
  `dens_update` and `dens_hear` exactly like the short maps.
- Features: `surge = short - long` (forager avoidance of active zones),
  `ratio = log2((short+.25)/(long+.25))` (hunter pull, clamped +-2),
  territory term switched to the LONG maps.
- Time variables: `t01` ramps danger avoidance 0.6 -> 1.4 over r60-300;
  `hunt_t` fades hunter pulls to 0 over r300-420; territory weight grows
  with t01.
- Validation log extended with long-map predictions (EL/AL rows).

## Measured result: REGRESSION

286-game screen: run
`experiment_data/drake-v10-dual-ewma_20260925144135103117`.
**Common 11-map subset 75-1-166 = 0.312** (v09: 0.366, v07: 0.370).

big_empty collapsed to **1-0-21** (v09: 9-0-13) - the dual/time package
broke exactly the matchup the density layer had fixed.  Gains elsewhere:
kraken 17-1-8 (best ever), hunter-v20 +1, autarky (new map) 11-0-11.

## Diagnosis

1. **Saturation**: with halflifes 40/90 on a 500-round game, the long
   maps pin at the cap almost everywhere allies/enemies have been for
   90+ rounds; the territory term (densL_a - densL_e) loses spatial
   contrast and degenerates into uniform noise.
2. **Late over-avoidance**: the 0.6 -> 1.4 danger ramp makes late
   foragers cede enemy-adjacent food zones during the crown race -
   precisely when the r300+ economy decides the ouroboros duels.

Both mechanisms are structural, not noise: v11 tests the fixes (long
halflifes 25/40, flat late danger, flat territory weight) and still
loses both big_empty sides to ouroboros in spot games, so the single
validated-EWMA design of v09 remains the frontier for this direction.

## What this version established

- Dual EWMAs per se are cheap and stable (no faults, sandbox-class
  compute), but the LONG map's halflife must stay well under the game
  horizon or its features saturate.
- Time-ramped caution is a trap on length-race maps: late-game avoidance
  multipliers above ~1.0 cost more food than they save deaths.
- The kraken/autarky gains suggest the surge/ratio features do carry
  signal against evaluator-style opponents; a follow-up could apply them
  selectively rather than globally.

## Sandbox / judge checks

Adds two more O(NZ) decays and O(1) feature lookups per scored cell;
same complexity class as v09 (family reference max 59.5M of 100M).
