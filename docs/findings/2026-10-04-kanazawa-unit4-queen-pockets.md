# Kanazawa unit 4: what sealed our queens? Terrain pockets 10/17, ally bodies 6/17, enemy 1/17

Date 4 Oct 2026, 04:40–05:05Z. Map set: post-m2 (started ≥ 2 Oct 03:49Z), LIVE_MAPS_M2 era, parent context carthage-05 era ladder. Team 7, 60 games sampled evenly from 286 eligible.
Tools: `tools/kanazawa/q_seal.py` (output `build/kanazawa/trap/seal.csv`), `tools/kanazawa/q_seal_who.py`.

## Question (frozen before the run)
Himeji H22-01 says 4 weakhold queens were sealed before their final split, which contradicts my H-KZ6 reading (unit 2: the queen split seals the queen).
Estimand: among queen wall deaths, the share sealed (a) before the last split, (b) by the last split, (c) otherwise; and, at the moment the head's flood region first falls below length+2 for good ("seal_start"), which bodies close it.
Flood = cells reachable from the head through non-kelp cells not occupied by any body at round start (wrap and portals via `nbr`), capped at 60. It is static, so moving tails are ignored.

## Result (17 queen wall deaths in 60 games)
| class | n | reading |
|---|---|---|
| sealed before the last split | 9 | the last split comes 1 round before death, inside a pocket of 0–4 cells: a symptom, not the cause |
| sealed by the last split (flood 60 → 0–3) | 5 | H-KZ6 mechanism |
| last split long before, sealed later | 3 | — |

Who closed the pocket at seal_start (flood with one body class removed):
| sealer | n | reading |
|---|---|---|
| **terrain only**: the flood stays at 0–4 with every body removed, and the queen had just moved in | **10** | queen walks into a kelp cul-de-sac (H-H6) |
| ally bodies (incl. split children): removing allies opens to 60 | 6 | H-KZ6 + ally crowding |
| enemy bodies | 1 | — |

The 10 terrain cases span Autarky, Trauma ×3, weakhold ×2, Around UNSW, Tower Defense, Portals ×2. The queen is length 2–3 and dies 1–6 rounds after entering.

## Reading
- The contradiction with Himeji resolves mostly in Himeji's favour. Split-sealing (H-KZ6) explains at most 5–6 of 17 queen wall deaths, and terrain cul-de-sac entry explains 10/17. H-KZ6 weight goes from 0.65 to 0.35. Its upper bound on the effect is about one third of queen wall deaths.
- Proposed H-KZ12 (0.6): a static terrain-pocket guard. The queen never moves into a cell whose kelp-only flood region (bodies ignored, own body excluded) is under k cells. The quantity is precomputable per map, so it costs nothing per turn. As a D-044 dial, use doses k ∈ {0, 4, 8, 16}. Primary metric: queen alive@RL-end on LIVE_MAPS_M2. Side effects: food/turn, wins.
- **RL translation (D-044):** feature = per-cell terrain pocket size (kelp-only flood, capped at 16), plus the queen's current pocket size and a binary "move enters a pocket < L+2". Label = queen wall death within 6 rounds. Value term = −(queen loss) propagated through pocket entry. To check: whether top-ten queens ever enter pockets (H-KZ13).
- Caveats: kelp is treated as static (the `nbr` map). A static flood can call a pocket sealed that a retracting tail would open, but every case here ended in death. n = 17 is small, so the class shares have wide CIs (10/17 → 59 % [36, 79] Wilson).
