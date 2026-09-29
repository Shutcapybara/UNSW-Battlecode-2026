# Ares V11 — undersized-room penalty

Ares V11 branches from Ares V09. It keeps V09 route and target selection, but makes its existing time-aware room probe reach the full post-move body when that is larger than the normal room target. If that reachable room cannot fit the body, the existing enclosure penalty is no longer reduced by the farm discount. Farm discount behavior remains unchanged when the body fits.

This addresses the trapped/mill leak while limiting the change to moves that can strand the current dragon in a room smaller than its body. It does not add a hard movement filter or change any other policy.

Development gate: compare V11 with V09 on matched Portals, Slithery Fight, and Schooltime seats. Track wall/enclosed deaths, pearl rate, r100 units and length, W/L, and sandbox points.
