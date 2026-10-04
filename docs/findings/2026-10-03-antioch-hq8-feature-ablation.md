# Antioch H-Q8 observation contract and GBT feature ablation

Date: 3 October 2026. Runtime: `unswbc==1.2.5`.

## Decision

The H-Q8-v1 observation contract is frozen as a 36-field signed-int32 block.
Unknown or unavailable values are `-1`; silence does not imply death. The
replay-derived dataset preserves the 1.2.5 local pilot's whole-game 80/20
split. Python/C++ feature parity and a check against actual Carthage05
controller observations both passed with no mismatches.

The matched GBT ablation found **no useful queen-action imitation gain** from
the block at this model size. Overall move accuracy changed by only +0.0043
percentage points on sampled holdout rows. Queen-turn accuracy did not change;
the augmented trees used only `rounds_remaining`—a deterministic transform of
the baseline `round`—and selected no queen-specific H-Q8 feature. Keep the
contract and dataset for follow-up experiments, but this result does not
justify adding H-Q8 to a deployable GBT or claim improved playing strength.

## Frozen observation contract and data

`tools/antioch/rl/hq8_features.py` and `hq8_features.hpp` define 36 values in
the order documented in `tools/antioch/rl/hq8_schema.md`. The observation uses
the actor's own protocol block and split history only. Examples of preserved
unknowns include inferred queen death, queen mode, map class, hidden exact
lengths/ranks, sonar interpretation and pearl provenance. `hq8_round` is kept
for audit but equals the existing baseline `round`, so it is not a second model
input.

The augmented dataset is
`build/antioch/rl/hq8-pilot-v1/dataset.parquet`:

- 123,215 sampled rows from the same 100-game 1.2.5 pilot;
- 80 training games and 20 held-out games, with each seat pair wholly in one
  partition (40 train pairs, 10 holdout pairs);
- all 36 H-Q8 values retained; 35 are added to the model beside the 270
  committed HB1 features, for 305 unique inputs;
- metadata, map, seed, outcome and labels are excluded from model inputs.

Dataset SHA-256:
`c999563cf094264c4a0db624d39d0c4dbd11c0856c16b51c06a4dbe174d912f2`.
Its manifest SHA-256 is
`697f1725d16664c3a4fae22594725fe8b33bc266c56826afe8511d7d75f704e4`.
The Python encoder is bound by SHA-256
`6d414fdf6fa99086d4fe369917cf523b55b51ca920f1a3d9b9219899e725ca11`;
the C++ feature header/schema digest is
`d98264ae6e3295941610c0f0a436fbfe1002a3c28aeebb08d35305f8e151969f`.

### Feature parity

- The packed Python/C++ encoder parity audit passed on 146,912 actor turns
  across eight maps, with zero byte mismatches (the existing G2 check).
- A new diagnostic build traced the H-Q8 encoder from the actual
  `hb1::block_from(ct, game)` controller observation, then matched those rows
  against replay reconstruction from the same games. It passed on 46,147
  actor turns in five frozen pilot fixtures spanning all five maps and both
  A/B seats, with zero mismatches. The traced fixtures were game IDs 1, 22,
  41, 62 and 81; their base-bot source fingerprint matches the pilot.
- The diagnostic copy adds logging and encoder work. These runs validate
  observation parity, not game performance or throughput. The measured bot
  snapshot and shared encoder were not modified.

Reports and artifacts:

- Contract: `tools/antioch/rl/hq8_schema.md`
- Dataset manifest/receipt: `build/antioch/rl/hq8-pilot-v1/manifest.json` and
  `receipt.json`
- Actual-controller probe: `build/antioch/rl/hq8-runtime-probe-v1/report.json`
- Probe runner: `tools/antioch/rl/hq8_runtime_probe.py`

## Matched-size action-imitation ablation

The target is the replay-reconstructed F/R/L move Carthage05 actually executed
on each sampled actor turn. Both models use the same 99,706 training rows,
23,509 holdout rows, labels, inverse per-game sampling weights and frozen
game/seat-pair split. Histogram thresholds are fitted on training rows only.
The deterministic trainer uses 120 rounds, depth 3, 32 bins, learning rate
0.08, L2 3, minimum gain 1 and minimum leaf size 64.

The baseline uses 270 HB1 inputs. The augmented model uses those same inputs
plus 35 H-Q8 values. Both store 120 complete depth-3 trees: exactly 36,000
node bytes plus a 12-byte three-class base vector (36,012 numeric bytes each).
This scratch trainer is an offline comparison, not the deployed HB1 model.

| Holdout slice / metric | Baseline | With H-Q8 | Paired delta (H-Q8 − baseline) |
|---|---:|---:|---:|
| All rows, accuracy | 78.1913% | 78.1956% | +0.0043 pp row-level; +0.0025 pp pair-macro [0, +0.0075] |
| All rows, inverse-sampling-weighted accuracy | 79.0844% | 79.0916% | +0.0072 pp |
| All rows, log loss | 0.520121 | 0.520120 | −0.00000114 row-level; −0.00000373 pair-macro [−0.00000737, −0.00000115] |
| Queen actor turns (612 rows / 20 games), accuracy | 77.1242% | 77.1242% | 0 pp (pair-macro 90% interval [0, 0]) |
| Queen actor turns, log loss | 0.528442 | 0.528434 | −0.00000805 |
| Round ≥350 (3,540 rows / 8 games), accuracy | 78.5311% | 78.5311% | 0 pp |

Intervals are central 90% percentile bootstraps over 10 paired holdout
matchups; both seat games remain together. The matched estimate is descriptive
for this local Carthage05 data and not a generalization or win-rate interval.
The queen/late intersection has just eight rows in one game and is not
interpretable.

The augmented model used two splits on `hq8_rounds_remaining` and zero splits
on every other H-Q8 field. Since `rounds_remaining = 500 - round`, the only
selected added signal duplicates the baseline clock. Accuracy and queen-turn
accuracy are effectively unchanged. This is evidence against a useful lift on
this teacher-imitation target and model budget; it is not a panel test and does
not determine whether H-Q8 improves a stronger search policy or game outcomes.

## Reproduction

```sh
.venv/bin/python tools/antioch/rl/hq8_local_dataset.py \
  --out build/antioch/rl/hq8-pilot-v1 --jobs 2

.venv/bin/python tools/antioch/rl/hq8_runtime_probe.py \
  --games 1,22,41,62,81

nice -n 10 .venv/bin/python tools/antioch/rl/hq8_gbt_ablation.py \
  --dataset build/antioch/rl/hq8-pilot-v1/dataset.parquet \
  --manifest build/antioch/rl/hq8-pilot-v1/manifest.json \
  --out build/antioch/rl/hq8-gbt-ablation-v1
```

The ablation report, per-game/pair CSVs, input audit, trainer source and
serialized scratch models are under `build/antioch/rl/hq8-gbt-ablation-v1/`.
No measured bot was changed or promoted. No queen-alive@490 or match-strength
claim was tested here.
