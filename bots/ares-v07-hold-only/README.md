# Ares V07 HOLD-only

This V06 child ports Chaewon Y05’s HOLD report without activating the map atlas or adding a probe-result cache. If a non-crown move leaves the head beside a known paired portal whose landing is outside vision, Ares replaces its outgoing sonar with one ray carrying the post-move head cell and round. An ally that receives the packet treats that blind landing as occupied for two rounds.

Ares type 7 already carries split handoff packets, so HOLD uses new packet type 8. The sender skips HOLD while a handoff packet is pending. The marker `ACT:hold` records sends.

The 160-game seed-1 panel scored 114–46–0. Ally head-on deaths fell 13.2% with no tier-2 increase above 10%, but the normalized pearl mean rose only +0.005, normalized r100 units fell, and expected score fell 5 percentage points. It fails the documented acceptance gate. See [the V07 finding](../../docs/findings/2026-09-30-ares-v07-chae-won-components.md).
