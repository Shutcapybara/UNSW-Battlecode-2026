# Antioch RL groundwork on the director's 3060 Ti host

Date: 3 October 2026. Runtime target: `unswbc==1.2.5`.

This records what is ready on the director's new machine and what remains before
starting learned-policy training. It does not promote a bot or claim that the
full H-Q8 proposal is implemented.

## Host and runtime

- PyTorch `2.14.1+cu130` detects the RTX 3060 Ti (8 GiB) and completes a CUDA
  matrix-multiplication smoke check when run with host GPU access. Driver
  580.178.04; CUDA runtime 13.0. The restricted sandbox cannot see the GPU.
- The batched engine harness is
  `tools/antioch/rl/batched_engine_bench.py`. It launches official in-process
  engines and sends real callback observations to one shared inference server.
  Its MLP is an untrained throughput probe, not a policy or strength result.
- GPU inference-only rates reached 39,848 decisions/s at batch 8 and 149,301/s
  at batch 32, including host/device transfers. One full H-Q8/CUDA process
  match completed 1,041 callbacks without errors. These are smoke results only.

## Readiness checks

| Gate | Result | Remaining limit |
|---|---|---|
| G1 — sustained batched engine throughput | Pass for the measured probe workload | 28.63 million actual callback decisions/hour; 3.05 average CPU cores under an eight-CPU affinity cap; zero engine/service errors. The workload uses an untrained MLP and does not measure policy quality or training-loop throughput. |
| G2 — Python/C++ observation parity | Pass for the declared H-Q8-v1 subset | Zero packed-byte mismatches over 146,912 actor turns, 36 signed int32 features, eight maps and both teams. A second trace from actual Carthage05 controller observations matched replay reconstruction on 46,147 turns across five pilot fixtures/five maps and both seat labels, zero mismatches. The subset deliberately leaves sonar interpretation, inferred mortality, map classification, hidden exact lengths/ranks and pearl provenance unknown. |
| G3 — direction-GBT size curve | Sizes and fresh local teacher fidelity measured | The 100-game 1.2.5 pilot has a frozen 20-game holdout. No smaller prefix passes its declared compression screen; keep 540 rounds. Historical expert accuracy remains unavailable without the original files. Local fidelity is a separate measurement. |
| G4 — H-Q8 GBT feature ablation | Completed; no useful queen-action accuracy lift at the tested budget | Matched 120-round/depth-3 models share an exact 36,012-byte numeric tree budget. Adding 35 unique H-Q8 inputs changes holdout action accuracy by +0.0043 pp over 23,509 rows; queen-turn accuracy is unchanged on 612 rows/20 games. The augmented model's only H-Q8 splits are two uses of `rounds_remaining`, a transform of baseline `round`. This is teacher-action imitation, not a strength or panel result. |

The G2 report and feature contract live in `tools/antioch/rl/hq8_schema.md`;
the replay parity output is `build/antioch/rl/hq8-parity-1000-1.2.5.json` and
the actual-observation trace is
`build/antioch/rl/hq8-runtime-probe-v1/report.json`. Parity proves the
implementations match for the documented contract; it does not validate
omitted features or learned-policy deployment integration. G4's complete
method and interpretation are in
`docs/findings/2026-10-03-antioch-hq8-feature-ablation.md`.

### Direction prior size points

The byte column is the compressed complete deployment-bot source upload, not
the size of the model header alone. The model is the committed HB1 cap3000 /
leaves255 fitted model, prefix-truncated without refitting.

| Boosting rounds | Upload bytes | Fits 4 MiB? | Historical rounded accuracy* |
|---:|---:|:---:|---:|
| 100 | 743,783 | yes | 0.827 |
| 400 | 2,908,604 | yes | 0.842 |
| 540 | 3,919,781 | yes | unavailable |
| 1,000 | 7,236,579 | no | 0.847 |
| 1,900 | 13,711,790 | no | 0.849 |
| 2,345 | 16,907,843 | no | 0.850 |

\*Archived 30,000-row samples in `claude/hb1-status.md:242-243`; rounded to
three decimals and not re-evaluated on this host. They are not the full original
179,436-row held-out result. Do not select a model size from these anchors.

