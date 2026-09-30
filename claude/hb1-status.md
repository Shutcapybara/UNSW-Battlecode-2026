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

Follow-up queued (`tools/hb1/q1_history.py`, user's suggestion): does memory beyond v5 help direction / gate —
action history (last 6 actions, turn EWMA) and a decayed spatial "trail" family (enemy/ally segment and head mass +
centroid in the egocentric frame at decay 0.7/0.9, own-position trail, echo-count EWMAs, Δdensity×step gradient).
Conventions verified on data: single-step displacement matches the frame tables 99.8 %, neck at g_-1_0 99.8 %.

Sonar (Q1d, descriptive): emitted on every turn the actor survives, always 4 rays. At length 2 the mask is all four
directions; at length ≥3 a turn (L or R) drops the new back (neck) ray ~91 %; a forward move drops it only ~28 %.

Q1(e) late concentration, from the per-game trajectories (`build/hb1/q1/traj_summary.csv`):

| set | games | elim W / L | round-limit W / L | limit losses with total-material lead | median longest in those losses (self / opp) |
|---|---:|---|---|---:|---|
| corpus (27–29 Sep) | 817 | 380 / 44 | 102 / 291 | 223 / 291 (77 %) | 12 / 27 |
| era (≤27 Sep) | 180 | 84 / 12 | 27 / 57 | 44 / 57 | 12 / 24 |

Paired within-game medians in round-limit games, r400→end: Δunits 0, Δtotal +21, Δlongest +2 (corpus); the
27 Sep packet's −1 / +19 / +2. The weakness is unchanged and now covers 87 % of all their losses.

## Q2 — in progress (`tools/hb1/wrapper.py`, `q2_enumerate.py`, `q2_command.py`)

Enumeration over all 7.3 M corpus actor-turns (`game_stats/runs/hb1-q2-enumerate-corpus.json`):

| state | observed |
|---|---|
| ordinary exit free | never wall / own body; ally cell 12 times in 7.08 M; enemy-head attacks 9,575 (policy) |
| no ordinary exit, no portal, split-eligible | split 89,986 / 90,072 (99.9 %) |
| no ordinary exit, portal, not eligible | portal 20,387 / 20,413 |
| no ordinary exit, portal, eligible | portal 7,204 vs split 5,387 — the one mixed blocked state (policy) |
| no exit at all, not eligible | ally **head** if adjacent (F>R>L), else forward — deterministic in a 1/3 sample; every such move dies |
| split sizes / capacity | 0 invalid of 186,440 |

Command-level accuracy (10 classes: F/R/L, SPLIT 2..8), held-out corpus games / era set:

| policy | raw | wrapped | era raw | era wrapped |
|---|---:|---:|---:|---:|
| class prior | 0.522 | 0.641 | 0.497 | 0.612 |
| tree depth 4 | 0.670 | 0.675 | 0.650 | 0.654 |
| GBT, MLP | pending | | | |

Observed commands outside the wrapper: 0.0014 % (corpus). The wrapper forces 0.9 % of rows at 98.9 % agreement.
27 Sep reference: 66.45 % command accuracy (greedy local routing 62.43 %).

Note: the desktop is shared with the R-lane panels (load ~100 on 16 cores at 08:25 ACST); the GBT fits are running
very slowly under that contention.
