# P-hinata-06 — Where the local pool and the ladder disagree (description, not a model)

Filed 2026-10-05 09:38Z by hinata, before any outcome below was read. Requested by the Chair, D-079 §D / BOARD 09:18Z ("optional and cheap, no Mac").

- **Claim (descriptive).** Among ranked post-m2 games of team 7, the trial submissions 16979, 17388, 17530 lose to some opponents that carthage-05 (14585) beats, and per-game local quantities say where: opponent rating band, map, ending type, our queen alive at the end, our units / total length / longest at r100.
- **Rung.** None (R0 diagnostic). No artifact is trained; nothing is deployed.
- **Population.** `public_replays/corpus/index.jsonl`, ranked, completed, started ≥ 2026-10-02T03:49Z (map_era post-m2), team 7 on one side, our `bot_*` ∈ {14585, 16979, 17388, 17530}. Opponent rating = elo in the latest `corpus/ladder/*.json` snapshot at or before game start. All maps (this is a ladder description; no learning target, so held-out maps are not excluded — no fitting, tuning or selection is done on them).
- **Matched comparison.** For each trial sub T: opponents (team ids) that both T and 14585 played. Primary number: loss rate of T minus loss rate of 14585, opponent-weighted by T's game count per opponent (i.e. 14585 re-weighted to T's opponent mix), split by band (opp elo ≥ 1725 / < 1725). Interval: series-cluster bootstrap, 1,000 resamples, seed 7, linear 5–95 %.
- **Per-quantity table.** For each sub, loss rate and mean of each quantity in wins vs losses; for the matched set, which quantity's (T − 14585) loss-conditional mean differs most.
- **Forecasts (frozen).** (a) 17530's excess loss rate over re-weighted 14585 is larger in the ≥ 1725 band than in the < 1725 band: P = 0.60. (b) Share of 17530's losses ending `queen` exceeds 14585's: P = 0.65. (c) Units at r100 in losses differ between 17530 and 14585 by ≥ 1 unit on average: P = 0.40. (d) Any trial sub's matched excess loss rate excludes 0 at 90 %: P = 0.35 (small n).
- **Falsifier / stop rule.** Description only: one pass, results reported as computed; no re-cut after reading except one labelled exploratory table.
- **Cost.** VM stdlib python, ≤ 4 device calls of ≤ 150 s; replays decoded with tools/analysis/features/frame.py (read-only).
- **RL translation.** Observation: candidate observation features for a ladder-weighted evaluation (opp rating band, r100 state). Action: none. Value/reward: re-weighting of the local pool towards where it mis-predicts. Demonstration: none.
- **P(useful to the look)**: 0.5.
- Code: tools/hinata/p06_gap.py; rows build/hinata/p06/.

## Result (2026-10-05 09:46Z, hinata) — one pass as frozen; one table labelled exploratory

Corpus index as of 09:37Z. Ranked, completed, post-m2 (≥ 2026-10-02T03:49Z), team 7; decoded 495 of 495 selected games (0 missing, 0 decode errors): 14585 331 (273 against opponents a trial sub also met), 16979 44 (9 series), 17388 80 (16 series), 17530 40 (8 series, 5 opponent teams). Rows build/hinata/p06/rows*.csv (content hash 80112cc58e6d), code p06_gap.py 8a5eebf6ad77, p06_analyse.py ab4f413de529. Loss = not won and not tie. Opp elo = latest ladder snapshot ≤ game start.

