# gavroche-v41-cpu-profile

| Opponent | W | D | L | Errors |
|---|---:|---:|---:|---:|
| gavroche-v31-saturated-divecap | 3 | 0 | 1 | 0 |
| TOTAL | 3 | 0 | 1 | 0 |

Both side assignments; deterministic maps, not independent random samples.

| Map | Side | Opponent | Result | Rounds | Longest (us / them) | Splits | Deaths |
|---|---|---|---|---:|---|---:|---|
| big_empty | B | gavroche-v31-saturated-divecap | A | 500 | 39 / 44 | 215 | {"head-to-head": 180, "self": 15, "body": 1} |
| big_empty | A | gavroche-v31-saturated-divecap | A | 500 | 57 / 30 | 223 | {"head-to-head": 172, "body": 8, "self": 23} |
| trauma | B | gavroche-v31-saturated-divecap | B | 500 | 13 / 12 | 14 | {"wall": 2, "self": 10, "body": 2, "head-to-head": 1} |
| trauma | A | gavroche-v31-saturated-divecap | A | 500 | 23 / 6 | 181 | {"wall": 79, "body": 30, "self": 62, "head-to-head": 7} |

## Health

| Map | Side | Peak CPU points (rounded) | Invalid actions | Replay analysis error |
|---|---|---:|---:|---|
| big_empty | B | 94700000 | 0 |  |
| big_empty | A | 89000000 | 0 |  |
| trauma | B | 74900000 | 0 |  |
| trauma | A | 85600000 | 0 |  |
