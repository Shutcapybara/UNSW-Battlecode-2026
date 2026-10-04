# Kanazawa unit 7: fatal tree-pocket entries are avoidable and pearl-baited (H-KZ11, H-KZ17)

4 Oct 2026, 06:10–06:30Z. Tool: `tools/kanazawa/q_forced.py` (repo root; about 30 s per 96 games on 4 jobs).

## Frozen before running
- Data: post-m2 team-7 index (286 eligible). Primary set: in-sample stride 96. The 94-game holdout was consumed in unit 6 (Himeji H25-04), so its numbers below are descriptive replication, not confirmation. No new team-7 games since 03:25Z.
- Pocket: as q_cycle. C(u→v) = cells reachable from v in terrain minus u, inclusive of v, capped at 5. Tree = P+{u} has no cycle. Orbit_ok = a cycle ≥ L+1.
- Body occupancy at round t = all dragon cells at R[t] minus each dragon's tail. This ignores same-round head moves and growth.
- **H-KZ11.** A queen's first tree entry is *avoidable* if u had another terrain neighbour w (not v, not the neck, not occupied) whose pocket is open (C > 5) or orbit_ok. Forced share ≥ 0.5 supports H-KZ11. Avoidable share ≥ 0.7 falsifies it.
- **H-KZ17.** An exposure is a round in which the queen's head is adjacent to a free tree-pocket cell w, counted up to the queen's first tree entry. The lure is supported if P(enter | pearl in P) ≥ 2× P(enter | no pearl), per side. It is falsified if the ratio is ≤ 1.

## Results
| | in-sample (96) | holdout (94, consumed) |
|---|---|---|
| our first tree entries: avoidable / no free neighbour / other | **16** / 2 / 1 of 19 | 12 / 4 / 3 of 19 |
| opponent first tree entries: avoidable / no free / other | 11 / 3 / 0 of 14 | 8 / 3 / 1 of 12 |
| pearl inside P at our first entry | **17/19** | 18/19 |
| pearl inside P at opponent first entry | 12/14 | 10/12 |
| us: P(enter per exposure round), pearl vs none | **17/86 = 19.8 %** vs 2/91 = 2.2 % | 18/71 = 25 % vs 1/96 = 1.0 % |
| opponents: P(enter per exposure round), pearl vs none | 12/313 = 3.8 % vs 2/124 = 1.6 % | 10/72 = 14 % vs 2/72 = 2.8 % |
| us: pockets ever entered, pearl vs none | 17/45 = 38 % vs 2/81 = 2.5 % | 18/55 = 33 % vs 1/67 = 1.5 % |
| opponents: pockets ever entered, pearl vs none | 12/46 = 26 % vs 2/46 = 4.3 % | 10/42 = 24 % vs 2/51 = 3.9 % |

## Reading
1. **H-KZ11 is falsified on the primary set** (avoidable share 0.84 ≥ 0.7). Pooled, 28 of 38 are avoidable (0.74). The holdout is weaker at 0.63, and some entries were forced: 6 of 38 had no free neighbour. Weight drops to 0.2. The H-KZ12 veto can act on most of these deaths; in unit 6 they were about 20 % of our queens.
2. **H-KZ17 is supported for both sides.** A pearl makes an entry about 10× likelier for us and 2–5× likelier for opponents. Per pocket, we take the bait somewhat more often (35 % vs 25 % pooled). Per exposure round we take it much faster: opponents sit next to baited pockets for about 7 rounds each, which is the Schooltime orbiting, while we enter within about 2 rounds. Almost every fatal entry on both sides was baited.
3. Implication for the switch: the veto is the general rule. A narrower rule that blocks pearl-seeking into C ≤ 5 tree pockets would cover 35 of 38 entries.
4. Limits: the pocket is terrain only, so cycle existence ≠ a body-legal route (Himeji H25-04). The approximate occupancy can mislabel a neighbour as free. Exposures within a queen are correlated, and the pocket-level rows are the robust version.

## New hypothesis (blue-sky)
- **H-KZ18 (0.15).** Pearls dropped into a tree pocket next to the enemy queen are a kill mechanism: they can come from a commanded cull or a split corpse of one of our small dragons. Opponents enter baited pockets 24–26 % of the time, and nearly all such entries are fatal. Falsifier: in a sim, enemy queen deaths within 10 rounds of a planted bait ≤ the base rate. Cost: one tester probe on Schooltime or Slithery with a planted-pearl harness. Suits Rome or Seoul, or a Claude tester.
