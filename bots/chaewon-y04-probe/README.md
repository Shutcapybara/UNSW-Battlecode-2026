# chaewon-y04-probe

Parent `chaewon-y02-atlas` (yuna-v05-core + atlas + newborn fix). Adds the **portal probe**: when the chosen move
leaves our head next to a portal whose landing we cannot see, the dragon casts that one ray alone (a ray passes
through portals and stops at the first dragon part); next turn the echo is attributable to it. Clear line →
blind-exit risk × `probe_clear_mult` (0.2); a dragon on the line → at least `probe_block_pb` (1.0) × V(me).
Not while crown, not on split turns.

Panel (8 live maps × 2 sides × {sinbad-v07, gavroche-v32} × seeds 1–3, 96 paired fixtures): **+0.062 vs yuna-v05**
(20 better / 14 worse, p = 0.39); Dilemma +0.50, Queen of Spades +0.42. Portal-step deaths per game unchanged
(35.9 vs 31.6): the probe is one round stale exactly when two dragons approach a portal pair from both sides.
