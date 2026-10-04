# Kanazawa unit 16: the queen-strike gap replicates out of sample (5.7x); the dodge reading weakens; pincers convert; tier gradient is inverted

**Date:** 2026-10-04 10:47–10:55Z. **Tool:** `tools/kanazawa/q_tier.py` (frozen 10:47Z; opportunity definition identical to q_suff, unit 15; flee/chase denominators are Himeji H34-03's joint survivors). **Corpus:** in-sample stride set (96 games, consumed, descriptive) and out-of-sample `--new --stride 2` (201 of the 399 eligible team-7 games after the first 286).

## Results

| set | queen side | opps | hit | rate | joint-surv non-hit | flee | chase | 1-striker | 2+-striker | ratio |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| in-sample | ours | 264 | 25 | 0.095 | 224 | 0.737 | 0.335 | 20/214 = 0.093 | 5/24 = 0.208 | 2.2 |
| in-sample | opp top ten (44 g) | 249 | 10 | 0.040 | 228 | 0.776 | 0.390 | 8/227 = 0.035 | 2/10 = 0.200 | 5.7 |
| in-sample | opp rest (52 g) | 337 | 8 | 0.024 | 320 | 0.834 | 0.353 | 6/301 = 0.020 | 2/16 = 0.125 | 6.3 |
| **OOS** | **ours** | 635 | 64 | **0.101** | 546 | 0.766 | 0.403 | 54/571 = 0.095 | 10/31 = 0.323 | 3.4 |
| OOS | opp top ten (3 g) | 14 | 1 | 0.071 | 13 | 0.846 | 0.538 | — | — | — |
| **OOS** | **opp rest (198 g)** | 2,754 | 48 | **0.017** | 2,628 | 0.809 | 0.447 | 30/2,139 = 0.014 | 18/292 = 0.062 | 4.4 |

In-sample numbers reproduce Himeji H34-03 exactly (25/264, 224 joint survivors, flee 73.7 %, chase 33.5 %).

## Readings against frozen predictions

1. **H-KZ33 (tiered dodge): prediction failed, gradient inverted.** Top-ten queens flee 77.6 % (not ≥ 85 %; falsifier ≤ 72 % not reached) and are struck *more* (4.0 %) than the rest (2.4 %, flee 83.4 %). The gap is against everyone, not the best queens. Weight 0.4 → 0.15. (OOS has only 3 top-ten games.)
2. **H-KZ35 (pincer): holds in and out of sample.** Opponent queens with ≥ 2 of our heads in reach are struck 4.4–6.3× as often as with one (OOS 18/292 vs 30/2,139). Our queen shows the same shape (3.4× OOS). Weight 0.3 → 0.6. Note: 38 % (18/48) of our OOS queen kills come from the 11 % of events with ≥ 2 strikers.
3. **H-KZ26 premise replicates out of sample, stronger:** our queen 10.1 % vs field 1.7 % per opportunity (5.7×; in-sample 2.4–4×).
4. **But the dodge mechanism weakens.** OOS flee differs by only 4.3 pp (76.6 vs 80.9 %), and per-opportunity conversion on one-striker events differs ~7× (9.5 % vs 1.4 %). Himeji's caveat stands: flee over survivors cannot separate cause. A flee gap of this size cannot carry a 5–7× conversion gap by itself. Either our queen's options at the opportunity are fewer (geometry, pockets, body), or the field's strikers convert better than ours (the two sides use different strikers). H-KZ26 weight stays 0.65 on the premise; the *mechanism* of the gain is now open (new H-KZ36).

## Implication for testers

Shenzhen probe N (H-SZ34 yield, all dragons, ~100 fires/game) cost −18 % total and −55 % on Islands. H-KZ26 is queen-only and fires ~25/1k queen-rounds, so it is a much smaller intervention, but it must be priced the H-SZ37 way: pool total per map with Islands as the canary. Seoul closed without running H-KZ26; it has no tester.

## New hypotheses

- **H-KZ36 (0.45):** our queen has fewer safe escape moves at an opportunity than field queens. Falsifier: median count of legal non-pocket (Cb ≥ 4) moves at the opportunity state for our queen ≥ field's. Cost: one corpus pass. Suits Kanazawa.
- **H-KZ37 (blue-sky, 0.15):** the out-of-vision strikes (unit 14: 4/20) are sonar- or broadcast-informed. Signature: striker on our queen's row or column with a clear line at R[dr−2], or a teammate of the striker with the queen in vision. Falsifier: neither signature beats a geometric baseline over the out-of-vision strikes. Cost: corpus geometry. Suits Kanazawa.
