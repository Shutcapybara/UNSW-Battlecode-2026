# Skadi v01: bounded routes and productive pockets

**Skadi** is a Norse-origin family name (Old Norse **Skaði**). This first
candidate starts from `bots/gavroche-v54-sparse-room` and combines its bounded route
search with two measured ideas from the other lines:

- Fafnir's **size-matched counter-threat support** discounts an enemy threat
  only when a visible ally at least as long as that attacker is close enough
  to answer it.
- Scholze's **exit guard** penalizes moves that leave no onward step. The
  zero-exit exception requires enough reachable pearls to reach split length
  and recover the two segments left behind as a trapped parent, an open
  production window, and a small bounded check that the escape child has room
  to move.

The opening rescue, crown, feeding, arrival-aware target values, density
guidance, and search budgets come from the Gavroche V54 source. Target search
is capped at 48 nodes from round 40, with the measured late sparse allowance
of 64; long-body flood checks are capped at 24 in the late phase. These limits
keep the expensive route and room work bounded.

## Evidence and status

This is a new, **unbenchmarked candidate**. Its parent, Gavroche V54, completed
its 108-game panel at 69–39 and 32–16 against Sinbad, tf05, grad1, and x04. Its
four judge-sandbox samples had 43.0–44.1M p99 and 52.8–63.7M maximum CPU, with
no timeouts. Those measurements apply to V54, not to Skadi after its new
support and exit checks.

Newton's compact fast-bed contest and round-200 conversion helped selected
compact fixtures but failed the frozen overall screen gate. Witten's reset-
qualified contest also failed its matched competitive panel; neither is
enabled here. Skadi keeps their map- and evidence-aware lesson, not their
unpromoted rules.

The family review and implementation rationale are in [`docs/skadi.md`](../../docs/skadi.md).
