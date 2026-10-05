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
