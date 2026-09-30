# TT — the top teams: cheji bt (team 70) and Stockfish (team 206)

Request (user, 30 Sep 2026): an HB-1-style analysis of the two top teams. Branch `r/tt` (from `r/hb1`). Method and
tools are HB-1's (`docs/findings/2026-09-30-hb1-heartbreaker.md`, `tools/hb1/`, now parameterised by
`HB_TEAM` / `HB_BUILD` / `HB_TAG`), plus `tools/tt/`. Running log with every table: `claude/tt-status.md`. Raw rows:
`game_stats/runs/tt*`.

## Headline

1. **The top teams' edge over Heartbreaker is the endgame conversion, not the swarm.** All three run the same swarm
   economy to ~r200. cheji bt and Stockfish then dissolve the swarm into one long dragon (longest 40 and 46 at r490,
   37–46 % of their material in it) and win 75 % / 72 % of round-limit games; Heartbreaker never converts (longest
   13, 10 %, 26 %).
2. **They convert by deliberately killing their own small dragons** (~1 % of turns; Heartbreaker: never). cheji bt: an
   invalid command, a timed mass cull — from ~r330 each small dragon dies with ~10 % per turn. Stockfish: a backward
   step into its own neck, from r250 at ~2 % per turn, weighted toward small dragons next to an ally head.
3. **They are harder to copy from the local view.** Command-level GBT accuracy: Heartbreaker 0.826, Stockfish 0.763,
   cheji bt 0.741. cheji bt's split gate is not a rule (0.829 vs Heartbreaker's 0.975); Stockfish's production is
   rule-like with round thresholds at ~250 and ~350 (hand-written phase logic).
4. **Our bots have the tactic and run it late.** Ares's feeder (within 4 cells of the elected crown, step backward
   into the neck) activates from ~r400–430, 100–150 rounds after the top teams; Ares ends at longest 25, hb1-12 at
   28.5 with 57 % of its round-limit losses despite a material lead.
5. **Moving Ares's feeding earlier fixes the conversion and does not pay on any local measure.** tt-01 (from ~r300)
   cuts round-limit losses with a material lead from 57 % to 20 % and loses 3 games net on the z1 panel (fewer
   elimination wins); tt-02 (from ~r250) over-converts (−5.0 pp). No local opponent converts early, so the value of
   the top teams' timing against teams that do is not measurable locally.

## Data

Mac corpus, synced 30 Sep: cheji bt 4,126 completed games (25 Sep 18:20 – 30 Sep 11:57 UTC, 116 opponents),
Stockfish 1,932 (26 Sep 22:12 – 30 Sep 12:11, 71 opponents), 105 shared. All extracted to v5 rows, 0 errors. No
submission ids. Ladder 30 Sep 12:11 UTC: cheji bt #1 (2096), Stockfish #4 (2079; #2–#4 within 2 Elo). Win rates in
the corpus 0.806 and 0.692; head-to-head cheji bt 69–36. cheji bt's weakest map (Slithery Fight 0.62) is Stockfish's
best (0.79). Held-out = 20 % of each team's games (by game, seed 62); map-identifying columns excluded.

## Q1 — structure (GBT held-out; tree depth 4 in brackets)

| decision | Heartbreaker | cheji bt | Stockfish |
|---|---:|---:|---:|
| split gate | 0.975 (0.952) | 0.829 (0.779) | 0.934 (0.872) |
| direction | 0.829 (0.685) | 0.751 (0.638) | 0.771 (0.664) |
| child size | 0.957 (0.918) | 0.911 (0.858) | 0.980 (0.871) |
| sonar mask | 0.981 (0.937) | 0.983 (0.950) | 0.971 (0.925) |
| late gate (r ≥ 350, len ≥ 8) | 0.9994 | 0.983 | 0.979 |
| whole command | 0.826 | 0.741 | 0.763 |

- Direction is driven by candidate features for all three (drop-family −11 to −14 pp); the two top teams leave about a
  quarter of moves undetermined by the local view (Heartbreaker a sixth). Calibration: near-certain moves 28 % /
  17 % / 21 %, near-ties 13 % / 22 % / 18 % (Heartbreaker / cheji bt / Stockfish), all calibrated (ECE ≤ 0.022).
- cheji bt splits on 27.5 % of eligible turns (Heartbreaker 9.7 %), with no simple rule; child sizes are more varied
  (many 8+ children). Stockfish's gate tree: no exit → split; in the open, split after eating at length ≤ 4, with
  branches at rounds ~250 and ~350. Stockfish also emits single-direction sonar rays, which neither other team does.
- Memory beyond the current view (action history + decayed spatial trail; 400-game subset per team): direction
  +0.97 pp for cheji bt (0.7448 → 0.7545, mostly its own-position trail), +0.39 pp for Stockfish, +0.19 pp for
  Heartbreaker; the split gate gains nothing. Memory does not close the gap: a quarter of their moves stay
  undetermined by the current view plus simple memory of it.

## Q2 — behaviour around blocked states (all games)

| state | Heartbreaker | cheji bt | Stockfish |
|---|---|---|---|
| trapped, split legal | split 99.9 % | split 98 % | split 98 % |
| trapped, split not legal | step into a wall or an ally head (all die; ally head-on kills the ally) | **self-kill in place 97 %** | wall 56 %, backward into own neck 27 %, ally cell 15 % |
| free exit, split not legal | never self-kills | self-kill 0.5 % (cull) | backward self-kill ~0.5 % (cull) |
| invalid splits | 0 / 186,440 | 0 / 694,397 | 0 / 547,677 |

