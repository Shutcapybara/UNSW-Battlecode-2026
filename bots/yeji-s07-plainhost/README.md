# yeji-s07-plainhost

**Lineage:** Yeji. **Parent:** `yuna-v03-core` (gavroche/yuna host; copied, not edited). **Status:** frozen candidate, **undecided**.

One change, written as the last line of `override.py`: `portal_mode 0, nb_mode 0, mom_w 0.0`. This switches off yuna's portal phase policy, newborn exit and direction momentum. All three were accepted on the live maps. The question was whether they hold on unseen maps.

Held-out panel: 10 synthetic maps from `maps/new/` (`tools/yeji/HOLDOUT_MAPS`) × both sides × 5 references (yuna-v02, gavroche-v32, sinbad-v07, witten-x03, vibing-mimic), unswbc 1.2.2. Each line pairs the variant with `yuna-v03-core` on the same fixtures:

| Seed | Variant | yuna-v03-core | Δ | better / worse | sign p |
|---|---|---|---|---|---|
| 1 | 0.560 | 0.420 | +0.140 | 23 / 9 | 0.02 |
| 2 | 0.490 | 0.586 | −0.091 | 12 / 21 | 0.16 |
| Both (199 pairs) | 0.528 | 0.503 | +0.025 | 35 / 30 | 0.62 |

**Not an improvement that can be shown.** The base itself moved 0.42 → 0.59 between the two seeds. One seed of 100 games can swing by ±0.1, so held-out selection needs at least 3 seeds (300 games per bot).

No CPU probe was run. The change only removes code paths from a host that passed the gate.
