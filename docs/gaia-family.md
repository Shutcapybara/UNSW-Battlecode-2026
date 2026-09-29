# Gaia family notes

Gaia is a new strategy lineage forked from Rory's Fenrir line. The first
snapshot is `gaia-v01-safe-expansion`, based on the immutable
`fenrir-v20-crowded-resource-revalue` source.

Gaia's acceptance rule is deliberately evidence-based: each material change
gets a new immutable `gaia-vNN-*` directory, focused protocol tests, and a
bounded replay tournament. A later version is made only when the replay and
comparison results show a meaningful gain in early population, safe pearl
income, newborn survival, portal coverage, or visited-map area with zero
runner errors.

## Version 01: safe expansion

The first version adds deterministic opening lanes, conservative portal-scout
assignment, post-pearl escape checks, adaptive split sizing, renewable-bed
breeding-area detection, checked Gaia status sonar, anti-stall movement bias,
and a final legal-action fallback. It is intentionally Python because the
Fenrir planner is already a working Python snapshot; the fallback and tests
are the first gate before considering a C++ pathfinding port.

The Queen-of-Spades six-game screen was error-free but V01 scored 1–3. It
reduced wall deaths in its A-seat loss to Fenrir, but its B-seat opening was
asymmetric and it suffered more early head-to-head deaths. V01 is retained as
an immutable rejected control.

## Version 02: mirrored cautious opening

V02 mirrors the deterministic compass lane for team B and rejects marginal
opening head trades unless the dragon has a two-segment advantage. Its first
gate is the same Queen-of-Spades replay panel, followed by a small cross-map
screen if the early survival signal improves.

V02 also scored 1–3 with zero errors, so it remains a rejected control.

## Version 03: contact guard

V03 added an execution-boundary check for opening head-to-head actions, an
early enemy-contact buffer, and a fallback preference for ordinary safe moves.
It was error-free but also scored 1–3; the hard guard is retained in later
experiments because it addresses a real replay failure mode.

## Version 04: balanced density

V04 restores Fenrir V18's `density_ally = 0.25` valuation after V20's
`density_ally = 0.10` was documented as an aggregate regression. This is a
single-parameter test of the resource-crowding hypothesis.

## Version 05: late survival

V05 carries the V04 early-growth signal into the later game with a smaller
enemy/ally contact penalty, one-turn head blocking in flood fills, and a
slightly stronger local crowding charge. The acceptance question is whether
the round-100 lead survives without increasing runtime faults or suppressing
safe pearl income.

## Version 06: bounded breeding scan

V05 exposed a performance failure on Big Empty: every tile is a renewable bed,
so the unbounded detector timed out both directional games after the team
reached the 64-unit cap. V06 keeps only 64 evidence-ranked candidates and
rescans every eight rounds. This is a reliability/performance fix and must
pass the same replay screen before promotion.

## Version 07: population discipline

V07 stops routine post-opening production at 48 units on large maps while
retaining emergency and breeding splits, and adds a weak persistent lane bias
after round 100. The target is lower small-dragon churn and better map spread
once early growth has saturated.

## Version 08: parent-aware exploration

V08 consumes the parent-alive bit from Gaia status sonar. After a two-turn
grace period, a child whose parent status is stale switches to outward
exploration and receives an origin-distance bonus, so a dead parent does not
leave offspring turtling in the old split pocket.

The six-game Queen of Spades panel against Fenrir V20 and Bifröst V01 was
error-free and even at 2W-2L for Gaia. In the two Gaia-A wins, Gaia reached
12 dragons / 26 total length by round 100, collected 326 pearls, visited 652
cells, and finished with 11 dragons versus Fenrir's one. The B-seat remains
the limiting case: in the corresponding Gaia-B fixtures it reached only
2-5 dragons by round 100. The four-map Fenrir screen (Queen of Spades, Big
Empty, arena, default; both sides) was also error-free and finished 3W-5L;
Gaia won both Big Empty games and reached 64 units without the V05 breeding
detector timeout.

