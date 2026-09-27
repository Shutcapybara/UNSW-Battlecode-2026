# Scholze v02: Opening Rescue

**Line:** Scholze. **Parent:** `scholze-v01-control`.
Effective source SHA-256: verified via benchmark tools.

### Mechanism
Addresses **Leak 1 (Opening Corridor Paralysis & Production Delay)**:
- On maps where starting dragons are long (`autarky` len 14, `dilemma` len 11), the dragon's body extends beyond the 7x7 vision window. Fafnir's `len(body) < L` blocks splitting for 11–14 turns, paralyzing reproduction in narrow corridors.
- `scholze-v02` implements `opening_rescue`:
  During rounds 0..2, if starting length $L \ge 8$, splits off the rear $n = L - 2$ segments into a new dragon facing outward.
  During rounds 0..20, if length $L \ge 4$ and units $< 8$, permits early production splits even if the body trail is still expanding.
- When `opening_rescue = 0` and `opening_prod = 0`, feature-off parity is byte-identical (21,113/21,113 actions identical to control).

### Measured Impact
- On Autarky vs Ouroboros v13:
  - Round 1 splits: 0 in control vs 4 in v02.
  - Round 1 units: 6 in control vs 10 in v02.
  - Conversion: Control eliminated Ouroboros at round 372 (15.9s); Scholze v02 eliminated Ouroboros at round 176 (7.3s), over 2× faster!
