# Sparta 08 — edge-safe queen flee

Sparta 08 forks Sparta 07. It keeps the queen's seven-segment reserve and the
distance-based retreat score near visible enemy heads. It also rejects queen
routes that cross an unknown edge, which the movement simulator otherwise
assumes is open. Other dragons continue the team-wide enemy-queen hunt and
accept a trade to kill her.

Sparta 08 scored 9–15 against Sparta 01 and 8–16 against Carthage 05. The
queen died in all 48 games: 16 head-on, 29 wall, and 3 body deaths; none lived
to round 490 among 27 games reaching it. Enemy-queen kills stayed at 10. The
unknown-edge veto did not improve the retreat variant. See the
[edge-safe retreat finding](../../docs/findings/2026-10-02-sparta08-edge-safe-queen-flee.md).