V08 is the historical retained baseline, but it is not promoted to the global
frontier: the evidence is map- and seat-sensitive. V47 now supersedes it as
the retained Gaia candidate within this experimental lineage.

## Version 44: compact-map sonar dispersion

V44 keeps V08's deterministic first-100 behavior, pearl safety, adaptive
splitting, breeding coordination, portal scout gate, and legal fallback. It
uses the existing density sonar field only after round 100, only on
non-large maps, and only when no enemy head is visible. Candidate moves then
receive a small tie-break toward lower allied density, so later explorers do
not all follow the same compact-map resource corridor.

The repeated four-map 24-game panel against Fenrir V20 and V08 was
error-free with no TLEs. V44 scored 9W-7L overall versus V08's 5W-11L;
against Fenrir both V44 and V08 scored 3W-5L, while V44 won the direct
V44-vs-V08 panel 6W-2L. Turn-100 Fenrir curves were unchanged on the large
map and the compact-map opening remained governed by V08. V44 was retained for
further benchmarking at that point; V47 now supersedes it within the Gaia
lineage and is still not a global frontier promotion.

## Version 47: medium-map threat-aware pearl gate

V47 restores the bounded enemy-threat exit check for visible pearls, but only
on ordinary compact maps from 400 through 1,999 cells. Tiny arenas retain
V44's geometry-only pearl rule because strict threat gating over-constrained
their already narrow opening. Big Empty also retains V44's saturated
throughput policy; the large-map threat gate had reduced round-100 pearl and
growth output in V46.

The four-map 48-game panel was repeated with identical standings: V47 scored
13W-11L, V44 scored 12W-12L, V08 scored 8W-16L, and Fenrir scored 15W-9L;
all 96 matches across the two runs had zero runner errors and zero TLEs. V47
beat V44 directly 5W-3L and matched V44's 3W-5L against Fenrir. The candidate
therefore becomes the retained Gaia version for continued testing.

The follow-up Arena controls did not improve the Fenrir match-up. V48 delayed
tiny-map splits until a checked 3+2 placement, V49 added a zero-exit opening
guard, and V50 delayed again for a 3+3 placement. Each lost both Arena games
against Fenrir; their 12-game comparison panels scored 2W-4L, 2W-4L, and
1W-5L respectively. These controls show that split timing alone does not fix
the remaining Arena head-to-head losses.

## Versions 51–53: opening and breeding controls

V51 added a bounded sonar enemy-density penalty during rounds 20–99 when no
enemy head was visible. Its 12-game Arena/Queen screen scored 2W-6L versus
Fenrir and 3W-5L for V47, with zero errors, so it was rejected as too weak to
justify changing the deterministic opening.

V52 added absent-to-present pearl transition counts to breeding-area scoring.
The full 48-game four-map screen completed with zero errors and zero TLEs:
Fenrir scored 16W-8L, while both V47 and V52 scored 11W-13L. V52 beat V47
directly 5W-3L and had slightly lower average deaths and newborn deaths, but
lost to Fenrir 2W-6L, so the spawn-rate detector remains a useful control and
is not promoted.

V53 tested a team-local mirrored opening lane only on the 121-cell Arena map,
where one A/B starting dragon shares a central corridor. Its 24-game
Arena/Default screen was error-free; V53 and V47 both scored 5W-7L, and both
lost all four Fenrir fixtures. The map-specific lane change is rejected.

V54 extended team-local lanes to medium compact maps. It tied V47 overall at
5W-7L in its 24-game Queen/Default screen and lost all four Fenrir fixtures;
the direct 3W-1L gain over V47 came from shifting results between Queen and
Default, so it was not retained. V55 broadcast repeated spawn-transition
evidence through Gaia guidance sonar; its 36-game screen tied V52 at 9W-9L
and produced identical round-100 and final replay metrics, showing no useful
remote breeding effect.

