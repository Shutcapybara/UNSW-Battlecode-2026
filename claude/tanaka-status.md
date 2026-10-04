# Tanaka — Phase 3 council auditor

Updated: 2026-10-04 16:57 UTC. State: **P-2 rev3 missing-result HOLD; P-5 engineering repairs verified; D-055 pending**.

## Ownership and cadence

- GPT council auditor, assigned by the user; branch `r/tanaka`.
- Worktree: `/Users/alik/.codex/worktrees/tanaka-council/UNSW-Battlecode-2026`.
- Hourly heartbeat: `tanaka-hourly-council-review`, active in this chat. Each wake performs useful new audit work, then yields. No repeated unchanged analyses or user alerts.
- Main read/fast-forward base: `f9ef84afe`; charter D-046, corrected held-out maps D-049, operational choices D-050 §8. Earlier D-045 numbering/gate/runtime/training-entry request resolved.
- BOARD writes now append only to main checkout per D-050 §8; no branch commits BOARD.
- Project-document mirror remains unavailable: no accessible destination supplied. This file is the status source.

## This unit's completed work

1. **P-2: AMEND/HOLD confirmation.** Independently reproduced all 14 cells' AUCs and game-bootstrap endpoints from frozen OOF (difference <3e-16), slope discrepancy <0.00050; whole-series bootstrap still supports late development gains. No held-out outcomes loaded and no model refit.
2. **New split defect:** frozen 5,799-game post-m2 training artifact includes 539 test-bucket games (173 series) and 555 validation-bucket games (175 series); no held-out-map rows. Development pools 3,427 ranked and 2,372 unranked games. LOMO shares series across fit/scoring in all 96 folds (28,216/35,948 scored game-checkpoint rows). Exact artifact censuses, no statistical interval. Chair/Hinata/Data alerted on main BOARD 11:53Z.
3. **P-2 implementation/provenance:** confirmation refits baseline from growing store, lacks interval gate evaluation, silently skips missing models, and claims completion only after scoring. Frozen registry source hash differs from current source. Review requests frozen comparator, source archive, population separation and atomic complete-cell confirmation before the one shot.
4. **D-048: AMEND to incumbent-relative rollback.** First/last 40 residual summaries independently reproduce; last40 = −0.09296 [−0.18362, −0.00230], 40 ranked post-m2 games / 8 series, central 90% whole-series percentile bootstrap (1,000, seed 7). Original 417-game full-history membership is not recoverable from the grown index; now 596 pre-cutoff games. Derived inputs frozen in the review receipts.
5. **Rollback power:** normal plug-in approximation from eight-series window gives about 25% power for a true −0.08 change under two 40-game windows, versus roughly 48% erroneous rollback for an equally strong candidate under the absolute rule if baseline mean stays −0.09296. These are analytic approximations, not measured future rates. Point threshold limits power at the −0.08 boundary to 50%, even with more data. Synthetic monitor probe finds future-snapshot fallback; unknown winner also maps to draw. Live ops owns fixes.
6. **D-046:** installed/cached 1.2.3 engine hash independently matches charter; cross-wheel 1.2.5/1.2.9 and server replication remain peer evidence. Recommend whole map×opponent clusters keeping both seats and seeds for the first full gate; preserve declared convention if Chair chooses otherwise, with paired-seat sensitivity.

## Deliverables and verification

- `docs/learning/reviews/P-2-tanaka.md`
- `docs/learning/reviews/D-048-tanaka.md`
- `docs/learning/reviews/D-046-tanaka.md`
- `docs/learning/reviews/tanaka-round1/`: hashes, full tables, frozen derived monitor inputs and reproduction instructions.
- `tools/tanaka/p2_audit.py`, `tools/tanaka/rollback_audit.py`.
- Bounded single-worker calculations only; no bot experiment, training, held-out confirmation, upload or activation. Disk checked. Initial sandbox niceness request failed; subsequent jobs ran nice 10. Frozen-data rollback reproduction and Python compilation passed.
- P-2 forecasts (subjective, conditional numerical confirmation with same weights): G-asis .03, G-amend .35, corrected gate .20. Current eligibility HOLD. D-048 .80 for an implementation A/A calibration gate, pending an operationally defined scored event. Full scope, dissent and RL translations are in the reviews.

## Second wake: repairs checked

- D-051 upheld the P-2 hold and requested preparation only; the council decision is now D-052.
- Independently checked v2 consumption tags: 0/126,694 metadata rows mismatch the frozen 1,777 training series. Clean in-scope post-m2 ranked counts reproduce (435/446/447); no held-out outcome projection. All 14 comparator files match manifest d8104492; archived source hash matches 2920bb57. Original 3138d107 is lost; Hinata's exact refit claim remains peer evidence, distinct from my file-integrity audit.
- New p2_confirm.py d298a6e7 synthetic defects: 5/5 malformed NaN metric probes return PASS; 1/1 changed-claim test accepts an altered gate after claim receipt. Changed predictions correctly rejected. Proposed record text satisfies its permissive startswith('D-') preflight. Owner fixes requested on main BOARD; no real confirmation run/claim created.
- Delivered `P-2-tanaka-repair-audit.md`, `D-048-tanaka-followup.md`, round2 receipts and `tools/tanaka/p2_confirmation_audit.py`. Compile and bounded one-worker nice-10 probes completed; disk checked before tests. No forecast changes.
- Rollback follow-up supports a prospective 120-game reference but notes simulation truncates boundary series/uses 200 inner draws and game-time own rating. Different per-window rating anchors create a +0.11968 synthetic difference with identical scores/opponents; recommend one common predeclared own-rating anchor. D-051 dev A/A is not the undefined rollback-calibration event underlying the earlier .80 forecast.

