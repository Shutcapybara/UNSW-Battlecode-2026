# Repository Guidelines

## Project Structure

`bots/` contains standalone bot snapshots; many are frozen experiment controls. `tools/` holds tournament, benchmarking, and analysis utilities. `tests/` contains Python behavior and tooling tests. `maps/` stores shared maps, while `configs/` stores comparison and validation rosters. `docs/` records workflows, experiment results, and artifact rules. Use `FRONTIER.md` as the canonical active-candidate registry.

## Build, Test, and Development

Build the selected C++ reference bots with:

```sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build
ctest --test-dir build --output-on-failure
```

CTest runs the registered subset; other Python tests are standalone, for example `python3 tests/test_von_neumann.py`. Run a bounded tournament with `python3 tools/benchmarking/tournament.py --bots <bot-a> <bot-b> --dry-run` before removing `--dry-run`. Use `uv run tools/compare_bot.py <bot-dir>` for a candidate comparison. Keep generated build and run output under `build/` or `/tmp`.

## Coding and Snapshot Conventions

Follow the surrounding style: four-space indentation in Python, and C++17 for the reference set. Python tests use `tests/test_*.py`; bot directories use descriptive family/version names such as `hunter-v23-supported-arrival-feed`. No repository-wide formatter or linter is configured. Treat measured bot snapshots as immutable: copy a bot to a new versioned directory for behavior changes, then update its family notes and relevant registry or comparison configuration.

## Testing Changes

Run the narrow relevant test first, then the corresponding CTest suite or full `ctest` after broader C++ changes. For strategy changes, record the bot names, map or opponent pool, and benchmark output path so results can be reproduced. Tests and local runs do not imply promotion; consult `FRONTIER.md` and family documentation.

## Commits and Pull Requests

Recent commits use short imperative summaries (for example, `Add file-queued local statistics protocol`) without a required prefix. Keep each commit focused. A pull request should explain the change and affected bot/tool versions, list verification commands and benchmark selections/results where relevant, and update workflow or family documentation when the experiment or status record changes. Do not add replay payloads, credentials, or generated build/ledger state; follow `docs/artifact-policy.md`.
