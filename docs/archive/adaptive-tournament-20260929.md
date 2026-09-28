# Archived adaptive tournament — 29 September 2026

Stopped at user request (2026-09-28T19:13:43.023317+00:00). No collector or ratings refresher remains active.

- Final roster: 340 bots, 33 weighted maps. Roster inclusion was for measurement, not frontier promotion.
- Campaign: `experiment_data/benchmark_20260928163631859920`. Sources, replays, logs and earlier campaigns remain in place.
- Archive metadata: `experiment_data/benchmark-archived-latest.json`.
- Preserved shared-ledger snapshot: `experiment_data/benchmark_20260928163631859920/archive/game_stats.parquet` (141,033 records). The original central ledger and contribution Parquets remain available to other experiments.
- Final campaign failed on a frozen-map path error before recording any games; details remain in `runner.log` and `progress.json`.
- Last successful ratings and their stopped/error status are copied under the campaign's `archive/`; they are not final rankings of all 340 bots.

The active campaign pointer has been retired into the archive. Restarting requires an explicit new campaign; repair the frozen-map path handling before resuming collection.
