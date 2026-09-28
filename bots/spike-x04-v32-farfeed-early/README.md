# spike-x04-v32-farfeed-early — x03 plus earlier feeding

- **Lineage:** Spike. Parent: `gavroche-v32-supported-divecap` (exact frozen snapshot); only `override.py` changes.
- **Change:** `feed_range` 16 -> 40 and `feed_base` 40 -> 70 (feeding starts 30 rounds earlier on every map; big_empty 384 -> 354).
- **Evidence (SPIKE-17):** of v32's 67 round-limit length losses on panel A, 21 were *conversion losses* — v32 finished
  with more total length (mean 153.5 vs 116) but a shorter longest dragon (32.3 vs 41.9), holding 10.1 units vs 5.5.
  Length-efficiency (longest/total) 21% vs the opponent's 36%. Concentrated on large maps (big_empty 5,
  commons_spread 4, default/stronghold 2 each) where most small dragons sit beyond 16 steps of the crown and never feed.
  Also matches the user-reported observation that a leading team wins by aggressively sacrificing small dragons late.
- **Question:** is recruitment distance the binding constraint on late conversion? Risk: feeders travelling far stop
  foraging/defending earlier and may cost elimination wins.
