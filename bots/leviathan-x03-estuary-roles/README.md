# leviathan-x03-estuary-roles

Line: Leviathan / Estuary. Python exploration fork, separate from Riptide.
Base: **leviathan-v09-arrival**. Borrowed through that base: Ouroboros v10's
mechanics, evaluator, world model, roles, crown/feeding and communication;
v09's arrival targeting and confirmed-only pearl simulation. No runtime import
from another bot folder. `bot.toml` bundles all local Python modules.

**Hypothesis:** resource-aware scout/gatherer/hunter jobs, gradual banking and
security-gated feeding improve the integration of expansion and conversion.
The experiment emphasizes role retirement, regional resource access, crowding,
donor discipline and long-body continuation. It is not a generalisation of
Riptide and is not a phase-end promotion candidate on screen results alone.

## Implementation

- `main.py`: inherited mechanics/evaluation plus explicit hooks into the new
  colony policy. The master-off path keeps v09 behavior.
- `estuary.py`: live role allocation, regional observations/gossip, production
  and banking targets, crown identity/election, donor checks and safety hooks.
- `continuation.py`: node-bounded continuation search, modelling body movement
  and one-time consumption of confirmed pearls. Unknown/budget-limited states
  return “unknown”, not “trapped”.
- `estuary_params.py`: new knob defaults, ranges and consumers.
- `config.py`, `pearl_model.py`: inherited weights and v09 arrival model.
- `params.py`: selected experimental profile; existing v09 pearl options remain
  enabled, `estuary.enabled=1` enables the fork, and `estuary.safety=0` disables
  the continuation option after its first ablation exposed regressions.

Three jobs have different objectives. Scouts favour information, allocate three
of four sonar slots to queued discoveries, and retire as coverage/time reduces
information value. Gatherers prefer relatively safe, productive regions and
reduce production during banking. Hunters have bounded chase targets, a lower
surviving-sprint price and a late replacement allowance. CROWN is the inherited
wire/evaluation code for a gatherer holding the banking responsibility.

Crown and enemy relays retain the original observation round. Self/enemy/crown
identities and portal IDs use 16 bits in the enabled profile. Crown election
uses fresh identities, length and deterministic tie-breaking. It is a local
belief, not globally guaranteed consensus across disconnected sonar regions.

Feeding requires a fresh larger recipient, direct sight of its head at the
moment of donation, a short known route to a corpse-drop tile, no recently
observed nearby enemy, a retained team reserve, and an ID-staggered time slot.
Hunters do not donate. Indicators explicitly identify donor turns; the engine
records the intentional no-action as a suicide/invalid-action death.

The continuation option penalizes long-body moves with no surviving searched
continuation and checks child escape geometry before splitting. It shares a
per-turn node budget and respects growth and collision-before-tail-release.
It treats other bodies as stationary and cannot reconstruct an unseen portion
of a long newborn's body. Its result is not an adversarial safety proof.

## Validation and verdict

Results are recorded in [the bot handoff](../../docs/leviathan/ESTUARY_BOT_HANDOFF.md).
The [strategy handoff](../../docs/leviathan/ESTUARY_STRATEGY_HANDOFF.md) explains
the public-field evidence, role interpretation and parameterisation for the
central aggregation model. The original HANDOFF and ACTIVE are unchanged.

Selected profile: **20–4** over 24 frozen native fixtures against Hunter v20
and Kraken v04, versus v09's **23–1** on identical fixtures (one improvement,
four regressions). Directly against v09: **2–6**, winning both Schooltime sides.
This is a useful alternative on Schooltime, not an overall promotion.

All 22 mechanistic tests pass. Master-off reproduces v09's action/sonar stream
in 6/6 controls. Four selected-profile sandbox checks have no timeouts; Big
Empty peaks at **98.8M / 100M CPU points**, so compute margin remains a concern.
See the handoff for the limited scope and the initial-profile runtime divergence.

## Running experiments

```sh
python3 tools/leviathan/lab.py run leviathan-x03-estuary-roles \
  --vs hunter-v20-portal-scouts kraken-v04-eval \
  --maps default_small,devil,schooltime,stronghold,trauma,big_empty \
  --jobs 3 --timeout 1200 --base leviathan-v09-arrival \
  --output build/leviathan/estuary-new-run
```

