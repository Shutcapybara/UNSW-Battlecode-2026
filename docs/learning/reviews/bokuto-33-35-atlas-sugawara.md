# bokuto-33/34/35 (atlas on again) — D-080 §D conditions and the hidden-layout cost of 35's known-bed term — Sugawara (unit 30, 5 Oct 2026 16:25–16:40Z)

Unassigned (step 3 of my unit: a gap before these bots reach the trial queue). Bokuto's JOB lines (BOARD 15:48Z, 16:00Z, 16:20Z) ask Asahi for pool, qk2, h2h vs kenma-03 and probe. Read: r/bokuto 5273710a9 (wt-bokuto), `bots/bokuto-35-knownbeds/{policy.hpp,world.hpp,params.hpp,atlas.hpp}`, diff 34 → 35.

## 1. The ruling that applies

33, 34 and 35 carry bokuto-30's change (d): the 17-map atlas on again (`atlas.hpp` n_maps = 17), whole-map routes for corridor targets, the queen and feeders. 35 adds one target-value hunk (policy.hpp l.835): an unseen cell with `bed == 1` and atlas class 1–5 is worth 0.7 × bed_value. D-080 §D admits an atlas bot only with (i) the gen panel, paired 5th pct above −5 vs `bokuto-13-cull`; (ii) the hidden-layout block not below 13-cull's; (iii) the `n_maps = 0` twin, built by Asahi as a copy, so the card shows how much of any gain is the atlas. **None of the three is in the JOB lines.** The pool, qk2 and h2h panels are all on template layouts, so they cannot see the atlas's cost; 17-map atlas gains on those panels are partly map identity by construction (Bokuto's motivating evidence is the Trophy seat-B local mirror, which is exactly an atlas-matched public map).

## 2. Replication: how often is a "known fast bed" real on the hidden layouts?

`build/sugawara/knownbeds/kb.py` (uses Bokuto's own `tools/bokuto/build_atlas.py` parser; frozen inputs `maps/live/*.map`, `maps/live_var/*.map`; output `out.txt`):

| hidden layout | template (edge match) | template fast beds (class 1–5) | still a bed | still fast | hidden fast beds not in template |
|---|---|---|---|---|---|
| devil_b | devil (exact) | 30 | 18 | 18 | 2 |
| dilemma_10 | dilemma (exact) | 8 | 8 | 8 | 0 |
| queen_of_spades_b | queen_of_spades (exact) | 0 | 0 | 0 | 0 |
| slithery_fight_b | slithery_fight (exact) | 131 | 118 | 108 | 8 |
| schooltime_open4 | schooltime (4 edges differ: no match) | 26 | — | — | — |

So the term is mostly right where it fires: phantom fast beds are 12/30 on devil_b (40 %) and 23/131 on slithery_fight_b (18 %). The cost is bounded by `!w.seen[c]` (a phantom drops when seen), i.e. wasted opener walks, not a lasting wrong belief. Expected sign on the hidden block: small negative to neutral on devil_b; neutral elsewhere. This is weaker than my unit-21 worry, and it is a structural count, not a game result.

## 3. Verdict: amend (the reads, not the code)

- **Add to the 34/35 jobs, before either enters the trial queue:** the hidden-layout block (both totals; devil_b and slithery_fight_b shown apart), the gen panel vs 13-cull, and the `n_maps = 0` twin of 35 (Asahi copy). Read 35 paired against 34 (its one-hunk parent), and 35 vs its twin; the twin difference is "how much is the atlas".
- **Cheap fix if devil_b shows harm** (D-080 §D's own suggestion): drop the matched layout at the first observed pearl that contradicts it (or on a seen template fast bed with no pearl after its class gap), instead of correcting cell by cell.
- **33 bundles five changes** over 27 (28, 25, 32, 30, 33). Its card cannot attribute; 34 and 35 are one-hunk steps on it, which is fine for them, but any 33-line candidate inherits the bundle. If it qualifies, the LOO idea (D-076 §C) applies.
- Legality: atlas is compiled from public maps, matched on observed terrain at turn start (world.hpp l.276–362, `learn_edge` overwrites); observable. Admissible in a free-lane bot under D-080 §D; the hard rule (`_common.md` l.21) binds it if it reaches a ladder rung, so the three conditions are not optional there.

## 4. Seat note (Bokuto 16:20Z: 17530 12–8 as seat A vs 48–52 as seat B)

0.60 vs 0.48, difference 0.12 with SE ≈ √(0.24/20 + 0.25/100) ≈ 0.12, so about one SE: no evidence of a seat effect yet. A seat column at the look is cheap and fine; it should not be read before ≥ 40 games per seat.

## 5. Forecasts (log only; Brier closed by D-072 §B)

- 35 − 34 on the pool win rate ≥ +2 pp: 0.35. 35 − twin(n_maps = 0) on the pool ≥ +2 pp: 0.45. 35's hidden-layout block below 13-cull's by > 2 games of 80: 0.25.

Precedent: Halite/Lux bots that hard-code map priors lose on new seeds; the standard remedy keeps geometry priors and learns resource priors online, which is what the per-layout drop rule does.
