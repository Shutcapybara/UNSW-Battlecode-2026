# R2 development battery — Tanaka audit

2026-10-04 20:19Z. Assigned D-057 §C: ensure no arm, fold or selection step uses the frozen confirmation cohort. **Development isolation checks pass within the inspected scope; AMEND the selection tooling before any real winner/confirmation claim.** Ongoing authorized fitting is not held by this review.

## Scope, replication and findings

MAIN source audited: r2_battery.py `8fdddd38ceb5184a56c29145888c99453ca0907c8f9069fa6d37a7b649729dc4`, r2_bc.py `a31faa5d8ea31652674b993c77d7549d978437b2226f7e659d7004fa76036427`, r2_cnn.py `5e8d6f46c667d4ddb5e1c09a6564e98bbee0a98d118378c92750b625c613802d`. The author's19:50ec9bbfa7battery revision is not this local file; publish it if the defects below are already repaired in the cloud. This audit does not certify an unseen revision.

**No confirmation path appears in inspected development code.** Battery arms and CNN share R.load, which checks train split and rejects held-out map names. Independent invented-row tests accept train/Dev and refuse test, val, and train-labelled Autarky. Instrumented reads in those probes touch only invented row/teacher files. Current development manifests reference the known teacher shards; fold selection uses series hashes, and CNN scalar normalization is fitted within each training fold. This is source review plus synthetic loader testing, not a file-access trace of every actual cloud job. The loader must read supplied metadata before refusing a wrong file: the guard is not permission to point it at the real frozen cohort. Keep that cohort out of all development command arguments and sidecars.

**Four independently reproduced defects in the local selector:**

1. With100invented F-labelled rows and all-NaN four-class predictions, write() reports accuracy1.0 and table() returns PASS against an invented R-predicting baseline. NumPy argmax supplies a class even when predictions are undefined. A2 can leave predictions missing when a teacher lacks train/test support; no finite/completion guard prevents that output reaching metrics. No claim that a real completed arm contains NaNs is made.
2. A pooled arm with80of the100baseline rows is accepted, gets100%accuracy and PASS; the join checks only that each candidate key exists in A0. It does not require equality of the declared pooled supports, their folds or labels.
3. An invented A10with1.0accuracy is marked non-pooled while A3with.8is selected. POOLED contains onlyA1/A3/A4/A5, contrary to D-059's A10addition.
4. An invented A7fixwith1.0accuracy is only a table row. The output has rows/selection/a0 and no teacher-specific decision. D-058's extra candidate path is absent; `best_ts` is unused. A2's pooled collection of teacher-specific fits cannot itself be deployed as one actor policy without selecting a teacher; A7 must be assessed in its fixed-identity deployment form on the declared target teachers.

**Consolidated corrections before selection:** validate finite normalized prediction vectors and complete expected keys; one-to-one joins; exact pooled key/fold/label equality to the frozen development support; explicitly declared subset support for teacher-specific arms; require the planned candidate inventory or list an approved unavailable arm; implement the D-058/059 candidate paths; identify each decision by arm, size, run and manifest hash. Freeze each teacher-subset metadata count before confirmation action labels. Keep teacher-specific paired comparisons on the same target-teacher rows, with the parent's predictions for those rows. Same-population selection is not established merely by matching some keys.

For CNN resumes, the current manifest omits imported preprocessing/metric source hashes and a teacher-file hash, and permits existing model files when manifest.json is missing. Bind those before reusing a cached run; do not attach a fresh manifest to orphaned weights. This is source inspection, not a reproduced stale CNN fit. Scalar mean/scale and quantization must eventually accompany any deployment export; parameter bytes alone are an estimate, not a verified4MiB/points result. No torch training was run by this audit.

## Learning curve independently reproduced

All published curve points are teacher-weighted, as the author now corrects. They share189,630move keys,188,250F/R/L labels, and all five frozen evaluation-fold hashes. Recomputed accuracies:

| Training-series fraction | .10 | .25 | .50 | 1.0 |
|---|---:|---:|---:|---:|
| F/R/L accuracy |.67601062|.68417530|.70281541|.71417264|

Full minus half=.01135724, paired whole-series1000/seed7/linear interval[.00904706,.01420057],43/49series positive. This supports the recorded *point-estimate*≥.010criterion; the lower interval bound is below.010. It does not prove every future doubling gains1.5points or transfer this curve unchanged to an unweighted arm. The new unweighted refit is a distinct recorded artifact. CNN layout parsing yields23channels×49cells+66scalars with no duplicated column; this verifies shape, not Data's physical channel/mirror semantics.

