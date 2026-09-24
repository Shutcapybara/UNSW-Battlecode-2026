# Charybdis: exploration results

New family: **leviathan-x04-charybdis-replies**. The experiment changes the decision model to adversarial local-game search; it does not train an actor-critic. The tested default uses a 450-node nominal budget with leaf accounting fixed.

## Full gauntlet and competitive diversity

| Set | W–L–D |
|---|---:|
| ALL | 31–79–0 |
| compact | 16–34–0 |
| side B | 16–39–0 |
| compact B | 10–15–0 |
| fry-v14-stateful-size-aware-3 | 5–17–0 |
| hunter-v14-cpp-hybrid-route-spacing | 8–14–0 |
| hunter-v20-portal-scouts | 7–15–0 |
| kraken-v04-eval | 9–13–0 |
| side A | 15–40–0 |
| compact A | 6–19–0 |
| ouroboros-v10-beacon | 2–20–0 |
| open | 15–45–0 |
| open B | 6–24–0 |
| open A | 9–21–0 |

On these identical 110 fixtures, v09 scores 85–25–0 and Riptide x02 scores 42–67–1. Charybdis scores **31–79–0**, adding **3** wins where v09 loses, of which **2** also lose for Riptide x02. It fails to retain 57 of v09's wins. Opponent sources, map hashes and execution modes match.

- `arena`, side B, vs `hunter-v14-cpp-hybrid-route-spacing`; Riptide result L.
- `arena`, side B, vs `ouroboros-v10-beacon`; Riptide result L.
- `default`, side B, vs `hunter-v14-cpp-hybrid-route-spacing`; Riptide result W.

These are fixture-specific niches, not a validated rule for selecting which bot to deploy.

## Causal screen: reply search versus no search

Base is `reply_plies=0`; candidate is the final default. Same evaluator, routing, production policy and root actions. Four control games reproduce the old no-search movement/split/sonar streams after the budget fix.

| Set | Base W–L–D | Candidate W–L–D | Score Δ | Net W–L Δ |
|---|---:|---:|---:|---:|
| ALL | 5–19–0 | 4–20–0 | -1.0 | -2 |
| compact | 1–17–0 | 2–16–0 | +1.0 | +2 |
| side B | 3–9–0 | 3–9–0 | +0.0 | +0 |
| compact B | 1–8–0 | 2–7–0 | +1.0 | +2 |
| hunter-v14-cpp-hybrid-route-spacing | 2–6–0 | 2–6–0 | +0.0 | +0 |
| hunter-v20-portal-scouts | 2–6–0 | 1–7–0 | -1.0 | -2 |
| leviathan-v09-arrival | 1–7–0 | 1–7–0 | +0.0 | +0 |
| side A | 2–10–0 | 1–11–0 | -1.0 | -2 |
| compact A | 0–9–0 | 0–9–0 | +0.0 | +0 |
| open | 4–2–0 | 2–4–0 | -2.0 | -4 |
| open B | 2–1–0 | 1–2–0 | -1.0 | -2 |
| open A | 2–1–0 | 1–2–0 | -1.0 | -2 |

Improved: 1; regressed: 2; unchanged: 21. Deterministic fixtures.

The screen contains three compact maps and one open map against Hunter v14, Hunter v20 and v09, both sides. Read the per-class splits; totals are not population-wide estimates.

| Profile | Logged / total decisions | Searched | Changed from immediate choice | Changed / searched | Max visited nodes |
|---|---:|---:|---:|---:|---:|
| screen | 57483 / 57483 | 12025 | 3985 | 33.1% | 2677 |
| myopic | 53321 / 53321 | 0 | 0 | 0.0% | 0 |
| final-screen | 57522 / 57522 | 11927 | 3959 | 33.2% | 459 |

Only recorded indicators contribute to the usage rates. These counts establish that the solver changes decisions, not that the changed actions are correct. Dead newborns may never produce an indicator.

| Profile | Pearls | Splits | Head deaths | Initiated head trades / 1,000 turns | Wall / self / body deaths |
|---|---:|---:|---:|---:|---|
| screen | 4816 | 1422 | 1189 | 12.33 | 60 / 80 / 114 |
| myopic | 4209 | 1160 | 961 | 7.95 | 51 / 60 / 96 |
| final-screen | 4828 | 1413 | 1164 | 11.72 | 68 / 72 / 108 |

