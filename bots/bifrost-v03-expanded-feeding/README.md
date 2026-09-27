# Bifröst v03 — expanded crown feeding

This variant retains Bifröst v01's crown-claim timing and portal-memory policy.
It tests the late feeding half of Avery v08's measured crown-race schedule:
from round 400, dragons up to length 20 can seek a known crown from 30 cells
away and feed when within two cells. On compact maps the original
map-size-based feeding time still applies when it is later than round 400.

The previous v02 variant showed that moving crown claims to round 220 caused
early losses on several maps. v03 isolates late feeding to test whether the
Big Empty crown gains can be retained without that early-growth cost.
Family-level matchup observations and iteration status are tracked in the [Bifröst family notes](../../docs/bifrost-family.md).


## Test result

Rejected after a 120-game focused screen: 72 wins and 48 losses, with no errors or runtime faults. It lost 3–9 to Bifröst v01. On 108 common external fixtures with exactly matching seeds, v01 scored 88–20 and v03 scored 69–39 (8 gains, 27 regressions). Expanded late feeding is not retained. See the [benchmark report](../../experiment_data/bifrost-v03-expanded-feeding_20260927115819514324/summary.md).
