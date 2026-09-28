# tools/analysis/features — F1 local feature lab

Replay → features → report, for local panels and (unchanged) for the field corpus. Docs: `docs/analysis/FEATURES.md`
(definitions, units, validation), `docs/analysis/F1-status.md`, `docs/analysis/FEATURE_BACKLOG.md`.

| module | role |
|---|---|
| `frame.py` | decode a replay once into a cached frame (snapshots, pearls, events incl. sonar origin/end/hit kind) |
| `extract.py` | side-game features, per-round series, 5-round spatial samples, dragon and death tables |
| `registry.py` | name → family, unit, definition, source, validation level |
| `checks.py` | V0 bookkeeping identities |
| `phases.py` | rule markers, exact changepoints, pooled left-to-right HMM |
| `report.py` | quantiles by map × result, strength, stability, identity, flags, interactive HTML |
| `run_panel.py` | seeded round-robin panel runner (resumable, shardable) |
| `probe_check.py`, `probes/` | V1 probe bots with known feature values |
| `test_features.py`, `fixtures/` | tests on a committed replay |

```
python -m tools.analysis.features.run_panel --panel z1 --jobs 2 --unswbc ~/.venvs/bc122/bin/unswbc --no-logs
python -m tools.analysis.features extract 'build/zoo/z1/replays/*.replay' --index build/zoo/z1/index.jsonl --out build/zoo/z1/features --cache build/zoo/z1/frames --jobs 4
python -m tools.analysis.features.probe_check --unswbc ~/.venvs/bc122/bin/unswbc
python -m tools.analysis.features.report --run build/zoo/z1/features --index build/zoo/z1/index.jsonl --out build/zoo/z1/report --notes docs/analysis/f1-z1-notes.html
python -m tools.analysis.features registry > registry.md
```
Needs Python ≥ 3.10 with pandas, pyarrow, numpy (plotly for the report); unswbc 1.2.2 (Python ≥ 3.11) for panels.
