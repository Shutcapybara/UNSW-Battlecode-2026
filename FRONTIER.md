# FRONTIER — bot pool and current status

**Reviewed 2026-09-29.** This is the canonical page for candidate status,
estimated ELOs, the default comparison roster, and contest deployment notes.

> **COMPLETE — 35-map frontier panel.** All 8,400 directional games were
> recorded for 16 bots across the shared bundle: 15 established maps and 20
> custom maps under `maps/new/`. The six family-specific reserve maps under
> `configs/` remain separate holdouts. Six pilot/sweep repeats were reduced to
> one result each; the single conflict keeps the pilot result. There were no
> runner errors or missing fixtures.
>
> The paired lineage-bootstrap rule found no supported dominator, so all 16
> bots remain on the statistical frontier. This frontier records the absence
> of map-wise dominance under the stated evidence threshold. The ELOs and
> map-leader scores still separate the candidates. Full ratings, map leaders,
> and pairwise intervals are summarized in the
> [panel report](docs/frontier-panel-20260929.md). The 7,616 campaign games are
> in [`game_stats/runs/187e0e722be944ec90f626a129b4b544.parquet`](game_stats/runs/187e0e722be944ec90f626a129b4b544.parquet);
> the full per-pair intervals are in the generated local data at
> `experiment_data/benchmark_20260928083347416650/frontier/frontier.json`.
> Recreate the analysis with
> `.venv/bin/python tools/frontier_panel.py experiment_data/benchmark_20260928083347416650`.

| Bot snapshot | All-map ELO | Statistical frontier | Fixtures / opponents / maps | Source fingerprint |
|---|---:|---|---:|---|
| `fenrir-v20-crowded-resource-revalue` | 1,654.3 | Retained; no supported dominator | 1,050 / 15 / 35 | `dc7717689882` |
| `bifrost-v01-portal-memory` | 1,620.9 | Retained; no supported dominator | 1,050 / 15 / 35 | `037872088e6f` |
| `gavroche-v33-half-support` | 1,618.0 | Retained; no supported dominator | 1,050 / 15 / 35 | `57d123043c7f` |
| `gavroche-v66-supported-safe` | 1,617.2 | Retained; no supported dominator | 1,050 / 15 / 35 | `a5c8dc0f8db5` |
| `von_neumann-x04-support` | 1,586.8 | Retained; no supported dominator | 1,050 / 15 / 35 | `3772d5a35503` |
| `skadi-v13-clear-exit-only` | 1,586.1 | Retained; no supported dominator | 1,050 / 15 / 35 | `34d716a3492d` |
| `sinbad-v07-divecap` | 1,572.6 | Retained; no supported dominator | 1,050 / 15 / 35 | `c759a5c8a8ba` |
| `serre-v01-foundation` | 1,566.2 | Retained; no supported dominator | 1,050 / 15 / 35 | `ae4bcc23254c` |
| `monte_christo-x12-remote-density` | 1,534.8 | Retained; no supported dominator | 1,050 / 15 / 35 | `5589c30d0525` |
| `tew-v12-mid-support` | 1,485.1 | Retained; no supported dominator | 1,050 / 15 / 35 | `8bff0f54828f` |
| `hunter-v20-portal-scouts` | 1,438.6 | Retained; no supported dominator | 1,050 / 15 / 35 | `f844fa3ae595` |
| `hunter-v23-supported-arrival-feed` | 1,416.7 | Retained; no supported dominator | 1,050 / 15 / 35 | `b10300e824d4` |
| `ouroboros-v10-beacon` | 1,407.8 | Retained; no supported dominator | 1,050 / 15 / 35 | `a9eafbaffc51` |
| `hunter-v14-cpp-hybrid-route-spacing` | 1,405.5 | Retained; no supported dominator | 1,050 / 15 / 35 | `6ba4e603ad19` |
| `fry-v14-stateful-size-aware-3` | 1,356.8 | Retained; no supported dominator | 1,050 / 15 / 35 | `962541eb674d` |
| `kraken-v04-eval` | 1,132.6 | Retained; no supported dominator | 1,050 / 15 / 35 | `7d23d380f291` |