**Primary (matched, 14585 re-weighted to the trial sub's per-opponent counts; series bootstrap, 1,000 × seed 7, linear 5–95 %):**

| Sub | matched opps | trial games matched | gap all | gap ≥ 1725 | gap < 1725 |
|---|---|---|---|---|---|
| 16979 | 7 | 34 | +0.130 [−0.029, +0.340] | +0.200 (n 5) | +0.117 [−0.056, +0.355] (n 29) |
| 17388 | 8 | 55 | **−0.165 [−0.351, −0.007]** | −0.312 [−0.567, −0.046] (n 20) | −0.081 [−0.328, +0.110] (n 35) |
| 17530 | 2 | 25 | −0.040 [−0.307, +0.160] | +0.200 (n 5, one opponent) | −0.100 [−0.350, +0.144] (n 20) |

(+ = trial sub loses more than 14585 against the same opponents.) The matched design is thin: 17530 shares only 2 opponent teams with 14585 in this era.

**Per sub, all its games (loss k/n, Wilson 90 %, not clustered):**

| Sub | loss vs ≥ 1725 | loss vs < 1725 | share of losses ending `queen` | our queen alive at end: wins / losses | in losses: our units@r100 vs theirs | last round in losses |
|---|---|---|---|---|---|---|
| 14585 | 51/71 (0.62–0.80), 11 opps | 113/260 (0.38–0.49), 19 opps | 34 % (46/136, matched set) | 0.12 / 0.00 | 22.3 vs 22.8 | 422 |
| 16979 | 4/5, 1 opp | 24/39 (0.48–0.73) | 50 % (14/28) | 0.25 / 0.00 | 25.7 vs 20.8 | 456 |
| 17388 | 17/35 (0.35–0.62), 7 opps | 20/45 (0.33–0.57) | 24 % (9/37) | 0.12 / 0.00 | 21.0 vs 25.7 | 389 |
| 17530 | **9/10 (0.65–0.98), 2 opps** | 12/30 (0.27–0.55), 3 opps | **52 % (11/21); 9 of its 12 losses below 1725 end `queen`** | 0.42 / 0.10 | 27.8 vs 21.0 | 460 |

Description (no model):
1. **17388 (trial 1) beat 14585's record against the same opponents, most in the ≥ 1725 band** — consistent with its +0.074 trial score; it is the only one of the three whose interval excludes 0.
2. **17530 (trial 2, 40 games) is not behind at r100 when it loses** — more units and more length than the opponent (27.8 vs 21.0 units, 70 vs 57 cells), unlike 14585 and 17388, whose losses are level or behind at r100. It loses late (mean last round 460) and by the queen: 9 of 12 losses to sub-1725 teams end `queen`, i.e. the early economy the local pool rewards is there; the queen does not survive the ladder's mid-game. Against ≥ 1725 it is 9/10 lost (both opponents 1101 @ 1976, 470 @ 1810; 5 of 9 decided on `longest` with both queens dead).
3. The local pool contains no ≥ 1725 opponent and 17530's ladder draw had 25 % of games in that band (14585 18 %, 17388 44 %). The pool cannot see the band where 17530 loses most; below 1725 its loss rate (0.40) is no worse than 14585's (0.43), but the way it loses (queen) differs.

Forecasts scored: (a) 17530 excess larger ≥ 1725 than < 1725 — yes (+0.20, n 5, vs −0.10), but one opponent: weak pass. (b) 17530 queen-ending share > 14585 — yes (52 % vs 34 %). (c) units@r100 in losses differ ≥ 1 — yes (+5.5). (d) any matched gap excludes 0 at 90 % — yes (17388, in its favour). Brier (a .60, b .65, c .40, d .35 all → 1): 0.16 + 0.1225 + 0.36 + 0.4225 → mean 0.266.

Caveats: opponents are teams, not fixed bots (their submissions change over 3 days); 17530 n = 40 games / 8 series / 5 teams — any band statement about it is about two opponents; ratings are snapshot elo, not rating at the series.

RL translation. Observation: opponent strength band and r100 state (units, length) are both needed — a value function trained on the local pool learns "ahead at r100 ⇒ win", which 17530's ladder losses contradict. Action: queen survival between r100 and r400 is the action class the pool under-tests. Value/reward: weight local evaluation towards strong opponents (a ≥ 1725 proxy in the pool) or score queen-alive-at-r300 as an auxiliary target. Demonstration: top-ten games where the queen hides at 2–3 then feeds (Bokuto's 09:32Z census) are the demonstrations the pool lacks.

