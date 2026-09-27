# Newton: closing the compact-contact leak of the serre chassis

Lineage owner: GLM (this session). Started 2026-09-26. Mission, from the
strategy-leak discovery brief: the strongest composite (fafnir) still donates
whole fixtures to the compact-production specialists its pooled gauntlet
averaged away. Newton diagnoses that residual leak at the decision-path level
and tests minimal, default-off repairs under pre-registered gates.

## 1. Baseline and identity

**Baseline: `bots/fafnir-v01-phalanx`, copied byte-identically to
`bots/newton-x01-frozen`** (SHA-256 manifest `tools/newton/frozen.json`, 11
files). Instrumentation added in the dev copy (`build/newton/dev`) is
counter-only; parity verified on the four v13 devil/arena fixtures — outcome,
rounds, reason and all final counters identical to the fresh diagnostic run
(`experiment_data/fafnir-v01-phalanx_20260926225920357152` vs
`experiment_data/parity-bot_20260926230646218463`).

Because the engine is deterministic and x01 is byte-identical to fafnir-v01,
x01 inherits fafnir's frozen records as its own baseline records (verified
pairing, not re-run): screen 25-7 (`experiment_data/f12-sizematch_20260926143914278071`),
gauntlet 140-42 (`f12-sizematch_20260926144850071036`), reserve 13-3
(`fafnir-v01-release_20260926150818154880`). The compact panel baseline is
fresh: **0-8** vs ouroboros-v13 + tew-v12 on devil+arena, both sides
(`fafnir-v01-phalanx_20260926225920357152`).

## 2. Leak dossier L1: compact contact (the specialists the gauntlet hid)

**Exposure.** fafnir-v01 gauntlet devil 5-9 / arena 6-8 pooled over 7
opponents, but **0-8 head-to-head vs the two compact specialists** (ouroboros-
v13, tew-v12; fresh native run, both sides, 2026-09-26). Arena eliminations at
rounds 46-60; devil eliminations at 334-394 or 500-round length loss.

**Devil mechanism — the production flywheel is lost, not the conversion.**
Timeline: units/splits/pearls track v13 through round ~30, then diverge: by
r200 fafnir 86 splits / 222 pearls vs v13 198 / 483; final 131 / 376 vs 474 /
1394. Trace funnel (one full game, all dragons, counters cumulative):

| funnel stage | count |
|---|---|
| dragon-rounds eligible (len ≥ 4) | 177 |
| blocked: `role != forager` (crown) | **126** |
| blocked: no child exit | 2 |
| blocked: child-area flood | 0 |
| proposed | 49 |
| chosen (argmax won) | 49 |

Whenever a *forager* reaches length 4 it splits (argmax_lost 0, gate losses
~0): the split policy is NOT the binder. The binders are upstream: dragons
rarely reach length 4 (income spreads over a small fleet), and from round 250
the crown-role gate locks out the team's longest dragon entirely (126 blocked
dragon-rounds). v13, by contrast, runs an unconditional ladder split at
length ≥ 4 and **accepts churn as a cost**: 474 splits, 431 self-inflicted
deaths (body 218, self 134, invalid 48), sustaining 46-58 units and ~4x pearl
income. fafnir dies less (102 self-inflicted) and loses. Secondary signal:
63% of fafnir's devil splits are emergency `escape_split` (all move candidates
dead) — chronic boxing by the enemy swarm.

**Arena mechanism — the opening melee is lost to newborn predation.** One
voluntary split in the entire game; 16/17 splits emergency; deaths: 9/17
enemy-initiated head-to-head (children hunted), 7/17 self-ram, vs v13's
deaths dominated by its own swarm collisions. Elimination by r46-60.

**Layers responsible.** Objective/valuation (fast central beds ceded via
`enemy_disc 0.6` under contest), role policy (crown production lockout post
`crown_from 250`), survival (newborn threat pricing `p_short 0.1` assumes
longer enemies never bother — false in a 20-unit melee), production pacing
(conditional split cannot match unconditional churn).

## 3. Freeze discipline

