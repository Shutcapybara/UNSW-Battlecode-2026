# Sparta 02 — known-edge queen guard

Sparta 02 forks Sparta 01 and keeps its team-wide queen hunt and all Carthage
05 parent behavior. It adds a queen-only veto for routes whose simulator
crosses an unobserved edge. The parent search treats such an edge as open, but
the queen waits for direct map knowledge before taking that step. Known safe
routes, head-on protection, and queen-hunt behavior are otherwise unchanged.

This targets Sparta 01's main measured queen-death cause: wall contact. The
first serial screen had 16 wall deaths among 40 own-queen games, and our queen
survived round 490 in 2 of 20 games that reached it. The change can strand the
queen if all routes require revealing an edge; it does not address head-on
ambushes or multi-turn traps.

In the fixed-seed paired screen, Sparta 02 went 12–12 against Sparta 01 and
9–15 against Carthage 05. Its queen survived round 490 in 0 of 20 games that
reached it; wall deaths remained common. The unknown-edge veto is retained as
a diagnostic control, not as an improvement. See the
[known-edge finding](../../docs/findings/2026-10-02-sparta02-known-edge-guard.md).
