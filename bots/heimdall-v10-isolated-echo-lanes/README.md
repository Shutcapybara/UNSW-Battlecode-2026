# Heimdall v10 — isolated echo lanes

V10 combines Fenrir v18's child-site handoff and Bifröst's portal memory with
v05's aggregate echo signal and an isolated directional scan. On scheduled
turns it emits one sonar ray, records that ray's origin and direction, and
applies a short-lived route cost to lanes where the next-turn echo reports an
enemy. It scans only when crown, prey, legacy handoff, and split-handoff
packets are not queued. Aggregate echoes are never treated as coordinates.

The 15-map champion panel completed with no game errors or runtime faults:

| Reference | Heimdall W–L |
|---|---:|
| Bifröst v01 | 20–10 |
| Fenrir v18 | 16–14 |
| Loki v01 | 19–11 |
| Skadi v02 | 17–13 |
| Skadi v13 | 19–11 |

Full results: [`experiment_data/heimdall-v10-isolated-echo-lanes_20260928073239050343`](../../experiment_data/heimdall-v10-isolated-echo-lanes_20260928073239050343/summary.md). The five-reference nine-map screen is in [`experiment_data/heimdall-v10-isolated-echo-lanes_20260928072233772956`](../../experiment_data/heimdall-v10-isolated-echo-lanes_20260928072233772956/summary.md). The family record and iteration notes are in [`docs/heimdall-family.md`](../../docs/heimdall-family.md).

One judge-sandbox Big Empty game completed 500 rounds without a runtime fault:
p99 49.6M CPU points, maximum 57.8M for Heimdall. This was a focused
single-game CPU check, not a full judge-sandbox panel.
