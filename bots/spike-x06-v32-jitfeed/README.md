# spike-x06-v32-jitfeed — Gavroche v32 with just-in-time feeding

- **Lineage:** Spike. Parent: `gavroche-v32-supported-divecap` (exact frozen snapshot, `override.py` unchanged).
- **Change (roles.py):** the team-wide feeding clock (`500 - feed_base - 0.6(W+H)`, recruits within 16 steps) is
  replaced by a per-dragon rule: a dragon becomes a feeder when `500 - round <= 1.3 x torus distance to the crown + 12`,
  the crown is fresh, at least `feed_min_crown` long and longer than it, and it is within 60 steps. Crown election,
  suicide distance, crown-food zones and everything else are v32's.
- **Why (SPIKE-22 audit):** feeding returns at most ceil(L/2) pearls per dragon and it removes the hunters that keep
  enemy crowns short (x04's new losses: opponent longest 39 vs 25; our total 65 vs 171; 59% reach <=2 units).
  Wider/earlier feeding (x04) fixed conversion but paid those costs. Just-in-time recruitment keeps every dragon
  hunting/farming until its own travel time forces it to leave, while still letting far dragons reach the crown.
