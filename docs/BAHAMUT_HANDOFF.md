# Bahamut experimentation handoff

## Task and base

Build and iterate a functional Python bot within the **lineage supplied in the
user's prompt**. Explore state estimation, features, execution, decision policies
and communication; compare versions using the shared statistics tools. Simple
hand-tuned designs and small learned models are both valid. The aim is useful
experiments and stronger bots, not implementing every idea below.

**Start from [`examples/bahamut-scaffold/`](../examples/bahamut-scaffold/)**:
[`main.py`](../examples/bahamut-scaffold/main.py),
[`protocol.py`](../examples/bahamut-scaffold/protocol.py), and
[`bot.toml`](../examples/bahamut-scaffold/bot.toml).
This is the newer scaffold with separate intent and engine-command sets.
`bots/bahamut-scaffold/` is the older alternative; do not accidentally use it as
this brief's base. Both are placeholders, not meaningful benchmark opponents.

Copy the base into `bots/<lineage>-vNN-<hypothesis>/`. Preserve the supplied
lineage prefix, choose the next unused version number, and retain earlier
versions as baselines. Existing experimental naming is `<lineage>-xNN-<slug>`.
Record the parent and any borrowed components in each bot's README. Read other
bots freely; make your changes in your own lineage rather than overwriting
another team's work or the common scaffold.

This document and the current user prompt define this experiment.
[`HANDOFF.md`](HANDOFF.md), [`FRONTIER.md`](../FRONTIER.md), and lineage reports
provide project context; old cycle assignments and proposals are not new
instructions or proof of current performance.

## Game references and essential rules

Official documentation: **https://game.battlecode.au/docs/**.
The following summary was checked against the published rules on 2026-09-25.
Check relevant pages and the installed toolkit version when implementing details.

