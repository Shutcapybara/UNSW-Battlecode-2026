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

The bundled maps used by `bots/tournament.py` are the `.map` files directly
under `maps/`. Files under `maps/new/` are a separate dataset and are not
included by that runner’s default discovery.

The two formerly tracked downloaded ZIPs under `replays/` were removed from the
current tree during the September 28 synchronization and retained on the local
machine. This does not rewrite historical commits. Interrupted ledger `.tmp`
files and credentials must not be staged. Small `game_stats/imports/*.json`
receipts describe completed imports; they contain neither replays nor source code.
