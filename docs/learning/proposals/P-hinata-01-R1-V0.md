# P-hinata-01 — R1 V0: GBT value model on Φ's features plus queen terms

Lane: hinata (Learner, Claude Opus). Written 4 Oct 2026 10:45Z, **before any outcome on a pool map was read**.
The Chair may renumber this card to P-<n>; the content is frozen from the timestamp above.

## Claim, rung, mechanism
- **Rung R1 (V0).** Diagnostic only; no bot change, no deploy gate.
- **Claim.** A GBT per regime x checkpoint on Φ's six opponent-relative shares **plus four queen terms** ranks post-m2 outcomes at
  least as well as Φ (logistic, same six shares, refit on identical folds) at every checkpoint, and better late on round-limit maps.
- **Mechanism (information, not re-weighting).** Under 1.2.3 the round-limit tiebreak is queen → longest → total, and ~45–50 %
  of ranked post-m2 round-limit games are queen-decided (Chongqing C5-02/C8-01). Φ has no queen term. The added terms are:
  `q_alive_own`, `q_alive_opp`, `q_len_rel` (queen length own vs opponent, dead = 0), `q_vs_longest_opp` (own queen vs the
  opponent's longest dragon). The GBT also allows interactions (e.g. a longest lead matters only when both queens are dead).

## Data and splits
- S-1 store (`build/s1/corpus`), `map_era = post-m2`, `in_scope`, server verdict `result_a ∈ {0,1}` (19 draws dropped).
  Coverage at freeze time: 7,057 decoded games, 17 maps, 323–514 games/map; queen features present on 96 % of r100 rows.
- **States:** a checkpoint row exists only if the game is still running at that round (ended rows dropped — 2,278/7,057 games
  have ended by r400). A Φ-comparable variant with ended rows kept is reported separately, never gated.
- **Held-out maps:** whatever D-045 (Phase 3) freezes. `fit` reads the manifest and never loads those maps; `confirm`
  scores them **once** and writes a `CONFIRMED` flag that blocks re-runs.
- Regime (diagnostic): Chongqing C7-03 — A (7 maps) = elimination, B+C+D+E (10 maps) = round-limit. Map-name based, so
  **not deployable**; a structural regime classifier is an R4/R5 item.
- Symmetry: both sides' rows train the model with mirror augmentation; prediction = ½[p(x) + 1 − p(mirror x)].

## Frozen objective and gate (macro §1 R1, with the reading made explicit)
Development = leave-one-map-out over the training maps; one row per game (side A) per cell; cell = regime x checkpoint
(r10, 25, 50, 100, 150, 250, 400) on post-m2.
1. AUC(V0) ≥ AUC(Φ) point estimate in **every** cell. Game-cluster bootstrap 90 % interval on ΔAUC reported (1,000 resamples, seed 7).
2. Round-limit r50 AUC(V0) ≥ 0.66.
3. Calibration slope of V0 in [0.9, 1.1] in every cell from r25 on.
4. Confirmation: the same three checks on the held-out maps, one shot. A dev PASS with a confirmation FAIL is a FAIL.
Stop rule: one fit, one confirm. No hyper-parameter search after reading any pool-map outcome. A FAIL produces a diagnosis
card (which cell, which criterion), not a re-run.

Hyper-parameters fixed now: LightGBM, 300 trees, lr 0.03, 15 leaves, min_child 40, subsample 0.8, colsample 0.9, λ 1.0.

## Expected sign and size
- r10–r50: ΔAUC ≈ 0 (± 0.01): queens are nearly all alive, the queen terms carry little.
- r150–r400, round-limit: ΔAUC **+0.02 to +0.06**: the queen gap opens (top ten alive ~0.41–0.47 at RL end, field 0.25–0.35).
- Elimination maps: ΔAUC ≈ 0 to +0.01 throughout.

## Falsifier
ΔAUC < 0 in any round-limit cell from r150 on, or no round-limit cell with ΔAUC > +0.01: the queen terms add nothing a value
model can use, and H-Q8's value side is refuted at the game-state level.

## P(pass) and the risk I see
**P(pass) = 0.25.** Expected effect: +0.03 ΔAUC at RL r250. The main risk is the conjunction, not the mechanism: 14 cells must all
hold ΔAUC ≥ 0 by point estimate (r10 is near chance for both models, so a coin-flip there can fail the rung), and 12 cells
must hold a GBT calibration slope inside [0.9, 1.1] under map shift. My P(mechanism real: RL r250 ΔAUC lb > 0) is 0.65.
**Request to the Chair (dissent with the macro gate as written):** consider "ΔAUC lb > −0.01 in every cell and point > 0 in
the late RL cells" instead of "point ≥ 0 everywhere". I will run the gate as written unless a D-record changes it **before** the fit.

## Cost
CPU only, ~5–10 min at 2–3 threads (VM-feasible; no HEAVY.lock needed under macro §8 thresholds). No upload, no quota.

## RL translation (D-044)
- (a) Observation: own/enemy queen alive and length, with knowledge age (enemy queen is not always visible: the deployable V
  needs the H-Q8 block's *estimated* enemy-queen state, not replay truth — R4 item).
- (b) Action: none at R1 (V only); V0 later feeds the search leaf (R5) and AWR weights (R2+).
- (c) Value/reward: the terminal tiebreak chain queen → longest → total; potential-based shaping F = γV(s′) − V(s) keeps the
  optimal policy (Ng et al. 1999).
- (d) Demonstration: top-ten keepers demonstrate queen survival (~0.41–0.47 alive at RL end); we are at 0.

## Precedent
Lux AI / Hungry Geese value heads; Antioch's Φ (`tools/antioch/value_target.py`) is the baseline this extends.

## Code
`tools/hinata/v0.py` (`dry`, `smoke`, `fit --splits`, `confirm --splits --model`). Registry entry written per run
(`registry.json`: data hash, code sha, features, hyper-parameters, verdict).

---

## Result card (appended 2026-10-04 10:51Z) — verdict **FAIL** (dev gate as written)

Run `build/hinata/v0/fit-c9d60466` (registry.json there; code sha in it). Splits: **provisional** manifest
`docs/learning/splits/PROPOSED-hinata-heldout-maps.json` (Autarky, Maze, Trauma held out; written by this lane at 10:50Z
because no Phase 3 splits record exists yet — if the frozen splits differ this result is advisory, see the manifest).
Population: post-m2, in-scope, decisive, running-state rows; 5,799 training games on 14 maps (elim 6, RL 8).
Leave-one-map-out, one row per game per cell; Δ interval = 90 % game-cluster percentile bootstrap, 1,000 resamples, seed 7.
Held-out maps **not scored** (dev gate failed; `confirm` only on Chair request).

| regime | r | n | AUC V0 | AUC Φ | ΔAUC [90 %] | slope V0 | slope Φ |
|---|---|---|---|---|---|---|---|
| elim | 10 | 2274 | 0.515 | 0.544 | −0.029 [−0.044, −0.014] | 0.08 | 0.40 |
| elim | 25 | 2274 | 0.771 | 0.759 | +0.012 [+0.003, +0.021] | 0.79 | 0.91 |
| elim | 50 | 2254 | 0.872 | 0.877 | −0.006 [−0.010, −0.001] | 0.83 | 0.98 |
| elim | 100 | 2057 | 0.949 | 0.949 | +0.000 [−0.002, +0.003] | 0.88 | 1.02 |
| elim | 150 | 1666 | 0.955 | 0.959 | −0.004 [−0.007, −0.002] | 0.83 | 1.04 |
| elim | 250 | 1062 | 0.945 | 0.950 | −0.005 [−0.009, −0.000] | 0.73 | 1.04 |
| elim | 400 | 575 | 0.924 | 0.902 | +0.022 [+0.006, +0.039] | 0.72 | 1.08 |
| RL | 10 | 3525 | 0.536 | 0.551 | −0.015 [−0.026, −0.004] | 0.21 | 0.41 |
| RL | 25 | 3521 | 0.615 | 0.615 | −0.000 [−0.011, +0.010] | 0.58 | 0.73 |
| RL | 50 | 3503 | 0.657 | 0.651 | +0.006 [−0.004, +0.015] | 0.65 | 0.82 |
| RL | 100 | 3436 | 0.708 | 0.702 | +0.006 [−0.002, +0.014] | 0.73 | 0.88 |
| RL | 150 | 3387 | 0.747 | 0.715 | **+0.032 [+0.022, +0.041]** | 0.78 | 0.89 |
| RL | 250 | 3273 | 0.795 | 0.740 | **+0.056 [+0.045, +0.067]** | 0.84 | 0.91 |
| RL | 400 | 3141 | 0.881 | 0.775 | **+0.106 [+0.093, +0.118]** | 0.92 | 0.93 |

Failed criteria: ΔAUC < 0 in 6 cells (elim r10/50/150/250, RL r10/25); RL r50 AUC 0.657 < 0.66; slope outside [0.9, 1.1] in
11 of 12 cells from r25.

**Diagnosis.**
1. **Mechanism confirmed; falsifier not triggered.** The queen terms carry the late round-limit outcome: ΔAUC lower bound > 0
   at RL r150/250/400, effect +0.03/+0.06/+0.11 (predicted +0.02 to +0.06 at r150–r400; r400 exceeds it). My separate
   P(mechanism) 0.65 resolves *true*.
2. **The failures are a model-class problem.** The GBT is over-confident out of map (slopes 0.58–0.88) and loses
   0.005–0.03 AUC where the queen terms are uninformative (early, and on elimination maps): it fits map-specific
   interactions that do not transfer. This is the Alicia lesson (learned weights overfit the maps they see) at the value level.
3. **The gate is partly unattainable on post-m2.** Φ itself fails the slope criterion on RL r25–r150 (0.73–0.89) and at
   r10 everywhere. No model that ranks like Φ passes "slope in [0.9, 1.1] in every cell from r25". Ask in the Chair's order:
   data (fine), labels (fine), **gate (wrong for post-m2 RL early cells)**.
4. RL r50 0.657 vs 0.66: the 0.66 bar was set against Φ's old-map 0.63; post-m2 Φ is 0.651 on these folds. Not a queen
   problem — queens are alive in nearly every game at r50.

**Next (one change):** P-hinata-02 — the same features in a symmetric logistic model (Φ's own model class), which keeps
Φ's calibration and adds the queen terms linearly. Pre-registered before it runs.

RL translation: unchanged from the card; the measured value of the queen terms is the reward-side evidence for H-Q8.
