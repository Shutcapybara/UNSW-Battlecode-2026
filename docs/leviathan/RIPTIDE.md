# Leviathan Riptide — independent experimental family

Created for the explicit request to make a hard design divergence and preserve
competitive diversity. This family is allowed to depart from the shared core
architecture. It is not a replacement for Leviathan v09 and does not change
ACTIVE. Mainline and Riptide remain separate sources of candidates.

## Naming and ownership

Use `leviathan-xNN-riptide-<hypothesis>` for structural versions:

- `leviathan-x01-riptide-horizon`: fresh route planner and resource-funded colonies.
- `leviathan-x02-riptide-viability`: add a separate escape-capacity requirement.

Keep the `leviathan-` namespace, the experimental `xNN` sequence, and the
`riptide` family marker. Do not recycle version numbers. Parameter-only
experiments are private `params.h` overrides in the lab, never bot folders.
The ordinary `leviathan-vNN-*` sequence remains the convergence line.

## The substantive divergence

| Decision | Leviathan v09 | Riptide |
|---|---|---|
| Selection | One evaluation of present candidates | Separate first-action beams forecast several future turns |
| Safety | Risk, space, target and material share one score | Survival depth and first-step risk precede route utility; x02 adds a capacity tier |
| Production | New unit priced against a population target and role constraints | Hard investment rule: split into two-segment child only when parent and child have distinct reachable food opportunities |
| Endgame | Elected crown, beacons, demotion, sacrificial feeding | Each surviving dragon banks its own length after the time/size cutoff |
| Coordination | Several packet kinds and role hand-off | One 20-bit-ID self-report kind; only consumer is soft resource ownership |
| Tactical posture | Deliberate strikes, role-dependent exchanges | Harvest and avoid contact; enemy-head collision only as a fallback when no ordinary move survives |
| Implementation | Python core derived from Ouroboros v10 | Fresh C++ decision logic; geometry/protocol concepts ported from Leviathan v07 |

This is not an Ouroboros or Hunter policy port and is not merely a parameter
preset. It has no dependency on another bot at runtime. C++ provides enough
budget to make future trajectories the basic decision unit.

## State and planning contract

`world.h` maintains observed terrain, integer portal identity without packet truncation, correction by
direct observation, pearl observations and countdowns, own movement history,
visible bodies and short-lived teammate positions. Unknown portal partners
stay blocked. Enemy and teammate bodies outside vision remain unknown.

`planner.h` builds enemy reach and a food/frontier potential field. Every legal
first move or bounded sprint gets its own beam. Forecast states carry a body,
eaten-pearl set and discounted reward. Only the first action is committed;
the next observation causes a new plan. Current sprint affordability and body
growth use only confirmed pearls. Forecast turns may use remembered or predicted
food and optimistic unknown edges; they are hypotheses, not safety guarantees.
Other observed bodies remain stationary in the forecast.

x02 adds an earliest-arrival flood that models when own segments would leave.
The capacity estimate assumes one tail release per future turn and therefore
can be optimistic if future growth prevents release. It also freezes other
bodies and blocks unknown terrain. It is a bounded heuristic, not an exact
proof of future escape. These assumptions are exposed so future forks can
replace them independently.

A split creates a two-segment child on the reversed tail. The parent and child
must have immediate exits, and x01/x02's default colony policy requires two
distinct food targets within their reachable catchments. The catchments can
overlap; this is a resource-assignment check, not a proof of disjoint territory.
Length banking is distributed and begins at round 350 or length 12 by default.

## Search baselines and ablations

The frozen configurations test different claims; none is silently overwritten:

| Profile | Source | Overrides | Question |
|---|---|---|---|
| Horizon colonies | x01 | defaults | Does independent forecasting plus resource-funded division work? |
| Myopic | x01 | `horizon=1` | Does forecasting add measurable value? |
| Early bank | x01 | `fork_food=False`, `split_stop=120` | Does a short production phase followed by distributed banking work? |
| Silent | x01 | `radio=False` | Does the self-report ownership consumer help? |
| Monolith | x01 | `population_max=1` | Can retaining all growth in the initial dragons beat churn/crown policies? |
| Viability colonies | x02 | defaults | Does explicit escape capacity prevent forecast traps? |
| Factory | x02 | `fork_risk=1.01`, `fork_food=False` | Does reproducing under head pressure repair the opening? |
| Neutral control | x02 | `viability=False` | Does disabling the capacity component recover x01's action stream? |

The early-bank and factory profiles intentionally vary a coherent policy group;
they do not isolate the contribution of each constituent parameter. x02's
original 0.35 reproduction-risk constant was subsequently exposed as
`fork_risk=0.35`, without changing its value, for the factory experiment.
Monolith disables reproduction; it does not remove initial dragons. The tested
open maps begin with two to four dragons per team, all of which can bank length.

## Reproduction

All tunables are documented with range and consumer beside the declaration in
`params.h`. Use the lab from the repository root; `--set` rewrites only the
copied header, records effective hashes and rejects unknown or nonnumeric keys.

```sh
python3 tools/leviathan/lab.py run leviathan-x02-riptide-viability \
  --vs leviathan-v09-arrival hunter-v20-portal-scouts \
  --maps arena,default_small,default,big_empty --jobs 3 \
  --base leviathan-x01-riptide-horizon --cycle riptide-1 \
  --output build/leviathan/my-new-riptide-run

python3 tools/leviathan/lab.py run leviathan-x01-riptide-horizon \
  --vs leviathan-v09-arrival --maps full --jobs 3 \
  --set population_max=1 --output build/leviathan/my-new-monolith-run

PYTHONPYCACHEPREFIX=/tmp/leviathan-pycache python3 -m unittest \
  discover -s tools/leviathan -p 'test_*.py'
```

The validation orientations were held out from Riptide profile selection; they
were previously used by the mainline and are not globally new maps.

The C++ tests exercise toroidal edges, portal IDs and correction, collision
before tail release, confirmed sprint payment, forecast/current separation,
20-bit identity and corrupted/expired/other-team packets, split funding,
endgame stop, legal planned actions and the capacity component. The existing
mainline regression suite remains active.

## Evidence and decision

Final results, side/class splits, CPU, ablations and diversity measurements are
recorded in [RIPTIDE_RESULTS.md](RIPTIDE_RESULTS.md). Deterministic map/side fixtures
are not independent random samples. A weak family is not promoted merely for
being different: preserve it as a search baseline and name demonstrated niches
separately from overall strength.

On the full 110-game gauntlet, x01 scores 33–77 and x02 scores 42–67–1,
against mainline v09's 85–25. x02 adds four wins on fixtures that v09 loses,
but targeted orientation validation is only 17–71. Use x02 for further
Riptide research and x01 as its control; neither is nominated for promotion.
The capacity component helps mainly on open maps. Compact opening economy
and conversion remain the main weaknesses.
