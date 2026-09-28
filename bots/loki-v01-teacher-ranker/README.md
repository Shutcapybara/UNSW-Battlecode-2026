# Loki v01 — Bifröst v01 teacher ranker

## Lineage

Parent: **Bifröst v01 (`bifrost-v01-portal-memory`)**. This folder began as
an exact copy of that snapshot. The only policy change is an exported learned
score bonus over Bifröst v01's existing action candidates. No later Bifröst
version and no Fafnir code is used.

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

## Baseline performance

The native six-map panel scored **47–13** over 60 games against Bifröst v01
and four reference bots. On 48 matched fixtures against those references, Loki
scored **40–8**, while Bifröst v01 scored **43–5** on the same seeds and runner.
The direct native matchup against Bifröst v01 was **7–5**.

The original sandbox matchup against Bifröst v01 went **0–12** and recorded 93
Loki `exceeded CPU limit` events. That result is the v01 baseline. The inference
optimization that addressed those faults is now isolated in
[`loki-v02-teacher-ranker`](../loki-v02-teacher-ranker/README.md).

Reports: [native panel](../../experiment_data/loki-v01-teacher-ranker_20260927133358001146/summary.md),
[matched native Bifröst control](../../experiment_data/bifrost-v01-portal-memory_20260927134114388817/summary.md),
and [original sandbox head-to-head](../../experiment_data/loki-v01-teacher-ranker_20260928053201903911/summary.md).

## Training

Install the training dependency into the project environment if needed:

```sh
.venv/bin/python -m pip install 'scikit-learn>=1.6,<2'
```

Then run `tools/loki/train.py` with the ten source replay paths. Training scripts
and feature definitions are in `tools/loki/`; the generated metrics and replay
provenance are in `experiment_data/loki-v01-teacher-ranker/`.
