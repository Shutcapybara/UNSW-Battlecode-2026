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
| 04a-sparsewide | L02/L03: widen the target search to 1,280 nodes when the previous search met no pearl or bed; replaces the parent's round rules (the r40 late cap never binds, min(160, 384) = 160) | L02, L03 | **−0.043 [−0.072, −0.005]** (seed 1, 160) | not run | +0.013 / −0.080 / −0.056 / −0.047 | −0.036 [−0.080, +0.018] / −0.002 [−0.054, +0.036] | all ±5 % | – | REJECT (screen: negative) | Sparsity-triggered wide search sends empty-handed dragons after distant targets; Schooltime −0.18, Trophy −0.17, Trauma −0.12. Lune's opening harm reproduces at every phase when the trigger is "found nothing". Also: Lune's late cap ×8 is effectively 48 → 160, not 384. |
| 05a-yield | Asymmetric yield: a visible ally head that can step into my first cell → higher id takes −4, lower id drops the crowd term | L05, L29 | −0.022 [−0.049, +0.022] (seed 1, 160) | not run | −0.014 / −0.039 / −0.038 / +0.004 | +0.000 / +0.040 [−0.029, +0.067] | wall −4 %, self −4 %, ally body −6 %, ally h2h −5 % | – | REJECT (screen) | Win +0.044 [−0.013, +0.100], but the target (ally h2h) moved −5 %: visible contests are not where ally head-on happens (see anatomy below). |
| 05b-yield-flat07 | STACK: 05a on 02b | L29 | +0.085 [+0.050, +0.143] vs 01; vs 02b −0.001 | not run | +0.094 / +0.118 / +0.077 / +0.052 | +0.019 / +0.028 | vs 01: ally h2h +31 %, self +11 %, wall +10 % | – | REJECT (guards) | Yield removes only 3 % of the flat cut's ally h2h. |

