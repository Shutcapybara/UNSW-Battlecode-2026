# Bahamut scaffold

Minimal Python starting point for the Bahamut series. All functions take no
arguments; strategy stages are `pass`. Only protocol input/output and the main
loop are implemented. The fallback moves straight ahead and sends four zero
sonar payloads; it has no collision avoidance or strategy.

`main.py` shows the complete flow. `game` and `turn` hold engine input;
`evidence` and `fields` persist; `work` resets each turn. Tiles are integer
tuples `(x, y, has_pearl, pearl_in)`. Body rows and edge grids retain wire-format
string tokens. Echo counts are ordered kelp, ally, ally head, enemy, enemy head.

Protocol framing follows the working Leviathan/Estuary loop and the official
[protocol 3 specification](https://game.battlecode.au/docs/protocol): optional
initial echoes, 64-bit sonar values, and one batched reply per turn.

Run: `unswbc run maps/arena.map bots/bahamut-scaffold bots/hunter-v20-portal-scouts`
