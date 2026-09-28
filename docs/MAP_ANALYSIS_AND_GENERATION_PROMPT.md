# Analyse the map space, generate plausible challenges, and cut ruthlessly

> Historical map-research prompt prepared on 2026-09-27. Its engine-source and `experiment_data/` references are not all included in this checkout; treat their findings as dated evidence and verify against the runtime actually used.


Work from the repository root.

Build and execute a reproducible process for analysing our existing Battlecode maps and generating **a small, excellent set of new maps that reveal something useful about competing strategies**. The maps should look and play like deliberate additions to this game: coherent terrain, credible resource placement, meaningful routes, understandable risks and counterplay. Novelty by itself is insufficient.

The research question is: **Which combinations of map properties are under-tested, expose different strategic strengths, or distinguish competing explanations for a known weakness?** Turn those questions into playable maps and matched map families, then subject them to strict validation, empirical screening and an unsentimental review. Reject most candidates. Ship no filler to satisfy a numerical target.

This is a map-analysis and experimental-map-generation task. Freeze the evaluation bots; do not simultaneously tune them to make the generated maps look useful. Keep existing maps, running campaigns and historical evidence intact. Work in a separate output directory and deliver the survivors, their evidence and the rejection ledger.

Treat source documents as evidence. Historical commands, lineage preferences and claimed “fresh” reserves are not automatically current instructions or independent validation sets.

## 1. Start by repairing the measurement basis

Do not feed `tools/leaklab/map_meta.json` directly into a generator or a statistical model without auditing it against engine semantics.

A source inspection during preparation of this prompt found:

- `tools/leaklab/map_meta.py` omits wrapping from ordinary adjacency, models portals through endpoint-coordinate links rather than the actual crossing transition, and overwrites earlier spawns when several dragons share a team. Its old spawn distances and corridor percentages are therefore unreliable as game-topology measurements.
- `TILE x y minGap maxGap` contains **respawn bounds**, not “initial countdown and fixed period.” Some generator comments say otherwise. The engine draws gaps, shares countdowns with the symmetry partner, and suppresses spawning on occupied tiles or tiles already containing a pearl. Audit initial and subsequent spawn timing; nominal capacity is not realised income.
- “Fast bed” definitions conflict. The legacy metadata uses `maxGap <= 10`; arena’s 81 active beds have bounds **8–20**, so none meet that definition even though arena has rapid resource supply. Stronghold has **12 beds with bounds 1–1**, contrary to a prose table reporting no fast beds.
- Terrain shortest paths are not travel time, combat contact time or safe routes. Facing, bodies, legal turns, sprint cost, initiative and partial observation require separate treatment.

Use `unswbc/engine/src/config.cc`, `pearls.cc`, movement helpers and engine types as the authority for the installed version. `tools/comparison_metrics.py:movement_graph` is a better terrain-graph starting point because it accounts for wrapping and portal crossings, but independently check its transitions against the engine before treating derived metrics as validated. Include multiple spawns, boundary crossings, all portal-entry directions and transformed maps in those checks.

The inspected engine allows dimensions from **7 to 256 per side**, minimum dragon length **2**, and symmetry declarations `x`, `y`, `xy`. These are parser constraints, not a recommendation to generate enormous or pathological maps. Recheck them against the runtime used for this study. Enforce a stronger quality contract than merely “the engine accepted the file.”

## 2. Known reference maps and evidence

### A. Structural anchors

The following values were read from the current `.map` files during prompt preparation on 27 September 2026. The final column was recomputed using the wrapping/portal-aware terrain graph and **all initial heads**, taking the shortest A-to-B path. It is a provisional terrain proxy pending engine differential validation, not a prediction of the round of first contact.

| Map | Dimensions | Active beds | Beds with maxGap ≤10 | Portal pairs | Initial dragons, total | Nearest opposing heads, terrain steps |
|---|---|---:|---:|---:|---:|---:|
| arena | 11×11 | 81 | 0 | 0 | 2 | 4 |
| default_small | 16×16 | 256 | 0 | 0 | 4 | 20 |
| Colosseum | 16×16 | 256 | 0 | 4 | 2 | 2 |
| devil | 32×16 | 174 | 18 | 0 | 6 | 31 |
| dilemma | 32×16 | 88 | 12 | 4 | 6 | 14 |
| trophy | 25×25 | 625 | 0 | 1 | 4 | 9 |
| queen_of_spades | 25×35 | 442 | 0 | 2 | 4 | 24 |
| autarky | 54×18 | 188 | 14 | 8 | 12 | 7 |
| default | 32×32 | 1,024 | 0 | 12 | 8 | 2 |
| stronghold | 48×24 | 210 | 12 | 4 | 4 | 152 |
| trauma | 48×24 | 142 | 12 | 6 | 4 | 98 |
| schooltime | 60×40 | 326 | 0 | 12 | 6 | 7 |
| big_empty | 64×64 | 4,096 | 0 | 0 | 6 | 40 |

