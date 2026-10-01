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

## Head-to-heads — does earlier conversion win when elimination is off the table? (`game_stats/runs/tt-h2h-*.json`)

Ten live maps, both seats × 2 seeds, the same 40 fixed fixtures as HB-1 (`tools/hb1/h2h.py`):

| match | result | how |
|---|---|---|
| hb1-12 vs hb1-04 (Heartbreaker mimic) | **33/40** | W: 19 on length, 14 by elimination; L: 6 by elimination, 1 on length |
| tt-01 vs hb1-04 | 29/40 | W: 19 on length, 10 by elimination; L: 7 by elimination, 4 on length |
| tt-01 vs hb1-12 | 19/40 | 9–9 by elimination, 10–12 on length |

Paired vs the mimic: tt-01 turns 4 of hb1-12's wins into losses and gains none. The mimic, like Heartbreaker, never
converts, so hb1-12's late conversion already wins 19 of 20 round-limit games against it; converting earlier only
gives up elimination wins. Direct, early vs late conversion is even.

Reading: no local opponent converts early, so no local test can show whether matching the top teams' timing matters
against teams that do. That needs games against them, or a faithful stand-in — and Q1 says a local-view mimic of
either would copy ~0.74–0.76 of their commands (Heartbreaker 0.83 gave a mimic at half strength), too weak to stand in.
Also a side result worth keeping: hb1-12 beats the Heartbreaker mimic 33/40.

## Memory test (`tools/hb1/q1_history.py`, 400-game subset per team, `game_stats/runs/tt{70,206}-q1-history.json`)

| direction accuracy | v5 | + history | + trail | + both | gain |
|---|---:|---:|---:|---:|---:|
| Heartbreaker (HB-1, all 817 games) | 0.8287 | 0.8302 | 0.8296 | 0.8306 | +0.19 pp |
| cheji bt | 0.7448 | 0.7498 | 0.7543 | 0.7545 | +0.97 pp |
| Stockfish | 0.7624 | 0.7635 | 0.7667 | 0.7663 | +0.39 pp |

Gate: no gain for either (cheji bt 0.8625 → 0.8608, Stockfish 0.9349 → 0.9345). cheji bt uses some memory — the
features that help are its own-position trail (where it has recently been) — but memory does not close the gap: about
a quarter of both teams' moves stay undetermined by the current view plus simple memory of it (global information,
communication, search, or randomness). Supports "not worth a local-view mimic".

## Close of the first pass (30 Sep, ~23:40 ACST)

Q0–Q3 done for both teams, the conversion analysis and cull models done, two ports measured (both fail the gate),
three head-to-heads done. Finding: `docs/findings/2026-09-30-tt-top-teams.md`. Open: conditional (state-keyed)
conversion as the next mechanism; whether the top teams' timing pays against converting opponents (not measurable
locally).

## Upload limit (1 Oct)

The upload zip is capped at 4 MiB, so hb1-12 (17.1 MiB) and the tt-01/tt-02 copies built on it are local-only.
`hb1-14-prior-r540` (the same prior, 540 rounds, 3.74 MiB; 141–19 on z1 s1, hold) is the uploadable base — see
`claude/hb1-status.md`. Further TT ports are built on hb1-14.

## Port 3 — tt-03-proxfeed (hb1-14 + Stockfish-rate proximity feed) vs hb1-14, z1 seed 1 (`game_stats/runs/tt-03-proxfeed-z1-s1.{json,md}`)

From r250, length ≤ 3, not the crown: a strictly longer ally head adjacent → self-kill p = 0.03/turn (distance 2:
0.012). **GATE: fail** — W–L 137–23 vs 141–19 (−2.50 pp), own-body deaths +10.8 %. Trajectory almost unchanged:
r400 33 dragons / longest 10 (parent 32 / 9); r490 7 / 28 (7 / 27); round-limit W/L 59–18 (62–14); elimination W/L
78–5 (79–5). The gradual feed keeps the elimination wins, as intended, but does not concentrate: feeding *any*
strictly longer ally scatters material (a length-3 dragon dying next to a length-4 one). "Near an ally head" is too
loose a reading of Stockfish's rule — which ally matters. (hb1-14's own trajectory: `build/tt/conc_hb1-14-prior-r540.log`.)

