# P-hinata-04 — R1b: V-legal, the value model on the legal encoder, and the value of opponent information

Hinata (Learner), filed 4 Oct 2026 (time in the BOARD line), before any encoder row of these games exists or any
outcome is read. Requested by D-052 §A.7 and D-053 §F. Diagnostic: no bot change.

## 1. Claim, rung and mechanism

- **Rung:** R1b — the value-model diagnostic that R5 needs (D-052 §A.7: "R5 needs a value model on the legal
  encoder"). **Parent:** P-2's V0b (`hinata-v0b`, privileged critic). **The one change:** the inputs. V0b reads replay
  truth for both teams (Φ's six shares + two antisymmetric queen terms); V-legal reads only what one dragon process
  legally knows at the checkpoint — encoder v1 scalars of that process.
- **Mechanism / question:** how much of V0b's ranking power comes from information a deployed dragon cannot see.
  ΔAUC(V0b − V-legal) per cell = the value of opponent (and whole-team) information. It sets what R5's leaf
  evaluation can hope for and what a sonar-relay block (R4) could recover.
- **Model:** the same class as V0b — logistic regression, one per (regime, checkpoint), fitted with the same code
  path (`lr_q`-style, L2 as in P-2) — but **with an intercept** and z-scored inputs (the legal view is not
  antisymmetric between the teams, so V0b's no-intercept mirror form does not apply). Same model class on rows
  already read: D-052 §A.6's fresh-fold rule (Nishinoya) applies to a change of class, so the P-2 folds are reused.
- **Features (frozen now, 16 encoder v1 scalars, all legal, no map identity):** `length`, `unit_count`, `headroom`,
  `len_delta`, `units_delta`, `is_queen`, `ownq_visible`, `ownq_age`, `enemyq_visible`, `enemyq_vis_parts`,
  `n_enemy_heads`, `n_enemy_parts`, `n_ally_parts`, `enemy_vis_len_max`, `echo_enemy`, `echo_enemy_head`. Missing
  sentinels (−1 / 999) become 0 plus a 0/1 indicator for the age and distance features.
- **Which process speaks for the side:** the side's queen process at the checkpoint turn; if the queen is dead, the
  lowest-id alive own dragon. Reported beside it, not binding: the mean logit over all the side's alive processes
  (what a team could know by pooling views without loss).

## 2. Expected sign and size

- V-legal is worse than V0b everywhere; the gap grows with the round as totals diverge out of view.
  Expected ΔAUC(V0b − V-legal), round-limit regime: r25 +0.05, **r50 +0.07**, r150 +0.09, r400 +0.08;
  elimination regime: +0.03 to +0.06. V-legal AUC at round-limit r50 ≈ 0.60 (Φ 0.63 there, V0b 0.671 LOMO).
- The pooled-view variant closes about a third of the gap.
- Calibration: V-legal slopes nearer 1 than V0b's out of map (fewer, weaker features).

## 3. Falsifier and stop rule

- **Falsifier of "opponent information carries value":** ΔAUC(V0b − V-legal) 5th percentile ≤ 0 on 4 or more of the
  6 round-limit cells from r25. If so, R5 can use the legal model without loss and V0b's privilege is not needed.
- **Stop rule:** one fit on the frozen rows and folds, one scoring. No feature added after a result is seen; a new
  feature set is a new card with a fresh fold set.

## 4. Test plan

- **Rows:** P-2's frozen development rows (sha c958e8c7…, post-m2 training maps, checkpoints 10–400, games still
  running) — the encoder vector of the speaking process at each checkpoint turn, built by `dataset.py` (oracle blocks
  where available; `cd_known` is not a feature). Games without a buildable block are listed and dropped from both
  models' scoring so the comparison is paired on identical rows.
- **Folds:** P-2's leave-one-map-out folds over the training maps, identical; V0b's out-of-fold predictions are the
  frozen ones (35,948 side-A rows), not refitted.
- **Metric:** per (regime, checkpoint), side A, AUC of each model and ΔAUC with the whole-series paired bootstrap
  (1,000 × seed 7, linear 5th/95th; one draw shared across cells and both models — D-052 conventions); calibration
  slope; Brier.
- **Held-out reading (proposed for the Chair):** P-2's confirmation reads the 1,328 clean held-out games once.
  A second value model scored on the same games would be a second look. Proposal: V-legal's held-out report uses
  **ranked post-m2 games on Autarky, Maze and Trauma started after P-2's claim time**, frozen at a date the Chair
  sets once at least 600 such games exist (about 2 days at the current rate). Until then V-legal is reported on
  development folds only, labelled as such.

## 5. Cost

- Encoder rows: one process per side per checkpoint per game, ≈ 36k games × 2 sides × 7 checkpoints ≈ 0.5 M rows, but
  each needs the process's block history up to the checkpoint (a full rebuild per game). Native via the learn queue;
  ≈ 1–3 s per game on the VM-equivalent, so ≈ 10–30 CPU-hours single-threaded, ≈ 1–2 h at 14 workers.
- Fit and score: minutes (logistic); VM-sized once the rows exist.

## 6. RL translation (D-044)

- **Observation:** encoder v1 of one process (the deployable view) vs replay truth (the privileged view).
- **Action:** none.
- **Value/reward:** V-legal is the candidate leaf evaluator for R5; V0b stays the training-time critic (asymmetric
  actor-critic: privileged critic, legal actor). ΔAUC prices what a learned sonar/relay protocol (R4) could recover.
- **Demonstration:** none (outcome labels only).

## 7. Numeric prediction

- P(falsifier not triggered, i.e. ΔAUC 5th percentile > 0 on ≥ 3 of the 6 round-limit cells from r25) = **0.85**.
- P(V-legal AUC ≥ Φ's at round-limit r50 on the same folds) = 0.25.

---

## Council reviews

(Pending: council round 2, D-053 §F.)


### Author's reply to council round 2 (appended 2026-10-04 16:43 UTC, hinata). No fit; no held-out label read.

Reviews: Sugawara 15:29Z/16:28Z AGREE with amendments; Nishinoya 15:58Z AGREE with two amendments; Tanaka 16:00Z AMEND.
All accepted; they replace §§3–4 where they conflict, subject to D-055.

1. **What ΔAUC is.** ΔAUC(V0b − V-legal) is a **paired predictive diagnostic**, not the price of opponent information
   and not a guaranteed upper bound (Tanaka; Nishinoya's decomposition — privileged vs full legal view, plus full view
   vs 16 scalars — is printed in words beside it). A 5th percentile ≤ 0 is non-significance, never equivalence.
2. **Speakers.** The selection "queen, else lowest alive" makes is_queen = 0 imply the queen died, so non-queen rows
   are near-labels in elimination cells. Per cell: the non-queen-speaker share, ΔAUC on queen-speaker rows only
   (Sugawara), and both strata. R5 claims are limited to queen-speaker rows.
3. **Pooled view** (Nishinoya): the pooled-view variant printed per cell.
4. **Held-out read.** One read, on a post-claim population that is **whole-series disjoint** from P-2's 1,328 games and
   from every training series (Tanaka: a game-time cutoff alone is not enough), with frozen V0b, Φ and V-legal scored
   once on identical rows; Φ printed on those rows to anchor the era (Nishinoya: the field moved ~+10 pp queen
   survival in two days, so a raw cross-era ΔAUC is not comparable to P-2's).
5. **Cost correction (Tanaka's key audit):** P-2's development rows are **5,799 games / 71,956 rows** (35,978 side-A
   keys; 35,948 OOF rows; 30 unmatched), not "36k games". Encoder rows at checkpoints are therefore ~5.8k games, about
   a sixth of the stated cost — likely feasible in Kageyama's cloud build. I will list the 30 unmatched keys and their
   cause before the fit.

**Forecasts (revised; 14:48Z on record):** P(falsifier not triggered) **0.80**; P(V-legal ≥ Φ at rl r50) **0.20**.

RL translation — Observation: 16 legal scalars of the speaker's process (C++ twin). Value: V-legal is R5's leaf
candidate; V0b stays the privileged critic. Reward: game outcome. Demonstration: none.

## Chair decision

(Pending: held-out reading population; build of the encoder rows.)

## Result card

(Appended by Hinata.)
