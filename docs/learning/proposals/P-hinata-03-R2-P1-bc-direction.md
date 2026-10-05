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

### Development result — encoder-only, series5 (appended 2026-10-04 18:21 UTC, hinata)

**Frozen stop triggered: F/R/L-conditional accuracy 0.7142 < 0.75** (pooled out-of-fold, 188,250 F/R/L rows, 97 games,
49 series, 10 teachers, 14 training maps; whole-series bootstrap 5th/95th [0.7057, 0.7238], 1,000 × seed 7). Every
fold is below 0.75: f0 0.719, f1 0.731, f2 0.698, f3 0.711, f4 0.708. Run `build/hinata/r2/dev120-enc-s5` (manifest
sha `6f222de6…`, code rev 3 `edc66ef7…`, rows/teachers/allowlist as in the pre-registration; fitted in the cloud
container, 1 core, 2,214 s; 5 models ≈ 11.5 MB each as LightGBM text).

| cut | rows | P1 acc | majority (class) |
|---|---|---|---|
| F/R/L, all | 188,250 | **0.714** | 0.425 (F) |
| F/R/L, queen | 5,315 | 0.678 | 0.392 (F) |
| F/R/L, non-queen | 182,935 | 0.715 | 0.425 (F) |
| four-class, all (incl. 1,380 reverse) | 189,630 | 0.712 | 0.421 |

Per teacher (F/R/L rows, acc / majority): 264 28,922 0.696/0.439; 91 27,549 0.676/0.386; 952 21,531 0.724/0.379;
55 19,625 0.740/0.466; 507 18,881 0.696/0.434; 842 17,893 0.768/0.444; 306 17,329 0.713/0.446; 19 16,573 0.749/0.479;
213 13,782 0.694/0.385; 566 6,165 0.711/0.345. Per map: range 0.642 (Prisoners Dilemma, 729 rows) to 0.782 (Devil,
7,211); Around UNSW 0.726 (37,140), Islands 0.695 (34,387), Australia 0.687 (33,438), Portals 0.765 (14,543),
Schooltime 0.709 (13,492). Log loss (4-class) 0.624. Per-class recall: F 0.83, R 0.63, L 0.63. Flat over the game
(0.714 / 0.716 / 0.713 / 0.714 for rounds ≤25 / 26–100 / 101–250 / >250).

Descriptive only (post hoc, not a gate): rows where the renormalised max probability ≥ 0.7 are 50.7 % of rows at
0.869 accuracy; ≥ 0.9, 21.2 % at 0.982 — the model is well ranked by its own confidence.

**Consequence under the frozen rule:** P1 on encoder v1 alone stops; it is recorded as the weaker variant. The union
model (encoder + HB-1 relative candidate scores from the bot's C++ extractor) was always the binding artifact and is
not yet fitted; it gets its own support line before its fit, on the same rows and folds, once Kageyama's extractor
columns exist. If the union also falls under 0.75, R2b is filed. G-parent (P1 − HB-1 prior) is not computable until
the extractor runs on these rows.

RL translation — Observation: encoder v1 alone recovers top-ten teachers' first step 71 % of the time (vs 42 %
majority), with confident decisions near-deterministic; the missing ~29 % is mostly R/L choice, which needs the
per-candidate consequences the HB-1 extractor computes. Action: first step over {F, R, L}. Value/Reward: none.
Demonstration: top-ten ranked post-m2 teachers, oracle rows.

### Learning curve — pre-registration (appended 2026-10-04 18:37 UTC, hinata; before any fit at frac < 1)

Asked by the Chair (BOARD 18:32Z): does encoder-only P1 gain from more rows or not? Descriptive, no gate, no tuning
of encoder-only (the 0.75 stop already bound it as the weaker variant).

- **Code:** `r2_bc.py` rev 4 sha `a31faa5d…` — one change from rev 3: `--frac` subsamples *training* series inside each
  fold (nested hash `frac/<series>` < frac × 1000); test folds are identical to the frac 1.0 run (fold test-row hashes
  must equal manifest `6f222de6…`; a mismatch voids the curve). Rows, teachers, allowlist, params, 400 rounds unchanged.
- **Points:** frac 0.10, 0.25, 0.50 (new runs `build/hinata/r2/lc-f10|f25|f50`) plus the existing 1.0 run
  (0.7142). Each scored pooled out-of-fold on the same 188,250 F/R/L rows; train rows/series per fold printed.
- **Reading rule (frozen):** slope per doubling of training series s = (acc(1.0) − acc(0.5)).
  s ≥ 0.010 → rows are a live lever (the 1,925-side teacher rows, ~16× dev120, are worth building for P1 even without
  new features); s < 0.005 → saturated on encoder v1, features (HB-1 consequences) are the lever; between → mixed.
  Extrapolation to 0.75 at constant per-doubling slope printed, labelled as extrapolation.
- **Author forecast:** 0.10 → 0.66, 0.25 → 0.685, 0.50 → 0.70; P(s ≥ 0.010) = 0.40, P(s < 0.005) = 0.30.
- **Caveat:** at 0.10 each fold trains on ~4 series (~10 games), so that point is noisy; the rule reads only 0.5→1.0.

### Learning curve — result (appended 2026-10-04 19:25 UTC, hinata). Descriptive; no gate; no tuning.

Runs `build/hinata/r2/lc-f10|lc-f25|lc-f50` (code rev 4 `a31faa5d…`; manifests 8d537bcd… / 67a4e8f9… / aaa2d607…), cloud
container, 533 s / 784 s / 1,233 s. **Fold test-row hashes equal the 1.0 manifest (6f222de6…) — same 188,250 F/R/L
rows, row-aligned.** Population: dev120 oracle move rows, 14 training maps, post-m2, top-ten teachers; whole-series
bootstrap 1,000 × seed 7, linear 5th/95th.

| frac | train series / fold (mean) | train rows / fold (mean) | F/R/L acc [5th, 95th] | queen F/R/L | log loss (4-class) |
|---|---|---|---|---|---|
| 0.10 | 6.4 | 27,918 | 0.676 [0.667, 0.686] | 0.644 | 0.730 |
| 0.25 | 12.8 | 43,038 | 0.684 [0.674, 0.695] | 0.643 | 0.691 |
| 0.50 | 22.4 | 79,784 | 0.703 [0.694, 0.713] | 0.658 | 0.648 |
| 1.00 | 39.2 | ~151,700 | 0.714 [0.706, 0.724] | 0.678 | 0.624 |

- **Frozen rule: s = acc(1.0) − acc(0.5) = +0.0114, paired whole-series bootstrap [+0.0090, +0.0142]** (43 of 49
  series gain) → **s ≥ 0.010: rows are a live lever** (point estimate; the 5th percentile, 0.009, sits just under the
  threshold, so "live but marginal" is the honest reading). 0.25→0.5: +0.0186 [+0.0165, +0.0209].
- Note the 1.0 − 0.5 step is 1.75× in series (0.81 doublings), so per doubling it is ≈ +0.014.
- **Extrapolation (labelled as such):** log2-linear fit over the four points, +0.0153 per doubling of training series;
  0.75 is reached at ≈ 205 training series (≈ 5× dev120's 39). The full teacher rows (~16× dev120) would extrapolate
  to ≈ 0.77 on encoder v1 alone if the slope holds — it need not (the 0.10→0.25 step was only +0.008, so the curve
  is not cleanly log-linear, and more series of the same ten teachers are not independent draws).
- Author forecast scored: 0.10 0.66 (obs 0.676), 0.25 0.685 (0.684), 0.50 0.70 (0.703); P(s ≥ 0.010) = 0.40 → occurred.
- **Consequence:** both levers are open. The union model (HB-1 `hb_pF/R/L`, Kageyama 18:50Z) stays the binding P1
  artifact on dev120; the full teacher rows Kageyama is building (D-056 order 3) are now worth fitting for P1 too,
  as a separate run with its own support line, not as tuning of the stopped encoder-only variant.

RL translation — Observation: encoder v1 is not saturated at ~150k rows; demonstration volume still buys accuracy
(~+0.015 per doubling). Action: first step F/R/L. Value/reward: none. Demonstration: more top-ten oracle rows are a
first-class input for BC, alongside the HB-1 consequence features.

### D-057 §C / D-058 §C battery — protocol as implemented (appended 2026-10-04 19:42 UTC, hinata; before any battery arm's outcome is read)

Tool: `tools/hinata/r2_battery.py` (new; imports r2_bc.py rev 4 a31faa5d… for load/folds/frl/series_boot, so the rows,
oracle filter, held-out refusals, series5 folds and F/R/L metric are those of A3's 0.714 run). Code sha 8fdddd38ceb5….
Smoke-tested on 12 dev series with synthetic hb columns (plumbing only, numbers discarded).

1. **Correction to the A3 baseline.** D-057 §C says pooled arms are **unweighted**; my 0.714 run used teacher weights
   (Elo × recency). A3 is therefore refitted unweighted at 400 and 800 rounds (running now, cloud, same 189,630 oracle
   rows; `--expect-folds dev120-enc-s5/manifest.json` passed = identical fold test rows). The weighted 0.714 stays as
   recorded; the battery table uses the unweighted A3.
2. **Sizes.** One fit at 800 rounds per arm and fold; 400 is the same booster's first 400 trees (identical to a
   400-round fit: trees are sequential, the bagging RNG advances per iteration). Model bytes per size = booster text
   truncated at that size, mean per fold.
3. **Arms implemented:** A0 (argmax hb_pF/R/L, no fit), A1 (HB-1 vector, prefix `hb_f_`), A2 (A1 per teacher team per
   fold), A3, A4 (ENC + hb_p\*), A5 (ENC + HB-1 vector + hb_p\*), A6 (A4 on the three highest-rated teachers: lowest
   crank, then highest elo in teachers_v1; trained and scored on those teachers' rows), A7 (A4 + teacher one-hot;
   scored with own identity and with identity fixed to the top-rated team = deploy form). **Not implemented:** A8
   needs Data's left–right column map of encoder v1 (request to Kageyama); A9 needs labels for split/cull/sprint
   heads on the same rows (y_kind ≠ 0; scoped after A0–A7).
4. **Sugawara's mechanism notes (19:30Z) adopted:** (1) all arms train and score on `blocks_src = oracle` rows (already
   the filter; HB-1 columns refused if any row lacks them); on the full rows the support line prints the oracle share
   per teacher and per map, and if < 1 the selected arm is also scored oracle-only. (2) If the selected arm lands in
   [0.750, 0.756], `table` prints the runner-up and a leave-one-fold-out selection (descriptive; the frozen-cohort
   confirmation binds). (3) A2 measures pooling cost; D-058 makes A2/A6/A7 a deploy-candidate type judged on its target
   teachers' rows. (4) The 0.77 extrapolation is an upper sketch; agreed.
