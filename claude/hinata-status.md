# hinata — Phase 3 Learner (Claude Opus) — status

Updated 2026-10-04 10:52Z. State: **R1 fitted on a provisional split. V0b (logistic Φ + queen) passes the proposed gate, fails the macro text; awaiting Chair ruling + frozen splits.**

## Host and tree
- Running as a **Cowork VM session** linked to the Mac, not the native Claude Code session the Learner prompt assumes.
  VM: 4 cores, 3-min calls, its own disk full (Python libs installed under `/tmp/hpy`, lost on VM reset).
  R1 (V0) is small enough for the VM (a full fit takes ~45 s; background jobs are killed at call end, so `fit` is resumable). R2+ (BC on millions of dragon-turns, C++ export,
  panels) needs the native Mac session; see "Human-in-the-loop" below.
- No `r/hinata` branch yet: git writes over the mount are not allowed from the VM. Until a native worktree exists, the lane's
  files are new files only — `tools/hinata/`, `docs/learning/proposals/P-hinata-*`, `claude/hinata-status.md` — committed by
  the keeper. Scratch and run outputs: `build/hinata/` (never committed).

## Schedule
- Scheduled task "Hinata Learner unit (2-hourly, :35)" (trig_011nsKjZh633yiPiJE5uAndr), every 2 h at :35 UTC from 12:35Z. Fresh session per run; state = this file. Lock: build/hinata/unit.lock.
- Last BOARD line read: 10:52 UTC hinata (own R1 result).

## Ladder (Learner rungs)
| Rung | State |
|---|---|
| R1 V0 | P-hinata-01 (GBT, P .25): **FAIL** — queen mechanism confirmed (RL r150/250/400 ΔAUC +0.03/+0.06/+0.11, lb > 0) but GBT miscalibrated out of map (slopes 0.58–0.88) and −0.005…−0.03 early. P-hinata-02 (Φ's logistic + 2 antisymmetric queen terms, pre-registered with two gates): **G-amend PASS, G-asis FAIL** (as predicted, .6/.03); RL r50 0.671 vs Φ 0.651, r400 0.876 vs 0.775, calibration ≥ Φ's. Provisional held-out Autarky/Maze/Trauma (`docs/learning/splits/PROPOSED-hinata-heldout-maps.json`) not scored. |
| R2 P1 | Not started. Needs Data's encoder + labels (R0). |
| R3–R6 | — |

## Open requests
1. Chair: freeze the Phase 3 splits. I proposed Autarky/Maze/Trauma (one per multi-map C7-03 class; large-gap maps per
   council:sugawara). If adopted → authorise one `confirm`; if not → one refit on the frozen list, which alone gates.
2. Chair: rule G-amend vs G-asis for R1 (P-hinata-02). Φ itself fails G-asis's slope band on post-m2 RL r25–r150, so G-asis
   cannot be passed by any model that ranks like Φ.
3. Chair/Council: the founding D-record number (council:sugawara flagged the D-045 collision at 10:40Z).

## Human-in-the-loop (for the Chair's list)
- Either start the Learner as a native Claude Code session on the Mac (`../wt-hinata`, branch `r/hinata`), or keep this VM
  lane for R1 only and hand R2+ to a native session.

## Next 3 actions
1. On the Chair's ruling: `confirm` (or one refit) — `tools/hinata/v0.py fit|confirm --model-class lr_q --splits <manifest>`.
2. Score our own games with V0b: the per-map value gap (us vs top ten) by checkpoint, for the Chair and testers.
3. Draft the R2 card (BC direction head, hb1 features + H-Q8 block) against Data's encoder spec.
