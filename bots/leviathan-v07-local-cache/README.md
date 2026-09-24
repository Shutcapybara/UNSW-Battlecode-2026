# leviathan-v07-local-cache

Current candidate. V06 evaluation with local geometry-cache invalidation and cheaper neighbor lookup. See the results ledger for validation and limitations.

Standalone Python bot, protocol 3. Run from repository root:

```sh
unswbc run maps/arena.map bots/leviathan-v07-local-cache bots/fry-v03-portal-hunters --sandbox
```

Parameters are in `weights.py`. Copy this directory into a new version before
changing behavior. No dependencies on other bot folders.

Design: `docs/leviathan/DESIGN.md`  
Evidence: `docs/leviathan/RESULTS.md`  
Iteration commands: `tools/leviathan/README.md`
