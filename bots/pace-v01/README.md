# pace-v01

Parent: `chaewon-y04-probe`; copied with attribution, then modified only for
pace scoring, child survival guards, newborn-neck anchoring, and the empty
action-set salvage fallback.

Strategy — Public-corpus zero-filled medians set the compact/open targets:
units r25/r50/r100 = 6/6, 9/9, 13/15; total length r250 = 0/54.5. The bot did
not attain them: median units r100 were 5 compact and 11 open; median open
total r250 was 2. The live record was unavailable. See findings for quantiles
and survival. Conversion funnel: not applicable.

Execution — Host foraging, portals and production remain. `ACT:pace+` marks
production pressure and `ACT:pace-` marks held splits; markers occurred in
357/360 pace games. Pace vs host scored −0.483 over 354 valid exact pairs
(5 better, 176 worse, 173 tied); pace-nolimit scored −0.514. Survival guards
improved median self+wall deaths from 8.545 to 6.264 per 1,000 turns and
newborn losses from 27.27 to 26.49 per 100 splits, but missed limits of 5 and
10. Direct win-share difference pace minus no-limit was +0.028.

Implementation — unswbc 1.2.2 and 1.0.0 metered probes all passed with zero
faults and zero `MC_ERROR`. Across Schooltime A, Portals B, Slithery Fight A,
and Trauma B, max ranged 61.6–76.4M and p99 46.5–59.8M. Exact per-fixture
turns, p99 and max are in the findings file. When all moves are certainly
lethal and only a verified escape split remains, the controller keeps that
split instead of returning an empty action set.

State — `world.py` owns body/occupancy, pearl and bed memory, portal pairs,
rosters and visible threats; `policy.py` consumes these for movement and
splits. `roles.py` consumes crown/handoff state. `yuna.py` stores the newborn
parent-pocket anchor and target hysteresis; no new state packet was added.

Messaging — No new packet kinds. Existing CROWN and HANDOFF packets feed
`roles.py`; PREY feeds prey state in `world.py`; FOOD updates pearl/bed memory;
PORTAL updates `world.learn_pair()`; DENSITY feeds `density.py`. Median total
sonar rays per game were 23,108 host, 5,216 pace and 4,306 pace-nolimit (shorter
survival explains much of the drop); this is rays, not decoded packet count.
No messaging ablation was run.

Momentum — Host target hysteresis remains; `note_birth()` fixes the newborn
neck anchor by adjacency. This probe did not ablate those mechanisms. No
certificate packet or momentum term was added.

Panel caveat — The 1,080-game panel was measured before the rare empty-action
fallback repair, except the two pace/Schooltime/Sinbad seed-1 sides rerun after
repair. Six host/Ouroboros/Slithery games timed out at 600 seconds. Results,
paired deltas, target attainment, model coefficients and the next-build
recommendation are in `docs/findings/2026-09-29-pace-v01.md`.
