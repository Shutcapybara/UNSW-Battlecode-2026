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
