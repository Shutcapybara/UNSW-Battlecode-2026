# Formatted Hunter v22 — complete policy

Complete C++ reformat of Hunter v22 around the explicit pipeline:

`information -> state -> intent -> command` and `reports -> sonar`.

Together the modules contain the entire original V22 implementation. Persistent
beliefs stay in `state`; `work` resets each turn and carries the selected
decision and output through the staged driver. The policy now returns a named
`Decision` instead of an anonymous command string, so experiments can replace
one execution without reverse-engineering the priority ladder.

## File layout

- `main.cpp` — staged lifecycle and reply framing.
- `src/model.hpp` — constants, wire tags, decisions, and state types.
- `src/params.hpp` — experiment switches and weights; defaults preserve V22.
- `src/bot.hpp` — the `Bot` state object and module composition.
- `src/state/` — protocol ingestion, persistent world knowledge, macro features,
  and local safety analysis.
- `src/navigation/` — portal planning, teammate routes, and pearl ownership.
- `src/communications/` — all 64-bit sonar packet construction.
- `src/brain/decision.inc` — reusable `require<T>()` and `fire_on<T>()` rule
  framework.
- `src/brain/decisions/` — individually replaceable execution scripts.
- `src/brain/policy.inc` — priority ordering, growth, forage, and frontier
  selection.

The important dependency direction is:

```text
protocol -> state/features -> execution scripts -> policy -> sonar/output
```

Decision scripts may read state and call navigation helpers. State and
navigation must not depend on policy classes.

## Good first experiments

Each item has one main edit surface and can be benchmarked as a separate copy
of this directory:

1. **Terrain safety:** set `use_local_safety_tiebreak` in `src/params.hpp`. Tune
   only the four local-safety weights. The bounded flood-fill and enemy reach
   projection live in `src/state/features.inc`.
2. **Attack execution:** change `attack_path()` in
   `src/brain/decisions/combat.inc` or its small wrapper in `attack.inc`. The
   policy invokes it as the named `Execution::ATTACK` script.
3. **Trap/surround execution:** change `boost_trap_action()` or
   `boost_surround_action()` independently in `combat.inc`.
4. **Exploration scoring:** change the frontier score in `policy.inc`; do not
   touch the portal planner or sonar.
5. **Growth routing:** change only `growth_action()` in `policy.inc`.
6. **Macro policy:** reorder the decision objects in `choose_decision()` without
   modifying their algorithms or conditions.
7. **Statistical policy:** consume `features()` (round, own length, visible
   counts, and friendly/enemy density EWMAs) in `choose_decision()`. These
   features are updated by observation ingestion but intentionally do not alter
   the default policy.

Keep one hypothesis per copied bot directory. First compare its stdout with V22
on protocol fixtures, then run both sides on a few targeted maps, and only then
run the full gauntlet. Sonar encoding should remain untouched unless sonar is
the experiment.

Nothing from V22's policy has been shortened or removed. This includes its
18-step portal round-trip beam planner, unmatched-portal scouting, emergency
portal escape, survival continuation search, boost trap and surround tactics,
enemy-size memory, teammate route ownership, crown coordination, late growth,
frontier scoring, revisit penalties, and all six sonar packet families.

Run from the repository root:

```sh
.venv/bin/unswbc run maps/trauma.map bots/formatted-hunter-v22 bots/hunter-v22-frontier-exploration
```

For a quick compile and behaviour-preservation check:

```sh
python3 tests/test_formatted_hunter_v22.py
```