## Verdict, forecast, effect, dissent and precedent

P(selected pooled arm passes the frozen paired G-parent confirmation) remains **0.60**, as carried forward by D-057. No forecast is revised using the curve or synthetic cases. Expected behavioral improvement is not measured here; the review prevents invalid evidence from choosing a model, rather than improving model accuracy itself. Teacher-specific confirmation and any multiple candidate opportunities need explicit labels; they do not retroactively become the one pooled event used for that forecast.

Dissent: a broad authorized development search is compatible with one frozen confirmation, but incomplete arrays, selective row loss, missing candidate paths and unstable artifact identity cannot define its winner. Precedent is this project's P-2 finite-metric failure and earlier R2 resume defect, which demonstrate the same concrete failure modes. D-058/059 provide the imitation architecture precedents; their external source verification belongs to the assigned mechanism review, not an unverified claim here.

RL translation: teacher actions are demonstrations, common folds measure imitation transfer, and the deployed policy may condition on one fixed teacher identity. Preserve the mapping from demonstration population to actor input and actual selected artifact. Offline accuracy and a CNN parameter budget do not replace the behavioral and runtime tests.

Receipt/source snapshots `tanaka-round9/`; helper `tools/tanaka/battery_audit.py`. Nice10, one worker,36GiBfree. No actual fit, real battery table invocation, held-out action/outcome labels or live outcomes read.

## Repair audit — 2026-10-04 21:25 UTC (D-060/D-061)

**Verdict: HOLD final selection; development fitting continues.** Audited battery `8a29e479aa9167cfb7dd18077a20e9ba1d56d6e8ce9e60dca0419314b6e1c5fd`, CNN `e237fb767a074a545130b92f1919f664891eff614602d00c2cc10d18c6ea840a`, shared R2 `a31faa5d…`. This supersedes the prior source-mismatch notice: the local files now match Hinata's repair claim. No actual battery selection or confirmation was executed.

**Repairs verified.** Seven separate synthetic malformed cases now refuse: NaN, infinity, non-unit probability sum, pooled 80/100 support, duplicate keys, changed labels and changed folds. A complete invented planned inventory selects A10 when it is the smallest overlapping candidate, confirming pooled eligibility; missing pooled arms block pooled PASS. Teacher-specific candidates now exist and use paired lift, as D-061 approved. CNN imported-source/teacher hashes and orphan-weight refusal are present on source inspection (no CNN fit/resume performed).

**Remaining release blockers, independently reproduced on invented data:**

1. A6 with 25 rows from **team 4**, while its manifest declares top teams **1,2,3**, reports that declared target and `goes_forward=true`. Expected support is the exact A0 subset of declared top teams, not any arbitrary subset of A0. Verify team identity and full target key set.
2. A7fix with just 20/100 rows contains only **5/25** top-teacher rows; it still advances on a perfect two-series comparison. Require the full target support (and full input support if that is the artifact contract). Derive team/series/map/queen metadata from A0 or verify exact equality on keys; altered `series_key` currently changes the bootstrap clusters without refusal.
3. A2 with 80/100 predictions NaN drops them and advances with the remaining 20. Every teacher has train support outside every toy fold, so these are **not** structurally unsupported team/fold cells. Derive allowed exclusions from the training-side membership first, freeze their keys/counts and refuse all other missing predictions. A generic `unsupported_rows` count is insufficient provenance.
4. A complete, full-support A7fix alone advances while A2/A6/other A7 sizes are absent. Print teacher-specific `INCOMPLETE` and block final advancement until its fixed planned inventory is complete or explicitly waived by the Chair. This is distinct from the pooled-inventory repair, which passes.

All toys have 100 A0 rows, four teams and ten series; reported exact proportions are deterministic synthetic checks, with no field inference. A6's output CI is [1,1] on the wrong population, demonstrating why correct arithmetic alone is insufficient. Full cases and source snapshots are in `tanaka-round10/`; reproduction helper `tools/tanaka/battery_repair_audit.py`. Additional hardening observation: [2,-1,0,0] passes the finite/unit-sum check; require nonnegative probability vectors. This did not occur in the published A3/A10 arrays.

**Published development results independently reproduced.** Same complete ordered keys, labels, folds and series for A3-u/A10-u; rows.parquet SHA `a0b1ea2e…`, registries `8807488c…` / `3e23db4a…`. Post-m2, 14 training maps, 97 games, 49 series, 10 teachers; 189,630 moves / 188,250 F/R/L rows. No frozen confirmation input was opened.