The Heartbreaker-measured wrapper slightly lowers command accuracy for both top teams: wrapper rules are
team-specific. (Tool fix: HB-1's enumeration and `wrapper.label()` assumed non-move = split; self-kill is now its own
class. Heartbreaker's results are unaffected.)

## Q3 — stability

Both policies are static over their well-sampled spans (within / forward / backward transfer within ~1 pp for every
decision; change-points only where the corpus density changes). cheji bt: a possible split-size change on 30 Sep
06:00–12:00 UTC (one window, 308 games, flagged only). Stockfish's rating rose ~100 Elo (1980 → 2079) while its five
per-turn decisions stayed the same.

## The conversion

Medians over running games, dragons / longest / total length:

| round | Heartbreaker | cheji bt | Stockfish | Ares V06 (z1 panel) | hb1-12 (z1 panel) | tt-01 (z1 panel) |
|---:|---|---|---|---|---|---|
| 200 | 25 / 9 / 78 | 40 / 4 / 95 | 40 / 5 / 100 | 29 / 4 / 69 | 36 / 4 / 87 | 36 / 4 / 84 |
| 300 | 28 / 10 / 98 | 51 / 5 / 123 | 35 / 15 / 100 | 30 / 5.5 / 75 | 45 / 6 / 112 | 44 / 5 / 107 |
| 400 | 27 / 11 / 109 | 8 / 25 / 86 | 21 / 32 / 105 | 26 / 9 / 88 | 45 / 9 / 133 | 15 / 22 / 88 |
| 490 | 27 / 13 / 124 | 4 / 40 / 77 | 11.5 / 46 / 100 | 5 / 25 / 63 | 8 / 28.5 / 91 | 4 / 33 / 69.5 |

(Teams vs the live ladder, our bots vs the zoo panel: timing comparable, levels not.)

The cull decision (turns at length ≤ 3; GBT AUC 0.991 cheji bt, 0.975 Stockfish): rate by round — cheji bt < 1.1 % to
r300, 2.5 % r300–350, 9.4–10.5 % from r350; Stockfish 0.4–0.5 % to r250, 1.8–2.5 % after. By distance to the nearest
ally head — cheji bt 3.7 % adjacent, ~1 % beyond; Stockfish 2.9 % adjacent, 1.2 % at 2, 0.6 % at 4, ≤ 0.2 % beyond 5.

## Ports onto hb1-12 (Ares V06 + Heartbreaker's direction prior)

| version | one change | z1 W–L (hb1-12: 139–21) | gate | round-limit win rate | limit losses with a material lead | longest r490 |
|---|---|---|---|---:|---:|---:|
| tt-01-feed300 | `feed_base` 40 → 140 (feeding from ~r300) | 136–24 | fail (−1.88 pp; own body +37 %) | 0.80 (0.78) | 20 % (57 %) | 33 (28.5) |
| tt-02-feed250 | `feed_base` 190 (from ~r250) | 131–29 | fail (−5.00 pp; own body +49 %) | 0.74 | 24 % | 34.5 |

Head-to-heads, ten live maps, 40 fixed fixtures: hb1-12 vs the Heartbreaker mimic 33/40; tt-01 vs the mimic 29/40
(paired: 4 W→L, 0 L→W); tt-01 vs hb1-12 19/40.

- Earlier feeding does what it is meant to (cheji bt's schedule reproduced; material no longer wasted at the round
  limit) and costs elimination wins against opponents that can be eliminated or that never convert.
- r250 is too early for Ares: Stockfish's feed is slow and proximity-weighted; Ares's is all-or-nothing near the
  crown, so the start round without the rate over-converts.
- Two notes on the gate for this kind of change: the economy mean uses pearls to r250, so a conversion change cannot
  move it; and the own-body hygiene rate counts feeder suicides, so it penalises deliberate feeding by construction.

## What to take, and what is open

- **Conditional conversion, not a fixed earlier round.** Keep the swarm while elimination is on; convert on the top
  teams' schedule when it is not. The measured ingredients: a rate schedule (cheji bt ~10 %/turn from ~r330,
  Stockfish ~2 %/turn from r250) rather than an instant feed; feeding toward any adjacent longer ally (Stockfish) as
  well as toward an elected crown.
- **Die in place when trapped** (cheji bt) instead of stepping into an ally.
- **Not worth a mimic.** A local-view copy of either team would match ~0.74–0.76 of commands; Heartbreaker at 0.83
  gave a mimic at half strength. Their strength is in decisions that depend on more than the local view, and in the
  conversion, which is a rule we can write.
- **Open, not measurable locally:** whether matching their conversion timing wins against teams that convert. It needs
  games against such teams.

## Ledger rows touched and proposed weights

| row | current | proposed | evidence |
|---|---:|---:|---|
| L03 (H10) phase bifurcation → phase-conditional logic keyed on state | 0.5 | **0.6** | Both top teams run an explicit phase switch (swarm → conversion), Stockfish with round thresholds; a fixed earlier round on our bot fails, pointing to state-keyed conversion rather than a clock. |
| L27 learned decision functions | 0.7 (HB-1 proposal) | 0.7 (unchanged) | The cull decision is learnable (AUC 0.975–0.991) but is better written as a rule; the top teams' steering is less learnable than Heartbreaker's. |
| new: endgame conversion timing/rate is where the top two differ from the rank-40 swarm | — | 0.8 | Trajectories over 4,126 + 1,932 + 817 games; round-limit win rate 0.75 / 0.72 vs 0.26. |
| new: converting earlier pays against opponents that also convert | — | 0.5 | Not measurable locally (tt-01 even vs hb1-12, worse vs non-converting opponents); needs ladder games. |
