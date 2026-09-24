# hunter-v15-shared-territory

C++ fork of Hunter V14. Dragons merge SONAR messages into a small replicated
team state rather than keeping a list of individual SONAR reports. The state
includes the largest known friendly and enemy lengths, the current friendly
unit count, an observed enemy count lower bound, pearl spawning sites, visited
map sectors, and portal endpoints that teammates have found. A portal is marked
safe after a dragon completes a return crossing. Messages cycle over four directions each
turn, so nearby dragons receive different parts of the state over time.

Pearl spawning sites are tiles with a pearl or a nonnegative spawn countdown.
Nearby sites are scored as a hotspot. Scouts use these reported hotspots,
unscouted sectors, unexplored edges of their visible area, and distance from
friendly dragons when choosing an exploration route. At four or more friendly
units, a dragon up to length three can scout portals when a larger teammate is
known, or any dragon can scout when the team has at least 16 units to spare.
Exploration-only portal trips pause when the team knows a dense pearl hotspot.
A scout observes the far side after crossing and plans a return or onward route
from its new view. It never assumes a remote endpoint is immediately safe
merely because another dragon reported it.

The SONAR channel holds one 64-bit value per direction per turn. This is a
rotating summary of useful facts, not a literal copy of every dragon's map.
Summary reports expire after 20 rounds. Pearl sites and portal endpoints are
static map facts and are rebroadcast periodically. Tactical collision and
route checks still use each dragon's current view.

Build and run from the repository root with the installed toolkit:

```sh
.venv/bin/unswbc run maps/arena.map bots/hunter-v15-shared-territory bots/hunter-v14-cpp-hybrid-route-spacing
```
