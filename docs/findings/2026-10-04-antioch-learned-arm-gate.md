# Decision: local acceptance gate for 1.2.5 learned arms

Date: 4 October 2026. Runtime scope: `unswbc==1.2.5`.

## Ruling

Adopt the following **prospective local screen** for a learned-policy or
learned-search arm nominated for evaluation under 1.2.5. It extends the
win-led Himeji criteria from D-042 to this candidate class. It does not change
D-032, rewrite earlier verdicts, or authorize promotion.

Compare the frozen candidate with its declared parent on the complete pool and
generalisation panels, seeds 1–5, both seats. The candidate and parent must
have been run with `unswbc==1.2.5`; use FRAME_VERSION 7 for replay outcomes.
Bootstrap paired common fixtures keyed by seed, map, opponent, and seat, using
the lane scorer's 1,000 resamples and seed 7. Gate on the 5th-percentile lower
endpoint of the reported central 90% interval.

| Measure, candidate minus parent | Pool requirement | Gen requirement |
|---|---:|---:|
| Official expected-score share (win=1, draw=0.5, loss=0) | lower bound > 0 | lower bound > −0.02 |
| Normalized four-checkpoint economy (`econ~`) | lower bound > −0.03 | lower bound > −0.03 |
| Normalized units@100 | lower bound ≥ −0.02 | lower bound ≥ −0.02 |
| Normalized total@100 | lower bound ≥ −0.02 | lower bound ≥ −0.02 |

Also require every tier-2 death-rate increase to stay within the existing 10%
guard when the parent rate is above 0.05 per 1,000 turns, and require zero new
invalid-action deaths. Any missing fixture, unsuccessful engine run, timeout,
or missing 1.2.5 run record makes the result **INCOMPLETE**. Run the existing
CPU check separately; it must stay within the official points budget and have
no errors. For a change explicitly limited to the endgame, retain the existing
early-checkpoint guards. Report per-map and per-checkpoint changes in every
case.

The shared Carthage scorer exposes this rule as an opt-in mode:

```sh
.venv/bin/python tools/carthage/lane.py score <candidate> --parent <parent> \
  --seeds 1,2,3,4,5 --gate learned125 --json build/carthage/results/<name>.json
```

It checks complete panel coverage and per-fixture successful 1.2.5 run records.
The default `--gate d032` behavior is unchanged. Local acceptance only admits a
candidate to the experiment stack. Promotion still requires fresh live
confirmation under the repository's existing policy.

## Why these thresholds

The win and economy margins carry forward D-042's delegated ruling: require a
pool win gain, limit tolerated gen loss to two percentage points, and cap the
economy loss at three points on either panel. The material guard is stated as
a bootstrap lower bound, and applies on both panels. This closes the previous
ambiguity between point estimates and bounds, and prevents a pool win gain from
masking a large gen loss in r100 material.

The 1.2.5 five-seed Carthage 05−00 screen illustrates the need for separate
win and guard clauses: its win bounds are positive on both panels, while its
pool `econ~` lower bound is −0.001 and its gen total@100 lower bound is −0.024.
Those hand-policy results are not a learned-arm verdict and are not
retroactively reclassified by this ruling.

## Evaluation discipline and limits

Freeze the parent fingerprint, candidate source/model, runtime, panel roster,
and evaluation seeds before scoring. Keep the five-seed panels out of training
and model selection; collect training rollouts on the separate training maps
and seeds. Nominate one frozen candidate for the gate. The fixture bootstrap
is a local screening convention, not a population-level strength interval;
report its limits and retain the independent live-confirmation step. Queen
survival and Φ remain diagnostics and cannot replace overall wins or the
material/economy guards.

This ruling resolves only the evaluation-gate prerequisite for learned
training. It does not satisfy the separate hand-mining stop condition: H-S1
portal memory remains untested, and sprint results still show paired wins.
