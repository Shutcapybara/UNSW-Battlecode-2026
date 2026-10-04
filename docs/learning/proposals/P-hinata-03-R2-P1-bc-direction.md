# P-hinata-03 — R2: P1, a behaviour-cloned direction head on encoder v1, as carthage-05's direction prior

Hinata (Learner), filed 4 Oct 2026 (time in the BOARD line that announces it), before any teacher row exists or any
outcome of this card is read. Requested by D-053 §F. One change: the model in the prior slot.

## 1. Claim, rung and mechanism

- **Rung:** R2 (macro §1). **Parent:** REG-000 `carthage-05-free-sprint`. **The one switch:** the direction prior that
  carthage-05 already adds to its move scores, `hb1_dir_lambda × log p(first step)` (`params.hpp`, `policy.hpp`
  l.1416), reads P1's probabilities instead of the HB-1 compact model's. λ stays at the parent's 1.0; the search,
  the score terms and every other rule are unchanged. Switch off = the parent bit for bit.
- **Mechanism.** The parent's prior was cloned from **one** team (Heartbreaker, 29 Sep, pre-m2, `hb1_features`). P1 is
  cloned from the **current top ten** on post-m2 ranked games and conditions on the queen block and echo counts
  that HB-1 lacks. HB-1 measured strength as steep in direction accuracy (0.73 → 7.5 % win, 0.829 → 35 %, 0.854 →
  55 % against Ares V04; `findings/2026-09-30-hb1-heartbreaker.md` §5), so a prior that matches today's strong play
  more often should move the search towards it.
- **Inputs (all frozen by Data, D-053 §A):** encoder v1 (`tools/learn/encode.py`, ENC_VERSION 1, 49 × 23 cells + 66
  scalars, int32, C++ twin `learn_encode.hpp` bit-identical on 40,002 turns; no absolute x/y, W/H or facing — no map
  identity), labels v1 (`y_first` ∈ F/R/B/L relative to the facing at turn start, move turns only), teacher list v1
  (`docs/learning/datasets/kageyama-teachers-v1.json`: 1,925 sides, 1,735 ranked post-m2 games, train split v2,
  14 maps; weights Elo × recency, half-life 2 days).
- **Deviation from the macro's R2 row, flagged:** the macro names "hb1's features plus the queen block"; D-053 §F
  names encoder v1. I follow D-053. HB-1's top features were per-candidate current-view scores, which encoder v1
  does not compute, so the head may be weaker per row. If it fails the development check below, the remedy is a
  separate card (R2b: encoder v1 + hb1 candidate features), not an edit of this one.

## 2. Expected sign and size

- **Offline (development, train split, grouped by series):** move-turn direction accuracy **0.79** (80 % range
  0.75–0.83); leave-one-map-out over the 14 training maps 0.77 (0.73–0.81); majority class (F) ≈ 0.55 (smoke:
  0.551 on 6,289 rows, one team, plumbing only). Queen turns lower, about 0.72. Per teacher team the spread will be
  wide (styles differ: Cache-me-outside is split-heavy, two top-three teams cull by command; `top-teams.md`).
- **Deploy:** small. The prior is one term of many and λ = 1 was tuned for HB-1's distribution. Expected pool Δwin
  +1 point (80 % range −2 to +4), gen ≈ 0; wall deaths slightly down; economy flat.

## 3. Falsifier and stop rule

- **Development falsifier (stops the card before any confirmation):** series-grouped development accuracy below
  0.75, or LOMO below majority + 0.10 on more than 3 of 14 maps → encoder v1 alone is not enough; file R2b.
- **Stop rule.** One development fit with the parameters in `tools/hinata/r2_bc.py` (LightGBM multiclass, 4 classes,
  63 leaves, η 0.08). One declared choice, made on series-grouped development folds only: rounds ∈ {400, 800}, and
  weighted vs unweighted by teacher weight. One learning curve (fractions of training series 0.1, 0.25, 0.5, 1.0).
  Then the model is frozen (registry `hinata-p1`) and confirmed once. No refit after the confirmation is read.

## 4. Test plan

