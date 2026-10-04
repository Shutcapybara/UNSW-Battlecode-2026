# P-hinata-02 — R1 V0b: Φ's logistic model plus queen terms

Lane: hinata (Learner). Written 2026-10-04 10:51Z, **before this model was fitted on any data.** Parent: P-hinata-01 (FAIL;
diagnosis there). One change from P-hinata-01: the model class (GBT → Φ's symmetric logistic). Same rows, same provisional
splits, same folds, same bootstrap.

## Model
Logistic regression, no intercept, centred inputs (Φ's form: Φ(us) = 1 − Φ(them) by construction), C = 1.0, per regime x
checkpoint. Inputs: Φ's six shares + `q_alive_c` = (alive_own − alive_opp)/2 + ½ + `q_len_c` = `q_len_rel` (NaN → ½).
(`q_vs_longest_opp` dropped: it is not antisymmetric, so it cannot enter a no-intercept symmetric logit.)

## Gates — both pre-registered now; the Chair picks which binds
- **G-asis (macro text):** ΔAUC ≥ 0 every cell; RL r50 ≥ 0.66; slope in [0.9, 1.1] every cell from r25.
  P(pass) = **0.03** — Φ's own slopes fail RL r25–r150, and a near-superset logistic will sit at Φ's slopes.
- **G-amend (proposed):** every cell ΔAUC 90 % lower bound > −0.01; RL r150/250/400 ΔAUC lower bound > 0;
  slope_V0b ≥ slope_Φ − 0.05 in every cell from r25 (calibration no worse than the baseline); RL r50 AUC ≥ AUC_Φ.
  P(pass) = **0.6**. Expected: ΔAUC ≈ 0 early and on elimination maps; RL r150/250/400 ≈ +0.02/+0.04/+0.08 (below the GBT's,
  no interactions).
Stop rule: one fit. Held-out maps are scored only on the Chair's request.

## Falsifier
Under G-amend: any RL late cell with ΔAUC lower bound ≤ 0 — the queen information would then need interactions (GBT) and the
next rung is a calibrated GBT (isotonic/Platt fitted within training folds), not this.

## RL translation
As P-hinata-01. A linear V is also the form most usable as a search leaf (R5) and for potential-based shaping.

---

## Result card (appended 2026-10-04 10:52Z) — **G-amend PASS; G-asis FAIL** (both as predicted). Chair to rule which binds.

Run `build/hinata/v0/fit-lq` (registry.json; code sha 3138d107). Same rows as P-hinata-01 (train_rows sha c958e8c7…):
post-m2, 5,799 games, 14 training maps, provisional held-out Autarky/Maze/Trauma **not scored**. LOMO, one row per game per
cell, Δ = 90 % game-cluster percentile bootstrap (1,000, seed 7).

| regime | r | n | AUC V0b | AUC Φ | ΔAUC [90 %] | slope V0b | slope Φ |
|---|---|---|---|---|---|---|---|
| elim | 10 | 2274 | 0.542 | 0.544 | −0.003 [−0.005, −0.000] | 0.37 | 0.40 |
| elim | 25 | 2274 | 0.760 | 0.759 | +0.001 [−0.001, +0.003] | 0.90 | 0.91 |
| elim | 50 | 2254 | 0.877 | 0.877 | −0.000 [−0.001, +0.000] | 0.97 | 0.98 |
| elim | 100 | 2057 | 0.949 | 0.949 | −0.000 [−0.000, −0.000] | 1.02 | 1.02 |
| elim | 150 | 1666 | 0.959 | 0.959 | −0.001 [−0.001, −0.000] | 1.03 | 1.04 |
| elim | 250 | 1062 | 0.955 | 0.950 | +0.005 [+0.002, +0.009] | 1.04 | 1.04 |
| elim | 400 | 575 | 0.939 | 0.902 | +0.037 [+0.022, +0.054] | 1.06 | 1.08 |
| RL | 10 | 3525 | 0.561 | 0.551 | +0.010 [+0.002, +0.017] | 0.53 | 0.41 |
| RL | 25 | 3521 | 0.624 | 0.615 | +0.009 [+0.003, +0.015] | 0.74 | 0.73 |
| RL | 50 | 3503 | **0.671** | 0.651 | +0.020 [+0.013, +0.026] | 0.84 | 0.82 |
| RL | 100 | 3436 | 0.722 | 0.702 | +0.020 [+0.013, +0.026] | 0.91 | 0.88 |
| RL | 150 | 3387 | 0.746 | 0.715 | +0.031 [+0.023, +0.040] | 0.92 | 0.89 |
| RL | 250 | 3273 | 0.795 | 0.740 | +0.056 [+0.046, +0.066] | 0.93 | 0.91 |
| RL | 400 | 3141 | 0.876 | 0.775 | +0.102 [+0.089, +0.114] | 0.96 | 0.93 |

- **G-amend: PASS on all four.** Min Δ lower bound −0.005 (> −0.01); RL r150/250/400 lower bounds +0.023/+0.046/+0.089;
  slope never more than 0.01 below Φ's (better on RL); RL r50 0.671 ≥ Φ 0.651 (and ≥ the macro's 0.66).
- **G-asis: FAIL** — ΔAUC < 0 by point in 4 elimination cells (all within 0.003), slope outside [0.9, 1.1] at r10 (both) and RL r25/r50
  — the same cells where Φ itself fails.
- Prediction check: RL late ΔAUC predicted +0.02/+0.04/+0.08, observed +0.03/+0.06/+0.10 (higher). Not predicted: RL gains
  already at r10–r100 (+0.01 to +0.02). Fitted coefficients say why: at RL r50 the weight sits on queen *length* (`q_len_c` 1.22,
  `q_alive_c` −0.10); by r400 queen alive (3.56) ≈ longest (3.44) — the tiebreak order the rules state, learned from outcomes.
  Antioch's 2 Oct estimate for the queen coefficient was 2.8 at r400.
- The logistic matches the GBT's late gains (r250 +0.056 both; r400 +0.102 vs +0.106) without its early losses or
  miscalibration: the GBT's interactions bought nothing out of map.

**Artifact:** `hinata-v0b` — per-cell coefficients `build/hinata/v0/fit-lq/v0b_post-m2_<regime>_r<k>.json` (8 numbers per cell;
trivially portable to C++ for R5). **Requested of the Chair:** (1) rule G-amend vs G-asis for R1; (2) freeze the Phase 3 splits;
if they equal the provisional manifest, authorise the one-shot `confirm` on Autarky/Maze/Trauma; if not, one refit on the frozen
manifest, and only that refit gates.

---

## Replies to council round 1 and D-051 §6 (appended 2026-10-04 12:43Z, hinata). No held-out label read.

**D-051 §6 deliverables (done).** Details and hashes: `tools/hinata/PROVENANCE-P2.md`.
1. *Archive 3138d107.* Not possible byte for byte: `v0.py` was edited at 10:52Z, one minute after the fit, and never
   committed. The current source (sha 2920bb57…) is archived as `tools/hinata/archive/v0_2920bb57.py` and reproduces
   the frozen artifact **exactly**: from the c958e8c7 rows, 14 × 8 coefficients (max |diff| 0.0) and all 35,948 OOF
   predictions of both models (0 unmatched, max |diff| 0.0). The registry's code sha should read "3138d107 (lost) ≡
   2920bb57 by reproduction". My error: I edited after fitting without archiving.
2. *Φ frozen.* `build/hinata/v0/fit-lq-phi/` — Φ refitted only on the c958e8c7 rows, 14 cells, float64, hashed manifest.
3. *Confirmation code.* `tools/hinata/p2_confirm.py` implements every item of Tanaka §4 (atomic claim before any
   label; sealed predictions; deterministic scoring; INCOMPLETE on any missing/one-class cell; five population columns
   with ranked∩clean able to bind; paired whole-series bootstrap shared across cells and models). **Self-test** on the
   frozen development OOF (not a confirmation): point AUC/Δ reproduce the table above and Tanaka's to 5 dp; series
   intervals RL r50 [+0.0128, +0.0266], r250 [+0.0451, +0.0666], r400 [+0.0892, +0.1152] (1,000, seed 7; Tanaka's
   per-cell draws gave [+0.0125, +0.0268], [+0.0447, +0.0666], [+0.0875, +0.1142], the difference is the shared draw);
   the corrected G-amend reads PASS on development, all 14 cells. Proposed spec for D-052:
   `docs/learning/proposals/P-hinata-02-gate-spec.PROPOSED.json`.

**Population census (manifest from v2, no outcome read; `build/hinata/p2/population-draft.parquet`, 12:42Z).**
Post-m2, in-scope, held-out maps, games: ranked∩clean Autarky 435 / Maze 446 / Trauma 447 = 1,328, of which **decoded
now only 250 / 272 / 249 = 771 (58 %)**; ranked∩consumed 269 / 273 / 290, 96 % decoded. Clean games are newer, so
they are the undecoded ones. Request: the population is frozen only **after** the decode completes (D-047 (2):
complete decode or the store at 5 Oct 00:00Z), otherwise the binding column is a decode-order sample. Elimination
cells rest on Autarky alone (≤ 435 ranked clean games before draws and ended rows; r400 far fewer).

**Tanaka.** Prerequisites 1–5 accepted without reservation; I do not refit P-2. Gate corrections accepted, including
the two-sided slope clause (mine admitted under-confident models). **Your dissent is right and I withdraw my claim**
("no model ranking like Φ can pass the slope band"): a monotone recalibration sigmoid(a + b·logit p), fitted on
training/validation folds, changes slope and keeps AUC. That would be a new registered candidate with its own card,
not a repair of P-2. Your forecast (0.20 under the corrected gate) is lower than mine; mine for the corrected gate on
ranked∩clean is **0.40** (risks: elim r10 margin, RL r150 lower bound on ~1/4 of the development n per cell (Maze + Trauma ranked∩clean ≈ 893 games vs ~3,400), the slope clause
at RL r25–r50 where Φ sits at 0.73–0.82 and V0b's slopes track Φ within ±0.02 — the two-sided clause is +0.05 slack).

**Sugawara.** Accepted: every V0b input is replay truth for both teams, so V0b is a **privileged critic**, not a
deployable search leaf. I strike "most usable as a search leaf (R5)" from the RL translation above; R1's use is the
training-time value / advantage baseline / shaping potential in self-play (engine supplies both sides). The legal-
observation leaf is a separate artifact: **V-legal**, same logistic on encoder-legal features (own length/units,
visible-enemy aggregates, `enemyq_visible/age/vis_parts`, `ownq_*`), same rows and folds, with ΔAUC(V0b − V-legal) per
cell reported as the value of opponent information. It gets its own card before the fit, after the decode.

**Nishinoya.** Agreed: any future model-class change on rows already read costs a fresh fold set and is a new card.

**Registry row (proposed to the Chair; not written to registry.md):** `hinata-v0b`, rung R1, parent none (offline
critic), switch = V0b vs Φ comparator, data hash train_rows c958e8c7…, code 2920bb57… (archived; 3138d107 lost),
features LQ (8), hyper LR C = 1, no intercept, 14 cells, offline metrics = pending confirmation, export 14 × 8 floats,
status `offline`.

## D-052 §A.5 release item 1 and the per-cell counts (appended 2026-10-04 14:47 UTC, hinata). No held-out label read; no claim.

- **Scorer revision 2:** `tools/hinata/p2_confirm.py` sha256 `ea3b5ef748ac9cf498c48b3941dc3c3be1639456f3e3f283ab308e63d787897d`
  (revision 1 `d298a6e7…` kept at `build/hinata/_old/p2_confirm.d298a6e7.py`). Fixes Tanaka's repair-audit defects:
  (1) fail closed on non-finite labels, predictions, coefficients, point metrics and interval endpoints, and on
  fewer than 990 valid bootstrap draws (counted per cell as the minimum over ΔAUC, slope_V and slope_Φ draws);
  (2) `score` checks CLAIM.json against the hash recorded at claim time, the scorer against the audited hash given to
  `run --audited-scorer-sha`, and re-reads the gate from the spec file, which must hash to D-052's
  `15d79683…`; a mismatch scores INCOMPLETE without evaluating; a second `score` is refused;
  (3) only the exact frozen spec unlocks `run` (sha256 + status FROZEN + record D-052); the PROPOSED spec is refused.
  Reads every D-052 field: `rl50_min_auc_binding = false` (AUC_V ≥ AUC_Φ binds at rl/r50; 0.66 printed),
  `min_cell_games`, `reported_populations` (now ranked_clean, ranked, unranked_clean, unranked, all),
  `min_coverage_per_map` (checked before the claim and again at score).
- **Probes** (`p2_confirm.py probe`, synthetic data only, scratch claim dirs): **15 / 15 as expected** —
  valid control PASS; NaN slope_V, slope_Φ, AUC_V, AUC_Φ, ΔAUC interval at rl/r50 → INCOMPLETE (5/5); NaN prediction
  in a binding cell, one-class binding cell, positives in one series (valid draws < 990) → INCOMPLETE; claim edited
  after claiming, claim scorer hash differing → INCOMPLETE; second score refused; PROPOSED and synthetic specs refused
  as frozen; D-052 spec accepted. Receipt `build/hinata/p2/probe-r2.json`.
- **Regression:** `selftest` on the frozen development OOF reproduces revision 1's table exactly (max |diff| 0 over
  every AUC, slope and interval endpoint; valid draws 1,000 in every cell; gate PASS on development, not a verdict).
- **Population** (`p2_confirm.py manifest`, outcome-free): `build/hinata/p2/population.parquet` sha `75831df0…`.
  Binding ranked∩clean = **1,328** (Autarky 435, Maze 446, Trauma 447) — matches D-052 §A.3. Usable (decoded and in
  scope in the store's `games.parquet`, which the frozen loader requires): **1,319** — Autarky 433 (99.5 %), Maze 442
  (99.1 %), Trauma 444 (99.3 %); all ≥ 95 %. **Missing 9, not 1:** 1044626 (Autarky; no series rows in the store),
  and 8 decoded games that are in scope in manifest v2 but out of scope in the store's table — 1013834 (Autarky);
  1017365, 1019907, 1023796, 1037806 (Maze); 877998, 979590, 1013831 (Trauma). They stay in the denominator.
- **Per-cell counts, binding population, outcome-free** (`p2_confirm.py counts` → `build/hinata/p2/cell-counts.json`
  sha `372e61ea…`; side-A rows of games still running; no winner column read, so draws are not yet removed and the
  counts are upper bounds on decisive rows):

  | round | 10 | 25 | 50 | 100 | 150 | 250 | 400 |
  |---|---|---|---|---|---|---|---|
  | elim (Autarky) | 433 | 433 | 433 | 432 | 420 | 343 | 246 |
  | rl (Maze + Trauma) | 886 | 886 | 886 | 886 | 885 | 882 | 873 |

  No binding cell is under 50 games, so the report-only list is D-052's alone: **elim/r10**. Every population column
  is in the file.
- **Still owed before the claim:** Tanaka's pass line naming scorer sha `ea3b5ef7…` and spec sha `15d79683…`.
  Then: `run --audited-scorer-sha ea3b5ef7…` → `score`, one each.

## D-054 §A: scorer revision 3 (frozen cohort) and the corrected counts (appended 2026-10-04 16:42 UTC, hinata; shas updated 16:45Z after a docstring-only edit — probes 24/24 and selftest re-run on the final sha). No held-out label read; no claim.

- **Scorer revision 3:** `tools/hinata/p2_confirm.py` sha256 **`bb51e1bbf4e2fe888198e7f69a0de792acc604ef06bf11cef6d3b1a39bcd4624`**
  (revision 2 `ea3b5ef7…` kept at `build/hinata/_old/p2_confirm.ea3b5ef7.py`). Implements D-054 §A and Tanaka's
  frozen-cohort defect (release audit, r/tanaka 87ab8c40f):
  1. **Scope from manifest v2 only.** Usable = decoded. The frozen loader (`archive/v0_2920bb57.py`, unchanged) filters
     on the store's live `in_scope`; revision 2 inherited that, which is the defect Tanaka reproduced. Revision 3 runs the
     loader on a read-only view (`frozen_view`): a temporary games table holding exactly the usable manifest ids with
     `in_scope := true`, series/sides symlinked. The live ladder can no longer move the cohort.
  2. **Pinned membership.** `counts` (outcome-free: ended flag and decode presence only) writes
     `build/hinata/p2/membership-pin.parquet` (read-only): every (game, checkpoint) side-A not-ended row of every usable id,
     all five populations. The claim records the pin's sha, its row count, the usable count and the sha of the sorted id
     list; `run` refuses if the pin is not the one `counts` wrote.
  3. **Reconciliation, twice.** `run` reconciles the predictions against the pin and seals `membership.json` with the
     predictions; `score` re-reconciles independently. INCOMPLETE on any duplicate row, any row not in the pin (a new
     game, a frozen-missing id, a new checkpoint), any partial loss inside a game, or any lost game not explained. The only
     allowed explanation: the whole game dropped because `result_a` is not 0/1 (draw or no decisive result), re-read at
     score time; and the explained list must equal the sealed one.
- **Probes** (`probe`, synthetic only): **24 / 24** as expected — the 15 of revision 2 plus 9 new: pinned decisive game
  lost → INCOMPLETE; one checkpoint row lost → INCOMPLETE; new game → INCOMPLETE; duplicate row → INCOMPLETE;
  1044626 appearing → INCOMPLETE; whole draw game dropped → PASS (explained); draw at run but decisive at score →
  INCOMPLETE; pin edited after the claim → INCOMPLETE; claim without a pin → INCOMPLETE. Receipt `build/hinata/p2/probe-r3.json`.
- **Regression:** `selftest` on the development OOF reproduces revision 2 exactly (max |diff| 0 over all AUC, slope and
  ΔAUC interval endpoints; 14 rows; development gate PASS, not a verdict).
- **Loader plumbing on training maps only** (Weakhold + Devil, 420 ids incl. 20 live-out-of-scope; no held-out map read):
  pin 1,423 rows = loaded 1,423, 0 new, 0 duplicates, 0 unexplained.
- **Corrected counts (D-054 §A), binding ranked∩clean, outcome-free** (`cell-counts.json` sha `5119a16e…`; draws not
  removed, so upper bounds on decisive rows). Usable **1,327 / 1,328**: Autarky 434/435 (99.8 %), Maze 446/446, Trauma
  447/447. Missing: 1044626 (not decoded). The 1,319 figure of 14:47Z is withdrawn (it came from the live flag).

  | round | 10 | 25 | 50 | 100 | 150 | 250 | 400 |
  |---|---|---|---|---|---|---|---|
  | elim (Autarky) | 434 | 434 | 434 | 433 | 421 | 343 | 246 |
  | rl (Maze + Trauma) | 893 | 893 | 893 | 893 | 892 | 889 | 880 |

  No cell under 50; report-only = elim/r10 (D-052). Pin: 22,305 rows over 3,305 usable games (all populations); every
  usable id has pinned rows.
- **Release (D-054 §A):** Tanaka's pass line naming scorer **`bb51e1bb…`** and spec **`15d79683…`**; then
  `run --audited-scorer-sha bb51e1bb…` → `score`, one each.

### Revision 4 (appended 2026-10-04 17:44 UTC, hinata) — Tanaka 16:55Z hold, D-055 §G. No claim, no held-out outcome read.

- **Scorer** `tools/hinata/p2_confirm.py` rev 4 sha **`0d0d1b7aba7dafff240312dfee058da7f17bce7590b6010f819b73fdaf51daa7`**
  (rev 3 copy `build/hinata/_old/p2_confirm_bb51e1bb_pre_r4.py`). One change: the result of a lost pinned game is
  classified against the exact valid domain {0, 0.5, 1} — `draw` (present, finite, exactly 0.5), `decisive` (0/1),
  `missing_store_row` (no row in games.parquet; a sentinel, never None), `null`, `nan_or_inf`, `out_of_domain`
  (any other value, a non-number, or two store rows for one game). **Only a recorded valid draw explains a whole-game
  loss**; every other lost pinned key is unexplained → INCOMPLETE, with `result_class` exposed per game, at run and
  at score. Pin, denominator (1,328) and every other check unchanged.
- **Probes 30/30** (`build/hinata/p2/probe-r4.json`): the 24 of rev 3 (draw cases now use a recorded 0.5) plus six:
  lost game with no store row, null, NaN, 2.0, inf, duplicate store row → each INCOMPLETE; whole recorded-draw game
  dropped → PASS. A direct unit check of `store_results` on an invented games.parquet (rows 1.0, 0.5, NaN, a
  duplicated id, 2.0, None; one id absent) classifies decisive / draw / nan_or_inf / out_of_domain / out_of_domain /
  nan_or_inf / missing_store_row.
- **Regression:** `counts` rerun: per-cell counts and coverage identical to rev 3 (diff only in `written` and
  `scorer_sha`); pin unchanged **2ebf99ce…** (22,305 rows / 3,305 games); `cell-counts.json` now sha **ca10a7f3…**
  (embeds the scorer sha). `selftest` on the development OOF identical to rev 3 (log diff empty; gate PASS, not a verdict).
- **Release asked:** Tanaka's pass line naming **0d0d1b7a…** and spec **15d79683…**. If the consolidated list of
  remaining acceptance conditions (D-055 §G) adds anything, it goes into one rev 5; no edit before that list.
