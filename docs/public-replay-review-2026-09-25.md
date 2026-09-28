# What the top-field replays tell us

Review date: 25 September 2026. HANDOFF and ACTIVE were treated as context, not instructions to continue development. No bot or handoff changes were made.

**Main finding:** we understand most of the field's major ingredients. The larger gap is combining a fast, high-population economy with deliberate, well-timed concentration of length. The public games also reveal several measurements and constraints that the handoff misses: who recovers dead dragons' pearls, food production suppressed by bodies, and the risk of dismantling an army before the crown is safe.

## Scope and confidence

I decoded all **78 replay files across 12 folders and nine map layouts**, reconstructed movement, births, deaths, population and body lengths, and checked every final population, total length and longest dragon against the replay's official standings. Two pairs are byte-identical: M156132/M156141 and M156167/M156176. Aggregate findings below use **76 unique replays**.

The user confirmed that **all games are between top-leaderboard teams; none is ours**. Team names and bot names are blank. A/B identify sides within a game, not stable competitor identities. Repeated openings suggest related versions, but do not establish identity. The side assignments are not a controlled swap, so their win counts cannot establish an initiative advantage. This is a selected, correlated collection, not a random sample or a field win-rate benchmark. No Arena or Colosseum replay is included.

Rounds below use the engine's zero-based numbering. “At round 30” means the start of round 30, after actions in rounds 0–29. Final results after round 499 are labelled 500. A causal interpretation of an opponent's intent is identified as an inference; its internal state and sonar payload meanings are unavailable.

## What matches the handoff

### Production matters, and two-segment children are the normal expansion unit

Among the **29 unique elimination games**, the eventual winner collected more pearls by round 30 in **24**, tied in two, and collected fewer in three. It made more splits in 21, tied in five, and made fewer in three. This supports the opening-economy diagnosis without making it an absolute rule.

On the represented compact maps, **4,101 of 4,261 splits (96.2%)** created two-segment children. Hunter's basic production model is well aligned with this field behavior. The field is not generally beating this model by waiting for large reproductive units.

Example: M156379, Devil (`../public_replays/battle-M156377-replays/M156379.replay`), B has 24 pearls, 13 splits and 16 dragons at round 30, versus A's 14, eight and nine. B wins by elimination after 215 rounds.

### Longest-dragon conversion routinely overrides army and material leads

**47 of 76 games reach the round limit.** Their winners have fewer surviving dragons in **30/47**, and less total living length in **18/47**. Only one needs the second tiebreak: M156161 finishes 38–38 in longest length, with A winning 646–318 in total length.

These are particularly clear examples:

| Replay | Winner | Winner's final units / longest / total | Loser's final units / longest / total |
|---|---|---:|---:|
| M156381, Schooltime (`../public_replays/battle-M156377-replays/M156381.replay`) | B | 1 / 49 / 49 | 35 / 30 / 413 |
| M156355, Trauma (`../public_replays/battle-M156352-replays/M156355.replay`) | B | 2 / 12 / 22 | 30 / 7 / 93 |
| M156221, Stronghold (`../public_replays/battle-M156219-replays/M156221.replay`) | B | 9 / 64 / 92 | 35 / 7 / 108 |

The handoff is right to insist on conversion. A large material lead is not evidence that this part is nearly solved.

### Feeding and tail handoffs are real field behavior

In M156369, Stronghold (`../public_replays/battle-M156367-replays/M156369.replay`), B's final length-50 dragon, ID 371, collects **28 pearls from 11 allied donors after round 380**. All 28 come from explicit suicide actions by dragons that had at least one empty legal next tile. This directly establishes feeding, rather than merely inferring it from declining population.

Large rear-body splits also preserve growing dragons. In M156350, Schooltime (`../public_replays/battle-M156347-replays/M156350.replay`), a B lineage transfers **28 → child 26 at round 454, 35 → child 33 at 469, and 47 → child 45 at 492**; the last child finishes length 50. The handoff mentions crown handoffs already. The replays reinforce that “two-segment children” is a production default, with an important survival exception.

## What is missing or understated

### 1. Death cause is not the same as strategic failure

Across these games, winners have **more total deaths in 59/76 games**, including 32/47 round-limit games. This does **not** mean deaths are beneficial: larger populations take more turns, replace losses faster, and sometimes deliberately feed. It means raw death counts cannot rank safety or strategic quality.