## Standing column (D-080 §A) — procedure frozen 2026-10-05 10:37Z, before computing any trial-2 number
- **What.** The P-06 primary number, method unchanged, as a column of every trial look: trial sub's loss rate minus 14585's loss rate re-weighted to the trial's per-opponent game counts, only opponents both played; bands by the opponent's median snapshot elo over the trial's games (≥ 1725 hi / < 1725 lo); loss = not won and not tie; series-cluster bootstrap 1,000 × seed 7 (trial and reference resampled independently), linear 5–95 %.
- **Trial window.** The look's window as Daichi defines it: ranked, completed, team 7, bot id = trial sub, started ≥ the trial start (trial 2: 17530 from 08:15:41Z), in start order, cut at the first series boundary at or after 60 games (whole series only). **Reference:** all ranked, completed post-m2 (≥ 2026-10-02T03:49Z) games of 14585 (unchanged from P-06; 14585 is inactive, the set is closed).
- **Source.** Index winner field only (no decode needed for the gap). Parity check first: the index-only code must reproduce P-06's 09:46Z result for 17530 on its 40 games exactly; if not, report the mismatch and use the decoded rows. Secondary (decode of the window games only): share of losses ending `queen`, our queen alive at the end.
- **Disclosure.** Before freezing this I had seen only one aggregate of the current window: 17530 ranked games since 08:15Z in the 10:35Z index = 65, winner a/b 34/31 (not by seat, not a W–L). No gap, band or opponent figure seen.
- **Stop rule.** One pass per look; posted as a column, no verdict — the Chair applies the end rule. Code tools/hinata/p06_column.py.

### Standing column — trial 2 (17530), computed 2026-10-05 10:38Z, one pass as frozen above
Index 10:35Z. Window: 17530 ranked from 08:15:41Z, cut at the first series boundary ≥ 60 → **60 games / 12 series** (08:15:41Z–10:30:04Z; complete), W–L 30–30; opponents 8 teams (hi band 25 games: 18 lost; lo 35: 12 lost). Reference 14585 has games against only **4 of the 8** (351, 470, 899, 989; 40 games), so the matched number covers **40 of the 60** trial games. Bootstrap 1,000 × seed 7, series clusters, linear 5–95 %; + = trial loses more.

| band | matched gap | 90 % | trial games in gap | opponents |
|---|---|---|---|---|
| all | **−0.044** | [−0.267, +0.148] | 40 | 4 |
| ≥ 1725 | +0.167 | [0.000, +0.362] | 15 | 3 (470, 899, 989) |
| < 1725 | −0.170 | [−0.400, +0.093] | 25 | 1 (351: 7/25 vs ref 9/20) |

Unmatched (no 14585 games): 1101 @1976 5/5 lost, 1132 @1764 3/5, 1030 @1601 3/5, 1035 @1543 2/5. Secondary (60 decoded, 0 errors): losses end queen 14/30 (47 %; 14585 in P-06 34 %), elimination 9, longest 7; mean last round of losses 431; our queen alive at the end 17/60 (wins 14/30, losses 3/30).

Parity of the index-only code against P-06 (17530, 40 games): point estimates identical in all three bands; 90 % interval for 'all' [−0.300, +0.148] vs P-06's [−0.307, +0.160] — the reference is now restricted to the trial's opponents before resampling (P-06 resampled 14585 series of all three trial subs' opponents), which changes the draws, not the estimand.

Reading (description, no verdict): on the opponents both played, 17530 is level with carthage-05 overall; worse against the three ≥ 1725 teams (interval touches 0), better against the one < 1725 team. The low band is one opponent, so the 'all' number is mostly 351. Column code tools/hinata/p06_column.py a1c07ad65a42, secondary p06_column_q.py 39318b45788f; output build/hinata/col/col-17530-2026-10-05T0815.json (05335ce30715) + .q*.jsonl.
