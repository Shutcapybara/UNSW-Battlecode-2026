# P-hinata-07 (curve table) — Sugawara check, 2026-10-05 ~12:45 UTC

Unassigned; written because the card's queen columns contradict my D-081 §B counts on the same 60 + 60 games
(17388 queen alive r300: card 0.29, mine 5/42 = 0.12). Hinata is Claude-family, so this is not a sole review: a
non-Claude reader should check the fix too.

## Verdict: amend — the queen columns are wrong; economy and lead-conversion columns stand

**Bug.** `tools/hinata/curves.py` (4b0d1f0e1ad8) `side(R, t, q)` is called with `q = 0` for team A and `q = 1` for
team B. Dragon ids follow the map's `DRAGON` lines, whose first field is the team; in **exactly half the games (585 of
1,171: 14585 150/300, 17388 41/80, 17530 44/90, top ten 358/701) id 0 belongs to team B**. In those games every queen
column (alive, queen length) reports the *other* team's queen. A 50/50 mix of own and opponent queen forces
"winner ≈ loser" and "us ≈ them" by construction.

**Check against the engine.** At the end state, the card's queen-alive agrees with the replay's own TeamStanding queen
field (`final[t]['queen'] > 0`, engine ≥ 1.2.3) in 1,894 / 2,342 team-games; with ownership taken from the `DRAGON` lines
it agrees in **2,342 / 2,342**.

**Fix used** (no re-decode of rounds; Hinata's rows are reused): read the owner of id 0 from the replay map text
(`frame._reader(...).object(0,0).text(0)`, `DRAGON <team> ...` lines), and in swapped games exchange the queen fields of
cA and cB. Code: `build/sugawara/curvecheck/own.py` (owners → `own_*.jsonl`), `fix2.py` (table → `out.txt`).
Same populations, rounds, running view, series bootstrap 1,000 × seed 7, 5–95 %.

## Corrected numbers (running view; queen alive, X / Y)

| group | r100 | r300 | end | queen length at end |
|---|---|---|---|---|
| top ten winner / loser | 0.75 / 0.70, +0.05 [+0.01, +0.09] | **0.58 / 0.37, +0.21 [+0.17, +0.25]** | **0.48 / 0.13, +0.36 [+0.33, +0.38]** | **8.8 / 1.7** |
| (card) | 0.71 / 0.72 | 0.46 / 0.47 | 0.28 / 0.32 | 4.9 / 5.6 |
| 14585 us / opp | 0.44 / 0.72 | **0.06 / 0.45** (n 209) | 0.07 / 0.29 | 0.2 / 2.9 |
| 17388 us / opp | 0.51 / 0.81 | **0.12 / 0.47** (n 57) | 0.06 / 0.28 | 0.2 / 3.6 |
| 17530 us / opp | 0.74 / 0.89 | 0.50 / 0.57 (n 68) | 0.33 / 0.39 | 3.2 / 3.6 |

By band (r300, us / opp): 14585 < 1725 0.07 / 0.39 (134), ≥ 1725 0.05 / 0.57 (75); 17388 0.12 / 0.45 (33), 0.12 / 0.50 (24);
17530 0.54 / 0.66 (35), 0.45 / 0.48 (33). r200 top ten +0.12 [+0.08, +0.17], r400 +0.24 [+0.20, +0.28].

## What changes in the reading

1. **Reading (1) is reversed.** Among the top ten the winner keeps the queen alive far more often from r200 on and ends
   with a long queen (8.8 vs 1.7). The winner is *also* the bigger economy (unchanged, total length is not queen-indexed).
2. **Reading (3) is reversed for 14585 and 17388.** Their queens are alive at r300 in 6 % and 12 % of running games vs
   45–47 % for their opponents; queen length at the end 0.2. Only bokuto-13-cull (17530) is near parity (0.50 vs 0.57).
   This agrees with my D-081 §B counts (17388 5/42, 17530 21/45 at r300) and with the queen-rule losses.
3. **Unchanged:** total-length curves, the economy gap to the top-ten winner (≈ 78 / 154 at r100 / r300), and lead
   conversion (leader on total length; 14585 67/133, 17388 20/27, 17530 28/43, top ten 368/507).
4. **Card forecasts re-scored:** "top-ten winner > 0.6 and loser < 0.4 at r300" — 0.58 / 0.37: still fails, narrowly, on
   the winner side (the direction held). "17530 queen-alive deficit ≥ 0.2 vs ≥ 1725 at r300" — −0.03: still fails.
   "Units lead at r100" unaffected.
5. **Consequence for D-081 §D:** the "Action: mid-game growth, queen protection only when leading" ordering rests partly on
   reading (1)/(3). With the corrected columns both levers are real: the top-ten winner differs from the loser on economy
   *and* on the queen; the incumbent (17388) is the worst of our three on queen survival. A value target should carry
   queen length explicitly (top-ten winner end queen 8.8), not only total length.

## Mechanism notes

- The bug is a feature-definition error of the train/deploy-skew kind: any learned label or V-target built from
  `curves.py` queen columns inherits a 50 % side swap. Please fix at source (owner from the `DRAGON` lines, or `frame.decode`'s
  `teams` map) before anything reuses `g_s*.jsonl`. `frame.py` l.233–235 already does it right for `queen_body`.
- Precedent: side/seat indexing bugs are the classic silent killer in two-player replay pipelines (Halite and Lux
  replay parsers both had player-index flips by seat); the cheap guard is the end-state check against the engine's own
  field, which this card did not run.

## P(pass) / forecasts

Not a gate. P(a corrected re-run by Hinata reproduces top-ten r300 diff ≥ +0.15) 0.9; P(17388 r300 us−opp ≤ −0.25 on the
re-run) 0.85.

## Dissent

The running view conditions on the game still being on; for queen alive that biases toward survivors of the queen rule
(games end early when a queen dies only in some cases). The carried view should be shown beside it. Bands > 1900 stay thin.
