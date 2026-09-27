# gavroche-v54-sparse-room

| Opponent | W | D | L | Errors |
|---|---:|---:|---:|---:|
| gavroche-v31-saturated-divecap | 2 | 0 | 2 | 0 |
| TOTAL | 2 | 0 | 2 | 0 |

Both side assignments; deterministic maps, not independent random samples.

| Map | Side | Opponent | Result | Rounds | Longest (us / them) | Splits | Deaths |
|---|---|---|---|---:|---|---:|---|
| big_empty | B | gavroche-v31-saturated-divecap | A | 500 | 40 / 43 | 220 | {"head-to-head": 170, "body": 5, "self": 23} |
| big_empty | A | gavroche-v31-saturated-divecap | B | 500 | 24 / 42 | 214 | {"head-to-head": 165, "self": 17, "body": 7} |
| trauma | B | gavroche-v31-saturated-divecap | B | 500 | 20 / 9 | 278 | {"wall": 146, "head-to-head": 31, "self": 65, "body": 32} |
| trauma | A | gavroche-v31-saturated-divecap | A | 500 | 20 / 7 | 316 | {"wall": 152, "head-to-head": 30, "body": 38, "self": 87} |

## Health

| Map | Side | Peak CPU points (rounded) | Invalid actions | Replay analysis error |
|---|---|---:|---:|---|
| big_empty | B | 61300000 | 0 |  |
| big_empty | A | 63700000 | 0 |  |
| trauma | B | 52800000 | 0 |  |
| trauma | A | 60700000 | 0 |  |
