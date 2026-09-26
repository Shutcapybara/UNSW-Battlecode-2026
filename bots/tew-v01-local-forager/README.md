# tew-v01-local-forager

Lineage: Tew. Parent: `examples/bahamut-scaffold/` (new scaffold). Borrowed components: none.

Hypothesis: a light local policy that prioritizes immediate pearl growth, open exits, and anti-dither visitation can outperform the scaffold while remaining cheap. It uses visible one-step safety checks and does not yet model portals or long routes.

Implemented: instance-local visit memory; local tile/body state; cardinal action generation; immediate pearl preference; rough exit-space scoring. No sonar reports or splitting. Edge tokens are required to be `.` for a candidate step.

Comparison configuration/run and measured results: pending.


## Measured results

Native comparison, `experiment_data/tew-v01-local-forager_20260925042755877139` (the preceding attempt failed during cache setup and is excluded): 0–0–8, no runtime faults. It lost 4 games each to `ouroboros-v10-beacon` and `hunter-v20-portal-scouts`, on `default_small` and `arena`, both sides. No sandbox checks. The greedy local policy is retained only as the Tew baseline.
