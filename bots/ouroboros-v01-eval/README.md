# ouroboros-v01-eval

First Ouroboros (Claude) bot: one evaluation function over candidate actions,
roles as weight slices, parent->child sonar hand-off. Design:
`docs/ouroboros-design.md`. Tooling: `tools/ouroboros/`.

## Benchmark (non-sandbox, all 14 maps, both sides)

`ouro.py run ouroboros-v01-eval --pool <7 bench bots> --maps full`

| opponent | W-L |
| --- | --- |
| hydra-v06-echo | 26-2 |
| fry-v03-portal-hunters | 26-2 |
| kraken-v03-judge-safe | 23-5 |
| hunter-v03-team-growth | 22-6 |
| hunter-v04-team-state-sonar | 21-7 |
| fry-v12-stateful-size-aware-hunters | 21-7 |
| fry-v14-stateful-size-aware-3 | 19-9 |
| **total** | **158-38 (0.806)** |

Weak spots: trauma 2-12 (round-limit, pearl-scarce: our longest dragon is
short), big_empty round-limit length races, small maps (arena,
default_small) against the fry/hunter swarms.

Sandbox CPU (judge pricing) on default: p50 26M, p99 38M, max 50M points
per turn (limit 100M).

## What mattered getting here (48-match screen, 4 opponents, quick maps)

| change | score |
| --- | --- |
| first working version | 0.47 |
| flood fill no longer treats tiles next to other heads as walls; exits count them as half | |
| sprint cost `w_sprint` (sprints were burning 37% of pearls on arena) | |
| pearl ownership (`own_disc`: leave pearls to a clearly closer head) | |
| tunnel/doom checks (ally head-on jams in 1-wide corridors) + split only when the newborn has a way out | |
| combined | 0.83 |
