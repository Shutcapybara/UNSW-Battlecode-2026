# THE GOAT lineage

Reviewed 2026-09-29. THE GOAT is a measured, immutable lineage for small
mechanism changes. It is not in `FRONTIER.md` yet; the current evidence is a
seed-1 local panel and does not meet the frontier registry's broader repeated
35-map admission standard.

## Retained snapshot

`the-goat-v02-sprint-discipline` is the current retained native candidate. It
is not runtime-ready for registration: its first pinned sandbox probe hit two
CPU-limit/no-action deaths. It is a standalone copy of
`fenrir-v20-crowded-resource-revalue` with one policy change:
`w_sprint = 1.5` instead of `1.0`. Routing, density, newborn separation,
portal handling, and crown logic are otherwise inherited from the frozen
Fenrir source. The change is map-independent and has a trace marker
`ACT:goat-v02`.

On the 16-game leak-focused exact panel against the Fenrir parent, v02 was
better/same/worse `8/7/1` on length at r100, sign-test `p=0.039`, with zero
errors. On the full ten-map live panel (both sides, seed 1), the candidate
scored 10–10 against Fenrir V20, 10–10 against Bifröst V01, 11–9 against
Gavroche V33, and 14–6 against Gavroche V66. Every run had zero bot errors.

The sprint accounting is deliberately reported separately: mean
`sprint_extra / eaten` moved from 0.811 in the Fenrir matched baseline to
0.796 in v02, while mean `sprint_extra / eaten_r100` moved from 14.426 to
14.331. This is a small tax reduction, not the originally hoped-for 25% drop;
the reason to retain v02 is the paired r100 material result with flat r100
pearls, not the tax metric alone.

The generalisation panel contains all 31 transformed/public/synthetic maps in
the measured command, both sides, seed 1: 62 games, 33–29, zero errors. No
map identity or atlas branch was added to the lineage.

## Rejected arms

`the-goat-v01-room-rescue` is the C++ chassis arm. It added a guarded split
when all known moves were room-cramped and both resulting bodies passed the
existing room proof. Its four-map smoke comparison to `anna-a02-chassis` was
1/6/1 better/same/worse on length r100 and it was only 1–19 against Fenrir on
the ten-map one-seed screen. It is preserved as a negative control, not a
retained candidate.

`the-goat-v03-sprint-hard` raised the sprint weight to `2.0`. On the same
seed-1 leak-focused fixtures against v02 it was 1/7/0 on length r100 and
0/8/0 on eaten pearls r100, so v02 remains the selected setting.

`the-goat-v04-bounded-sprint` attempted to preserve v02 while lowering search
and flood caps. Its first pinned Trauma B probe recorded ten CPU-limit errors
and a maximum of `99,906,163` points, so the bounded successor is rejected.

## Reproduction

The local fixture records are under ignored `build/` paths. The main commands
were:

```sh
python3 tools/cx/bench.py bots/the-goat-v02-sprint-discipline \
  bots/fenrir-v20-crowded-resource-revalue --maps live --seeds 1 \
  --sides AB --jobs 4 --out build/goat-v02-vs-fenrir-live-s1.jsonl

python3 tools/cx/bench.py bots/the-goat-v02-sprint-discipline \
  bots/fenrir-v20-crowded-resource-revalue --maps <generalisation-list> \
  --seeds 1 --sides AB --jobs 4 \
  --out build/goat-v02-vs-fenrir-generalisation-s1.jsonl
```

`tools/cx/arena.py` now records `sprint_extra`, `sprint_actions`, and the two
sprint-per-eaten ratios; `tools/cx/bench.py` accepts map-relative paths such as
`new/mc26_archipelago` for out-of-sample fixtures.

The sandbox failures are deliberately retained in the local evidence ledger:
v02 reached `87,580,567` points with two CPU-limit/no-action deaths on its first
Schooltime probe, while v04 reached `99,906,163` points with ten CPU-limit
errors on its first Trauma B probe. Neither snapshot is promoted to
`FRONTIER.md`.
