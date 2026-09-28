# Bifröst v01 — portal memory

Bifröst is the rainbow bridge in Norse mythology. The name fits a policy that
uses map memory to make risk-aware decisions around portal exits.

## Lineage

Parent: Gavroche V54 sparse-room, the selected active candidate. This keeps its
round-40 search cap, sparse late-game search and flood caps, crown/endgame
policy, and CPU-conscious move generation. Gavroche V54 already carries the
supported-trade and dive-value mechanisms measured in Gavroche V32.

This version adds portal-exit risk memory from the Scholze V03 / Witten X01
lines. It records where other bodies were recently visible, then prices an
unseen portal exit at full risk if a body was recently near it, reduced risk
if the exit was recently surveyed and quiet, and half risk if the area is
unknown. The policy still uses the original full-risk estimate when no exit
cell can be identified.

## Confirmed Autarky losses

The replay headers do not identify the family names; the user identified
Gavroche as side A in both Autarky openers: M376704 (from
battle-M376704-replays.zip) and M376714 (from
battle-M376714-replays.zip). Gavroche therefore lost both games.

- M376704 ended by Gavroche's elimination at round 290. Gavroche collected
  176 pearls and made 9 portal steps; side B collected 348 pearls and made
  65 portal steps. This is the direct motivation for testing portal-exit
  memory and more willing exploration.
- M376714 reached the round limit. Both sides finished with four units, but
  Gavroche had longest dragon 4 and total length 12; side B had longest dragon
  36 and total length 83. Pearl pickups were close (361 for Gavroche, 344 for
  side B), while side B made 27 suicide actions. This points to a late-game
  crown-growth and feeding challenge.

Bifröst keeps Gavroche V54's endgame parameters for this first comparison so
the portal-memory change remains identifiable. The benchmark includes both
Autarky sides, the V54 control, and strong cross-family references.

## Benchmark status

The first benchmark completed with 372/372 games against 31 opponents on six
maps, with both sides played using deterministic fixture seeds. The panel had
22 of the 24 primary families in the [curation report](../../docs/benchmark-pool-20260927.md)
(two, `vn-x01-margin-2` and `vn-x01-preymin-6`, were unavailable locally),
eight additional frontier families from the supplied rankings, and Gavroche
V54 as the parent control. It recorded 273 wins, 0 draws, and 99 losses
(73.4%), with no game errors or runtime faults. This run used native execution
without the judge CPU sandbox, so it does not establish judge CPU safety.

Against the active Gavroche V54 parent, Bifröst scored 8-4. It won both
Autarky side swaps (2-0), Queen of Spades (2-0), and Trauma (2-0); split
Big Empty and Stronghold (1-1 each); and lost both Schooltime sides (0-2).
Across the eight frontier families from the current rankings screenshot, it
scored 55-41 over 96 games. Across all opponents, its weakest maps were Big
Empty (30-32), Trauma (35-27), and Stronghold (36-26); it scored 60-2 on
Autarky, 54-8 on Queen of Spades, and 58-4 on Schooltime. These are observed
fixture results, not an uncertainty-adjusted rating.

Full tables, per-map and per-opponent logs, and replay artifacts are in the
benchmark report (`../../experiment_data/bifrost-v01-portal-memory_20260927104358397848/summary.md`)
and interactive report (`../../experiment_data/bifrost-v01-portal-memory_20260927104358397848/index.html`).
Family-level matchup observations and iteration status are tracked in the [Bifröst family notes](../../docs/bifrost-family.md).
