# Current bot frontier

**Updated 2026-09-29.** Rows are ordered by displayed ELO. Numbers in the first
column are 35-map panel ranks; `Screen` entries have provisional 10-map ratings.

| Rank / status | Bot snapshot | ELO (evidence) | Source fingerprint |
|---:|---|---:|---|
| Screen | `tyr-v12-devil-scout-tiebreak` | 1,786 (10-map) | `d2f691c4fc0c` |
| 1 | `fenrir-v20-crowded-resource-revalue` | 1,654.3 (35-map) | `dc7717689882` |
| 2 | `bifrost-v01-portal-memory` | 1,620.9 (35-map) | `037872088e6f` |
| 3 | `gavroche-v33-half-support` | 1,618.0 (35-map) | `57d123043c7f` |
| 4 | `gavroche-v66-supported-safe` | 1,617.2 (35-map) | `a5c8dc0f8db5` |
| 5 | `von_neumann-x04-support` | 1,586.8 (35-map) | `3772d5a35503` |
| 6 | `skadi-v13-clear-exit-only` | 1,586.1 (35-map) | `34d716a3492d` |
| Screen | `eunchae-s02-pearl-band` | 1,576 (10-map) | `46ffdb69ce64` |
| 7 | `sinbad-v07-divecap` | 1,572.6 (35-map) | `c759a5c8a8ba` |
| 8 | `serre-v01-foundation` | 1,566.2 (35-map) | `ae4bcc23254c` |
| 9 | `monte_christo-x12-remote-density` | 1,534.8 (35-map) | `5589c30d0525` |
| 10 | `tew-v12-mid-support` | 1,485.1 (35-map) | `8bff0f54828f` |
| 11 | `hunter-v20-portal-scouts` | 1,438.6 (35-map) | `f844fa3ae595` |
| 12 | `hunter-v23-supported-arrival-feed` | 1,416.7 (35-map) | `b10300e824d4` |
| 13 | `ouroboros-v10-beacon` | 1,407.8 (35-map) | `a9eafbaffc51` |
| 14 | `hunter-v14-cpp-hybrid-route-spacing` | 1,405.5 (35-map) | `6ba4e603ad19` |
| 15 | `fry-v14-stateful-size-aware-3` | 1,356.8 (35-map) | `962541eb674d` |
| 16 | `kraken-v04-eval` | 1,132.6 (35-map) | `7d23d380f291` |

These provisional screen ELOs are anchored to the 16-bot panel. Map-bootstrap
95% intervals from 2,000 resamples (seed 20260929): Tyr 1,682–1,924; Eunchae
1,436–1,716. The fit uses 160 recent screen games across five screen bots,
holding panel ratings and the +19.1 ELO A-seat term fixed. Intervals do not
capture all run-to-run behavior randomness.

## Panel and admission

The official ratings cover 35 maps (15 established, 20 custom), both starting
sides, and 15 opponents per bot: 8,400 unique games total. Preliminary
Bradley–Terry ELOs are centered at 1,500 across these source fingerprints;
they are not contest ratings. A paired lineage bootstrap found no supported
map-wise dominator, so all 16 remain on the statistical frontier.

A map qualifies for dominance analysis when both bots have both sides against
at least three opponents there. A bot dominates another only when the paired
95% interval is nonnegative on every qualified map and positive on at least
one. New candidates need 200 distinct directional fixtures, 15 exact-source
opponents, 6 lineages, 10 maps, and at least 3 paired opponents on 10 maps
before admission. Screen rows above do not meet that threshold.

Full ratings and intervals are in the [35-map panel report](docs/frontier-panel-20260929.md).
The 7,616-game campaign contribution is
[`game_stats/runs/187e0e722be944ec90f626a129b4b544.parquet`](game_stats/runs/187e0e722be944ec90f626a129b4b544.parquet).
Recreate the analysis with
`.venv/bin/python tools/frontier_panel.py experiment_data/benchmark_20260928083347416650`.

## Gaia experimental lineage

`gaia-v47-medium-map-threat-pearl` is the current retained Gaia snapshot,
forked from Fenrir V20 through the V08 parent-aware line and V44's compact-map
dispersion policy. It adds a bounded enemy-threat pearl-exit check on ordinary
compact maps while retaining V44's tiny-arena and Big Empty behavior. The
repeated four-map 48-game panel scored 13W-11L for V47 versus 12W-12L for V44
and 8W-16L for V08, with zero runner errors or TLEs. Against Fenrir, V47
matched V44 at 3W-5L and won the direct V47-vs-V44 comparison 5W-3L. These are
family-development results, not frontier-qualified evidence. V09–V63 remain
immutable lane, pearl, breeding, pathfinding, split, portal, and density
controls; V51–V63 did not produce a significant repeatable gain. V56 improved
portal traversal on the portal-heavy screen but lost to Fenrir, while V57/V58
traded early population for lower newborn risk. Post-V63 Arena diagnostics
tested immediate-threat veto, Arena child siting, and stronger opposing lanes;
each lost both Fenrir orientations and was rejected. No Gaia version has
triggered the C++ fallback threshold: all tested panels completed with zero
runner errors and zero TLEs. Additional contact-penalty relaxations also
scored 0-8 on the four-map screen, so V47 remains the retained Gaia
candidate.