For example, big_empty uses bounds **1–750**, not a fixed 750-round period; most stronghold beds use **1–200**, alongside its 12 every-round beds. Arena has few dimensions but immediate contact; schooltime is large yet has short portal-aware paths between some spawns. Avoid equating area with openness, distance, resource abundance or time to combat.

The provisional graph also finds tiles unreachable from A’s initial heads in queen_of_spades, schooltime and trauma. Investigate the components and their relevance before assigning a defect: decorative/inaccessible regions and disconnected play-critical regions are different cases. Existing maps are examples to understand, not proof that every characteristic is desirable.

### B. Statistical and experimental anchors

Use these as scoped evidence, with exact records refreshed before new conclusions:

- The audited replay study found round-100 behavior improved held-out log loss **0.474 → 0.359** over **7,762 games**, with **0.347** after adding material state. Population growth and resource throughput carry substantial signal, but are observational and correlated. Cap timing alone added about **0.00145**, versus **0.1044** for the population family. A cap-rush arena is not automatically a valuable test.
- Holding stronghold out entirely made the behavior model worse by about **0.140 log-loss units**. This motivates genuinely new map-family tests, not another shuffled game split on familiar maps.
- Leaklab reports sharp matchup reversals: compact resource/contact specialists such as Ouroboros/Tew expose Sinbad/Serre production weaknesses, while Sinbad/Serre can reverse the result on portal or open-economy maps. One devil fixture recorded **197 versus 1,509 pearls** and **72 versus 522 splits**. Those are mechanism clues from particular fixtures, not typical effects established across all maps.
- Valjean’s portal-risk memory addressed dragons stuck in portal boxes; its reported dilemma/autarky result improved **3–21 → 14–10**. Sinbad’s reduced dive incentive improved its portal-map record **36–20 → 45–11**. New maps should distinguish paralysis, useful exploration and reckless commitment.
- Sinbad’s reported performance against one opponent fell from roughly **75% on originals to 50% on flipped maps**. Check orientation robustness without treating reflections as independent map families or assuming all divergence is a bug.
- The strategy atlas placed **179 of 206 source identities** using **14,513 replays**, across opening, expansion, midgame and conversion. Its 50–100 expansion partition failed the majority-label baseline; cluster identities are provisional and stage-specific. Among stronger bots, late groups exhibited a trade-off between total-material retention and longest-dragon advantage. These are useful axes for map design, not causal proof or known optimal phase schedules.
- Fafnir improved its reported gauntlet **134–48 → 140–42**, but its 16-game reserve was identical to the baseline because the changed mechanisms never activated. That reserve did not demonstrate the intended benefit and missed its stated promotion gate. **A map’s description is not evidence that it exercises its advertised mechanism.**

There are many games but only a small number of established base maps. The effective sample size for a claim about a map property is not the number of team-turns or all games played on that map. Related transforms and generated siblings share ancestry. The existing pool also has selective schedules and replay retention; it is not a random sample of competition maps or strategies.

## 3. Build a useful map feature model

Inventory official/reference maps, generated reserves, transformed maps and their exposure history. Record source hash, semantic identity, ancestry, generator version/seed and known selection history. Never label a previously inspected reserve “fresh.”

Build a documented feature table with three distinct layers:

| Layer | Candidate descriptors |
|---|---|
| Static geometry | Area/aspect ratio; legal symmetry; initial team count/length/facing; wrapping-aware components; all-spawn distance distributions; articulation/bottleneck structure; route redundancy; corridor widths and lengths; room/pocket sizes; portal shortcut value and dependence; alternative routes around contested exits. |
| Resource opportunity | Active-bed density; full min/max-gap distribution; explicit ≤1/≤10/≤30 summaries; clusters and concentration; near-spawn versus shared supply; arrival-time accessibility by side; resource-weighted bottlenecks; time-dependent availability; initial scarcity; nominal supply versus plausible harvesting capacity. |
| Observed gameplay | Time to first resource/contact; early harvest and splitting; activation/rejection of relevant actions; collector/newborn survival; bed blocking and corpse flows; congestion; portal hesitation/dive deaths; absolute crown growth and survival; elimination timing; round-limit conversion; runtime cost. |

