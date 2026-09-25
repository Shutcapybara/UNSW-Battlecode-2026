# Bahamut scaffold example

A proposed replacement structure, kept separately from `bots/bahamut-scaffold`
for comparison. This is a transport-valid starting point, not a functional
competitor: every strategy hook takes no arguments and contains `pass`. The
fallback moves straight ahead, with no collision avoidance and no sonar.

**Edit `main.py`. Normally leave `protocol.py` alone.** The latter is our adapter
for the [game protocol](https://game.battlecode.au/docs/protocol), not a game SDK.
Sonar payload encoding/decoding is team-owned strategy code in `main.py`.

## Flow

Engine input → decode reports → update state → build available intentions →
choose an intention → translate it to an engine command → construct messages →
encode messages → diagnostics → commit script memory → engine output.

- `io.game`: initialization data; read-only to strategy code.
- `io.observation`: fresh engine input each turn; read-only to strategy code.
- `state`: persistent memory owned by this dragon instance. `update_state()`
  handles perception updates. Selected scripts queue top-level memory assignments
  in `work["state_updates"]`, committed at the end of the turn. Other stages read
  state rather than silently changing it. This is an explicit second write point.
- `work`: per-turn scratch data, reset every turn.
- `io.reply`: one `Command`, its argument, and direction-to-uint64 sonar payloads.

Tiles are `(x, y, has_pearl, pearl_in)` integer tuples. Body rows and edge grids
retain the wire-format string tokens. Echo counts are kelp, ally, ally head,
enemy, enemy head. The adapter handles initial turns without echoes and later
protocol-3 turns with echoes and 64-bit messages.

## Two action sets

`Intent` describes what the policy chose. `Command` describes what the engine
accepts. Actions are `(Intent, parameters)` pairs, so the same intention can have
different targets. For example:

```python
work["selected"] = (Intent.FEED_ALLY, {"target_id": 17})
# execute_action would establish a suitable sacrifice, then produce:
io.reply.update(command=io.Command.MOVE, argument="E")
```

This is illustrative, not an implemented feeding rule. `FEED_ALLY` and `ATTACK`
are never sent to the engine. They remain distinct policy/training labels even
when their execution happens to use an ordinary movement command.

Cheap availability checks belong in `build_actions()`. A selected script can do
more expensive work in `execute_action()`. Each executor must define its fallback
if the intention cannot be achieved. Scripts spanning turns additionally need
continuation/interrupt rules in their implementation. Those are not implemented
by this scaffold.

Run from the repository root:

```sh
unswbc run maps/arena.map examples/bahamut-scaffold bots/hunter-v20-portal-scouts
```
