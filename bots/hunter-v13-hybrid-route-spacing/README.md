# hunter-v13-hybrid-route-spacing

Python v12 fork that prefers current body-aware routes for teammate spacing,
then falls back to known static terrain routes when temporary bodies block the
live path, and finally to wrapped Manhattan distance when map knowledge is
incomplete. Pearl ownership remains body-aware.

Map memory stays sparse to avoid dense startup work. V13 itself exceeded the
judge CPU limit late in a 500-round `big_empty` mirror; see the results report.

Run from the repository root:

```sh
PATH="$PWD/.venv/bin:$PATH" unswbc run maps/arena.map \
  bots/hunter-v13-hybrid-route-spacing bots/hunter-v12-static-map-spacing
```