Add information-demand descriptors where justified: portal exits outside initial vision, hidden resource basins, route ambiguity, value of remembered observations and useful communication distance. A visual motif is not an information challenge unless it changes available knowledge or decisions.

Use continuous descriptors and a few predeclared interactions instead of mutually exclusive labels such as “big,” “compact” and “portal.” Measure overlapping conditions: for example renewable supply × contact pressure, corridor capacity × population, portal benefit × exit uncertainty, and distributed income × conversion distance.

Do not put observed match outcomes or full-game features into a supposedly static map descriptor. Keep latent opportunity, actual policy use and eventual success separate. Estimate resource supply over relevant horizons using the engine’s timing semantics; do not substitute the mean upper gap bound for supply.

Fit interpretable, regularised models first. Compare strength/map/side baselines with approach-by-map-feature interactions. Examine whether the same feature contrast recurs across different opponents, map families and bot implementations. Report uncertainty, sparse support and alternative explanations. Do not fit dozens of map effects to thirteen layouts and claim discovery from thousands of repeated matches.

Validate by holding out complete map families and, separately, opponent approaches. Keep all transformations and siblings together. For predictive claims, fit ratings, preprocessing and feature selection inside the outer split. Mark model extrapolation explicitly. Use historical correlations to choose experiments; use controlled map variants to test them.

## 4. Generate hypotheses and families, not random noise

First write a short candidate specification: target mechanism, competing predictions, intended challenge, plausible geometry, controlled variables, expected activation evidence, and a reason an existing map cannot already answer the question.

Build a parameterised grammar of understandable motifs—resource basins, contested lanes, porous partitions, pockets, rings, flanking routes and portal shortcuts. Compose a small number coherently. Generate seed variants within a motif family and controlled sibling pairs that change one main axis while holding others approximately fixed. Remeasure the result: changing a wall or portal can alter several properties simultaneously.

Initial families worth considering:

1. **Renewable commons:** matched total supply, centralised versus distributed access; contestability and route capacity varied separately. Tests production under contact without simply giving one side more food.
2. **Safe detour versus valuable shortcut:** a portal offers real travel benefit, an alternative route exists, and exit visibility/congestion varies. Tests calibrated information and commitment rather than unconditional portal use.
3. **Productive pockets:** useful resource rooms with controlled exits and escape/reproduction opportunities. Distinguishes productive pocket farming from unavoidable self-traps; avoids assuming all dead ends are bad.
4. **Long-game conversion:** enough viable income and room to build material, but varying costs of aggregating it near a crown. Tests resource distribution, protection and rounds 400–500, rather than merely starving all bots.
5. **Scale/contact decoupling:** large maps with short meaningful contact routes, and smaller maps with separated basins and credible reconnection. Tests whether policies mistake area for tactical conditions.
6. **Interaction crossings:** compact renewable supply with optional portals; spacious layouts with scarce contested bottlenecks. Tests whether combined doctrines work when the old map classes overlap.

Treat this list as starting hypotheses, not a requirement to force every family into the final set. Include interior variations around the reference distribution and selected plausible gaps between known regimes. Keep extreme adversarial stress maps in a separately labelled collection; do not quietly mix them into a representative evaluation suite.

Keep rule parameters such as round limit and unit cap fixed initially. Rule mutations answer different questions from terrain/resource changes. If later useful, isolate them in a separate experiment.

“Plausible” means a human can explain the map’s structure and choices without knowing which bot wins. Require a readable visual hierarchy, coherent resource placement, intentional portal relationships, credible movement options and meaningful opportunity to respond. Symmetric pixel noise, gratuitous chokepoints, inaccessible rewards, decoration without gameplay purpose and maps tailored to a bot’s exact thresholds are poor default candidates. Symmetry must preserve the relevant terrain, resources, bodies, facing and portal relationships, not merely the picture.

## 5. Use a strict rejection pipeline

A reasonable initial funnel is **128 cheap candidates → at most 24 structural/visual survivors → at most 12 gameplay-screened candidates → roughly 6–8 final maps**. These are budget ceilings and a curation ambition, not statistical thresholds or quotas. Generate more only when it addresses a documented coverage gap. Returning fewer excellent maps is preferable to lowering the bar.

