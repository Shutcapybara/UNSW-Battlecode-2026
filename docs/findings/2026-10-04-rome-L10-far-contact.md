# Rome L10: far-contact guard — complete re-read

**Status: HOLD (gate interpretation and unit guard remain unresolved).** The experiment is complete under `unswbc 1.2.3`, and features have been re-extracted with FRAME_VERSION 7 / official replay winners. The old FRAME_VERSION 5 scorecard is superseded.

## Test and preregistered expectation

- Parent: `rome-01-nodevil`, the measured post-rule base (hb1-14 prior, D-033 terms off).
- Candidate: `rome-02-far-contact`, one switch skipping direct head-on paths when the contact cell is more than six Manhattan cells from any currently known bed.
- Expected sign: fewer enemy head-on losses per 1,000 dragon-turns; economy neutral or positive.
- Panels: pool 480 and gen 1,392 paired side-games; seeds 1–3, both seats; runtime `unswbc 1.2.3`; CPU probe max 10.82M points/turn, zero errors.
- Parity / provenance: scorecard features re-extracted under FRAME_VERSION 7; winner taken from engine replay verdict. See Himeji's official winner correction and `game_stats/runs/rome-02-far-contact-z1+gen-s1-2-3.md`.

## Outcome

| Panel | Parent W-L-D | Candidate W-L-D | Win-share Δ | Literal mean econ Δ, cluster 90% CI | Median-checkpoint econ Δ, cluster 90% CI |
|---|---:|---:|---:|---:|---:|
| Pool (480) | 396-83-1 | 399-80-1 | +0.63 pp | +0.0004 [-0.0001, +0.0010] | 0.0000 [-0.0017, +0.0005] |
| Gen (1,392) | 1,036-356-0 | 1,033-359-0 | -0.22 pp | +0.0087 [+0.0026, +0.0150] | -0.0042 [-0.0124, +0.0079] |

The literal mean is the paired per-game mean of each game's four normalized checkpoint values; the median-checkpoint form is the mean of the four per-checkpoint median differences. Clair's 1 Oct D-032 revision requires a positive economy lower bound on at least one panel and non-harm on the other, with win lower bounds above -0.02 on both; the result changes with which economy estimand is used. Under the literal mean, gen is positive and pool is non-harm at displayed cluster precision; under the median-checkpoint form, neither panel demonstrates positive economy. Until the analysts settle the units/length guard form and the gate's economy estimand, this is a hold, not an accept.

| Panel | Units@100 Δ, cluster 90% CI | Total length@100 Δ, cluster 90% CI | Mean win Δ, cluster 90% CI |
|---|---:|---:|---:|
| Pool | 0.000 [0, 0] | 0.000 [0, 0] | +0.0063 [-0.0021, +0.0167] |
| Gen | +0.0114 [-0.0228, +0.0286] | +0.0023 [-0.0322, +0.0345] | -0.0022 [-0.0093, +0.0050] |

Gen guard intervals touch below -0.02 for units and total length, so this candidate cannot be accepted until that pending analyst ruling is applied. The mean-per-1k tier-2 rates in the official lane convention do not rise by more than 10% when a parent rate exceeds 0.05: pool changes are wall -0.9%, own-body +1.5%, ally-body -0.2%, ally-head-on -0.7%; gen changes are wall -0.7%, own-body +4.8%, ally-body +7.1%, ally-head-on unchanged. The scorecard's displayed median gen tier-2 rates are also retained in its report; they are not the lane's mean-rate hygiene gate.

## Preregistered diagnostic and map deltas

Enemy head-on deaths per 1,000 dragon-turns (cluster bootstrap over map × opponent × seat, seeds grouped) changed from 4.272 to 4.242 on pool (Δ -0.029, 90% CI [-0.066, +0.004]) and from 9.403 to 8.988 on gen (Δ -0.415, [-0.556, -0.269]). This supports the expected direction strongly on gen and weakly on pool; the metric is a per-turn proxy, not deaths per far-contact encounter.

Per-map median-checkpoint economy deltas are in `game_stats/runs/rome-02-far-contact-permap.csv` with structural-cluster intervals in the companion `.clusters.csv`. The gen deltas range from -0.066 (pulse_farms) to +0.073 (causeway_portal); pool deltas are close to zero (range approximately -0.001 to +0.004). Checkpoint and absolute / parent-relative values are in the full scorecard. No post-change field reference exists for the gen maps, so gen values remain parent-relative.

## Decision

**HOLD; do not stack.** The behavioral diagnostic improved on gen, but pool impact is inconclusive, economy acceptance depends on the unresolved estimand, and the gen material guard interval crosses the current -0.02 boundary. Keep both version directories and use `rome-01-nodevil` as the parent for the next single-mechanism experiment.