- **Development (now allowed):** rows = `dataset.py` on teacher list v1, oracle blocks where available
  (`blocks_src`; variant games carry `cd_known = 0` and stay in), `--process-pct 25` (≈ 3 M move rows, sampled by
  process, so whole dragon histories are kept). CV: 5 folds by series hash (a series never straddles), plus LOMO.
  Reported: accuracy all / queen / non-queen, per map, per teacher team, log loss, class shares, learning curve.
- **Offline gate — two forms pre-registered now; the Chair picks before the fit:**
  - **G-macro (as written):** direction accuracy ≥ 0.83 on the confirmation population; queen-turn accuracy
    reported separately.
  - **G-parent (proposed):** P1's accuracy minus the parent prior's (HB-1 compact model) accuracy on the **same**
    confirmation rows, 5th percentile > 0 (whole-series bootstrap, 1,000 × seed 7, linear), with 0.83 printed. The
    0.83 bar was measured on one team's own held-out games with HB-1's features; a pooled ten-team target has
    irreducible disagreement between teachers, so a fixed level mostly measures the population. The paired
    comparison measures the switch. Needs Data to compute `hb1_features` on the confirmation rows (or the parent's
    prior read through the C++ chassis); if that is not feasible, G-macro binds.
- **Confirmation population (Data builds it only when the Chair releases it; one shot):** top-ten ranked post-m2
  sides by the teacher-list-v1 rule and ladder snapshot, on (a) the held-out maps Autarky, Maze and Trauma —
  **binding**, each map reported; (b) test bucket 0 on the 14 training maps — reported (opponent/time transfer).
  Unweighted move-turn accuracy binds; teacher-weighted accuracy is reported. Validation bucket 1 is not used.
- **Panel (after an offline pass, if the Chair advances it):** screen seed 1 pool + gen against REG-000, then the
  D-046 §4 gate on seeds 2–3 (D-052 §C clusters). The prior weight is a natural dial (D-044): P1 at λ ∈ {0.5, 1, 2} against the parent (HB-1 prior, λ = 1). The Chair may screen λ = 1 only.
- **Live:** the D-052 §B rollback rule after any promotion.
- No designed invalid commands.

## 5. Cost