Raw totals depend on game duration and population. The deeper prototype makes more head trades while losing more screen games than the no-search control. This is evidence against this particular model/evaluator pairing, not against adversarial search in general.

### Opening economy

**myopic**

Rounds [0,30); earlier eliminations stop at the final state.

| Class | Games | Pearls us/them | Splits us/them | Units at end us/them |
|---|---:|---|---|---|
| compact | 18 | 26.56 / 20.50 | 8.94 / 8.50 | 7.39 / 7.44 |
| open | 6 | 9.83 / 8.83 | 5.67 / 6.67 | 8.50 / 10.33 |


**final-screen**

Rounds [0,30); earlier eliminations stop at the final state.

| Class | Games | Pearls us/them | Splits us/them | Units at end us/them |
|---|---:|---|---|---|
| compact | 18 | 25.67 / 23.00 | 8.11 / 9.50 | 6.44 / 8.11 |
| open | 6 | 8.50 / 11.33 | 5.50 / 6.83 | 8.83 / 10.17 |


## Orientation validation

Six transformed open maps × Hunter v20/v09 × both sides (24); this is not full G+V or a globally unused holdout.

| Set | W–L–D |
|---|---:|
| ALL | 2–22–0 |
| open | 2–22–0 |
| side B | 1–11–0 |
| open B | 1–11–0 |
| hunter-v20-portal-scouts | 2–10–0 |
| leviathan-v09-arrival | 0–12–0 |
| side A | 1–11–0 |
| open A | 1–11–0 |

## Compute and engineering history

The deeper 1800-budget prototype reached 99.8M CPU points. Reducing its nominal budget to 450 still reached 94.9M: leaf evaluations were bypassing the budget decrement. The final implementation charges leaves too. Evaluation weights and strategic rules were not tuned during this repair.

| Implementation snapshot | Screen W–L–D | G W–L–D | Orientation W–L–D | Judge max, M |
|---|---:|---:|---:|---:|
| 1800, expansion-only | 2–22–0 | 26–84–0 | 2–22–0 | 99.8 |
| 450, expansion-only | 2–22–0 | 26–84–0 | 2–22–0 | 94.9 |
| 450, leaf-accounted | 4–20–0 | 31–79–0 | 2–22–0 | 57.0 |

Final judge sample: arena, big_empty, trauma, both sides against Hunter v20.

| Metric | Per-game range, million points |
|---|---:|
| cpu_p50 | 4.7–7.9 |
| cpu_p99 | 5.8–34.4 |
| cpu_max | 5.9–57.0 |

Sampled CPU gate: **pass** (p99 <60M; max <80M). Ranges are runner-rounded per-game statistics, not pooled percentiles or a worst-case proof.

All **520 executions** have checked replays, no runner/analysis errors or recorded timeouts, and zero Charybdis invalid-action deaths. These include repeated deterministic fixtures under different implementations/configurations and are not 520 independent samples. The archive contains one final source family; earlier implementations remain in frozen run snapshots.

The regression suite passes, including focused local-game tests for turn order, same-round births, collision/carcass rules, sprint funding, bed timing, incomplete observation, a forced-reply tactic and leaf-budget accounting.

## Exploration verdict

Retain Charybdis and its no-search control as distinct experimental baselines
for phase-end selection. This exploration does not change ACTIVE or replace
the stronger Leviathan v09 reference. The value of reply search remains a
measured question; resemblance to a chess engine is not evidence of strength.

The new reusable component is the local multi-actor transition model and its
opponent-reply solver. The evidence motivates different experiments at phase
end: multi-opponent interaction instead of a single duel; opponent-policy
sampling instead of a worst-case reply; and a value function that distinguishes
locally favorable exchanges from team-level winning chances. Each would be a
new hypothesis, not a reason to keep tuning this branch's current weights.

The existing approximation can value a local sacrifice incorrectly because it
omits the rest of the team's future. Away from a fully observed duel the policy
is a greedy economic evaluator, and it has no long-route trap solver. Those are
explicit model limits; the match totals alone do not isolate their individual
contributions. Unknown edges are blocked for both players, so a predicted trap
can be false when an opponent can escape into unseen terrain. No trained-network
or online-learning claim is made.

Design, assumptions and commands: [CHARYBDIS.md](CHARYBDIS.md).
Raw evidence: `build/leviathan/charybdis-*`.
