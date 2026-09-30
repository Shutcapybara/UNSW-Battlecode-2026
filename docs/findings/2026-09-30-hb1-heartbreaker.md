# HB-1 — Heartbreaker (team 62): anatomy of a learned policy, and a structured mimic

Prompt: `docs/hub/prompts/2026-09-30-HB1-heartbreaker-anatomy.md`. Branch `r/hb1`. Running log with every table:
`claude/hb1-status.md`. Raw rows: `game_stats/runs/hb1-*.json`. Desktop, 30 Sep 2026.

## Headline

1. **Heartbreaker is a rule wrapper around one learned decision.** Four of the five per-turn decisions (split gate,
   late split, child size, sonar pattern) are near-deterministic rules that a depth-4 tree recovers to 92–99.9 %;
   only the move direction is learned (depth-4 tree 0.685 vs GBT 0.829, gap +12.9 pp). Direction is a function of
   the current 7×7 view — history, decayed spatial memory and echo EWMAs add ≤ 0.2 pp.
2. **The wrapper is exact and copyable**: five rules cover all but 0.0014 % of their 7.3 M observed commands,
   including a deterministic exit-less fallback (ally head F>R>L, else forward).
3. **No training loop is visible 27–29 Sep**: the policy is static (no drift between 6-hour windows, no
   behavioural change-points, an era model from ≤ 27 Sep predicts 29 Sep as well as a same-window model). Whether it
   is RL cannot be decided from replays.
4. **A structured mimic in C++ on the Ares chassis works and is deployable** (`bots/hb1-04-deployable`: 30.6 MB per
   process, ≤ 8.4 M points per turn). It matches 82 % of their commands on held-out games and plays their game —
   same strong maps, same weak maps, lost the same way — and against our deployed Ares V04 it scores **22/40 vs
   Heartbreaker's real 28/40**.
5. **Strength is steep in direction accuracy**: ~0.73 → 7.5 % win rate, 0.829 → 35 %, 0.854 → 55 %, real
   Heartbreaker 70 % (vs Ares V04). The mimic's remaining gap is the direction model, and that model is still
   data/capacity-limited.

## Data (Q0)

817 corpus games (27 Sep 20:18 – 29 Sep 21:48 UTC, no submission ids, 10 maps, 46 opponents) + the 180 era-labelled
games of the 27 Sep packets (14 maps). All 997 extracted to v5 actor-turn rows (`tools/team_recon_claude/features_v5.py`,
`tools/hb1/build_dataset.py`): 0 errors, ~10 k rows / game, 294 columns. Held-out set for everything below: 163 of
the 817 corpus games (by game, seed 62), never used for fitting. Map-identifying columns (W, H, absolute x/y,
absolute facing, map) are excluded everywhere (OOS rule).

## Q1 — structure before parameters

| decision | n test | majority | tree depth 4 | GBT | MLP | gap tree→MLP | largest drop-family Δacc |
|---|---:|---:|---:|---:|---:|---:|---|
| split gate (eligible turns) | 128,379 | 0.903 | 0.952 | 0.975 | 0.970 | +0.018 | candidates −1.27 pp |
| **direction (F/R/L)** | 179,436 | 0.534 | 0.685 | 0.829 | 0.814 | **+0.129** | candidates −14.0 pp |
| sonar ray mask | 94,761 | 0.699 | 0.937 | 0.981 | 0.966 | +0.029 | action taken −9.6 pp |
| child size | 34,445 | 0.753 | 0.918 | 0.957 | 0.943 | +0.025 | length/units −0.99 pp |
| late gate (r ≥ 350, len ≥ 8) | 48,345 | 0.960 | 0.9993 | 0.9994 | 0.9988 | −0.001 | candidates −0.93 pp |

- Rules read from the trees: no exit of any kind → split; in the open, split only right after eating at length ≤ 4
  (the 2+2 production split) plus an opening split at r0–1; after r350 a long dragon splits *only* when fully
  blocked — no productive late splits, which is the mechanism behind the concentration weakness below.
- Sonar: 4 rays every surviving turn, absolute order N,E,S,W, payload 0 on all 475,192 sonar turns; at length ≥ 3
  the ray into the new neck is usually redrawn. Received messages carry 0.05 pp for sonar, 0.86 pp for direction
  (echo counts inform steering; the protocol gives echo *counts* only, no direction).
