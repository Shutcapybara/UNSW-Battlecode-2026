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

### cheji bt — calibration and wrapper (Q1 cal, Q2 enumeration; `game_stats/runs/tt70-q1-calibration.json`, `tt70-q2-enumerate-corpus.json`)

- Direction calibration: ECE 0.021; acc 0.751 at mean max-p 0.730; near-deterministic (≥ 0.95) only 17 % of moves
  (Heartbreaker 28 %), near-ties 22 % (13 %) holding 42 % of errors. More of cheji bt's steering is undetermined by
  the local view.
- **Deliberate suicide.** 1.24 % of cheji bt's turns are an invalid command that kills the dragon (`noValidAction`;
  19,590 of 1.58 M turns in a 207-game sample), almost always at length 2, spread over r50–r400, at any unit count.
  Heartbreaker: 0 in 7.3 M turns. Real splits never kill the splitter (33,808 splits, 0 deaths).
- Wrapper, all 4,126 games: trapped & split legal → split 113,501 (98 %), suicide 1,935; **trapped & split not
  legal → suicide 229,728** (Heartbreaker stepped into a wall or an ally head — the latter killing the ally too);
  free exit & split not legal → suicide 141,469 (0.5 %, culling); 0 invalid splits of 694,397. cheji bt dies in place
  rather than take an ally with it, and culls small dragons.
- Tool fix (applies to all teams): HB-1's enumeration and `wrapper.label()` treated every non-move action as a split;
  suicide is now its own command class `X`. Heartbreaker's results are unaffected (no such rows). `q2_command`'s
  per-game sample now scales with `HB_CAP_FACTOR` (its fixed 1,500 rows/game ≈ 15 GB for 4,126 games; the first run
  was terminated at load, likely by memory pressure).

### cheji bt — Q3 stability (`game_stats/runs/tt70-q3-windows.json`)

Static across the well-sampled span: windows 12–16 (28 Sep 18:00 – 30 Sep 00:00 UTC, 94k–287k rows each) agree
within ~1 pp whether fitted within the window, forward or backward (direction 0.726–0.737, gate 0.807–0.824, child
size 0.896–0.912). Change-points at 28 Sep 11:00 and 13:00 UTC coincide with the corpus going from ~5 to 100+ games
per window — most likely sampling, not a new policy. Possible change on 30 Sep: child size fitted on 30 Sep 00–06
scores 0.844 on 06–12 (usual ~0.90), the window with the lowest win rate (0.70, 308 games) — thin, flagged only.
Ladder: Elo 2060–2141, rank 1–5 over 274 snapshots, 2096 at the last.

## Q1 — Stockfish (team 206) (`game_stats/runs/tt206-q1-gaps.json`)

Held-out = 20 % of 1,932 games; sampling caps × 0.5.

| decision | n test | majority | tree depth 4 | GBT | MLP | gap tree→MLP | top drop-family Δacc |
|---|---:|---:|---:|---:|---:|---:|---|
| split gate | 167,190 | 0.805 | 0.872 | **0.934** | 0.912 | +0.039 | scalar −1.66, cand −1.65, grid −1.05 pp |
| direction | 224,125 | 0.516 | 0.664 | **0.771** | 0.753 | +0.090 | cand −11.02, grid −1.77 pp |
| sonar mask | 114,558 | 0.726 | 0.925 | 0.971 | 0.953 | +0.029 | action −11.0 pp |
| child size | 104,022 | 0.740 | 0.871 | **0.980** | 0.962 | +0.092 | scalar −2.16, cand −1.13 pp |
| late gate | 137,277 | 0.961 | 0.978 | 0.979 | 0.977 | −0.002 | cand −0.75 pp |

Three teams, GBT held-out: gate 0.975 (Heartbreaker) / 0.829 (cheji bt) / 0.934 (Stockfish); direction 0.829 /
0.751 / 0.771; child size 0.957 / 0.911 / 0.980; sonar 0.981 / 0.983 / 0.971; late gate 0.9994 / 0.983 / 0.979.

Reading: Stockfish sits between the two. Its production gate is rule-like with **round thresholds** (tree: no exit →
split; in the open, split after eating at length ≤ 4 as Heartbreaker does; branches at rounds ~250 and ~350 — phase
switches by round number, typical of hand-written logic). Child size is the most predictable of the three (0.980,
though a depth-4 tree gets only 0.871). Direction is as hard as cheji bt's (0.771): for both top teams about a
quarter of moves are not determined by the local view (Heartbreaker: a sixth). Sonar differs: single-direction ray
masks (1, 2, 4, 8) appear, which neither other team emits — directed signalling.

## Headline so far — the top teams' edge is the endgame conversion (`tools/tt/concentration.py`, `game_stats/runs/tt-concentration.json`)