5. **Selection code = the Chair's text:** pooled {A1, A3, A4, A5} × {400, 800}; leader by F/R/L fold accuracy; among
   arms whose whole-series interval overlaps the leader's (p95 ≥ leader p05), the smallest model; passes iff paired
   whole-series bootstrap of (arm − A0) accuracy has 5th pct > 0 and acc ≥ 0.75; else R2b. Bootstrap 1,000 × seed 7.
6. **Blocked on Kageyama:** hb_pF/R/L and HB-1's feature vector per dev120 oracle row (join key game, side, dragon,
   round, turn). A0, A1, A2, A4–A7 run within ~5 h of cloud CPU once it lands (≈ 75 min per 800-round arm).

### 1b. Precedent (appended 2026-10-04 19:42 UTC, D-058)

- **Behaviour cloning from top players as the first policy:** AlphaStar (supervised from human replays before league
  RL), Hungry Geese and Lux AI S1/S2 Kaggle top teams (imitation of top leaderboard agents, then RL or search),
  Heartbreaker's own HB-1 recipe on one team (our in-house precedent). Close: discrete per-unit actions, replays of
  top agents, partial observation (Hungry Geese). Departure: ten teachers with differing styles (Lux S1 lesson: one
  strong teacher can beat a pooled mix — tested by A2/A6/A7), a small per-turn compute budget, and the head is a prior
  inside a hand search bot, not the whole policy. Sugawara's D-058 §B verification of the precedent list binds over
  this paragraph.

### D-059 §B arm A10 (small CNN) — configuration fixed before any A10 fit on dev rows (appended 2026-10-04 19:50 UTC, hinata)

Tool `tools/hinata/r2_cnn.py` (new; imports r2_bc rev 4 and r2_battery). Input: encoder v1 window planes inferred from
column names — x_f{a}r{b}_{ch}, a = forward offset −3..3, b = lateral offset −3..3, 23 channels → [23, 7, 7], facing-relative
(no absolute position, no map identity); the other 66 allowlisted columns as scalars (z-scored on the training fold).
Kageyama: please confirm the layout (D-059 §B). Net: conv3×3 23→32, ReLU, conv3×3 32→32, ReLU, flatten ++ scalars → FC 64,
ReLU → FC 4; Adam 1e-3, batch 512, **4 epochs**, unweighted, seed 7. 120,804 parameters = 118 KiB at 8-bit weights;
≈ 0.88 M multiply-accumulates per inference (324,576 + 451,584 + 104,576 + 256) (points per turn: Evaluator deploy probe, not estimated by me). One config,
no tuning; pooled for the D-057 §C selection (r2_battery POOLED now includes A10). Smoke on 12 series (1 epoch) is
plumbing only. Also noted: in this facing-relative layout A8's mirror is a flip of the lateral axis plus swapping the
_R/_L channels — Kageyama to confirm before A8 is built.

### Battery arms A3 (unweighted) and A10 (CNN) — development results (appended 2026-10-04 20:54 UTC, hinata). Descriptive; no selection (D-060 §E); no tuning.

Same 189,630 dev120 oracle move rows (188,250 F/R/L), 49 series, 10 teachers, 14 training maps, post-m2; fold test-row hashes
= dev120-enc-s5 manifest (checked by --expect-folds). F/R/L-conditional accuracy; whole-series bootstrap 1,000 × seed 7, linear
5th/95th; paired = whole-series bootstrap of the accuracy difference on identical rows.

| arm | F/R/L acc [5th, 95th] | queen | non-queen | per teacher (min–max) | model size |
|---|---|---|---|---|---|
| A3-400 unweighted | **0.7145** [0.7061, 0.7239] | 0.6847 | 0.7153 | 0.676–0.769 | 11.5 MB LightGBM text / fold |
| A3-800 unweighted | 0.7114 [0.7034, 0.7200] | 0.6717 | 0.7125 | 0.674–0.765 | 23.0 MB |
| A10-e4 (CNN) | 0.6727 [0.6641, 0.6815] | 0.6542 | 0.6732 | 0.625–0.713 | 120,804 params (118 KiB int8), 0.88 M MAC |
| (A3 weighted, REG-004) | 0.7142 [0.7057, 0.7238] | | | | |

- Paired: A3-800 − A3-400 = −0.0031 [−0.0044, −0.0019] (800 rounds overfits slightly); A3-400 − A10 = **+0.0418 [+0.0379, +0.0463]**, 49/49 series bootstrap.
- Weighting is immaterial for A3 (0.7145 unweighted vs 0.7142 weighted).
- A10's training loss was still falling at epoch 4 (0.65); the config was fixed before the fit and is not tuned here. The gap
  is large enough that "a small CNN matches boosted trees on the same encoder columns" is not supported at this row count (both arms see the same 1,193 encoder columns).
- Code: r2_battery.py fit sha 8fdddd38… (A3-u run), r2_cnn.py 5e8d6f46… (A10-u run); the current tools (8a29e479… /
  e237fb76…) only add validation and manifest binding, fits unchanged. Registry: build/hinata/r2/battery/{A3-u,A10-u}/registry.json
  (registry sha 8807488c… / 3e23db4a…); A3 models as split tgz + models.sha256, A10 weights .pt.

### D-063 §C arm A10b (early-stopped CNN) and its learning curve — configuration fixed before any A10b fit (appended 2026-10-04 21:37 UTC, hinata)

Declared by the Chair (D-063 §C); this section only fixes the implementation details the ruling leaves open. Tool
`tools/hinata/r2_cnn_b.py` (new file; r2_cnn.py e237fb76… untouched). Same rows (teachers_dev120.p0/p1, sha 1a3c552c… /
30826ce9…), same allowlist b109e5c0…, same series5 folds (test-row hashes must equal the A10-u manifest), same net, optimiser,
batch, seed and scoring as A10.

- **Inner split:** inside each fold, training series with sha256('inner/<series>') mod 1000 < 200 form the inner validation set
  (≈ 20 % of training series, whole series; at least one series is forced if the hash picks none). The net trains on the rest.
- **Stopping:** after each epoch, 4-class cross-entropy on the inner validation rows; keep the weights of the best epoch; stop
  after 3 epochs without improvement or at 40 epochs. Test rows are predicted with the best-epoch weights. **No refit** on the
  inner validation series (so A10b trains on ≈ 80 % of the series A10 saw — stated, not corrected).
- **Learning curve (D-062 §C "A10's learning curve 0.25 / 0.5 / 1.0"):** run with the A10b protocol, not 4 fixed epochs,
  because A10 at 4 epochs had not converged and a curve of an unconverged net reads training length, not data. Training
  series subsampled by sha256('frac/<series>') < frac × 1000, exactly as r2_bc rev 4 (same series as lc-f25/lc-f50); test folds
  unchanged. Points 0.25, 0.50; 1.0 = A10b itself. Same reading rule as the tree curve: s = acc(1.0) − acc(0.5).
