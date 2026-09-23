# Child-count comparison

For **every bot against every other bot on every map**, use
`python3 bots/tournament.py` from the repository root. It runs both sides and
saves results, a leaderboard, logs and replays. See the root README for subset
selection, dry runs and resuming interrupted tournaments. Use `--jobs 8` to
run eight matches at once (default: up to four).

These are standalone snapshots of the bot, differing only in their proactive
child target. Every child repeats its variant's rule. Both variants retain
emergency splitting, so the target is not a lifetime cap on all splits.

- `one-child/`: creates one two-segment child as soon as legal.
- `two-children/`: creates two two-segment children as soon as legal, one per turn.

Run from the repository root:

```sh
unswbc run maps/arena.map bots/one-child bots/two-children
unswbc run maps/arena.map bots/two-children bots/one-child
```

Run every map with sides swapped:

```sh
python3 bots/compare.py
```

Results, logs and replays are saved in `build/child-comparison/`. Results compare
these snapshots only: later edits to the main bot do not update them automatically.
Each map is played once in each order; this is a small benchmark, not proof that
one strategy will beat other teams. The main bot remains independently editable.

Each version can also be submitted directly:

```sh
unswbc submit bots/one-child
unswbc submit bots/two-children
```

## Other strategies

- `portal-hunters/`: based on dragon-hunters, with planned portal round trips
  that collect current and upcoming pearls and reserve an exit route.
- `dragon-hunters/`: a self-replicating aggressive swarm that hunts enemy
  heads, spreads friendly dragons across the map, uses close-range face-off
  sonar, and treats pearls as a secondary objective.