## Third wake: D-052 and cage review

- D-052 decisions incorporated by fast-forward, with prior lane work retained. Chair adopted common rollback anchor and local map×opponent clusters; P-2 r10 and absolute r50 floor report-only. Exact-spec P(PASS) forecast now **0.40**, filed before CLAIM (existence checked only), in `D-052-tanaka.md`.
- No P-2 release: scorer remains d298a6e7 with known defects. Did not repeat unchanged tests or read held-out outcomes. Data reports decode complete and a one-game scope discrepancy; owner reconciliation remains necessary.
- **P-sugawara-01: reject dimension identity gate; amend denominator.** `P-sugawara-01-tanaka.md` cites user hard rule and D-033; 55 map headers independently checked. Read frozen Schooltime seed-1 queen tables: Asahi01 has 4 joint survivors /16 fixtures (15 reach RL), 15 wins; carthage05 0/16,14 wins. Twelve total queen deaths in Asahi01, eleven among RL games. Recommend fixed 16 denominator, paired opponent clustering, diagnosis before any revised card and a lawful structural trigger. No bot built or run. Conditional numerical-support forecast .45 applies only to the original intervention if authorized and cap-death prerequisite holds, not to a replacement.
- Live monitor future-snapshot fix independently passes 4/4 synthetic checks; no claim of D-052 rollback implementation or calibration. Existing absolute monitor and unknown-winner handling not re-alerted as new.
- `tanaka-round3/audit.json` freezes 32 derived Schooltime rows, map headers/hashes and probes; `tools/tanaka/cage_review_audit.py` reproduces them. One-worker nice10, 21 GiB disk available; no heavy job or shared lock needed. Hidden-bed variant reconstruction is now peer-reported blocked; do not substitute approximate variants silently.

## Fourth wake: D-053, revised scorer and two council cards

- D-053 incorporated by fast-forward; previous commit1b6f4e5b2 was merged. R0 passed with stated map-variant limitations, pool remains17maps/136clusters. P-3 rejected and cage work parked; the cap-death diagnosis is dropped. No cage forecast scored.
- P-2 scorer ea3b5ef7 fixes prior finite/claim defects:18/18 malformed-metric probes INCOMPLETE; immutable receipt/spec/scorer/prediction checks and one-score rule verified. Numerical synthetic cell AUC exactly matches independent pair calculation; invalid/one-class/low-valid-draw cases recognized. **New HOLD**: invented frozen excluded game nevertheless predicted by cmd_run (decoded-only filter; mutable store scope). Owner asked to pin usable IDs/checkpoint membership and reconcile actual coverage; no real confirmation/data read. Metadata1319/1328usable,9misses,allmaps>95%, already acknowledged by Hinata. P(PASS)0.40 unchanged. Review P-2-tanaka-release-audit.md.
- D-053 k16 forecast **P(gate PASS on seeds2–3)=0.35**, filed14:51 before card. Independent736seed1pairs: pool+7/272 entirelyWeakhold,gen−1/464. Paired-seat136/232cluster bootstraps: pool[+0.3676,+5.1471]pp,gen[−1.0776,+0.4310]pp. Review P-A02-k16-gate-tanaka.md. No new game or gate outcome read.
- H-KZ26 card **AMEND**, P(support)=0.30 conditional on fixed measurement contract: exact event-time strike labeller, all candidate branches including post-loop splits, paired rate denominators and fixed-fixture survival, explicit food guard/memory semantics/dense-observation CPU. Review P-sugawara-02-tanaka.md. No bot built or run.
- Rollback decision formula independently verified on8synthetic unequal-series datasets (error<=1.39e−17),849/172frozen sequence contiguous. Full Monte Carlo rates remain peer evidence; convention unscored, no repeated request. D-052-tanaka-rollback-audit.md.
- Receipts/source snapshot/736paired rows in tanaka-round4; bounded single-worker nice10 work,20GiB free, no heavy lock needed. New R2 and V-legal cards landed while this audit ran; reserved for the next council review, with no learning or held-out use authorized by this seat.

## Fifth wake: council round 2 complete

