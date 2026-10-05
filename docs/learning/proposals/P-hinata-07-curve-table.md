# P-hinata-07 — The curve table (D-080 §B, moved to Hinata by D-081 §D)

Filed 2026-10-05 11:37 UTC, before any curve is computed. Lane: hinata (Learner, service). Rung: R0 (description; no model, no gate).

## Claim
A by-round description of the ranked games shows where and when we fall behind: units, total length, longest, queen
alive and queen length, ours and the opponent's, every 25 rounds, split by opponent rating at game time, with the top
ten among themselves (winners vs losers) as the reference shape.

## Populations (frozen)
- **Ours** (team 7, ranked, completed, post-m2 = started ≥ 2026-10-02T03:49Z, decided before 11:24Z on 5 Oct):
  - 14585 (carthage-05): its last 300 such games before 02:13Z on 5 Oct (the P-06 reference era, superset of the 120-game reference);
  - 17388 (kenma-03-pocket-queen): all its games started before 11:24Z (trial window 05:02–07:13Z and nothing else);
  - 17530 (bokuto-13-cull): all its games started before 11:24Z.
- **Opponents:** the other side of those games.
- **Top ten:** ranked, completed, post-m2 games in which both teams are in the top ten non-dev teams (by elo) of the
  last ladder snapshot before the game (706 games, 22 teams at the time of filing); each game gives a winner curve
  and a loser curve.
- **Band** = opponent elo in the last snapshot before the game: < 1725, 1725–1900, > 1900 (D-080 §B).

## Measures (frozen)
At the start of rounds 0, 25, …, 475 and at the end (final state): units, total length, longest, queen alive (0/1),
queen length (0 if dead). Queen = the team's lowest-id initial dragon (the engine's 1.2.3 definition). Per cell the
denominator is the games still running at that round (n reported); a second view carries ended games forward at their
final state (labelled 'carried'). Our-minus-opponent differences per cell with a series bootstrap (1,000 × seed 7,
linear 5–95 %). Descriptive only: no test, no tuning, no map identity, no held-out use.

## Expected (stated now)
Below 1725 we are level or ahead by round 100 and at the end; at ≥ 1725 we lead or are level on units at r100 and fall
behind on queen alive from about r150 and on queen length from r300; top-ten winners have a queen alive at r300 in
> 60 % of games (loser < 40 %). P(the units lead at r100 against ≥ 1725 for 17530 is > 0) 0.65; P(our queen-alive
deficit vs ≥ 1725 opponents at r300 is ≥ 0.2 for 17530) 0.6.

## Falsifier / stop rule
A description cannot fail; it is wrong if a re-run on the same populations does not reproduce it. One pass; if a
decode error rate exceeds 2 %, report and stop.

## Cost
≈ 1,100 replays × 1.6 s decode on the VM (4 shards, ≈ 4 calls of 150 s). tools/hinata/curves.py (decode →
build/hinata/curves/g_s*.jsonl, resumable) and curves_table.py (aggregate → build/hinata/curves/table.csv, card).

## RL translation
Observation: round index and opponent strength are the state axes along which our value diverges. Value/reward: the
round at which the curves split gives a horizon for a shaped auxiliary (queen alive/length at r300). Action: none
directly. Demonstration: the top-ten winner curves are the target trajectory shape.

## Result (2026-10-05 11:44 UTC) — one pass, as frozen
Decoded 1,171/1,171 (0 errors): 14585 300 games / 60 series, 17388 80 / 16, 17530 90 / 18, top ten 701 / 197 (22 teams;
701 not 706 at filing because the frozen cut is 11:24Z). Full table: build/hinata/curves/table.csv (group × band × round ×
view), differences with intervals: ci.csv. Code tools/hinata/curves.py 4b0d1f0e1ad8, curves_table.py d6c2be3f2662.
Running view (games still on at that round), series bootstrap 1,000 × seed 7, linear 5–95 %, post-m2 ranked.

**Total length (all units), ours vs opponent, and top-ten winner vs loser (r100 / r300 / end):**

