# Javert x03: game-relative policy consumption (F2/P3)

On top of x02, the policy consumes once-per-turn strategic facts:
openness (bounded reachable room around the head / room needed), phase
(round < space_phase_end), population saturation (units >= limit) and the
local length balance from the D2 field. REPRODUCE is demoted where openness
< 1 (no splitting into confined pockets); ATTACK approach value is boosted
while early and population-saturated with length balance not hopeless, and
an approach-only attack may then be selected instead of suppressed. The
executor and candidate rules are exactly x02's.
All javert-x0* cells share identical executable files except `settings.py`.
See [the Javert report](../../docs/javert.md) for the controlled study.