V56 moved the deterministic portal-scout start from round 100 to round 50.
It beat V47 directly 4W-2L on Portals, Autarky, and Default and increased
portal traversals, but lost all six Fenrir fixtures and had higher deaths; it
remains a portal control rather than a main-line promotion.

V57 required length-five parents for three-segment opening children on medium
maps. Its full 48-game panel tied V47 at 10W-14L; round-100 population fell
from 23.08 to 20.79 dragons on average despite a modest h2h-death reduction.
V58 enabled that larger child only when an enemy head was visible and also
tied V47 at 11W-13L in the full panel. V59 narrowed the trigger to four cells
and fell to 5W-7L in its focused screen. These split controls reduce some
newborn risk but do not yet improve efficient growth.

V60 added a bounded escape-margin bonus among already-safe pearls, but scored
3W-9L in its focused screen. V61 and V62 ranked simulator-legal fallback
moves before the terminal unchecked direction; both completed their 18-game
screens with zero errors but scored 3W-9L, so the reliability experiments did
not change strategic quality. V63 withheld opening pearl gossip while keeping
bed, density, portal, and status sonar; it tied V47 and Fenrir at 6W-6L with
identical round-100 and final metrics. None of V54–V63 meets the promotion
gate.

## Post-V63 Arena diagnostics (not releases)

A temporary trace copy of V47 confirmed a concrete Arena failure mode: during
the first 30 rounds, some selected ordinary moves landed in the visible
enemy-reach map before the later equal-length head collisions. Three narrow
prototypes were screened without adding bot snapshots: an immediate-threat
execution veto, a minimum-three-segment Arena child when legal, and a stronger
team-local opening lane force. Each lost both Fenrir Arena orientations
(0-2); the lane force extended one Gaia-side game to round 69 but still lost
and increased newborn/body churn. These were rejected as strategy changes,
not promoted as Gaia versions. The four-game V47 Arena/Default safety check
also completed 0-4 for Gaia with zero errors, zero invalid actions, and zero
timeouts. The trace supports further newborn-siting work, but does not yet
justify changing the retained all-map candidate.

Two score-level follow-ups were also rejected without creating snapshots. A
distance-2/3 contact-penalty relaxation lost all eight Fenrir orientations and
gave up both Big Empty wins; reducing the opening near-contact charge and
removing the late contact charge likewise scored 0-8. Both remained
error-free, so the result is a strategy regression rather than a runtime
failure. The retained contact policy remains unchanged pending a more
targeted newborn-route improvement.

The later opening diagnostics use the serial tournament harness (`--jobs 1`)
because concurrent low-level runs were not reproducible: a temporary visible
pearl-value control appeared to win 8-0 in parallel, but its replay-producing
and serial runs scored 0-8. Under the serial gate, V54's four-way team-local
lane fix, head-block removal, no-lane control, contact relaxations, and shared
pearl eligibility all lost their focused Default/Queen screens with zero
errors. The action trace explains the remaining gap: Gaia rejects cells in
the enemy next-turn reach map while Fenrir enters them. No unsafe relaxation
was promoted.

## Version 09: global-ID mirror control

V09 tested a direct global-ID 180-degree opening rotation. It remained
error-free and split 1W-1L against Fenrir on Queen of Spades, but its B-seat
round-100 result (4 dragons / 11 length) did not improve enough to retain the
variant.

## Version 10: team-local mirror control

The map roster interleaves initial IDs as A0, B1, A2, B3. V10 derives the
team-local index and assigns A north/east lanes and B south/west lanes. This
corrects the lane-duplication bug in V08, but the two-game Queen screen was
0W-2L despite zero runner errors. It remains an immutable diagnostic control;
the lane correction needs a stronger safety result before promotion.

## Runtime and C++ decision

