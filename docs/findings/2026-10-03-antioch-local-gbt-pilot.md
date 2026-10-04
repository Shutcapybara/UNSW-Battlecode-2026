# Fresh local GBT pilot without the historical HB1 parquet files

Date: 3 October 2026. Runtime: `unswbc==1.2.5`.

## Decision

Keep the existing 540-round direction prior. No smaller tested prefix passes
the compression screen declared before the games ran. The 400-round prefix
saves 25.79% of the Carthage05 upload, but its paired agreement change versus
540 is −0.5006 percentage points, with central 90% interval
[−0.7279, −0.2568]. Its lower bound misses the declared −0.5 pp tolerance.

The replacement dataset and curve are complete. No additional games are needed
for this first fidelity measurement. This result does not justify a new bot or
a reserved pool/gen panel. No bot was changed or promoted.

## What the measurement means

The original `build/hb1/games.parquet` and
`build/hb1/q1/direction.parquet` are unavailable on this machine. Fresh states
were collected and each prefix was compared with the **committed full
2,345-round GBT**. The target is that model's prediction, not Carthage's search
action. Search actions and game outcomes are retained as separate metadata.

Agreement measures compression fidelity on local states. It neither reproduces
historical Heartbreaker imitation accuracy nor establishes playing strength.
The full teacher is a fixed reference, not an oracle. No model was fitted.

## Frozen dataset

- Base: `carthage-05-free-sprint`, both seats against Fenrir V18, Yuna V05,
  Chaewon Y04, Sinbad V07 and Gavroche V32.
- Maps: `arena`, `big_empty`, `Colosseum`, `default_small`, `stronghold`.
  These are the lane's dedicated training maps, outside both reserved panels.
- Seeds: 101 and 102; 100 games total. No existing pool/gen replay was used
  to build or select from this dataset.
- Partition fixed before running: 80 training games and 20 holdout games.
  Split seed 62 selects two holdout matchups per map; both seats of each
  map/opponent/seed matchup stay together. The holdout has 10 fixture pairs.
- Python v5 reconstruction supplies all 270 model features. Map names,
  seeds, outcomes and action labels are excluded from model input.
- All 914,353 actor rows are retained in per-game parquet files. Of those,
  900,803 have eligible move labels F/R/L. Uniform sampling without replacement
  selects at most 2,000 eligible states per game, using seed `20261003 + game_id`.
  The sample contains 123,215 rows: 99,706 train and 23,509 holdout. Inverse
  sampling weights are retained for future consumers; the primary curve gives
  each game equal weight, rather than estimating frequency across all turns.

Inputs and local output: `build/antioch/rl/local-pilot-v1/`.

```text
manifest SHA256: fafb6d459512a1f275eb557d9d9a9e935b3ac110e65ec10a2683c2ad0dea9fe5
dataset SHA256:  a17f835d5ce340098219ec322a0df73e517d4a34c2dc5874f7022ea9cdadf084
teacher SHA256:  49e10ee42a16d0d6938dffba094b7adbe70e5df6cfc8df40623e3e9ccc38fe22
```

## Curve and declared screen

The screen requires at least 10% upload saving versus 540 rounds and a paired
agreement-change lower bound of at least −0.5 pp. These criteria were in the
frozen manifest before any game ran. Adoption would still require actual
reserved game panels.

| Rounds | Mean game agreement with full teacher | Carthage05 upload bytes | Fits 4 MiB? |
|---:|---:|---:|:---:|
| 25 | 85.4571% | 217,278 | yes |
| 50 | 88.7702% | 390,856 | yes |
| 100 | 91.8345% | 745,014 | yes |
| 200 | 93.8917% | 1,463,717 | yes |
| 400 | 95.2893% | 2,909,835 | yes |
| 540 | 95.7899% | 3,921,012 | yes |
| 1,000 | 96.7618% | 7,237,810 | no |
| 1,900 | 98.5191% | 13,713,021 | no |
| 2,345 | 100% | 16,909,074 | no |