- **Rows:** ≈ 1,925 sides × 6,500 dragon-turns × 0.25 ≈ 3 M rows × 1,200 int16 columns ≈ 7 GB in memory as float32;
  built and trained natively (Asahi's queue, `build/learn/queue/`, under `build/learn/HEAVY.lock`). Decode of teacher
  rows by `dataset.py` with the 1.2.9 wheel (oracle): Data's estimate governs.
- **Training:** 5 + 14 folds + 4 curve points + final ≈ 24 fits; ≈ 10–20 min each at 14 threads → 4–8 h native CPU.
  Can be cut to series-5 + final (≈ 2 h) if the queue is contended; LOMO then runs after.
- **Export:** LightGBM → static C++ arrays (`hb1_gbt.hpp` evaluator layout). 400 rounds × 4 classes × 63 leaves ≈
  1,600 trees ≈ 1–2 MB compiled, inside the 4 MiB zip (the parent's direction model is 12.9 MB of source). Turn-0
  load is zero (compiled in); per-turn cost ≈ 1,600 tree walks + one encoder pass (C++ twin ~0.6 M turns/s native).
  Evaluator checks the 30 M points/turn budget on the gate panels.

## 6. RL translation (D-044)

- **Observation:** encoder v1 only — the legal per-process view and own memory, identical in training and in the bot
  (C++ twin); queen knowledge from own-view history only (R0 constraint 2).
- **Action:** the first step of a move, relative to facing (F/R/B/L). Split, cull and sprint length are later heads
  (R3).
- **Value/reward:** none here; the prior shapes the search's move ordering/score, V is untouched. At R6 the same head
  is refitted on search targets (expert iteration).
- **Demonstration:** top-ten ranked post-m2 play, Elo × recency weighted, decoys excluded by using ranked games only.
  Known failure modes (macro §6.10): copying a decoy, copying the field's shared mistakes, prior shift once our own
  play changes — measured per teacher team and on our own games after deploy.

## 7. Numeric prediction

- Development accuracy ≥ 0.75 (falsifier not triggered): **0.80**.
- **P(G-macro passes) = 0.20**; P(G-parent passes) = 0.45 (conditional on Data computing the parent's prior on the
  confirmation rows).
- P(the D-046 §4 panel gate passes at λ = 1, given an offline pass) = 0.25.

---

## Council reviews

(Pending: council round 2, D-053 §F.) Round 2 reviews: Sugawara AMEND, Nishinoya AMEND, Tanaka AMEND — see the reply below.

### Author's reply to council round 2 (appended 2026-10-04 16:43 UTC, hinata). No teacher-row fit; no confirmation label read.

Reviews answered: Sugawara 15:29Z and 16:28Z (`P-hinata-03-sugawara.md`, `P-5-sugawara.md`), Nishinoya 15:58Z
(`P-5-nishinoya.md`), Tanaka 15:52Z and 16:00Z (`P-5-tanaka.md`, r/tanaka 1582bb308). The card's §§1–7 stay as filed
(timestamped before any outcome); the amendments below replace them where they conflict, subject to D-055.

1. **Feature set — accept the union** (Chair's leaning; Nishinoya, Tanaka, Sugawara agree). Binding artifact = encoder v1
   (incl. its queen block) **plus** HB-1's *relative* per-candidate direction scores computed by the bot's own C++
   extractor, so training and deployment share one implementation. The encoder-only model is fitted on identical rows
   and reported as the ablation column. Features enter only through a hashed allowlist the loader enforces
   (`tools/hinata/r2_bc.py` rev 2: unlisted columns are ignored, listed-but-absent refuses, and W, H, x, y, xn, yn,
   width, height, map*, abs_* refuse even if listed). Encoder list: `tools/hinata/r2_features_enc_v1.txt`, 1,193
   columns, sha `b109e5c0…`; the HB-1 list is added as a second file once Kageyama states the extractor's columns and
   cost. If the extractor cannot be run on the teacher rows, the encoder-only model binds and is **recorded as the
   weaker variant** (Nishinoya): a fail then routes to R2b without re-litigating.
2. **Gate — G-parent binds; 0.83 is printed.** Binding population = Tanaka's series-clean cohort: the ranked post-m2
   in-scope held-out-map games of the ten teacher teams whose series share no series with teachers_v1 (Tanaka
   15:52Z: 115 games — Autarky 35, Maze 46, Trauma 34; 85 series per Sugawara), frozen by Data/Chair from metadata
   before any fit. Whole-series bootstrap (1,000 × seed 7, linear, 5th percentile > 0), per map printed. The 497-game
   read is descriptive. Development LOMO shares series with its fits (all 14 folds) and is **descriptive only**; the
   development falsifier now reads series5 only (accuracy < 0.75 → stop, file R2b).
3. **Training rows — `blocks_src == 'oracle'`**, not `cd_known` (Sugawara 16:28Z replication: 3,925 of 40,444
   rebuild rows carry cd_known = 1; Tanaka: 236 of 11,838 in the smoke file). Implemented as the default
   (`--blocks oracle`); the dropped share is printed per map (Sugawara on dev120: 17.2 % of rows; QoS 72 %, Slithery
   68 %, Schooltime 43 %, PD 43 %). **Confirmation:** binding rows are oracle rows (the bot always sees real timers);
   all rows reported. Request to Data: publish oracle coverage of the confirmation cohort before label access.
4. **3- vs 4-class slot, defined (Sugawara, Tanaka).** The parent slot prices F/R/L (3 classes) and leaves reverse at
   hb_logp = 0. P1 is trained 4-class; at deployment the slot reads P1's F/R/L probabilities **renormalised over
   {F, R, L}** and reverse keeps the parent's convention (0). The switch therefore changes only the pricing of the
   three forward moves. Offline: G-parent compares argmax over {F, R, L} for both priors on rows whose label is F/R/L;
   B rows (0.8 % of dev120 first steps) are reported separately.
5. **Reports, no cutoffs:** full-decision flip rate of REG-000's decisions (share whose argmax changes) and mean
   entropy P1 vs HB-1 on the same decisions — report-only; Sugawara's < 1 % no-panel stop is withdrawn (Tanaka right:
   rare critical moves can decide games).
6. **Dose (Nishinoya):** if the Chair advances a panel, screen λ ∈ {0.5, 1}, not λ = 1 alone.
7. **Resume defect (Tanaka 15:52Z) fixed:** `r2_bc.py` rev 2 sha `b3ce4789e399018100a2779f29ed8432de227961bbc160eaa81ead4a9a04454d`
   writes an immutable `manifest.json` per run (rows, teachers, code, feature-list and parameter hashes, row count,
   each fold's test-row-key hash); a rerun with any difference refuses. Synthetic tests (`build/hinata/r2/synth`):
   resume with identical inputs OK; changed rows → refused (folds, n_rows, rows_sha); changed rounds → refused;
   allowlisted x_W → refused; per-map blocks drop printed.
8. **Smoke correction accepted (Tanaka):** 6,200 of the prototype's 6,289 teacher move rows had unknown timers; the
   0.649 leave-one-game-out figure was plumbing and is withdrawn as evidence of anything.

**Revised forecasts (author; the 14:48Z numbers stay on record):** development series5 ≥ 0.75 (union) **0.80**;
G-parent on the series-clean cohort **0.55**; accuracy ≥ 0.83 printed **0.25**; D-046 §4 panel gate given an offline
pass **0.25**.

RL translation — Observation: encoder v1 + HB-1 relative candidate scores (both legal, C++). Action: first step over
{F, R, L}, reverse unchanged. Value/Reward: none (behaviour cloning). Demonstration: top-ten ranked post-m2 teachers,
oracle-timer rows only.


## Chair decision

(Pending: which gate binds; release of the confirmation population.)

## Result card

(Appended by Hinata.)

### Development run pre-registration (appended 2026-10-04 17:37 UTC, hinata — before any fit on teacher rows)

D-055 §E approved the card as amended; the Chair (17:12Z) ordered the encoder-only development fit first, without
waiting for the HB-1 extractor. This section fixes the projection and the 0.75 stop's support **before fitting**
(Tanaka 16:57Z).

- **Code:** `tools/hinata/r2_bc.py` rev 3 sha `edc66ef7cb55d718a2e18272854994f8d32f44689a1466759c1ea76ef103b3c6`.
  One change from rev 2 (b3ce4789, audited): reporting only — F/R/L-conditional accuracy (rows whose teacher first
  step is F, R or L; argmax over the three probabilities renormalised; reverse rows excluded and counted), the
  majority class of the same population beside every cell, a `support` command, and a descriptive whole-series
  bootstrap (1,000 × seed 7, ratio of sums, linear 5th/95th). Training, features, folds and parameters are unchanged.
- **Rows:** `teachers_dev120.p0/p1.parquet` (sha 1a3c552c…, 30826ce9…), teachers `teachers_dev120.parquet`
  (0552ab3f…), allowlist enc v1 1,193 columns (b109e5c0…), `blocks_src == oracle`, move turns only.
- **Support (`build/hinata/r2/dev120-enc-s5/support.json`):** 189,630 move rows (39,011 of 228,641 dropped as non-oracle);
  **188,250 F/R/L rows** + 1,380 reverse rows; **97 games, 49 series, 10 teacher teams, 14 maps** (no Autarky, Maze or
  Trauma rows); 5,315 queen F/R/L rows. series5 folds (F/R/L rows / games / series): f0 45,096/24/11, f1 39,308/20/11,
  f2 35,123/23/8, f3 37,233/17/11, f4 31,490/13/8.
- **Frozen stop:** pooled out-of-fold series5 F/R/L-conditional accuracy of the encoder-only model **< 0.75 → stop P1
  on this feature set and file R2b**; ≥ 0.75 → continue to the union model and the G-parent gate. The bootstrap
  interval, per-map, per-team, queen/non-queen and four-class figures are descriptive and do not bind. The union model
  (HB-1 columns) gets its own support line before its fit. G-parent (P1 minus HB-1 prior) cannot be computed on these
  rows until the extractor runs on them; it is not computed here.
- **Author forecast (unchanged):** series5 ≥ 0.75, 0.80 (stated for the union; for encoder-only, 0.75).
