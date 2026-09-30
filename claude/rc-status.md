# R-2c `rc` status — Gustave lineage (Claude Opus 5.5, desktop)

Lane brief: `docs/hub/prompts/2026-09-30-R2c-open-lane-guided.md` (the director renamed the lineage from Cézanne to
**Gustave**: bots `bots/gustave-<nn>-<slug>/`, `lineage = "gustave"`). Branch `r/rc`, worktree `../wt-rc`,
tools `tools/rc/` (copied from `tools/ra/` and `tools/lune/score.py`; scoring logic unchanged, gate replaced by D-032).

## Base

- `gustave-00-base` = `lune-r1-07-latecap8x-only` verbatim. Golden parity against lune-r1-07's own transcripts
  (seed 1 vs yuna-v05-core): schooltime-A 17,210 turns / 310 dragons, devil-B 5,519 / 213, trauma-B 5,847 / 98 —
  **0 divergent**. Fingerprint `9fbac543…f320`.
- `gustave-01-nodevil` = 00 + `Params::shape_terms=false` (D-033: `devil_center_bonus`, `devil_lane_bonus`,
  `ally_body_buffer` inactive). Golden vs the same transcripts: schooltime-A and trauma-B 0 divergent, devil-B
  358/5,519 divergent (the 32×16 terms only). Fingerprint `c882651b…91a8`. Parent of everything after.

## Gate (D-032, `tools/rc/lane.py score`)

Paired fixtures (seed, map, opponent, seat), seeds 1–3, pool (`run_panel.ZOO` × 10 live maps × 2 seats = 160/seed)
+ generalisation panel (4 opponents × 31 off-pool maps × 2 seats = 248/seed); 1,000-draw paired bootstrap, 90 %
intervals. Accept: pool Δecon~ lb > 0; gen Δecon~ lb > −0.02; units@100 and length@100 lb ≥ −0.02; no tier-2 mean up
> 10 %; pool win lb > −0.02. econ~ = mean over r50/100/150/250 of the per-checkpoint medians of pearls ÷ field
per-map median (pool) or ÷ renoir-00's per-map medians (gen, `tools/rc/gen_reference.json`, frozen).
`--phase late` scores p@150/p@250 with p@50/p@100 as guards.

## Running table

| Version | Mechanism | Ledger | Pool Δecon~ [90 %] | Gen Δecon~ [90 %] | Per-checkpoint (pool p50/100/150/250) | units / length@100 | Tier-2 | CPU max | Verdict | Why |
|---|---|---|---|---|---|---|---|---:|---|---|
| 02a-sciel03a (diag) | sciel-03a verbatim on gustave-01 | L12 | **+0.090 [+0.044, +0.143]** (seed 1, 160) | not run | +0.111 / +0.124 / +0.071 / +0.053 | −0.027 [−0.095, +0.036] / +0.015 [−0.056, +0.046] | wall +13 %, self +14 %, ally body +18 %, **ally h2h +34 %**, nb10 35.5→38.9 | – | REJECT (replication) | Replicates Sciel-03a on the D-033 base to the digit (Sciel: +0.067, h2h +34 %). Guards kill it. |
| 02b-flat07 (diag) | control: 03a's factor clamped to 0.70 (no memory) | L12 / L14 | +0.087 [+0.050, +0.136] vs 01; **vs 02a: −0.003 [−0.020, +0.023]** | not run | vs 02a: −0.010 / +0.003 / −0.007 / +0.001 | vs 02a: −0.009 / +0.000 | vs 02a: all within ±4 % | – | DIAGNOSTIC | **Sciel-03a is a flat ×0.70 cut on unseen and bed values, not a density memory.** Instrumented: 95.5 % of 1.54 M factor evaluations are exactly 0.70, 4.5 % in 0.71–0.9, none > 1 (the kernel density rarely leaves 0 against ref 0.5). The flat control reproduces 02a on every metric (92/160 fixtures identical pearls@100). This is Renoir's 07a/07c exploration-value lever (churn: ally h2h +35 %). Sciel's proposed 03b fix (shrink the factor's departure from 1 near allies) would *raise* values near allies, i.e. increase crowding. |
| 03a-ewbonus-w3 | L12 density term itself: bonus only (ref 0, floor 1, cap 2, weight 3) + ally-saturation discount on the bonus | L12 | +0.008 [−0.025, +0.035] (seed 1, 160) | not run | +0.002 / +0.016 / −0.013 / +0.025 | −0.036 [−0.080, +0.033] / +0.010 [−0.038, +0.052] | all within ±3 % | – | REJECT (screen: flat) | The density memory, measured on its own, does nothing: 94.8 % of evaluations at 1.0, 5.2 % in (1, 1.5]; closed loop flat on every metric. Stopped at the screen (interval centred on 0). |
| 03b-ewbonus-w6 | same, weight 6 | L12 | −0.005 [−0.029, +0.030] (seed 1, 160) | not run | +0.001 / −0.030 / −0.003 / +0.011 | −0.036 [−0.089, +0.028] / +0.008 [−0.051, +0.026] | ally h2h +6 %, rest ±3 % | – | REJECT (screen: flat) | Doubling the weight does not move it either. L12's only positive evidence was the flat cut (02b). |