The 540-round agreement has a seat-pair bootstrap central 90% interval of
[95.3575%, 96.2708%]. Bootstrap uses 2,000 resamples and seed 62. Paired
prefix-minus-540 comparisons resample whole fixture pairs, preserving both
seats. Game intervals and sampled-row intervals are also recorded. Only two
seeds, five maps and ten holdout pairs are represented; this is a pilot screen.

Upload bytes cover the complete Carthage05 C/C++ source ZIP after replacing
its direction header, using ZIP_DEFLATED. They are neither header-only bytes
nor compiled wasm size. They differ slightly from the earlier hb1-14 size table
because Carthage05 has different policy source.

The holdout includes 612 queen states across 20 games and 3,540 late states
(round ≥350) across eight games. Mean game agreement for queen states is
94.1634% at 400 rounds and 94.3272% at 540; for late states it is 95.9629%
and 96.2986%. These are diagnostic slices with fewer observations. Class,
opening, seat, total-variation, KL and Jensen–Shannon results are in the curve.

## Checks and provenance

All 100 games completed with zero runner errors. Reconstruction recorded
1,869,886 successful movement checks and 200 successful terminal standings
checks, with no bad counters.

Five fresh fixtures, on Arena, Big Empty and Stronghold and across both seats,
passed Python/C++ feature-mirror comparison on 70,048 actor rows: all 270 model
inputs covered, zero mismatches at absolute tolerance 1e-6, maximum difference
4.44e-15. This compares replay reconstruction with the C++ mirror; it does not
claim parity with captured runtime observations.

The compact evaluator matched the actual committed `hb1::dirc_proba` on 32
sampled holdout states: zero probability differences and zero argmax differences.
The full teacher agrees with itself exactly, with zero probability divergence.

The completion audit checks every fixture/index binding, replay/raw/sample
hash, cached outcome and partition, deterministic sample and weight, and the
combined dataset. `producer.json` and `extraction-receipt.json` bind future
reuse to the recorded code and inputs. Producer source was recorded after
completion: validation/resume code changed during this pilot, while feature,
filter and sampling semantics stayed unchanged. The adoption audit verifies
the resulting sampling recipe directly. Earlier receipts are archived locally.
Completed extraction now verifies and returns without rewriting data or timing.

Measured compute: games about 281 s including the initial two-game smoke run,
extraction 379.92 s, curve including compiled header parity 54.34 s—approximately
12 minutes, excluding setup and audits.
The entire pilot, curve and checks occupy about 659 MiB locally. Generated
parquet, replay and binary files remain under ignored `build/`.

## Reproduction and next work

```sh
.venv/bin/python tools/antioch/rl/local_dataset.py plan
.venv/bin/python tools/antioch/rl/local_dataset.py run --dry-run
.venv/bin/python tools/antioch/rl/local_dataset.py run --jobs 8
.venv/bin/python tools/antioch/rl/local_dataset.py extract --jobs 2
.venv/bin/python tools/antioch/rl/local_dataset.py audit
nice -n 10 .venv/bin/python tools/antioch/rl/gbt_local_curve.py \
  --dataset build/antioch/rl/local-pilot-v1/dataset.parquet \
  --manifest build/antioch/rl/local-pilot-v1/manifest.json \
  --out build/antioch/rl/local-pilot-v1/curve \
  --deployment-bot bots/carthage-05-free-sprint --header-parity-rows 32
```

Feature parity can be reproduced with `tools/antioch/rl/hb1_local_parity.py
--replay <pilot-replay> --side A|B --out <build-directory>`.

The outputs are `curve/curve.json`, `curve.csv`, `per-game.csv`,
`per-pair-deltas.csv`, and `slices.csv`; game and dataset timing/counts are in
`run-report.json` and `dataset-report.json`.

The missing original files no longer block collecting local data or measuring
fresh teacher fidelity. Historical expert accuracy still requires those original
inputs. A refit or distillation experiment should use only the frozen training
partition and its own declared screen. For actual improvement, recheck the
training-entry conditions and then use search/exploration plus outcomes for GBT
expert iteration. The unresolved learned-feature integration and 1.2.5
evaluation gate remain; keep PPO parked.
