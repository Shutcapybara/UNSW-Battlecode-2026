# HB-1 status — Heartbreaker (team 62) anatomy

Prompt: `docs/hub/prompts/2026-09-30-HB1-heartbreaker-anatomy.md`. Branch `r/hb1`, worktree `../wt-hb1`
(desktop, `~/Documents/Projects/2026/`; the original `~/Projects` checkout was wiped at ~07:25 ACST 30 Sep and the
uncommitted Q0 scaffolding was rebuilt from the session transcript, then pushed step by step).

## Q0 — data + extractor (done, 30 Sep)

- `tools/hb1/sync_from_mac.sh` — the prompt's data recipe plus `public_replays/team-62/` (era-labelled replays).
  Re-run to pick up new games.
- `tools/team_recon_claude/features_v5.py` — v4 actor-local row, versioned; one parquet (+ `.traj.json`) per game.
- `tools/hb1/build_dataset.py --jobs 14` — `build/hb1/games.parquet` + `build/hb1/v5/{corpus,era}/`; incremental.

| set | games | span (UTC) | win rate | ranked | maps | opps |
|---|---|---|---|---|---|---|
| corpus | 817 | 27 Sep 20:18 – 29 Sep 21:48 | 0.590 | 384 | 10 | 46 |
| era (27 Sep packets, sub ids) | 180 | 21 Sep – 27 Sep 14:11 | 0.617 | 97 | 14 | 50 |

Extraction: 997/997 games, 0 errors, 7m46s on 14 jobs; ~10k actor-turn rows/game, 294 columns. Corpus and era
sets do not overlap. The corpus covers only 10 maps (era set 14), so map-cliff comparisons must use the era set.

## Q1 — five decisions (done; `tools/hb1/q1_decisions.py`, raw `game_stats/runs/hb1-q1-gaps.json`)

Holdout = 163 of 817 corpus games (by game, seed 62); map-identifying columns (W, H, x, y, facing_abs, map) excluded.
GBT = XGBoost on the GPU (63 leaves, lr 0.1, early stop) — CPU boosting starved under the R-lane panel load;
on gate/alloc it matches sklearn HistGBT to 0.05 pp. MLP = 256-128 ReLU, 12 epochs.

| decision | n test | majority | tree depth 4 | GBT | MLP | gap tree→MLP | largest drop-family Δacc |
|---|---:|---:|---:|---:|---:|---:|---|
| gate (split-eligible turns) | 128,379 | 0.903 | 0.952 | 0.975 | 0.970 | +0.018 | candidates −1.27 pp |
| direction (F/R/L) | 179,436 | 0.534 | 0.685 | 0.829 | 0.814 | **+0.129** | candidates −14.0 pp |
| sonar mask | 94,761 | 0.699 | 0.937 | 0.981 | 0.966 | +0.029 | action taken −9.6 pp |
| alloc (child size) | 34,445 | 0.753 | 0.918 | 0.957 | 0.943 | +0.025 | scalars (length) −0.99 pp |
| late gate (r≥350, len≥8) | 48,345 | 0.960 | 0.9993 | 0.9994 | 0.9988 | −0.001 | candidates −0.93 pp |

Reading: **direction is the learned part; the other four are rules.**
- Late gate = "split iff no exit of any kind (portals included)" (tree 99.93 %; "no ordinary exit" alone 99.54 %).
  Late splitting is only an escape reflex — no productive late splits, consistent with the concentration weakness.
- Gate depth-4 tree: no exit → split; in the open → split iff it just ate and length ≤ 4 (the 2+2 production
  split), plus an opening split at r0–1. The tree→GBT 2.3 pp is the fuzzy edge of that production rule.
- Alloc: `length−2` baseline 77.9 %, child-2 75.3 %; only length/units matter (other families < 0.5 pp).
- Sonar: keyed to the action just taken and own-body layout (grid −1.4 pp); received messages −0.05 pp
  (no receiver response, as on 27 Sep).
- Direction ablations: candidates −14.0, grid −2.0, local −1.2, memory −0.96, scalars −0.89, messages −0.86 pp.
  Messages matter 9× more for direction than for the gate: the echo counts inform steering.