| group | n games | r100 X–Y | r300 X–Y | end X–Y |
|---|---|---|---|---|
| top ten winner–loser | 701 | 78.5–61.3, +17.3 [14.4, 19.8] | 153.7–110.9, +42.8 [36.1, 50.0] | 142.5–73.6, +69.0 [60.8, 77.0] |
| 14585 vs all | 300 | 62.7–47.2, +15.6 [11.7, 19.7] | 128.1–92.6, +35.6 [23.1, 48.6] | 87.3–69.1, +18.2 [4.6, 31.0] |
| 17388 vs all | 80 | 59.9–52.6, +7.3 [−0.3, +15.1] | 115.8–102.2, +13.6 [−4.7, +33.2] | 74.8–79.9, −5.1 [−35.4, +22.5] |
| 17530 vs all | 90 | 55.1–41.6, +13.5 [5.4, 22.0] | 103.2–80.3, +22.9 [2.8, 43.1] | 79.4–67.6, +11.8 [−11.0, +33.1] |
| 17530 vs 1725–1900 | 40 | 49.2–42.0, +7.2 [−2.9, +17.3] | 94.4–76.6, +17.8 [0.1, 39.4] | 68.8–60.8, +8.1 [−15.6, +32.6] |

**Queen alive (fraction of running games), X vs Y, r100 / r300 / end:** top ten winner 0.71 / 0.46 / 0.28, loser 0.72 /
0.47 / 0.32 (r300 diff −0.01 [−0.05, +0.03]; end −0.04 [−0.07, −0.003]). 14585 0.60 / 0.29 / 0.19 vs opp 0.55 / 0.22 /
0.16; 17388 0.68 / 0.29 / 0.18 vs 0.63 / 0.29 / 0.15; 17530 0.79 / 0.52 / 0.38 vs 0.82 / 0.54 / 0.33. Queen length at the
end (dead = 0): top ten 4.9 / 5.6; ours 1.5 (14585), 2.5 (17388), 3.7 (17530).

**Lead conversion (games still on at r300, leader on total length):** top ten the leader wins 368/507 (72.6 %; leader
losses: longest 72, queen 66). Ours when leading: 14585 67/133 (50 %; losses queen 48, longest 16, total 2), 17388 20/27
(74 %; queen 5, longest 2), 17530 28/43 (65 %; queen 11, longest 4).

**Forecasts (stated at filing):** units lead at r100 vs ≥ 1725 for 17530 > 0 — **held** (1725–1900 20.2 vs 16.0, n 39;
> 1900 16.2 vs 26.0, n 5; pooled +2.6). Queen-alive deficit ≥ 0.2 at r300 vs ≥ 1725 for 17530 — **failed** (1725–1900
−0.07 [−0.31, +0.17], n 29). Top-ten winners' queen alive at r300 > 0.6 and losers < 0.4 — **failed** (0.46 vs 0.47).

**Reading.** (1) Among the top ten, winners and losers keep their queens alive at the same rate at every round; the
winner is the larger economy from r100 on (leader at r300 wins 73 %). (2) Our absolute economy is at the top-ten
*loser's* level: total length at r100 55–63 vs winner 78.5 / loser 61.3; at r300 103–128 vs 153.7 / 110.9. We lead our
opponents mid-game because they are weaker on average. (3) Our queens die no more often than our opponents'; the loss
is in converting a length lead: carthage-05 lost half its r300 leads, 48 of 66 of those by the queen rule; kenma-03
converts at the top-ten rate (74 %, n 27). So the queen matters as the tiebreak that turns a length lead into a loss,
not as a survival-rate gap; and the length lead itself is smaller than the top ten build. Caveats: running view is
conditioned on the game still being on; bands > 1900 have 5–10 games; 17388 and 17530 met different opponents.

**RL translation.** Observation: round and opponent band are the axes; the top-ten winner curve (total ≈ 78 at r100,
≈ 154 at r300) is a concrete trajectory target. Value/reward: V should carry total-length lead and queen length jointly;
a lead without a queen is worth ≈ a coin flip for 14585. Action: economy growth r100–r300 (top-ten winners +75, ours
+48 to +65) and queen protection when leading. Demonstration: top-ten winner games are the demonstration set for
mid-game growth.
