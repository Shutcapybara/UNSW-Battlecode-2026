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