| Arm/contrast | Accuracy or paired difference | Central 90% whole-series bootstrap |
|---|---:|---:|
| A3-400 unweighted | .71446481 | [.70613843,.72387977] |
| A3-800 unweighted | .71137849 | [.70340629,.71998209] |
| A10-e4 | .67268526 | [.66405781,.68148378] |
| A3-400 minus A10-e4 | +.04177955 | [.03789811,.04627209] |
| A3-800 minus A3-400 | −.00308632 | [−.00436652,−.00185762] |

Intervals: 1,000 draws, seed 7, linear 5th/95th. This confirms the published figures; it does not select a battery winner. Published A10 was fitted with the earlier CNN manifest; new resume protections do not retroactively add provenance. Retain that manifest and source history; no refit is requested.

D-062 copied HB scores were not present in the inspected battery/output inventory at this audit. No A0/side-score coverage pass is asserted; audit those keys once available, without another production request. No changed loader isolation path was found; previous synthetic train/test/val/held-out refusal evidence remains applicable. No global trace of remote jobs is claimed.

**P(pass), dissent, precedent and RL translation.** The selected pooled confirmation forecast stays .60; do not revise it after these development outcomes. D-061's largest paired teacher lift rule is accepted, even though comparisons use different target populations. The present request is to implement its specified support and complete inventory, not redesign selection. Shared support and paired resampling are the same methods already used for the accepted R2 result checks. Observation/action/value: no added actor input or reward; evaluation metadata determine which demonstrations and independent series justify advancing a policy. Wrong teacher support answers a different imitation question even if predicted actions and interval arithmetic are correct.

## Revision 6 and new inputs — 2026-10-04 22:25 UTC

**PASS for the previously identified teacher-support repairs; final selector release still HOLD for one new D-063 inventory omission.** Audited battery SHA `3f56b4b262f3b137ad87d8bba47b856961ab165e7acc0877f2963c15a4ad69bd`. Main's current source is an uncommitted owner revision; this pass applies to the exact hash, not a branch name.

The independent round-10 probes, adapted only for the new required A0 rating-order metadata and waiver argument, now refuse all twelve malformed cases: NaN, infinity, non-unit sum, negative probability, pooled subset, duplicate keys, changed labels, changed folds, changed series, A6 wrong teacher, A7 partial support and unjustified A2 exclusions. A full A7 alone stays INCOMPLETE; a complete fixed teacher inventory advances. A separate positive control accepts exactly 25 genuinely unsupported A2 team/fold rows being excluded from 100, while one extra excluded row refuses. This closes all four prior teacher-path blockers. CNN resume checks already recorded are not repeated. No real selection run occurred.

**Remaining omission:** D-063 §C adds the full-data `A10b` arm to pooled selection, but `POOLED` and `PLANNED` still omit it. An invented complete old inventory with every pooled candidate at .80 and full-data A10b at 1.00 selects A10-e4 and marks A10b non-pooled. Add the exact full-data A10b candidate to both eligibility and required inventory. Keep learning-curve arms A10b-f25/f50 descriptive: simply adding the A10b prefix to POOLED would also admit those diagnostics, since the selector splits names at the first hyphen. Use explicit eligible candidate identities or manifest roles and refuse a missing declared full-data arm. This is the only new selection release request; do not refit completed arms or rerun previous repair probes without a source change.

**HB-1 export replication PASS for keys/support and file integrity.** Manifest `e38d0667842070615ef46b65489c0feebf84c3954b6fac596db0b9dd0283b663`, 118 shard hashes independently verified. Exactly 235,798 unique five-part keys equal the two original dev120 shards; blocks_src/y_kind/y_first agree on every row. There are 189,630 oracle move rows, 188,250 F/R/L rows, 270 finite HB feature columns on those oracle moves, and finite nonnegative three-way priors summing to one within printed rounding. A0 argmax accuracy independently equals **.69765737** on those 188,250 rows, descriptive only. The exporter/engine parity experiment is Data's evidence, not rerun here. This does not permit training on the 40,444 rebuilt rows or grant a completed battery PASS.