Both top teams deliberately kill their own small dragons (~1 % of turns): cheji bt by an invalid command
(`noValidAction`), Stockfish by stepping backward into its own neck (`hitSelf`, 17,317 of 1.92 M turns in a 194-game
sample, 100 % fatal, 65 % at length 2, 56 % with an exit available). Heartbreaker never does.

Medians over running games, subject's dragons / longest / total length:

| round | Heartbreaker | cheji bt | Stockfish | Ares V06 (z1 panel) | hb1-12 (z1 panel) |
|---:|---|---|---|---|---|
| 100 | 19 / 6 / 53 | 22 / 4 / 52 | 24 / 4 / 57 | 20 / 4 / 47 | 24 / 4 / 57 |
| 200 | 25 / 9 / 78 | 40 / 4 / 95 | 40 / 5 / 100 | 29 / 4 / 69 | 36 / 4 / 87 |
| 300 | 28 / 10 / 98 | 51 / 5 / 123 | 35 / 15 / 100 | 30 / 5.5 / 75 | 45 / 6 / 112 |
| 400 | 27 / 11 / 109 | 8 / 25 / 86 | 21 / 32 / 105 | 26 / 9 / 88 | 45 / 9 / 133 |
| 490 | 27 / 13 / 124 | 4 / 40 / 77 | 11.5 / 46 / 100 | 5 / 25 / 63 | 8 / 28.5 / 91 |

| | Heartbreaker | cheji bt | Stockfish | Ares V06 | hb1-12 |
|---|---:|---:|---:|---:|---:|
| round-limit win rate | 0.26 | 0.75 | 0.72 | 0.69 | 0.78 |
| round-limit losses with a material lead | 0.77 | 0.32 | 0.43 | 0.33 | 0.57 |
| longest / total at r490 | 0.10 | 0.46 | 0.37 | 0.39 | 0.30 |

(Our bots' rows are vs the zoo panel, the teams' vs the live ladder — timing comparable, levels not.)

Reading: all run the same swarm economy to ~r200. cheji bt then dissolves its swarm between r300 and r400 (51 → 8
dragons, longest 5 → 25); Stockfish starts ~r250 (its gate tree has round thresholds at ~250 and ~350) and ends
longest (46). Heartbreaker never converts (26 % at the round limit). Ares has the same tactic in code — a feeder
within 4 cells of the crown steps backward into its own neck (`policy.hpp`, why 'f') — but feeders activate only from
`feed_from = 500 − feed_base − 0.6·(W+H)` ≈ r400–r430, ~100–150 rounds after the top teams; it ends at longest 25.
hb1-12 (Heartbreaker's steering on Ares) builds the largest swarm (133 total at r400) and converts on the same late
schedule: 57 % of its round-limit losses are with a material lead — the late-economy dip that kept it at hold.

Experiment (one constant each, on hb1-12): `tt-01-feed300` (`feed_base` 40 → 140, feeding from ~r300, cheji bt's
timing) and `tt-02-feed250` (190, ~r250, Stockfish's). Note the scorecard's economy mean uses pearls to r250, so
these can move win share, not the economy gate.

### Stockfish — calibration and Q3 (`game_stats/runs/tt206-q1-calibration.json`, `tt206-q3-windows.json`)

- Calibration: ECE 0.014; acc 0.771 at mean max-p 0.757; near-deterministic 21 % of moves (99.7 % correct), near-ties
  18 % (Heartbreaker 28 % / 13 %, cheji bt 17 % / 22 %).
- Q3: decisions stable across all eight well-sampled windows (28 Sep 16:00 – 30 Sep 16:00 UTC, 52k–292k rows):
  direction 0.742–0.770, gate 0.903–0.927, child size 0.964–0.980, within / forward / backward within ~1 pp.
  Change-points only at the start of dense data (28 Sep 15:00, 17:00 UTC). Ladder: Elo 1980 → 2079 over the span
  (range 1918–2098, rank 21 → 1–4): the rating rose ~100 while the five per-turn decisions stayed the same — still
  converging, or improvement outside these decisions (concentration timing, directed sonar).
- Self-kill: backward step into the own neck, 0.9 % of turns, 100 % fatal, 65 % at length 2, 56 % with an exit open.

### The cull decision (`tools/tt/cull_model.py`, `game_stats/runs/tt{70,206}-cull.json`)

Turns at length ≤ 3; label = self-kill; same held-out games as Q1; every cull kept and re-weighted to the base rate.

| | cheji bt | Stockfish |
|---|---|---|
| base rate (length ≤ 3 turns) | 1.3 % | 1.0 % |
| by round | < 1.1 % to r300; 2.5 % r300–350; **9.4–10.5 % from r350** | 0.4–0.5 % to r250; **1.8–2.5 % from r250** |
| by distance to nearest ally head | 3.7 % adjacent, ~1 % beyond | 2.9 % adjacent, 1.2 % at 2, 0.6 % at 4, ≤ 0.2 % beyond 5 |
| when trapped (no exit) | 96.8 % | 26.4 % |
| depth-4 tree / GBT (AUC) | 0.954 / 0.991 (recall 0.77 at p ≥ 0.5) | 0.945 / 0.975 (recall 0.43) |
| tree's round threshold | ~r330 | r250 |

Two conversion styles. cheji bt: a **timed mass cull** — from ~r330 every small dragon has ~10 % per turn of killing
itself wherever it is (and trapped small dragons always do). Stockfish: a slower, **proximity-weighted feed from
r250** — small dragons near an ally head die; no elected crown needed. Ares: feeder within 4 cells of an elected crown
steps backward into its neck, from ~r400–430.

Stockfish command-level accuracy (11 classes incl. self-kill; `tt206-q2-command.json`): GBT 0.763 raw / 0.760
wrapped, MLP 0.740 / 0.738 — the Heartbreaker-measured wrapper slightly hurts, since Stockfish handles trapped states
differently (wrapper rules are team-specific). cheji bt's command run was killed twice by `earlyoom` (43 GB, then
40 GB from a stale full-size sample cache); cache removed, re-running at the scaled size.

cheji bt command-level accuracy (`tt70-q2-command.json`, scaled sample): GBT 0.741 raw / 0.733 wrapped, MLP 0.724 /
0.717, tree 0.624. Whole-command predictability from the local view: Heartbreaker 0.826, Stockfish 0.763, cheji bt
0.741 — the stronger the team, the less of its play a local-view model captures; and the Heartbreaker-measured
wrapper slightly hurts both.

## Port 1 — tt-01-feed300 (hb1-12 + feeding from ~r300) vs hb1-12, z1 seed 1 (`game_stats/runs/tt-01-feed300-z1-s1.{json,md}`)

**GATE: fail.** W–L 136–24 vs hb1-12's 139–21 (−1.88 pp); economy mean +0.0000 (pearls to r250 cannot move — the
mechanism starts at r300); own-body deaths 3.37 → 4.62/1k (+37 %) — that rate *is* the mechanism (a feeder dies by
stepping into its own neck), so the hygiene gate penalises deliberate feeding by construction.

