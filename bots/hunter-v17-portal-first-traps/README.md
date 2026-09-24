# hunter-v17-portal-first-traps

C++ fork of the measured Hunter V16 candidate. V17 gives a planned portal
route priority over a boost-and-trap attack so attacks do not interrupt an
ongoing portal trip. If no portal move is available, V16's surround and cutoff
attacks remain available with their existing size and safety checks.

Build and run from the repository root:

```sh
.venv/bin/unswbc run maps/help.map bots/hunter-v17-portal-first-traps bots/hunter-v16-boost-traps
```
