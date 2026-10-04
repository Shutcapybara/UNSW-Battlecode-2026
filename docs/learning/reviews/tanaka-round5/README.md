# Tanaka round 2 review receipts (fifth wake)

`audit.json` records independently computed teacher/split metadata overlap, smoke labels/provenance, prototype loader checks, P-2 row-key alignment and memory arithmetic. Confirmation projections contain identifiers/team/map/split metadata only; no held-out outcome or action label was read. Smoke labels are already authorized development plumbing inputs.

`resume-audit.json` demonstrates stale cached-model registration using a fake LightGBM module and two invented games. No model is actually fitted. `r2_bc_snapshot.py` pins the audited source8af15d01.

Reproduction: from the shared main checkout, use its .venv/bin/python with nice10 and BLAS threads1 on tools/tanaka/round2_data_audit.py and r2_resume_audit.py in Tanaka's worktree. Outputs are /tmp/tanaka-r5. The metadata helper covers the base checks; supplemental key-alignment and column-guard checks are incorporated in the committed helper. Paths are explicit local data sources; no helpers modify owner data or invoke a confirmation.
