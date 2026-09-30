# Ares V42 — memory and teammate dispersion

V42 branches from V41. It removes V41's Devil lane movement bonus and changes
how dragons value exploration around portal exits and other crowded areas.

An unseen exploration cell loses value when its 8×8 sector has at least eight
remembered cells and no known pearl bed. The discount rises with sector
coverage, up to 65%. Known-bed sectors keep their full exploration value. The
fallback sector target uses the same discount, so it also prefers fresher or
bed-bearing sectors when ordinary target search finds nothing.

Move scoring also charges up to 3 points when the move brings the dragon closer
to visible teammate heads within six tiles. Crown and feeder roles are exempt.
Resource target scoring, combat evaluation, and split logic are inherited from
V41.

In a native ten-map, both-seat screen against V41, V42 scored **8–12** with no
runner errors, replay-analysis errors, or runtime faults. It swept Portals and
Slithery Fight; V41 swept Autarky, Default, Devil, and Trophy; the other four
maps split. This is one generated-seed development screen, so V42 remains
experimental. Logs, replays, and the report are in
`experiment_data/ares-v42-memory-team-dispersion_20260930123201634335/`. See
the [V42 finding](../../docs/findings/2026-09-30-ares-v42-memory-team-dispersion.md).