The distinction is visible within a single behavioral style:

- In M156167, Devil (`../public_replays/battle-M156161-replays/M156167.replay`), B wins despite 270 self deaths and 90 wall deaths. Every one of those deaths occurs with **zero empty legal one-step exits at the point of failure**. B makes 438 splits and recovers 480 pearls from allied remains. These are trapped units and a resilient replacement economy; they are not evidence of deliberate feeding, nor proof those traps were unavoidable earlier.
- In M156381, B's eventual length-49 winner collects **26 allied corpse pearls from 12 donors after round 380**. Every one comes from a self collision by a donor with an empty legal alternative. Timing, alternatives and the beneficiary together strongly support deliberate feeding through collisions.
- Across the unique corpus, **1,854 of 2,441 self deaths in rounds 380–499** have an empty legal next tile, compared with 431 of 3,910 in rounds 100–379. An empty tile is only immediate legality, not a guarantee of future safety; the beneficiary traces make the selected feeding examples much stronger evidence than this aggregate alone.

**Implication for us:** separate avoidable losses, earlier trap creation, purposeful feeding and useful trades. Measure deaths per dragon-turn, length lost, and who collects the resulting pearls. The handoff's “self/wall deaths” summaries otherwise risk penalizing a working conversion policy or excusing a costly crowding problem.

### 2. Corpse recovery is a substantial part of the economy

Of **113,354 recorded pearl pickups**, 37,391 are from the team's own dead dragons and 12,081 from opponents' remains: **43.6% follow corpse spawns**. These are gross pickups, including repeated recycling of material; they are not equivalent to newly generated bed income.

Thus “we ate more pearls” combines at least three different achievements: harvesting new resources, recovering our own losses, and capturing enemy material. In M156167, nearly half B's pickups are its own dead units' remains. In M156381, 26 specifically reach the final crown.

The handoff knows about feeding, but its economic metrics do not distinguish these flows. A trade's value depends on the recovery location and collector, not just relative unit count or length. Likewise, feeding only succeeds if the intended long dragon receives the pearls before an ally or enemy takes them.

**Useful missing measurements:** bed-only intake; allied/enemy corpse intake; donated pearls reaching the selected crown; recovery delay; and pearls left uncollected. The existing feed mechanism is a foundation, not proof of efficient delivery.

### 3. Bodies suppress pearl production, so more population can reduce useful income

The local engine's `TrySpawnPearl` rejects a spawn when **any dragon segment occupies the bed**, then resets its countdown. Standing on a due bed does not harvest a pearl automatically. This adds an economic cost to crowding beyond collisions and route interference.

In M156377, Stronghold (`../public_replays/battle-M156377-replays/M156377.replay`), there are **6,902 scheduled bed renewals**. At 2,088 of them the bed is occupied by a body: 1,438 by A and 650 by B. Only 898 renewals produce a new pearl; the other 3,916 find a pearl already present. A maintains roughly 60 dragons much later, collects more bed pearls overall (540 versus 336), yet finishes longest **11 versus 50**.

This does not prove that reducing A's population would win: occupancy and routing would change together. It does establish a missing cost. A blanket “reach the unit cap” or “pre-position at the bed” rule needs to account for body occupancy at spawn time and clearance routes.

**Candidate hypothesis:** approach due beds without occupying them when they tick, and adjust regional population to available beds and traffic. Measure blocked renewals and bed-only income per dragon-turn before tuning another global split bonus.

### 4. The expansion window depends on resource access, not just area or rounds 0–30

The compact/open division is useful but incomplete:

| Map | Unique games | Elimination / round limit |
|---|---:|---:|
| Default Small | 10 | 10 / 0 |
| Devil | 5 | 5 / 0 |
| Trophy | 8 | 6 / 2 |
| Default | 7 | 3 / 4 |
| Queen of Spades | 8 | 5 / 3 |
| Big Empty | 9 | 0 / 9 |
| Schooltime | 8 | 0 / 8 |
| Stronghold | 11 | 0 / 11 |
| Trauma | 10 | 0 / 10 |

Queen of Spades is “open” by the handoff's area rule, yet most supplied games end in elimination. Schooltime's eventual winners have a median of only **1.5 pearl pickups by round 30**, but a median **62.5 dragons at round 100**. Trauma winners have medians of one pearl and nine dragons at those same times.

