# Faye: cohort strategy exploration

Lineage owner: GLM. Started 2026-09-27. Brief: `docs/COHORT_STRATEGY_EXPLORATION_PROMPT.md`.
Faye works cohort-level questions: transfer of diagnosed mechanisms across the map
suite, coverage of the synthetic half of the evaluation target, and cross-lineage
evidence reconciliation. Each cycle gets an immutable record under
`experiment_data/cohort_research_<stamp>_faye/cycle_*/`.

## Cycle ledger

| Cycle | Question | Verdict |
|---|---|---|
| 001 | Does the compact-contact doctrine (newton n10) transfer to the synthetic renewable-contest motifs, and is the v13 leak cohort-wide (serre) or fafnir-specific? | **UNRESOLVED per frozen rule** (n10 net +2, 1/4 commons flips, 1 regression; doctrine fires r24–64 in-scope, action-identical out-of-scope). Primary asset: v13 snowball-or-stall bistability — family 15–0 vs stalled v13, ~0–11 vs snowballed. serre 8–4: leader exposed but sturdier. |
| 002 | Is the snowball bistability v13-specific or shared by the churn class (tew-v12)? | **MIXED per frozen rule, strong qualitative match**: fafnir 7–5 vs tew (threshold was ≤6–6), but all five losses are snowball cells with tew at u25–60 by r100–200 and identical loss geography to v13. Leak is churn-class-shaped with per-opponent intensity differences; F-002 mechanism should condition on observed snowball dynamics, not opponent identity. |

Next queue: F-002 snowball survival/prevention mechanism (fork `faye-x01` from serre-v01,
instrument decision-path first), F-004 ledger-publication decision for the 64 archived
validation fixtures (owner call). Full detail in the workspace SYNTHESIS.md.

## Standing observations (accumulating)

- 2026-09-27: the map-suite validation batch (`experiment_data/map_coverage_20260927_091715`)
  contains 64 never-published fixtures on all 20 synthetic maps with frozen release sources
  (fafnir-v01 anchor vs ouroboros-v13 / valjean-v01 / von_neumann-x06). Observed records:
  fafnir–v13 16–10, fafnir–valjean 12–14, fafnir–vn-x06 4–8. The v13 losses concentrate on
  the renewable-contest/gate motifs: commons_shared 0–2, commons_spread 0–2, causeway_portal
  0–2, spring_wells 1–1, delayed_commons 1–1; fafnir sweeps crossroads, equatorial_belt,
  portal_quartet, scattered_fleets, orchard_narrow, promenade_ring. None of these games are
  in the shared ledger, so every active bot's synthetic-map rating cell is model completion.
- Tile geometry: commons maps 480, spring_wells 572, delayed_commons 528 — all inside
  newton n10's compact scope (256–625). causeway_pair 768, crossroads 1024, promenade 952,
  portal_quartet 896 sit outside it (n10 ≡ fafnir behaviour there, per `compact_prod()` and
  the `fast_edisc` scope gate in `bots/newton-x10-candidate/policy.py`).
- Cycle-001 measured (24 games, 0 faults, published to ledger): n10 5–7 vs fafnir 4–8 on
  identical cells; serre 8–4. Out-of-scope cells were entire-game action-identical to the
  archived fafnir streams (behavioral proof of the tile scoping). spring_wells is an A-side
  initiative map for every bot tested (serre and fafnir streams byte-identical there).
  Full records: `experiment_data/cohort_research_20260927T0115Z_faye/`
  (CYCLE.md, curves_analysis.md, results.md, decision.json, activation_check.json,
  leak_register.json, SYNTHESIS.md).
