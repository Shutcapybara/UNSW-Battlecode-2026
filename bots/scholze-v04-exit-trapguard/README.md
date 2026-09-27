# Scholze v04: Exit Trapguard

**Line:** Scholze. **Parent:** `scholze-v01-control`.
Effective source SHA-256: verified via benchmark tools.

### Mechanism
Addresses **Leak 3 (Congestion Trap Deaths & Dead-End Blindness)**:
- Replay autopsies revealed that over 50% of casualties (14 of 27 deaths before round 100 on Devil) were self, wall, or body collisions occurring when `free_exits = 0`.
- The baseline flood-fill (`tx.flood`) awards 8 frontier credits for any tile near the 7x7 vision edge (`n == -2`), tricking length-2 and length-3 dragons into believing a closed dead-end tile has ample room (`need = 5`).
- `scholze-v04` introduces `exit_guard = 1`:
  Directly evaluates `tx.exits(nb)` on simulated move candidates:
  - Landing with `exits == 0`: penalized with `w_exit_zero = 300.0` (eliminates suicide steps into cul-de-sacs).
  - Landing with `exits == 1`: penalized with `w_exit_one = 2.0` when not eating food.
- When `exit_guard = 0`, feature-off parity is byte-identical to control.

### Measured Impact
- On Devil vs Ouroboros v13:
  - Total casualties before round 100 reduced from 27 in control down to 21 in v04.
  - Head-to-head melee deaths reduced from 13 down to 7 (a ~46% reduction in combat losses).
