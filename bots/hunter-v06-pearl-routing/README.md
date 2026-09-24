# hunter-v06-pearl-routing

Python Hunter fork of v05. It compares visible route distances when assigning
pearls to teammates, and gives food routes more weight than friendly separation.
Exploration retains v05's spread preference.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v06-pearl-routing bots/hunter-v05-safe-attack-routes
```

V06 scored six more points than v05 over 40 comparable matches in the shared
v04/v05/v06 pool. The later v08 snapshot ties v06's tactical score and carries
a wider sonar ID field. See [the tournament report](../../docs/hunter-python-results.md).
