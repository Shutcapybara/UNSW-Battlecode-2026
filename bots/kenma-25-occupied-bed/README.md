# Kenma25 — respect bed occupancy in the no-reserve pocket controller

Parent20, changing only the next-round bed-pressure calculation. A known bed whose timer expires next round creates pressure only if the queen's projected body leaves it uncovered. The engine suppresses pearl spawning on occupied beds.20 ignored occupancy and unnecessarily shrank all8 tested queens to2; once shrunk, a long bed timer can prevent regrowth for the rest of the game.25 retains length3 when its own body safely covers the due bed. Exposed beds, current unconsumed food, stale views, final-turn growth and split/donor rules keep20 behavior. There is no global reserved slot.

This uses only current legal observations and the candidate's exact simulated body, no map identity or hidden timer layout. It remains a hypothesis: when a genuinely exposed bed forces a shrink, final length2 may still lose against another keeper. Unknown future actions are not predicted. No new best claim.

Status: prepared, unmeasured. Check covered/exposed synthetic beds and all three recorded fatal-meal warnings before a bounded Schooltime smoke. Reserved seeds11–13/new maps untouched.

Preflight passed under ASan/UBSan: covered bed preserves3, exposed due bed shrinks, remaining food/stale view/final-turn rules. All three recorded fatal-meal protocols still request preventive sprint at130/371/290. Runtime9f5ed4f094672561cfdff23e165104c6094de4677a68248453e61f0a103725c7. Eight Schooltime games (both seats,seeds1/2/3/5) running; all retained replays will be read.

Smoke complete8–0, zero errors, all8 replays read. All queens survive: length3 in both seats of seeds2/3, length2 in both seats of seeds1/5, versus20 ending2 in all8. Thus occupancy correction improves the intended mechanism but still risks losing ties against length3 keepers. Full screen held; preserve as an experiment. Output k25-schooltime-s1235/score.json and k25-smoke-diagnostics.json.
