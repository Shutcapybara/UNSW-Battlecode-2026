# Child-count comparison

The repository contains hundreds of historical bot snapshots. Select a small
roster explicitly when using `python3 bots/tournament.py`; large schedules
require `--allow-large`. The runner plays both sides and saves results, a
leaderboard, logs and optional replays. See the root README for dry runs and
resuming interrupted tournaments.

These are standalone snapshots of the bot, differing only in their proactive
child target. Every child repeats its variant's rule. Both variants retain
emergency splitting, so the target is not a lifetime cap on all splits.

- `fry-v06-one-child/`: creates one two-segment child as soon as legal.
- `fry-v07-two-children/`: creates two two-segment children as soon as legal, one per turn.

Run from the repository root:

```sh
unswbc run maps/arena.map bots/fry-v06-one-child bots/fry-v07-two-children
unswbc run maps/arena.map bots/fry-v07-two-children bots/fry-v06-one-child
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
unswbc submit bots/fry-v06-one-child
unswbc submit bots/fry-v07-two-children
```

## Other strategies

- `fry-v03-portal-hunters/`: based on fry-v02-dragon-hunters, with planned portal round trips
  that collect current and upcoming pearls and reserve an exit route.
- `fry-v02-dragon-hunters/`: a self-replicating aggressive swarm that hunts enemy
  heads, spreads friendly dragons across the map, uses close-range face-off
  sonar, and treats pearls as a secondary objective.
