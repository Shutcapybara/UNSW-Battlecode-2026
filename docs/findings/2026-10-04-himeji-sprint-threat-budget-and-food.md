# Himeji unit30 — verified sprint strikes and food-aware threat reach

4 October2026. **Kanazawa's20 distance-selected own-queen deaths are confirmed enemy multi-step attacks. Four exceed the attacker's food-free movement budget through meals along the route.** A length3 attacker in game869494 eats three corpse pearls and reaches the queen five steps away. This supports a new threat-feature hypothesis; it does not establish avoidability, deliberate queen targeting, or a live ranked loss rate.

## Event verification and population

Source Kanazawa c7369c1a1, unit11 `q_h2h.py` and committed raw rows. Selected all24 `kdist>=2 && kdied` cases:20 own queens plus4 opponent queens,23 unique games. Read existing replays only;23 payload hashes, full map-text hashes and official winners agree with frozen metadata. Exact attacker TurnStart reconstructed from raw events; no future round snapshot used for these attack states. In all24 cases the killer is the acting enemy, the command is a multistep move, shortest terrain distance at its TurnStart equals command length, and the replay contains command-length−1 successful head updates before the fatal head collision. This confirms the attack primitive, not just a distance proxy.

| Selected population | Cases / series | Mode | Command lengths | Beyond food-free budget |
|---|---:|---|---|---:|
|Our original queen, verified14585|20 /12|2 ranked,18 unranked|14×2,3×3,1×4,2×5|4|
|Opponent queen in team7 games|4 /4|2 ranked,2 unranked|4×2|0|

These cases come from the same consumed96-game mixed-mode sample; they are not independent replication or a matched top-ten comparison. Full per-case map hashes, sides, identities, events, source peer rows and series are committed. Unknown opponent submissions remain unknown. Our20 cases span10 maps and r14–210. The comparison20/43 versus4/36 is conditional on queen h2h death and mixed populations, not a per-exposure targeting rate. No confidence interval or stable field target is claimed for that selected mechanism census.

## Movement budget checked in isolated1.2.3

For a food-free unobstructed route, the budget is

`B(L) = ceil(L/4) + L − 2`.

Twelve fixed-action open-path checks at B and B+1, followed by18 collision checks at target distances B/B+1/B+2, use Himeji's isolated unswbc1.2.3 engine. No repository bot, arm, tournament or policy was built. All cases are deterministic mechanics checks, not independent performance trials. Engine hash and replay/map hashes are in the receipts; replay payloads remain scratch only.

| Initial length | Free steps | B: verified food-free reach | B+1 and B+2 collision attempts |
|---:|---:|---:|---|
|2|1|1|invalid before target|
|3|1|2|invalid before target|
|4|1|3|invalid before target|
|5|2|5|invalid before target|
|6|2|6|invalid before target|
|9|3|10|invalid before target|

At B, the open-path actor reaches its next turn at length2 and the collision fixture kills both heads. There is **no extra fatal step beyond B** in the no-food controls. A proposed distance≥enemy-length rule is unsafe at L5/6/9: L5 can hit at5 and L9 at10. Even distance>B is only a no-food bound. Real paths must account for meals, portals, occupancy, turn order and observations. A terrain-distance lower bound does not prove an executable path exists; conversely the presence of a blocking body is not a persistent shield without an event-time/path check.

| Live replay / round | Attacker length | B | Commanded steps | Meals before collision |
|---|---:|---:|---:|---|
|869494 /14, Prisoners Dilemma|3|2|5|3 corpse pearls:2 ally,1 enemy|
|881387 /26, Default|3|2|3|1 pearl|
|857671 /118, Around UNSW|3|2|3|1 pearl|
|869498 /180, Trauma|4|3|4|1 pearl|

For869494 the attacker starts(19,6), the queen(16,4); command N,N,W,W,W. It consumes at(19,5),(18,4),(17,4), then hits the queen. Exact head updates verify the first four steps. This is an observed food-supported route, not a counterfactual replay proving that removing one pearl would save the queen. The three other over-budget attacks also have recorded meals; all four are retained individually rather than pooled into a new incidence target.

## New hypothesis and guidance

**H-H8, proposed ledgerL24/L49, weight0.4: path food changes the enemy reach relevant to queen safety.** A queen-threat feature that accounts for observable food along enemy candidate routes should detect attacks missed by a distance/current-length threshold. This refines Kanazawa H-KZ26; it does not replace its owned next-unit avoidability/visibility pass. Keep H-H6.5 and H-H7.4 unchanged.

First test on an independent later sample of at least60 eligible enemy/queen encounters with both attacks and non-attacks, not60 selected deaths. Match or stratify map hash, mode, seat, phase, enemy size, time/order, visible food and opponent; hold out whole series. Sixty is a coverage/variance pilot, not a guarantee of statistical resolution. Compare food-blind versus food-aware features on the same encounters, include empty-route and inaccessible-food controls, and record unknown/stale information. The falsifier is an adequately precise absence of additional threat detection/calibration on food-exposed cases, or a tester's qualified arm losing overall wins/food without reducing the targeted deaths; a wide or unexposed null is inconclusive.

If Kanazawa's hold clears and an assigned tester chooses this mechanism, use carthage05/liveM2 with parent0 and at least two predeclared nonzero doses of the **same** threat penalty, for example penalty multipliers0/1/2. Keep route/food prediction fixed across doses; do not mix different reach definitions as doses. Expected sign: fewer food-supported queen strikes, possible food/territory cost from retreat. Report all-cause queen deaths, food, units/total/longest, joint and reached queen survival and official wins. A selected dose needs the held-out D-042 gate; prior10pp paired-win planning149/306/463 pairs at discordance.2/.4/.6 is before series clustering, so estimate design effects from the pilot. Suitable analysts Kanazawa/Himeji; tester Rome/Seoul when assigned. No new arm requested or launched here.

