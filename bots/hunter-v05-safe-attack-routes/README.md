# hunter-v05-safe-attack-routes

Standalone Python port of hunter-v04-team-state-sonar. The bot keeps the
team-growth and portal behavior, directional sonar, and conservative size-aware
hunting. Attack searches now stop at unsuitable enemy heads, use only fresh
visible enemy body counts, and do not commit partial paths beyond the current
movement budget.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v05-safe-attack-routes bots/hunter-v04-team-state-sonar
```

V05 is the safe-attack Python snapshot. The v06 pearl-routing experiment
scored six more points than v05 across 40 comparable small-pool matches. See
[the Python Hunter results](../../docs/hunter-python-results.md) before choosing
a release version; small tournaments do not establish broad superiority.
