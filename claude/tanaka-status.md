# Tanaka — Phase 3 council auditor

Updated: 2026-10-04 13:53 UTC. State: **D-052 read; cage card rejected as written; awaiting scorer repair**.

## Ownership and cadence

- GPT council auditor, assigned by the user; branch `r/tanaka`.
- Worktree: `/Users/alik/.codex/worktrees/tanaka-council/UNSW-Battlecode-2026`.
- Hourly heartbeat: `tanaka-hourly-council-review`, active in this chat. Each wake performs useful new audit work, then yields. No repeated unchanged analyses or user alerts.
- Main read/fast-forward base: `2af0e07cd`; charter D-046, corrected held-out maps D-049, operational choices D-050 §8. Earlier D-045 numbering/gate/runtime/training-entry request resolved.
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

## Next wake

Read status/STOP and fresh Chair/BOARD changes first. Audit Hinata's repaired scorer only after source changes, with synthetic inputs and exact D-052 hash, finite metrics, valid bootstrap counts, claim/scorer binding, coverage and predeclared cell roles. Post an explicit hash-specific release PASS only when justified; do not run confirmation. Review a revised structural reserve card and Asahi's cap-death diagnosis when available. Verify Daichi's exact-rule calibration after it lands, without repeating old requests. Commit lane artifacts only; append new findings to main BOARD and request a keeper push only if no request is pending. Project-document mirror remains unavailable.
