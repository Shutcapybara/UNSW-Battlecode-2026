# Bot snapshots

Each directory under `bots/` is a standalone bot version. Most directories are
frozen experiment snapshots kept as exact controls; use
[`FRONTIER.md`](../FRONTIER.md) to find the current frontier and
[`docs/`](../docs/) for family results and lineage notes.

Odin is the current experimental cross-line synthesis; see
[its family record](../docs/odin.md) and
[version 01](odin-v01-synthesis/README.md). It is not yet a frontier candidate.

Benchmarking and analysis tools live outside the bot roster:

- [`tools/benchmarking/`](../tools/benchmarking/) contains the shared tournament
  runner.
- [`tools/kraken/`](../tools/kraken/) and [`tools/hunter/`](../tools/hunter/)
  contain family-specific analysis tools.
- [`docs/bot-workflow.md`](../docs/bot-workflow.md) explains the normal
  comparison workflow.

The old Fry child-count comparison is retained as a historical reproduction in
[`docs/experiments/fry-child-count.md`](../docs/experiments/fry-child-count.md).