Frozen from x01: everything except explicitly parameterised mechanisms below.
Arms are `override.py` files (the params.py OVERRIDE hook) against the dev
master `build/newton/dev`; mechanism code enters the master default-off and
must reproduce x01 exactly with switches off (structural parity, spot-checked
on 2+ fixtures per new code path). The harness: cached deterministic arena
(`tools/feynman/arena.cpython-313.pyc`, sinbad-lineage runner preserved as
bytecode) for arm iteration; `tools/compare_bot.py` + `configs/newton/` for
gate records.

## 4. Pre-registered arms (cycle 1) — manifest frozen before outcomes

| Arm | Type | Change | Hypothesis |
|---|---|---|---|
| N1 `crown_split` | mechanism | crown role may `split_option` when `compact_prod()` | reopen the 126 blocked devil dragon-rounds; late production without touching the length-race on open maps |
| N2 `fast_edisc 0.9, fast_edisc_per 25` | params (existing dormant code) | fast-regrowing beds keep value when the enemy head is closer | stop ceding the devil centre; contested fast beds cannot be monopolised |
| N3 `guard_age 12, guard_p 0.7` | mechanism | dragons younger than 12 rounds price all enemy-head reach at ≥ p_eq | arena newborn predation (9/17 enemy-ram) |
| N4 `ladder_nc 625, ladder_floor -3` | params (existing dormant code) | v13's priority-ladder doctrine on compact maps | bounds/diagnostic arm: quantifies the unconditional-churn doctrine on this chassis |
| combos | — | only after singles, 2x2 vs both parents | — |

## 5. Pre-registered selection rule (`tools/newton/selection_rule.json`)

1. **Parity**: every arm, mechanism off, reproduces x01 on ≥2 spot fixtures
   exactly (outcome/rounds/counters).
