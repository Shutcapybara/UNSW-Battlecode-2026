# Tanaka — Phase 3 council auditor

Updated: 2026-10-04 12:53 UTC. State: **repair audit complete; awaiting D-052 and confirmation-scorer fixes**.

## Ownership and cadence

- GPT council auditor, assigned by the user; branch `r/tanaka`.
- Worktree: `/Users/alik/.codex/worktrees/tanaka-council/UNSW-Battlecode-2026`.
- Hourly heartbeat: `tanaka-hourly-council-review`, active in this chat. Each wake performs useful new audit work, then yields. No repeated unchanged analyses or user alerts.
- Main read/fast-forward base: `8988d9489`; charter D-046, corrected held-out maps D-049, operational choices D-050 §8. Earlier D-045 numbering/gate/runtime/training-entry request resolved.
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

## Next wake

Read D-052/new decisions and acknowledgments first. Do not consume confirmation data, repeat this audit or silently refit the candidate. Check Hinata's finite-metric, immutable-claim and approved-spec repairs with synthetic inputs only; verify Live ops' snapshot/outcome fixes if delivered. Data's v2 consumption tagging and comparator file integrity are now independently checked. Do not repeat those checks without new inputs. Review any new assigned card; otherwise remain quiet. Commit only lane artifacts and request `push_branches` through the keeper when no request is pending.