### Which ally does a small dragon die next to? (`tools/tt/cull_target.py`, `game_stats/runs/tt{70,206}-cull-target.json`)

Rows: length ≤ 3 after each team's onset round (300-game sample); the nearest ally head and the visible length of its
dragon (flood over connected ally cells in the 7×7 grid — approximate where two allies touch).

| nearest ally's visible length | cheji bt (r ≥ 330): adjacent / distance 2–3 | Stockfish (r ≥ 250): adjacent / distance 2–3 |
|---|---|---|
| 1–2 | 6.2 % / 4.4 % | 3.6 % / 1.6 % |
| 3–4 | 23.9 % / 10.0 % | 4.2 % / 2.4 % |
| 5–6 | 45.0 % / 23.7 % | 6.4 % / 3.4 % |
| 7–9 | 57.4 % / 37.5 % | 7.1 % / 4.1 % |
| 10–14 | 74.1 % / 52.2 % | 8.8 % / 5.1 % |
| 15+ | 81.5 % / 56.4 % | 11.7 % / 9.1 % |
| no ally head in view | 4.3 % | 0.3 % |

**Correction to the "timed mass cull" reading above:** cheji bt's ~10 %/turn is an average. The rule is targeted —
after r330 a small dragon beside a long ally almost always kills itself, one with no ally in view almost never does:
it feeds the long dragon. Stockfish follows the same rule much more gently. tt-03 (flat 3 % beside any longer ally)
encoded the wrong thing. Unlike Ares's feeder (travel to one radio-elected crown, die within 4 cells), this needs no
election and leaves the swarm away from the long dragon alive.

Port 4 — `tt-04-feedlong` (on hb1-14, uploadable): cheji bt's rate table from r330 for length ≤ 3, nearest ally head
within distance 3 and visibly longer.

## Port 4 — tt-04-feedlong vs hb1-14, z1 seed 1 (`game_stats/runs/tt-04-feedlong-z1-s1.{json,md}`)