2. **Screen gate** (32 serre-screen fixtures, paired vs x01's 25-7):
   arm ≥ +2; no map cell worse by ≥2.
3. **Compact gate** (8 fixtures vs v13+tew, devil+arena, both sides; x01 0-8):
   arm ≥ 3-5.
4. **Gauntlet gate** (182 fixtures, x01 140-42): ≥ +3; no map cell worse by
   ≥3; big_empty and stronghold ≥ 12-2 each (fafnir: 14-0/14-0).
5. **Reserve gate** (16 frozen fresh-map fixtures, x01 13-3): ≥ 13-3;
   per-fixture flips listed.
6. **Judge gate**: sandbox vs hunter-v22 on arena+stronghold, both sides:
   0 TLE / 0 faults / 0 errors.
7. Promotion requires ALL gates. A failed gate is recorded, never relaxed;
   an arm whose mechanisms never activate on a gate set is an activation
   finding, not a pass.

## 6. Experiment log

### Cycle 1 diagnosis runs (2026-09-26)

- Compact panel baseline: x01 **0-8** (fafnir-v01-phalanx_20260926225920357152).
- Parity: instrumentation-only dev copy **4/4 fixtures identical**.
- Trace funnel + death attribution: `tools/newton/funnel_sum.py`,
  `tools/newton/h2h_actor.py`, `tools/newton/replay_churn.py`; traces under
  `/tmp/sinbad-*` from run `experiment_data/dev_20260926230739142442`.

(Arm results appended below as they complete.)

### Cycle 1 arm ledger (compact panel = 8 fixtures vs v13+tew on devil+arena; screen = 32 serre-screen fixtures, paired per fixture)

| Arm | Change | Compact | Screen | Verdict |
|---|---|---|---|---|
| n1 `crown_split 1` | crown may produce under compact_prod | 0-8 (3/8 fixtures differ) | — | null: fires rarely, converts nothing |
| n2 `fast_edisc 0.9/25` | fast-bed contest | **2-6 (+2)** devil 2-2 | 25-7 (+0): devil +1, trauma −1 | best single; trauma regression |
| n2b `fast_edisc 1.0` | full-value contest | 2-6 (+2) | — | plateau at 0.9; devil-A stronger (1740 pearls) |
| n3 `guard_age 12/guard_p 0.7` | young-dragon threat floor | 0-8 (7/8 differ) | — | null: pricing doesn't save newborns |
| n4 `ladder_nc 625/floor −3` | v13 ladder doctrine | 0-8 (8/8 differ) | — | negative: evaluator-floor-gated ladder ≠ v13's |
| n5 `atk_space 1` | space-denial trades | 0-8 (devil-only activation; A-side collapses r203, B-side survives +48% pearls) | — | negative alone |
| n6 = n2c + n5 | contest + space trades | 0-8 | — | **harmful interaction**: trades destroy the contest's A-side wins |
| n2c = n2 + `fast_edisc_nc 625` | contest scoped to compact maps | 2-6 (+2) | **26-6 (+1)**: devil +1, trauma protected | best cycle-1 candidate; both gates one short |
| n2c = n2 + `fast_edisc_nc 625` | contest scoped to compact maps | 2-6 (+2) | **26-6 (+1)**: devil +1, trauma protected | best single-mechanism candidate; both gates one short |
| n7 `unit_stop_round 300` | compact conversion stop | 0-8 | — | null alone (cession keeps B-side dead) |
| n8 = n2c + n7 (stop 300) | contest + conversion stop | 2-6 | 26-6 (+1) | devil-A conversion stronger (longest 46 vs 8); devil-B/tew one segment short (24 vs 25) |
| n9a stop 250 | coordinate descent | 2-6 | — | crown still 24 vs 25 |
| n9b stop 200 | coordinate descent | **3-5 (+3) — compact gate PASS** | 25-7 (+0): devil/B/leviathan lost | conversion flips devil-B/tew (longest 35 vs 17) but cedes the grind game vs evaluators |
| n10-r0-visibility | contest gated on no-enemy-at-spawn | 0-8 | — | **rejected implementation**: newborns spawn near enemies, so their per-process flag disables the contest for exactly the dragons that need it |
| n10 = contest (0.9/25, nc 256–625) + stop 200 | + arena floor | pending | pending | nc floor added after n2c's gauntlet showed arena −4: recorded as post-hoc scoping, gauntlet is confirmatory only |

**n2c gauntlet (182 games): 142-40 (+2, gate needs +3) with arena 2-12 (−4, cell rule violated).**
Gains: default_small +3, trophy +2, devil +1, dilemma +1; losses: arena −4, Colosseum −1;
big_empty/stronghold/schooltime/default/queen/autarky/trauma unchanged. The contest transfers
to default_small/trophy/dilemma (compact fast-bed maps) and is actively harmful on arena
(melee map: contesting = feeding).

**The cycle-1 structural finding.** The two mechanisms that work are opponent-conditional
in opposite directions, and no static parameter passes both gates:
- fast-bed contest recovers devil-A completely (churn-economy parity with v13/tew)
  but devil-B remains structurally lost (center control is first-mover-favored under
  the engine's A-first action order; B-side suffocation by 64-unit saturation);
- conversion stop (200) wins the length race against swarm survivors (devil-B/tew)
  but cedes the grind game against evaluators (devil-B/leviathan: x01's 383-split
  grind held leviathan to longest 10; stop-200's 254 splits let it grow 29).
The parallel to godel's cycle-1 verdict is exact: the component is real and worth
keeping, but its correct conditioning is a stateful property (opponent class /
game state), not a global constant.

Mechanism notes:
- n2's devil-A reversals are total: pearls 376→1616, splits 131→598, deaths
  accepted 133→579, opponent crushed to 1-7 units — the chassis runs the churn
  economy once it stops ceding fast beds. v13-as-B collapses symmetrically
  (66-128 splits) when contested by A: devil center-control is strongly
  first-mover (engine A-first action order) favored under mutual contest.
- devil-B suffocation (timeline analysis): fafnir-B dies slowly of
  self/body/wall collisions in shrinking space while v13-A saturates the 64-unit
  cap; fafnir's material-value strike margin never fires against a len-2 swarm.
- arena: unchanged by every arm except the contest (which harms it, arena −4 in
  the n2c gauntlet). Newborns die before eating two pearls; local-superiority
  conditions never hold at 3:1 unit deficits. The arena fix needs
  production-rate or newborn-siting mechanisms not yet attempted; the n10
  composite excludes arena from the contest via an NC floor as damage control.