- D-054 incorporated; previous87ab8c40f merged. **P-2 scope ruling supersedes the prior decoded-and-live-store filter**: frozen v2 scope plus decode presence binds (1327/1328;1044626missing). Current scorer ea3b5ef7 is unchanged and still reads live scope; no repeat test or duplicate hold notice. Await owner revision that enforces frozen IDs/checkpoint membership and revised counts. P-2 forecast0.40 unchanged.
- P-4 approved with measurement amendments; P(support)=0.30 remains as Chair recorded. K16 gate not yet started in D-054; P(PASS)=0.35 unchanged. Cage stays parked.
- **P-5 AMEND**, delivered P-5-tanaka.md: prefer encoder+explicit HB-1 candidate-feature allowlist, encoder-only paired development comparison, G-parent binding and0.83report. Independently found382/497potential heldout-map metadata games share289teacher training series; only115games/85series clean. Teacher list1925sides/1735games/506series,14maps; LOMO overlap1856/1925sides across14/14folds. No confirmation labels read. Freeze series-clean cohort before fit; no redraw.
- P-5 engineering probes: fake backend confirms old folds reused after changed inputs/400→800rounds with new registry hash and zero new fits. Synthetic identity guard accepts x_W/H/x/y/xn/yn emitted by HB-1 extractor; use allowlist. Smoke all11838rebuild_redacted, but236cd_known1(no visible beds); require actual oracle provenance. Loader retains6200unknown rows/6289teacher moves. Single3M×1193float32matrix13.33GiB beforecopies, not~7GB.
- P-5 forecasts encoder-only / proposedunion: no development falsifier0.60/0.75; G-parent0.50/**0.60**; G-macro0.10/0.25; panelgateatλ1givenofflinepass0.20/0.25. Expectedunionaccuracygain~3pp,poolwin~0.5pp,gen~0; D-055 fixes scored event. Flip rate should remain descriptive, reject unsupported<1%no-panel cutoff.
- **P-6 AMEND**, delivered P-6-tanaka.md: selected-speaker diagnostic only, no causal information-price or guaranteed upper-bound claim; global speaker selection does not generalize to arbitrary actor. Non-significance is not equivalence. PairV0b/Phi/legal on fixedfuturewhole-series cohort; retain developmentfoldoverlap label. FrozenP2 input5799games/71956rows,35978sideAkeys vs35948OOFkeys (30missing); fix cost estimate and explicitkeyintersection. Forecast nofalsifier0.80, legal≥PhiRLr50=0.20, expectedAUCgap~0.07; no fit yet.
- Receipts/source snapshot in tanaka-round5; tools round2_data_audit.py and r2_resume_audit.py. Bounded single-worker nice10,18GiBdiskfree; no heavy work, fit, bot run or confirmation. Daichi's new A/A report is peer evidence:68/136completed,752inactive, floor1/68vs545; Chair disposition pending, no repeated request from Tanaka.

## Sixth wake: revision 3 and round-2 replies

- Main remains f9ef84afe/D-054; no new D-055, registry promotion or gate result. Own1582bb308 not yet in main; preserved own branch without overwriting owner work. D-045 reference conflict remains resolved.
- **P-2 rev3 bb51e1bb HOLD**: frozen scope view repaired; metadata pin22305rows/3305games, binding1327/1328 and all14counts independently match. Synthetic missing store row/null/NaN/invalid result is called an explained nondecisive loss; missing/null/invalid pass real score preflight with mocked passing metrics. Known0.5draw legitimately excluded, decisive loss fails. Request valid-result domain/store presence checks at run and score on BOARD16:55. No real CLAIM (existence only), predictions or held-out outcomes read.18finite cases and989/990boundary still correct; second score refuses. Numerical forecast0.40 unchanged.
- **P-5 rev2 b3ce4789 repairs verified** with fake backend: identical resume works, changed rows/rounds refuse; identity allowlist, missing-feature guard and oracle source filter pass. Author accepts design amendments. Prototype four-class metrics differ from amended FRL-conditional gate: implement named support and freeze development-stop convention in D-055 before fit. Completion/duplicate/fixed-learning-curve requirements remain in original review.
- Development provenance235798rows/118games/52series reproduces97oracle/21rebuilt;3925rebuiltrows have cd_known1. **Zero held-out-map rows**, so their oracle coverage is untested. Live~15%layout prevalence extrapolation not a validated population interval. New BOARD correction/request follows.
- P-6 author accepts diagnostic interpretation, selected-speaker scope and future whole-series separation; review acknowledges, forecasts unchanged. P-5/P-6 authorization awaits D-055. k16 forecast0.35/P-4support0.30 unchanged; evaluator owns runs, no duplicate idle request.
- Appended P-2/P-5/P-6 reviews; receipts/source snapshots tanaka-round6; helper revision3_audit.py. Disk15GiB. Bounded single-worker nice10 successful after sandbox niceness retry; no heavy job/lock, fit, real confirmation or bot experiment. Project-document destination remains unavailable.

## Next wake

Read status/STOP and fresh Chair/BOARD first. Await P-2 source change fixing unknown-result membership, then audit exact scorer/spec hashes with synthetic inputs; never run real confirmation. D-055 should freeze P-5 gate support/development stop, series-clean cohort and oracle coverage before fit, plus P-6 rules. No repeated tests or requests for unchanged source. Preserve all forecasts until exact scored-event ruling/results. Commit own lane only; MAIN BOARD append-only and keeper push only when absent. Mirror remains unavailable.
