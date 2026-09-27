# Scholze v05: Composite Stepping Stone

**Line:** Scholze. **Parent:** `scholze-v01-control`.
Effective source SHA-256: verified via benchmark tools.

### Architecture & Mechanisms
`scholze-v05-composite` combines the three leak-free stepping stones into a coherent, balanced candidate:
1. **Opening Rescue (`opening_rescue = 1`)**:
   - Rescues initial long dragons ($L \ge 8$) on constrained maps (`autarky`, `dilemma`) during rounds 0..2 by detaching the rear $L - 2$ segments to face outward, and enables early production splits ($L \ge 4$) up to 8 units during rounds 0..20.
2. **Portal-Exit Risk Memory (`blind_mem = 1`)**:
   - Replaces flat full-dragon unseen-exit risk with recent body-sighting memory (surveyed: 0.15, unknown: 0.5, body near: 1.0), unblocking navigation through portal networks on portal maps (`autarky`, `dilemma`, `Colosseum`, `queen_of_spades`, `schooltime`).
3. **Exit Trapguard (`exit_guard = 1`)**:
   - Directly checks `tx.exits(nb)` on simulated candidate landings. Penalizes moves leaving 0 legal exits next turn with `w_exit_zero = 300.0`, eliminating suicide steps into cul-de-sacs, and penalizes entering 1-exit corridors with `w_exit_one = 2.0`.
4. **Feature-Off Parity**:
   - When all three switches are disabled, the bot matches `scholze-v01-control` action-for-action (21,113 / 21,113 actions identical on 500-round Devil fixture).
