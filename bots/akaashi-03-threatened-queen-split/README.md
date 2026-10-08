# Akaashi 03 — dodge threatened queen splits

Fork of immutable `akaashi-02-queen-strike`, preserving its visible queen
attacks and Akaashi 01's escape safety. Atlas stays disabled.
Experimental local candidate; deployed Akaashi 01 remains submission 20222.

When a queen split would leave her head in an observed enemy's bounded
sprint reach, ask for a dodge at any round. The replacement must pass the
same six-step survival horizon; existing risk ranking chooses the direction.
Safe production splits and necessary cage splits remain available. The
previous unconditional late-game split-to-dodge behavior is retained.

Incomplete or missing enemy body information receives four-step bounded
reach, rather than an optimistic short default. Each enemy reach search has
its own visited mask, so overlapping marked regions cannot suppress another
enemy's traversal. This is conservative threat coverage, not a guarantee
against arbitrarily long sprints or every adaptive enemy action.

Trigger: Trophy match 1407768, team A, protocol round 109. Queen 0 at (19,11)
splits while enemy 51, whose visible body is incomplete, is at (19,14).
Its NNN sprint kills our stationary queen later that same round. 03 selects
north to (19,10). An official-engine branch using the exact original prefix
and then native 03 only for queen 0 keeps her alive and wins against the
remaining scripted actions. This is a targeted regression, not a strength
claim against responsive play.

Tests:

```sh
python3 tests/test_akaashi_threatened_split.py
python3 tests/test_akaashi_queen_escape.py
python3 tests/test_akaashi_queen_strike.py
```

See [family evidence](../../docs/akaashi-family.md). Replay/probe/branch
artifacts remain under `build/queen-strike-1407768/`.
