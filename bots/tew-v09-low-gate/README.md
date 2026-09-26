# tew-v09-low-gate

Lineage: Tew. Parent: `tew-v08-early-hunter`; strategy base: Ouroboros v13 ladder.

Hypothesis: v08's 2–2 versus hunter-v20 (both wins on Arena, both losses on default_small) may come from the lower attack gate or the relaxed risk limit. This ablation keeps `ladder_attack_units=2` and restores `ladder_risk_max=1.0` to isolate the gate.

Comparison: native, `default_small` and `arena`, both sides, versus v07 and hunter-v20. Pending. No judge CPU validation.


## Measured results

Native comparison `experiment_data/tew-v09-low-gate_20260925045012194719`: 3–0–5 across 8 games, no runtime faults; 2–2 versus v07 and 1–3 versus hunter-v20 on `default_small` and `arena`, both sides. Restoring the original risk veto while keeping the lower attack gate performed worse against hunter-v20 than v08 (1–3 vs 2–2); no evidence supports adopting the lower gate alone. No sandbox checks.