Each bot's coverage is 1,050 games against 15 opponents: both starting sides
on each of the 35 maps. These preliminary Bradley–Terry estimates are centered
at 1,500 across the 16 measured source fingerprints; they are not official
contest ratings. Every candidate pair qualified on all 35 maps, but no pair met
the paired lineage-bootstrap dominance rule on the full bundle. See the report
for map leaders and pairwise uncertainty intervals.

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

## All-map head-to-head completed

Fenrir V20 played Hunter V20 twice on every map in the 35-map bundle, once from
each starting side: **70 games, 50–20 for Fenrir, with no draws or runner
errors**. Fenrir swept both games on 18 maps, Hunter swept 3, and the sides split
the remaining 14. These 70 results document one direct matchup; the complete
16-bot panel and frontier are summarized above.

The sweep repeats six side/map fixtures from the earlier three-map panel; five
repeated results matched and one differed on arena. Bots can behave
non-deterministically, so these runs are not independent evidence and must not
be blindly pooled. The new sweep's 70 outcomes are saved in
[`game_stats/runs/549ce497d5e14041bf5321a96787d7a0.parquet`](game_stats/runs/549ce497d5e14041bf5321a96787d7a0.parquet)
and its local logs are under the ignored
`build/frontier-map-sweep-20260928/` directory.

## Experimental Norse family: Tyr

Tyr V01 combines Fenrir V20's measured core with Yuna V03's direction momentum.
Against Yuna V03 it scored **38–32 over 70 games on the frozen 35-map set**,
including a 2–0 Queen of Spades result, with no draws or runner errors. Tyr V04's
room-return guard scored 34–36 against Yuna on the same panel. Tyr V08 adds a
two-round, two-tile return penalty and scored **37–33 over 70 games** on the
same 35 maps, with no errors. Its Queen score was 0–2 in that full run; a
separate short Queen screen was 1–1 against Yuna and 2–0 against Tyr V01.

V08 runtime-source fingerprint (Python and bot.toml):
`facd1c5192b0f847f80042dde840754253a640117bf567431b434bacc7503d53`.

These are direct, unseeded screens against one opponent, not frontier admissions or ELO
ratings. Keep all Tyr variants out of the pilot table until the wider admission
screen is met. Details and runtime fingerprints are in
[the Tyr family notes](docs/tyr-family.md); match logs remain under ignored
`build/tyr-*/` directories.

Tyr V12 is a Devil-specific scouting arm: it scored **12–0** against Tyr V01
across six fixed seeds and both seats on Devil in native mode, then **12–0**
against the documented Yuna V05 Core finalist on the same Devil screen. Over all
46 repository maps and both seats, it scored **50–42** against Yuna V05 with
zero runner errors (one unseeded game per map-seat; 32–14 as Team A, 18–28
as Team B). Across paired map outcomes, Tyr won 14, Yuna won 10, and 22
split. Queen of Spades split 1–1. Sandbox faults remain; this preliminary
screen does not promote V12 to the all-map frontier. Details are in
[the Tyr family notes](docs/tyr-family.md); local results are under
`build/tyr-v12-yuna-v05-allmaps-20260929/` and
`build/tyr-v12-devil-vs-tyr1/`.
## How the frontier is defined

For each bot, compare its expected score (win = 1, draw = 0.5, loss = 0)
against the same panel on each map, using both starting sides. Weight maps and
opponent lineages equally. Bot A dominates bot B when A is no worse on every
qualified map and better on at least one. The frontier is the set of bots not
dominated by another. This preserves map specialists with different strengths.

For a dominance call, use paired evidence: compare the bots against the same
opponents, keep both starting sides together, group opponents by lineage, and
bootstrap whole lineages. Require the 95% interval for A−B to stay at or above
zero on every qualified map and above zero on at least one. A map qualifies
when both bots have both sides against at least three opponents on it. Missing
coverage means “under-tested,” not “dominated.”

