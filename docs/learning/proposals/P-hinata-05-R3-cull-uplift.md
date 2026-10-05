# P-hinata-05 — R3 next route: a learned cull gate for `bokuto-13-cull`, fitted from the base's own logged randomisation

Hinata (Learner), filed 2026-10-05 07:38 UTC, before any of the three remaining clone arms (D-077 §E) is read and
before any per-event outcome of a `bokuto-13-cull` game is read. Answers D-077 §E ("Hinata then proposes one next
route with a forecast"). **Conditional:** it becomes the active route only if the D-077 §E stop rule fires (no
clone arm with paired 5th percentile > −5 pp vs carthage-05). Stage S0 is diagnostic and VM/cloud-sized; S1 is a bot
change and needs the Chair.

## 1. Claim, rung and mechanism

- **Rung:** R3 (one more head: cull), on the new base `bokuto-13-cull` (D-077 §A local reference).
- **Why not another clone (lesson of D-074…D-077):** A1-400 predicts top-team directions better than the live prior
  (0.720 vs 0.698 on dev120 rows) yet plays 6–7 pp worse at equal entropy. Off-line agreement with teachers is not
  in-play value inside a search co-tuned with its own prior. A head cloned from teachers' cull/split timing inherits
  the same risk. The safer target is **the base's own decision, scored by its own outcomes**.
- **The natural experiment already in the base:** `bokuto.hpp:273` culls an eligible spare length-2 dragon only when
  `((me*7919 + rnd*131) & 7) == 0` — a 1-in-8 hash of dragon id and round, independent of board state. So in every
  `bokuto-13-cull` game, eligible dragon-turns are randomly assigned cull (p = 1/8) or no cull (7/8): logged
  propensities, i.e. contextual-bandit data, at zero extra compute (Asahi's 272 pool + 80 var replays exist:
  `../wt-asahi/build/asahi/runs/bokuto-13-cull/d192d721/`).
- **The one change (S1):** replace the hash in `cull()` with a learned gate: cull iff the uplift model's predicted
  advantage of culling in this state > 0 (all other conditions unchanged). No map identity; inputs = encoder v1
  block + Kageyama's trajectory columns (`x_traj_*`, TRAJ_VERSION 1), all bot-legal.

## 2. Stages

- **S0 (diagnostic, no bot change).** Reconstruct the eligibility superset from replays (own length 2, units ≥
  limit − 1, round 60–340, not the queen, no pearl in view, dragon id & 4095 > 1) — `g_br->demand` and `dec.why` are
  internal, so the superset is diluted; the hash is exact. Per event: treatment = hash hit; outcome = own team's
  Δ(total length) and Δ(units) over the next 20 and 50 rounds (team-level, so interference is inside the outcome),
  and game result. Estimates: (a) intent-to-treat effect of a hash hit (unbiased by design, diluted by the superset);
  (b) game-level regression of result on #hits given #eligible (instrument for cull count); (c) T-learner / IPW uplift
  by state with series-grouped folds, reported only on the training maps.
- **S1 (bot, Chair-gated).** If S0(c) finds a state split with positive out-of-fold uplift, export the gate (depth ≤ 3
  tree or logistic; ≤ 10 inputs) to a copy `bots/hinata-…` of `bokuto-13-cull`; hand to Asahi for one seed-1 pool
  paired vs `bokuto-13-cull` and carthage-05, plus the probe. Evaluator decides the trial.

## 3. Expected sign and size

- S0(a): hash hit raises own Δlength@50 (the cull exists to free a slot for a corridor split) — sign +, small (≤ 1
  length unit per event), P(sign + with 90 % interval excluding 0) 0.35 at n ≈ 272 games.
- S0(c): heterogeneity: uplift + when a corridor is near and enemy contact is absent (`close20` = 0), − under
  contact. P(an out-of-fold split with uplift gap > 0 at 90 %) 0.30.
- S1 pool vs `bokuto-13-cull`: point +1 pp, P(paired 5th pct > −3 and point > 0) 0.30; P(point ≥ +3) 0.12.

## 4. Falsifier and stop rule

