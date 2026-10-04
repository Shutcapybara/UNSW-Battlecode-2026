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

### Amendment A — fallback to Φ on elimination-regime maps before r150 (appended 2026-10-04 18:38 UTC, hinata; Chair 18:32Z)

Ordered by the Chair after P-2's confirmation failed (elimination r25 ΔAUC(V0b − Φ) −0.0099 [−0.0152, −0.0049], 434
Autarky games). **This choice is informed by P-2's held-out read**, so it is not a pre-registered hypothesis: it is
a declared deployment rule, and P-6's confirmation stays on games played after P-2's claim (18:19:04Z), whole-series
disjoint as in reply item 4. No fit has been run; no V-legal outcome has been read.

1. **The deployable value (V-legal\*)** is a composite fixed now: V-legal\*(s) = Φ(s) if regime(s) = elimination and
   round < 150; V-legal(s) otherwise. The privileged comparison composite is V0b\* (same rule with V0b). Both are
   scored beside the plain V-legal, V0b and Φ; the confirmation's binding comparison becomes V-legal\* vs Φ
   (non-inferiority −0.01 on every cell, as P-2) plus the §3 falsifier on V0b\* − V-legal\*. In the gated cells
   V-legal\* ≡ Φ, so ΔAUC there is 0 by construction and is printed as such, not counted as a pass.
2. **Regime by structure, never map identity.** The C7-03 RL-share classes used in P-2 are a per-map label table
   (identity); they stay as the *reporting* cells only. The *gate* uses a structural rule computed from the
   start-of-game board as one process sees it: a depth-1 stump on **one** of {open-cell share, portal count,
   head-to-head spawn path length / (W+H)}, threshold chosen by leave-one-map-out agreement with the C7-03 class on
   the 14 training maps only (Autarky, Maze, Trauma never read). Frozen (feature, threshold, LOMO agreement) is written
   to this card before the V-legal fit; if no stump reaches LOMO agreement ≥ 12/14 maps, the gate falls back to
   "elimination" for all maps before r150 (Φ everywhere early) and that is reported.
3. **Why r150, not r100:** P-2's held-out elimination cells were ΔAUC < 0 at r25–r100 and ≥ 0 from r150 (Chair's
   wording). r150 is used as given; no other threshold is tried.
4. **Forecasts (new, before any fit):** P(stump LOMO agreement ≥ 12/14) = 0.55; P(V-legal\* non-inferior to Φ on every
   cell at confirmation) = 0.35 (the legal view is weaker than V0b on round-limit maps where V0b's margin was large).

RL translation — Observation: start-of-game structure (one stump feature) selects the critic; encoder v1 scalars feed
V-legal. Action: none. Value/reward: regime-gated leaf value for R5 (Φ early on elimination boards). Demonstration: none.

### Author's reply to Sugawara's review of Amendment A (appended 2026-10-04 19:41 UTC, hinata). No fit; no stump selected yet; no held-out map read.

Review: `docs/learning/reviews/P-6-amendA-sugawara.md` (19:30Z), verdict AMEND §2.

1. **Accepted in full.** The three named candidates (whole-map open-cell share, whole-map portal count, spawn-to-spawn
   path / (W+H)) are not observable by a process at turn 1 (wrapping 7×7 window; portals do not extend vision; enemy
   heads and SYMMETRY are not in the IO block). Gating a "deployable" value on them would reproduce the train/deploy
   skew V-legal exists to remove, and is map identity in effect. I meant "the whole map", so this is a real change, not
   a rewording. **§2 now reads:** the stump's candidates are only IO-observable quantities fixed at turn 1 —
   W·H, W+H, min(W,H) (`get_map_size`); own-window open share at turn 1; portals in the own window at turn 1; own unit
   count at turn 1. Window features are computed per process from the map file's spawn tiles and the 7×7 wrapping
   window exactly as the engine reveals it, then reduced to one value per map (median over our team's spawn processes;
   the reduction is fixed now). LOMO on the 14 training maps, ≥ 12/14, else the declared fallback (Φ everywhere before
   r150) — unchanged. A running "observed-so-far" feature would be a new card.
2. **Label era printed.** The frozen stump is written with `label_era = post-m2 (v0.py ELIM_M2)`; reuse after a field
   shift only after a re-check (Sugawara point 2).
3. **Your size-only replication** (W·H ≤ 1362, LOMO 11/14; misses Portals, Prisoners Dilemma, weakhold) is taken as
   given for the size candidates; I will reproduce it in the selection script and add only the three window
   candidates. The selection script is new lane code (training-map headers and spawn windows only) and runs before
   any V-legal fit.
4. **Forecasts revised (before any selection):** P(observable stump LOMO ≥ 12/14) 0.55 → **0.25** (agree with
   Sugawara: size tops out at 11; window shares are noisy); P(V-legal\* non-inferior to Φ on every cell) 0.35 →
   **0.38** (the likely fallback makes the early elimination cells 0 by construction).

### 1b. Precedent (appended 2026-10-04 19:41 UTC, D-058)

- **Value heads trained on the deployed observation** (AlphaZero/MuZero value head; Hungry Geese and Lux AI top
  agents' critics trained on the agent's own observation tensor): the critic sees what the policy sees, so no
  regime switch is needed. V-legal follows this; V0b (privileged, full-board) is the departure we measured.
- **How close:** ours is partially observable (7×7 window) like Hungry Geese, unlike Kore/Halite (full observation).
  Where a map-level prior is used under partial observability, it comes from map size and history only.
- **Departure:** the Φ fallback before r150 is not from precedent; it rests on our own evidence (P-2's held-out
  elimination cells, informed, hence confirmation on later games only).

### Amendment A §2 — stump selection result (appended 2026-10-04 19:46 UTC, hinata). Training-map headers and spawn windows only; held-out map files skipped by file name before opening; no V-legal fit; no outcome read.

Code `tools/hinata/regime_stump.py` sha de7d07aa3829…; output `build/hinata/p6/stump.json`. label_era = post-m2
(v0.py ELIM_M2, C7-03; 6 elimination / 8 round-limit training maps). Window = edges with both end tiles in the wrapping
7×7 window centred on each team-0 head (first DRAGON segment), median over the team.

| candidate | in-sample | LOMO | LOMO misses |
|---|---|---|---|
| W·H (≤ 1362.5 → elim) | 11/14 | **11/14** | Portals, Prisoners Dilemma, weakhold |
| units at turn 1 (≤ 2.5 → elim) | 11/14 | 11/14 | Default, Devil, weakhold |
| W+H | 11/14 | 9/14 | + Queen Of Spades, Default |
| win_portals | 8/14 | 8/14 | 6 maps |
| win_open | 10/14 | 7/14 | 7 maps |
| min side | 10/14 | 5/14 | 9 maps |

**Decision (declared rule): FALLBACK — no stump reaches 12/14, so V-legal\*(s) = Φ(s) for every map before r150,
V-legal(s) from r150.** Sugawara's W·H replication (11/14, same three misses) reproduced exactly. No second stump, no
two-feature rule, no other threshold is tried (one stump was declared). Consequence for the confirmation: every cell
before r150 is Φ vs Φ = 0 by construction and is printed as such, not counted as a pass; P-6's evidence lives in
r150–r400 cells. Forecast P(V-legal\* non-inferior on every cell) stays 0.38.
