# Loki v02 — optimized teacher ranker

## Lineage

Parent: **Loki v01 (`loki-v01-teacher-ranker`)**, whose policy is an exact
Bifröst v01 (`bifrost-v01-portal-memory`) fork with a learned score bonus. Loki
v02 preserves the v01 model and action policy while reducing inference cost.
No later Bifröst version and no Fafnir code is used.

The model imitates public actions from team 龙虎豹's ranked submission **#7771**.
It ranks the actions Bifröst already generates; all sensing, persistent memory,
sonar communication, roles, safety checks, candidate generation, and fallback
behavior remain from Bifröst v01.

## Model and data

`trained_model.py` contains 48 shallow gradient-boosted trees and uses only
standard-library inference. The model was fitted with scikit-learn in the
repository `.venv`; the game bot does not import scikit-learn or NumPy.
`loki_features.py` is shared by the trainer and bot. Replay features are limited
to the same local 7×7 view, the bot's own known body, and public round/unit
counts. Hidden enemy lengths, remote cells, and remote pearls are excluded.

The source is ten ranked replays from submission #7771, side A: five games vs
calc and five vs SHINK AI 6500. Replay IDs and SHA-256 hashes are in
`experiment_data/loki-v01-teacher-ranker/replay_manifest.json`.

The candidate menu covered 136,069 of 136,760 teacher decisions (99.5%). The
remaining 691 actions were not available in Bifröst v01's candidate menu and
were not trained. The fit used 28,931 sampled decisions, retaining every split
and one fifth of ordinary movement decisions.

Whole-series held-out action-ranking results:

| Held-out series | Top-1 teacher-action match | Uniform menu reference |
| --- | ---: | ---: |
| vs calc | 64.1% | 21.9% |
| vs SHINK AI 6500 | 70.3% | 23.2% |

The average candidate menu had about seven actions. The figures are for the
learned ranker by itself; Loki also adds its score to Bifröst v01, so they are
not the integrated policy's measured action accuracy. They do not establish match
strength or transfer to later submissions.

## Inference changes

The 48-tree forest splits on only six of the 28 features. V02 caches destination
lookups, computes only those six features, simulates movement with a tail offset
instead of repeated front-list shifts, and skips candidates that cannot beat
the leader under a safe bound on forest scores. The full feature builder remains
for training. Model weights, training data, Bifröst candidate generation, and
fallback policy are unchanged from v01. Feature parity was checked on 6,800
synthetic actions, and a 2,000-menu randomized check confirmed that candidate
pruning preserves the full-model argmax.

## Benchmarks

A 30-game native panel against Fenrir v18 covered all 15 bundled maps and both
sides. Loki scored **11–19**, with no game errors. Fenrir swept Colosseum,
Default, Devil, Portals, Schooltime, Stronghold, and Trophy. Loki swept Arena,
Default Small, and Queen of Spades; the other five maps split 1–1. Fenrir's
README reports a prior 20–10 result against Loki, so the current matchup is
consistent with Loki losing roughly two games for every one it wins.

The judge-sandbox direct screen against Bifröst v01 scored **7–5** with no Loki
CPU-limit events. In a broader Hydra panel, Loki scored 43–13 in 56 completed
games; four games hit the runner's 600-second wall-clock timeout. All 50 CPU
limit events in that panel were attributed to Hydra.

A separate sandbox panel against Fenrir was stopped after 23 of 30 fixtures
were recorded: 10–12 over 22 completed games, one 600-second timeout, and seven
pending. The saved logs contain 94 Fenrir CPU-limit events and none from Loki.
Loki's highest recorded turn cost was 94.1M CPU points, close to the 100M cap.
Because Fenrir also TLEd repeatedly, those sandbox W/L results are not a clean
measure of strategic strength; use the native panel for that comparison. The
sandbox run nevertheless shows Loki stayed below the cap in every recorded
turn while leaving little worst-case headroom.

These experiments were run while the optimized files still lived under the
v01 directory. The source snapshot is the same code now stored in this v02
folder; report directory names retain the pre-migration v01 label.

Reports: [Fenrir native panel](../../experiment_data/loki-v01-teacher-ranker_20260928073609587715/summary.md),
[interrupted Fenrir sandbox panel](../../experiment_data/loki-v01-teacher-ranker_20260928063051000260/summary.md),
[optimized Bifröst head-to-head](../../experiment_data/loki-v01-teacher-ranker_20260928055412884222/summary.md),
and [broader Hydra sandbox panel](../../experiment_data/loki-v01-teacher-ranker_20260928060127668979/summary.md).

## Training

Install the training dependency into the project environment if needed:

```sh
.venv/bin/python -m pip install 'scikit-learn>=1.6,<2'
```

Then run `tools/loki/train.py` with the ten source replay paths. Training scripts
and feature definitions are in `tools/loki/`; the generated metrics and replay
provenance are in `experiment_data/loki-v01-teacher-ranker/`.