- S0 stops the route if (a) and (c) both show nothing (intervals cover 0, no out-of-fold split): then cull timing is
  not learnable at this n, and the route moves to the second candidate (value model on the base's self-play, §8).
- S1: one gate export, one pool. If paired point < 0 vs `bokuto-13-cull`, the gate is dropped; no tuning loop on the
  pool.

## 5. Splits and leakage

- Pool and var panels include held-out maps (Autarky, Maze, Trauma; PROPOSED-hinata-heldout-maps). **Rows from
  held-out maps are excluded from every fit and every S0 estimate** (filtered by replay file name before parsing).
  Fixture opponents are not held out (eval-only bots), noted.
- Pool games are also the S1 evaluation panel: S1 is scored on a **new seed** (seed 2) pool, not on the replays it
  was fitted on.

## 6. Cost

- S0: replay parsing + features on the VM/cloud (≈ 272 × 2 seats, ≈ 1 h compute in ≤ 150 s steps, or one Mac learn
  job ≈ 10 min); fits are small (≤ 100 k rows).
- S1: one export (Kageyama-style or hand-written ≤ 30 lines C++), one pool + probe (≈ 25 min Mac).

## 7. RL translation

- Observation: HB-1/encoder v1 + trajectory columns at the decision.
- Action: binary cull at eligible turns (a new head).
- Value/reward: Δteam length/units over 20/50 rounds as short-horizon reward; game result as the return.
- Demonstration: none — this is learning from the base's own randomised behaviour (off-policy, logged propensity 1/8),
  the first lane artifact that does not imitate a teacher.

## 8. Weighing the Chair's candidates

| Route | For | Against | P(useful pool gain ≥ +1 pp within 2 units of Mac) |
|---|---|---|---|
| **Cull gate from logged randomisation (this card)** | data exists now; propensities known; base's own outcome | small n of events; diluted eligibility | 0.30 |
| Clones of split/corridor timing from teachers | labels exist (`y_kind`, `y_child`) | same failure mode as the direction clone (teacher ≠ base) | 0.12 |
| Value model on the base's self-play | general; feeds R5 | no V leaf in the base's search; V0/V0b failed confirm; integration cost high | 0.08 |

Frozen objective: S1 pool Δwin vs `bokuto-13-cull`, seed 2, 272 paired, map × opp clusters 1,000 × seed 7, 5–95 %.

## Reply to Sugawara's review (docs/learning/reviews/P-hinata-05-sugawara.md) and D-078 §D — amendment filed 2026-10-05 08:37 UTC, before any S0 number is read

**Accepted in full.** Algebra re-checked: 7919 ≡ 7, 131 ≡ 3 (mod 8), 3⁻¹ ≡ 3, so the hit condition is rnd ≡ 3·me (mod 8)
(me = full id `w.me`; the phase is set by me mod 8). My S0(a) per-turn "hit vs no hit" design was wrong: it would
estimate a few rounds of delay, not cull vs no cull, and the rows are not p = 1/8 draws. S0 is replaced as below; the
§3 S0 forecasts are withdrawn.

**S0 (amended, frozen now).**
1. *Cull signature.* Bot logs are off in the pool (`logs: false`), so a cull is identified from frames: own death,
   cause `self`, length 2, id & 4095 > 1, round 60–340, on a round ≡ 3·id (mod 8). Self-deaths of length-2 spares off
   that phase are counted and reported as a misclassification check (expected ≈ 0).
2. *Unit (primary) = per-dragon eligibility spell* on the turn-start-legal superset of §2 (length 2, not queen,
   team units ≥ limit − 1, round 60–340, no pearl in the dragon's view, head not on a corridor cell where the frame
   gives one); r0 = first eligible round; **instrument D = (3·id − r0) mod 8**. Diagnostics: D histogram (expected flat),
   spell-length distribution.
3. *First stage:* P(cull observed in spell | D), with the gap G = P(cull | D = 0) − P(cull | D = 7).
   **Stop rule (fixed now): G < 0.25 → no cull-vs-no-cull contrast; the route stops at S0 with a timing-only report
   and I file the self-play V route (§8) as the next card.**
4. *ITT / Wald:* team Δlength and Δunits at r0+20, r0+50 and game result on D (D = 0 vs D ≥ 4 and linear in D);
   Wald = ITT / first-stage gap; game (series) clusters, 1,000 × seed 7 bootstrap, linear 5–95 %; training maps only
   (Autarky, Maze, Trauma dropped by file name).
5. *Interference (co-primary at team level):* one cull drops units below limit − 1 and closes every teammate's spell,
   so I also report the team "cap spell" (maximal run with team units ≥ limit − 1 and ≥ 1 eligible spare), instrument
   D_team = min delay over the spares eligible at its entry (categorical; not uniform, histogram reported).
6. *Hand strata before any model* (Sugawara): D-contrast by corridor near (yes/no) × enemy head within 20 (yes/no).
   An uplift model (S0(c)) is fitted only if a stratum's D-contrast excludes 0 at 90 %.

**S1 additions.** The gate means "cull at the first eligible round when predicted positive, otherwise never"; a
TRAJ_VERSION 1 bot-side parity check of every `x_traj_*` input precedes the export. Card file: this file is P-9's own
card (D-078 §D); S1 still needs the Chair.

**Forecasts (replacing §3 for S0):** P(G ≥ 0.25) 0.40; P(a D-contrast effect on team Δlength@50 excluding 0 at 90 %)
0.18; S1 given S0 passes: point +1 pp, P(5th pct > −3 and point > 0) 0.25 (Sugawara's, adopted).

## Result card — S0 first stage, 2026-10-05 08:40 UTC (one pass, frozen rule of 08:37Z applied as written)

**Verdict: the S0 stop rule fires. G = P(cull | D = 0) − P(cull | D = 7) = 0.0179 [0.0129, 0.0228] < 0.25** (65,753
eligibility spells from 91 games in which bokuto-13-cull reached 63 units, of 224 training-map pool games; seed-1
pool, unswbc 1.2.3, FRAME_VERSION 7, post-m2 bots; map × opp clusters (48) 1,000 × seed 7, linear 5–95 %). The route
stops at S0; no outcome (ITT, Wald, strata, uplift) was computed or read.

| D | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|---|---|---|---|
| spells | 8,277 | 8,249 | 8,201 | 8,338 | 8,048 | 8,200 | 8,218 | 8,222 |
| P(cull in spell) | 0.0199 | 0.0135 | 0.0085 | 0.0046 | 0.0061 | 0.0035 | 0.0012 | 0.0021 |

- **Diagnostics.** D histogram flat (8,048–8,338): the instrument is as-randomised. Spell length: 1 round 36.6 %,
  ≥ 12 rounds 4.1 %; 747 spells a game at cap. Signature check: at-cap self-deaths of length-2 spares, rounds 60–340, by
  residue (round − 3·id) mod 8: **544 at 0 vs 58–81 at each of 1–7** — the signature is real (w.rnd = frame round,
  limit 64), but ≈ 68 of the 544 (≈ 12.5 %) are non-cull self-deaths at the base rate; my "≈ 0" expectation failed.
  ≈ 476 true culls in 91 games (≈ 5 a game at cap; none in 133 of 224 games).
- **Why the rule fired — not the failure it was written for.** Sugawara's concern was saturation (first stage flat
  near 1). The data show the opposite: **dilution**. When the hit round is reached inside a spell, P(cull) = 0.0199
  (24,561 spells): the internal conditions (`g_br->demand`, head on a corridor cell, `dec.why` f/c) and the pearl-in-view
  approximation block ≈ 98 % of hash hits. The superset is not the bot's eligibility set, so a D-contrast has ≈ 2 %
  compliance and no usable power. Narrowing the superset now would be a post-hoc change after reading the first
  stage; I do not do it under this card.
- **Leverage bound (descriptive).** The cull fires ≈ 5 times a game, only in the 41 % of training-map games that reach
  the cap; even a perfect gate acts on few events. This lowers my prior for any cull-timing head, independent of the
  identification problem.
- **Forecast scoring:** P(G ≥ 0.25) 0.40 → outcome no (Brier 0.16). Sugawara 0.45 (0.20).

**Next (as frozen at 08:37Z):** I file the self-play V route (§8) as the next card, with a forecast, next unit.

**RL translation.** Observation: unchanged. Action: a cull head is not learnable from this base's logs — the hash is
not the binding gate (≈ 2 % compliance). Value/reward: none estimated. Demonstration: none. Lesson for any
logged-randomisation design: randomise at the last gate before the action (or log the gate's inputs with the bot), or
compliance dilutes the instrument to nothing.
