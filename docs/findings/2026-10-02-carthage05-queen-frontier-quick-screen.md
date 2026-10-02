# Carthage 05 Queen-rules frontier quick screen (2 Oct 2026)

`carthage-05-free-sprint` played four pre-rules frontier references on four
maps, both starting sides, one `fixture_hash_v1` seed per opponent/map pair.
The 32-game native screen used `unswbc 1.2.5`, four concurrent workers, and
recorded no game errors, analysis errors, or runtime faults.

| Opponent | Wins | Draws | Losses |
|---|---:|---:|---:|
| `tyr-v12-devil-scout-tiebreak` | 8 | 0 | 0 |
| `fenrir-v20-crowded-resource-revalue` | 5 | 0 | 3 |
| `bifrost-v01-portal-memory` | 6 | 0 | 2 |
| `gavroche-v33-half-support` | 8 | 0 | 0 |
| **Total** | **27** | **0** | **5** |

This is evidence that Carthage 05 is competitive with the selected old-frontier
bots on these maps. It does not establish an overall ranking: the panel is
small, includes no full comparison against post-rules candidates, and is a
native run rather than judge CPU validation. The run used four workers; the
frontier notes require serial runs for promotion evidence because concurrent
low-level runs have not been reproducible. Treat this screen as exploratory.

The first, wider 120-fixture attempt was interrupted after 13 games. Its
separate Tyr-only contribution scored 11–1–1 across seven maps and is not pooled
with the 32-game result. The full report and replay artifacts remain in the
local, ignored `experiment_data/` directory. The reusable roster is
[`comparison-carthage05-queen-frontier-quick.toml`](../../comparison-carthage05-queen-frontier-quick.toml);
it uses one worker for follow-up runs. Shared outcome contributions are in
[`9c6d8215.parquet`](../../game_stats/runs/9c6d82151b4347e2b5fa4d5544e0bccf.parquet)
and [`f633df67.parquet`](../../game_stats/runs/f633df674e7f48759a27320da4a16057.parquet).

The team’s post-ruleset baseline result remains the stronger basis for keeping
Carthage 05 as the leading submitted adaptation: see the [Phase 2 summary](../PHASE2-SUMMARY-2026-10-02.md).
