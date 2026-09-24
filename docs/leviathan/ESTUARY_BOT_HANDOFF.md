# Estuary: implementation and phase handoff

## Status

**Exploration branch: `leviathan-x03-estuary-roles`, Python, based on `leviathan-v09-arrival`.**
Keep it as an alternative doctrine and a source of separable components. It is
not a demonstrated replacement for v09. Riptide, ACTIVE and the main handoff
were not changed. No online submission or promotion was made.

The user requested a role-based exploration fork informed by top-leaderboard
replays. The companion [strategy summary](ESTUARY_STRATEGY_HANDOFF.md) describes
that evidence and the parameterisation for the central aggregation model.
The [bot README](../../bots/leviathan-x03-estuary-roles/README.md) lists every
new parameter, its range and its consumer. The original public-replay review
contains the broader comparison with Hunter and Ouroboros.

## What is implemented

The inherited core supplies parsing, movement/sprint simulation, terrain and
portal memory, arrival-aware food targeting, candidate evaluation, production,
sonar and emergency tail handoffs. Estuary adds a separate colony policy with
three jobs:

- **Scouts:** prefer exploration over long food detours, avoid enemy attraction,
  send regional discovery reports, and retire as coverage or elapsed time makes
  more scouting less valuable. Desired scout share falls with estimated coverage.
- **Gatherers:** value bed density discounted by observed danger; waypoint
  scoring discounts crowding and movement scoring charges for occupying a bed
  due next tick. They reproduce early, then progressively retain length.
- **Hunters:** chase only recent nearby targets, pay a lower price for surviving
  sprints and can replace losses late while the population is below its target.

The **crown is a gatherer carrying the final-length objective**. It remains a
separate internal role code because the inherited evaluator already recognizes
it. Election uses full identities, fresh known lengths and deterministic ties.
Banking ramps from round 280 to 400; the desired population declines rather
than switching from full production to universal liquidation on one turn.
These are fixed exploratory defaults, not learned optimum timings.

Donation begins at round 380 and requires a larger, fresh recipient whose head
is directly visible, a short known route from that head to a corpse-drop tile,
no recently observed nearby enemy, a retained population reserve, and an
ID-staggered opportunity. Hunters and crowns do not donate. An explicit replay
indicator labels the intentional no-action death. These conditions reduce
reckless donation but do not reserve a pickup route or command the recipient.

Communication changes preserve original observation times through crown/enemy
relays and use 16-bit dragon and portal identities. Scouts can spend three of
four sonar slots on queued discoveries. Regional packets have actual consumers:
coverage estimates, role retirement, target/waypoint values and population
targets. This is still a tagged, unauthenticated protocol.

## Implemented but disabled in the selected profile

`continuation.py` performs a bounded existence search using the moving body,
one-time consumption of confirmed pearls, and collision before tail release.
It can penalize long-body moves and reject splits whose reversed child has no
searched continuation. Unknown terrain and exhausted search budget return
unknown; incomplete newborn geometry is not treated as a complete body.

**The selected `params.py` sets `estuary.safety=0`.** This restores the inherited
geometry evaluator while retaining the new doctrine. On Schooltime, Stronghold
and Trauma against Hunter v20 and Kraken v04, both sides, the all-enabled profile
went **8–4**; disabling this option went **11–1**, recovering three Stronghold
losses with no outcome regressions in that subset. Keeping the unproven veto
enabled merely because it sounds safer would misrepresent the evidence.

The search holds other bodies stationary, cannot model an unseen long newborn
completely, and shares a budget across candidates. Those are plausible sources
of over-conservatism and unequal candidate coverage, not demonstrated causal
autopsies of the three recovered games. Separate the small-child veto from the
long-crown continuation penalty before revisiting this feature.

## Experiments

All outcomes are deterministic local fixtures, not independent random samples
or estimates of leaderboard win rate. Sources and maps were frozen by the lab.
Native outcomes and sandbox CPU checks are kept separate. The parent comparison
uses common map/opponent/side fixtures from `cycle1-v09-G`; the comparison tool
checked matching opponent and map hashes.

