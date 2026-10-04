# Carthage 05 vs 04 — five-seed gen-panel addendum on unswbc 1.2.5

Completed 3 Oct 2026 on the XPS 8940 as the continuation of the queued `carthage-05-free-sprint` vs
`carthage-04-sprint123` comparison. Runtime was `unswbc==1.2.5`; the gen panel used 4 opponents, 31 maps, both seats,
and seeds 1–5: 1,240 paired fixtures per arm (2,480 games total). Every game returned successfully. Feature extraction
completed for 1,240/1,240 replays per arm with zero errors.

## Paired gen result

| Metric | 05 candidate | 04 parent | Paired change (central 90%) |
|---|---:|---:|---:|
| Expected score | 0.7008 | 0.6843 | +0.0165 [+0.0056, +0.0282] |
| Geometric economy (`econ~`) | 1.1055 | 1.1059 | −0.0004 [−0.0064, +0.0059] |
| Arithmetic economy | 1.3202 | 1.3243 | −0.0041 [−0.0095, +0.0014] |
| Pearls @50 / @100 / @150 / @250 | 1.348 / 1.317 / 1.314 / 1.302 | 1.349 / 1.318 / 1.313 / 1.317 | +0.000 / −0.002 / +0.000 / +0.000 |
| Units @100 | 1.809 | 1.810 | +0.000 [−0.019, +0.019] |
| Total @100 | 1.925 | 1.922 | +0.000 [−0.024, +0.027] |

The candidate's expected-score estimate improves by 1.65 percentage points, with a positive fifth-percentile bound of
0.56 pp. Economy is flat. Tier-2 rates rise modestly: wall +1.8%, self +1.2%, ally-body +6.0%, ally head-on +4.3%;
invalid moves remain zero and newborn deaths rise about 0.2%.

## Combined reading with the pool result

The same five-seed comparison's pool result is recorded in
`docs/findings/2026-10-03-carthage-05-vs-04-five-seed-pool.md`: expected-score change +0.19 pp [−1.94, +2.19],
so the pool-positive lower-bound condition is not met. Across both panels, the gen win noninferiority and economy
conditions in D-042's 1.2.3 adaptation screen are met, but the gen total@100 lower bound (−0.024) is below the
−0.020 material guard. The pool win and gen total@100 bounds therefore keep this comparison from clearing that
screen. D-042 was scoped to 1.2.3 adaptations; this is a fresh 1.2.5 remeasurement, and no 1.2.5-specific gate ruling
is recorded here. Treat it as a local paired-panel screen, not a promotion decision or field-strength estimate.

Intervals are the lane's paired fixture bootstrap over common (seed, map, opponent, seat) fixtures, reporting the 5th
and 95th percentiles.

## Reproduction and artifacts

- Parent gen run: `build/carthage/runs/carthage-04-sprint123/gen/`
- Candidate gen run: `build/carthage/runs/carthage-05-free-sprint/gen/`
- Combined paired score JSON: `build/carthage/results/carthage-05-vs-04-pool-gen-seeds1-5-1.2.5.json`

The automatic extractor's Python 3.14 forkserver could not bind its socket in this sandbox. The same feature extractor
completed with the `fork` multiprocessing start method; all 1,240 replays per arm decoded without errors. Game runs
were not repeated for extraction.

## Ledger

L50 is touched; retain weight 0.8. The gen panel supports the win effect on this panel, while the pool interval spans
zero and the gen total@100 guard misses by 0.4 pp. Keep the 05−00 bundle and 05−04 increment distinct.
