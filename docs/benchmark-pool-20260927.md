# Comparison-pool decision — 27 September 2026

Use **24 primary opponents** for routine comparisons, down from 286 names. The running collector, its frozen manifest, the rating worker and the shared ledger were not changed. The central `benchmark.toml` and `comparison.toml` now apply this decision to future runs; previous defaults are archived in `benchmark-all-20260927.toml` and `comparison-before-curation-20260927.toml`. All 24 are the new reference panel. `docs/benchmark-pool-status.json` records every roster decision and source identity for sharing.

Snapshot: 89,096 ledger games; 78,455 matching named fixtures; 76,767 distinct directional fixtures after exact-source alias pooling; 272 source versions. 222 meet broad-evidence requirements.

## Decision

| Status | Names |
|---|---:|
| deprecated_weak | 65 |
| reserve | 77 |
| deprecated_dominated | 51 |
| duplicate_alias | 14 |
| primary | 24 |
| runtime_hold | 11 |
| needs_evidence | 39 |
| deprecated_redundant | 5 |

Deprecated means removed from routine comparisons, not deleted or excluded from historical analysis. Reserve bots remain available for targeted regression tests; needs-evidence bots remain eligible for screening. Neither category is labelled weak. Runtime holds inherit prior timeouts involving the named bot; they are not proof of a defective bot.

## Primary pool

| Bot | Distinct fixtures | Opponents / lineages | Maps with ≥3 paired opponents | Selection reason |
|---|---:|---:|---:|---|
| serre-v01-foundation | 584 | 127 / 19 | 13 | broad overall leader; map leader: big_empty; map leader: queen_of_spades; map leader: schooltime; map leader: stronghold |
| sinbad-v07-divecap | 454 | 144 / 22 | 13 | broad overall leader; map leader: Colosseum |
| von_neumann-x03-balance | 440 | 140 / 22 | 13 | broad overall leader |
| von_neumann-x07-quiet | 492 | 126 / 22 | 13 | broad overall leader |
| von_neumann-x04-support | 444 | 147 / 23 | 13 | broad overall leader |
| tew-v12-mid-support | 3690 | 213 / 21 | 13 | map leader: arena |
| fry-v13-stateful-size-aware-2 | 1060 | 124 / 19 | 13 | map leader: autarky |
| avery-v09-frontier-bfs | 426 | 125 / 21 | 13 | map leader: default |
| valjean-v01-portal-memory | 848 | 150 / 21 | 13 | map leader: default_small |
| monte_christo-x12-remote-density | 706 | 146 / 23 | 13 | map leader: devil; map leader: trophy |
| hydra-v01-core | 288 | 79 / 22 | 13 | map leader: dilemma |
| porthos-x04-policy | 759 | 140 / 21 | 13 | map leader: trauma |
| godel-x02-pacifist | 298 | 133 / 22 | 13 | strong and distinct strength-adjusted profile |
| godel-x14-tb25-ps2-05 | 402 | 112 / 19 | 13 | strong and distinct strength-adjusted profile |
| avery-v08-crown-race | 582 | 117 / 22 | 13 | strong and distinct strength-adjusted profile |
| avery-v11-maze-sweep | 466 | 125 / 22 | 13 | strong and distinct strength-adjusted profile |
| godel-x19-ps1-090 | 332 | 141 / 22 | 13 | strong and distinct strength-adjusted profile |
| sinbad-v03-hunt | 850 | 111 / 19 | 13 | strong and distinct strength-adjusted profile |
| tew-v09-low-gate | 566 | 113 / 20 | 13 | strong and distinct strength-adjusted profile |
| monte_christo-v03-logistic-risk | 424 | 125 / 23 | 13 | strong and distinct strength-adjusted profile |
| godel-x24-gm2 | 334 | 138 / 21 | 13 | strong and distinct strength-adjusted profile |
| vn-x01-margin-2 | 394 | 140 / 22 | 13 | strong and distinct strength-adjusted profile |
| vn-x01-preymin-6 | 394 | 138 / 22 | 13 | strong and distinct strength-adjusted profile |
| godel-x03-berserk | 298 | 129 / 21 | 13 | strong and distinct strength-adjusted profile |

## Method and limits