- **Report:** accuracy, bootstrap, queen/non-queen, per teacher, best epoch per fold, epochs run, paired A10b − A10 and
  A3-400 − A10b on identical rows. Pooled; the selector stays held (D-063 §C) — no selection claim from this run.
- **Author forecast (before the fit):** A10b = 0.695 (80 % interval 0.680–0.712); P(A10b − A10 ≥ +0.010) = 0.65;
  P(A10b ≥ A3-400) = 0.10; mean best epoch 8–15. Curve: 0.25 → 0.665, 0.50 → 0.682; P(s_CNN > s_trees = 0.0114) = 0.55
  (networks usually gain more from rows than trees in this range).
- **Bearing:** if A3-400 − A10b stays ≥ +0.02 with its 5th percentile > 0, trees win at dev120 scale for a converged net too,
  and P-7 runs as distil-from-trees (D-063 §D). If A10b closes to within 0.01, the network is a live P-7 actor without distillation.

### Arm A10b and its learning curve — development results (appended 2026-10-04 21:55 UTC, hinata). Descriptive; no selection (D-063 §C); no tuning.

Runs `build/hinata/r2/battery/A10b-u | A10b-f50 | A10b-f25` (tool r2_cnn_b.py ba151375…, imports r2_bc a31faa5d… and
r2_battery 8a29e479…; manifests 56ee8b12… / 7e1479ca… / 26391dba…; registries 6164e241… / cbc32215… / 1a72cd12…; all 45 files
sha-verified on the Mac, `A10b.sha256`). Cloud container, 1 core: 482 s / 242 s / 129 s. Fold test-row hashes equal the
A10-u manifest (--expect-folds), and row keys equal A10-u's in order. Population: dev120 oracle move rows, 188,250 F/R/L of
189,630, 49 series, 10 teachers, 14 training maps, post-m2. F/R/L-conditional accuracy; whole-series bootstrap 1,000 × seed 7,
linear 5th/95th; paired = whole-series bootstrap of the difference on identical rows.

| run | fit series / fold (mean) | fit rows / fold | best epoch (0-based) per fold | F/R/L acc [5th, 95th] | queen |
|---|---|---|---|---|---|
| A10b-f25 | 9.6 | 35,803 | 7, 6, 6, 6, 9 | 0.6419 [0.6300, 0.6528] | 0.633 |
| A10b-f50 | 17.6 | 64,557 | 5, 10, 8, 8, 5 | 0.6582 [0.6475, 0.6682] | 0.613 |
| **A10b** | 32.0 (+ 7.2 inner) | 124,972 | 7, 7, 10, 6, 6 | **0.6785 [0.6694, 0.6875]** | 0.652 |
| (A10-e4, 4 fixed epochs) | 39.2 | ~151,700 | — | 0.6727 [0.6641, 0.6815] | 0.654 |
| (A3-400 trees) | 39.2 | ~151,700 | — | 0.7145 [0.7061, 0.7239] | 0.685 |

- **Paired:** A10b − A10 = **+0.0058 [+0.0030, +0.0081]**; A3-400 − A10b = **+0.0360 [+0.0326, +0.0403]** (49 series).
  Early stopping chose 7–11 epochs; inner loss bottoms at ≈ 0.652–0.656 and then rises, so A10 at 4 epochs was close to
  converged in accuracy terms (its still-falling loss was training loss). A10b per teacher 0.639–0.716; per fold 0.662–0.689.
- **CNN curve: s_CNN = acc(1.0) − acc(0.5) = +0.0203 [+0.0174, +0.0236]**; 0.25 → 0.5 +0.0163 [+0.0129, +0.0196]. Trees'
  s = +0.0114 [+0.0090, +0.0142] (lc-f50 → 1.0). The intervals do not overlap: the network gains about twice as much per
  step of rows. Per doubling of fit series: CNN ≈ +0.024 (0.5 → 1.0 is 1.82×), trees ≈ +0.014–0.015.
- **Extrapolation (labelled as such; two log-linear lines, not a model):** the gap (+0.036) closes by ≈ 0.009 per doubling,
  so parity would need ≈ 4 doublings of series, ≈ 16× dev120 — about the size of the full teacher rows Kageyama is building.
  Part of the gap is A10b's 20 % inner hold-out (32 vs 39 series ≈ −0.007 at the CNN slope).
- **Forecasts scored:** A10b 0.695 (80 % 0.680–0.712) → 0.6785, below the interval; P(A10b − A10 ≥ +0.010) = 0.65 → did not
  occur; P(A10b ≥ A3-400) = 0.10 → did not occur; best epoch 8–15 (1-based) → 7–11, mostly inside; curve 0.665 / 0.682 →
  0.642 / 0.658 (too high by ≈ 0.024 at both); P(s_CNN > s_trees) = 0.55 → occurred.
- **Bearing (pre-registered rule):** A3-400 − A10b ≥ +0.02 with 5th percentile > 0 → **trees win at dev120 scale for a
  converged small CNN too**; if trees are selected, P-7 runs as distil-from-trees (D-063 §D). Beside it, the steeper CNN curve
  means the full teacher rows are the test that could reverse this; a CNN refit there is a new card, not tuning of A10b.
- Registry rows proposed: hinata-r2-bat-A10b (6164e241…), hinata-r2-lc-A10b-f50 (cbc32215…), hinata-r2-lc-A10b-f25 (1a72cd12…).

RL translation — Observation: same 1,193 encoder columns; the window CNN extracts less of the teachers' direction choice than
trees at 125–150k rows, but its error falls faster with rows. Action: first step F/R/L. Value/reward: none. Demonstration:
demonstration volume matters more for a network actor than for trees, so P-7's network actor needs either the full teacher rows
or distillation from trees (which can also label unlimited self-generated states, DAgger-style).

### Author's reply to Tanaka's repair audit (21:25Z) — r2_battery.py rev 6 (appended 2026-10-04 21:55 UTC, hinata)

All four blockers and the hardening note are implemented in `tools/hinata/r2_battery.py` rev 6 (sha 3f56b4b2…; 8a29e479… kept
as `tools/hinata/archive/r2_battery_8a29e479.py`). Fit paths are unchanged; only `a0` (records teams_by_rating) and `table`
change. (1) A6 must be exactly A0's rows of A0's top three teams, and its declared teams must equal them. (2) A7/A7fix need the
full A0 support and the declared top team must equal A0's; team, series_key, map and x_is_queen must equal A0's on every key,
and bootstrap clusters and targets are taken from A0. (3) A2's allowed exclusions are derived from A0 alone (cells team × fold
with no A0 row of that team outside the fold); any other missing row refuses; the excluded cells and counts are printed.
(4) Fixed teacher-specific inventory (A2/A6/A7fix × 400/800): missing arms print INCOMPLETE and block goes_forward unless the
Chair waives them (--waive-ts, recorded). Probabilities must be nonnegative. Synthetic check `tools/hinata/r2_battery_rev6_synth.py`
(invented data, 100 rows, 4 teams, 10 series; no real output read): your cases 1, 2 (partial and altered series_key), 3 and the
[2, −1, 0, 0] vector refuse; a structurally unsupported A2 cell passes and one extra missing row refuses; A7fix alone and other
partial inventories give goes_forward = false; the complete inventory gives true. Requesting a pass line on 3f56b4b2….
Note: A0 must be (re)run with rev 6 so its registry carries teams_by_rating; the table refuses otherwise.

### Author's reply to Tanaka's round-11 audit (22:25Z) and D-064 §C — r2_battery.py rev 7 (appended 2026-10-04 22:44 UTC, hinata). No battery table read on real rows.

- **rev 7 `af1c87e0d4de7dc2b1cc16783b037edbad184420ea4211b88d7ffec267428207`** (rev 6 3f56b4b2… archived as `tools/hinata/archive/r2_battery_3f56b4b2.py`). The fit and a0 paths are unchanged; only identities and the selector change.
  1. **Explicit candidate identities** (Tanaka): `POOLED_NAMES` = A1/A3/A4/A5 × {400, 800}, `A10-e4`, `A10b` (full data, D-063 §C). `DESCRIPTIVE` = `A10b-f25`, `A10b-f50`, `A7-*`, `A7fix-*`. Any arm name outside the declared sets refuses (no prefix classification). `A10b` is in PLANNED, so a missing full-data A10b makes the pooled selection INCOMPLETE. Each table row carries `role`.
  2. **D-064 §C:** A7fix is descriptive (printed as `descriptive_vs_A0_top_team`), never a teacher-specific candidate; the teacher-specific inventory is A2 and A6. An A2 team candidate is eligible only with ≥ 10 frozen-cohort series, from a Data-supplied `--cohort-series {team: series}` file (counts only, no labels; Hinata does not open the cohort). Without the file and with A2 present, the teacher-specific path is INCOMPLETE.
