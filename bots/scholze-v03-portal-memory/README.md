# Scholze v03: Portal-Exit Risk Memory

**Line:** Scholze. **Parent:** `scholze-v01-control`.
Effective source SHA-256: verified via benchmark tools.

### Mechanism
Addresses **Leak 2 (Portal Paralysis & Flat Unseen Risk)**:
- Monte Christo and baseline Fafnir/Serre charge every unseen portal exit a flat full-dragon penalty (`p_blind = 1.0 * dragon_value`). This causes dragons to hesitate or freeze in portal boxes, failing to exploit portal corridors on portal-rich maps (`dilemma`, `autarky`, `Colosseum`, `queen_of_spades`, `schooltime`).
- `scholze-v03` activates `blind_mem = 1`:
  Estimates unseen-exit risk from recent dragon sightings near the exit within 12 rounds:
  - Surveyed and quiet exit: $0.15 \times V(\text{dragon})$.
  - Unknown exit: $0.50 \times V(\text{dragon})$.
  - Recent body seen near exit: $1.00 \times V(\text{dragon})$.
- When `blind_mem = 0`, feature-off parity is byte-identical to control.
