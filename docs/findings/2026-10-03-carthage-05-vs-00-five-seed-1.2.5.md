# Carthage 05 vs 00 — five-seed bundle comparison on unswbc 1.2.5

Completed 3 October 2026 on the director's XPS 8940. This remeasures the
registered `carthage-05-free-sprint` bundle against `carthage-00-base` under
`unswbc==1.2.5`: corrected sprint pricing plus free on-route multi-step moves.
The run used seeds 1–5, both seats, 8 pool opponents / 10 live maps, and 4 gen
opponents / 31 maps. The pool panel has 800 paired fixtures per arm; gen has
1,240 paired fixtures per arm. All 2,040 baseline replays and all matching
candidate features were present. Game runs and extraction had zero errors.

## Paired results

Central 90% intervals are the lane bootstrap over common
(seed, map, opponent, seat) fixtures, reporting the 5th and 95th percentiles.

| Panel / metric | 05 candidate | 00 parent | Paired change [90% interval] |
|---|---:|---:|---:|
| Pool expected score | 0.8600 | 0.8338 | +0.0262 [+0.0062, +0.0450] |
| Pool geometric economy (`econ~`) | 1.1353 | 1.1348 | +0.0005 [−0.0013, +0.0037] |
| Pool arithmetic economy | 1.3118 | 1.3068 | +0.0050 [+0.0029, +0.0072] |
| Pool units @100 | 1.556 | 1.556 | +0.000 [0.000, 0.000] |
| Pool total @100 | 1.472 | 1.472 | +0.000 [−0.0032, +0.0041] |
| Gen expected score | 0.7008 | 0.6883 | +0.0125 [+0.0020, +0.0230] |
| Gen geometric economy (`econ~`) | 1.1055 | 1.1044 | +0.0012 [−0.0048, +0.0080] |
| Gen arithmetic economy | 1.3202 | 1.3269 | −0.0067 [−0.0128, −0.0009] |
| Gen units @100 | 1.809 | 1.810 | +0.000 [−0.019, +0.019] |
| Gen total @100 | 1.925 | 1.921 | +0.000 [−0.024, +0.027] |

The win increase is positive on both panels. The pool's arithmetic economy
improves, while gen arithmetic economy declines modestly; both `econ~`
intervals include zero. The gen units lower bound (−0.019) narrowly clears
−0.020, while the gen total lower bound (−0.024) misses −0.020. Tier-2 death
rates remain below +10%: pool wall/self/ally-body/ally-head-on rates change
about +1.7/+1.8/+5.2/+5.5%; gen changes about +2.1/+0.3/+6.4/+5.4%. Invalid
moves remain zero.

## Reading and scope

The scorer's default Carthage lane gate prints `REJECT` because pool `econ~`
has lower bound −0.001, just below its strict >0 threshold. Under D-042's
1.2.3 adaptation screen, the win limbs and arithmetic-economy bounds pass, but
the gen total@100 lower bound misses the −0.020 material guard. D-042 was
scoped to 1.2.3 adaptations; this 1.2.5 rerun is a fresh-runtime paired screen,
not a new promotion ruling. Keep it distinct from the five-seed 05−04
incremental screen and do not infer field strength from these local panels.

## Reproduction and artifacts

The 00 baseline was run with:

```sh
CARTHAGE_NICE=10 UNSWBC="$PWD/.venv/bin/unswbc" \
  ./.venv/bin/python tools/carthage/lane.py run carthage-00-base \
  --panel both --seeds 1,2,3,4,5 --jobs 8
```

The sandbox's Python 3.14 forkserver could not bind its socket for automatic
extraction. Both panels were instead extracted with Python's `fork` start
method; 800/800 pool and 1,240/1,240 gen replays decoded without errors.

- Baseline runs: `build/carthage/runs/carthage-00-base/{pool,gen}/`
- Paired score: `build/carthage/results/carthage-05-vs-00-pool-gen-seeds1-5-1.2.5.json`
- Candidate runs/features: `build/carthage/runs/carthage-05-free-sprint/{pool,gen}/`

Outputs remain local under ignored `build/` state.
