# drake-v11-satutfix

**Lineage**: Drake. **Parent**: `bots/drake-v10-dual-ewma/`.
No new borrowings.

## Hypothesis

v10's regression is dominated by two structural pathologies, not by the
dual-EWMA idea itself: long-map saturation (halflifes 40/90 pin at cap
over 500 rounds) and late over-avoidance (danger ramp to 1.4).  Fix the
parameters - long halflifes 25/40, danger 0.8 early -> 1.0 flat,
territory weight flat - and keep the surge difference, log-ratio hunt
pull and hunt fade unchanged.

## Measured results

**Spot checks only (not screened, not promoted):**

- big_empty vs ouroboros-v10: loss both sides (500 rounds, length).
- queen_of_spades vs ouroboros-v10: loss (this fixture was 0-2 for v09
  as well, so not diagnostic).

The big_empty losses say the parameter fixes do NOT recover v09's
open-map edge; too many correlated deltas remain between v10 and v09
(long-map territory vs short-map, surge term, hunt fade, ratio pull) to
isolate the active ingredient without another full screen.  Stopping
here: the family's measured frontier for the density direction remains
**drake-v09-density-tuned** (0.366 common subset, ouroboros-v10 10-6).

## What this variant is for

A future session can screen it cheaply (frozen `drake-eval.toml`) if it
wants to complete the ablation of v10's feature set, or strip v10 back
feature-by-feature from the v09 side (surge term first: it is the one
addition with no v09 equivalent and the kraken/autarky gains point at
it).
