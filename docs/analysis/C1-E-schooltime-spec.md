# C1-E (a) — the Schooltime opening of the top ten, described from replays

Ten top-ten ranked Schooltime wins (29 Sep corpus), read from the cached frames with
`tools/analysis/c1e_schooltime.py` (re-derivable: `~/.venvs/bc122/bin/python tools/analysis/c1e_schooltime.py`,
raw dump in `build/c1e/schooltime_anatomy.jsonl`). Five of the ten are **swarm wins** (48–64 units at r100;
teams 70 ×2, 306 ×2, 91) — those carry the lever. The other five (units 10–32) are the same teams winning without
the swarm against weaker opponents; team 70 won both ways, i.e. it version-switches on Schooltime.

## The map in numbers

60×40, 12 portal pairs, 3 initial dragons per side (length 4 each). **444 live bed cells** (identical in both
layouts; the local `maps/schooltime.map` has only 326 — use `game_stats/live_beds.json`). Beds begin spawning in
rounds 0–2 but trickle: the first pearl is *eaten* at r19–31 (median ~21). At median bed rates the whole field
produces ~1.7 pearls/round; the swarm winners harvest 2.0–3.3/round by r60+ — essentially everything that spawns
on their half. The harvest, not headcount, caps the swarm.

## The opening timeline (median of the five swarm wins)

| round | 0 | 5 | 10 | 20 | 30 | 40 | 50 | 60 | 70 | 80 | 90 | 100 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| units | 3 | 6 | 6 | 6 | 6 | 8 | 13 | 20 | 31 | 48 | 53 | 58→64 |

1. **r0–5 — split the starters immediately.** Each initial length-4 dragon splits 4→2+2 → six length-2 workers by
   r5. (Every swarm game opens with exactly 3 splits in r0–10.)
2. **r5–45 — travel, don't grow.** Units sit at 6 for ~40 rounds. The workers drive to bed fields; the first pearl
   lands ~r21. A few children born in r20–40 die (no economy yet); net units don't move.
3. **r45–100 — the flywheel.** Pearl → length → split at 4 → new worker claims another bed → more pearls. Units
   double every ~10–15 rounds: 8 at r50, 20 at r60, 31 at r70, 48 at r80, ~58–64 by r90–100 (the 64-dragon cap).
   84 % of all pearls eaten by r100 arrive in rounds 50–100 (167–315 in that window).

## The split rule

Split the moment length reaches 4, into 2+2. Across the five swarm games 95 %+ of splits are before=4 → parent 2,
child 2 (residual: before 5–6 when two pearls land in one turn). Children are always length 2. There is no other
production rule: no big-children, no reserve, no timing schedule — the schedule is pearl-gated, not round-gated.

## Where the children go

**They stay home.** Median net displacement from birthplace after 60 rounds is 4–10 cells. A child inherits its
parent's neighbourhood and takes the nearest unclaimed bed cluster (≥ ~3 cells from allied heads); at r100 the
median distance to the nearest allied head is 2 and 86–100 % of heads sit within 2 cells of a live bed. Workers
move nearly every turn (95 %+ of rounds; only ~4 % stays) — they **patrol** a ~5×5 area around their bed cluster,
not camp: they loop locally and eat each pearl the round it spawns. With ~50 heads each covering a 5×5 patch,
~50 % of the 444 beds are inside the swarm's patrolled area by r100 (35–59 % across games).

## Portals

Portal coverage is a *by-product*, not a plan: beds are not preferentially near portals (median bed→portal 4 vs a
grid baseline of 5), and as the bed-patrol spreads, 11 of 12 pairs end up within 3 cells of a head by r100
(from 4 of 12 at r25–50). Transits are opportunistic: 28–54 per 100 rounds in four games, **6 in team 91's 48-unit
win** — near-zero portal use still reaches the cap. Portal discipline (C1-D) matters more for *not dying* than for
coverage. Transit use rises late (13 in r90–99 alone in game 497728) as the free half fills up.

## Body avoidance at 40–64 units

The structure is the avoidance mechanism; there is no visible explicit collision protocol beyond it:

- **Bodies are tiny**: 75 %+ of dragons are length ≤ 2 at r100 (36 of 48 in game 510684); only 0–5 dragons reach
  length 8+ before r100. Total body cells peak at ~4.5 % of the map (109 of 2,400).
- **Spacing is one head per bed cluster**: nearest allied head at median 2 cells, but each head's patrol area is
  its own; nobody roams.
- Deaths concentrate in the dense phase (r60–90, 2–7 per decade), causes mixed body/self/h2h — 18–48 deaths per
  game by r100 against 79–103 splits. Churn is accepted: 3–28 newborns die within 10 rounds of birth per 100
  births; replacement outruns death. Invalid-action deaths are survivable too (16 in rank-2 team 70's 64-unit win).

## The spec for C1-B (what to implement, in order)

1. Turn 0: split every length-4 starter, 4→2+2. (Three commands, no scouting needed.)
2. Route the six workers to bed clusters (the reconstructed bed map, `game_stats/live_beds.json`, keyed by
   `map_hash`); spread so each claims a distinct cluster — target: first pearl by r22, six claimed clusters by r40.
3. Patrol locally (~5×5 around the cluster; move every turn; eat on spawn). No roaming, no long sprints.
4. Split at length 4, always 2+2; child stays within ~5 cells of birth and claims the nearest unclaimed bed
   (≥ 3 cells from allied heads). Route through a portal only when it shortens the claim distance; never double-transit.
5. Accept newborn deaths; do not slow production to prevent them. Expected curve: 8 units r50, 20 r60, 31 r70,
   48 r80, 64 by r90–110; 200–300 pearls in rounds 50–100; ~50 % of beds covered at r100.
6. Do not build a crown before r100 (the winners' crowns are post-r100 feeding).

## Caveats

n=5 swarm wins (three teams: 70, 306, 91 — two play-styles converge on the same loop); no submission ids, so
team 70's swarm/non-swarm games may be different versions; both layouts share the same 444-bed set; team 7's own
ranked Schooltime sample is n=2 (units r100 median 8) — we currently do not play this game at all. The units
curve is the median of five games; individual games vary ±10 units at r80.