**Ally head-on anatomy** (`tools/rc/h2h_anatomy.py gustave-02b-flat07`, 160 games, 2,204 collisions): every one of
our ally-h2h deaths has `near_portal` true (Portals map 41 %, 42 % newborns). Of the 1,830 with known geometry, 98 %
are the mover crossing a paired portal blind and landing on an ally head out of its view: the ally had walked onto
the exit mouth earlier in the same round (50 %) or was standing on it (31 %). The ally was heading into the portal
(queueing to cross the other way) in ~21 % of all collisions and *not* heading in (passing or loitering on the mouth)
in ~61 %. Visible contests (05a's target) are ~1 %. → 07a (mouth occupancy rule).
| 06a-bedguard | L11: wait ≤ 8 on a ripening bed only if ≤ 2 known beds within Manhattan 8 and no enemy head within 4 | L11 | +0.000 [0.000, +0.004] (seed 1, 160) | not run | 0 / 0 / 0 / 0 | 0 / 0 | ±1 % | – | REJECT (inert) | Key on in 6 % of decisions (instrumented: 61 % see ≥ 11 beds within 8). 159/160 fixtures identical except Schooltime. → 06b at ≤ 6 beds (~27 %). |
| 07a-mouthclear | −1.5 for ending on a known-paired portal mouth unless crossing or just arrived | L23, L05 | +0.005 [−0.013, +0.029] (seed 1, 160) | not run | 0.000 / −0.020 / +0.036 / +0.005 | **+0.054 [−0.010, +0.089] / +0.040 [−0.009, +0.062]** | ally h2h 2.62 vs 2.60 (0 %), rest ±1 % | – | REJECT (screen: target unmoved) | Anatomy: mouth loitering (walked on, not heading in) −11 %, but crossing-queue collisions +32 %; total 1,744 vs 1,725. Convoy ruled out (victims walked the round before, 97 %). Units/length/win (+0.025) lean positive. → 07b (weight 4, any portal edge). |
| 06b-bedguard6 | 06a with the sparse key at ≤ 6 beds within 8 (~27 % of decisions) | L11 | −0.016 [−0.038, −0.001] (seed 1, 160) | not run | 0 / −0.019 / −0.033 / −0.011 | −0.036 / −0.016 [−0.071, −0.002] | nb10 +2 % | – | REJECT | Widening the key turns the guard into Renoir's flat wait (Autarky −0.07); Schooltime +0.15 the only gain. L11 closed for this lane. |
| 07b-mouthclear4 | 07a at weight 4, any portal edge counts | L23, L05 | **−0.128 [−0.209, −0.058]** (seed 1, 160) | not run | −0.107 / −0.153 / −0.164 / −0.087 | −0.009 / −0.011 | **ally h2h −71 % (2.60→0.75)**, ally body −21 %, wall −16 %, self −7 %, nb10 35.5→31.7 | – | REJECT (economy) | The mouth *is* the ally-h2h channel (−71 %), and win +0.044 [−0.031, +0.106]; but it taxes legitimate crossings that need a turn on the mouth: Portals −0.69, Trauma −0.34, Schooltime −0.31. → 07c exempts mouths on the dragon's own route. |
| 07c-mouthroute | 07b + route intent: a mouth the dragon's route to its target crosses within 3 steps is exempt | L23, L05 | +0.001 [−0.017, +0.018] (seeds 1–3, 480) | −0.005 [−0.012, +0.004] (744) | −0.006 / +0.011 / −0.019 / +0.018 | −0.029 [−0.058, +0.008] / −0.032 [−0.056, +0.004] | **ally h2h −18 % pool, −23 % gen**; rest within ±4 % | 8.72 M (08b probe, same rule) | **HOLD (confirmed at full gate)** | Hygiene-only, economy flat on both panels. **Gen win +0.022 [+0.001, +0.043]** and gen units +0.027 [0.000, +0.050]; pool win +0.025 [−0.008, +0.058]. Pool units/length lower bounds miss −0.02. Queued for stacking on the next accepted economy change. |
| 08a-mouth-flat07 | STACK: 07c (HOLD) on 02b's ×0.70 value cut | L14, L29, L23 | **+0.032 [+0.006, +0.056]** (seeds 1–3, 480; seed 1 alone +0.071) | **+0.027 [+0.012, +0.047]** (744) | +0.047 / +0.058 / +0.021 / +0.003 | **−0.046 [−0.108, −0.017]** / −0.032 [−0.056, +0.004] | wall +11 %, ally h2h +10 %, self +8 %, ally body −2 %, nb10 35.6→38.2 | pending | **REJECT** (units, length, win −0.024 [−0.062, +0.018], wall) | Economy is real and generalises (gen lb +0.012, gen units/length/win flat), but the pool pays in retention: fewer dragons at r100. The mouth rule held ally h2h to +10 % (cut alone +35 %). Devil −0.23 without the 32×16 terms. |
| 08b-mouth-flat08 | STACK: 07c on a ×0.80 cut | L14, L29, L23 | +0.009 [−0.019, +0.036] (seeds 1–3, 480; seed 1 alone +0.027) | +0.010 [−0.002, +0.028] (744) | −0.020 / +0.027 / +0.008 / +0.019 | +0.000 [−0.048, +0.027] / −0.021 [−0.043, +0.024] | ally h2h −8 %, wall +5 %, self +4 %, ally body −8 %, nb10 +4 % | 8.72 M | **REJECT** (econ, units, length lb) | Hygiene-clean and neutral: the ×0.8 cut with the mouth rule buys nothing measurable on either panel. 08a/08b bracket the trade: the cut's economy comes with its retention cost. |
| 09a-portalintent | Stateful portal intention on 07c: commit to the route's mouth, keep immunity for 6 rounds after the route last crossed it, clear on crossing | L30 (proposed), L23 | vs 01: −0.005 [−0.030, +0.033]; **vs 07c: −0.005 [−0.027, +0.013]** (seed 1, 160) | not run | vs 07c: −0.006 / −0.010 / −0.010 / +0.004 | vs 07c: +0.018 / +0.009 | vs 07c: **ally h2h +11 %** (2.06→2.30); vs 01: ally h2h −12 % | – | REJECT vs 07c (HOLD vs 01) | Persistence adds immunity without economy: 07c's per-turn route exemption had already removed the transit tax (07b→07c), so the extra immune rounds are loitering. Win vs 01 +0.056 [0.000, +0.113]. Statefulness is not the missing piece for the portal case; L30's general layer (commitments with abandonment rules) stays proposed for the next phase. |

## State at end of phase (30 Sep, 17:55 ACST)

- Accepted stack: `gustave-01-nodevil` (nothing has passed D-032).
- HOLD: `gustave-07c-mouthroute`, confirmed at seeds 1–3 on both panels. The first mechanism in the programme to
  measurably cut a self-inflicted death rate off-pool without an economy cost.
- Economy lever on record: the exploration/bed value cut (02b; = sciel-03a). Its economy generalises (08a gen +0.027
  [+0.012, +0.047]), but it costs pool retention even with the mouth rule; the ×0.8 point is neutral (08b).
- Proposed for the next phase: L30, a stateful intention layer (09a showed a portal-only commitment adds nothing on
  top of 07c).
