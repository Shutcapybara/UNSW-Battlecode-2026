# Monoco ra-06 — stronger target hysteresis

Based on Ares V06 with atlas use off. The single switch `Params::monoco_target_hysteresis` raises the existing target hysteresis from 1.25 to 1.75; switching it off restores V06.

The switch-off copy replayed all four V06 golden transcripts with zero divergent decisions (52,728 turns, 1,842 dragons). The z1 seed-1 pool result and CPU probe are recorded in `claude/ra-status.md`.
