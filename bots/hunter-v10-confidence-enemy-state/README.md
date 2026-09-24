# hunter-v10-confidence-enemy-state

Python v09 fork that timestamps visible enemy body-count lower bounds. Recent
sightings decay and expire after 20 rounds, so a hidden enemy observation
cannot indefinitely affect the late-game growth threshold. Attacks continue to
use only body counts visible this turn.

It inherits v09's sparse observed-edge cache, incremental portal index, and
on-demand neighbor calculation to reduce large-map startup work. This does not
rule out intermittent runtime timeouts; see the V09 notes in the results report.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v10-confidence-enemy-state bots/hunter-v09-confidence-team-state
```

V10 addresses the stale enemy size estimate identified in the strategy backlog.
Its tournament will compare it with the current v09 candidate and the v06/v08
references.
