# avery-v09-frontier-bfs

**Lineage:** Avery · **Parent:** `bots/avery-v08-crown-race` ·
**Status:** measured, **rejected** (net-negative; superseded by the v10/v11
exploration-gating experiments).

## Hypothesis

trauma is v08's worst map (5–7) and the failure is exploration, not combat:
in a traced 500-round game all 13 avery dragons stayed inside an ~11×11
corner (350 of 1152 cells) and the team ate 37 pearls while ouroboros-v10
ate 426 (≈ every spawn of every bed — trauma has 12 period-1 and 130
period-200 beds). Root cause: loot targeting pays `w_dist=1.0` per BFS step
so the tiny frontier bonus never carries beyond ~2 steps, and the idle
fallback follows a manhattan gradient to a zone centre, which dithers
against maze walls.

## Changes vs v08

- `choose_target` scores every BFS-reached cell for exploration (staleness
  via `seen[]` age + full `w_frontier` per unknown side + mild
  `expl_w_dist=0.3` distance + per-dragon jitter 0.6); when nothing
  productive scores (`best_s < 1.0`), the best exploration cell **replaces**
  the zone waypoint as target.

## Measured results

Native gauntlet (132 games; run interrupted at 119 by a missing
`game_stats/runs/` directory — another agent's git op — and resumed to
completion): `experiment_data/avery-v09-frontier-bfs_20260925130508074100`.

**97–34–1** vs v08's 100–31–1 — **rejected**.

| Map | v09 | v08 |
|---|---|---|
| trauma | **8–4** | 5–7 (hypothesis confirmed) |
| default_small | 8–4 | 7–5 |
| trophy | 8–4 | 7–5 |
| queen_of_spades | 9–3 | 12–0 (regression) |
| default | 9–3 | 12–0 (regression) |
| devil | 9–3 | 11–1 (regression) |

tew-v12 matchup 11–11 → 8–14.

## Why rejected (traced)

Ungated exploration marches lone dragons through contested space: on
queen_of_spades side A both starters walked in a straight line for 48 rounds
(never eating) into ouroboros territory and were struck dead by r49; v08
wins that fixture 12–0 across opponents. The zone waypoint's cohesion
(crowd balancing + heat avoidance) is load-bearing on open maps. Follow-ups:
v10 (safety gates — still loses qos) and v11 (exploration only when the
waypoint is BFS-unreachable).