To reproduce historical expert accuracy, restore these original files from the
former machine:

```text
build/hb1/games.parquet          # frozen original 817-game corpus
build/hb1/q1/direction.parquet
```

Then run:

```sh
.venv/bin/python tools/antioch/rl/gbt_direction_curve.py \
  --heldout-parquet build/hb1/q1/direction.parquet \
  --games build/hb1/games.parquet
```

Do not regenerate the historical split from an expanded corpus. Reproducing a
historical depth ablation also needs the original
`build/hb1/v5/corpus/*.parquet` training files and CPU XGBoost.

### Completed alternative when those files are unavailable

The new local pilot produced 914,353 actor rows and 123,215 sampled direction
states, with 23,509 states in a holdout fixed before running. All 100 games and
reconstruction checks passed. The curve compares prefixes with the committed
full 2,345-round teacher, not with expert labels.

The 400-round prefix saves 25.79% of Carthage05 source-upload bytes but loses
0.5006 pp of teacher agreement versus 540, paired central 90% interval
[−0.7279,−0.2568]. It misses the declared −0.5 pp lower-bound tolerance;
no smaller prefix qualifies. Keep 540 rounds. Fresh teacher fidelity is now
measured without the original data; historical accuracy remains a separate
unavailable benchmark. Full method, checks and reproduction:
`docs/findings/2026-10-03-antioch-local-gbt-pilot.md`.

## Carthage runtime comparison

The five-seed `carthage-05-free-sprint` versus `carthage-00-base` comparison
completed under `unswbc==1.2.5`, for pool and gen panels, both seats, seeds 1–5.
Pool win change was +2.62 pp [+0.62,+4.50]; gen win change was +1.25 pp
[+0.20,+2.30]. The default lane screen rejects because the pool `econ~` lower
bound is −0.001; gen arithmetic economy is −0.007 [−0.013,−0.001], and the
gen total@100 lower bound −0.024 misses D-042's −0.020 guard. D-042 was scoped
to 1.2.3 adaptations; this is a new 1.2.5 paired screen, not a 1.2.5 ruling.
All baseline features extracted successfully. Full result:
`docs/findings/2026-10-03-carthage-05-vs-00-five-seed-1.2.5.md`.

## Training decision

Do not begin PPO yet. The next order is:

1. Use the completed local fidelity curve to retain the 540-round prior.
   The fresh dataset is available for a separately declared refit or
   distillation experiment. Recover the original artifacts only if exact
   historical expert-accuracy reproduction is needed.
2. Keep H-Q8-v1 as a frozen observation/data contract, but do not add it to a
   deployable GBT on this imitation result: queen-turn accuracy did not move
   and the model selected only the redundant round countdown. A panel on a
   changed learned/search policy would be needed to test playing strength.
3. The 4 Oct follow-up checked the gate and hand-mining conditions: no
   ratified 1.2.5 learned-arm win-led gate exists, and the all-family
   hand-mining stop condition is not met (H-S1 portal memory is untested and
   sprint has positive two-panel 05−00 results). Keep GBT expert iteration
   queued until those prerequisites are resolved; reserve PPO for a plateau.
   The actual 540-round Ares rollout rate is 5.43M actor turns/hour over its
   measured fixture mix. Full audit and method:
   `docs/findings/2026-10-04-antioch-rl-entry-check.md`.

The G1 raw output is `build/antioch/rl/batched-engine-hq8-cuda-8-workers-1.2.5.json`;
the Carthage paired score is
`build/carthage/results/carthage-05-vs-00-pool-gen-seeds1-5-1.2.5.json`.

Supporting reports: `docs/findings/2026-10-03-antioch-batched-engine-readiness.md`,
`docs/findings/2026-10-03-antioch-local-gbt-pilot.md` and
`docs/findings/2026-10-03-antioch-hq8-feature-ablation.md`. Generated curves:
`build/antioch/rl/gbt-direction-curve/curve.json` and
`build/antioch/rl/local-pilot-v1/curve/curve.json`.
