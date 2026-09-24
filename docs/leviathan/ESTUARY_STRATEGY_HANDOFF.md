# Public-field strategy synthesis and Estuary design brief

Audience: the central model aggregating this phase. This is an exploratory contribution, not an instruction to promote a bot or replace ACTIVE. Evidence: [the complete public-replay review](../public-replay-review-2026-09-25.md).

## What a crown is

The crown is the **designated carrier of the team's final longest-dragon score**. It is normally a large gatherer, but not necessarily whichever dragon is largest on this exact turn. Its teammates should preserve its growth opportunities and survival. A longer or safer candidate can replace it; a rear-body split can transfer the responsibility to a child. Keeping a dragon long is useful only if it survives until the result is evaluated. The engine has no special crown unit: it compares the longest living dragon at the round limit, then total living length if those tie. Elimination remains an immediate way to win or lose.

Treat **scout / gatherer / hunter as jobs**, and **producer / banker / donor / protected crown as changing states**, rather than introducing a fourth unrelated economic role. The implementation may retain a crown role code for compatibility while its semantics remain “gatherer carrying the length objective.” Crown election is based on incomplete, delayed information: temporarily having regional candidates is more realistic than assuming perfect global agreement.

## How the proposed roles fit

| Job | Main objective | Production and length | Transition conditions | Main failure to prevent |
|---|---|---|---|---|
| Scout | Find productive regions, portal links and useful enemy information; communicate findings | Collect convenient pearls to replace/produce explorers and fund useful travel, but avoid long food detours | Retire into gathering when coverage is high; into hunting where recently observed enemies make border pressure useful | Permanent exploration after information stops paying; repeated scouts inspecting the same area; paying length for purposeless speed |
| Gatherer | Harvest rich, relatively safe patches and supply the team | Split aggressively while another unit has economic value, progressively retain length, and sometimes donate to a better banker | Crown selection, changing local crowding, depletion, enemy access, declining reproduction horizon | Literal camping on a bed, suppressing spawns; crowding own offspring; many small bankers competing for the same pearls |
| Hunter | Defend productive territory, expand access and threaten enemy heads/crowns | Maintain a replaceable force; spend length on attacks when the expected exchange is useful | Rebuild when local force is weak; stop distant chases; protect the crown when enemy reach matters | Sprinting without a concrete payoff; equal trades while under-producing; abandoning the crown to chase |

A gatherer should **circulate through a productive defended patch**, not stand on the due bed: a body occupying the bed prevents that spawn. “Defended” should mean observed control and manageable enemy reach, not a fixed map quadrant. “Border” is similarly the changing interface between productive friendly space, unknown territory, and enemy access—not necessarily a Euclidean line.

Sonar has four directional rays per surviving dragon per turn. All our inherited roles already use all four. “High-density sonar scouts” therefore means **more useful discoveries per ray, better message selection and useful positioning**, not exceeding the four-ray limit. Preserve self reports and parent-to-child handoffs while allocating more scout slots to fresh terrain/resource information. A packet needs a receiver-side decision that consumes it.

Pearl gathering and scouting are not opposites. Food has reproductive value while scouts are scarce, and denying food in contested territory can support hunters. The scout's food/exploration ratio and retirement conditions should be parameters rather than a permanent prohibition on collecting pearls.

## Field evidence the aggregator should preserve

All public games are between top-leaderboard teams, not ours. There are 78 files, 76 unique games after two exact duplicates, nine map layouts, blank competitor identities and correlated repeated openings. Do not turn their aggregate outcomes into our estimated field win rate or an initiative estimate.

- **Opening economy:** in 24/29 elimination games the eventual winner ate more pearls before round 30. Two-segment children account for 96.2% of compact-map splits.
- **Delayed expansion also matters:** public Schooltime winners have a median 1.5 pearls before round 30, yet 62.5 dragons at round 100. Our fresh reference tests reached only 16–24 for Hunter v20 and 25–38 for Ouroboros v10. Opponents differ; use this as a diagnostic target, not a controlled comparison.
- **Conversion:** 30/47 round-limit winners have fewer survivors and 18/47 have less total living length. M156381 wins with one length-49 dragon against 35 dragons totaling 413.
- **Both successful endgames exist:** M156381 contracts its army around a crown; M156127 retains 61 units and a length-83 leader. Neither maximal population nor maximal liquidation should be a universal doctrine.
- **Deaths are heterogeneous:** winners have more deaths in 59/76 games. Larger armies, voluntary feeding, profitable trades and trapped replacements all contribute. In M156381, the final leader receives 26 pearls from 12 allied self-collision donors after round 380, each with an immediately legal alternative.
- **Gross food is not new income:** 43.6% of pickups follow corpse spawns, including repeated recycling. Track bed income separately from allied recovery and enemy capture.
- **Crowding changes income:** M156377 has 2,088 body-blocked bed renewals out of 6,902 scheduled renewals. This is a measurable economic cost, not just a collision risk.
- **Conversion can lose to elimination:** M156175 shrinks from 29 units at round 400 to four at 425; a length-five attacker kills its final length-23 dragon at round 470.
- **Banked length can be lost to geometry:** in a fresh local Schooltime game, Ouroboros transfers 49 segments to a child at round 415; the child reaches 52 and dies trapped at 419. The bot still wins, hiding the failure in the aggregate result.

Our major concepts already match the field. Hunter has real production/tactical strengths; Ouroboros and Leviathan v09 already possess feeding, crowns and tail handoffs. Hunter v20 also has late growth logic: the missing capability is coordinated, reliable conversion, not literally “no endgame behavior.”

