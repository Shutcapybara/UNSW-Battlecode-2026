# Ares V44 — shared sector exploration

V44 forks V43 after replay 710870 showed dragons repeatedly scouting the same
low-value areas. Each dragon previously held a private explored-sector count,
and no message reserved a frontier target for a teammate.

V44 shares the strongest single-dragon coverage report for each 8×8 sector and
whether any pearl bed has been observed there. Coverage is monotone and never
sums reports from different dragons, avoiding false confidence from overlapping
vision. A sector's barren discount still grows gradually with coverage and
reaches its maximum only when the sector is fully known.

An explorer also advertises its target sector with an eight-round lease,
refreshed every three rounds. Other dragons sharply discount unseen cells in a
claimed sector and prefer unclaimed sectors in the fallback search. Receivers
relay active claims and improved sector reports. These messages use the soft
density lanes first; reports can use a pearl-gossip lane when no softer lane is
available. Higher-priority crown, prey, and split-handoff traffic keeps its
existing priority. V43's visible-teammate approach cost remains in place.

Against V43 on the ten live maps, both sides, and seeds 1–3, V44 scored
**32–28** over 60 games, with no draws or runner errors. It scored 4–2 on
Autarky. This small screen is inconclusive and does not establish a reliable
gain; V44 remains experimental. Results are in
`build/cx/ares-v44-vs-v43-20260930.jsonl` and
`build/cx/ares-v44-vs-v43-seeds2-3-20260930.jsonl`. See the
[V44 finding](../../docs/findings/2026-09-30-ares-v44-shared-sector-exploration.md).
