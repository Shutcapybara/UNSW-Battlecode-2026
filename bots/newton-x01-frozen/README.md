# fafnir-v01-phalanx

- **Lineage:** Fafnir (leak-lab composite, 2026-09-26). Mission: the ledger
  shows every strong line wins one map class and donates another (see
  `docs/leaklab-findings.md` for the taxonomy); fafnir composes the proven
  components of the strongest lines on the strongest chassis.
- **Parent:** `bots/serre-v01-foundation` (sinbad e23). With every fafnir
  parameter off, the source reproduces serre-v01 exactly (verified on
  arena/devil/Colosseum fixtures, deterministic engine).
- **Name:** the phalanx — units that stand together hold contested ground.

## What was grafted (each measured alone, all default-off in the dev tree)

1. **Compact production doctrine** (`compact_nc 625`, `unit_target 26`,
   `prod_boost 2.0`) — from ouroboros-v13/tew-v12 (v13: devil 97%, arena 91%):
   on maps of at most 625 cells, keep splitting toward 26 units, past
   `split_stop`.
2. **Split-gate relaxation** (`split_nothreat 1`, `compact_child 1`) — the
   enabling diagnosis, from replay study of why a bare split boost changed
   nothing (devil fixtures byte-identical): serre's split branch re-charges
   the ambient enemy-head threat the parent faces on every branch, and
   demands a 4-cell newborn pocket. Under compact production the ambient
   threat is dropped (splitting spreads risk to two units), the newborn
   pocket need drops to 3, the parent trap penalty halves.
3. **Counter-threat support discount** (`threat_ally 0.25`, `threat_ally_all
   1`, `threat_ally_foe 1`, floor 0.25x) — from tew-v11/v12's support gating
   (arena 86-92%): an enemy trade is discounted only when an allied head at
   least as long as the attacker stands within `support_rad 3` of the
   attacker. Two earlier semantics failed and are recorded below.

## Dead ends (do not retry without a new idea)

- period-aware bed-value multiplier (`bed_per_k`): queen/trauma collapse
  (screen -3/-7); early period estimates poison the value field.
- self-centred support (allies near *me*): stronghold -4 — long dragons
  underprice threats because feeders cluster near them.
- attacker-centred support without the size match: big_empty -3 — small
  feeders "protect" the crown against attackers they cannot deter.
- strike support *bonus*: inert (serre strikes are value-gated first; tew's
  mechanism is a gate, not a bonus).
- portal-exit risk memory (`blind_mem`): net 0 on the screen; code kept
  default-off pending dilemma/autarky evidence.

## Measured (native deterministic fixtures, both sides; serre-v01 baseline in brackets)

| Set | Record | Per map |
|---|---|---|
| Screen 32 | **25-7** [23-9] (+2, gate met; no map cell regressed) | devil 4-4 [2-6], trauma 6-2, Colosseum 8-0, queen 7-1 |
| Gauntlet 182 | **140-42** [134-48] (+6, gate met) | **devil 5-9 [2-12]**, arena 6-8 [5-9], schooltime 13-1 [11-3], Colosseum 13-1 [12-2], big_empty/stronghold 14-0 held, worst cell default_small 11-3 [12-2] |
| Reserve 16 | **13-3** [13-3] (equal: all 16 fixtures identical to baseline — the active mechanisms never fire on the frozen families; the strict "+1" gate is not met, recorded as such) | twinlakes 8-0, crossfire 5-3 |
| Judge sandbox | **clean** (4/4 recorded, 0 TLE, 0 faults, 0 errors; 2-2 vs hunter-v22) | 100M points / 48MB per dragon turn |

Run directories: `experiment_data/f12-sizematch_20260926143914278071` (screen),
`experiment_data/f12-sizematch_20260926144850071036` (gauntlet),
`experiment_data/fafnir-v01-release_20260926150818154880` (reserve). Arm ledger
and the leak taxonomy: `docs/leaklab-findings.md`, tooling in `tools/leaklab/`.

## Known remaining holes

- devil vs ouroboros-v13 still 1-3 head-to-head (was 0-4): the swarm centre
  contest improved but is not won.
- arena 6-8 (was 5-9): the melee production race is closer, not closed.
- Crossfire-family A-side losses (3/4): the fresh-family verdict is unchanged.