## Parameterising the problem

Use a common team objective, but distinguish **resource creation, redistribution, information and survival**:

`V ≈ material + future production + controlled food access + useful information + final-length advantage − expected loss`.

The final-length term becomes dominant as the remaining horizon shrinks. Birth value depends on local supply and travel time, not only elapsed round. Information value depends on how much uncertainty remains and whether acting on the discovery can still pay. A sacrifice transfers only part of its body as pearls and has value only through the expected collector and reduced congestion. A crown loss is discontinuous near the end, so a simple per-segment risk price is insufficient on its own.

A practical parameterisation separates **doctrine**, **role weights**, **action options**, and **hard mechanics**:

| Parameter family | Candidate variables | Observable inputs / consumer |
|---|---|---|
| Role allocation | scout fraction/quota; minimum gatherer and hunter force; assignment cooldown; scout retirement coverage/time | Fresh nearby role reports, explored fraction, recent enemy contact → self/child job assignment |
| Exploration | frontier reward; scout food reward; portal incentive; information expiry; scout gossip slots | Known terrain, resource observations, unmatched portals → target and sonar scheduler |
| Regional economy | density reward; local crowd discount; regional unit demand; due-bed occupancy cost | Known beds, local bodies/heads, countdowns → target, split and route scoring |
| Production | split threshold/child size; population target; unit value; role-specific split multiplier; late reserve | Supply/access, current exact friendly population, remaining horizon → split candidate value |
| Banking | bank-start/full-conversion rounds; length threshold; crown preference/hysteresis; beacon freshness | Known friendly lengths and identities, enemy reach, time left → banker/crown state |
| Feeding | donor length cap; crown range; minimum retained force; recipient freshness; enemy exclusion radius; donor scheduling | Direct recipient observation, route/access, local alternatives → donate/approach/keep working |
| Hunting | chase horizon; local numerical margin; strike value; sprint price; late crown target value | Visible threats, recent reports, reachable attack paths → target and action score |
| Survival | continuation depth/node cap; child escape requirement; crown trap penalty; unknown-space treatment | Exact body simulation, terrain, uncertain future occupancy → candidate filter and bounded lookahead |
| Communication | freshness, relay hops, role-specific slot allocation; discovery priority | Four-ray budget and named receiver consumers → packet scheduling |

Keep true mechanics fixed: collision precedes tail movement, sprints cost length, occupied beds fail to spawn, splitting is limited by actual population, and sonar is not authenticated by the engine. Do not “tune” these facts. Keep forecasts explicitly uncertain: stale pearls cannot pay for a sprint, old crown positions cannot justify immediate suicide, and a local enemy count is not a global population estimate.

These parameters interact. Larger armies can improve access but suppress local spawns; earlier banking may lose the expansion race; earlier feeding may expose a lone crown; stronger safety can starve exploration. A collection of role labels is not yet a doctrine. Define how state changes weights, and record those state transitions in experiments.

## Exploration fork: Estuary

Namespace/name: **leviathan-x03-estuary-roles**, Python. Base: leviathan-v09-arrival, itself explicitly derived from ouroboros-v10-beacon. This is separate from Riptide and does not change its code or research agenda.

Hypothesis: **a resource-aware three-job colony, with gradual banking and security-gated feeding, can improve the coupling between exploration, production and endgame survival.** Emphasis is on presently weak areas rather than reproducing every existing tactic: information retirement, the 30–100 growth window, crowding costs, donor discipline and long-body continuation after a handoff.

Reuse the established mechanics, evaluator and arrival model. Put the new doctrine and bounded continuation routines in separate Python modules with explicit toggles. Keep a neutral master switch so a reference behavior comparison is possible. Add only communication that informs an actual decision, and keep per-turn work bounded for the judge.

### Evaluation for this phase

- Compare against the frozen base and active references on compact controls plus Schooltime, Big Empty, Stronghold and Trauma; use both sides.
- Use direct base matches and paired common-opponent fixtures for different questions; never confuse them.
- Record outcome diversity: which fixtures improve or regress relative to v09, not only an overall score.
- Autopsy opening/30–100 growth, crown lengths over time, large-dragon deaths, newborn viability and deliberate feeding. Keep corpus-derived priorities distinct from hypotheses about the new implementation.
- Run narrow feature ablations and at least representative judge CPU checks. A neutral switch should preserve the reference action/sonar stream.
- Do not spend this phase on broad parameter exploitation or promote solely from a small screen. Hand the central model components, counterexamples, bounded measurements and unresolved weaknesses.

The companion [Estuary bot handoff](ESTUARY_BOT_HANDOFF.md) records what was actually implemented, tested and learned. Design intentions above are not claims of successful behavior.

### Implemented result for aggregation

The Python fork now exists. The selected profile retains the adaptive jobs,
regional resource/crowding scores, gradual banking, fresh crown identities and
guarded donations. Its optional continuation planner is disabled after a mixed
ablation: it helped some open-map fixtures but harmed others, particularly
Stronghold. Long-body survival remains an unsolved priority rather than a
delivered guarantee.

Selected Estuary scores **20–4 versus the parent's 23–1** on 24 matched native
reference fixtures, with one new win and four regressions. In eight direct
matches it beats the parent on **both Schooltime sides** and loses on both sides
of Big Empty, Stronghold and Trauma. That supports keeping it for diversity,
not promoting it as the best general bot. The selected judge sample has no
timeouts but reaches **98.8M of 100M CPU points** on Big Empty. The bot handoff
details runtime differences, donor attribution and the remaining gaps.
