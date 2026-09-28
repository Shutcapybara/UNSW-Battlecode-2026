# ACTIVE — repository comparison roster and deployment record

**Reviewed 2026-09-28.** This file records the checked-in default comparison
roster and what the repository can establish about deployment. Earlier cycle
notes are preserved in [cycle 00](cycles/cycle-00.md).

## Deployed

The exact version currently deployed to the contest is **not recorded in this
checkout**. Older deployment claims in [`HANDOFF.md`](HANDOFF.md) and the
archived cycle note are historical and have not been verified for the current
submission.

## Default comparison roster

[`comparison.toml`](../comparison.toml) is the actual default roster consumed by
`tools/compare_bot.py`. It contains five reference opponents and uses both
starting sides across the maps directory. This is a local experiment default;
it does not by itself identify the deployed bot or certify a champion.

| Bot | Line |
|---|---|
| `ouroboros-v10-beacon` | Ouroboros |
| `hunter-v14-cpp-hybrid-route-spacing` | Hunter |
| `hunter-v20-portal-scouts` | Hunter |
| `fry-v14-stateful-size-aware-3` | Fry |
| `kraken-v04-eval` | Kraken |

Copy `comparison.toml` to create a focused roster. For tournament round-robin
schedules, use [`bots/tournament.py`](../bots/tournament.py) with explicit bot
and map selections; its default discovery includes every bot snapshot.

## Naming note

Rory Peterson's later snapshots formerly named `bifrost-*` are now the
[`Fenrir` line](fenrir-family.md). Zach's original `bifrost-*` snapshots and
root history remain the Bifröst line described in
[`bifrost-family.md`](bifrost-family.md).
