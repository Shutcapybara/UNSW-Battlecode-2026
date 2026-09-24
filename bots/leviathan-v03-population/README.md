# leviathan-v03-population

Removed the map-area population cap. Better production; evaluator still wasted pearls on sprinting.

Standalone Python bot, protocol 3. Run from repository root:

```sh
unswbc run maps/arena.map bots/leviathan-v03-population bots/fry-v03-portal-hunters --sandbox
```

Parameters are in `weights.py`. Copy this directory into a new version before
changing behavior. No dependencies on other bot folders.

Design: `docs/leviathan/DESIGN.md`  
Evidence: `docs/leviathan/RESULTS.md`  
Iteration commands: `tools/leviathan/README.md`