**GATE: fail** — W–L 136–24 vs 141–19 (−3.12 pp), own-body deaths +74 %. The rule fires (r400: 21 dragons vs the
parent's 32) but the material does not arrive: longest 12 at r400 and 27 at r490 (parent 9 and 27) while total length
falls (r400 81 vs 100; r490 56 vs 73). Small dragons die beside the long one and it does not eat them. Same lesson
as hb1-11: a donor's rule works only with the donor's other behaviour — cheji bt's long dragons evidently collect what
dies beside them; Ares's steering does not. Ares's own crown + feeder logic is co-designed (feeders walk to the crown,
the crown harvests), which is why tt-01 — that logic started earlier — is the one port that concentrated (33).

| port on the direction-prior base | mechanism | z1 W–L vs parent | longest r490 | limit losses with lead | verdict |
|---|---|---|---:|---:|---|
| tt-01-feed300 (on hb1-12) | Ares feeders from ~r300 | 136–24 vs 139–21 | 33 (28.5) | 20 % (57 %) | fail; concentrates, loses eliminations |
| tt-02-feed250 (on hb1-12) | Ares feeders from ~r250 | 131–29 vs 139–21 | 34.5 | 24 % | fail; over-converts |
| tt-03-proxfeed (on hb1-14) | flat 3 % beside a longer ally from r250 | 137–23 vs 141–19 | 28 (27) | 44 % (50 %) | fail; no concentration |
| tt-04-feedlong (on hb1-14) | cheji bt's rate table from r330 | 136–24 vs 141–19 | 27 (27) | 29 % (50 %) | fail; kills without feeding |

## Is there a state that says "convert now"? And is there a converting opponent locally? (`tools/tt/elim_state.py`, `by_opponent.py`)

hb1-14's 160 z1 games: 79 elimination wins, **62 of them before r300**; 96 games alive at r300 → 62 round-limit
wins, 17 late elimination wins, 14 round-limit losses, 3 elimination losses.
- Own unit count at r300 (observable) does not predict a late elimination (spread over every bucket).
- The opponent's unit count does: ≤ 5 opponent dragons at r300 → 14 of 17 elimination wins; > 5 → 3 of 79. Not
  directly observable; "no enemy met for a long time" would be the stand-in.
- Earlier conversion did not reduce round-limit losses (tt-01 15 vs hb1-12's ~14); it changed their kind.

By opponent, round-limit games, median longest at the end (ours / theirs): hb1-14 — chaewon 33.5 / 24, fenrir 25 / 20,
gavroche 32 / 22, hunter 33 / 5, kazuha-s01-swarm-dissolve 24.5 / 17, ouroboros-m01-vibing-mimic 28 / 13, sinbad 31 /
18.5, yuna 27.5 / 24.5. tt-01 raises ours to 30–45 (kazuha 10–0 at the round limit) with no more wins overall.

**No zoo opponent converts like the top teams** (their longest 5–24.5; cheji bt 40, Stockfish 46). The value of the
top teams' conversion against converting opponents cannot be measured on this panel — only on the ladder. For that
test an uploadable early converter is needed: `tt-05-feed300-up` = hb1-14 + `feed_base` 140 (tt-01's change on the
uploadable base).

## Port 5 — tt-05-feed300-up (hb1-14 + feeders from ~r300; uploadable, 3.74 MiB) vs hb1-14, z1 seed 1

W–L **141–19, identical to hb1-14** (win share +0.00 pp, economy +0.0000). GATE reads fail only on own-body deaths
+60 % (3.22 → 5.16/1k) — the feeding mechanism itself. Trajectory: r400 12 dragons / longest 21.5 (hb1-14 32 / 9;
cheji bt 8 / 25); r490 longest 32, 56 % of material in it (27, 34 %; cheji bt 40, 46 %). Round-limit W/L 67–13
(62–14); round-limit losses with a material lead 8 % (50 %); elimination W/L 74–6 (79–5). Five elimination wins
traded for five round-limit wins: break-even on a panel with no converting opponent, with the top teams' conversion
profile. **tt-05 is the uploadable early converter for a ladder comparison against hb1-14.**

| uploadable bot | z1 s1 vs Ares V06 / vs hb1-14 | longest r490 | conversion |
|---|---|---:|---|
| hb1-14-prior-r540 | 141–19 vs V06's 122–38 | 27 | late (Ares default, ~r400) |
| tt-05-feed300-up | 141–19 (= hb1-14) | 32 | from ~r300 (cheji bt's timing) |

## Interpolating hb1-14 → tt-05 through the game (user request, 1 Oct; local, though uploadable)

hb1-14 and tt-05 are the same bot except for one decision — when a dragon near the crown starts feeding it (tt-05
~r300, hb1-14 ~r400). The interpolation hands that decision over gradually: each dragon, each turn, uses tt-05's onset
with probability rising linearly across a window, hb1-14's otherwise (`tools/tt/make_ramp.py`). z1 seed 1, same 160
fixtures:

| bot | W–L | round-limit W/L | elimination W/L | longest r490 | share in longest | gate vs hb1-14 |
|---|---|---:|---:|---:|---:|---|
| hb1-14 (onset ~r400) | 141–19 | 62–14 | 79–5 | 27 | 0.34 | — |
| **tt-05 (switch at ~r300)** | **141–19** | **67–13** | 74–6 | **32** | **0.56** | level (fail only on own-body) |
| tt-06-ramp-300-400 | 138–22 | 61–17 | 77–5 | 31.5 | 0.46 | fail (−1.87 pp) |
| tt-07-ramp-250-450 | 132–28 | 58–23 | 74–5 | 30 | 0.43 | fail (−5.63 pp) |

The ramps keep hb1-14's elimination wins and lose round-limit games the sharp switch wins; the wider ramp loses more.
A swarm that is partly converting gets less concentration than tt-05 without keeping hb1-14's elimination edge. On
this panel the validated choice is a clean switch at ~r300, not an interpolation. Head-to-heads (hb1-14 vs tt-05, each
ramp vs both endpoints, ten live maps) running.

Head-to-heads, ten live maps (`game_stats/runs/tt-h2h-*.json`; 40 fixtures, extended to 80 for the three that bear
on tt-06):

| match | 40 fixtures | 80 fixtures | one-sided p (80) |
|---|---:|---:|---:|
| hb1-14 vs tt-05 | 21/40 | 37/80 | — |
| tt-06-ramp-300-400 vs hb1-14 | 24/40 | 40/80 | 0.54 |
| tt-06-ramp-300-400 vs tt-05 | 23/40 | 43/80 | 0.29 |
| tt-07-ramp-250-450 vs hb1-14 | 20/40 | — | — |
| tt-07-ramp-250-450 vs tt-05 | 21/40 | — | — |

**Conclusion.** tt-06's apparent direct-play edge at 40 fixtures (47/80 combined, p ≈ 0.07) vanished at 80 (40/80,
43/80). In direct play hb1-14, tt-05 and the ramps are equal; against the zoo the ramps are worse (−3 and −9 games).
Interpolating the feeding onset adds nothing and a wide ramp costs round-limit games; the validated choice is a clean
switch, and hb1-14 and tt-05 are interchangeable on every local measure.

## Dummy-bot check (user warning, 1 Oct: some teams — reported for Cutlery and possibly others at its university —
## hide their bot when ranked scrims are not forced and upload a dummy) — `tools/tt/dummy_check.py`

Ranked scrims are forced, so ranked games are the real bot. Per game, a behavioural fingerprint (split rate on
eligible turns, self-kill rate, forward share, turns per round, units / longest / total at r100 and r250); ranked vs
unranked compared, plus the share of games with ≥ 2 fingerprint features > 4 robust-z outside ranked play.

| team | ranked / unranked games | split rate (R / U) | self-kill rate | forward share | outlier share (R / U) | verdict |
|---|---|---|---|---|---|---|
| cheji bt (70) | 619 / 3,507 | 0.311 / 0.326 | 0.007 / 0.007 | 0.495 / 0.495 | 8.1 % / 5.9 % | same bot |
| Stockfish (206) | 414 / 1,518 | 0.237 / 0.215 | 0.005 / 0.006 | 0.523 / 0.520 | 4.8 % / 8.9 % | same bot |

Unranked games show slightly more material and wins (weaker unranked opponents), no dummy cluster: the cheji bt and
Stockfish analyses (all games) stand. The same check runs first on every new team.

## Next two teams (1 Oct): Cache me outside (952, #1, Elo 2096) and forgot to mention (264, #2, 2094)

Ladder 30 Sep 17:15 UTC: #1 Cache me outside, #2 forgot to mention, #3 SSS, #4 cheji bt, #5 Stockfish, #7 Cutlery.
Synced and extracted: Cache me outside 1,608 games (598 ranked), forgot to mention 2,792 (495 ranked), 0 errors.

Dummy check. Fingerprints match (outlier share 2.0 % / 1.5 % and 0.8 % / 1.7 %, ranked / unranked), but split rate is
higher in ranked games within the same 6-hour windows (+0.10 and +0.17) — state or a different policy? Decisive test
(`tools/tt/dummy_policy.py`): GBT fitted on 70 % of ranked games, scored on held-out ranked vs unranked:

| team | decision | ranked held-out | unranked | gap | per window |
|---|---|---:|---:|---:|---|
| forgot to mention | gate | 0.963 | 0.969 | −0.6 pp | equal in all 8 |
| | direction | 0.729 | 0.725 | +0.4 pp | equal in all 8 |
| Cache me outside | gate | 0.981 | 0.976 | +0.5 pp | equal |
| | direction | 0.763 | 0.741 | **+2.2 pp** | ranked ahead in 7 of 8 (+1 to +4 pp) |

forgot to mention: same bot — all games used. Cache me outside: not a dummy (a dummy would collapse), but its
unranked direction policy differs systematically — a variant (older version / other settings). **Distilled from its
598 ranked games only** (`build/tt/team952r`, symlinked ranked subset; caps × 1).

### Q1 — forgot to mention (264; all 2,792 games; caps × 0.3; `game_stats/runs/tt264-q1-gaps.json`)

| decision | n test | majority | tree depth 4 | GBT | MLP | gap tree→MLP | top drop-family Δacc |
|---|---:|---:|---:|---:|---:|---:|---|
| split gate | 140,151 | 0.693 | 0.900 | **0.975** | 0.942 | +0.042 | scalar −5.24, cand −1.56 pp |
| direction | 197,597 | 0.442 | 0.631 | **0.735** | 0.720 | +0.089 | cand −12.44, msgs −0.85 pp |
| sonar mask | 98,966 | 0.644 | 0.893 | 0.964 | 0.942 | +0.049 | action −9.8 pp |
| child size | 171,750 | 0.842 | 0.947 | 0.988 | 0.980 | +0.034 | scalar −1.45 pp |
| late gate | 145,681 | 0.971 | 0.985 | 0.986 | 0.985 | −0.001 | cand −0.74 pp |

A rule-driven production machine: its gate is as predictable as Heartbreaker's (0.975) but far more aggressive
(splits on 31 % of eligible turns vs 10 %): split whenever it has just eaten, while units ≤ 61, until ~r350, with
further round thresholds near 260 and 350 (scalars carry −5.2 pp, the most of any team). Child size is 2 in 84 % of
splits (0.988). Direction is the hardest of any team so far (0.735). Sonar uses single-direction rays, as Stockfish.

forgot to mention — calibration, wrapper, command, stability (`tt264-q1-calibration.json`, `tt264-q2-*.json`,
`tt264-q3-windows.json`):
- Calibration: ECE 0.013; acc 0.735 at mean max-p 0.722; near-deterministic 24 % (99.8 %), near-ties **25 %** holding
  49 % of errors — the most undetermined steering of any team.
- Wrapper: trapped & split legal → split 231,837 but **suicide 99,817 (30 %)**; trapped & not legal → suicide 436,938
  (~98 %); free exit → suicide 29,811 (eligible) / 41,089 (not); 0 invalid splits of 835,879. Self-kill ≈ 2.3 % of
  turns, by invalid command (as cheji bt) — the most aggressive culling of any team; it chooses death over a legal
  split 30 % of the time when trapped.
- Command-level GBT 0.741 raw / 0.726 wrapped (Heartbreaker's wrapper hurts again); MLP 0.717.
- Q3: direction stable (within / forward / backward 0.705–0.735); one behavioural change-point at 29 Sep 18:00 UTC and
  a gate forward-transfer dip to 0.919 — likely an upload. Ladder Elo 2040 → 2094 (range 1992–2098, rank 1–8).

### Q1 — Cache me outside (952; 598 ranked games only; caps × 1; `game_stats/runs/tt952-q1-gaps.json`)

| decision | n test | majority | tree depth 4 | GBT | MLP | gap tree→MLP | top drop-family Δacc |
|---|---:|---:|---:|---:|---:|---:|---|
| split gate | 71,197 | 0.582 | 0.945 | **0.970** | 0.952 | +0.007 | scalar −1.69, memory −1.28 pp |
| direction | 127,269 | 0.383 | **0.584** | **0.758** | 0.734 | **+0.150** | cand −11.71, grid −2.16 pp |
| sonar mask | 44,637 | **0.277** | 0.613 | 0.928 | 0.879 | +0.266 | action −10.81, **cand −4.35** pp |
| child size | 43,212 | 0.945 | 0.977 | 0.997 | 0.986 | +0.009 | scalar −0.41 pp |
| late gate | 27,137 | 0.974 | 0.984 | 0.987 | 0.982 | −0.002 | cand −0.62 pp |

A third style. Most aggressive production of any team (splits on 42 % of eligible turns): split right after eating at
length ≤ 4 until ~r450 (Heartbreaker's rule) and **again within 4 turns of the previous split** (chain-splitting);
memory matters for its gate, unlike every other team. Its steering has the largest tree→GBT gap of any team (+17 pp,
0.584 → 0.758) — the strongest candidate for a learned direction policy. Child size 2 in 94.5 %. Sonar is unlike any
other team: the most common ray pattern covers only 28 % of turns (others 64–78 %), GBT 0.928, and candidate features
matter (−4.35 pp) — state-dependent signalling, likely real communication.

Cache me outside (ranked) — calibration, wrapper, command, stability: ECE 0.021, acc 0.757 at mean max-p 0.736,
near-ties 22 %. Self-kill by the **backward step** (as Stockfish): trapped & split not legal → back 93,842, ally
31,816, wall 5,775; free exit → back 23,336 (culling); 0 invalid splits of 221,047. Command GBT 0.765 / 0.753 wrapped.
Q3: gate transfer 0.955–0.986; one change-point at 28 Sep 21:00 UTC; **Elo 1842 → 2096 (rank 35 → 1)** over the span
— a fast-improving team, which the ranked-only restriction keeps on its current bot.

## The conversion across all four top teams (`tools/tt/concentration.py`, `cull_model.py`, `cull_target.py`)

| round | forgot to mention (dragons / longest / total) | Cache me outside, ranked |
|---:|---|---|
| 200 | 36 / 4 / 90 | 36 / 4 / 87 |
| 300 | 41 / 5 / 106 | 36 / 7 / 101 |
| 400 | 22 / 18 / 108 | 28 / 23 / 112 |
| 490 | 9 / 36 / 94 | 14 / 35 / 110 |

| | Heartbreaker | cheji bt | Stockfish | forgot to mention | Cache me outside (ranked) |
|---|---:|---:|---:|---:|---:|
| longest at r490 | 13 | 40 | 46 | 36 | 35 |
| round-limit win rate | 0.26 | 0.75 | 0.72 | 0.64 | 0.55 (vs strong ranked opponents, their longest 35) |
| self-kill method | none | invalid command | backward step | invalid command | backward step |
| cull rate, length ≤ 3, by round | — | < 1.1 % → ~10 % from r350 | 0.4 % → ~2 % from r250 | ~2 % → 6–7 % from r400 | ~1.6 % → ~3 % from r250 |
| cull beside an ally of length 1–2 / 5–6 / 10–14 / 15+ | — | 6 / 45 / 74 / 82 % | 3.6 / 6.4 / 8.8 / 11.7 % | 6.3 / 11.7 / 23.5 / 37 % | 7.5 / 11.2 / 18.4 / 21 % |

**All four top teams convert, all four cull their small dragons, and all four feed the long one** — a small dragon
beside a long ally is several times likelier to kill itself than one beside a short ally. The strength and timing
differ (cheji bt extreme, Stockfish gentle, the two new teams between). Heartbreaker (rank ~40) is the one that never
does. Four independent top teams converging on one mechanism makes it the lane's most robust finding.

## Memory as a predictor, all five teams (user question, 1 Oct)

Base v5 memory family (in every model) — drop-family Δacc, gate / direction: Heartbreaker −0.31 / −0.96, cheji bt
−0.26 / −1.13, Stockfish −1.02 / −0.57, forgot to mention −0.61 / −0.52, Cache me outside −1.28 / −1.31 (messages
−1.13). History + decayed spatial "trail" test (`q1_history.py`; Cache me outside all 598 ranked games, forgot to
mention 400): direction gain Heartbreaker +0.19, cheji bt +0.97, Stockfish +0.39, forgot to mention +0.52 (0.7327 →
0.7379), **Cache me outside +0.94** (0.7566 → 0.7650; gate +0.22, the only team whose gate gains). The two
learned-looking steerers use the most momentum and memory (Cache me outside's top memory features: its left/right and
turn-rate EWMAs, echo-total EWMA), but under a point — not where their unexplained quarter lives.

Internal map (never tried before): `tools/tt/features_map.py` — per-dragon remembered edges, cell sightings, pearls,
beds; per candidate a wall-aware BFS (radius 12) gives reach beyond the view, frontier distance, remembered-pearl and
ready-bed distances, staleness. Validated on a cheji bt game (blocked agreement with v5 100 %; reach median 78 vs in-view
area 39; 1.4 ms/turn). Extraction (400 games per team, Cache me outside's 598 ranked, Heartbreaker as control) and the
v5 vs v5+map comparison running (`tools/tt/run_map.sh`, `mapmem_chain.sh`).

### Internal map results (`tools/tt/features_map.py`, `q1_mapmem.py`; `game_stats/runs/*-mapmem.json`)

400 games per team (Cache me outside: all 598 ranked), held-out 20 % of those games, GPU GBT, v5 vs v5 + map:

| team | direction v5 → v5 + map | gain | (history + trail gain) | top map features (gain rank of ~300) | gate change |
|---|---|---:|---:|---|---:|
| Heartbreaker | 0.8245 → 0.8325 | +0.80 pp | +0.19 | remembered-pearl BFS distance (8, 9, 11) | −0.05 |
| **cheji bt** | 0.7395 → 0.7654 | **+2.59 pp** | +0.97 | **distance to unexplored cells** (5, 7, 8), reach (9) | +0.06 |
| Stockfish | 0.7616 → 0.7713 | +0.97 pp | +0.39 | remembered reach (5, 6, 7), pearl (9) | −0.08 |
| forgot to mention | 0.7199 → 0.7335 | +1.36 pp | +0.52 | pearl (6), frontier (7, 10), reach (8) | +0.19 |
| Cache me outside | 0.7551 → 0.7626 | +0.75 pp | +0.94 | reach (9, 10, 13), pearl (11) | +0.01 |

Every team's steering uses a remembered map more than momentum or decayed density; cheji bt most — it steers toward
cells it has not seen (exploration). Gates do not use it. For the mimics this means a C++ port of the map memory would
add ~1–2.6 pp of direction agreement; Ares already keeps such a map (`world.hpp`), so a map-aware prior on Ares is
also cheap to compute.

## Mimics and priors for the next two teams (user request, 1 Oct)

forgot to mention:
- `tt-08-ftm-mimic` (local only; `tools/tt/make_mimic.py` on hb1-04's chassis): cull model first (held-out 0.9986),
  die in place when trapped with no legal split, mask-driven sonar; gate 0.972, child size 0.987, sonar 0.957; scaled
  direction GBT (650 rows/game, 255 leaves, 1,282 rounds, 3,846 trees, held-out 0.750; compact parity exact on
  20,000 rows; 15.7 MB at run time).
- Fidelity (`replay_drive_cpp.py`, 40 held-out games, 428,216 turns; now scoring self-kills): family 0.9935,
  direction 0.7545, child size 0.986, **self-kill recall 0.904 / precision 0.983** (10,128 recorded), command
  **0.761**, sonar multiset 0.585, 0 missing replies. (`game_stats/runs/tt264-fidelity-mimic.json`)
- `tt-09-prior-ftm` (uploadable, 3.74 MiB): hb1-14 with forgot to mention's direction model (540 rounds) as the prior.
- Scorecards vs Ares V06 (z1 seed 1, 160 side-games; V06 122–38):
  - tt-09-prior-ftm: **117–43, gate fail** (economy −0.066, win share −3.1 pp). The forgot-to-mention steering is a
    worse prior for Ares than Heartbreaker's (hb1-14).
  - tt-08-ftm-mimic: **91–69, gate fail** (economy +0.081, length +0.074, win share −19.4 pp; own-body deaths
    3.7 → 13.3 /1k — the copied culls). Stronger than the Heartbreaker mimic hb1-01 was against the zoo, but well below Ares.

Cache me outside (ranked games only — its unranked bot is a variant):
- `tt-10-cmo-mimic` (local only): gate 0.969, child size 0.996, sonar 0.906, cull 0.995; scaled direction GBT
  (6,096 trees, 3.1M nodes, held-out 0.788; compact parity exact on 20,000 rows; 48.7 MB header).
- Fidelity (40 held-out ranked games, 421,569 turns): family 0.990, direction 0.804, child size 0.993, self-kill recall
  0.804 / precision 0.729 (9,037 recorded), **command 0.806**, sonar multiset 0.499 (many rays per turn), 0 missing
  replies. (`game_stats/runs/tt952-fidelity-mimic.json`)
- `tt-11-prior-cmo` (uploadable, 3.73 MiB): hb1-14 with Cache me outside's direction model (540 rounds).
- Scorecards vs Ares V06 (z1 seed 1; V06 122–38):
  - tt-11-prior-cmo: **127–33, hold** (economy +0.000, length +0.059, win share +3.1 pp). Below hb1-14 (141–19).
  - tt-10-cmo-mimic: **78–82, gate fail** (economy **+0.242**, length +0.265, win share −27.5 pp; own-body
    3.7 → 13.8 /1k).

Why the mimics have the economy but lose (`build/tt/conc_*.log`, medians over 160 games):

| bot | win | round-limit W/L | round-limit losses with a material lead | longest at r490 | units at r490 |
|---|---:|---:|---:|---:|---:|
| tt-08 ftm mimic | 0.569 | 28–56 | 71 % | 12.5 | 21 |
| tt-10 cmo mimic | 0.488 | 33–71 | 79 % | 10 | 50 |
| tt-09 prior-ftm (Ares) | 0.731 | 49–29 | 10 % | 25 | 5 |
| tt-11 prior-cmo (Ares) | 0.794 | 58–23 | 26 % | 25 | 5 |
| real forgot to mention / Cache me outside (ladder) | — | — | — | 36 / 35 | — |

The mimics copy the swarm (more total material than Ares) and the per-dragon culls, but not the conversion: their
longest dragon at r490 is 10–12.5 against the real teams' 35–36, so they lose round-limit games they lead on
material. The cull model learned *when* a dragon dies, but the feeding target (which ally is "the long one") is a
team-level choice a local-view policy does not see. Ares' crown rule supplies it, which is why the priors win the
round limit.

## Hand-off: Cache me outside swarm early, Ares late (user: "continue reasonable next steps", 1 Oct)

`tools/tt/make_handoff.py NAME MIMIC ROUND`: the mimic decides before ROUND, Ares V06 from it; Ares' World is sensed
every turn and the mimic's moves committed to it, so the map memory is complete at the switch. Local only.

| bot | z1 vs V06 (122–38) | round-limit W/L | limit losses with material lead | longest r490 | elim W/L |
|---|---:|---:|---:|---:|---:|
| tt-10 mimic (no handoff) | 78–82 | 33–71 | 79 % | 10 | 45–11 |
| tt-12 handoff r250 | 121–39 | 66–24 | 38 % | 25 | 55–15 |
| tt-13 handoff r300 | 121–39 | 59–25 | 8 % | 26 | 62–14 |
| tt-14 handoff r350 | 118–42 | 66–30 | 20 % | 26 | 52–12 |
| hb1-14 (reference) | 141–19 | 62–14 | — | — | 79–5 |

- The hand-off repairs the conversion (longest 10 → 26) and brings the mimic level with V06, not above it. Economy is
  +0.24 up to r250 (+0.44 at r50, fading to +0.08 by r250), wall deaths −78 %, own-body deaths up (the copied culls).
- Against hb1-14 it gives up elimination wins (62 vs 79), loses 6 eliminations to the Vibing mimic (hb1-14: 2) and is
  2–8 at the round limit against yuna. The early swarm's material does not turn into kills.
- tt-15 = same swarm handing off to hb1-14 (Heartbreaker prior) at r300 (`tools/tt/make_handoff_hb.py`; both
  direction models in one binary, Heartbreaker's renamed `dirhb_*`): **122–38**, identical to V06 and to the plain
  hand-off. The Heartbreaker prior after r300 adds nothing, so hb1-14's +19 wins come from its steering in the first
  300 rounds, which is exactly the phase the swarm replaces. **The early-swarm line is closed** for this panel.
- Next: a prior-weight sweep on hb1-14 (λ was fixed at 1.0 before screening and never swept).

## Prior-weight sweep and map-regime selector (1 Oct)

Prior weight λ on hb1-14 (z1 vs V06 122–38): 0.5 → 129–31 fail; 1.0 → 141–19 hold; **2.0 → 144–16 pass** (seed 2:
139–21 pass; `hb1-17-prior-lam20`, uploadable); 4.0 → 140–20 pass.

Per-map analysis → see findings ("per-map specialists"). Selector `tools/tt/make_regime.py` (feeding onset by local
regime features, no map names), two z1 seeds each (320 games):

| bot | rule | s1 | s2 | total |
|---|---|---:|---:|---:|
| hb1-17 | — | 144–16 | 139–21 | 283–37 |
| hb1-19 | feed_base 140 if W·H ≥ 1100 or ≥ 4 portal edges/100 seen cells | 142–18 | 141–19 | 283–37 |
| hb1-20 | same, feed_base 200 | 135–25 | 132–28 | 267–53 |

Per map (hb1-19 vs hb1-17, 32 games each): elimination maps identical in wins (Devil, Dilemma, Queen, Trophy
bit-identical; Default/Autarky game lengths differ because the portal rule fires locally on Default); Portals 25 → 29,
Schooltime 27 → 24, Slithery 24 → 23, Trauma 31 → 31. Ares' onset already scales with W + H, so large maps are already
early; the small portal-dense map is where the earlier onset helps. → `hb1-21-portal-feed140` (portal rule only,
threshold 5/100), tested on Portals over 10 seeds (`build/tt/mapduel/`, `run_panel --maps`).