Use a new output path. `--set estuary.enabled=0` is the neutral control.
Feature ablations: `--set estuary.regions=0`, `--set estuary.safety=0`,
`--set estuary.roles=0`, or `--set estuary.feeding=0` (the latter restores
inherited proximity feeding while retaining Estuary's election).
The lab writes overrides into frozen copies, not this bot directory.
The selected profile already has safety disabled; `--set estuary.safety=1`
restores the exploratory continuation planner. The table below gives module
defaults; `params.py` explicitly overrides enabled to 1 and safety to 0.

This is an exploration screen, not broad parameter optimization. Native outcome
comparisons and sandbox CPU checks are reported separately. No online submission
has been made.

## New parameters

| Parameter | Default | Range / units | Consumer |
|---|---:|---|---|
| `estuary.enabled` | 0 | 0/1 | all Estuary hooks; 0 retains v09 |
| `estuary.roles` | 1 | 0/1 | self/child assignment and role weights |
| `estuary.regions` | 1 | 0/1 | regional target/waypoint and discovery packets |
| `estuary.feeding` | 1 | 0/1 | security-gated donor policy; 0 inherited feeding |
| `estuary.safety` | 1 | 0/1 | bounded continuation and child checks |
| `estuary.role_period` | 16 | 4..40 rounds | role reassignment hysteresis |
| `estuary.scout_share` | 0.22 | 0..0.5 fraction | desired role mix |
| `estuary.scout_retire` | 0.8 | 0.3..1 coverage fraction | scout retirement |
| `estuary.scout_until` | 340 | 100..450 round | scout retirement |
| `estuary.scout_food` | 0.65 | 0..2 multiplier | scout pearl/spawn weights |
| `estuary.scout_gossip` | 3 | 1..3 rays | scout sonar scheduling |
| `estuary.hunter_share` | 0.25 | 0..0.6 fraction | desired role mix |
| `estuary.chase` | 6 | 2..12 tiles | hunter target horizon |
| `estuary.compact_units` | 48 | 8..64 dragons | population ceiling |
| `estuary.open_units` | 64 | 8..64 dragons | population ceiling |
| `estuary.late_units` | 0.4 | 0.1..1 fraction | banking population target |
| `estuary.split_gain` | 1.2 | 0.5..2 multiplier | early split candidate value |
| `estuary.density` | 3.0 | 0..8 evaluator units | safe productive-region target |
| `estuary.crowd` | 0.35 | 0..2 evaluator units/head | region waypoint congestion |
| `estuary.bed_block` | 0.65 | 0..4 evaluator units | next-tick occupied bed cost |
| `estuary.zone_period` | 4 | 2..16 rounds | scout discovery packet rate |
| `estuary.zone_ttl` | 80 | 10..200 rounds | regional report freshness |
| `estuary.bank_start` | 280 | 150..400 round | banking ramp and crown eligibility |
| `estuary.bank_full` | 400 | 320..460 round | banking ramp endpoint |
| `estuary.bank_min` | 6 | 4..16 segments | early crown eligibility |
| `estuary.feed_start` | 380 | 300..450 round | donor activation |
| `estuary.feed_reserve` | 4 | 2..16 dragons | minimum force after donation |
| `estuary.guard_reserve` | 10 | 4..24 dragons | population floor under observed threat |
| `estuary.feed_period` | 3 | 1..8 rounds | ID-staggered donor opportunities |
| `estuary.feed_gap` | 3 | 1..10 segments | recipient advantage over donor |
| `estuary.feed_radius` | 8 | 3..15 tiles | recent enemy exclusion near recipient |
| `estuary.crown_fresh` | 12 | 2..30 rounds | crown election beacon freshness |
| `estuary.depth` | 5 | 2..7 plies | long-body continuation |
| `estuary.nodes` | 120 | 30..300 expansions/turn | shared continuation budget |
| `estuary.long_min` | 8 | 4..20 segments | continuation activation |
| `estuary.trap_cost` | 35.0 | 10..100 evaluator units | failed continuation penalty |
| `estuary.indicators` | 1 | 0/1 | replay role and donor attribution |

The inherited P/RP weights remain available in config.py. The new parameter
families are not a mathematically complete representation of every strategy:
regional counts are estimates, enemy strength is only partially observed, and
there is no formation controller or verified escort assignment yet.