Direction calibration (`tools/hb1/q1_calibration.py`, `game_stats/runs/hb1-q1-calibration.json`): the v5 GBT is
calibrated and slightly under-confident (ECE 0.022; acc 0.829 at mean max-p 0.808). 28 % of held-out moves have
max-p ≥ 0.95 at 99.2 % accuracy (rule-like); 12.8 % are near-ties (top-2 gap < 0.2) at 52 % accuracy and hold 36 % of
all direction errors. A copy that samples from these probabilities would agree 73 % move-for-move (argmax 83 %).
The residual is what a sampled policy or unseen state produces; the replays cannot tell which.

Memory beyond the current view (`tools/hb1/q1_history.py`, `game_stats/runs/hb1-q1-history.json`; user's suggestion):
action history (last 6 actions, turn / left-right EWMAs, since-turn, eats in 10) and a decayed spatial "trail"
(enemy/ally segment and head mass + centroid in the egocentric frame at decay 0.7/0.9, own-position trail, EWMAs of
the five echo counts, Δdensity×step gradient). Same rows as Q1 (verified), same held-out games, GPU GBT:

| decision | v5 | + history | + trail | + both | MLP + both |
|---|---:|---:|---:|---:|---:|
| direction | 0.8287 | 0.8302 | 0.8296 | 0.8306 | 0.8167 |
| gate | 0.9747 | 0.9746 | 0.9746 | 0.9745 | 0.9702 |

+0.19 pp at most. The top 24 features by GBT gain are all current-view candidate features (forward run, blocked
neighbours, reachable area, pearl distance, ally heads within 2); the first memory feature is the turn EWMA at #25.
Steering is a function of the current local view — consistent with a memoryless (feed-forward) policy, though these
summaries only show that no predictable memory signal of this form exists. The engine's echo is five aggregate counts
(no direction), so an echo EWMA is the most any bot could keep from sonar. Conventions verified on data before use.

## Q2 — wrapper vs policy (done; `tools/hb1/wrapper.py`, `q2_enumerate.py`, `q2_command.py`)

Enumeration over all 7.3 M corpus actor-turns (`game_stats/runs/hb1-q2-enumerate-corpus.json`):

| state | observed |
|---|---|
| ordinary exit free | never wall / own body; ally cell 12 times in 7.08 M; enemy-head attacks 9,575 (policy) |
| no ordinary exit, no portal, split-eligible | split 89,986 / 90,072 (99.9 %) |
| no ordinary exit, portal, not eligible | portal 20,387 / 20,413 |
| no ordinary exit, portal, eligible | portal 7,204 vs split 5,387 — the one mixed blocked state (policy) |
| no exit at all, not eligible | ally **head** if adjacent (F>R>L), else forward — deterministic in a 1/3 sample; every such move dies |
| split sizes / capacity | 0 invalid of 186,440 |

Command-level accuracy (10 classes: F/R/L, SPLIT 2..8; raw `game_stats/runs/hb1-q2-command.json`). Trained on the
654 corpus training games; tested on the 163 held-out corpus games and on the 180-game era set (≤27 Sep, older
submissions — the era the 27 Sep packet's 66.45 % was measured on).

| policy | corpus raw | corpus wrapped | era raw | era wrapped | raw invalid picks (corpus / era) |
|---|---:|---:|---:|---:|---|
| class prior | 0.522 | 0.641 | 0.497 | 0.612 | 18.1 % / 17.7 % |
| tree depth 4 | 0.670 | 0.675 | 0.650 | 0.654 | 1.8 % / 1.3 % |
| GBT | 0.826 | 0.826 | 0.799 | 0.799 | 0.9 % / 0.8 % |
| MLP | 0.806 | 0.807 | **0.655** | **0.703** | 1.0 % / 7.8 % |

Reading: the 66 % ceiling is broken by capacity and the v5 candidate features (GBT 82.6 % / 79.9 %), not by the
wrapper — in distribution both learners have absorbed the wrapper. The prompt's test holds where it matters: the
same MLP out of time (era) is at 65.5 % raw with 7.8 % invalid picks and 70.3 % wrapped. The wrapper is the part to
copy verbatim (it is exact and costs nothing); it protects a learned component when that component is off
distribution. Observed commands outside the wrapper: 0.0014 % (corpus), 0.0032 % (era). The wrapper forces 0.9 % of
rows at 98.9 % agreement.

Next: Q3 (`tools/hb1/q3_windows.py`, queued after the memory-feature test).