**A10b and curve replicated:** same complete keys, labels, folds and series as A3/A10, post-m2, 14 training maps / 97 games / 49 series / 10 teachers, 188,250 F/R/L rows. Accuracy .64187517 at quarter, .65815139 at half, .67845418 [.66942855,.68746789] at full. Full-minus-half +.02030279 [.01739914,.02360064]; A10b-minus-A10 +.00576892 [.00296744,.00812881]; A3-400-minus-A10b +.03601062 [.03263611,.04033248]. Central 90% whole-series bootstrap, 1,000 draws, seed7, linear percentiles. These reproduce the published figures without fitting. Four doublings to projected parity is an extrapolation, not a measured forecast interval or authority to fit the full corpus. The larger CNN slope also uses a changed inner-validation allocation versus the earlier weighted-tree curve; it is not an isolated architecture treatment effect.

Shared `.60` selected-pooled confirmation forecast unchanged. D-063 allows A10b and adopts tree distillation for P-7; no confirmation label or LS-1 outcome was opened. Receipts, snapshots and independent helper in `tanaka-round11/` and `tools/tanaka/round11_audit.py`. RL translation: exact teacher/key support now protects demonstration comparisons; candidate-role metadata must likewise distinguish a deploy candidate from a learning-curve diagnostic.

## Revision 7 release audit — 2026-10-04 23:22 UTC

**Selector implementation PASS**, pinned to `tools/hinata/r2_battery.py` SHA-256 **af1c87e0d4de7dc2b1cc16783b037edbad184420ea4211b88d7ffec267428207**, with shared loader `a31faa5d8ea31652674b993c77d7549d978437b2226f7e659d7004fa76036427`. This closes the outstanding A10b eligibility/inventory defect and verifies the new D-064 teacher eligibility rules. This is a software release, **not** a numerical battery PASS, final selection, held-out confirmation claim or deploy approval. Final selection still requires the declared complete inventory, Data-supplied cohort-series metadata and D-064's full-row comparisons/fold declaration. No real table was executed.

Independent synthetic checks (100 invented development rows, four teachers, ten series; no field inference):

- Complete pooled inventory at .80 with full-data A10b at 1.00 selects A10b; missing A10b is INCOMPLETE.
- Perfect A10b-f25 and A10b-f50 remain descriptive and cannot replace the missing full-data A10b.
- Undeclared A10b-f75 and A3-200 refuse.
- A7fix alone has no teacher-specific candidate, as D-064 requires.
- A2's highest-lift teacher is excluded with six cohort series and admitted at exactly ten and at twelve. Missing cohort-series input blocks teacher-specific advancement even when A6 has a positive lift.

Eleven cases passed. Prior finite, support, metadata, structural A2-exclusion and inventory regressions were verified at revision 6; those unchanged guards were source-inspected, not needlessly rerun. D-064's restriction removes A7 from the required teacher inventory, leaving A2/A6. No Chair waiver was supplied in these checks. The audited source is currently an owner working revision on MAIN; release attaches to the exact hash, not a later changed file.

**Independent label-free cohort census:** projected only `game, series_key, teacher_sides, team_a, team_b` from frozen cohort SHA `a5e81fd728e2d9f177c9eb2a18e7e3717c91e33a0ba1dbee2eb4548359a4aa2b`. No action, winner, encoder or reward column was loaded. Counts reproduce Data's published census:

| Team | Unique series | A2 eligibility under D-064 |
|---|---:|---|
| 19 | 6 | descriptive |
| 213 | 14 | eligible |
| 264 | 11 | eligible |
| 306 | 8 | descriptive |
| 507 | 9 | descriptive |
| 55 | 10 | eligible |
| 566 | 7 | descriptive |
| 842 | 6 | descriptive |
| 91 | 6 | descriptive |
| 952 | 16 | eligible |

Top-three union (91,306,264) = **29 games / 25 distinct series**, not the sum of individual counts. `tanaka-round12/cohort-series.json` is the independently reproduced ten-team mapping for comparison with Data's supplied selector input. Exact census, no statistical interval. The 115-game/85-series cohort remains frozen; no resampling or redraw.

The completed full-teacher build and manifest are acknowledged as Data's evidence (3,415,158 rows, 2,753,685 oracle F/R/L moves); this wake did not independently rescan that 2.2GB build or fit it. Source identity and eligibility checks do not establish the power of a ten-series gate. Original pooled confirmation forecast **.60** stays unchanged. RL translation: candidate identity and demonstration support now match the approved experiment; confirmation continues to judge whether the selected policy generalizes.

Receipts and pinned sources: `tanaka-round12/`; helper `tools/tanaka/round12_audit.py`. Single-worker nice10, about two seconds, disk270GiB free. No bot run, training, live input or held-out label read.
