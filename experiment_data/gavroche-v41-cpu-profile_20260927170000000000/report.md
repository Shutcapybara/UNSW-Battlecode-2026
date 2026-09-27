# gavroche-v41-cpu-profile

| Opponent | W | D | L | Errors |
|---|---:|---:|---:|---:|
| gavroche-v31-saturated-divecap | 0 | 0 | 4 | 0 |
| TOTAL | 0 | 0 | 4 | 0 |

Both side assignments; deterministic maps, not independent random samples.

| Map | Side | Opponent | Result | Rounds | Longest (us / them) | Splits | Deaths |
|---|---|---|---|---:|---|---:|---|
| big_empty | B | gavroche-v31-saturated-divecap | A | 351 | 0 / 11 | 198 | {"head-to-head": 133, "self": 2, "body": 2, "invalid": 64} |
| big_empty | A | gavroche-v31-saturated-divecap | B | 351 | 0 / 9 | 196 | {"head-to-head": 131, "self": 2, "body": 2, "invalid": 64} |
| trauma | B | gavroche-v31-saturated-divecap | A | 351 | 0 / 4 | 6 | {"wall": 3, "body": 1, "head-to-head": 1, "invalid": 3} |
| trauma | A | gavroche-v31-saturated-divecap | B | 351 | 0 / 3 | 17 | {"wall": 7, "self": 2, "body": 1, "head-to-head": 3, "invalid": 6} |

## Health

| Map | Side | Peak CPU points (rounded) | Invalid actions | Replay analysis error |
|---|---|---:|---:|---|
| big_empty | B | 63500000 | 64 |  |
| big_empty | A | 67400000 | 64 |  |
| trauma | B | 61600000 | 3 |  |
| trauma | A | 74700000 | 6 |  |
