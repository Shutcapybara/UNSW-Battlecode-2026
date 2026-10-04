---
id: shenzhen-unit11-cap-dose-and-corpse-economy
author: Shenzhen (P2-A analyst, Opus 5.5)
kind: simulator dose check + corpus query
title: Unit 11 — H-SZ26 refuted at two doses (no production splits at ≥ 60 / ≥ 52 units costs 19–28 % total on Slithery); late-game length on cap maps is almost all corpse pearls, and the top ten recycle ~50 % more
evidence: cloud workspace (unswbc 1.2.9 live Slithery, carthage-05 C+D parent vs dose arms, seeds 1–3 both seats; one game lost to a build race at dose 60); corpus: tools/shenzhen/fountain.py, 387 post-m2 games on Slithery, Around UNSW, Islands, Trauma, Portals with a top-ten side or us
---

# 1. H-SZ26 dose check (D-044 style: none / 60 / 52)

| arm vs C+D | sides | wins | total at end | total at r400 | bed eats r150+ | corpse eats r150+ | trapped len ≥ 4 at ≥ 60 units |
|---|---|---|---|---|---|---|---|
| dose 60 | 5 | 2/5 (parent 3/5) | 605 vs 745 (−19 %) | 935 vs 1,034 (−10 %) | 2,917 vs 3,594 (−19 %) | 3,533 vs 4,188 (−16 %) | 45 vs 59 |
| dose 52 | 6 | 3/6 (3/6) | 637 vs 884 (−28 %) | 1,117 vs 1,241 (−10 %) | 3,697 vs 4,160 (−11 %) | 4,368 vs 5,068 (−14 %) | 32 vs 90 |

Stopping production at the cap removes dragons that would have eaten beds and corpses. Both doses lose material and do
not gain wins; the effect grows with the dose. **H-SZ26 (stop production at the cap, grow instead) is refuted in the
simulator.** This agrees with Himeji H25-02 (throttling production may reduce bed capture) and with my unit-10 G result.

# 2. Where late-game length comes from (corpus)

Eats by cell type after r150, per side (beds from `maps/live`, which match the server; "other" = cells with no bed, i.e.
corpse pearls):

| map | top ten: bed / corpse | us: bed / corpse | top ten − us, corpse |
|---|---|---|---|
| Around UNSW | 3 / 1,542 | 4 / 986 | +56 % |
| Islands | 20 / 1,179 | 7 / 807 | +46 % |
| Slithery Fight | 166 / 1,718 | 109 / 1,076 | +60 % |
| Trauma | 30 / 609 | 22 / 397 | +53 % |
| Portals | 51 / 820 | 63 / 957 | −14 % |

Late-game income on these maps is 85–99 % corpse pearls. The top ten recycle about half again as many on four of five
maps; Portals is the exception (we recycle more there and still lose: 0.21 win vs 0.75). Bed cells with interval 1 (the
"fountains", 8–24 per map) yield almost nothing (≤ 25 eats per side per game on Slithery, ~1 elsewhere): the interval is
not a per-round regrowth. H-SZ27 (fountains) is dropped.

# 3. Hypotheses

| id | claim | falsifier | size | suits |
|---|---|---|---|---|
| H-SZ26 | stop production at the cap | **refuted in simulator** at doses 60 and 52 (total −19 % / −28 %, wins not up) | — | — |
| H-SZ27 | pearl fountains (interval-1 beds) | **dropped**: ≤ 1 eat per side per game outside Slithery | — | — |
| H-SZ28 recycling throughput | Late-game length on cap maps is the corpse loop: split → die → eaten. The top ten run it ~50 % faster (Around UNSW 1,542 vs 986 corpse meals after r150). Our bottleneck is who eats the corpses: if our corpses are eaten by enemies or left on the board, the loop leaks. Next: split corpse meals by origin (ally vs enemy) and count uneaten corpse pearls at r490. | ally-corpse share of our corpse meals ≥ the top ten's, and uneaten corpse pearls not higher than theirs (then the gap is volume, not leakage) | corpus, 400 games | analyst (next unit) |
| H-SZ29 corpse proximity | Culls should happen next to a long ally's head, not wherever the small dragon is (the crown teams' donors die 3 rounds before the queen eats). A cull rule keyed to "a long ally head within 2" converts more corpse into length. | ally-corpse meals per cull not up ≥ 20 % in simulator | simulator, Slithery/Around UNSW 12 sides | Claude tester |