- Each dragon acts in ascending ID order within a round. Games last at most
  500 rounds. Eliminating the other team wins; mutual elimination in the same
  round draws. At the limit, compare longest living dragon, then total living
  length, then draw. “Crown” is team terminology for a dragon being grown or
  protected for this tiebreak, not an extra game object.
  [Structure](https://game.battlecode.au/docs/structure).
- Vision is a wrapping 7×7 window, containing absolute coordinates, pearl
  presence/countdowns, dragon segments with IDs/teams, and terrain edges.
  Portals change movement connectivity but do not extend the vision window.
  [Vision](https://game.battlecode.au/docs/vision).
- A turn chooses movement or splitting. Moving onto pearls grows length.
  Sprinting multiple steps costs one segment per additional step; each step
  checks collisions. Entering kelp or any occupied body tile kills the mover,
  including its own tail before that tail moves. Entering another head kills
  both dragons, including allies.
  [Movement](https://game.battlecode.au/docs/movement).
- Splitting reverses rear segments into a child headed from the old tail. Both
  parent and child need length at least two; the default team limit is 64.
  The child gets a fresh program instance and can act later that round; it does
  not inherit the parent's Python memory. Illegal splits are fatal.
  [Splitting](https://game.battlecode.au/docs/splitting).
- Missing/invalid actions are fatal. Death deposits pearls on alternating
  segments. A replay-labelled “suicide” does not prove intentional sacrifice.
  [Death](https://game.battlecode.au/docs/death).
- Protocol 3 permits four sonar rays per turn, one per cardinal direction,
  each carrying a uint64. They fire after a surviving action, wrap, traverse
  portals and stop at kelp or a dragon. Own-body rays can emerge from the tail.
  Received payloads have no sender/team metadata; sender echoes count kelp,
  allies, ally heads, enemies and enemy heads. The rules specify no length cost
  for sonar. Information use and scheduling are experimental choices.
  [Sonar](https://game.battlecode.au/docs/sonar).
- Judge limits are 100 million CPU points per dragon per turn and 48 MB memory;
  initialization also counts. Native games do not establish judge-budget safety.
  Batch output, limit logging and bound expensive searches/precomputation.
  [Timeouts and runtime](https://game.battlecode.au/docs/timeouts).

The engine uses text stdin/stdout; official helper objects wrap that protocol.
Our scaffold supplies its own adapter. Initialization includes a unique dragon
ID, team, map dimensions and unit limit. Absolute positions and IDs already
exist: do not invent a coordinate-registration or identity-hashing problem where
the engine has solved it. A compact transmitted ID may still require handling
truncation/collisions. [Wire protocol](https://game.battlecode.au/docs/protocol).

## Architecture and information flow

Keep five conceptual layers. They need clear interfaces, not necessarily five
files or a large framework.

| Layer | Responsibility | Scaffold location |
| --- | --- | --- |
| State | Tracked observations, retained evidence, estimates and script memory owned by this instance. | `state`, `initialize_state()`, `update_state()` |
| Features | Transform state into quantities useful for both policy and execution. | Add an explicit `build_features()` stage after state update; e.g. `work["features"]`. This hook is not in the base yet. |
| Execution | Implement an available intention as a legal game action, possibly using an algorithm or continuing a script. | `Intent`, `build_actions()`, `execute_action()` |
| Decision | Choose between available execution options using rules, scores or a learned/stochastic policy. | `choose_action()` |
| Encoding | Validate/decode sonar packets and encode structured outgoing reports into 64 bits. | `decode_messages()`, `encode_messages()` |

`construct_messages()` separately decides **what to communicate and in which
directions**. Encoding implements representation, not message selection.

Intended flow, adding the feature stage in your copy:

```text
protocol input → decode reports → update state → build features
  → build available intentions → choose intention → execute intention
  → construct reports → encode reports → diagnostics → commit script memory
  → protocol output
```

The existing hooks take no arguments and contain `pass`; their shared containers
keep the initial scaffold short. You may refactor your version as it becomes
useful. Current containers and write ownership:

- `io.game`: initialization; `io.observation`: fresh per-turn input. Treat these
  as read-only engine data. Tiles are integer tuples; body and edge rows remain
  wire-format string tokens and need interpretation by your implementation.
- `state`: persistent per-instance data. `update_state()` handles perception and
  estimation updates. Define the meaning, units and age of each retained value.
- `work`: scratch data cleared each turn, including decoded reports, candidates,
  selected intention, outgoing reports and optional features.
- `work["state_updates"]`: selected execution queues script-memory assignments;
  the loop commits these with `state.update(...)` at turn end. This is an explicit
  second state-write point, not an accidental side effect of scoring candidates.
- `io.reply`: `Command`, argument and direction-to-uint64 sonar dictionary.
  `protocol.py` handles framing, optional initial echoes, `PROTOCOL 3`, and output.
  **Normally leave this boilerplate alone.** Fix demonstrated adapter bugs when
  necessary; put strategy and packet semantics elsewhere.

`Intent` currently includes NSEW, split, attack and feed-ally examples.
`Command` contains only engine MOVE/SPLIT. A minimum bot can choose raw actions;
a richer bot can choose attack, gather, scout, retreat, produce soldiers, hunt
portals or donate length, with executors computing the actual action. These are
optional action abstractions, not mandatory permanent roles. Intentional feeding
should remain an explicit policy option even if its executor ultimately moves
into a fatal tile.

Availability checks should be cheap; more expensive pathing can run after
selection. Executors need legal fallbacks and, for multi-turn scripts,
continuation/interruption rules. The current fallback merely moves straight:
it supplies valid transport, not collision avoidance or a functioning policy.

## Experimental state and features

The working strategic hypothesis is spatial allocation: enough friendly dragons
to harvest useful regions, with surplus effort moving toward exploration,
defence and expansion. Local crowding need not mean control, and low friendly
density need not mean danger. Test density, topology, direction and time together
where useful; do not assume one control formula is established.

Explore **any subset, including none**, of these ideas:

1. Accumulate concrete terrain, pearl-bed and portal observations into a local map.
2. Keep moving averages or rolling windows of visible allies, enemies and pearls.
3. Broadcast these local summaries with enough position/time context to use them.
4. Combine received reports into smoothed estimates of wider swarm/enemy density.
5. Try richer spatial statistics, uncertainty estimates or learned predictors.
6. Use absolute position, displacement from this instance's start, and game time.
7. Estimate connectivity or travel distance to pearls/enemies; cache or bound
   pathing when appropriate. Portal-aware topology is optional to investigate.
8. Measure free space, corridors and exits, combined with ally/enemy density.
9. Track observed deaths, possible sacrifices, friendly collisions and enemy
   kills/losses. Retain uncertainty where local evidence cannot determine cause.
10. Use own length and its implications for mobility, splitting and endgame value.
11. Use relative densities and spatial gradients to estimate safety, frontier,
    crowding and low-information areas. Unseen is not the same as empty.

Distinguish counts of dragons, heads and body segments. Choose and document EWMA
time scales, spatial support, report age handling and whether repeated reports
represent fresh evidence. These are model choices to test, not a prescribed
global-map architecture. Validate prediction features against later observations
where useful; likelihood-based fitting requires an explicit observation model.
Full replay truth is available for offline analysis, not runtime perception.

For communication, specify bit layouts, ranges, quantisation and packet versions.
Use a small tag/checksum/parity scheme and sensible field validation to reject
accidental interpretations of unrelated payloads. Parity alone accepts many
random packets; checksums are not authentication against deliberate spoofing.
Choose a measured overhead rather than assuming enemy messages are trustworthy.
Scheduling and relay policy are separate tunable choices; sophisticated sonar
avoidance is not a prerequisite for a useful first bot.

## Comparison and shared statistics

Use [`tools/compare_bot.py`](../tools/compare_bot.py), with
[`comparison.toml`](../comparison.toml) as the default example roster. Copy the
TOML for a focused comparison; bot and map paths are relative to the TOML. Run
from the repository root:

```sh
uv run tools/compare_bot.py bots/LINEAGE-vNN-slug --dry-run
uv run tools/compare_bot.py bots/LINEAGE-vNN-slug
uv run tools/compare_bot.py bots/LINEAGE-vNN-slug --config my-comparison.toml
uv run tools/compare_bot.py --resume experiment_data/<run-directory>
```

Set `sandbox = true` in the TOML for judge CPU checks and use `--jobs N` to
change concurrency. Comparison outputs, replays, and frozen experiment copies
are local artifacts. The comparison writes each completed game's outcome into
the game statistics contribution ledger, including source and map fingerprints.

Share `game_stats/runs/<run-id>.parquet` contributions through Git. The merged
`game_stats.parquet` and `experiment_data/` outputs are local; the existing
historical files already tracked under `experiment_data/` remain provenance.
After merging new contributions, rebuild and summarize with:

```sh
uv run tools/game_stats.py rebuild
uv run tools/game_stats.py summary --output /tmp/bot-pairs.csv
```

The [benchmarking guide](benchmarking.md) covers the supported single-candidate
and bounded tournament runners. The previously documented collection-wide
campaign scripts are absent from this checkout.

## Iteration and handoff expectations

Use your own earlier versions **and** major pool bots. Direct parent-versus-child
matches and performance against common opponents answer different questions;
check both. Keep map and side breakdowns, retain counterexamples and inspect
replays for large regressions. Identical deterministic fixtures repeated are
not independent samples; use additional maps/variants or distinct documented
seeds when testing generalisation. Keep native and sandbox evidence separate.

Hand tuning, small parameter searches, supervised feature fitting and lightweight
policy/value learning are all reasonable. Training is optional. Work fits a
MacBook Pro: bound experiment sizes and concurrency, favour compact inference,
and do not assume large-scale ML infrastructure. Use held-out fixtures when
fitting, and save parameters, seeds, training provenance and comparison results.
The current comparison tools provide outcomes and replay diagnostics, not an
actor-critic trainer or a ready-made per-decision learning dataset.

Iterate all layers as evidence warrants; neither a complex state model nor a
learned decision policy is inherently better. Test components against simpler
alternatives, use statistics to choose the next experiment, and validate compute
before claiming deployment readiness. Preserve promising diverse behaviour even
when its aggregate score does not justify promoting it.

Each version's README/handoff should identify lineage, parent, hypothesis,
implemented layers, parameters, exact comparison configuration/run locations,
W/L/D and important map/side regressions, diagnostic explanations, sandbox checks
actually performed, and remaining uncertainties. Separate measured results from
predictions. This gives the team and a later aggregating model enough evidence
to reuse components and choose the next experiments.