The broader admission screen retained from the previous campaign is at least
200 distinct directional fixtures, 15 exact-source opponents, 6 opponent
lineages, 10 maps, and 10 maps with at least 3 paired opponents. These are
screening thresholds, not guarantees of statistical power. The earlier
24-bot shortlist is in
[`docs/benchmark-pool-20260927.md`](docs/benchmark-pool-20260927.md); it was a
loose empirical selection, not an exact Pareto frontier.

The 16-bot pilot played both sides against the other 15 bots on Colosseum,
arena, and autarky: 720 native games, 90 per bot. Its four point-estimate
survivors were Fenrir V20, Hunter V20, Hunter V23, and von Neumann X04. A
2,000-replicate paired lineage bootstrap found pilot-level dominance for these
pairs: Bifröst V01 over Hunter V14, Kraken, and Ouroboros; Fenrir V20 over Fry
V14, Hunter V14, Kraken, and Ouroboros; Fry V14 over Kraken; Gavroche V33 over
Fry V14, Hunter V14, Kraken, and Ouroboros; Gavroche V66 over Hunter V14,
Kraken, and Ouroboros; Hunter V23 over Kraken and Ouroboros; Serre V01 over
Kraken and Ouroboros; Sinbad V07 over Kraken and Ouroboros; and Skadi V13 over
Kraken and Ouroboros. These are only three-map findings. The bootstrap does not
capture all behavior randomness or adjust for the many pairwise comparisons.
No bot is retired based on this pilot.

## ELO method and pilot artifact

The pilot ratings use a Bradley–Terry model with win = 1, draw = 0.5, loss = 0,
an A-seat term, and a 400-point logistic ELO scale. Ratings are centered at
1,500 over these 16 bots. The estimated A-seat advantage was about 50 ELO. Each
bot had 90 games against 15 exact opponents on 3 maps; these estimates are
historical pilot ratings alongside the completed 35-map refit above.

The 720-game pilot is saved in
[`game_stats/runs/bc86c2adc518428f8d77039e11111a97.parquet`](game_stats/runs/bc86c2adc518428f8d77039e11111a97.parquet)
(run ID `bc86c2adc518428f8d77039e11111a97`, `unswbc 1.2.1`). Bifröst V29 was
not included because the family notes do not promote it; Bifröst V01 is the
strongest tested Zach Bifröst candidate. Rory Peterson's renamed Fenrir line
remains separate.

## Contest deployment and comparison defaults

The exact version currently deployed to the contest is **not recorded in this
checkout**. The default comparison roster in [`comparison.toml`](comparison.toml)
is Ouroboros V10, Hunter V14, Hunter V20, Fry V14, and Kraken V04. This is an
experiment control set, not a deployment record. The three-map pilot flagged
Fry V14, Hunter V14, Ouroboros V10, and Kraken V04 as dominated on those maps.
The full 35-map analysis found no supported dominator for any candidate; keep
all four as controls while gathering repeated evidence.

## Updating this page

1. Add the exact source fingerprint for each new version; a changed source is a
   new measured bot even if its folder name stays the same.
2. Benchmark the frozen candidate pool on the same 35 maps, against the same
   opponents, with both starting sides. Repeat games to characterize unseeded
   behavior.
3. Refresh ELOs and per-map profiles from the same frozen panel. Keep ratings
   labeled preliminary until the broader screen is met.
4. Before removing a bot, record its direct frontier replacement, per-map
   evidence, uncertainty result, date, and both source fingerprints.
5. Update the review date and link the frozen result contributions or report.

For experiment setup see [`docs/benchmarking.md`](docs/benchmarking.md), the
ledger schema in [`game_stats/README.md`](game_stats/README.md), the custom map
catalog in [`maps/new/EXPLAINER.md`](maps/new/EXPLAINER.md), and the line
histories under `docs/`.
