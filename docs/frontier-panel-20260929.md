# All-map frontier panel

Campaign `187e0e722be944ec90f626a129b4b544`; 16 bots × 35 maps, 8,400 distinct directional fixtures.

The 6 repeated ledger rows were reduced to one result per fixture. 1 repeated fixture had different outcomes; the six pilot/sweep overlaps use the pilot results.

## ELO estimates

Bradley–Terry scores use win = 1, draw = 0.5, loss = 0, a 400-point scale, and an A-seat term. Ratings are centered at 1,500. Estimated A-seat effect: +19.1 ELO.

| Rank | Bot | All-map ELO |
|---:|---|---:|
| 1 | fenrir-v20-crowded-resource-revalue | 1654.3 |
| 2 | bifrost-v01-portal-memory | 1620.9 |
| 3 | gavroche-v33-half-support | 1618.0 |
| 4 | gavroche-v66-supported-safe | 1617.2 |
| 5 | von_neumann-x04-support | 1586.8 |
| 6 | skadi-v13-clear-exit-only | 1586.1 |
| 7 | sinbad-v07-divecap | 1572.6 |
| 8 | serre-v01-foundation | 1566.2 |
| 9 | monte_christo-x12-remote-density | 1534.8 |
| 10 | tew-v12-mid-support | 1485.1 |
| 11 | hunter-v20-portal-scouts | 1438.6 |
| 12 | hunter-v23-supported-arrival-feed | 1416.7 |
| 13 | ouroboros-v10-beacon | 1407.8 |
| 14 | hunter-v14-cpp-hybrid-route-spacing | 1405.5 |
| 15 | fry-v14-stateful-size-aware-3 | 1356.8 |
| 16 | kraken-v04-eval | 1132.6 |

## Point map leaders

| Map | Leader | Equal-lineage score |
|---|---|---:|
| Colosseum | fenrir-v20-crowded-resource-revalue | 80.6% |
| arena | hunter-v23-supported-arrival-feed | 80.8% |
| autarky | fenrir-v20-crowded-resource-revalue | 94.4% |
| big_empty | fenrir-v20-crowded-resource-revalue | 82.6% |
| default | bifrost-v01-portal-memory | 83.3% |
| default_small | fenrir-v20-crowded-resource-revalue | 83.3% |
| devil | monte_christo-x12-remote-density | 79.9% |
| dilemma | hunter-v23-supported-arrival-feed | 92.3% |
| new/mc26_archipelago | fenrir-v20-crowded-resource-revalue | 81.2% |
| new/mc26_crossroads | von_neumann-x04-support | 74.3% |
| new/mc26_delayed_commons | hunter-v23-supported-arrival-feed | 86.5% |
| new/mc26_equatorial_belt | gavroche-v66-supported-safe | 92.3% |
| new/mc26_far_harbors | gavroche-v66-supported-safe | 83.3% |
| new/mc26_nursery_bays | skadi-v13-clear-exit-only | 81.9% |
| new/mc26_pinwheel | fenrir-v20-crowded-resource-revalue | 77.8% |
| new/mc26_portal_quartet | bifrost-v01-portal-memory | 81.2% |
| new/mc26_pulse_farms | fenrir-v20-crowded-resource-revalue | 87.5% |
| new/mc26_relay_depots | monte_christo-x12-remote-density | 100.0% |
| new/mc26_scattered_fleets | gavroche-v66-supported-safe | 70.5% |
| new/mc26_seam_market | gavroche-v33-half-support | 71.8% |
| new/mc26_spring_wells | serre-v01-foundation | 80.6% |
| new/md26_causeway_detour_s0 | fry-v14-stateful-size-aware-3 | 91.7% |
| new/md26_causeway_portal_s0 | von_neumann-x04-support | 87.5% |
| new/md26_commons_shared_s0 | gavroche-v66-supported-safe | 69.2% |
| new/md26_commons_spread_s0 | hunter-v20-portal-scouts | 94.2% |
| new/md26_orchard_narrow_s0 | hunter-v20-portal-scouts | 94.2% |
| new/md26_orchard_wide_s0 | hunter-v14-cpp-hybrid-route-spacing | 96.2% |
| new/md26_promenade_ring_s0 | gavroche-v33-half-support | 74.4% |
| portals | sinbad-v07-divecap | 75.0% |
| queen_of_spades | skadi-v13-clear-exit-only | 85.4% |
| schooltime | fenrir-v20-crowded-resource-revalue | 93.8% |
| slithery_fight | sinbad-v07-divecap | 75.0% |
| stronghold | sinbad-v07-divecap | 83.3% |
| trauma | sinbad-v07-divecap | 79.2% |
| trophy | von_neumann-x04-support | 88.9% |

## Frontier

A candidate is dominated only when the paired lineage-bootstrap interval is nonnegative on every qualified map and strictly positive on at least one. Each map needs both sides against at least three shared opponents. The frontier retains candidates with no supported dominator.

| Bot | Dominated by |
|---|---|
| bifrost-v01-portal-memory | — |
| fenrir-v20-crowded-resource-revalue | — |
| fry-v14-stateful-size-aware-3 | — |
| gavroche-v33-half-support | — |
| gavroche-v66-supported-safe | — |
| hunter-v14-cpp-hybrid-route-spacing | — |
| hunter-v20-portal-scouts | — |
| hunter-v23-supported-arrival-feed | — |
| kraken-v04-eval | — |
| monte_christo-x12-remote-density | — |
| ouroboros-v10-beacon | — |
| serre-v01-foundation | — |
| sinbad-v07-divecap | — |
| skadi-v13-clear-exit-only | — |
| tew-v12-mid-support | — |
| von_neumann-x04-support | — |

## Limits

The bootstrap resamples opponent lineages as whole clusters. It does not capture all behavior randomness or correct for the number of pairwise comparisons. Results describe this frozen 35-map panel and should not be read as official contest ratings.

Full map-by-bot profiles and every pairwise interval are in the local generated
file [`frontier.json`](../experiment_data/benchmark_20260928083347416650/frontier/frontier.json).
