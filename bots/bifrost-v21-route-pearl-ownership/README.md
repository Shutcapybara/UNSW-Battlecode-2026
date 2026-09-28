# Bifröst v21 — route-based pearl ownership

This candidate keeps V01's movement and resource policy, but corrects pearl
ownership for up to three nearby allies using bounded searches over known map
terrain and paired portals. The baseline compares torus Manhattan distance,
which can send multiple dragons toward the same target when walls or portals
make the actual routes different. The bounded search falls back to the baseline
distance if it cannot reach a cell within its cap.

This targets the reported Trophy opening overlap and portal-era route
coordination. The focused native screen uses the same six maps and four
competitive families as the V01 control. Results are recorded in the [family
notes](../../docs/bifrost-family.md).
