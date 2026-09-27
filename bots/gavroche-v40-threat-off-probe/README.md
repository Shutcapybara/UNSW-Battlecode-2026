# Gavroche V40 threat-map CPU probe

Parent: Gavroche V36. This diagnostic disables only `tx.threat_map()` in
`main.py`; the 0–4 score is expected and has no strategic meaning. It isolates
whether full enemy reach-map construction accounts for the saturated CPU peaks.

The paired four-game sandbox run finished without faults. Candidate p99/max was
50.3–53.0M / 76.7–85.5M on Big Empty and 60.4–61.5M / 82.4–86.7M on Trauma.
The peaks still exceed 80M and both Trauma p99 values exceed 60M, so removing
the threat map does not clear the CPU gate. Continue profiling visible-body
state sensing, especially the vacancy-chain pass.

Run: `experiment_data/gavroche-v40-threat-off-probe_20260927160000000000`.