- Broad evidence requires ≥200 distinct directional fixtures, ≥15 distinct source opponents, ≥6 opponent lineages, ≥10 maps, and ≥10 maps with at least three fully side-paired opponents. This is an executive coverage rule, not a formal confidence guarantee.
- Pool exact effective packaged-source identities, even across different names. Repeated directional fixtures contribute their mean once; games, bot revisions and runtime identities remain intact in the ledger.
- Fit a regularized paired-comparison model with bot strength, bot-by-map effects and starting-side effects. Each unordered lineage-pair/map block receives equal total fitting weight. Lineages are a coarse proxy: shared ancestry across names can remain correlated.
- General-strength estimates include average map affinity. For residual profiles, fit five folds holding out whole opponent pairs (all maps and both sides); subtract expected outcomes from general strength and initiative, retaining map preferences and matchup differences.
- Exact common-opponent/map residual correlations take precedence when ≥80 shared paired cells span ≥6 lineages and ≥10 maps, with correlation ≥0.85 and lower cluster-sensitivity bound ≥0.65. Also average residuals within opponent-lineage/map cells; correlate these with equal lineage weight and capped cell-support weights. Require ≥50 shared cells, ≥6 lineages and ≥10 maps. The latter pools different opponents within a lineage: it is approximate strategic similarity, not a causal or code-level classification.
- Strength sensitivity uses 40 lineage-cluster reweightings; similarity uses 200 lineage-cluster reweightings. These ranges reflect sensitivity to opponent mix, not calibrated confidence intervals. Anchor choice, regularization, lineage boundaries and adaptive sampling remain limitations.
- Anchor panel: strongest broadly measured source per lineage, weighted equally across lineages and maps. These scores are not comparable to the live six-reference percentages. Sparse bots can have extreme fitted scores and are excluded from primary selection regardless.
- Seed the primary pool with the five broad overall leaders and each map leader. Fill to 24 using strength plus residual diversity, avoiding correlations ≥0.85 with lower sensitivity bound ≥0.65. This is a loose empirical frontier: it deliberately retains alternatives and map specialists rather than claiming exact mathematical Pareto optimality.
- Weak retirement requires broad evidence, upper strength sensitivity bound <40%, and no modeled map score >60%. Observed dominance requires shared fixtures spanning ≥6 lineages and ≥10 maps: mean advantage lower sensitivity bound >2pp, with no shared map more than 10pp worse. It is conditional on observed coverage, not proof against every possible opponent.
- Redundancy retirement requires correlation ≥0.85, lower sensitivity bound ≥0.65, a primary representative within 2pp of strength or better, and no modeled map advantage >10pp. Conservative reserves retain cases that do not satisfy these conditions.

## Visuals

[Map profiles](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/experiment_data/curation-20260927/map-profiles.png) · [Strength-adjusted correlation matrix](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/experiment_data/curation-20260927/residual-correlations.png)

The matrix shows the coarser lineage/map correlations; exact shared-opponent comparisons also inform deprecation when sufficiently supported.

## Reproduction and artifacts

All analysis artifacts are in `experiment_data/curation-20260927/`: frozen `games.parquet`, `manifest.json`, aliases, `analysis.json` (pair evidence), `profiles.npz`, `family-profiles.npz`, `decisions.json` (every name and reason), `decisions.md`, and `benchmark-curated.toml`. The working bots may have changed; the TOML points to the measured frozen sources. Those local snapshots must be copied with the TOML when sharing, or source fingerprints verified against a teammate’s checkout.

```sh
.venv/bin/python tools/curate_benchmarks.py --output experiment_data/curation-20260927
.venv/bin/python tools/curate_benchmark_profiles.py --output experiment_data/curation-20260927
.venv/bin/python tools/select_benchmark_pool.py --output experiment_data/curation-20260927
.venv/bin/python experiment_data/curation-20260927/plot.py
```

Only add `--apply-default` to the `select_benchmark_pool.py` command when intentionally updating the future default roster. No command here restarts or changes the live campaign. The next actual campaign still requires the normal explicit plan/run step.

## Collector health discovered during verification

The original 286-bot collector had already failed at 2026-09-26 22:47 UTC with a readonly SQLite error. The saved database passed its integrity and write-lock checks. The same campaign and command were resumed, and subsequent games completed successfully. Its roster, scheduling code and campaign pointer were unchanged; the 24-opponent defaults have not been applied to that live campaign.