V05 exposed a genuine large-map timeout because breeding detection scanned and
clustered every renewable tile. V06 bounded the evidence set to 64 candidates
and rescanned every eight rounds in Python; V47 completes the repeated Big
Empty screen under the tournament timeout with no invalid-action errors. Since
the bounded Python planner is reliable and fast enough on the measured maps,
there is no current justification for a C++ port. A future version should
switch the pathfinding core to C++ only if a bounded benchmark reproduces a
timeout or invalid-action failure after these guards.

## Versions 11–26: follow-up screens

The later experiments were kept as immutable controls rather than silently
folded into v08:

- V11 added enemy-threat awareness to post-pearl escape checks. It reduced
  some Big Empty collision losses but scored 1W-7L on the four-map Fenrir
  screen.
- V12 fixed the known lane duplication by spreading global IDs across four
  sectors. Its Queen B fixture reached 8 dragons / 18 length at round 100,
  versus v08's 5 / 10 in the comparable screen, but its four-map result was
  1W-7L.
- V13's close-start retreat bias scored 2W-6L; V14's breeding traffic cap also
  scored 1W-7L. V15/V16's opening threat vetoes and V17's persistent sector
  hold were too restrictive and scored 0W-8L.
- V18's casualty retreat, V20/V21's tighter post-opening population caps, and
  V22/V23's combined or size-gated opening-room variants did not beat v08.
- V19's relaxed opening flood check improved one Default seat from 11 / 23 to
  15 / 30 at round 100, but a direct v08-v19 panel favored v08 5W-3L because
  the extra early population collapsed later.
- V24's late threat spacing was too passive (0W-8L). V25's smaller adaptive
  child-room floor reproduced v08's metrics exactly, and V26's contextual
  opening-room rule remained 1W-7L.
- V27 kept the v08 opening and used four-way sectors only after round 100. It
  improved one Default seat's visited area and pearl count, but scored 2W-6L;
  V28 weakened that late sector bias and returned to 1W-7L.
- V29 re-checked child room with a bounded, uncontested-opening fallback. It
  completed the focused and four-map panels with zero errors, but tied v08 at
  3W-5L on the focused panel and 3W-5L against Fenrir; retain it as a split
  control, not a promotion.
- V30 hard-blocked unknown first edges during the opening. It had no TLEs or
  invalid actions, but over-restricted frontier expansion and fell to 1W-7L;
  reject it. V31 changed that to a soft unknown-edge penalty and again tied
  v08 at 3W-5L without changing the measured early curves enough to promote.
- V32's known-only pearl flood was too conservative (1W-7L); V33's fractional
  unknown-room credit improved that only to 2W-6L. V34's B-only four-way lane
  improved one Queen B turn-100 curve but did not improve the panel; V35/V36's
  small-map reproduction caps likewise remained controls.
- V37 corrected breeding evidence to count pearl spawn transitions rather than
  repeated bed visibility. It improved selected Big Empty pearl/death curves
  while remaining bounded, but scored 2W-6L on the compact-map screen. V38's
  portal slots overused learned portals and was rejected; V39–V41's split
  occupancy guards were too restrictive. V42 improved direct spreading but
  lost all eight Fenrir games in its four-map screen; V43/V44 progressively
  gated that density signal, with V44 passing the repeated 9W-7L gate before
  V47 added the medium-map threat-aware pearl gate. V45's tiny-arena opening
  population cap fell to 1W-5L on its Arena screen and was rejected; V46's
  all-map threat gate tied V08 at 9W-15L in its full panel because Big Empty
  throughput regressed.

These results support retaining V47 as the current Gaia candidate while the
lineage continues to seek a stronger all-map result. All tested versions
completed with zero runner errors; the limiting issue is strategy quality, not
protocol reliability.

Baseline and candidate replay artifacts belong under ignored `build/` folders.
Do not add replay payloads or generated run state to source control.
