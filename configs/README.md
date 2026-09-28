# Comparison configurations

[`../comparison.toml`](../comparison.toml) is the default roster used by
`tools/compare_bot.py`. Older line-specific screens and comparisons are grouped
under `configs/<family>/` by authoring line. TOML paths resolve relative to the
configuration file that contains them.

`configs/porthos/reserve.toml.disabled` is intentionally unavailable because
its original custom map files are missing. Restore those maps before creating a
runnable replacement; do not point it at a different suite under the same name.
