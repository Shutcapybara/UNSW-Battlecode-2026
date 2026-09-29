# Ares V14 — escape only when enclosed

Ares V14 branches from V13 and retains its benchmark-aligned five-step reach probe, but activates open-room priority only when the current dragon is already enclosed (15 or fewer reachable cells). This keeps V09 target scoring unchanged while the dragon is in open space. Once enclosed, it prefers a legal post-move candidate above 15 cells; if no candidate clears that threshold immediately, it moves toward the candidate with the largest reachable area.

V13's initial Portals seat pair lost twice and reached zero pearls by r100, showing that applying open-room priority while currently safe blocks normal food routes. V14 limits the same escape rule to actual enclosed states.

Development gate: all 10 active maps, both seats, seed 1 against V09. Record exact `death_rate_enclosed_per1k`, W/L, r100 pearls/units/length, and sandbox points.
