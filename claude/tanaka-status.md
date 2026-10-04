# Tanaka — Phase 3 council auditor

Updated: 2026-10-04 12:02 UTC. State: **round 1 reviews complete; awaiting Chair D-051 and data/provenance remedy before confirmation**.

## Ownership and cadence

- GPT council auditor, assigned by the user; branch `r/tanaka`.
- Worktree: `/Users/alik/.codex/worktrees/tanaka-council/UNSW-Battlecode-2026`.
- Hourly heartbeat: `tanaka-hourly-council-review`, active in this chat. Each wake performs useful new audit work, then yields. No repeated unchanged analyses or user alerts.
- Main read/fast-forward base: `0b5a953a0`; charter D-046, corrected held-out maps D-049, operational choices D-050 §8. Earlier D-045 numbering/gate/runtime/training-entry request resolved.
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

## Next wake

Read D-051/new decisions and acknowledgments first. Do not consume confirmation data, repeat this audit or silently refit the candidate. Check Data's consumed-series ledger, Hinata's frozen comparator/source, and Live ops' snapshot/outcome fixes if delivered. Review any new assigned card; otherwise remain quiet. Commit only lane artifacts and request `push_branches` through the keeper when no request is pending.
