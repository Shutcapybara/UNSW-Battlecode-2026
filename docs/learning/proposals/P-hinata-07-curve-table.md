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

## Forecast for trial 4 (`asahi-27-b13-reserve`, D-086 §C), filed 2026-10-05 17:36 UTC — before trial 4 is live and before the trial-3 (17791) look is read

- Procedure: identical to the trial-3 look procedure above (look.py 6a691c0f6bbc; first series boundary ≥ 60 ranked games from its activation time, post-m2; band by opponent ladder elo at game start; carried and reached views at r100/r300; series bootstrap 1,000 × seed 7, 5–95 %). Reference row = 17530 (`bokuto-13-cull`, its lineage parent without the reserve) from build/hinata/curves2 (90 games, 18 series), printed by `look.py block build/hinata/curves2 17530` at filing: carried r300 all 91.1 vs 70.0 (+21.2 [+0.6, +39.4]); ≥ 1725 78.4 vs 77.6 (+0.8 [−24.9, +24.8]); ≥ 1725 carried growth r100→r300 us 29.6 (48.8 → 78.4); queen alive carried r300 all 0.47; elimination losses ≥ 1725 11/45.
- Basis: local panels only (Asahi 14:0x–15:39Z): h2h vs kenma-03 69–33, qk2 33–35, qk2 total r300 98.2 (b18 94.5), qk2 queen alive r300 0.50, r300 leads converted 61 %. Local-to-ladder transfer has been weak for every trial so far (D-078, D-085 §A), so all probabilities are near 0.5.
- Forecasts (P that the stated side holds at the look; each scored once, as read):
  1. Carried r300 total (us), all bands ≥ 91.1 (17530): **P 0.60**.
  2. ≥ 1725 carried r300 diff > +0.8: **P 0.55**; ≥ +15: **P 0.20**.
  3. ≥ 1725 carried growth r100→r300 (us) ≥ 29.6 cells: **P 0.60** (the reserve's mechanism is length kept through mid-game).
  4. Queen alive carried r300, all bands ≥ 0.47: **P 0.55**.
  5. ≥ 1725 elimination losses ≤ 11 per 45 games (rate ≤ 0.244): **P 0.50**.
  6. Weakhold (map with the most trial games, any band): win rate ≥ 17530's on the same rows: **P 0.50** (no local basis; recorded for the column only).
- Joint reading with trial 3 (stated now): if 17791 and trial 4 both beat 17530 on item 3, the gain is the shared reserve; if only 17791 does, the queen changes. Neither reading is claimed if the interval of the diff vs 17530 includes 0 — then it is "no ladder evidence either way".
- Stop rule: one read; no re-look at a later boundary unless the Chair asks; values recorded as printed, no relabel. Brier score of items 1–6 appended with the result.
- RL translation: value — tests whether a length-retention rule (reserve) moves the mid-game carried-length trajectory that V0b's value gap localises at r100–300 against ≥ 1725; no observation/action change.

## Trial-3 look result (17791 `bokuto-18-queenfeed`), 2026-10-05 18:40 UTC — frozen procedure, one read

- Selection: first series boundary ≥ 60 ranked post-m2 games of 17791 from 14:19:00Z → 60 games / 12 series (14:30:13–17:48:46Z), 0 decode errors, queen guard 120/120. Same window as Daichi/Sugawara's elo look (D-084 §C, BOARD 18:25/18:27Z). Bands by opponent ladder elo at game start: ≥ 1725 55/11 series, < 1725 5/1 series (one series — the < 1725 row is not read). Intervals: series bootstrap 1,000 × seed 7, 5–95 %. Output build/hinata/look3/block.txt.

| ≥ 1725 | 17791 (n 55/11) | 17530 ref (n 45/9) |
|---|---|---|
| W/n | 28/55 | 17/45 |
| carried r100 total us/opp, diff | 65.1 / 57.3, +7.8 [−2.9, +18.2] | 48.8 / 45.0, +3.8 [−8.6, +15.4] |
| carried r300 total us/opp, diff | 97.5 / 90.9, +6.6 [−14.2, +29.3] | 78.4 / 77.6, +0.8 [−24.9, +24.8] |
| reached r300 (n) total us/opp, diff | (40) 115.7 / 107.7, +8.0 [−12.9, +29.2] | (33) 92.1 / 85.9, +6.2 [−18.4, +31.3] |
| carried growth r100→r300 (us) | 32.4 | 29.6 |
| queen alive carried r100 / r300 (us) | 0.93 / 0.62 | 0.73 / 0.42 |
| r300 leads converted | 20/26 | 15/21 |
| elimination losses (before r300) | 14/55 (9) | 11/45 (7) |

- All bands: carried r300 97.4 vs 92.8 (+4.6 [−13.7, +23.2]); 17530 all 91.1 vs 70.0 (+21.2) — not comparable (17530's field was half < 1725, 17791's 11/12 series ≥ 1725).
- Top-ten reference (D-082, reached): winner 78.5 r100 / 153.7 r300, loser 61.3 / 110.9. 17791 ≥ 1725 reached: 65.1 / 115.7 — at the top-ten loser's line, ~38 cells under the winner's at r300.
- End reason × result, ≥ 1725: L elimination 14, queen 7, longest 6; W longest 17, elimination 6, queen 5. < 1725: W longest 4, L elimination 1.
- Seat × result (D-087 §B column): A 21/35, B 11/25 (seat drawn per series; no term).
- Standing column (p06_column.py, vs 14585 re-weighted to the trial's opponents; matched 10/12 opponents, ref 125 games): loss-rate gap ≥ 1725 −0.094 [−0.267, +0.124] (n 45), all −0.110 [−0.263, +0.082] (n 50).
- Server compute (D-087 §A item 4; pts_own.py over the same 60 games, 748,548 dragon-turns, team 7 cpu only): max 12.62 M (game 1157167), first-turn max 9.96 M, 0 turns > 30 M, 0 cuts/TLE. Daichi's 13.05 M covers 89 games incl. unranked — consistent.
- Reading: 17791 is ahead of 17530 at ≥ 1725 on every curve column (r100 total +16.3, queen alive r300 +0.20, carried r300 +19.1 cells), but every diff interval includes 0 and the opponent sets differ, so by the frozen rule this is "no ladder evidence either way" on the curves; the elo look (Daichi/Sugawara) decides the trial. The largest shift is early (r100 total and queen alive), not growth r100→r300 (32.4 vs 29.6) — consistent with the queen changes, not a mid-game length gain. Joint reading with trial 4 (stated 17:36Z): item 3 baseline from 17791 is 32.4.
- RL translation: value — the ≥ 1725 gap to the top-ten winner sits at r100–r300 (r300 −38 cells reached); queen survival is the only column that moved materially, so a value target that weights queen-alive at r300 is the cheapest observation to add; no action or demonstration change.

## Reply to Sugawara's check (D-088 §C, docs/learning/reviews/D-088-curveblock-sugawara.md) — hinata, 2026-10-05 19:36 UTC

All three amendments accepted; no number changes, the labels do. Re-run `look.py block` (frozen code, same rows) on build/hinata/look3 and build/hinata/curves2, ≥ 1725 band, ranked post-m2, anchor 1725, series bootstrap ×1,000 seed 7, 5–95 %:

| ≥ 1725, reached view (game reached r300) | 17791 (n 40 of 55) | 17530 (n 33 of 45) |
|---|---|---|
| leads at r300 converted | **14/20 = 70 %** | **10/16 = 62.5 %** |
| queen alive r300 (us / opp) | **0.72** / 0.42 | 0.45 / 0.48 |
| total r100 → r300 | 65.1 → 115.7 (growth 50.6) | 48.1 → 92.1 (growth 44.0) |
| diff r300 | +8.0 [−12.9, +29.2] | +6.2 [−18.4, +31.3] |

1. Conversion: the carried 20/26 and 15/21 both count early elimination wins as converted leads. Quote reached 14/20 (70 %) vs 17530's 10/16 (62.5 %); with n 20 and 16 the difference is not resolved.
2. Queen alive r300: reached 0.72 (17530 0.45) goes against the D-083 target 0.58; carried 0.62 (0.42) only for the like-for-like 17530 comparison.
3. "Shift is early" holds **vs 17530 only**. Against the top-ten winners (reached), the gap is r100 −13.4 and growth r100→r300 −24.6 (50.6 vs 75.2): **most of the economy gap is growth after r100.** The 18:38Z line's "32.4 vs 29.6" mixed growth with elimination (carried r300 minus a shared r100) and is withdrawn. Caveat: in the reached view the populations differ by r (r100 n 55, r300 n 40), so "growth" here is a difference of means over two populations, not a per-game growth; per-game growth on the 40 games that reached r300 is the next check if anyone uses it as diagnosis.

RL translation (amended): value — two label/feature fixes. (a) Queen alive at r300 as a value feature (unchanged). (b) The conversion target is "lead alive at r300 → win" (reached), never the carried count, so the carried artefact does not get into a label. Reward/diagnosis — the main deficit against the top ten is mid-game growth (r100–300), not the opener, so a growth-rate feature over r100–300 belongs in V before anything opener-side.

## Pre-registration: per-game growth check (the 19:36Z caveat) — hinata, 2026-10-05 20:36 UTC (before any per-game number is read)

- Claim: on games that reached r300, per-game growth (total r300 − total r100, same game, our side) of 17791 vs ≥ 1725 opponents is well below the top-ten winners' per-game growth; the reached-view "growth gap −24.6" is not a population artefact.
- Rows (frozen, no new decode): build/hinata/look3 (17791, ≥ 1725 opp elo at game start, last_round ≥ 300, n 40 expected); build/hinata/curves2 pop 17530 same filter; curves2 pop top10, winner side, last_round ≥ 300 (no band, as D-082). Field: c<side>[r][1] (total). Interval: series bootstrap ×1,000 seed 7, 5–95 % for each mean; the gap interval is an independent two-sample series bootstrap (same seed, 1,000).
- Expected: 17791 per-game growth ≈ 50 (pop-diff 50.6), top-ten winners ≈ 75, gap ≈ −25. P(gap ≤ −10 and its 95 % end < 0) = 0.75.
- Falsifier / stop rule: gap > −10 or the interval includes 0 → the label "most of the economy gap is growth after r100" is withdrawn and replaced by "not resolved"; one run, no re-cut.
- Code: tools/hinata/growth_pg.py (new, ~40 lines, read-only over the jsonl).

## Result: per-game growth check — hinata, 2026-10-05 20:37 UTC

`python3 tools/hinata/growth_pg.py` (sha256 f49aef58a388), frozen rows, games that reached r300, total = column 1, series bootstrap ×1,000 seed 7, 5–95 %.

| reached r300 | per-game growth r100→r300 | n games / series |
|---|---|---|
| top-ten winners (D-082 rows, no band) | 68.2 [63.8, 72.0] | 507 / 192 |
| 17791, opp ≥ 1725 | 38.2 [26.2, 48.7] | 40 / 11 |
| 17530, opp ≥ 1725 | 37.2 [26.9, 49.0] | 33 / 9 |

- Pre-registered test: gap 17791 − top-ten winners **−29.9 [−41.5, −18.6]** (17530: −31.0 [−41.7, −19.0]). **PASS** on the frozen rule (gap ≤ −10, interval excludes 0). The label stands.
- The two-population figure overstated our growth: per-game 38.2, not 50.6 — the games that reached r300 were the richer ones at r100 (≈ 77.5 vs 65.1 over all 55).
- 17791 vs 17530 per-game growth is level (38.2 vs 37.2): 17791's gain over 17530 is all before r100 and in queen survival, as first read.
- Exploratory, not pre-registered, no intervals: the winners-only reference is outcome-conditioned. Top-ten losers grow 34.9 (507/192), so the unconditioned top-ten mean is ≈ 51.6 and our gap to it ≈ −13; 17791 split by result: wins 50.8 (22 games), losses 22.9 (18). Our wins grow ≈ 17 less than top-ten wins. The deficit is real but about half the size the winners-only comparison suggests.
- RL translation: value — growth r100→r300 is a legitimate V feature (separates our wins 50.8 from losses 22.9), but its target must be fitted on all outcomes, never "match the top-ten winners' curve" (that bakes outcome selection into the label); demonstration — top-ten r100–r300 play from both winners and losers, weighted by outcome, not winners only; action — no change.

## Trial-4 look result (17940 `asahi-27-b13-reserve`), 2026-10-05 22:45 UTC — frozen procedure, one read; forecast of 17:36Z scored

- Selection: first series boundary ≥ 60 ranked post-m2 games of 17940 from 18:25:06Z → 60 games / 12 series (18:37:04–21:58:53Z), 0 decode errors, queen guard 120/120. look.py sha1 6a691c0f6bbc. Bands by opponent ladder elo at game start: ≥ 1725 50/10 series, < 1725 10/2 series (two series — not read). Intervals: series bootstrap 1,000 × seed 7, 5–95 %. Output build/hinata/look4/block.txt.

| ≥ 1725 | 17940 (n 50/10) | 17791 (n 55/11) | 17530 ref (n 45/9) |
|---|---|---|---|
| W/n | 19/50 | 28/55 | 17/45 |
| reached r300 (n): queen alive us/opp | (39) **0.33 / 0.74** | (40) 0.72 | — |
| reached r300 leads converted | 10/18 | 14/20 | — |
| reached r300 total us/opp, diff | 110.6 / 107.4, +3.2 [−30.0, +29.5] | 115.7 / 107.7, +8.0 [−12.9, +29.2] | 92.1 / 85.9, +6.2 [−18.4, +31.3] |
| per-game growth r100→r300, reached r300 (growth_pg filter) | **46.4 [34.0, 59.2] (39/10)** | 38.2 [26.2, 48.7] (40/11) | 37.2 [26.9, 49.0] (33/9) |
| carried r100 total us/opp, diff | 57.1 / 59.9, −2.8 [−16.6, +9.1] | 65.1 / 57.3, +7.8 | 48.8 / 45.0, +3.8 |
| carried r300 total us/opp, diff | 95.7 / 98.0, −2.3 [−39.7, +30.8] | 97.5 / 90.9, +6.6 | 78.4 / 77.6, +0.8 |
| carried growth r100→r300 (us) | 38.6 | 32.4 (withdrawn as a growth measure) | 29.6 |
| queen alive carried r100 / r300 (us) | 0.74 / 0.36 | 0.93 / 0.62 | 0.73 / 0.42 |
| elimination losses (before r300) | 11/50 (6) | 14/55 (9) | 11/45 (7) |

- Per-game growth diffs (exploratory, same bootstrap): 17940 − 17530 +9.3 [−8.9, +27.0]; 17940 − 17791 +8.2 [−9.3, +24.8]; 17940 − top-ten winners −21.8 [−35.6, −9.2] (17791: −29.9).
- End reason × result, ≥ 1725: **L queen 14**, elimination 11, longest 6; W elimination 9, longest 8, queen 2. (17791: L elimination 14, queen 7, longest 6.) < 1725: W longest 5, queen 1; L elimination 2, longest 2.
- Seat × result: A 12/25, B 13/35.
- Watch maps (W/n; 17791 / 17530 on their own looks): Australia 1/7 (1/2, 2/6), weakhold 1/5 (4/7, 2/9), Slithery Fight 1/3 (5/7, 1/3), Schooltime 3/3 (4/4, 4/4), QoS 1/2 (0/4), Trophy 1/3 (0/3), Default 1/4 (0/2), Stripes 2/4 (0/2), Maze 0/3, Trauma 0/3. Cells are 2–7 games; none is read alone.
- Standing column (p06_column.py, vs 14585 re-weighted to the trial's opponents; matched 8/12 opponents, ref 111 games): loss-rate gap ≥ 1725 −0.024 [−0.207, +0.133] (n 30), all −0.024 [−0.183, +0.100] (n 40). Output build/hinata/col/col-17940-look4.txt.
- Server compute (pts_own.py, same 60 games, 725,814 dragon-turns, team 7 only): max 12.94 M (game 1173074), first-turn max 9.90 M, 0 turns > 30 M, 0 TLE.
- **Forecast score (items as filed 17:36Z, outcome as read):** (1) carried r300 all 96.8 ≥ 91.1 — held, P 0.60, Brier 0.160; (2a) ≥ 1725 carried diff −2.3 > +0.8 — failed, P 0.55, 0.303; (2b) ≥ +15 — failed, P 0.20, 0.040; (3) ≥ 1725 carried growth 38.6 ≥ 29.6 — held, P 0.60, 0.160; (4) queen alive carried r300 all 0.35 ≥ 0.47 — failed, P 0.55, 0.303; (5) ≥ 1725 elimination losses 11/50 = 0.22 ≤ 0.244 — held, P 0.50, 0.250; (6) weakhold 1/5 vs 17530 2/9 — failed (also failed on the map with most trial games, Australia 1/7 vs 2/6), P 0.50, 0.250. **Mean Brier 0.209 over 7 (coin 0.250).** Item 4 was the costly miss: I forecast the reserve to leave the queen alone.
- Joint reading (stated 17:36Z): both 17791 and 17940 beat 17530 on item 3, but every diff interval vs 17530 includes 0 → by the stated rule, "no ladder evidence either way" on whether the reserve carries a growth gain.
- Reading: 17940 is the first trial whose per-game growth point estimate moves toward the top-ten line (46.4 vs 38.2/37.2; gap −21.8 vs −29.9), but its queen falls (reached r300 0.33 vs 17791's 0.72; queen losses 14/50 vs 7/55) and its r100 lead is gone (carried r100 −2.8 vs 17791 +7.8). 17940 lacks 17791's queen-feed, so this is the trial-3 decomposition again from the other side: growth and queen survival are separate levers, and each trial has moved one. The elo look (Daichi, end rule > +0.204 at 1725) decides the trial; this block is not a decision statistic.
- RL translation: value — queen alive at r300 and per-game growth r100→r300 enter V as two separate features (fitted on all outcomes, training maps only); the 17940 vs 17791 contrast is a natural paired demonstration set for the queen term (same lineage, queen feed on/off). Action — none. Observation — none new.

## Reply to Sugawara's D-091 §B check (docs/learning/reviews/D-091B-growth-sugawara.md) — hinata, 2026-10-05 23:36 UTC

- **Accepted (amend).** The +8.2 per-game growth of 17940 over 17791 is level-vs-slope plus map mix, not a growth lever. I withdraw the 22:45Z reading "growth and queen survival are separate levers, and each trial has moved one" as far as it claims 17940 moved growth; what stands is the queen contrast (reached r300 0.33 vs 0.72) and 17791's r100 lead.
- Replicated the asked column with a new single-purpose tool, `tools/hinata/r100col.py` (sha1 cccfdb37f98b; ≥ 1725, all games reaching r100, series bootstrap 1,000 × seed 7, 5–95 %): 17940 58.3 [52.7, 63.6] (49/10) vs 17791 65.1 (55/11), **diff −6.8 [−17.1, +3.4]** — equal to Sugawara's figure. It is added to every block from trial 5 on; the per-game growth row stays but is quoted with the r100 and r300 levels beside it.
- RL translation: value — compare trajectories by level at the target horizon (r100, r300), not by slope; per-game growth is not a V feature on its own (drop the 22:45Z "separate growth feature" item; keep queen-alive r300 and r100/r300 levels).

## Trial-5 look procedure and forecast (18078 `bokuto-61-mouth`, D-090/D-091), filed 2026-10-05 23:36 UTC — before any 18078 game is read

- Procedure: as trial 4 (look.py 6a691c0f6bbc; first series boundary ≥ 60 ranked post-m2 games from activation 22:55:18Z; band by opponent ladder elo at game start; reached/carried at r100/r300; series bootstrap 1,000 × seed 7, 5–95 %), plus r100col.py, growth_pg row, p06_column, pts_own, seat × result, end reason × result, watch maps. Reference row 17791 (incumbent of record, build/hinata/look3).
- Sugawara's 22:27Z portal-adjacency test is not built: Asahi ran it on frozen qk2 frames (23:12Z, 0 of 10) and the mechanism is refuted (Sugawara 23:42Z). At the look I print, for losses with end reason queen, map and round only (my rows carry no death cause).
- Basis: 61 = 46's generation + mouth rule, carries the fed queen; local qk2 41–27 (+16.2 vs 18), queen wall deaths 10 vs 46's 3 (dead-end walks, Asahi 23:12Z); pool misses vs 41 on Australia/Slithery are queen deaths. Local-to-ladder transfer has been weak, so probabilities stay near 0.5.
- Forecasts (≥ 1725 unless stated; P the stated side holds; each scored once, as read):
  1. Queen alive, reached r300 (us) ≥ 0.58: **P 0.40**; ≥ 0.72 (17791): **P 0.20**.
  2. Losses with end reason queen ≤ 0.127 of games (17791 7/55): **P 0.40**.
  3. r100 total (r100col, games reaching r100) ≥ 65.1 (17791): **P 0.45**.
  4. Reached r300 total (us) ≥ 115.7 (17791): **P 0.40**.
  5. Per-game growth r100→r300 (reached) ≥ 38.2 (17791): **P 0.55**.
  6. Australia + Slithery Fight, any band, W rate ≥ 17791's 6/9: **P 0.30** (watch item, cells small).
  7. QoS + Trophy + Default + Stripes, any band, W rate ≥ 0.30 (17791 0/11): **P 0.50**.
  8. Schooltime, any band: no loss (if ≥ 1 game): **P 0.65**.
  9. Server max per turn < 30 M and 0 TLE: **P 0.95** (probe 14.32 M).
- Stop rule: one read at the boundary; no re-look unless the Chair asks; values as printed; Brier over items 1–9 (10 scored outcomes) appended with the result. Not a decision statistic — Daichi's end rule decides.
- RL translation: value — tests whether a feeding-queen bot keeps the queen-alive-r300 level of 17791 when a terrain rule (mouth) changes where migrations stop; the dead-end-walk class is a candidate observation feature (free neighbours of the queen's head over the last 3 rounds) for V and for a queen-move prior.
