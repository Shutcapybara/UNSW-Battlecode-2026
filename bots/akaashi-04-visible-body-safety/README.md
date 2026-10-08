# Akaashi 04 — visible own-body collision safety

Fork of immutable Akaashi 03; preserves queen escape, visible queen attacks and
threatened queen split dodging. Atlas disabled; no map-specific conditions.

Movement simulation includes every own segment in the current legal observation,
including disconnected pieces outside the head-connected reconstructed chain.
When that chain is partial, its front is not the real tail: do not free those
known occupied cells while evaluating a sprint. Complete bodies retain ordinary
exact tail-vacancy simulation. A final known-collision check also replaces a
DOOMED movement command with a legal single step when available, preserving
intentional feeder/cap-cull deaths.

Trigger: Around UNSW replay 1410660, dragon 711 at r408: length 36, represented
chain only four cells, chooses NEE and self-collides after eating at length 37.
04 chooses N, avoiding the observed self-collision. In the official-engine
scripted continuation it survives that round but dies against a wall at r411;
this fix does not claim to solve every long-dragon death.

See the [campaign review](../../docs/finals-campaign/HEARTBREAKER_ITERATION.md)
and [family notes](../../docs/akaashi-family.md). Tests:
`python3 tests/test_akaashi_visible_body.py` plus prior Akaashi regression suites.
