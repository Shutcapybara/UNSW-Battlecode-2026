# esquie-04-crit-split

Esquie M-1 Part 3, second mechanism, target cluster: the corridor/kelp leak maps
(Slithery trapped 101.3 / Portals 81.9 / Devil 68.8 per 1k dragon-turns, rounds 0-99).

The teammates' `ares-v19-critical-enclosure-split` mechanism ported onto `esquie-01-nodevil`:
a five-step body-blocked BFS reach probe (occupied-by-others + own body except head block); when
the current reach is <= 8 cells AND the best-scoring legal move still ends at reach <= 8, fire
the base's own tail escape split (`tyr_escape_split`) instead of moving. Switch-off is the parent.

Their evidence (20-game screens vs V09): 11-9, trapped length loss 55.1->49.9 per 1k dt,
<=8-band hazard 679.6->615.0, Slithery trapped 103.9->82.8, Portals 65.0->75.8, pearls -3 %.
The missing step per BASELINES item 4 is the fixed 160-panel + generalisation panel, paired -
this version.
