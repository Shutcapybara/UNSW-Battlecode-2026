# hunter-v08-pearl-wide-sonar

Python v06 strategy with the v07 64-bit sonar format. The 20-bit ID prevents
lifetime dragon IDs from aliasing; message age and ordering checks reject stale
or older teammate observations. Pearl ownership still compares visible route
distance and food routes retain the v06 scoring preference.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v08-pearl-wide-sonar bots/hunter-v06-pearl-routing
```

On the completed 11-map pool, v08 and v06 tied at 24 wins and 20 losses.
V08 is the current Python candidate because it corrects sonar ID aliasing; this
small sample shows no tactical win-rate gain over v06. See [the report](../../docs/hunter-python-results.md).