| Experiment | Scope | Result |
|---|---|---|
| Initial all-enabled screen | Six maps, Hunter v20 + Kraken v04, both sides | 18–6; parent 23–1 on identical fixtures; 0 improvements, 5 regressions |
| Continuation ablation | Schooltime, Stronghold, Trauma; same two opponents/sides | 11–1 without continuation vs 8–4 with it |
| Adaptive-role ablation | Same 12 fixtures, continuation still enabled | 7–4–1 with adaptive roles off vs 8–4 with them on; mixed exchanges, not an independent proof of role benefit |
| Neutral master switch | Arena, Default Small, Default vs Hunter, both sides | 6/6 exact parent action/sonar streams |
| Mechanistic tests | Geometry, feeding, state, packets and real-runner bootstrap | 22 passing |

### Selected profile: continuation disabled

| Map | Parent v09 | Selected Estuary | Fixtures |
|---|---:|---:|---|
| Big Empty | 4–0 | 2–2 | Hunter v20 + Kraken v04, both sides |
| Default Small | 4–0 | 3–1 | Same |
| Devil | 3–1 | 4–0 | Same |
| Schooltime | 4–0 | 4–0 | Same |
| Stronghold | 4–0 | 4–0 | Same |
| Trauma | 4–0 | 3–1 | Same |
| **Total** | **23–1** | **20–4** | **24 native fixtures** |

Relative to the parent, **one fixture improves and four regress**. The new win
is Devil B versus Hunter. Regressions are Big Empty A versus Hunter, Big Empty
B versus Kraken, Default Small A versus Hunter and Trauma B versus Kraken.
The Big Empty Kraken loss ties at longest 45 but loses total length 394–636:
the secondary score still matters. Compared with the all-enabled Estuary,
disabling continuation improves four fixtures and regresses two, so the safety
ablation is not a universal improvement either.

Directly against v09 on Big Empty, Schooltime, Stronghold and Trauma, selected
Estuary is **2–6**. Both wins are Schooltime: final longest **38–24 from B** and
**52–15 from A**. It loses both sides on the other three maps. This is the most
concrete evidence of useful matchup diversity, not an overall strength claim.
Schooltime A still loses a length-86 dragon to self-collision at round 448
before winning with a replacement; the crown-survival gap remains real.

Selected Schooltime growth against Hunter reaches **54/22 units at round 100
(A/B)** versus the parent's 38/25. Against Kraken it reaches **41/31** versus
27/28. Improvement is concentrated in particular openings rather than universal.

Across the selected 24 games, **142/142 invalid-action deaths** are same-round
marked donations, with no unaccounted invalid actions, replay errors or timeout
flags. The 426 donor drop events yield 252 attributed pickups by the intended
recipient (232 within ten rounds), 126 by other allies and five by enemies.
These are descriptive outcomes of changed games, not a controlled efficiency
comparison with the first profile.

The selected 24 consists of `estuary-no-safety-v2` plus
`estuary-selected-complement`. Their Python runtime modules and effective
parameter dictionaries were checked against the final bot, as were the direct
parent and judge runs. Evidence: `estuary-selected-source-verification.json`.

### Judge and cross-runtime checks

| Selected profile vs Hunter | Result | p99 CPU points | Maximum CPU points |
|---|---|---:|---:|
| Big Empty B | Win | 73.9M | 94.0M |
| Big Empty A | Loss | 74.0M | 98.8M |
| Trauma B | Win | 36.4M | 49.5M |
| Trauma A | Win | 34.8M | 45.5M |

All four have zero timeout flags and no unexplained invalid actions. Values
are the runner's rounded per-team summaries. **98.8M against a 100M limit is
not comfortable headroom.** This fork should receive a focused performance pass
before a broader judge campaign; passing these fixtures is not a global bound.

Selected native and sandbox outcomes agree on all four fixtures, but their
full streams are identical on only three. Big Empty B first differs in sonar
at round 358. The initial all-enabled profile also diverges between runtimes;
Big Empty A changes from a native win to a sandbox loss, with its first stream
difference a movement at round 444. No timeouts explain these differences.
Their cause is not established. Keep runtime mode explicit and do not transfer
native rankings to the judge without checking. Native master-off equivalence
is a separate, successfully verified claim.

### What the first screen taught us

The 30–100 expansion window is a real, measurable target. Against Hunter on
Schooltime, initial Estuary reaches **58 units at round 100 from A**, versus
the parent's 38. From B it reaches **24 versus 25**. Against Kraken the counts
are **41/32 versus 27/28** (A/B). That is useful evidence of changed growth
behavior, but the side asymmetry matters and the initial profile did not win
any fixture the parent lost.

