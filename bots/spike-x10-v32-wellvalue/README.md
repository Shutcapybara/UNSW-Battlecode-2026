# spike-x10-v32-wellvalue — Gavroche v32 + period-aware bed value

- **Lineage:** Spike. Parent: `gavroche-v32-supported-divecap`. Component from Newton/Witten (`bed_per_k`, off in those hosts' defaults).
- **Change:** world tracks each bed's largest observed countdown (`bper`). A predicted-bed target is worth
  `v_bed x min(4, 1 + (30/bper - 1))`, so an every-round well is worth 4x a slow bed and beds with period >= 30 are unchanged.
- **Why (SPIKE-25/26 probe):** on spring wells (4 every-round wells + slow farms) v32 collects 3-9 pearls by r50 vs
  9-26 for the opponents that beat it. A single-fixture probe raising v_bed 8 -> 14 flipped v32 vs serre (pearls@50 7 -> 27,
  splits 7 -> 37). x10 targets fast beds specifically; `spike-x09-v32-bedvalue` is the blunt global dose.
