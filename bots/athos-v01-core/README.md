# athos-v01-core

Lineage: **athos** (generation 1). Parent: `bots/monte_christo-v01-core`
(the recommended baseline of the messaging study). Architectural base:
`examples/bahamut-scaffold` (protocol.py / bot.toml unchanged).

This release is the **behaviour-preserving extraction** of v01 onto the
stable execution contract requested by the next-generation handoff. It is
not yet the semantic intention menu: intention labels classify the nominated
action for diagnostics and do not influence selection.

## Contract

Six stages per turn in `main.py`:

| Stage | Owner | Responsibility |
|---|---|---|
| state | world.py, roles.py, radio.hear | observation + decoded reports -> retained facts, estimates, role state (once) |
| features | tactics.py, decision helpers | threat map, head reach; progress/flank/need built with the plan |
| candidates | executors.py | frozen availability checks: route plan (MEM script state), feeder sacrifice probe, move enumeration, split facts; escape stays decision-gated |
| decision | decision.py | per-candidate previews (fixed executor interface) + P0 scoring, nomination by max(score) |
| execution | executors.py | serialize the nominated command; queue trail cells |
| commit | main.py, radio.py, comms.py | messages + handoff override, sonar encode, trail extend, reply |

`executors.py` is the frozen executor dependency closure E0: candidate
generation, movement simulation, routing, internal target choice, tie-breaks,
availability thresholds, search budgets, role rules for execution and fallback
behaviour, verbatim from v01 `policy.py`/`main.py`. Decision scoring changes
must not reach it; any change is E0 -> E1 and must be versioned. `decision.py`
is policy P0, verbatim v01 arithmetic. Unchanged copied layers
(protocol, params, world, tactics, comms, radio, roles, risk_features) are
byte-identical to v01 and guarded by `tests/test_athos.py`.

Intention vocabulary (diagnostic in this release): GATHER, SCOUT, ATTACK,
RETREAT, FEED_ALLY, REPRODUCE — `decision.classify` labels the nomination;
`ATHOS_INTENT`/`ATHOS_RISK` traces are opt-in via `training_trace`.

## Verification claim

Stream identity with monte_christo-v01-core: identical movement/split/sonar
streams on both sides of every source-matched fixture — see
`docs/athos.md` and `tools/athos/stream-verify.json` for the executed
comparison. No outcome record is claimed beyond inheriting v01's standing.
