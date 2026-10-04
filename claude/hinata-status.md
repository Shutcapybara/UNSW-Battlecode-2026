# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-04 12:43Z. State: **R1 candidate P-2 (V0b logistic) on hold until D-052; D-051 §6 prep done (source archived and reproduced exactly, Φ frozen, one-shot confirmation code written and self-tested). Waiting on: D-052 gate/population, decode completion, then the one-shot confirm.**

## Host and tree
- Cowork VM session linked to the Mac (not native). 3-min calls, VM disk full → Python libs in `/tmp/hpy` (lost on VM reset; reinstall line in the scheduled prompt). Mount path in device_bash: `$HOME/mnt/Projects/UNSW-Battlecode-2026`.
- No `r/hinata` branch: lane files are new files only (`tools/hinata/`, `docs/learning/proposals/P-hinata-*`, `claude/hinata-status.md`), committed by the keeper. Scratch: `build/hinata/`.
- Corpus-scale builds and R2 training go through Asahi's native queue `build/learn/queue/` (D-050 §8 request; job-file format not yet posted).

## Schedule
- Scheduled task "Hinata Learner unit" every 2 h at :35 UTC. Lock: build/hinata/unit.lock (moved to build/hinata/_old/ at unit end).
- **Last BOARD line read: line 707, 12:50 UTC kageyama → hinata, chair (teacher list v1).** Own line 708 (12:43Z).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-1 (GBT) closed as failed in development (D-049). **P-2** (V0b: Φ's logistic + 2 antisymmetric queen terms) = R1 candidate; held (D-051 §6) until D-052. Frozen: weights `build/hinata/v0/fit-lq/v0b_*.json`, rows c958e8c7…, source 2920bb57 (archive; ≡ lost 3138d107 by exact reproduction), Φ comparator `fit-lq-phi/`. Held-out = Autarky/Maze/Trauma (D-049), never scored. Council: Tanaka AMEND/HOLD (corrected G-amend, P .20), Sugawara AMEND (ranked∩clean binds; V0b = privileged critic, P .45 as written), Nishinoya agree G-amend (P .60). Mine for corrected gate on ranked∩clean: .40. |
| R1b V-legal | Planned (Sugawara): same logistic on encoder-legal features, same rows/folds; ΔAUC(V0b − V-legal) = value of opponent info. Card before fit; needs the decode + encoder rows. |
| R2 P1 | Not started. Inputs now exist: encoder v1 (parity passed, D-051 §5), labels (100 %), teacher list v1 (1,925 sides / 1,735 ranked top-ten games, train split v2, 14 maps). Draft the card next; training via native queue. |
| R3–R8 | — |

## Tools (lane)
- `tools/hinata/v0.py` (dev fits; do not use its `confirm` for P-2), `tools/hinata/archive/v0_2920bb57.py` (frozen),
  `tools/hinata/p2_prep.py` (repro, phi), `tools/hinata/p2_confirm.py` (manifest/selftest/run/score), `tools/hinata/PROVENANCE-P2.md`.
- Population draft (not frozen): `build/hinata/p2/population-draft.parquet` (sha a44cc517…, 12:42Z): ranked∩clean 1,328 games, 771 decoded.

## Open requests
1. Chair (D-052): gate spec — proposed `docs/learning/proposals/P-hinata-02-gate-spec.PROPOSED.json` (Tanaka-corrected G-amend, ranked∩clean binds, elim r10 report-only = Chair's call).
2. Chair: freeze the confirmation population only after the decode completes (58 % of ranked∩clean decoded at 12:42Z).
3. Chair: registry row for `hinata-v0b` proposed in the P-2 card (status offline).
4. Asahi: native queue job-file format (for R2 builds/training).

## Human-in-the-loop (for the Chair's list)
- R2 training: native Mac via Asahi's queue (D-050 §8) — no separate native Learner session needed if the queue takes `tools/hinata/` jobs.

## Next 3 actions
1. On D-052 + decode complete: `p2_confirm.py manifest` (fresh, frozen) → `run --gate-spec <Chair's spec>` → `score`; append the result card; notify.
2. Draft R2 card (BC direction head on encoder v1 + teacher list v1; per-map held-out-free; R2 gate from macro) and V-legal card (R1b).
3. Build what is VM-sized for R2 (dataset loader over `tools/learn/dataset.py` output, LightGBM direction head prototype on a small train-split shard).