Trajectory (`tools/tt/concentration_bot.py`): r400 15 dragons / longest 22 (hb1-12: 45 / 9; cheji bt 8 / 25); r490
4 / 33, share in the longest 0.49 (hb1-12 8 / 28.5, 0.30; cheji bt 4 / 40, 0.46). Round-limit win rate 0.80 (0.78);
round-limit losses with a material lead 20 % (57 %). Elimination W/L 75–9 over 160 games (hb1-12 ~85–6).

Reading: the conversion works as designed — cheji bt's schedule reproduced, material no longer wasted at the round
limit — and it costs elimination wins: dissolving the swarm at r300 removes the pressure that eliminates zoo
opponents. The zoo panel is weak enough that hb1-12 eliminates over half its opponents; cheji bt on the live ladder
wins 49 % by elimination. Against opponents that cannot be eliminated the round limit decides, so this panel
understates early conversion for ladder play. Points to a conditional conversion (keep the swarm while elimination is
on, convert when it is not) rather than a fixed earlier round.

## Port 2 — tt-02-feed250 (hb1-12 + feeding from ~r250) vs hb1-12, z1 seed 1 (`game_stats/runs/tt-02-feed250-z1-s1.{json,md}`)

**GATE: fail.** W–L 131–29 vs 139–21 (−5.00 pp); economy mean +0.0000; own-body deaths +49 % (the mechanism).
Trajectory: total length at r300 91 (tt-01 107, hb1-12 112) — feeding from r250 cuts growth while the swarm is still
compounding; r490 4 dragons / longest 34.5 (tt-01 33); round-limit W/L 59–21 = 0.74 (tt-01 61–15 = 0.80, hb1-12 0.78);
elimination W/L 72–8.

| | hb1-12 | tt-01 (~r300) | tt-02 (~r250) |
|---|---:|---:|---:|
| W–L (160) | 139–21 | 136–24 | 131–29 |
| total length r300 | 112 | 107 | 91 |
| longest r490 | 28.5 | 33 | 34.5 |
| round-limit win rate | 0.78 | 0.80 | 0.74 |
| elimination W/L | ~85–6 | 75–9 | 72–8 |

Reading: r250 is too early for Ares. Stockfish starts at r250 because its feed is slow (~2 %/turn, near allies only);
Ares's feeder is all-or-nothing within 4 cells of the crown, so copying Stockfish's start round without its rate
over-converts. What transfers is the rate schedule, not a start round. On this (weak, eliminable) panel the order is
monotone: the earlier the swarm is dissolved, the more elimination wins are lost.
