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
