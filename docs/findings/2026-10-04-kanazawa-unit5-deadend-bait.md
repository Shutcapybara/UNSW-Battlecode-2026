# Kanazawa unit 5: our queens die in static dead ends, usually after eating their way in

4 October 2026, 05:11–05:35 UTC. Branch r/kanazawa. Map set: post-m2 (started ≥ 2 Oct 03:49Z), team-7 games, LIVE_MAPS_M2 era; parent in those games: carthage-05 and the submissions Himeji lists (14585/14265). Corpus reads only; no bot run.

## 1. Correction (Himeji H23-01 accepted)

Himeji is right. `q_seal_who.py` removed the queen's "own" body as `b[1:]` retained, which is the same as not removing it, and no call removed all bodies together. My unit-4 line "terrain-only 10/17, stays sealed with all bodies removed" is wrong as worded. With no bodies at all, the 17 heads reach 239–4,095 cells.

`tools/kanazawa/q_seal_entry.py` (output `build/kanazawa/trap/seal_entry.csv`) narrows what the body does. On the same 17 seal states, blocking **only the neck cell b[1]** gives exactly the same flood as blocking the whole own body in all 10 own-sealed cases (0–4 cells). The queen's body seals these pockets only through the cell it entered from. So the feature is static after all, but per **directed edge**, not per cell:

> E(u→v) = size of the component of v in the terrain graph minus u (wrap and portals included).

E is precomputable per map_hash for every edge and observable online, since the live maps are fixed (maps/live). This reconciles Himeji's "body-conditioned" (correct in general) with a static table (enough for these 10 of 17).

## 2. Exposure and outcome (H-KZ12 corrected, H-KZ13 partial)

`tools/kanazawa/q_deadend.py --n 96`: 96 post-m2 team-7 games (of 286), every single-step queen move u→v, both sides. Queen = lowest id per side at round 0. Label: queen wall death ≤ 6 rounds after the move (diagnostic only, per H23-05; not an input).

| side | queens | wall deaths | after an E ≤ 4 move | grew inside the dead end |
|---|---:|---:|---:|---:|
| us | 96 | 30 | **21** | **17** |
| opponents | 96 | 15 | 9 | 6 |

| E bucket | our moves | wall ≤ 6 r | opp moves | wall ≤ 6 r |
|---|---:|---:|---:|---:|
| 0–4 | 73 | 60 (82 %) | 3,045 | 26 (0.9 %) |
| 5–8 | 27 | 4 | 5 | 0 |
| 17+ | 8,629 | 108 (1.3 %) | 13,998 | 62 (0.4 %) |

- **70 % of our queen wall deaths (21/30) follow a move into a static dead end of ≤ 4 cells, and in 17 of those 21 the queen ate on the way in** (length rises step by step down the corridor, e.g. Autarky 3→6, Maze 8→10). Pearls in dead ends bait the queen. This is H-KZ13's second clause, supported.
- We almost never use E ≤ 4 edges safely (73 moves in 96 games, 82 % fatal). A hard guard therefore costs us almost no current safe moves; the cost is the pearls it forgoes.
- Opponents make 3,045 such moves and survive 99 %. Most (≈ 1,500 per 48 games) are Schooltime, where the queen circles a tiny pocket at length 3. Non-Schooltime opponent entries (Trauma, PD) are at length 2–4 and mostly survive. Those pockets presumably contain a cycle the queen can turn in; ours are corridors (trees). Not yet measured.

## 3. Hypotheses

- **H-KZ12 (restated, 0.65):** the queen rejects u→v when E(u→v) + 1 < L + 2 and the dead end has no cycle of length ≥ L+1. Dial k: reject when E < k, doses k ∈ {0, 4, 8, 16} with the cycle exemption; 0 = carthage-05. The table is static per map_hash (precompute from maps/live, about 4k cells × 4 edges, flood capped at 17). Pearl valuation is where the bait enters, so a softer variant discounts pearls behind such edges. Frozen primary: queen wall deaths per game and queen alive@RL-end on LIVE_MAPS_M2, paired vs carthage-05, expected sign +. Side effects: food/turn, wins, deaths by cause. Upper bound on the size: 21/96 games lose the queen this way; h2h (Nara: 140/280) remains, so alive@490 moves by less. If every guard fires and the guarded moves lose under 2 % of food, the guard is a cheap fix. Falsifier: at k=4/8, queen wall deaths fall < 30 % or food/turn −10 %. Suits Rome/Seoul (one switch). RL translation: E(u→v) per candidate action plus a cycle bit as action features; label: queen wall death ≤ 6 r after the move (censored as Himeji specifies).
- **H-KZ14 (blue-sky, 0.25): orbit parking.** Opponent queens at length 3 circle cyclic micro-pockets (Schooltime, ≈ 1,500 moves per 48 games, no deaths). A pocket with one entrance exposes the head to h2h only at that entrance. Using it on keeper maps could cut the h2h half of our queen hazard, at the cost of the length race. Falsifier: queens observed orbiting ≥ 20 consecutive E ≤ 4 moves die at ≥ the field's per-round hazard. Cost: corpus pass. Suits Kanazawa → tester.

## 4. Caveats

- E is the terrain component behind u only. It ignores bodies, which can only make it smaller, so this undercounts traps and does not overstate them.
- Sprints and teleports (head moves that are not adjacent) are skipped. The opponent column mixes all opponents, not top ten; the H-KZ13 top-ten contrast is still open.
- Move-level rates count several moves per fatal entry; the queen-level table is the unit to cite.
