# Repository artifact policy

Keep source, reusable configuration, and the small shared result contributions
in Git. Keep machine-specific output and large generated artifacts out of new
commits by default.

| Path | Policy |
|---|---|
| `bots/`, `configs/`, `maps/`, `docs/`, source and tools | Tracked project inputs |
| `game_stats/runs/*.parquet` | Shared contributions; commit new run files with the bot or experiment they document |
| `game_stats.parquet`, `game_stats/sources/`, `game_stats/.write.lock` | Generated/local ledger state; do not commit |
| `build/`, `.unswbc-build/`, `Testing/` | Local build output and reports; do not commit |
| `experiment_data/`, `public_replays/`, `replays/`, `*.replay`, compressed/decoded replay payloads | Local runs, frozen copies, and downloaded/generated replay output; do not add new artifacts by default |

There are already historical files under `experiment_data/` tracked in Git.
They remain available as provenance; the ignore rule only prevents additional
local output from being added accidentally. A path being ignored does not remove
an already tracked file.

The shared maps used by `bots/tournament.py` are every checked-in `.map` file
under `maps/`, including the custom bundle in `maps/new/`. Nested paths are
selected relative to `maps/`. Family-specific reserve maps under `configs/`
remain separate validation fixtures.

Replay ZIPs are not tracked by default. The M376704 and M376714 archives were
removed from Git and moved to ignored `experiment_data/replays/` for local
analysis; their outcomes and summary metrics remain in the Bifröst README. Two
older tracked replay ZIPs were also removed from the September 28 tree
synchronization; this does not rewrite historical commits. Interrupted ledger
`.tmp` files and credentials must not be staged. Small
`game_stats/imports/*.json` receipts describe completed imports; they contain
neither replays nor source code.
