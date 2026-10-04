# Carthage 05 vs 04 — five-seed pool comparison on unswbc 1.2.5

Completed 3 Oct 2026 on the XPS 8940. This closes the queued five-seed pool comparison for `carthage-05-free-sprint`
against its explicit parent `carthage-04-sprint123`. Runtime pinned to `unswbc==1.2.5`. The panel used 8 zoo opponents,
10 live maps, both seats and seeds 1–5: 800 paired fixtures per arm (1,600 games total). All fixtures returned
successfully; feature extraction reports 800/800 replays for each arm.

## Paired pool result

| Metric | 05 candidate | 04 parent | Paired change (central 90%) |
|---|---:|---:|---:|
| Expected score | 0.8600 | 0.8581 | +0.0019 [−0.0194, +0.0219] |
| Geometric economy (`econ~`) | 1.1353 | 1.1337 | +0.0015 [0.0000, +0.0040] |
| Arithmetic economy | 1.3118 | 1.3058 | +0.0060 [+0.0038, +0.0082] |
| Pearls @100 | 1.146 | 1.146 | +0.000 [0.000, +0.0034] |
| Units @100 | 1.556 | 1.556 | +0.000 [0.000, 0.000] |
| Total @100 | 1.472 | 1.473 | +0.000 [−0.0041, +0.0035] |

The expected-score point estimate is +0.19 percentage points; its fifth-percentile bound is −1.94 pp, so this sample
does not establish a positive pool win effect. Fixture outcomes improved in 51 pairs, worsened in 49, and tied in 700.
Material at round 100 is effectively flat. Tier-2 health changes are small: wall deaths +1.7%, self deaths +1.8%,
ally-body deaths +5.8%, ally head-on deaths +4.7%; invalid moves stay at zero and newborn deaths rise about 0.3%.

## Reading and scope

The pool-positive limb of D-042's win-led screen (pool win lower bound > 0) is not met on this 1.2.5 remeasurement.
D-042 specified that screen for predeclared 1.2.3 adaptations; this is a fresh 1.2.5 run, and no separate 1.2.5 gate
ruling is recorded here. It is therefore a pool-only screen, not a full promotion decision. The gen panel was not run.
This 05−04 incremental comparison does not replace the distinct 05−00 bundle comparison.

Intervals are the lane's paired fixture bootstrap, resampling the common (seed, map, opponent, seat) fixtures and
reporting the 5th and 95th percentiles. Treat them as a local panel screen, not a field-strength estimate.

## Reproduction and artifacts

Run and extraction directories (800 rows each):

- `build/carthage/runs/carthage-04-sprint123/pool/`
- `build/carthage/runs/carthage-05-free-sprint/pool/`

Paired score JSON: `build/carthage/results/carthage-05-vs-04-pool-seeds1-5-1.2.5.json`.
The outputs are local build artifacts and are not committed.

## Ledger

L50 is touched; retain weight 0.8. The five-seed incremental pool result is near zero with an interval spanning zero,
and the gen result is absent, so this is inconclusive evidence about the increment rather than a second rejection of
the broader 05−00 bundle.