Early resource capture can also regress. On Default Small A versus Hunter,
initial Estuary collects five pearls before round 30 versus the parent's 16,
then loses by elimination. Late crown policy cannot repair an opening it does
not survive. Stronghold's initial round-100 populations were lower than the
parent's on all four fixtures, despite retaining enough activity to generate
many deaths and splits later.

Donation is disciplined but imperfectly directed. In the initial 24 games,
all **150 invalid-action deaths** had same-round explicit donation indicators.
Those donors produced **435 drop events**; the replay attributes **232 pickups
to the named recipient** (213 within ten rounds), **148 to other allies**, and
**14 to enemies**. The remainder is uncollected or lost to provenance overwrites.
This is gross last-spawn attribution, not net production or an exact transfer
efficiency estimate. Visibility and proximity alone do not guarantee delivery.

Long-body survival is not solved. The initial profile still loses a length-59
dragon to self-collision on Schooltime against Kraken, and several other large
dragons die despite the continuation option. Winning the match does not erase
these failures. The optional planner needs stronger evidence before promotion.

## Limitations the central model should retain

- Regional resource values estimate **bed density**, not exact future net yield
  or respawn frequency. The bed-occupancy charge covers only the next tick.
- Role quotas are inferred from fresh local reports, not enforced globally.
  Coverage uses per-region maxima, so it is an estimate rather than a union of
  every teammate's visited cells. Disconnected regions may elect several crowns.
- “Defended” means observed danger is low. There is no formation controller,
  escort assignment, interception planner, or proof that an unseen attacker
  cannot reach the banker. A reserve count is not an escort.
- Feeding does not include a recipient acknowledgement, pickup reservation,
  guaranteed return on the donor's remaining lifetime, or a comparison against
  the value of keeping that donor harvesting.
- Hunter improvements here are bounded targets and sprint/replacement weights.
  Numerical superiority and coordinated attack timing remain inherited or
  absent; this is not a new team combat planner.
- The inherited first-turn child path reconstructs only locally visible body
  geometry. Sparse observations and portal distance approximations remain.
- Initial all-enabled Big Empty judge use reached 96.8M CPU points on one side;
  that is little margin under 100M. Judge figures below determine the selected
  profile's observed health, not a universal upper bound over unseen maps.

## What to aggregate and what to test next

Carry forward the **three jobs plus changing economic state** model, full-ID
freshness-preserving crown reports, explicit donor attribution, the economic
cost of bed blocking, and the need to measure delayed expansion separately from
round-30 opening income. Keep switches so the aggregator can transplant and
test one component at a time.

The next informative experiments are recipient-acknowledged feeding, supply-
and-crowding-based birth value, and separating crown continuation from child
split rejection. Evaluate component combinations against the full active pool
and held-out orientations before exploiting parameters. This phase did not
perform the full 110-game gauntlet or broad tuning, and should not claim that
the role doctrine is better merely because its explanation is attractive.

## Reproduction and artifacts

The lab's `manifest.json`, `results.json`, `ledger.jsonl`, logs and `.replay`
files retain each experiment. Relevant directories under `build/leviathan/`:

- `estuary-screen-v2`: initial 24-game profile with continuation.
- `estuary-no-safety-v2`: 12-game selected-profile subset; safety disabled in
  frozen parameters. Runtime modules match the selected bot.
- `estuary-selected-complement`: selected profile's other 12 screen fixtures.
- `estuary-no-roles-v2`: adaptive-role ablation, retaining continuation.
- `estuary-selected-base`: direct matches against the parent.
- `estuary-neutral-v2`: master-off equivalence control.
- `estuary-judge-v2`, `estuary-judge-open-v2`: initial-profile CPU checks.
- `estuary-selected-judge`: selected-profile CPU checks.
- `estuary-metrics-v2`, `estuary-selected-metrics`: reconstructed growth,
  deaths and corpse pickup provenance.
- `estuary-initial-audit.json`, `estuary-selected-audit.json`: joined donor and
  growth/death evidence; `estuary-selected-source-verification.json`: final
  runtime-source and effective-parameter checks.

`tools/leviathan/estuary_audit.py` joins the replay metrics with same-round donor
indicators and reports unaccounted invalid actions. The bot README supplies
run commands; toggles are snapshot-only when passed through the lab.

The earlier `estuary-screen-v1` and `estuary-judge-v1` are **excluded integration
failures**, caused by assuming the runner registered its executed program as
`sys.modules['__main__']`. The live namespace interface fixes that assumption;
a regression test reproduces the runner's execution style. They are not losses
to include in strategy comparisons.