Freeze the rubric before observing screening results. Maintain a rejection code and short reason for every cut. A score cannot override a hard failure.

### Gate 1 — Engine correctness: zero tolerance

Reject invalid format/counts, unsupported dimensions, malformed or overwritten portals, illegal body chains, overlaps, broken declared symmetry, invalid resource ranges, and generator nondeterminism. Test the engine load and actual legal initial moves. A terrain path is insufficient if no initial dragon can legally follow any viable opening.

Check both teams, all initial dragons, wrapping and portal boundaries. Distinguish a tough but playable opening from forced death or effective immobilisation before a meaningful decision. Detect accidentally isolated play-critical regions and resource schedules that never deliver their advertised opportunity within the game. Preserve explicitly justified special cases as labelled diagnostics, not silently as normal maps.

### Gate 2 — Plausibility and distinctness: cut before expensive games

Render every survivor with spawns, body orientation, resources, walls and clearly paired portals. Run a critic pass against the frozen rubric, separately from the generation rationale. Judge the visible map before being told which bot it favours.

Reject arbitrary clutter, incoherent resource layouts, accidental dominant routes, meaningless portals, copied maps with cosmetic edits, and candidates whose novelty is solely a name, rotation, reflection or portal-ID relabelling. Check semantic similarity and ancestry, not only file hashes. Keep useful matched controls explicitly labelled; they are not independent discoveries.

Do not require every legal tile to be reachable simply because it is easy to measure. Require the unreachable regions to be intentional and compatible with the map’s purpose. Conversely, do not excuse a broken map merely because a reference map has a superficially similar feature.

### Gate 3 — Gameplay credibility and mechanism activation

Use a frozen panel of competitive, behaviorally distinct bots plus relevant specialist probes. Start with a small set of informative matched pairs and both starting sides, expanding only for a concrete unresolved question. Reuse source-identical controls. Do not spend the budget on a full round robin for every candidate.

Before interpreting W/L, verify that the advertised challenge actually occurs: a resource contest is contested; portal memory receives decisions it can affect; split admission is binding; the conversion test reaches a meaningful late position. Read representative early, middle and terminal replay frames and the decision diagnostics where available.

Reject or quarantine accidental spawn lottery, pathology-driven results, crashes mistaken for strategic separation, inability to exercise the target mechanism, and maps producing an uninformative repetition of an existing matchup profile. Short games are not automatically bad—arena is a legitimate early contest. The question is whether decisions and counterplay matter.

Balance means comparable opportunity, not forcing every matchup to 50:50. Test geometric bias using side swaps, transformations and appropriate controls; account for the engine’s initiative and dragon-ID order. Self-play alone cannot certify fairness. Define practical bias tolerances before results; label uncertainty when evidence is too sparse to decide. Never reject a map merely because our favourite bot loses.

### Gate 4 — Robustness and scientific value

Advance candidates only when their intended behavior or information value survives additional relevant opponents and plausible sibling layouts. Distinguish a stable mechanism from a single deterministic upset. Test whether a small coordinate or resource perturbation destroys the purported explanation.

A narrow regression fixture may still be worth retaining, but label it as such. It does not earn a place in the general challenge suite by being dramatic. A good diagnostic map need not reverse the ranking: it can reveal a missing condition, disprove a hypothesis, test a boundary or cover a genuinely unmeasured regime.

For the final critic pass, use this proposed curation score, recording evidence for each item:

| Dimension | Weight |
|---|---:|
| Plausibility and coherent choices | 25 |
| Mechanism activation and diagnostic clarity | 25 |
| Marginal coverage or information beyond retained maps | 20 |
| Fair opportunity and robustness | 20 |
| Observability, reproducibility and affordable evaluation | 10 |

Default acceptance: **at least 80/100**, with **at least 4/5 for plausibility and fairness/robustness**, no dimension below 3/5, and no unresolved hard failure. These are explicit editorial rules, not calibrated probabilities. Do not retroactively lower them. Reject redundant candidates even if each is individually good; retain the smallest set that covers the justified questions. Allow at most one planned revision per rejected design before cutting it or returning it as a clearly new candidate with a new hypothesis.

## 6. Protect the experiment from selection bias

Generated maps selected because they expose a known bot are a **diagnostic challenge suite**, not an unbiased estimate of leaderboard strength. Keep diagnostic results, an independently weighted general evaluation panel, and untouched confirmation maps separate.

