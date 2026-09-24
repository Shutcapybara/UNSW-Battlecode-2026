# leviathan-v01-evaluator

Initial evaluator. Rejected: 0/8 wins against Fry and Kraken on arena/default_small.

Standalone Python bot, protocol 3. Run from repository root:

```sh
unswbc run maps/arena.map bots/leviathan-v01-evaluator bots/fry-v03-portal-hunters --sandbox
```

Parameters are in `weights.py`. Copy this directory into a new version before
changing behavior. No dependencies on other bot folders.

Design: `docs/leviathan/DESIGN.md`  
Evidence: `docs/leviathan/RESULTS.md`  
Iteration commands: `tools/leviathan/README.md`
