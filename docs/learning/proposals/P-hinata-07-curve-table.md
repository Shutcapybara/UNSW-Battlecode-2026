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

## Correction procedure (filed 2026-10-05 12:37 UTC, before any corrected number is read) — reply to Sugawara's review P-hinata-07-sugawara.md

**Accepted as a bug in my code:** `side(R, t, q)` used id 0 as team A's queen and id 1 as team B's; ids follow the map's
`DRAGON` lines. My queen columns (alive, queen length) and readings (1) and (3) are withdrawn as of now.

**Fix at source:** `curves.py` now takes each team's queen as the lowest id among the map's initial dragons of that team
(`frame.terrain(maptext)[0]['dragons']`, the same table `frame.decode` builds `teams` from). Existing rows are not
re-decoded: `tools/hinata/curves_owner.py` reads only the map text of each replay (my own read, not Sugawara's own.py
output) and `tools/hinata/curves_fix.py` writes corrected rows to build/hinata/curves2/ (swap the two queen fields of cA/cB
where team A's queen is not id 0; units/total/longest untouched). `curves_table.py` is unchanged except a directory
argument; same populations, rounds, views, bootstrap (1,000 × seed 7, linear 5–95 %).

**Guard (pass/fail before any table is used):** end-state queen alive in corrected rows must equal the engine's own
TeamStanding queen field (`final[t]['queen'] > 0`) in every team-game whose replay carries it; any disagreement → stop,
no table. Also counted: agreement of the *uncorrected* rows (expected ≈ 1,894 / 2,342 per Sugawara).

**Forecasts (mine, now):** top-ten winner − loser queen alive at r300 ≥ +0.15: P 0.85. 17388 us − opp at r300 ≤ −0.25: P 0.8.
Economy and lead-conversion cells identical to the first run (they are not queen-indexed): P 0.99.

## Corrected result (2026-10-05 12:41 UTC)

**Guard passed:** corrected end queen alive = engine TeamStanding queen in **2,342 / 2,342** team-games (uncorrected 1,894 /
2,342). Owners from my own map-text read agree with Sugawara's own.py in 1,171 / 1,171 games; team A's queen is id 1 in
**593** / 1,171 (14585 150, 17388 41, 17530 44, top ten 358 — the review's per-population counts; its total "585" is a sum
slip). Economy cells (units, total): 0 of all cells changed. Rows build/hinata/curves2/ (sha 8e7ecc6d6735), registry.json there.

**Queen alive, running view, X vs Y, diff [5–95 %] (series bootstrap 1,000 × seed 7):**

| group | n r300 | r100 | r200 | r300 | end | queen len end |
|---|---|---|---|---|---|---|
| top ten winner / loser | 507 | 0.75 / 0.70, +0.05 [+0.01, +0.09] | +0.12 [+0.07, +0.17] | **0.58 / 0.37, +0.21 [+0.17, +0.25]** | 0.48 / 0.13 | 8.8 / 1.7 |
| 14585 us / opp | 209 | 0.44 / 0.72 | 0.17 / 0.54 | **0.06 / 0.45, −0.39 [−0.46, −0.33]** | 0.07 / 0.29 | 0.2 / 2.9 |
| 17388 us / opp | 57 | 0.51 / 0.81 | 0.17 / 0.62 | **0.12 / 0.47, −0.35 [−0.47, −0.25]** | 0.06 / 0.28 | 0.2 / 3.6 |
| 17530 us / opp | 68 | 0.74 / 0.89 | 0.62 / 0.69 | 0.50 / 0.57, −0.07 [−0.19, +0.06] | 0.33 / 0.39 | 3.2 / 3.6 |

Carried view at r300 (all games, last state carried): top ten 0.55 / 0.27 (n 701); 14585 0.10 / 0.36 (300); 17388 0.13 /
0.45 (80); 17530 0.47 / 0.51 (90) — same sign and size as running. The **end** column is partly definitional (games decided
by the queen rule end with the loser's queen dead); read r200–r300, not end.

**Forecasts re-scored:** top-ten r300 diff ≥ +0.15 (P 0.85) — held (+0.21). 17388 us − opp ≤ −0.25 at r300 (P 0.8) — held
(−0.35). Economy unchanged (P 0.99) — held. Original card forecasts: top ten winner > 0.6 / loser < 0.4 at r300 — still
fails narrowly (0.58 / 0.37); 17530 deficit ≥ 0.2 vs ≥ 1725 — still fails (1725–1900 0.00, n 29).

**Corrected reading (replaces readings (1) and (3); (2) and lead conversion stand).** (1) Top-ten winners differ from losers
on **both** economy (+17 total at r100, +43 at r300) and queen survival (+0.12 at r200, +0.21 at r300; queen length at r300
4.3 vs 2.4). (3) Our queens die far more than our opponents' for 14585 and the incumbent 17388 (alive at r300 6 % and 12 %
vs 45–47 %; deficit present already at r100, −0.28 / −0.30); bokuto-13-cull (17530) is near parity (−0.07 [−0.19, +0.06]).
So 17388 is our best converter of the few length leads it holds (20/27) but our worst queen; 17530 the best queen but the
smallest economy. No current bot has both, and the top-ten winner has both.

**RL translation.** Observation: queen alive and queen length by round are first-class state, not a tiebreak detail; any
label/V-target from these rows must use curves2 (or curves.py ≥ 368313e94f33). Value/reward: V carries total-length lead
and queen length jointly (top-ten winner end queen 8.8). Action: queen safety from r100 (the deficit starts there) plus
r100→r300 growth. Demonstration: top-ten winner games carry both behaviours; 17530's queen handling is our own nearest example.

## Re-read of the ≥ 1725 queen forecast on corrected rows (D-083 §A ask; 2026-10-05 13:37 UTC)

Rows build/hinata/curves2/ (sha 8e7ecc6d6735, unchanged). Script build/hinata/qband/qband.py (d7b802d93152; output
qband.csv there). Band = opponent elo in the last ladder snapshot before the game (D-080 §B). Queen alive us − opp, running
view (games still on at the round), series bootstrap 1,000 × seed 7, 5–95 %; carried view (last state carried) beside it per
Sugawara's dissent. Population: our ranked post-m2 games in the P-07 cut (same 1,171-game selection).

| bot | band | n games / series r300 | r100 diff | r300 us / opp, diff [5–95 %] | carried r300 diff (n) | win rate |
|---|---|---|---|---|---|---|
| 14585 | < 1725 | 134 / 39 | −0.19 | 0.07 / 0.39, −0.32 [−0.40, −0.25] | −0.17 (195) | 0.44 |
| 14585 | ≥ 1725 | 75 / 21 | −0.45 | 0.05 / 0.57, **−0.52 [−0.61, −0.44]** | −0.43 (105) | 0.36 |
| 17388 | < 1725 | 33 / 9 | −0.22 | 0.12 / 0.45, −0.33 [−0.47, −0.22] | −0.27 (45) | 0.58 |
| 17388 | ≥ 1725 | 24 / 7 | −0.41 | 0.12 / 0.50, −0.38 [−0.57, −0.17] | −0.40 (35) | 0.54 |
| 17530 | < 1725 | 35 / 9 | −0.21 | 0.54 / 0.66, −0.11 [−0.31, +0.09] | −0.02 (45) | 0.60 |
| 17530 | ≥ 1725 | 33 / 9 | −0.09 | 0.45 / 0.48, **−0.03 [−0.18, +0.12]** | −0.07 (45) | 0.36 |

(> 1900 alone: n ≤ 6 games / ≤ 2 series per bot — not read.)

**Forecast verdict (unchanged, not relabelled):** "17530 queen-alive deficit ≥ 0.2 vs ≥ 1725 at r300" (P 0.6) — **FAILED** on
corrected rows: −0.03 [−0.18, +0.12], both views. The 12:41Z note quoted only 1725–1900 (0.00, n 29); the pooled ≥ 1725 cell is
the forecast's population and agrees.

**What the corrected rows add.** (1) For 14585 the queen deficit **grows with opponent strength** (−0.32 → −0.52; intervals
disjoint); for 17388 it is large in both bands (−0.33 / −0.38). (2) **17530 has queen parity in both bands, yet wins 0.36 vs
≥ 1725** — so its loss to strong opponents is not the queen: end reason of its 28 losses vs ≥ 1725 = elimination 11, longest
10, queen 7 (vs < 1725: queen 11 of 16). Its total length vs ≥ 1725 at r300 is 94.4 / 76.6 (1725–1900, +17.8 [+0.1, +39.4],
n 29) — it leads on length and on queen and still loses 59 % there, so for 17530 the ≥ 1725 gap is **conversion / combat
(elimination + longest-at-limit)**, the third D-083 target, not the first two. Small n (9 series): a reading, not a claim.
(3) Consequence for trial 3 (bokuto-18 = b13 lineage + reserve): read r300 leads converted **and** losses by elimination
vs ≥ 1725 at the look; a queen-alive gain alone will not show up in the statistic at 1725.

**RL translation.** Observation: opponent strength changes which failure dominates (queen death for 14585/17388, combat
conversion for 17530) — a V must be conditioned on opponent-strength proxies visible in play (opponent length, head count),
never on map or opponent identity. Action: for the b13 lineage, the mid-game action to improve vs strong opponents is
engagement/defence of the lead (avoid elimination, keep longest at the limit), not more queen hiding. Value/reward: total-length
lead × queen length stays; add "longest at r500" for games that reach the limit. Demonstration: top-ten winner games vs
≥ 1725 opponents with a length lead at r300 (72.6 % converted) are the demonstrations for conversion.

**For review (D-083 §A rule):** Sugawara, please check reading (2) before the Chair records it.

## Reply to Sugawara's review of the ≥ 1725 reading (docs/learning/reviews/P-hinata-07-band-sugawara.md) — 2026-10-05 14:36 UTC

**Amendment accepted in full.** Independent replication with my own code (build/hinata/qband2/carried.py, sha 31f0c2c6a397; rows curves2 8e7ecc6d6735; population 17530 ranked post-m2; band = opponent Elo in last snapshot; carried view = state at r300, or end state if the game ended earlier, eliminated side 0; series bootstrap 1,000 × seed 7, 5–95 %):

| 17530 vs | n games / series | total r300 us − opp, carried | r300 leads | converted | W | elimination losses (before r300) |
|---|---|---|---|---|---|---|
| < 1725 | 45 / 9 | +41.5 [+15.7, +64.2] | 35/45 | 26/35 = 74 % | 29 | 4 (2) |
| ≥ 1725 | 45 / 9 | +0.8 [−24.9, +24.8] | 21/45 | 15/21 = 71 % | 17 | 11 (7) |

All of Sugawara's carried numbers reproduce exactly. My 13:37Z "length lead vs 1725–1900" was a survivorship artefact of the reached-r300 view (7 of 11 elimination losses end at r158–270 and drop out).

**Corrected reading (replaces the 13:37Z one):** for 17530 (b13 lineage) the ≥ 1725 gap is *fewer and smaller leads built* (21/45 vs 35/45; +0.8 vs +41.5 cells) *plus early combat losses* (elimination before r300: 7 vs 2); conversion is band-invariant (71 % vs 74 %); no detectable queen deficit at n = 9 series (±0.2), which does not establish "not the queen". The RL line "action: defend the lead" is withdrawn.

**At the trial-3 look** I report reached-r300 and carried views side by side, for every r300 column (total, queen alive, leads, converted), plus elimination losses before r300 by band.

**RL translation (amended):** observation — in-play strength proxies (opp length / head count / contact rate), never identity or rating; action — survive early contact (avoid trades before r300 when not ahead) and grow r100→r300; value — carried r300 length difference (eliminated = 0) with queen length; demonstration — top-ten winners' r100→r300 growth vs ≥ 1725.

## Look procedure for trial 3 (17791), frozen 2026-10-05 15:38 UTC — before any 17791 outcome is read

- Tool: `tools/hinata/look.py` sha1 6a691c0f6bbc. Selection identical to `p06_column.py` (first series boundary at or after 60 ranked games of the sub from 14:19:00Z, post-m2). Band = opponent elo in the ladder snapshot at game start (< 1725 / ≥ 1725). Views at r100 and r300 side by side: **reached** (games still running) and **carried** (every game; value at r or the end state, eliminated side = 0). Columns: total us/opp and diff [series bootstrap 1,000 × seed 7, 5–95 %], queen alive us/opp, leads at r300 and converted, W/n, elimination losses and those before r300; engine queen guard.
- Validation: `look.py block build/hinata/curves2 17530` reproduces D-085 §A exactly (carried r300 +41.5 [+15.7, +64.2] < 1725, +0.8 [−24.9, +24.8] ≥ 1725; leads 35/45 → 26 and 21/45 → 15; elimination losses 4 (2) and 11 (7)).
- Pre-decoded 20/20 available 17791 games (0 errors, queen guard 40/40) without reading the block; the provisional selection was moved to `build/hinata/look3/_prelook/` so the look re-selects at the boundary. Reference rows at the look: 17530 from curves2 (same tool) and top-ten winner/loser 78.5/153.7 vs 61.3/110.9 (D-082).
