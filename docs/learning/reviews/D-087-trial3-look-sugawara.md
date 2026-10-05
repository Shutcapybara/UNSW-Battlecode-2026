# Trial-3 look (17791 vs 17388) — Sugawara replication, 5 Oct 2026 18:3xZ

Card: Daichi BOARD 18:25Z (D-084 §C end rule applied). Duty: D-083 §B (look reviewed by me before the Chair reads it).

**Verdict: agree.** The end rule fires as Daichi states; 17791 is the incumbent of record. Two notes, neither changes the decision.

## Replication (frozen inputs; `build/sugawara/look3/rep.py`, imports tools/daichi/live_monitor read-only)

Ranked only, team 7, bot field from index, score − E at anchor 1725, opponent rating = last ladder snapshot at or
before the game start (max lag 10.0 min, no look-ahead), series bootstrap 1,000 × seed 7, 5–95 %.

| window | n / series | W | score − E | 5–95 % |
|---|---|---|---|---|
| 17791, first boundary ≥ 60 (14:30:13–17:48:45Z) | 60 / 12 | 32 | **+0.174** | [+0.079, +0.282] |
| 17388, all ranked (05:02:01–13:50:18Z) | 130 / 26 | 75 | **+0.060** | [−0.010, +0.132] |
| 17388, 05:00–08:15Z | 80 / 16 | 43 | +0.052 | [−0.046, +0.161] |
| 17388, 12:30–14:20Z | 50 / 10 | 32 | +0.074 | [−0.038, +0.166] |
| 17791 excl. team 801 | 55 / 11 | 31 | +0.181 | [+0.073, +0.298] |

All Daichi numbers match to the third decimal. Difference 17791 − 17388: +0.115, independent series bootstrap
(2,000 × seed 11) 5–95 % [−0.013, +0.247]; P(diff ≤ 0.03) = 0.13. The rule is a point-estimate rule, so it fires.

## Note A — the +0.005 → +0.060 change is the anchor, not snapshot timing

Daichi attributes the D-084 §B figure (+0.005 over 129, 13:53Z) to later ladder snapshots and one late-indexed game.
`rating_at` takes the last snapshot at or before the game, so snapshots fetched later cannot enter. Recomputing the
same 130 (or first 129) games over anchors: 1725 +0.060 (+0.064 on 129), 1760 +0.015, 1780 −0.010. **+0.005 corresponds
to an anchor of ≈ 1765–1770**, i.e. 17388's activation-time rating, not 1725. Both looks should state the anchor; the
D-084 §B record of "+0.005" is at a different anchor from today's +0.060. Decision holds at either (Δ ≥ +0.11).

## Note B — trial 4's bar is selection-inflated

Trial 4 (17940) must exceed 17791's +0.174 + 0.03 = +0.204 on its own 60-game look. 17791 was chosen because its look
was high; its 90 % interval reaches +0.079, and its field was 11/12 series ≥ 1725. A winner's-curse reading predicts
17791's true value nearer +0.10. A trial-4 "fail" is therefore weak evidence against asahi-27. Suggestion (Chair's
call, not a re-litigation): report 17940 against both 17791's look (+0.174) and the pooled 17388+17791 incumbent
line, and keep 17791 running for its own post-window games when 17940 is not live.

## Maps

17791 scored 0/12 on Queen Of Spades 0/4, Trophy 0/3, Default 0/2, Stripes 0/2 (+ Trauma 0/1, Dilemma 0/1). This is the
set Bokuto (18:16Z) names as opener-dither elimination maps (QoS, Stripes, Tower Defense, Default). bokuto-46's region
migration targets it but uses atlas beds, so D-087 §C applies (≥ its `bokuto-41-atlas0` twin on the pool).

## Forecasts (log, not Brier-scored under D-072 §B)

- 17940 exceeds +0.204 at its look: **0.25**.
- 17791 post-window ranked games (if any accrue) mean score − E < +0.174: 0.70.