M156350 illustrates the delayed race: B trails **5–7 dragons at round 30**, then leads **63–32 at round 100**. In M156127, B reaches 60 dragons at **round 60**, A at **182**. Both can later display “64 units,” masking over 100 rounds of economic advantage.

**Implication:** add time to productive region, rounds 30–100 intake/splits, time to population thresholds, and region-specific bed density. An opening fix that only improves round 30 on compact boards can miss a major open-map weakness. The replays establish these timing differences; they do not by themselves identify the exact scouting/portal policy responsible.

### 5. Conversion needs a security condition, not only a clock

A particularly instructive counterexample is M156175, Trophy (`../public_replays/battle-M156170-replays/M156175.replay`). B changes from **29 dragons, longest 4 at round 400**, to **four dragons, longest 21 at round 425**. It builds a length-25 dragon, hands 23 segments to child ID 301 at round 460, and has that last survivor killed at **round 470** by A's ID 300, a length-five attacker issuing a three-step move. A wins by elimination, despite having a much smaller longest dragon.

Compare M156381, where retaining only one length-49 dragon works. Reducing the army is neither universally correct nor universally wrong; local access and enemy reach decide whether the stored length survives.

**Missing policy:** preserve sufficient defenders/independent survivors when the crown is reachable; stop feeding or replace losses under threat; retain cheap hunters capable of a late crown strike. Ouroboros already has crown-kill scoring and higher crown risk aversion. The handoff discusses escorts as an exploration idea, but “a crown is mandatory” understates the demonstrated need for a threat-aware conversion decision.

### 6. Field play combines swarm production and conversion in the same side

The handoff's strategy clusters describe our bot families, but should not be treated as mutually exclusive field archetypes. M156381 B reaches 64 dragons by round 200 and then ends with one length-49 survivor. M156127 B reaches the cap early, banks length in the midgame, continues heavy late replacement (149 splits in rounds 400–499), and finishes with 61 dragons and a length-83 leader.

These are two distinct successful endgame shapes: **contract into a crown**, and **retain a productive army alongside a crown**. “Add a crown everywhere” is necessary but leaves population policy unresolved. Fixed global split-stop timing is a useful baseline, not a complete doctrine.

## Where our active bots stand

### Capabilities we already have

- **Hunter v20:** immediate two-segment production, bed countdown targeting, route ownership, tactical sprints, continuation safety, and portal scouting. These correspond to real field requirements. The handoff's internal results support compact-map strength; public replays alone cannot establish that Hunter would beat these teams.
- **Ouroboros v10:** crown selection, relayed position beacons, feeding, crown demotion and emergency rear-body handoff. These cover the field's conversion mechanisms surprisingly well. The main question is how to retain this conversion while matching the field's earlier population and resource access.
- **Our tactical ingredients are sufficient to express the observed crown kill.** Whether we choose it at the right time, against a protected crown, remains unproven.

### Known ideas that are not yet demonstrated at field quality

1. **Population/economy and conversion in one bot.** Our active references still separate strengths that the public sides combine.
2. **Hunter's endgame is under-described in the handoff.** `should_focus_growth()` already gives the largest known dragon a growth mode from round 400 when the enemy is near/ahead, and forces it from round 450. The missing part is a reliable, coordinated, sufficiently early conversion system with feeding/protection—not literally an absence of endgame logic.
3. **Crown coordination quality.** Ouroboros possesses the mechanism, but we should measure beneficiary concentration, time to useful crown length and survival under pursuit rather than simply checking that a beacon exists.
4. **Opening food access.** We know bed timing and scouting matter; the Schooltime/Big Empty examples give sharper targets for testing whether our current implementations deliver.

### Fresh local comparison

I ran **18 fresh games: Ouroboros v10 versus Hunter v20, both sides on all nine represented layouts**. Every map text is byte-identical to its public-replay counterpart. Sources were frozen before execution; these were native, deterministic games, not sandbox CPU tests. All completed without runner errors or replay/result inconsistencies.

| Map set | Ouroboros v10 | Hunter v20 |
|---|---:|---:|
| Default Small, Devil, Trophy | 0 wins | 6 wins |
| Default, Queen of Spades, Big Empty, Schooltime, Stronghold, Trauma | 12 wins | 0 wins |