- Memory test (user's suggestion; `tools/hb1/q1_history.py`): last-6 actions, turn EWMAs, decayed enemy/ally
  segment and head density with centroid (the density gradient), own-position trail, echo-count EWMAs, Δdensity ×
  step. Direction 0.8287 → 0.8306 (+0.19 pp), gate unchanged. The top 24 features by gain are current-view candidate
  features. Consistent with a memoryless policy over the local observation.
- Calibration: the direction GBT is calibrated (ECE 0.022). 28 % of moves are near-certain (≥ 0.95, 99.2 %
  correct); 13 % are near-ties (52 %). The residual is not useful randomness — see hb1-02 below.
- Late concentration (the 27 Sep weakness) is unchanged and larger: 87 % of their corpus losses are at the round
  limit, 77 % of those with a total-material lead; median longest in those losses 12 vs the opponent's 27.

## Q2 — wrapper vs policy (`tools/hb1/wrapper.py`)

| rule | observed (7.3 M corpus actor-turns) |
|---|---|
| W0 split validity (len ≥ 4, units < limit, child ∈ [2, len−2]) | 0 violations in 186,440 splits |
| W1 no ordinary exit, no portal, split-eligible → split | 89,986 / 90,072 (99.9 %) |
| W2 no exit at all, not eligible → ally head F>R>L, else forward | deterministic in the sample; every such move dies |
| W3 portal only, not eligible → portal | 20,387 / 20,413 |
| W4 ordinary exit free → never wall / own body / ally cell | 12 ally moves in 7.08 M; enemy-head attacks (9,575) are policy |

Command-level accuracy (10 classes), same held-out games: GBT 0.826 raw = wrapped (the learner has absorbed the
wrapper); on the out-of-time era set the MLP falls to 0.655 raw with 7.8 % invalid picks and **0.703 wrapped** — the
wrapper is exact, costs nothing, and protects a learned component off-distribution. The 27 Sep packet's 66 %
ceiling was a capacity/feature limit, not a wrapper effect.

## Q3 — is a training loop running?

6-hour windows from 27 Sep 20:00 UTC; on the five large windows (105–193 k rows each) within-window, era-trained,
forward and backward transfer agree within ~1 pp for every decision (direction 0.803–0.820, gate 0.965–0.974); no
systematic backward > forward. Hourly change-points (penalised mean-shift DP over 36 hours): none. Ladder: Elo
1788–1874, rank 30–52, no trend. The policy is static over the span; frozen RL and a static hand-written bot look
identical in replays, so the RL question is not answerable here and no further spend is made on it.

## Q4 — the structured mimic

Built on a verbatim copy of Ares V06 behind `Params::hb1_mode` (Ares untouched when off):
C++ port of the v5 row (`hb1_features.hpp`; parity vs Python on 3 held-out games: 19,553 rows × 276 columns, 0
mismatches) → wrapper W0–W4 as rules → exported GBTs for gate, child size, direction, sonar (C++ evaluator parity vs
XGBoost margins: 0 mismatches) → sonar N,E,S,W payload 0.

| version | one change | held-out direction | vs Ares V04 (40 fixed fixtures) |
|---|---|---:|---:|
| hb1-01-structured | the structured mimic | 0.829 | 14/40 |
| hb1-02-sampled | direction sampled, not argmax | (~0.73 expected) | 3/40 — rejected |
| hb1-03-direction-scaled | direction GBT on 2.4× data, 255 leaves, early-stopped (local blob) | 0.854 | **22/40** (paired vs 01: 9 L→W, 1 W→L, sign test p = 0.011) |
| hb1-04-deployable | hb1-03's model as 8-byte compiled nodes | 0.854 (bit-identical) | = hb1-03 |
| *real Heartbreaker* | | | *28/40* |

Per map vs Ares V04 (hb1-01 / hb1-03 / real): Autarky 3/3/4, Default 1/2/3, Devil 2/4/3, Prisoners Dilemma 4/4/4,
Portals 0/0/1, Queen of Spades 1/2/4, Schooltime 0/1/1, Slithery Fight 0/0/0, Trauma 2/3/4, Trophy 1/3/4. Every
map that moved, moved toward Heartbreaker's record; the weak maps are the same maps, lost the same way (length at r500).

- Fidelity of the deployed binary (open-loop conditional replay, 40 held-out games, 356,944 of their turns):
  family 0.993, direction 0.824, child size 0.944, command 0.821, sonar multiset 0.681, 0 missing replies.
- Where hb1-01 lost strength: not in production (split rates match to 3 pp in every phase) and not the environment
  (r0–24 eat rates identical); from r25 it eats 5–10 % less per dragon-turn and self-traps up to 25 % more, which
  compounds to 60 % of Heartbreaker's material at r100 — i.e. direction quality.
- Deployability (hb1-04, judge sandbox): clang 20 wasm build OK; 30.6 MB per dragon process (cap 48 MiB);
  p50 7.6 M / p99 8.0 M / max 8.4 M points per turn; 0 fallbacks in 10,560 turns.
- Scorecard (z1 + generalisation panels, field-relative): running at the time of writing; appended below when done.

## Q5 — what transfers

Pending. Components with measured fidelity: the wrapper (exact), the split gate (0.975), child size (0.957), the
direction scorer (0.854). Each is to be ported alone into a copy of Ares V06 as a switch (`hb1-1x-<component>`)
and run through the gate.

## Ledger rows touched and proposed weights

| row | current | proposed | evidence |
|---|---:|---:|---|
| L27 learned decision functions beat hand rules for a specific decision at ≈ 0 live CPU | 0.5 | **0.6** | First C++ learned decision measured end-to-end: exact export, ≤ 3 M marginal points, and a steep, significant dose–response between one learned decision's accuracy and strength (hb1-01→03, p = 0.011). "Beats our hand rules" is Q5's test; weight moves again on the first hb1-1x result. |
| L24 trapped hazard ≤ 8 reach; escape split | 0.5 | 0.5 (unchanged) | Heartbreaker splits on 99.9 % of exit-less eligible turns and walls only under total blockade — supportive of the escape-split form, but descriptive until Q5 ports W1 to Ares. |
| L05 leaks fixable on Ares | 0.7 | 0.7 (unchanged) | The wrapper is a leak fix by construction (0 invalid commands, wall moves only under blockade); measured on Ares in Q5. |
| L04 / L20 weights | 0.6 / 0.2 | unchanged | Not tested by HB-1 so far. |
| new: a strong opponent's strength can concentrate in one learned decision, and imitation strength is steep in that decision's accuracy | — | 0.7 | Q1 gap table; hb1-01/02/03 dose–response vs Ares V04. |