The attacker's dead head is evidence of a mutual exchange, not evidence it identified the queen. H-KZ27 targeting needs exposure-matched short non-queen controls, including food on the approach path and action order. Its stated rate ratio must have an interval; death-selected counts cannot establish intent or hidden active-bot switching. H-H2 remains unresolved.

## Readings and disagreements retained

- **Kanazawa H-KZ24:** accept the frozen sample decision11/43<1/3 as its preregistered downgrade, not population falsification. A descriptive whole-series bootstrap over22 series,4000 resamples/seed3030 gives95%8.9–45.7%, including1/3; only6/43 cases are ranked. The approximation to alternative legality remains. H29 contract corrections acknowledged; a continued “15/30 ceiling” is still disputed for the reasons in H29. Exact event-time entry audit remains Kanazawa-owned.
- **Chongqing9f2b15829 C7 clusters:** structural signatures can be useful descriptive groups, but sharing a cluster does not permit pooling old/new hashes. Keep per-map-era references. Behavioural clusters fitted to termination/win-related outcomes are exploratory; freeze weights on a separate window before use. **Reject the proposed class-A queen exemptions under D-043.** FrozenH20 already contains an Autarky queen-decided loss (1/2 own losses), and its field reached490 counts are nonzero on Default, Devil, QoS and Tower Defense. Low observed RL share is not zero relevance, and an intervention can change reach. All-map official-win guards stay in force.
- C7's Schooltime11/16 and13/16 are *joint* queen survival, while its field0.86 is conditional on RL; do not read their difference as a target gap. Candidate reached survival is11/12 and13/13, still a local panel, not a matched live cohort. The cage package's complete r250 cost cannot be assigned to E without C+D/E0; H29's attribution qualification stands. Cause-inclusive deaths and off-Schooltime side effects still need reading.
- C7 entry rates are useful mediator endpoints, **alongside** deaths/wins. Equal enclosure among already-dead queens cannot by itself prove entry rate is the difference; that conditions on the outcome. Observe at-risk entries/queen turns, subsequent escape and cause-specific/all-cause death. C7's31–42% corpse figures remain gross-flow quantities pending Shenzhen's accepted same-birth-cohort correction.
- Rome cursor22 reports corrected dose0 golden parity and a diagnostic smoke check, with corrected seed1 M2 pool starting on the tester host. That supports parent parity/log availability, not a result or D-042 gate. Earlier k5 remains under its earlier feature specification. No new completed tester outcome at this unit's wake. At close, cursor23 reports464 failed gen launches with no replays from an executable labelled1.0.0; agree these are missing games, not losses or valid1.2.3 evidence. Rome is retrying into a clean directory with explicit1.2.3. Require runtime/provenance receipts and official outcomes before scoring.

## Reproduction and freshness

`tools/himeji/sprint_strike_audit.py` takes main repo, frozen index, committed selected.json and an output file; `sprint_food_extension.py --audit-dir <output-directory>` verifies the over-budget meals. `sprint_budget_check.py` and `sprint_collision_check.py` take `--repo <main> --out <scratch>` and **must run only with** `/Users/alik/Documents/Codex/2026-10-01/p2-a-analyst-one-claude-opus/work/himeji-venv/bin/python` (asserts1.2.3). Main analysis Python is used only for read-only decoding. `summarize_sprint_strikes.py tools/himeji/unit30_audit --out /tmp/himeji-strike-summary.json` reproduces summary/assertions without decoding. `h2h_bar_interval.py --peer tools/himeji/unit30_audit/peer-q_h2h.txt --index <frozen-or-current-index> --out <scratch>` reproduces the diagnostic interval. Full source/data receipts in unit30_audit; no corpus/store/main writes or replay payload commits.

Freeze08:24:06Z:122497 corpus games,+440/0own,latest own06:35:02Z. Collector35400 healthy40downloads/latest completed pass,zero errors; ownwatch absent and source6bb33fd7 unchanged. H26 integration/backfill request still pending without another identical census. Read-only immutable/query-only DB checkpoint08:17:57Z:14585 active,14265 idle,1169series, WALexcluded. Ladder081820Z and full hashes in manifest. Own31/62+1110queue/historical754 unchanged; shared51396 peer-reported, not certified here.

Sources own06faf0614/main21186bf24 unchanged/separate, newKZc7369c1a1/CQ9f2b15829; SZ93a34815a/Seoulff8fac943/Romeb926cdf64/Naraa884062ea and older lanes unchanged. Protocol, board/TARGETS/status changes read. KZ08:35 label was available08:22; commit cursor governs chronology. One replay worker plus brief isolated fixtures, all complete; direct actionable evidence delivered to active Rome without an extra-run request. Half-hour automation unchanged.

## D-044 learning translation

- **Observation:** observed enemy head/body/length, candidate path food provenance/availability, terrain/portals, action order, queen identity and unknown/stale flags. Keep future meals and the eventual victim/kill outcome out of inputs.
- **Action:** candidate-specific retreat, route or shielding choice under a fixed food-aware threat estimate; penalty strength is the dose. Do not assume a currently present ally body is a guaranteed shield.
- **Value/reward:** official team win, all-cause queen survival and preserved longest/total, with food/territory costs. Detecting more theoretical threats is not itself a win reward; record false alarms and lost productive actions.
- **Demonstration/exploration:**24 attacks validate the primitive and4 meal-supported extensions; they do not demonstrate safe alternatives. Add non-attacked exposed controls and later held-out series; use fixed-action budget checks as mechanics controls. No policy or model built.
