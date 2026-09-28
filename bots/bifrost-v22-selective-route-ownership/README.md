# Bifröst v22 — selective route-based pearl ownership

V21's route-aware ownership improved its compact-map aggregate by one result
but regressed on larger maps. V22 runs those searches only on maps of at most
625 cells and uses a route distance only when it differs from torus Manhattan
distance by at least two steps. Otherwise it preserves V01's original ownership
comparison. This tests whether the compact-map gains survive with fewer
unnecessary target changes.

The focused native screen uses the same six maps and four competitive families
as the V01 control. Results are recorded in the [family notes](../../docs/bifrost-family.md).
