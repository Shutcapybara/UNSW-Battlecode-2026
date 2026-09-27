# gavroche-v33-half-support

| Opponent | W | D | L | Errors |
|---|---:|---:|---:|---:|
| gavroche-v31-saturated-divecap | 2 | 0 | 2 | 0 |
| TOTAL | 2 | 0 | 2 | 0 |

Both side assignments; deterministic maps, not independent random samples.

| Map | Side | Opponent | Result | Rounds | Longest (us / them) | Splits | Deaths |
|---|---|---|---|---:|---|---:|---|
| big_empty | B | gavroche-v31-saturated-divecap | B | 500 | 46 / 46 | 188 | {"head-to-head": 145, "self": 25, "body": 2} |
| big_empty | A | gavroche-v31-saturated-divecap | B | 500 | 52 / 61 | 187 | {"head-to-head": 134, "body": 5, "self": 36} |
| trauma | B | gavroche-v31-saturated-divecap | A | 500 | 19 / 20 | 173 | {"wall": 74, "self": 55, "head-to-head": 24, "body": 18} |
| trauma | A | gavroche-v31-saturated-divecap | A | 500 | 17 / 9 | 173 | {"wall": 78, "body": 26, "head-to-head": 29, "self": 39} |

## Health

| Map | Side | Peak CPU points (rounded) | Invalid actions | Replay analysis error |
|---|---|---:|---:|---|
| big_empty | B | 99600000 | 0 |  |
| big_empty | A | 91900000 | 0 |  |
| trauma | B | 85600000 | 0 |  |
| trauma | A | 95500000 | 0 |  |
