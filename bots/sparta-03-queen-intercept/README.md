# Sparta 03 — queen intercept

Sparta 03 starts from Sparta 01 and preserves its queen hunt. When a dragon
can see both our queen and an enemy head within three cells of her, the two
nearest visible non-queen allies become local defenders. They target that
enemy head; if they can trade heads with it, they accept the trade to remove
the immediate threat. Other non-queen dragons continue their queen hunt.

This response is local and short-lived. It needs no new sonar message and
does not pull the whole team back to the queen. The fixed-seed screen scored
12–12 against Sparta 01 and 9–15 against Carthage 05; the queen died in all 48
games (19 head-on, 25 wall, 4 body), with none surviving to round 490. The
interceptor did not improve the screen. See the
[intercept finding](../../docs/findings/2026-10-02-sparta03-queen-intercept.md).
