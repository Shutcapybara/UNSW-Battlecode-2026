# formatted-hunter-v22-python

Python semantic port of the structured C++ Hunter V22. It keeps the same macro
boundaries while making the execution functions directly importable from
Python:

```text
main.py
src/
  core/
    config.py              policy and feature parameters
    model.py               shared decisions and state types
  state/
    world.py               protocol ingestion and persistent world state
    features.py            EWMA density and terrain safety
  communications/
    sonar.py               64-bit packet encoding
  brain/
    decision.py            require/fire_on framework
    policy.py              execution priority and fallback selection
    decisions/             independently editable execution scripts
```

Implemented in the first port:

- visible ally/enemy count EWMAs;
- timestamped, positioned density sonar packets;
- bounded terrain-safety flood fill and enemy reach;
- attack, threat-aware survival, crown growth, move-aside, split, forage, and
  frontier exploration executions;
- single-write Protocol 3 output.

Intentional parity gaps relative to the C++ V22:

- portals are treated as blocked instead of using the 18-step round-trip beam
  planner;
- boost surround/trap tactics are not yet ported;
- density packets are emitted but remote density fusion is not yet implemented;
- crown, hotspot, coverage, and scout-claim packet families are not yet ported.

Example imports from inside the bot:

```python
from src.brain.decisions.attack import Attack
from src.state.features import local_safety
from src.state.world import World
```

Run from the repository root:

```sh
unswbc run maps/default_small.map bots/formatted-hunter-v22-python bots/formatted-hunter-v22
```
