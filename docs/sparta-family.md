# Sparta family

Sparta is an experimental C++ line built from the measured Carthage 05
snapshot. The first version tests a symmetric queen priority: our original
queen avoids immediate lethal head contact, while the rest of the team hunts
the enemy's original queen and accepts a non-queen trade to kill it.

## Sparta 01 — queen priority

Parent: `carthage-05-free-sprint`. Carthage 05 contains corrected 1.2.3 sprint
pricing and useful on-route free sprints. It also carries Bifröst/Skadi's
higher bounded target search, Fafnir's size-matched counter-threat support,
and HB-1's direction prior. Its full sprint bundle improved paired win share
against Carthage 00 on the pool and generated panels, while the free-sprint
increment over Carthage 04 alone remained inconclusive. See the
[Carthage sprint finding](findings/2026-10-02-carthage-sprint-rules.md).

Sparta 01 adds three rules:

1. The original queen for our team rejects a simulated death, a destination in
   the enemy head danger map, and a head-on trade. Other Carthage movement,
   production splits, and portal choices remain active.
2. A visible enemy queen becomes the team's prey target, regardless of its
   length. The existing type-4 prey sonar carries the sighting; the queen
   report stays active for 60 rounds and cannot be displaced by a generic
   prey report while fresh.
3. Every non-queen dragon follows the last reported enemy queen cell ahead of
   forage and crown roles. A simulated head-on with that queen receives a
   dominant score regardless of relative length or unit count. A large route
   bonus pushes movement toward the queen ahead of ordinary goals. The
   existing constrained-newborn escape may temporarily override that hunt.

The guard rejects moves the simulator marks as dead, head-on trades, and cells
marked reachable by visible enemy heads. It does not forecast multi-turn
entrapment or threats outside the visible danger map, or find enemy queens
that have never been seen. Stale reports can send the team to an empty cell.
The offensive rule can trade away a valuable hunter without ending the game,
so its score is an explicit, aggressive hypothesis rather than a proven
value.

Sparta 01 is not admitted to the all-map frontier. Its first focused serial
screen scored 17–23 in 40 games and found 16 wall-caused queen deaths; see the
[Sparta 01 screen finding](findings/2026-10-02-sparta01-focused-screen.md).
The original design hypothesis is in the
[queen-priority finding](findings/2026-10-02-sparta-queen-priority.md).

## Sparta 02 — known-edge queen guard

Sparta 02 adds a queen-only veto when a simulated route crosses an unknown
edge. Its fixed-seed paired screen tied 01 (12–12), lost to Carthage 05
(9–15), and kept the queen alive in 0/20 games reaching round 490. The veto
did not improve this screen; keep 02 as a diagnostic control. See the
[known-edge finding](findings/2026-10-02-sparta02-known-edge-guard.md).

## Sparta 03 — local queen intercept

Sparta 03 starts from Sparta 01 rather than stacking Sparta 02's inconclusive
edge veto. When a visible enemy head is within three cells of our visible
queen, the two nearest visible non-queen allies target that head and accept a
trade to remove it. Other non-queen dragons keep hunting the enemy queen. Its
fixed-seed screen tied Sparta 01 (12–12), lost to Carthage 05 (9–15), and the
queen died in all 48 games; keep it as a diagnostic variant. See the
[intercept finding](findings/2026-10-02-sparta03-queen-intercept.md).

## Sparta 04 — queen reserve

Sparta 04 forks Sparta 01 and disables ordinary/opening queen splits while
leaving emergency escape splits available. It scored 13–11 against Sparta 01
and 7–17 against Carthage 05. The queen was alive at round 490 in 3/32 reached
games (Sparta 03: 0/22) and made 15 emergency split actions (Sparta 03: 156
split actions), but the candidate killed the enemy queen in 13 games (Sparta
03: 28). This suggests a modest survival gain with a substantial production
cost. See the [queen-reserve finding](findings/2026-10-02-sparta04-queen-reserve.md).

## Sparta 05 — thresholded queen reserve

Sparta 05 uses the Sparta 04 length retention only until a normal split can
leave the queen at length seven. It matched Sparta 04 at 13–11 against Sparta
01 and 7–17 against Carthage 05. It recorded 27 queen splits and 14 enemy
queen kills, compared with 15 and 13 in Sparta 04; queen survival stayed at
3/32 reached games. The change did not alter wins or survival. See the
[length-reserve finding](findings/2026-10-02-sparta05-queen-length-reserve.md).

## Sparta 06 — shorter queen reserve

Sparta 06 lowers the parent length reserve to five. It scored 13–11 against
Sparta 01 and 6–18 against Carthage 05, with 31 queen splits and 15 enemy
queen kills, but only 2/32 queens alive@490. That is four more splits and one
more enemy queen kill than Sparta 05, but one fewer queen survivor and one
additional loss to Carthage 05. See the
[five-segment reserve finding](findings/2026-10-02-sparta06-queen-reserve-five.md).

## Sparta 07 — queen threat flee

Sparta 07 used Sparta 05's seven-segment reserve and added a queen-only
movement score that rewarded increasing distance from visible enemy heads
within eight cells. It tested an active retreat response after local
interceptors failed to improve queen survival. It scored 9–15 against Sparta
01 and 8–16 against Carthage 05; head-on deaths fell to 16, but wall deaths
rose to 29, queen alive@490 fell to 0/27 reached games, and enemy-queen kills
fell to 10. See the
[queen-threat finding](findings/2026-10-02-sparta07-queen-threat-flee.md).

## Sparta 08 — edge-safe queen flee

Sparta 08 added Sparta 02's queen-only unknown-edge veto to Sparta 07's retreat
bonus to test whether unknown terrain caused the wall deaths while preserving
the head-on survival gain. It matched Sparta 07's result (9–15 vs
Sparta 01, 8–16 vs Carthage 05), death causes, and queen survival: 0/27 reached
games alive@490. The veto did not improve the retreat branch; see the
[edge-safe retreat finding](findings/2026-10-02-sparta08-edge-safe-queen-flee.md).

## Family result

The eight fixed-seed variants produced no candidate that both improved the
all-around score and materially protected the queen. Sparta 04/05 gave the
best measured queen survival in this panel (3/32 queens alive at round 490)
but lost 7–17 to Carthage 05. Keep Sparta 01 as the family control; keep
Sparta 04/05 for further safety work. Do not promote any Sparta snapshot from
these four maps and three seeds alone.
