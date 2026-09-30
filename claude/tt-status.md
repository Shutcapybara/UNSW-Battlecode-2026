# TT status — top teams: cheji bt (team 70) and Stockfish (team 206)

User request (30 Sep 2026, ~21:30 ACST): run an HB-1-style analysis on the top two teams, cheji bt and Stockfish,
using what HB-1 learned. Branch `r/tt` (from `r/hb1` at `bfd67c37`), worktree `../wt-tt`. HB-1 method and tools:
`docs/findings/2026-09-30-hb1-heartbreaker.md`, `tools/hb1/`.

## Targets and data

Ladder snapshot 30 Sep 12:11 UTC: #1 cheji bt (id 70, Elo 2096), #4 Stockfish (id 206, 2079; #2–#4 within 2 Elo).
Mac corpus: cheji bt 4,130 games (25 Sep 18:20 – 30 Sep 11:57 UTC), Stockfish 1,931 (26 Sep 22:12 – 30 Sep 12:11).
No submission ids (as for Heartbreaker after 28 Sep).

## Tooling

HB-1's Q0–Q3 scripts are parameterised by `HB_TEAM` (team id), `HB_BUILD` (build dir under `build/`) and `HB_TAG`
(output prefix in `game_stats/runs/`); team 62 defaults unchanged. `tools/hb1/sync_team.sh TEAM` pulls a team's
replays from the Mac. Per team: `HB_TEAM=70 HB_BUILD=tt/team70 HB_TAG=tt70`, `HB_TEAM=206 HB_BUILD=tt/team206
HB_TAG=tt206`.

## Plan

1. Q0 data: sync, extract v5 rows for every game.
2. Q1 structure per team: the five decisions' tree / GBT / MLP gap table and drop-family ablations; the memory test.
   What decides the rest: a large tree→GBT gap with high accuracy on one decision means a learnable policy
   (Heartbreaker's shape); low accuracy with no gap and memory features helping means search or state beyond the
   7×7 view, which a local-view mimic cannot copy — that changes what is worth porting.
3. Q2 wrapper enumeration; Q3 stability over time windows (plus ladder).
4. Q4 mimic and Q5 component ports onto Ares V06 only where Q1 says they pay (HB-1: a learned direction prior was the
   only port that held; hb1-12).

## Q0 — data (corpus index profile, 30 Sep)

Synced 5,953 replays (4.8 GB; `tools/hb1/sync_team.sh`, 3.5 min): cheji bt 4,126 completed games, Stockfish 1,932,
105 shared (their head-to-heads).

| | cheji bt (70) | Stockfish (206) |
|---|---|---|
| games / win rate | 4,141 / 0.806 | 1,932 / 0.692 |
| ranked share / opponents / maps | 0.15 / 116 / 12 | 0.21 / 71 / 10 |
| best maps | Queen of Spades 0.97, Schooltime 0.90, Default 0.88 | Portals 0.80, Schooltime 0.80, Slithery Fight 0.79 |
| weakest maps | Slithery Fight 0.62, Prisoners Dilemma 0.72 | Prisoners Dilemma 0.52, Devil 0.54 |
| head-to-head | 69 / 105 (0.66) | 36 / 105 |

cheji bt's weakest map is Stockfish's best (Slithery Fight — also Heartbreaker's weakest).

Extraction (`HB_TEAM=… tools/hb1/build_dataset.py --jobs 14`): cheji bt 4,126 / 4,126 games, Stockfish 1,932 / 1,932,
0 errors, ~40 min for both on the quieter evening host. Q1–Q3 run as `tools/tt/q13_chain.sh` (per-game sampling
caps × 0.25 for cheji bt, × 0.5 for Stockfish, keeping ~1 M rows per decision as in HB-1). The memory test
(`q1_history.py`, ~16 s/game in Python) is deferred: it runs on a game subset only if Q1 points to state beyond
the current view.

## Q1 — cheji bt (team 70) (`game_stats/runs/tt70-q1-gaps.json`)

Held-out = 20 % of 4,126 games (by game, seed 62); sampling caps × 0.25.

| decision | n test | majority | tree depth 4 | GBT | MLP | gap tree→MLP | Heartbreaker GBT | top drop-family Δacc |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| split gate | 191,397 | 0.725 | 0.779 | **0.829** | 0.817 | +0.038 | 0.975 | scalar −1.43, local −1.22, cand −1.18 pp |
| direction | 246,010 | 0.485 | 0.638 | **0.751** | 0.738 | +0.100 | 0.829 | cand −11.46, grid −1.78 pp |
| sonar mask | 115,986 | 0.775 | 0.950 | 0.983 | 0.975 | +0.025 | 0.981 | action −10.26 pp |
| child size | 138,771 | 0.790 | 0.858 | 0.911 | 0.898 | +0.041 | 0.957 | scalar −1.22 pp |
| late gate | 257,731 | 0.965 | 0.981 | 0.983 | 0.982 | +0.001 | 0.9994 | cand −0.61 pp |

Reading: cheji bt is far less predictable from the dragon's own 7×7 view than Heartbreaker. Its split gate is not a
rule (splits on 27.5 % of eligible turns vs Heartbreaker's 9.7 %; "split iff no ordinary exit" 0.766; GBT only
0.829, no family dominates); direction tops out at 0.751 (Heartbreaker 0.829) with a similar tree→GBT gap; child
size is more varied (40k splits in the 8+ class). The late-gate tree branches on messages received and ally-head
echoes. Decisions depend on something the local view lacks — search, longer memory or shared information — so the
memory test is worth running on a game subset, and a local-view mimic should be expected to copy it less well.
