# Gavroche v18: fused room flood

Parent: Gavroche v17. The native policy and parameters are unchanged. When the
early saturated density push is active, one flood-fill now runs to
`max(trap_need, info_room_cap)` and supplies both the trap score and room
factor. This removes the second per-candidate flood that was active through
round 199 on crowded teams.

The M274421/M274432 submission replays show why this matters: both Big Empty
games hit the 100M CPU cap, and their 8 and 15 timeout flags exactly match the
missing actions. Other maps had no timeouts; their recorded maxima ranged from
59M to 92M. The fused flood preserves trap scoring because the larger search
still returns exact room size whenever it is below `trap_need`; it preserves
the gradient room factor because both prior and combined searches saturate at
12 cells.

The full endgame length-race issue is a separate follow-up so the CPU change
can be measured on its own.
