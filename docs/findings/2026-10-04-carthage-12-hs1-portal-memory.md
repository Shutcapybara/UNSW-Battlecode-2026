# H-S1 portal-memory test — Carthage 12 (4 Oct 2026)

## Verdict

**Reject H-S1 as implemented. Both predeclared falsifiers fired.** The exact
per-transit death-within-three-round rate fell by only 2.7% on pool and 1.3%
on gen, short of the required 25%. Normalized `econ~` lower bounds were −0.065
on pool and −0.038 on gen, both below the −0.02 floor.

The arm reduced portal traffic by about a quarter. Raw transit-death counts
fell by a similar amount, but the chance of death after a transit barely
changed. This is the throttle cost H-S1 was intended to avoid.

## Test and implementation

The frozen candidate was `carthage-12-portal-memory`, forked from
`carthage-05-free-sprint`. It reports known transits with tagged sonar, treats
the lack of a timestamped report from that dragon through the three-round risk
window as possible death, relays trauma reports, and blocks the pair for 30
rounds. A later crown or density report from the same dragon confirms survival.
Prey-sighting packets are excluded because their ID names the prey. Sonar is
directional and silence can mean a missed or intercepted ray; a dragon that
dies during its move cannot send a report afterward ([execution order and
sonar timing](https://game.battlecode.au/docs/execution-order)). These limits
make this a missed-heartbeat approximation, not authoritative death knowledge.

`carthage-11-portal-memory` was an earlier partial draft that counted
prey-sighting IDs as source heartbeats. Its interrupted run is preserved under
`build/carthage/runs/carthage-11-portal-memory-unscored-partial/` and is excluded
from all results below.

The declared H-S1 panel protocol was followed: seeds 1–3, both seats, pool and
gen, compared with Carthage 05 on the same seed/map/opponent/seat fixtures under
`unswbc 1.2.5`. Candidate coverage was 480/480 pool and 744/744 gen fixtures;
all candidate run records verified 1.2.5 and succeeded, all replays decoded,
and feature extraction completed with zero errors. The Carthage 05 parent
replays are from the 1.2.5 five-seed rerun documented in the
[`05 vs 00 finding`](2026-10-03-carthage-05-vs-00-five-seed-1.2.5.md); its
older index rows predate the `runtime_version` field. The paired replay
analysis counts each portal step once and marks it died3 when the same dragon
died from the transit round through round +3, inclusive. Bootstrap intervals
resample paired game fixtures (3,000 draws, seed 17); intervals below are
central 90%.
Replay movement reconstruction verified 7,560,060 candidate / 7,492,807 parent
pool moves and 8,881,125 candidate / 8,778,297 parent gen moves, with zero
mismatches and zero decode errors.

## Portal outcomes

| Panel | Candidate died3 / transits | Parent died3 / transits | Candidate rate | Parent rate | Paired rate delta [90% interval] | Relative rate reduction |
|---|---:|---:|---:|---:|---:|---:|
| Pool | 14,420 / 44,578 | 19,655 / 59,105 | 32.35% | 33.25% | −0.91 pp [−1.45, −0.31] | 2.7% |
| Gen | 13,319 / 31,507 | 18,323 / 42,799 | 42.27% | 42.81% | −0.54 pp [−1.40, +0.26] | 1.3% |

Pool traffic fell 24.6% and raw died3 counts fell 26.6%. Gen traffic fell
26.4% and raw died3 counts fell 27.3%. The paired death-rate result does not
support a 25% reduction in risk per transit on either panel.

### Named maps

| Panel / map | Candidate rate | Parent rate | Relative reduction |
|---|---:|---:|---:|
| Pool / Portals | 49.82% (9,332/18,733) | 48.41% (13,224/27,316) | −2.9% |
| Pool / Schooltime | 25.48% (1,581/6,204) | 26.08% (1,830/7,016) | 2.3% |
| Pool / Trauma | 10.47% (467/4,461) | 10.98% (558/5,080) | 4.7% |
| Gen / pub/portals_rec | 50.17% (4,637/9,243) | 48.41% (6,667/13,773) | −3.6% |
| Gen / var/portals_tr | 56.37% (6,019/10,677) | 54.61% (8,183/14,985) | −3.2% |
| Gen / var/trauma_tr | 12.99% (368/2,833) | 11.02% (357/3,240) | −17.9% |

The two portal-heavy gen maps regressed on per-transit risk. Trauma improved
slightly on pool and regressed on gen; no named map approaches the 25% target.

## Economy and paired score

| Panel | `econ~` delta [90% interval] | `econ_mean` delta [90% interval] | Win delta [90% interval] |
|---|---:|---:|---:|
| Pool | −0.052 [−0.065, −0.034] | −0.025 [−0.033, −0.016] | −0.027 [−0.056, 0.000] |
| Gen | −0.029 [−0.038, −0.011] | −0.006 [−0.015, +0.005] | −0.012 [−0.028, +0.004] |

The Carthage lane's standard D-032 score is `REJECT`. Its other pool lower
bounds also miss the material guards: units@100 −0.054 and total@100 −0.052.
These are three-seed local results, not a promotion or field-strength claim.

## Conclusion and follow-up

Do not register or promote Carthage 12. Keep Carthage 05 as the family
reference. Treat the pair-blocking missed-heartbeat rule as a negative portal
arm: the implementation cuts traffic without materially improving survival
per transit, and fails the economy bound. Any revival needs a more reliable
positive outcome signal or an exit-side intervention that improves per-transit
survival while retaining portal volume. This is one negative portal arm; it
does not satisfy the separate two-consecutive-non-movers-per-family condition
for stopping hand-mining.

## Reproduction and artifacts

```sh
CARTHAGE_NICE=10 UNSWBC="$PWD/.venv/bin/unswbc" \
  ./.venv/bin/python tools/carthage/lane.py run carthage-12-portal-memory \
  --panel both --seeds 1,2,3 --jobs 12
UNSWBC="$PWD/.venv/bin/unswbc" \
  ./.venv/bin/python tools/carthage/lane.py score carthage-12-portal-memory \
  --parent carthage-05-free-sprint --seeds 1,2,3 \
  --json build/carthage/results/carthage-12-vs-05-hs1-pool-gen-seeds1-3-1.2.5.json
python3 tools/carthage/portal_memory_report.py carthage-12-portal-memory \
  --parent carthage-05-free-sprint --seeds 1,2,3 --jobs 8 \
  --out build/carthage/results/carthage-12-hs1-portal-deaths-pool-gen-seeds1-3.json
```

Run records, replays, extracted features, lane score, and portal-death JSON are
under `build/carthage/runs/carthage-12-portal-memory/` and
`build/carthage/results/`. The focused analyzer is
`tools/carthage/portal_memory_report.py`.