Select the screening roster for distinct relevant mechanisms, not just familiar names or a single scalar rank. Include current Sinbad/Serre/Fafnir, Valjean/Von Neumann/Porthos, compact production specialists and supported endgame/information specialists as appropriate; verify exact versions and aliases. Hold back some relevant approaches from generator feedback.

A genuinely untouched reserve may receive structural validation and visual review before outcomes are read. Freeze its hashes, families, seeds, roster and decision rules. Once gameplay outcomes are used to accept, reject or revise a map, that map belongs to discovery/validation, not the untouched reserve. A structurally vetted, unplayed reserve must be labelled **play behavior unverified**, not “proven fair and informative.”

Reserve different layouts and preferably different motif families, not only more seeds from the exact template that was optimised. Group transformations and near-clones when reporting uncertainty. Record generator seed separately from game RNG/seed and engine version; repeating a deterministic fixture does not supply fresh evidence. Map transforms may also change random resource realisations, so verify what is preserved.

Report support and uncertainty for each conclusion. Use selection-aware language and fresh confirmation for claims discovered through many candidate searches. Do not use a noisy learned simulator as the final judge of either fairness or novelty; verify its predictions in actual games.

## 7. Required outputs

Save a reproducible batch under `experiment_data/map_discovery_<timestamp>/`. Deliver:

1. **Measurement audit:** corrected feature definitions, engine/version assumptions, discrepancies in old metadata, and transition/timing validation evidence.
2. **Reference atlas:** feature table, coverage/missingness, map-family relationships, clear renderings and conditional strategy-performance comparisons.
3. **Generator and manifest:** parameterised families, seeds, hashes, ancestry, intended interventions, controlled variables and generation constraints.
4. **Candidate review ledger:** every candidate, gate outcomes, scores, revision history, hard rejection reasons, costs and confidence. Preserve rejected evidence; do not distribute rejected maps as accepted outputs.
5. **Curated playable maps:** actual `.map` files, matched controls where useful, previews, validation logs and reproducible match manifests. For each, provide a short map card: purpose, why it seems plausible, nearest existing analogue, meaningful difference, target mechanism, activation evidence, outcome profile, counterplay, limitations and reason it survived the cuts.
6. **A compact final report:** which maps earned inclusion, what they teach us, what remains unresolved, which claims failed, and which reserve maps are genuinely untouched. Keep adversarial stress maps and narrow regression fixtures separately labelled.

The final set should be easy to inspect and hard to excuse. If a survivor cannot defend its legality, plausibility, fairness, distinctive purpose and evidence, cut it. If nothing survives, report that honestly and identify which measurement or generation assumption failed.

Use existing parsers, renderers, game ledgers and runners where suitable. Coordinate with ongoing campaigns; avoid duplicate work and unbounded game batches. Keep historical manifests and results immutable. Save a second copy of the final report/manifest outside the working repository because earlier chat deliverables disappeared during repository changes.

## Source and implementation entry points

- [Map files](../maps/): authoritative current layouts; freeze hashes before analysis.
- Legacy map metadata code (`../tools/leaklab/map_meta.py`) and saved metadata (`../tools/leaklab/map_meta.json`): audit targets, not trusted ground truth.
- Engine map reader (`../unswbc/engine/src/config.cc`), resource timing (`../unswbc/engine/src/pearls.cc`), engine constants (`../unswbc/engine/include/engine/types.h`).
- [Replay/terrain metrics](../tools/comparison_metrics.py) and [map parser/ASCII view](../tools/ouroboros/mapview.py): reusable starting points with the limitations above.
- [Leaklab findings](leaklab-findings.md), [Sinbad handoff](handoffs/sinbad-handoff.txt), [Valjean handoff](handoffs/valjean-handoff.txt), [Fafnir record](../bots/fafnir-v01-phalanx/README.md).
- Audited replay statistics (`../experiment_data/replay_analysis_20260926_evidence/REPORT.md`), strategy atlas (`../experiment_data/strategy_discovery_20260926/REPORT.md`), stage-value analysis (`../experiment_data/strategy_discovery_20260926/stage_value/REPORT.md`).
- [Existing reserve generator](../tools/serre/make_reserve.py) and [freeze manifest](../tools/serre/reserve_frozen.json): examples to audit; do not overwrite or treat their consumed outcomes as new reserves.
- Outcome/provenance sources: `game_stats/runs/`, `game_stats/sources/`, `experiment_data/benchmark-current.json`, `experiment_data/bot-ratings/` and lineage-specific frozen experiment records.