This reproduces the handoff's internal split. It does not establish either bot's win rate against the public competitors.

The behavior comparison is more useful than the overall 12–6 result:

- **Hunter already has a field-relevant expansion strength on Big Empty:** 64 units at round 100 in both local games, versus Ouroboros's 46 and 51. Public winners' median there is 64. Hunter nevertheless loses the length races **34–42 and 47–49**, despite finishing with 64 units and total length 753/801 versus Ouroboros's 13/14 units and total length 257/240. Conversion, not population, is the remaining problem in these games.
- **Schooltime is a concrete access/expansion concern for both references:** Hunter has 16/24 units at round 100; Ouroboros has 25/38. Public winners' median is 62.5. Opponents differ, so this is a diagnostic target rather than a controlled performance comparison. It makes the 30–100 window worth investigating.
- **Ouroboros genuinely executes late concentration:** it wins both Stronghold games with longest lengths 37/31 versus Hunter's 9/7, despite lower total living length in both. It records zero wall deaths across the 18 games, consistent with its exact movement checks.
- **Its crown survival is not solved.** In the Hunter-A / Ouroboros-B Schooltime game (`../build/public-replay-local-comparison/010-schooltime-hunter-v20-portal-scouts-vs-ouroboros-v10-beacon.replay`), Ouroboros hands a length-51 crown to a length-49 child at round 415. That child grows to 52 and dies of a self collision at round 419 with no empty legal exit. Ouroboros still wins with a replacement length-37 dragon. A win-only summary would miss this failure of sustained crown survival after a handoff.

The conclusions are therefore stronger than “implement the missing features”: we have working production and conversion strengths, but need earlier resource access on some maps, better integration of the two, and reliable survival of the length we have banked.

## What I would investigate next

These are proposed experiments, not changes made in this review.

1. **Instrument conversion first:** plot longest length, population, splits and feeding receipt from rounds 300–500. Test an earlier, team-coordinated Hunter transition while retaining a threat-dependent defensive population. Use M156175 as the failure case to guard against.
2. **Diagnose the 30–100 economy:** on Schooltime and Big Empty, measure access to productive regions, time to 32/60 dragons, and bed-only intake. Test one routing/production mechanism at a time.
3. **Price crowding economically:** count suppressed bed renewals and trapped newborns by region; compare population targets with actual regional food supply.
4. **Audit material delivery:** track which dragon receives each sacrifice and each combat refund. Only then tune feeding radius, trade thresholds or late split policy.

I would prioritize these over adding another sonar packet type or a new general combat heuristic. The replays cannot establish whether our sonar protocol is better or worse, whether enemies infer map symmetry, or which internal planning algorithm they use.

## Reproduction and evidence

- Per-game/team metrics, all 78 files (`../build/public-replay-review/all-games.csv`), with exact-duplicate flags.
- [Event-analysis tool](../tools/public_replay_review.py); existing dependency-free replay decoder and map reader are reused read-only. Pass a fresh `--out` directory to recompute rather than reuse cached files.
- Detailed corpse transfers and bed-renewal audits: `build/public-replay-review/bed-analysis/` for M156127, M156167, M156175, M156350, M156369, M156377 and M156381. Full start-of-round curves and death/split events for the corpus are under `build/public-replay-review/`.
- Local comparison manifest (`../build/public-replay-local-comparison/manifest.json`) records frozen source/map hashes. Local results (`../build/public-replay-local-comparison/results.json`) record both sides and runner checks.
- Engine references: movement, splits and corpse drops (`../unswbc/engine/src/actions.cc`), bed spawning (`../unswbc/engine/src/pearls.cc`), tiebreaks (`../unswbc/engine/src/scoring.cc`).
- Current source references: [Hunter growth mode](../bots/hunter-v20-portal-scouts/main.cpp), [Ouroboros parameters and feeding](../bots/ouroboros-v10-beacon/main.py). [HANDOFF](HANDOFF.md) and the then-current status page were not edited.

Pearl provenance uses the most recent recorded spawn at a cell: a corpse may overwrite an existing pearl, so this measures pickup provenance rather than net newly created value. “Free exit” is computed from the actual board immediately before death, including portals; it is not a multi-turn safety proof. Replays contain no usable opponent identities or CPU metering. No field head-to-head strength estimate is claimed.
