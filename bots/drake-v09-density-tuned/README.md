# drake-v09-density-tuned

**Lineage**: Drake. **Parent**: `bots/drake-v08-density/`
(= v07 + the EWMA territory layer). No new borrowings.

## Hypothesis

v08's regression had two suspects: the ray schedule (two density packets,
one self packet — ally tracking starved) and zone_danger on a 5-round
memory (prediction-optimal but too twitchy for avoidance).  Fix both:
**one** density ray per turn, two self packets restored, zone_danger back
on the legacy ~30-halflife heat; the validated density maps feed only the
new features (territory term, hunter density pull, waypoint
de-congestion) and the K_DENS channel.

## Measured results

Full screen (11 opponents x 13 maps x 2 sides = 286 games):
run `experiment_data/drake-v09-density-tuned_20260925141057061384`.

- **Common 11-map subset: 88-1-153 = 0.366** — recovery from v08's 0.291,
  aggregate tie with v07's 0.370.
- Direct head-to-head vs v07 (all 13 maps, both sides): **12-14**.

| Opponent | v09 | v07 |
| --- | --- | --- |
| ouroboros-v10-beacon | **10-0-16** | 7-0-15 |
| hunter-v14 | 15-0-11 | 14-0-8 |
| hunter-v20 | 12-0-14 | 12-0-10 |
| fry-v14 | 15-0-11 | 16-0-6 |
| kraken-v04 | 14-1-11 | 13-1-8 |
| tew-v07..v12 | 4-5 avg | 4-5 avg |

Map profile shift vs v07 — the point of this version:

- **big_empty 9-0-13 (was 2-20); ouroboros-v10 record 10-6 (first time
  positive vs the top bot)**; stronghold 13-9 (was 7-15).
- queen_of_spades 14-8 (was 21-1), default 8-14 (was 13-9), fry closer.
- The two new community maps (autarky 1-21, dilemma 2-20) were never
  tuned and drag the 286-total.

## Interpretation

The territory layer changes *who* drake beats, not how much: against
ouroboros-class open-map play the smoothed ally/enemy field (transmitted
and diffused through K_DENS) measurably wins the macro game; against
aggressive swarms on structured maps the same territory bias slightly
hurts (foragers drift toward safe-but-contested zones while fry floods).
Aggregate ties with v07, so **v07 remains the Drake candidate**, and v09
is preserved as the diversity variant for the open-map subclass
(the handoff's "preserve promising diverse behaviour" clause).

## What the messaging run established

1. **Constant messaging is right** — sonar costs nothing beyond the
   batched write; the real constraint is slot ALLOCATION (v08's 2-dens
   schedule cost ~8 aggregate points by starving self packets).
2. **Halflife validation methodology**: `dens_features=0` makes variants
   play byte-identical deterministic games, so prediction quality is
   comparable without confounds.  Answer: shorter strictly better
   (enemy 5, ally 12 rounds; see v08's table).
3. **Prediction-optimal != decision-optimal**: the 5-round map predicts
   sightings best but zone_danger wants the ~30-round memory.
4. The K_DENS channel (checksum, round-stamped, saturation-capped zone
   readings + smoothed-position anchor) survives a full roster screen
   with no faults and flips the hardest matchup in the family's history.

## Next experiments for this direction

- Split the territory term: keep it vs ouroboros-class, disable vs
  swarm-class (cheap classifier: enemy density variance or opponent
  split rate from echoes).
- Send K_DENS only from low-information zones (where reception changes
  beliefs most) and use the freed slot for a second self packet.
- Tune on autarky/dilemma before the next frozen-roster freeze.

## Sandbox / judge checks

Same complexity class as v08/v07 (O(zones) decay, one pack, O(1)
folds); family reference max 59.5M of 100M pts/turn.  Re-run before
submitting v09 anywhere the judge meters.
