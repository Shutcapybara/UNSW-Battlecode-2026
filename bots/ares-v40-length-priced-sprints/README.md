# Ares V40 — length-priced sprints

V40 branches directly from V37. Its simulator already removes one tail
segment for every move after the first, so normal move scoring now prices that
simulated body-length change once instead of also subtracting a separate
sprint cost. A single-move pearl grows the body through the same length term;
a pearl collected on a dash replaces the segment spent and does not increase
current length.

An uncontested pearl collected after the first move gets a small opportunity
cost (`0.25` of a segment value) because taking it early gives up a later
growth opportunity. If an enemy head is within two tiles of the pearl, the
candidate instead gets one segment value for denying it. Each additional move
continues to cost one segment through the simulated body loss; head-to-head
dash scores use the same per-segment value.

The focused regression checks that an uncontested pearl is left for a normal
move and that a nearby rival makes the dash worthwhile. On the seed-1 ten-map
panel, V40 beat V37 **11–9** with zero runner errors. Length-3 dash rates were
2.43% for V40 (1,170/48,092 turns) and 1.94% for V37 (998/51,467 turns) in
that panel. This is a development screen, not a promotion result. See the
[V40 finding](../../docs/findings/2026-09-30-ares-v40-length-priced-sprints.md).
