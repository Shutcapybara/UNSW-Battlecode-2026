# THE GOAT v02 — sprint discipline

1. **Built:** `bots/the-goat-v02-sprint-discipline`, a new THE GOAT lineage snapshot copied from the frozen Fenrir V20 source; only `w_sprint` changes from 1.0 to 1.5, with an activation marker.
2. **Deciding number:** on 16 leak-focused exact fixtures versus the Fenrir parent, length r100 was **8 better / 7 same / 1 worse**, sign-test **p = 0.039**, with r100 pearls flat in the matched seed-1 v02/v03 sweep; the sprint metric fell only modestly, 0.811 → 0.796 mean sprint-extra/eaten.
3. **Pairs:** full live seed-1 panel was 10–10 vs Fenrir V20, 10–10 vs Bifröst V01, 11–9 vs Gavroche V33, and 14–6 vs Gavroche V66; all four had zero errors. Generalisation was 33–29 over 62 games across all transformed/public/synthetic maps, zero errors.
4. **Sandbox:** the first pinned Schooltime probe failed with two CPU-limit/no-action deaths (max `87.6M` points); a bounded v04 successor then failed its first Trauma B probe with ten CPU-limit errors (max `99.9M`). Native matchup results therefore do not clear the runtime gate.
5. **What failed:** the original 25% sprint-tax target was not met; the harder v03 sibling was rejected after 1/7/0 r100-length pairs and 0/8/0 r100-pearl pairs versus v02. The C++ room-rescue v01 was also rejected after a neutral smoke result and a 1–19 Fenrir screen.
6. **Next:** keep v02 frozen as the best native THE GOAT candidate, but move runtime work to a lighter host or compiled chassis; do not promote or combine mechanisms until a candidate clears the pinned gate and survives repeated strongest-control panels.

## Method and scope

The starting guidance was `docs/TEAM-SUMMARY-2026-09-29.md`: optimize leaks,
benchmark against the strongest measured bots rather than the historical zoo,
and report the live pool beside an atlas-free out-of-sample panel. The controls
were selected from the current `FRONTIER.md` top entries: Fenrir V20, Bifröst
V01, Gavroche V33, and Gavroche V66.

`tools/cx/arena.py` was extended to count the extra segments spent by sprint
actions. `tools/cx/bench.py` was extended to accept map-relative paths, so the
generalisation run included the nine `maps/var` transforms, two `maps/pub`
fixtures, and all twenty `maps/new` maps. These are local ignored results; no
replay payloads or generated build state is added to the lineage.

## Runtime gate result

The v02 sandbox check was intentionally stopped after the first completed
fixture once it recorded two CPU-limit/no-action deaths; it reached a maximum
of `87,580,567` points. The v04 attempt was likewise stopped after its first
completed fixture after ten CPU-limit errors and a maximum of `99,906,163`
points. These failures are recorded as negative evidence rather than hidden
behind the stronger native matchup results.