- **Synthetic check** `tools/hinata/r2_battery_rev7_synth.py` c877f6fc… (invented data; reuses only the rev 6 synth's helpers): (a) complete old inventory at .80 + A10b at 1.00 → selects A10b, inventory complete; (b) A10b absent → pooled_missing [A10b], no claim; (c) A10b-f25 at 1.00 without A10b → role descriptive, not selected, INCOMPLETE; (d) `A10b-f75` and (e) `A3-200` → refused; (f) A2 best team with 6 cohort series → an eligible team is chosen instead; (g) the same team with 12 → chosen; (h) no counts → goes_forward false, counts listed missing; (i) A7/A7fix only → no teacher-specific candidate. The rev 6 probe cases 1–3, 5, 6, 6b were re-run in this unit on the intermediate draft 224c667a… (identity sets only, before the D-064 §C edits) with outcomes identical to rev 6; case 4b's expectation changes by D-064 §C (A7fix no longer counts).
- **A0 run (rev 6/7 a0 path, records teams_by_rating):** `build/hinata/r2/battery/A0-u`, 0.6977 [0.6891, 0.7069] on 188,250 F/R/L oracle moves (dev120, 49 series, 10 teachers, 14 training maps, post-m2; whole-series bootstrap 1,000 × seed 7, linear 5th/95th), queen turns 0.6754. Equals Kageyama's and Tanaka's .69766. HB-1 export manifest e38d0667…, 118/118 shard hashes re-verified after transfer.
- **Requests:** Tanaka — pass line on rev 7 af1c87e0…. Kageyama — `--cohort-series` JSON: frozen-cohort series count per teacher team (all ten), no labels.

### Full-row refit (D-064 §C) — configuration fixed before any full-row fit (appended 2026-10-04 22:50 UTC, hinata). No full-row outcome read.

- **Claim / rung.** R2 P1: the development table's ordering (trees > CNN by +0.036 at dev120 scale) is measured again on the full teacher rows before the selection is read as final (D-064 §C; D-057 §C order select → refit → confirm unchanged). Descriptive beside the development table; it does not re-run the selection.
- **Rows.** `build/learn/kageyama/teachers_v1/` (Kageyama's native build, `_manifest.json` read only for totals): 1,709 games, 506 series, 10 teachers, 14 training maps, 0 frozen-cohort games or series; oracle F/R/L moves 2,753,685 (14.6 × dev120's 188,250). Train split only; held-out maps refused; oracle rows only (Sugawara point 1); support.json prints the oracle share per map (Schooltime .65, Devil .63, Queen of Spades .48, Slithery Fight .54, Prisoners Dilemma .39, the other nine 1.0 — from Data's manifest) and the F/R/L rows per teacher.
- **Arms.** (i) **the best development tree arm**: among A1/A3/A4/A5 × {400, 800}, the one rev 7's pooled rule ranks first among tree arms once A1, A4 and A5 are complete (highest dev F/R/L accuracy; among tree arms whose interval overlaps it, the smallest); (ii) **A10b** (`A10b-full`), r2_cnn_b's network, inner split (20 % of training series), patience 3, ≤ 40 epochs, seed 7, unchanged.
- **Tool.** `tools/hinata/r2_full.py` (new). Same r2_bc.PARAMS except `num_threads` (= ASAHI_MAX_WORKERS on the Mac queue; thread count can change the last digits of a LightGBM fit — declared, not a parameter change). Loading per shard with column projection; encoder kept int16; LightGBM Dataset from a `lightgbm.Sequence` (bins from LightGBM's default 200,000-row sample, as for the numpy path); CNN windows cast to float32 per mini-batch. Folds: series5 (`sha256('hinata-r2/<series>') % 5`) over the full-row series. Metric: F/R/L accuracy, whole-series bootstrap 1,000 × seed 7, linear 5th/95th; paired trees − A10b-full on identical rows; per map, per teacher, queen turns. **Bridge line** (descriptive): out-of-fold accuracy on the dev120 games vs the rest.
- **Parity check before the Mac run:** on the dev120 rows, r2_full `trees --arm A3 --sizes 10` must reproduce r2_battery `fit --arm A3 --sizes 10` (same fold hashes; predictions equal to 1e-6 at num_threads 3). Result appended below before any full-row fit.
- **Expected sign / size (log-linear extrapolation of the dev curves, labelled as such; Sugawara: curves usually bend):** trees 0.7145 + 0.0114 × log2(14.6) ≈ 0.759; A10b 0.6785 + 0.0203 × 3.87 ≈ 0.757. **P(best tree arm ≥ 0.75 on full rows) = 0.40; P(A10b-full − trees > 0, paired 5th pct > 0) = 0.15; P(A10b-full − trees within ±0.01) = 0.30.**
- **Falsifier of the dev ordering:** A10b-full ≥ trees with the paired 5th percentile > 0. If so, the Chair decides whether the pooled selection is re-read on full rows; Hinata does not reselect.
- **Cost.** Mac learn queue, heavy, one job per arm. Memory: trees A3/A4 ≈ 6.6 GB int16 + binned dataset ≈ 3 GB; A5 adds ≈ 3 GB float32; CNN ≈ 6.6 GB + float32 scalars. Time (from 1-core dev costs × 14.6 rows ÷ threads): trees ≈ 1–2 h at 800 rounds, CNN ≈ 1–2 h. **Needs:** tools/hinata/r2_full.py, r2_battery.py rev 7 and r2_cnn.py committed on main (queue rule).
- **Stop rule.** One fit per arm; no retuning; no re-run of a completed fold; results appended as one section with registry rows.
- **RL translation.** Demonstration volume: whether a network actor (needed for P-7 self-play) can match trees once fed the full demonstrations decides between distil-from-trees and direct network BC as P-7's starting actor.

#### Full-row refit — tool amendment and parity result (appended 2026-10-04 23:11 UTC, hinata). Still no full-row fit.

- **Amendment (before any full-row fit):** the `lightgbm.Sequence` loader named above is dropped. On dev120 fold f0 it pre-filters 45 of 1,193 rare encoder features differently from the numpy path (e.g. `x_f1r0_enemy_queen`: 0 bins vs 2), which changes feature_fraction's column draws and so the model (10-round test: 0.666 vs 0.6638). r2_full.py now materialises each training fold as float32 and hands it to LightGBM exactly as r2_battery.fit does. Memory, revised: A3/A4 ≈ 6.6 GB int16 store + ≈ 10.5 GB float32 training copy (≈ 18 GB peak); A5 ≈ 23 GB peak. **Asahi: please confirm the Mac's RAM before these jobs are queued.**
- **Parity (dev120, A3, --sizes 10, num_threads 3), r2_full.py 6be9dd8d9306a0af7920212516612bdc46970dc4079783fa31d74470f43c823e vs r2_battery fit:** identical fold hashes, identical row order, max |Δp| = 0.0 on 189,630 rows; F/R/L accuracy 0.6638 both (188,250 rows). Bridge line works (all rows are dev120 games here). **CNN path parity** (`cnn`, threads 1, dev120) vs A10b-u (6164e241…, r2_cnn_b ba151375…): identical fold hashes and row order, best epochs 7/7/10/6/6 as before, max |Δp| = 0.0 on 189,630 rows, 0.6785 [0.6694, 0.6875] — the full-row CNN is A10b with only the loader changed.

### Battery arms A0 and A1 — development results (appended 2026-10-04 23:31 UTC, hinata). Descriptive; no selection (inventory incomplete: A4, A5, A2, A6 pending); no tuning.

Population: dev120 oracle F/R/L moves, 188,250 rows of 189,630 oracle moves, 49 series, 10 teachers, 14 training maps, post-m2; series5 folds (fold hashes equal dev120-enc-s5, checked by --expect-folds); whole-series bootstrap 1,000 × seed 7, linear 5th/95th; paired differences on identical rows (row keys equal A0's).

| Arm | Inputs | F/R/L acc [5th, 95th] | queen turns | vs A0 (paired) | bytes/fold |
|---|---|---|---|---|---|
| A0 | parent prior hb_pF/R/L argmax | 0.6977 [0.6891, 0.7069] | 0.6754 | — | 0 |
| A1-400 | HB-1's 270 features, trees | **0.7184 [0.7101, 0.7278]** | 0.6850 | +0.0207 [+0.0170, +0.0244] | 11.2 MB |
| A1-800 | same, 800 rounds | 0.7158 [0.7075, 0.7251] | 0.6741 | +0.0181 [+0.0142, +0.0219] | 22.5 MB |
| A3-400 (earlier) | encoder v1, trees | 0.7145 [0.7061, 0.7239] | 0.6717 | — | 11.5 MB |

- **A1-400 − A3-400 = +0.0039 [+0.0018, +0.0060]** (paired, 49 series): the parent's hand-built 270-feature vector, refitted on teacher moves, is slightly better than the 1,193-column encoder. 800 rounds are again worse than 400 (A3: −0.0031; A1: −0.0026).
- Registry: A0-u registry.json d6abd0d5d1056f74…, A1-u registry.json 66444789f9a8ecf3… (code r2_battery 224c667a… — fit path identical to rev 7 af1c87e0…; r2_bc a31faa5d…; HB-1 export manifest e38d0667…). Models: `build/hinata/r2/battery/A1-u/models.tgz.part_*` + models.sha256.
- RL translation: observation design — HB-1's compact, hand-engineered features carry at least as much imitation signal as the raw window encoder; A5 (both) tests whether they are complementary.

### Arm A8 (left–right mirror augmentation) — configuration fixed before any A8 fit or mirror diagnostic (appended 2026-10-05 00:04 UTC, hinata)

- **Claim / rung.** R2 P1 (D-058 §C 3, D-063 §C): adding the left–right mirror image of every *training* row (labels swapped) raises F/R/L accuracy of the base arm on unmirrored test folds. Mechanism: the game is mirror-symmetric in movement; mirroring doubles the demonstrations for rare lateral situations and removes teacher handedness that does not generalise.
- **Base arm.** The pooled tree arm the rev 7 rule selects from the complete development table (A1/A3/A4/A5 × 400/800); if a CNN were selected, A8 is not run on it without a new card. Same params, same rounds, same series5 folds; test rows never mirrored; dev120 rows only.
- **Mirror map** (`tools/hinata/r2_mirror.py`, Kageyama 21:26Z and 21:56Z): encoder window `x_f{F}r{R}_{ch}` → `x_f{F}r{−R}_{ch}` with kelp_R↔kelp_L, portal_R↔portal_L, head_fac_R↔head_fac_L; scalars x_exit_R↔x_exit_L, x_last_first_rel 1↔3, negate x_ownq_r, x_enemyq_r, x_home_r, x_mirror_xy_r, x_mirror_y_r except the sentinel 999; HB-1 `hb_f_g_{f}_{r}_*` → `hb_f_g_{f}_{−r}_*`, cR_*↔cL_*, pearl_right↔pearl_left, mem_last_rel 2↔3; hb_pR↔hb_pL; label y_first 1↔3. Kageyama's caveats stand (even-side n/2 offsets; HB-1 per-candidate symmetry untested; sonar order N,E,S,W is not mirror-symmetric).
- **Pre-checks (reported before the fit; do not gate it unless they fail):** (1) the map is an involution on every development row and every input column of the base arm (mirror(mirror(x)) = x exactly); (2) every column is either mapped or declared invariant — the invariant list is printed; (3) **symmetry diagnostic, descriptive:** the base arm's existing fold models scored on mirrored test rows (labels swapped) vs unmirrored; a large drop measures how much handedness the clone has learned.
- **Expected sign / size.** A8 − base: +0.002 to +0.006. **P(A8 − base > 0 with paired 5th pct > 0) = 0.35; P(A8 − base < 0 with paired 95th pct < 0) = 0.15.** Symmetry diagnostic: mirrored accuracy 0.005–0.02 below unmirrored.
- **Falsifier.** A8 − base ≤ 0 or its interval spans 0: augmentation does not help at this scale; A8 is reported and not carried.
- **Deployability (D-065 §C).** A8 has the base arm's size and inputs; no new export cost.
- **Cost.** One fit of the base arm on doubled training rows: ≈ 2 × base cost on the cloud core (A1 ≈ 1.5 h, A3/A4 ≈ 2.5 h), or the Mac queue.
- **Stop rule.** One fit, no retuning; results appended with registry row; D-057 §C selection may then include A8 only if the Chair rules it pooled.
- **RL translation.** Demonstration augmentation by a symmetry of the game; the same map is the data-augmentation/equivariance for P-7's network and for self-play rollouts (each rollout counts twice).

#### A8 pre-checks — results (appended 2026-10-05 00:14 UTC, hinata). No A8 fit yet (base arm not selected).

- **Tool** `tools/hinata/r2_mirror.py` 45cdb1b1870cfc5c… (check / diag / fit).
- **(1) Involution:** mirror(mirror(x)) = x exactly on all 189,630 dev120 oracle move rows × 1,466 columns (encoder 1,193 + HB-1 270 + hb_p 3) and y_first. 0 failures. **(2) Coverage:** 1,174 columns permuted, 7 value-mapped (share of rows changed: x_last_first_rel .548, hb_f_mem_last_rel .561, x_ownq_r .221, x_enemyq_r .057, x_home_r .058, x_mirror_xy_r .063, x_mirror_y_r .060), 285 declared invariant (the R = 0 column's 17 symmetric channels × 7 rows, the symmetric scalars, HB-1's non-lateral features, hb_pF) — list in `build/hinata/r2/mirror/check.json`. Labels: R 53,947 / L 54,395 → swapped exactly.
- **(3) Symmetry diagnostic, A1-400 (descriptive):** mirrored test rows 0.7175 vs unmirrored 0.7184, **mirrored − unmirrored −0.0009 [−0.0028, +0.0012]** (188,250 F/R/L rows, 49 series, paired whole-series bootstrap 1,000 × seed 7, linear 5/95). My expected drop of 0.005–0.02 is **not met**: the clone's accuracy is nearly mirror-invariant. But the argmax agrees on only **0.891** of F/R/L rows between a row and its mirror image (mean |Δp| 0.037): about one decision in nine flips under reflection. Reading: the model is not biased to one side, it is noisy across the reflection — which is the case where augmentation (and mirror test-time averaging, a separate arm needing its own card) should help.
- RL translation: equivariance — a policy that changes one decision in nine under a symmetry of the game wastes demonstrations; P-7's network should be built mirror-equivariant or trained with this augmentation.

### Battery arm A4 — development result (appended 2026-10-05 00:39 UTC, hinata). Descriptive; no selection (A5, A2, A6 pending).

Same population and conventions as §"A0 and A1" (188,250 F/R/L rows, 49 series, paired series bootstrap 1,000 × seed 7, linear 5/95; row keys equal A0's).

| Arm | Inputs | F/R/L acc [5th, 95th] | queen | vs A0 | vs A1-400 | vs A3-400 |
|---|---|---|---|---|---|---|
| A4-400 | encoder + hb_pF/R/L | **0.7205 [0.7123, 0.7297]** | 0.6739 | +0.0229 [+0.0188, +0.0268] | +0.0021 [+0.0003, +0.0042] | +0.0061 [+0.0042, +0.0079] |
| A4-800 | same, 800 rounds | 0.7178 [0.7098, 0.7271] | 0.6675 | +0.0201 [+0.0160, +0.0242] | −0.0006 [−0.0026, +0.0016] | +0.0033 [+0.0013, +0.0054] |

- A4-400 leads so far, but by D-065 §C it must carry the present prior's model (3.74 MiB compressed) as well as its own trees; A1 (0.0021 behind, interval just above 0) replaces the prior. Registry: A4-u registry.json 31b0c7b79dad4979… (code 224c667a…, fit path = rev 7). The container restarted at ≈ 00:20Z; fold f4 resumed from saved fold models (resumable by design; manifest unchanged).
- RL translation: the parent policy's own action probabilities are a useful observation for the student (policy-prior as input, as in residual/KL-regularised RL), worth ≈ +0.006 over the raw encoder.

### D-066 §C–D — inventory file (rev 8), A8b results, full-row jobs queued (appended 2026-10-05 01:04 UTC, hinata)

- **r2_battery.py rev 8 b5346f3c…** (rev 7 archived as `archive/r2_battery_af1c87e0.py`): the candidate inventory, the teacher-specific inventory, the cohort minimum and the A6/A7 input base are read from **`tools/hinata/r2_inventory.json` 838de555…** (env R2_INVENTORY overrides). No inventory file existed in rev 7, so this one code change makes later changes configuration only (D-066 §C 5). **Equivalence:** with `r2_inventory_rev7_equiv.json` (rev 7's constants), r2_battery_rev7_synth.py's nine cases print identically under rev 7 and rev 8 (diffed). New synth `r2_battery_rev8_synth.py` 30b0c27c…: A4-400 at 1.00 stays descriptive; a missing A8b entry makes the pooled selection INCOMPLETE; A6/A7 take ts_base's inputs. Inventory now: pooled A1-400/800, A3-400/800, A10-e4, A10b, A8b-A1-400, A8b-A3-400; descriptive A4-*, A5-*, A10b-f25/f50, A7-*, A7fix-*; teacher-specific A2-400/800, A6-400/800; **ts_base = A1** (A6/A7 re-based on the HB-1 vector, stated before any A6/A7 fit, D-066 §C 3).
- **A8b (mirror-averaged prediction, no refit; Chair's declaration D-066 §C 4)**, `r2_mirror.py tta` 8ba355a0…, same population and conventions as the table above (188,250 F/R/L rows, 49 series, paired series bootstrap 1,000 × seed 7, linear 5/95; row keys equal A0's):

| Arm | F/R/L acc [5th, 95th] | queen | vs its base | vs A0 |
|---|---|---|---|---|
| **A8b-A1-400** | **0.7224 [0.7144, 0.7317]** | **0.7040** | +0.0040 [+0.0029, +0.0053] vs A1-400 | +0.0248 [+0.0211, +0.0285] |
| A8b-A3-400 | 0.7190 [0.7100, 0.7288] | 0.6818 | +0.0045 [+0.0032, +0.0060] vs A3-400 | — |

  A8b-A1 − A8b-A3 = +0.0034 [+0.0013, +0.0055]; A8b-A1 − A4-400 (non-selectable) = +0.0019 [−0.0002, +0.0040]. On queen turns A8b-A1 − A1 = +0.019 [−0.004, +0.048] (20 series). Cost at play: two evaluations of the same model per decision (Kageyama to state points); zip unchanged. My 00:14Z reading (unbiased but noisy across the reflection) predicted the sign; no size was forecast for A8b.
- **r2_full.py rev 2 704805c7…** (D-066 §D ceiling 14.4 GiB): two-pass loader into preallocated int16/float32 matrices; peak RSS recorded. Parity on dev120 re-run: trees (A3, 10 rounds) max |Δp| 0.0 vs r2_battery; CNN max |Δp| 0.0 vs A10b-u. Dev-scale peak 2.0 GiB (dominated by the two 117k-row dev shards). **Full-row peak estimates:** A10b-full ≈ 9–10 GiB (int16 matrix 6.2 GiB + scalars 0.7 + standardised scalars 0.7 + metadata ≈ 1 + runtime); A1-full ≈ 7–8 GiB (float32 2.8 GiB + one float32 training copy 2.2 GiB + binned set + metadata). Both under 14.4 GiB; measured peaks are printed per fold and recorded in each registry.
- **Queued (main ea8ada4e2):** `hinata-01-a10b-full` (running since ≈ 01:06Z; 8 torch threads) then `hinata-02-a1-full` (A1, **400 rounds only** per D-066 §C 6; num_threads = ASAHI_MAX_WORKERS). Outputs `build/learn/hinata/r2full/`. A3-full (chunked route) is third only if A3 stays within 0.005 of A1 (now 0.0039) — tool not yet built.
- RL translation: averaging a policy over a game symmetry is free strength at inference (+0.004 here); for P-7 the same symmetry belongs in the network or the data, not only at test time.

### Battery arm A5 — development result (appended 2026-10-05 02:21 UTC, hinata). Descriptive (not selectable, D-066 §C 1).

| Arm | Inputs | F/R/L acc [5th, 95th] | queen | vs A8b-A1-400 (best selectable) | vs A1-400 | vs A4-400 | vs A0 |
|---|---|---|---|---|---|---|---|
| A5-400 | encoder + HB-1 vector + hb_p | **0.7267 [0.7179, 0.7361]** | 0.6674 | +0.0043 [+0.0017, +0.0067] | +0.0083 [+0.0063, +0.0103] | +0.0062 [+0.0049, +0.0073] | +0.0290 [+0.0249, +0.0330] |
| A5-800 | same, 800 rounds | 0.7259 [0.7175, 0.7350] | 0.6647 | | | | |

- Same population/conventions (188,250 F/R/L rows, 49 series, post-m2; paired series bootstrap 1,000 × seed 7, linear 5/95; keys equal A0's). Registry A5-u registry.json d82bc6f68432bac6… (code 224c667a…, fit path = rev 7/8). Container restart mid-unit; folds resumed from saved models.
- **D-066 §C 1 test:** a size-matched variant of a non-selectable arm may be filed only if it beats the best selectable arm by ≥ 0.005 with 5th pct > 0. A5-400 − A8b-A1-400 = +0.0043 < 0.005 → **no size-matched A5 is filed.** Note for the Chair (no action taken): the encoder and the HB-1 vector are complementary (A5 − A1 +0.0083, A5 − A4 +0.0062); an arm on encoder + HB-1 vector *without* hb_p would be a single model (≈ 1 MB) and so selectable, but it is a new arm and needs a ruling before any fit.
- RL translation: the two observation encodings carry partly different information; the learned policy's observation should be their union, not either alone.

### D-067 §E.2 arm T0 and D-068 §5 single-team priors — configuration fixed before any fit (appended 2026-10-05 02:25 UTC, hinata)

- **T0** (`tools/hinata/r2_t0.py` ec2ca5d8…): A1's recipe exactly (HB-1 vector, r2_bc.PARAMS, dev120 oracle rows, series5 folds = dev120-enc-s5, 400 and 800 rounds from one fit) **minus hb_f_round and the 16 hb_f_mem_* terms** (253 of 270 columns). Paired against A1-400 on identical rows. Expected cost +0.001 to +0.004 (A1's gain share in those 17 inputs is 7.2 %). **P(T0 costs ≥ 0.005, i.e. A1 − T0 ≥ 0.005) = 0.25** — the D-067 §E.3 trigger for T1 (phase models). One fit, cloud core.
- **Single-team priors** (D-068 §5): A1's recipe on **one teacher team's full rows** (teachers_v1, oracle F/R/L moves, train split), teams **213** and **91**; series5 folds over that team's series (the accepted full-row fold rule restricted to the team); 400 rounds; `r2_full.py trees --arm A1 --team <id>` (rev 3, `--team` added, one-team folds without test series skipped; parity with rev 2 on dev120 re-checked). Reported on the team's held-out folds: F/R/L accuracy with series interval, **log-loss, entropy, floor share (min F/R/L option ≤ 1e-4) and mean top-two log gap**, plus the same for A0 on the same rows. Then one deploy model per team = the fold-f0 model? — **no: a deploy file is a refit on all of the team's series at 400 rounds**, written after the CV figures (Kageyama exports, Asahi screens at λ 1). Mac learn queue, ahead of A1-full (job names sort first).
- **No forecasts of play** from me; offline forecast: each team's CV accuracy above A1-400's on that team's dev120 rows, P = 0.5 (more data of one style vs fewer rows).

### D-067 §E.1 time diagnostic and D-068 prior-shape table (appended 2026-10-05 02:30 UTC, hinata). No fit; descriptive.

Population: dev120 oracle F/R/L moves, 188,250 rows, 49 series, post-m2; out-of-fold predictions of the existing runs; paired series bootstrap 1,000 × seed 7, linear 5/95. Output `build/hinata/r2/d067/d067_time_diagnostic.json` (1532e03a…).

**Prior shape (F/R/L renormalised; floor = min option ≤ 1e-4):**

| Arm | acc | log-loss | entropy (nats) | floor share | top-2 log gap |
|---|---|---|---|---|---|
| A0 (live HB-1 prior) | 0.6977 | 0.748 | 0.425 | **0.390** | 3.37 |
| A1-400 | 0.7184 | 0.602 | 0.585 | 0.018 | 2.23 |
| A3-400 | 0.7145 | 0.606 | 0.605 | 0.089 | 2.15 |
| A4-400 | 0.7205 | 0.597 | 0.575 | 0.108 | 2.38 |
| A5-400 | 0.7267 | 0.586 | 0.560 | 0.112 | 2.45 |
| A8b-A1-400 | 0.7224 | 0.595 | 0.593 | 0.010 | 2.20 |
| A8b-A3-400 | 0.7190 | 0.600 | 0.613 | 0.072 | 2.12 |
| A10b | 0.6785 | 0.664 | 0.615 | 0.037 | 1.83 |

Reproduces Sugawara's 01:31Z floor shares (38.9 / 8.9 / 1.8 / 1.0 %). Every clone is better calibrated (log-loss 0.59–0.61 vs 0.75) and much softer than A0.

**By phase bucket (encoder x_phase) — acc A0 / A1 / A3 / A4; A1 − A0; A1 − A3:**
- 0 (2,887 rows, 44 series): .686 / .722 / .722 / .724; +.036 [+.024, +.049]; +.000 [−.012, +.013]
- 1 (23,235, 49): .692 / .715 / .717 / .721; +.023 [+.017, +.030]; −.002 [−.007, +.004]
- 2 (73,159, 48): .696 / .716 / .712 / .719; +.021 [+.016, +.026]; +.004 [+.001, +.007]
- 3 (66,760, 43): .701 / .721 / .716 / .722; +.021 [+.017, +.025]; +.005 [+.002, +.009]
- 4 (22,209, 39): .703 / .719 / .713 / .722; +.016 [+.011, +.021]; +.006 [+.002, +.011]

**By rounds since birth:** 0–5 (23,256 rows): .739 / .754 / .750 / .756, A1 − A0 +.015 [+.011, +.019]; 6–20 (41,267): .707 / .728 / .725 / .732, +.021 [+.017, +.025]; 21–100 (90,188): .688 / .711 / .707 / .713, +.024 [+.019, +.028]; > 100 (33,539): .684 / .702 / .699 / .703, +.018 [+.011, +.024].

**Empty view (H-SZ69; my operationalisation: no enemy or ally head or part, no pearl and no bed in the 7×7 window):** 4,210 rows / 35 series: .786 / .807 / .809 / .810, A1 − A0 +.022 [+.013, +.031]; non-empty 184,040: .696 / .716 / .712 / .719.

**Gain share of time and memory inputs (5 fold models, 400 iterations):** A1 (hb_f_round + 16 hb_f_mem_*): **7.2 %** (folds 6.9–7.4 %); A3 (13 encoder time/memory scalars: round, rounds left, phase, turn index, rounds since birth/split, last kind/steps/first-rel, length and unit deltas, queen ages): **5.3 %** (4.9–5.5 %).

Reading: the clones' accuracy gain over the live prior is present in every phase and every age bucket, largest at the start (+0.036) and smallest late (+0.016); A1's advantage over A3 grows with the phase (0 → +0.006). Accuracy does not explain D-068's loss in play; the prior-shape columns (floor share 39 % vs 1–11 %) differ by an order of magnitude. RL translation: as a search prior, calibration and sharpness are separate properties from top-1 accuracy — the reward signal for choosing a prior is play, not imitation accuracy.

### Arm T0 — result (appended 2026-10-05 03:01 UTC, hinata). Descriptive.

- **T0-400 (A1 minus hb_f_round and the 16 hb_f_mem_*; 253 inputs): 0.7150 [0.7070, 0.7240]**, queen 0.6719; T0-800 0.7127. **A1-400 − T0-400 = +0.0034 [+0.0022, +0.0046]** (188,250 F/R/L rows, 49 series, paired series bootstrap 1,000 × seed 7, linear 5/95). By phase 0→4: +.007 [−.004, +.017], +.004 [+.000, +.009], +.003 [+.001, +.004], +.005 [+.003, +.006], +.001 [−.003, +.004]. T0 − A0 +0.0174 [+0.0138, +0.0210].
- **Cost < 0.005, so T1 (phase models) is not triggered (D-067 §E.3).** My forecast P(cost ≥ 0.005) = 0.25 → outcome no; Brier 0.0625.
- Registry: T0-u registry.json 55a941c4f048678b… (r2_t0.py ec2ca5d8…, r2_battery 224c667a… fit path).
- RL translation: the clone uses time and memory a little (≈ 0.003 of accuracy, 7 % of gain); the missing time structure the lead points at (D-067) is not recoverable from these per-turn inputs — it needs trajectory features (encoder v2) or a latent (P-8).

### Arm A11 (encoder + HB-1 vector, no hb_p) — configuration fixed before any A11 fit (appended 2026-10-05 03:38 UTC, hinata). D-069 §C.

- **Claim.** The encoder and the HB-1 vector are complementary without the parent's prior: a single model on both (1,463 columns = A5's 1,466 minus hb_pF/hb_pR/hb_pL) is about as accurate as A5 and has a sharper-than-A5 but non-degenerate prior shape. Rung R2 (P1, measurement arm). Mechanism: A5 − A1 +0.0083 and A5 − A4 +0.0062 say each encoding adds information the other lacks; hb_p is a deterministic function of the HB-1 view, so the trees should recover most of it from the HB-1 vector.
- **Recipe** (`tools/hinata/r2_a11.py` a758e1f5…): r2_battery.fit for arm A5 exactly (r2_bc.PARAMS, dev120 oracle F/R/L rows, series5 folds = A5-u's fold hashes via --expect-folds, 400 and 800 rounds from one fit, unweighted) with the three hb_p columns removed; outputs renamed A5-* → A11-*. Cloud core only (D-069 §C); fold models copied back to the Mac as they finish (resumable across units).
- **Inventory:** `A11-400`, `A11-800` added to `descriptive` in `tools/hinata/r2_inventory.json` (49923dda…) before the fit; no selection, no slot work.
- **Report:** F/R/L accuracy [series 5/95], paired against A5-400, A8b-A1-400, A1-400 and A3-400 on identical rows; **log-loss, entropy, floor share (min option ≤ 1e-4), mean top-two log gap**; model bytes at 400 rounds. Population: 188,250 F/R/L rows, 49 series, post-m2; paired series bootstrap 1,000 × seed 7, linear 5/95.
- **Expected:** A11-400 ≈ 0.723–0.727; A5-400 − A11-400 in [0, +0.003]. **P(A11-400 − A1-400 ≥ +0.005, 5th pct > 0) = 0.55. P(A11-400 − A8b-A1-400 ≥ +0.005, 5th pct > 0) = 0.15. P(A11-400 floor share < A5-400's 11.2 %) = 0.6.** Model bytes at 400 rounds < 4 MiB: 0.9.
- **Falsifier:** A11-400 below A1-400 (5th pct of A11 − A1 < 0) refutes complementarity without hb_p.
- **Stop rule:** one fit, no tuning, no further variants on this card; held-out maps never read.
- **Cost:** ≈ 2.5 h on one cloud core (A5's per-fold time), across two units.
- **RL translation:** observation = union of the window encoder and the HB-1 hand-built vector; the parent's prior is not needed as an input if the union carries it, which keeps the actor a single network/model over raw-ish features.

### Arm A11 — result; A10b-full and single-team priors — results (appended 2026-10-05 05:23 UTC, hinata). Descriptive (selection by accuracy suspended, D-068).

Population for A11: dev120 oracle F/R/L rows, 188,250 rows, 49 series, post-m2, keys equal A0's; paired series bootstrap 1,000 × seed 7, linear 5/95.

| Arm | F/R/L acc [5th, 95th] | log-loss | entropy | floor share | top-two log gap | model text bytes (400) |
|---|---|---|---|---|---|---|
| **A11-400** (encoder + HB-1 vector, no hb_p) | **0.7264 [0.7179, 0.7356]** | 0.5865 | 0.5712 | 6.4 % | 2.31 | 11,452,609 |
| A11-800 | 0.7238 | | | | | |
| A5-400 | 0.7267 | 0.5864 | 0.5604 | 11.2 % | 2.45 | |
| A8b-A1-400 | 0.7224 | 0.5948 | 0.5925 | 1.0 % | 2.20 | |
| A1-400 | 0.7184 | 0.6017 | 0.5850 | 1.8 % | 2.23 | 11,229,460 |
| A0 | 0.6977 | 0.7480 | 0.4254 | 39.0 % | 3.37 | |

- Paired: A11-400 − A5-400 −0.0003 [−0.0016, +0.0008]; − A8b-A1-400 +0.0039 [+0.0017, +0.0060]; − A1-400 +0.0080 [+0.0063, +0.0097]; − A3-400 +0.0119 [+0.0099, +0.0138]; − A0 +0.0287 [+0.0247, +0.0330]. Queen rows 0.6627 (n 5,315).
- Against the pre-registration (03:38Z): A11 ≈ A5 (yes; Δ inside [−0.003, 0]); A11 − A1 ≥ +0.005 with 5th pct > 0: **yes**; A11 − A8b-A1 ≥ +0.005: no (+0.0039); floor share below A5's: yes (6.4 % vs 11.2 %); model under 4 MiB in export: not measured (text 11.45 MB, the same class as A1-400). Falsifier not triggered. **hb_p adds nothing once the encoder and the HB-1 vector are both inputs.**
- Registry build/hinata/r2/battery/A11-u/registry.json (sha e2e50514…; fit code r2_battery rev 8 b5346f3c…, wrapper r2_a11.py a758e1f5…, features 1,463, r2_bc.PARAMS, folds = A5-u's). Cloud core, 5 folds × ≈ 19 min. Fold models as gz on the Mac (models.sha256 = uncompressed).
- RL translation: observation = encoder window ∪ HB-1 vector; no need to feed the parent's prior.

**A10b-full** (D-064 §C; Mac job hinata-01, rc 0, 2 h 51 min, peak 7.38 GiB): 0.7280 [0.7254, 0.7312] on 2,753,685 full-row F/R/L rows, 496 series (series5 out-of-fold; early stop at epoch 5–7). On the dev120 games' rows (188,250, labels agree 100 %): 0.7284 [0.7196, 0.7383]; vs A8b-A1-400 +0.0060 [+0.0025, +0.0093], vs A1-400 +0.0100 [+0.0065, +0.0138], vs A5-400 +0.0017 [−0.0017, +0.0055], vs A0 +0.0307. Not like for like (≈ 14.6× training rows, different folds); A1-full (five one-fold jobs) is the fair comparison. Prior shape on those rows: 0.584 / 0.575 / floor 26.2 % / 2.27.

**Single-team priors** (D-068 §5; Mac jobs 015/016 rc 0; deploy files model_all_400.txt): team 213 0.7541 [0.7476, 0.7603] (268,722 rows, 63 series), team 91 0.7133 [0.7092, 0.7175] (222,647 rows, 40 series), out-of-fold on the team's rows; vs A10b-full on the same rows +0.0579 [+0.0557, +0.0602] and +0.0292 [+0.0266, +0.0315]. Shape: 213 0.539 / 0.561 / 2.4 % / 2.19; 91 0.603 / 0.612 / 7.3 % / 2.15. A0 on the same rows: next unit.

### Clone in play — entropy-matched λ for the team-213 prior: definition fixed before computing (appended 2026-10-05 05:37 UTC, hinata). D-075 §E.

- **Ask (Chair 05:19Z):** beside the team-213 arm at λ 1, one arm at the λ where the tempered prior's mean entropy on the development rows equals the live prior's. λ is computed off-line, once, before any pool game of either arm; it is not tuned on any pool result.
- **Tempered prior exactly as the slot plays it** (kageyama-02 policy.hpp, D-055 §E): q_i ∝ max(p_i / (p_F + p_R + p_L), 1e-4)^λ over i ∈ {F, R, L}; entropy H(q) in nats over these three.
- **Model:** `build/learn/hinata/r2full/A1-team213/model_all_400.txt` (the deploy refit Kageyama exports), features by the model's own feature names.
- **Rows (primary):** dev120 oracle F/R/L rows **not played by team 213** (the deploy model trained on 213's rows, so its entropy there is in-sample and too low). **Target:** mean H of the live prior (hb_pF/R/L, renormalised, same floor) on the same rows. **Secondary (reported, not used):** all 188,250 dev120 rows.
- **Solve:** bisection on λ ∈ [0.5, 6] to |ΔH| < 0.001, rounded to 2 decimals. Also reported: λ = 1 entropy of the 213 model, and the same computation for A1-400 (dev OOF) so the λ 1.41 arm (−5.88 pp) can be placed on the same scale.
- **Expectation:** λ ≈ 1.4–1.9 (213's in-sample 0.561 → 0.43). P(λ_match in [1.3, 2.0]) = 0.7.
- **Queen columns** for both arms are the pool harness's (Asahi); no extra metric of mine.
- RL translation: λ is the actor's inverse temperature on the demonstration prior; matching the live prior's entropy isolates content from sharpness.

### Results: entropy-matched λ, and A1-full vs A10b-full (appended 2026-10-05 05:45 UTC, hinata). Descriptive.

**λ_match (definition fixed above).** Rows: dev120 oracle F/R/L rows not played by team 213, 174,468 rows, 46 series, post-m2. Live prior (hb_pF/R/L, renormalised, floor 1e-4) mean entropy **0.4228** nats.

| Prior on these rows | acc (F/R/L argmax) | H at λ 1 | H at λ 1.41 | **λ_match** | log-loss at λ 1 / λ_match |
|---|---|---|---|---|---|
| team-213 deploy model (model_all_400) | 0.6954 | 0.5304 | 0.4303 | **1.45** | 0.681 / 0.772 |
| A1-400 (dev OOF, pooled) | 0.7197 | 0.5810 | 0.4829 | 1.72 | 0.599 / 0.663 |
| live prior (A0) | 0.6977 | 0.4228 | — | 1 | 0.745 |

All 188,250 rows (secondary): team-213 λ_match 1.44 (in-sample on 213's 13,782 rows), A1-400 1.73, live 0.4257. Queen rows (not 213, 4,810): live 0.371 vs team-213 at λ 1 0.483. Expectation λ in [1.3, 2.0] (P 0.7): yes.
- **Arm requested: team-213 prior at λ 1.45** (beside λ 1). Read-across: the A1-400 arm at λ 1.41 (−5.88 pp) was still softer than the live prior (0.483 vs 0.423); A1-400 needs λ 1.72 to match.
- **Note for the route:** on other teams' rows the team-213 model predicts no better than the live prior (0.6954 vs 0.6977) and worse than pooled A1-400 (0.7197): it is a 213 imitator, not a better general predictor. Its in-play value is untested; the pool is the test.

**A1-full vs A10b-full** (Mac jobs hinata-02a…02f rc 0, r2_full rev 4 908647…; full teacher rows, 2,753,685 F/R/L rows, 496 series, series5 out-of-fold, identical rows/folds/labels; paired whole-series bootstrap 1,000 × seed 7, linear 5/95):
- **A1-full 0.7379 [0.7352, 0.7409]; A1-full − A10b-full +0.0099 [+0.0089, +0.0107]**; positive on all 14 maps (+0.004 Around UNSW … +0.032 Trophy); queen rows (52,783, 184 series) **+0.0421 [+0.0342, +0.0506]** (0.7334 vs 0.6913); team 213 rows +0.0211, team 91 +0.0116.
- On the dev120 games' rows: A1-full 0.7392 (out-of-fold; folds differ from the development table's) vs A1-400 dev 0.7184 and A10b-full 0.7284 — the data size step (≈ 15×) is worth ≈ +0.02 for trees.
- Shape (F/R/L): A1-full log-loss 0.5647, entropy 0.5856, floor share 9.6 %; A10b-full 0.5819 / 0.5694 / 26.5 %.
- Registry: build/learn/hinata/r2full/A1-full/registry.json (code r2_battery fit path b5346f…, r2_full rev 4; rows_sha 6f531e91…; 270 features; r2_bc.PARAMS; 400 rounds; fold models 11.4 MB text each).
- RL translation: with the full demonstration set the hand-built vector + trees beat the small CNN on the raw window by ≈ 1 pt overall and 4 pts on queen decisions; the actor's observation should keep the HB-1 vector.

### A1-full deploy refit — pre-registration (appended 2026-10-05 05:45 UTC, hinata)
- **What:** `r2_full.py trees --arm A1 --final --sizes 400 --run build/learn/hinata/r2full/A1-full` — reloads the five fold models (no refit, same scores), then one refit on all 2.75 M rows → `model_all_400.txt`. One job, ≈ 5–10 min, peak ≈ 5 GiB.
- **Use:** the pooled prior candidate for the slot (for Kageyama's export) after the team-213 arms read; its λ_match computed by the definition above (dev120 rows, in-sample for this model on all of them, so reported as in-sample). No pool arm is requested by this card; any arm gets its own declared λ.
- **Expectation:** CV metrics unchanged to 4 decimals (P 0.95); λ_match(in-sample) in [1.6, 2.1] (P 0.6).
- Stop rule: one refit, no tuning.

### Result: A1-full deploy refit and its λ_match (appended 2026-10-05 06:40 UTC, hinata). Descriptive; no pool game read.
- **Job hinata-05-a1-full-final rc 0** (Mac, 06:26–06:31Z; load 42 s, refit 257 s, peak 8.38 GiB). CV metrics unchanged (fold models reloaded): A1-400 0.7379 [0.7352, 0.7409], n 2,753,685, queen 0.7334 — expectation "unchanged to 4 decimals" (P 0.95): **yes**. Artifact: `build/learn/hinata/r2full/A1-full/model_all_400.txt` (11.4 MB text, sha256 60c57a64c41eba85…, 270 features, 400 rounds, rows_sha 6f531e91…, code b5346f3c…/r2_full rev 4).
- **λ_match (definition above), dev120 oracle F/R/L rows not played by 213 (174,468 rows, 46 series, post-m2; live H 0.4228):**

| A1-full prior on these rows | acc | H at λ 1 | **λ_match** | H at λ 1.72 | log-loss λ 1 / λ_match |
|---|---|---|---|---|---|
| deploy model, in-sample (trained on these rows) | 0.7491 | 0.5844 | **1.76** | 0.4295 | 0.548 / 0.575 |
| series5 out-of-fold | 0.7404 | 0.5864 | 1.77 | 0.4315 | 0.563 / 0.600 |
| live prior | 0.6990 | 0.4228 | 1 | — | 0.745 (from lam.json) |

  All 188,250 rows: 1.765 in-sample / 1.777 OOF. Expectation λ_match(in-sample) in [1.6, 2.1] (P 0.6): **yes**.
- **Reading:** A1-full's λ_match (1.76) is within 0.04 of A1-400's (1.72), and A1-full at λ 1.72 has H 0.430 vs live 0.423. So the Chair-ordered arm **A1-400 @ λ 1.72** (D-076 §D) is, in sharpness, also the A1-full arm; a later A1-full arm at **λ 1.76** isolates the content/data step (+0.02 accuracy off-line) at fixed entropy. No arm requested by this note beyond D-076's queue.
- Hand-off (Kageyama): A1-full export = same input path and feature order as A1-400; declared λ for any A1-full arm **1.76**.
- RL translation: the full-data demonstration prior is softer than the live hand prior at λ 1 by 0.16 nats; matching entropy needs inverse temperature ≈ 1.76 — the actor's temperature must be set per prior, not inherited.
