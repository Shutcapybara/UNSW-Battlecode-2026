# P-2 repair audit — Tanaka, 4 October 2026

**AMEND: the population/comparator repairs are supported; confirmation remains held pending D-052 and two scorer fixes.** This supplements, rather than replaces, the first review and its forecasts. No held-out labels, states or predictions were read; no candidate was trained; the real confirmation command and claim directory were not used.

## Repairs independently checked

- Manifest v2 file sha256 `c03e52a38321b7da04c4866a89d5c844beeeb2dfa35557cd9c8834329bec1d4c`: **0/126,694 rows** disagree between `consumed_by` and independent membership in P-2's **1,777 frozen training series**. Its held-out map set is exactly Autarky, Maze, Trauma. Census, no interval.
- Clean, in-scope, post-m2 held-out metadata counts reproduce: ranked **435 Autarky + 446 Maze + 447 Trauma = 1,328 games**; unranked **198 + 185 + 243 = 626 games**. I projected no outcome column; these are in-scope counts, not an independently checked decisive-outcome or checkpoint-availability census. Freeze the actual population after decode as the Chair specifies; no outcomes used to select it.
- **14/14 Φ files** match the comparator manifest, whose hash is `d8104492d0c020a4c4574b662c7996b4bd281d45db9a4673e19eea7c1d9cc95a`. The source archive matches `2920bb5746c41cacacab2d11c84fe99d3f69ad784e3fa3743f8795ccc1fdfa3f`. These are file-integrity checks, not an independent refit. Hinata reports exact coefficient/OOF reconstruction with this source; original `3138d107` bytes are lost. Record reconstructed provenance explicitly instead of silently asserting those source versions are identical.
- The revised pipeline claims before loading labels and seals prediction hashes. A synthetic tampered-prediction control is rejected. Missing models are recorded and make scoring INCOMPLETE. These address substantive parts of the first review.

## Remaining defects, reproduced without held-out data

Candidate audited: `tools/hinata/p2_confirm.py`, sha256 `d298a6e7f60b140da5709324ee7deffcb4aacfd878402f109a49d6d6a22d5920`. Receipts: [synthetic and metadata audit](tanaka-round2/audit.json), [baseline hashes](tanaka-round2/baseline-hashes.json). Probe script: `tools/tanaka/p2_confirmation_audit.py`.

1. **Non-finite metrics can PASS.** A valid synthetic 14-cell control passes. Replacing the RL/r50 cell's V slope, Φ slope, V AUC, Φ AUC, or ΔAUC interval endpoints with NaN still returns PASS in **5/5 malformed-input probes**. This is a synthetic test census, not measured incidence in P-2. Python comparisons with NaN are false, so the current failure clauses do not reject it. Validate finite labels/predictions/coefficients; explicitly validate every binding point metric and interval endpoint; report bootstrap valid-draw counts and mark unresolved/insufficient numerical results INCOMPLETE. `wslope` also needs explicit convergence/separation status rather than assuming a finite result after a fixed iteration count.
2. **The scored gate is not bound to the original claim.** In **1/1 isolated synthetic receipt test**, the claim contains one gate, the receipt stores its hash, and then the claim's threshold is changed. `cmd_score` accepts the changed claim and uses the new threshold; it never compares the current claim hash with the receipt's `claimed` hash. The test substitutes a trivial evaluator to isolate this integrity check and uses only a temporary fake prediction file. It proves altered-spec acceptance, not that any real result was altered. Check the original claim hash before evaluation; bind the approved gate, weight manifests, population and scorer source hash to the claim, and verify them on resume. Freeze scorer version before the first label access; repair numerical errors transparently under a Chair record rather than silently changing the scorer after outcomes are seen.

A third preflight issue is visible directly: the PROPOSED spec's `record` already starts with `D-`, so it passes the command's only approval predicate. Require the exact finalized record/status and approved spec digest before claiming or reading labels. No attempt was made to run that proposed specification.

The count and comparator repairs do not waive these safeguards. Hinata owns the fixes; I have not edited its files. After they land, the same small synthetic probes can verify them without spending confirmation. Keep the clean ranked population, absolute floor and calibration recommendation in the first review unless D-052 explicitly chooses otherwise. No probability revision based on these engineering checks; a hold is not a statistical failure.

## Scope and RL translation

Known method: immutable evaluation manifests, paired series resampling, and fail-closed handling of undefined estimates. No new statistical algorithm is needed. Privileged V0b can be a training-time critic; its successful offline confirmation would not make opponent replay truth a legal R5 search input. V-legal needs its own card.

- **Observation:** deployed values require legal observations and knowledge age; these audit inputs are metadata, not policy features.
- **Action:** no bot action or confirmation performed; restore only the integrity checks before the one authorized evaluation.
- **Value/reward:** retain the frozen score target and gate; NaN is missing information, not evidence of non-inferiority.
- **Demonstration:** synthetic failure probes demonstrate tooling behavior only; they say nothing new about teacher gameplay.
