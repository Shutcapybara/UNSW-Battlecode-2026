# tools/analysis — heavy one-off analyses (handoff A1, 28 Sep 2026)

Read-only over every input. The recurring subset runs inside the hub every ten minutes (`tools/hub/analysis_a1.py`,
called from `tools/hub/analysis.run`, tests in `tests/test_hub_analysis.py`); the scripts here reproduce the numbers in
`docs/analysis/ATLAS.md` and `docs/findings/2026-09-28-analysis-claude-Q*.md` from the raw files.

| Script | Input | Output | Findings |
|---|---|---|---|
| `live_record.py` | `LIVE/state/state.json` (selected keys only) | one row per game with stage curves flattened (`--out x.parquet`), `--summary` | all |
| `a1_report.py` | state.json (+ `LIVE/state/ladder.json`) | Markdown: inventory, Q1 loss anatomy, Q2 exact pairs, Q3 layout rule + batch parity table, Q5 opponent fingerprints, Q6 runtime, Q7 sonar, Q9 ranked series | Q1 Q2 Q3 Q5 Q6 Q7 Q9 |
| `probe_turns.py` | one judge-sandbox probe log | CSV of dragon-turns (round, bot, team, lines, SONAR lines, bytes, points, first command, living dragons) | Q6 Q7 |
| `scan_runs.py` | `experiment_data/*/` comparison runs | CSV of per-round series at r100/250/400/499 for the named bots (run on the Mac) | Q4 |
| `transfer.py` | `game_stats.parquet`, state.json, the series CSV | absolute calibration, paired common cells, toolkit strata, trajectory matching | Q4 |
| `ratings_sanity.py` | `experiment_data/bot-ratings/latest.json` (+ state.json) | evidence tiers, shrunk scores, live join, Spearman | Q10 |
| `replay_drive_live.py` | `LIVE/state/decoded/*.replay`, `bots/<local bot>` | replay-drive agreement per live game within a time budget; `--summary` writes `build/a1_replay_drive_live.csv` (run on the Mac / VM; needs `pycapnp`) | Q8 |

Typical run (container or Mac venv with pandas + pyarrow + scipy):

```
python -m tools.analysis.live_record --state LIVE/state/state.json --out build/live_games.parquet --summary
python -m tools.analysis.a1_report --state LIVE/state/state.json --ladder LIVE/state/ladder.json --out build/a1_report.md
python -m tools.analysis.scan_runs fenrir-v18-arrival-ready-beds,bifrost-v01-portal-memory,ein-dog-v02-momentum,ein-dog-x08-momentum-scoped,yuna-v02-core,tidus-t02-spread-only,yuna-v03-core,yuna-x10-core-nocong > build/a1_local_series.csv
python -m tools.analysis.transfer --state LIVE/state/state.json --ledger game_stats.parquet --series build/a1_local_series.csv
python -m tools.analysis.ratings_sanity --ratings experiment_data/bot-ratings/latest.json --state LIVE/state/state.json
python -m tools.analysis.replay_drive_live 8540 bots/bifrost-v01-portal-memory 160 ; python -m tools.analysis.replay_drive_live --summary
```

Conventions: units of independence are named in every table; stage fields carry the terminal state forward after
elimination (no survivor-only medians); missing fields stay missing; opponents are stratified by submission id;
A-side only. Build artefacts from the 28 Sep pass are under `build/a1_*` (git-ignored).
