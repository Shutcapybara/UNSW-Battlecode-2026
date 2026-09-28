# FRONTIER — bot pool and current status

**Reviewed 2026-09-29.** This is the canonical page for candidate status,
estimated ELOs, the default comparison roster, and contest deployment notes.

> **TODO — complete the all-map frontier panel.** The 16-bot ratings below use
> only Colosseum, arena, and autarky. The shared map bundle has **35 maps**: 15
> established maps and 20 custom maps in `maps/new/`. The six family-specific
> reserve maps under `configs/` are separate holdouts, not part of this shared
> bundle. A balanced 16-bot all-pairs panel requires 8,400 distinct directional
> games. So far, 720 fixtures cover all bots on three maps; a separate 70-game
> Fenrir V20 vs Hunter V20 sweep covers all 35 maps. It adds 64 fixtures on the
> 32 maps outside the pilot; its other six fixtures overlap the pilot's two
> sides on Colosseum, arena, and autarky, and one repeated outcome differed. If
> using one result per fixture, keep the pilot results for those six and
> schedule the remaining 7,616 fixtures. The all-map ELOs
> and frontier remain to be calculated; do not treat the three-map results as
> final.

| Bot snapshot | 3-map pilot ELO | All-map evidence | Pilot status | Fixtures / opponents / maps | Source fingerprint |
|---|---:|---|---|---:|---|
| `fenrir-v20-crowded-resource-revalue` | ~1,750 | 50–20 vs Hunter V20 | 3-map point-frontier candidate | 90 / 15 / 3; plus 70 / 1 / 35 | `dc7717689882` |
| `gavroche-v33-half-support` | ~1,650 | Pending full panel | Point-dominated; uncertainty remains | 90 / 15 / 3 | `57d123043c7f` |
| `bifrost-v01-portal-memory` | ~1,640 | Pending full panel | Point-dominated; uncertainty remains | 90 / 15 / 3 | `037872088e6f` |
| `gavroche-v66-supported-safe` | ~1,630 | Pending full panel | Point-dominated; uncertainty remains | 90 / 15 / 3 | `a5c8dc0f8db5` |
| `skadi-v13-clear-exit-only` | ~1,600 | Pending full panel | Point-dominated; uncertainty remains | 90 / 15 / 3 | `34d716a3492d` |
| `serre-v01-foundation` | ~1,560 | Pending full panel | Point-dominated; uncertainty remains | 90 / 15 / 3 | `ae4bcc23254c` |
| `hunter-v23-supported-arrival-feed` | ~1,560 | Pending full panel | 3-map point-frontier candidate | 90 / 15 / 3 | `b10300e824d4` |
| `sinbad-v07-divecap` | ~1,560 | Pending full panel | Point-dominated; uncertainty remains | 90 / 15 / 3 | `c759a5c8a8ba` |
| `von_neumann-x04-support` | ~1,510 | Pending full panel | 3-map point-frontier candidate | 90 / 15 / 3 | `3772d5a35503` |
| `hunter-v20-portal-scouts` | ~1,480 | 20–50 vs Fenrir V20 | 3-map point-frontier candidate | 90 / 15 / 3; plus 70 / 1 / 35 | `f844fa3ae595` |
| `monte_christo-x12-remote-density` | ~1,480 | Pending full panel | Point-dominated; uncertainty remains | 90 / 15 / 3 | `5589c30d0525` |
| `tew-v12-mid-support` | ~1,470 | Pending full panel | Point-dominated; uncertainty remains | 90 / 15 / 3 | `8bff0f54828f` |
| `fry-v14-stateful-size-aware-3` | ~1,360 | Pending full panel | Dominated on pilot; do not retire | 90 / 15 / 3 | `962541eb674d` |
| `hunter-v14-cpp-hybrid-route-spacing` | ~1,330 | Pending full panel | Dominated on pilot; do not retire | 90 / 15 / 3 | `6ba4e603ad19` |
| `ouroboros-v10-beacon` | ~1,260 | Pending full panel | Dominated on pilot; do not retire | 90 / 15 / 3 | `a9eafbaffc51` |
| `kraken-v04-eval` | ~1,160 | Pending full panel | Dominated on pilot; do not retire | 90 / 15 / 3 | `7d23d380f291` |

The pilot ELO estimates are centered at 1,500 across these 16 source
fingerprints; they are not all-map ratings or official contest ratings. The
all-map evidence column reports only the completed direct duel; it is not a
score against the full panel.

## All-map head-to-head completed

Fenrir V20 played Hunter V20 twice on every map in the 35-map bundle, once from
each starting side: **70 games, 50–20 for Fenrir, with no draws or runner
errors**. Fenrir swept both games on 18 maps, Hunter swept 3, and the sides split
the remaining 14. This is one head-to-head across the map set, not a 16-bot
frontier or a complete ELO refit.

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
bot had 90 games against 15 exact opponents on 3 maps; these estimates should be
refreshed from a frozen all-map panel before promoting or retiring candidates.

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
Fry V14, Hunter V14, Ouroboros V10, and Kraken V04 as dominated on those maps;
keep them as controls until the full pool has been measured.

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
