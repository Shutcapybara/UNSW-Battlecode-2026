# Ares V32 — save the long child at a dead end

V32 branches from V31. Match 658569 showed a length-4 head splitting before the last pearl, then reaching the endpoint as length 3 and dying. V31's A-side Autarky replay delayed the split until after the pearl, but still split off a two-segment child; the original length-3 head then wall-died while the child survived.

V32 retains the feed-before-split guards. At a critically enclosed endpoint where every one-step head move is dead, it searches from the largest possible tail child down to two segments. It selects the largest child with an open exit and enough forecast room, leaving the trapped original head as the smaller half. This allows a length-5 dragon to collect the final pearl, split 3+2, and send the three-segment child back out of the dead end.

Development screen: Autarky, A side, V32 versus V28, seed
`0x84ed9bbaf7053078`. V32 won in 233 rounds with no runner errors. Dragon 61
moved west onto the final pearl at round 65, then split 3+2 at round 66
(`SPLIT 3`): child 76 moved south out of the dead end while the original
length-2 dragon wall-died at round 67. Child 76 later lost a head-to-head at
round 102, away from the dead end. This single A-side game verifies the split
orientation; it is not a broad strength or promotion result. The replay and
decoded review are under
`build/ares-v32-dead-end-screen-658569-seed1/`.


## Direct V19 screen

The ten-map, both-seat sandbox screen against Ares V19 used unswbc 1.2.2 and
seed 1. V32 won **11–9**, with no runner errors. All 20 replays decoded and
matched the saved game results. V28 scored 12–8 on the same panel, so V32 keeps
a positive V19 result while changing the target dead-end behavior. This is one
deterministic seed, not a broad promotion result. The games and replay reviews
are under `build/ares-v32-vs-v19-all10-seed1-20260930/` and
`build/ares-v32-vs-v19-replay-review-20260930/`.
