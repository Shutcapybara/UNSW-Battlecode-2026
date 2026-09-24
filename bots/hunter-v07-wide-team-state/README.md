# hunter-v07-wide-team-state

Python v05 fork testing a wider sonar message: 20-bit lifetime dragon IDs,
length, coordinates, and round fit in the 64-bit protocol. It rejects stale,
invalid, and out-of-order teammate updates while preserving `MOVE_ASIDE` on
the forward channel.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v07-wide-team-state bots/hunter-v06-pearl-routing
```

V07 regressed against v06 in the 11-map small pool. V08 combines the corrected
sonar with v06's pearl routing and ties v06's tactical score. See [the report](../../docs/hunter-python-results.md).