The serial harness is now the promotion gate (`--jobs 1`): concurrent
low-level runs were not reproducible and an apparent pearl-value 8-0 was
reversed by replay-producing and serial runs at 0-8. Serial V54 four-way
lanes and the subsequent contact/pearl controls also failed their focused
screens, so no Gaia V64 has been promoted.

## Recent screens

- **Tyr V12:** 14–6 against Fenrir on 10 maps; it won at least one game on
  nine maps and swept both seats on five. The other candidates in that screen
  were Chaewon Y04 (10–10), Heimdall V10 (8–12), and Tyr V01 (8–12). Outcomes:
  [`db75c3f2.parquet`](game_stats/runs/db75c3f2093b4e71b67afebb3e91736c.parquet),
  [`27f41a20.parquet`](game_stats/runs/27f41a20010e40019846871a99347b23.parquet).
- **Eunchae S02:** 10–10 against parent Chaewon Y04, 9–11 against Fenrir,
  6–14 against Bifröst, and 5–15 against Tyr V12. It went 7–1 on Crossroads
  and 6–2 on Scattered Fleets, but 1–7 each on Portal Quartet, Queen of Spades,
  and Stronghold. No draws or runner errors. Results:
  [`ed4cbcaa.parquet`](game_stats/runs/ed4cbcaa5ccc48de92f1dd1c9a2cb3bc.parquet);
  logs: `build/frontier-eunchae-s02-screen-20260929/`.
- **Fenrir V20 vs Hunter V20:** 50–20 over 70 games on all 35 maps, with no
  draws or runner errors. Results:
  [`549ce497.parquet`](game_stats/runs/549ce497d5e14041bf5321a96787d7a0.parquet).
- **Tyr V16:** `tyr-v16-live-loss-response` scored 7–11 against Tyr V12 in an
  18-game screen on the nine review maps, both sides, zero runner errors. V16
  split 1–1 on seven maps and lost both Devil and Trauma games. This unseeded
  focused screen gives V16 no all-map ELO; keep V01 as the baseline and V12 as
  the Devil specialist. See the [Tyr family notes](docs/tyr-family.md); results
  are in `build/tyr-v16-vs-v12-loss-review-20260929/`.
- **Tyr V33:** `tyr-v33-targeted-resource-defense` scored 55–53 against V12
  over six fixed seeds, both sides on the same nine maps (108 games, no draws
  or errors). Fresh seeds 7–18 reversed that edge: 91–125 over 216 games.
  Across seeds 1–18, V33 scored 146–178; it went 32–4 on Trauma, 2–34 on
  Autarky, and 6–30 on Dilemma. Keep it experimental, not a general V12
  improvement; see the [Tyr family notes](docs/tyr-family.md), the
  [V33 result](bots/tyr-v33-targeted-resource-defense/README.md), and
  `build/tyr-v33-fresh-v12-seeds7-18-absolute-20260929/`.
- **Tyr V34:** lowering V25's pearl-funded sprint threat floor to 0.2 scored
  37–71 against V12 on fresh seeds 19–24 (108 games, zero errors); V12 swept
  26 paired map/seed sets to V34's 9, with 19 split. Rejected. V01 remains the
  all-map baseline and V12 the Devil-specialist reference; see the [Tyr family
  notes](docs/tyr-family.md) and [V34 result](bots/tyr-v34-calibrated-pearl-sprint/README.md).

The V12, Eunchae, and Fenrir screens above used native `unswbc 1.2.1` with both
starting sides. Tyr V16 used native `unswbc 1.2.2` on its focused nine-map
screen. The [Tyr family notes](docs/tyr-family.md) contain its earlier Devil
and Yuna experiments. The earlier three-map pilot is preserved in
[`bc86c2ad.parquet`](game_stats/runs/bc86c2adc518428f8d77039e11111a97.parquet);
its dominance findings are limited to those three maps.

## Defaults and upkeep

The deployed contest version is not recorded here. [`comparison.toml`](comparison.toml)
keeps Ouroboros V10, Hunter V14, Hunter V20, Fry V14, and Kraken V04 as controls.
See [`docs/benchmarking.md`](docs/benchmarking.md) for the workflow,
[`game_stats/README.md`](game_stats/README.md) for the ledger, and
[`maps/new/EXPLAINER.md`](maps/new/EXPLAINER.md) for custom maps. Update this
table with exact source fingerprints and linked results when a candidate is
screened or admitted.
