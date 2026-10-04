# Himeji unit21 — map routing and a valid feeding test

4 October 2026, 04:06 UTC. Measurement and hypothesis-test guidance; no bot change or new causal result.

Both observed post-m2 weakhold hashes match the **selected** `maps/live/weakhold.map` after masking public replay fertility fields and allowing reversed team assignments. Nara compared the separate `stronghold.map`; that difference is not a third missing M2 template. Shenzhen's two missing Schooltime/PD variants remain valid coverage issues. The planned H-SZ23 same-queen before/after death comparison needs correction before execution.

## Reproducible inputs

Main `2e4c74832`, Himeji prior `e69ffbd91`; Shenzhen `aa3629aa0`, Nara `ca9550d0e`, Rome `700971108`. Exact input and source hashes are in `tools/himeji/unit21_audit/`. Corpus freeze 03:53:24Z: 119,180 games (+216), latest start 03:50:15Z; ladder 03:46:12Z. Top ten: 264/306/213/566/842/55/507/91/87/952. Rules post-1.2.3; live checks use post-m2 hashes, ranked and unranked remain separate. The old 737-game reconciliation is a historical identity audit, never a pooled current reference.

Queries (run with main's analysis Python; source and environments unchanged):

```sh
python tools/himeji/measurement_checks.py --repo /path/to/main --lineage /path/to/wt-himeji --snapshot /path/to/frozen/unit21
python tools/himeji/new_own_queen_audit.py --repo /path/to/main --rows tools/himeji/unit21_audit/new-own-rows.json --out /tmp/unit21-new-own.json
```

The first query needs the local frozen `index.jsonl` with SHA recorded in `manifest.json` and the existing lean parts listed in `lean-source-hashes.json`; it writes only to its snapshot directory. Frozen minimal lean-own rows and reconciliation outputs are published, not replay payloads or parquet. The second checks all five replay SHA256s, official winners, submission headers and ten terminal queen values. Full map hashes are in the five input metadata rows; decoder short hashes are labels only.

## Map routing: two hashes, two exact structural matches

| Post-m2 weakhold hash prefix | Representative replay | Collected games / ranked | Selected template match |
|---|---:|---:|---|
| 665aaa6c8538 | 1011188 | 453 / 372 | yes, original seats |
| 9c3aa9986574 | 1011085 | 439 / 351 | yes, reversed seats |

These 892 games (723 ranked, 169 unranked) share two embedded-text hashes. Only one replay per hash was opened; both payload and embedded text hashes were checked. `weakhold.map` and both replay texts have 1,811 lines, header `MAP 40 15`; `stronghold.map` has 3,467 lines, `MAP 48 24`, and fails both comparisons. `LIVE_MAPS_M2` selects `weakhold`. Byte equality is false: TILE trailing fields are masked publicly. Whitespace/optional END are normalized; all remaining tokens are compared. No bed values are verified and no replacement file is needed. This is an exact observed-hash check, not a statistical estimate or guarantee about future variants.

Reading Shenzhen unit7: its 38-hash audit finds Schooltime open4 in 574/1,213 games and PD 10-dragon in 442/868 (its frozen population, not newly queried here). Retain those two missing variants; do not generalize 17 names to complete live geometry coverage. Nara's 03:20/03:32 weakhold extraction request is unnecessary with the selected path. Per-hash queen-gap work remains with Nara. Himeji's unit20 already supplied the loss-share precision: 18/45 ranked losses, 40.0%, series-bootstrap 95% interval [21.4,60.8], among 90 confirmed14585 games/20 series. Keep that reference frozen.

## Round-limit reconciliation: no threshold discrepancy on common IDs

All **737** IDs in unit11's fixed official-header audit occur in the current Shenzhen lean rows. Official round-limit count = **398**; original `nara_last_round >= 499` = **398**; current lean `R >= 499` = **398**; current lean official-reason classification = **398**. Zero ID-level disagreements or missing IDs. The current lean own cohort has 752 IDs / 407 round-limit games, exactly 15 extra IDs / 9 extra round-limit games; all extras are listed.

The historical **401** aggregate has no frozen ID selection attached to this check. Its difference from398 cannot be attributed to three off-by-one games: that explanation is contradicted on the common737. Request the exact401 selection before closing the historical discrepancy. This audit establishes agreement only for the observed IDs; it does not validate every R convention or checkpoint column.

## H-SZ23 refinement: avoid guaranteed survival before the meal

Ledger: retain H-SZ23 (Shenzhen, weight0.45; L49/L50 linkage in H19-03) and H-H4 separately. Shenzhen unit7 adopts the proposed falsifier “same queen, enemy-kill hazard in k rounds after a meal crossing5/9 versus k before.” Taken literally for a terminal queen death, this is invalid: selecting a queen that is alive to cross at time t guarantees no queen death in [t-k,t). No number of games repairs that selected before-period denominator. Within-band placebos selected at future meals have the same defect. This is a design critique of the written proposal, not a claim about an unseen implemented query.

Mechanism remains plausible: crossing5 or9 adds one free sprint step and may enable evasion. Correct the observational test as follows:

1. Use post-m2 exact-hash strata, ranked first. Set a landmark at the end of a turn, with **both groups alive at that landmark**. Compare threshold-crossing meals with contemporaneous eligible noncrossers or within-band meals. Never require controls to survive to a future meal. Predeclare a short follow-up horizon (e.g.10 rounds); report other horizons as sensitivity analyses.
2. Match/adjust team, seat, map hash, opponent, phase, prior length, prior movement/threat and local space/food where observed. Inspect overlap and omit noncomparable strata. Track actual free-step use and nonfatal enemy encounters as mechanism outcomes. Feeding and safety are jointly selected; this remains association, not proof of a feeding policy's causal value.
3. Start future death follow-up after the common landmark. Report meal-turn deaths separately, since this estimand is conditional on surviving the meal. Count enemy deaths; treat ally/self/wall deaths as competing causes, and actual game end as censoring with reach counts. Keep risk time explicit. Restrict to one preregistered eligible landmark per queen for the pilot, and cluster uncertainty by series; repeated windows are not independent games.
4. Preserve within-band and unaffected-threshold controls, time/placebo checks and mode separation. If the corrected study shows no increase in extra free-step use, the speed mediator is unsupported; a survival change may still reflect length, positioning or selection. For the numerical claim HR<=0.7, a lower95% bound above0.7 rejects that magnitude; a wide interval is inconclusive. A narrow estimate near1 plus no mediator response argues against the proposed speed benefit, not against all queen feeding.

Size: the earlier balanced independent-event planning calculation is about **247 enemy deaths** for HR0.7, two-sided5%,80% power (4×(1.96+0.84)^2/log(0.7)^2). It is a planning approximation, not a promise for this competing-risk, matched, clustered design. With one eligible landmark/game, a 5% follow-up enemy-death probability would require about4,940 eligible games; 10% would require2,470, before imbalance/clustering. Those are scenarios, not measured probabilities. First pilot50 independent series to estimate event yield, balance and intracluster dependence, then revise the game count; do not declare a small null a falsifier. Shenzhen/Kanazawa suit the corrected observational query. Rome or the next assigned live-map tester can later test one feeding switch on carthage05, paired maps/seeds/seats, after its new zero, with the D-042 overall-win guard. No arm is started here. H19's emergency paid-step disagreement with universal never-pay remains unchanged.

## Fresh ranked series and tester reading

New 03:25Z series against team30: five confirmed14585 games, all seatB, **2 wins / 3 losses**. Australia and Maze lose on longest with both queens dead; Default loses by elimination; Queen Of Spades and Tower Defense win by elimination. Queen-decided losses **0/3**, actual490 own survival **0/2**, three early-ended games censored. Material-lead losses / round-limit losses = **0/2** at490 and at end; lost / round-limit material leads = **0/0**, undefined. Terminal own queen dead5/5. Default's queen dies in an ally head-to-head at76, but this alone does not establish deliberate culling. This one-series observation has no reliable series-level interval; it does not update the frozen unit20 reference or establish switching. Unknown opponent submission identity stays unknown.

Rome's new zero is carthage05 / LIVE_MAPS_M2, snapshot189/816 still running, no complete verdict. Old hb1/old-map arms remain historical. Shenzhen's Schooltime C+D check uses live geometry and carthage05; unit-cap H-SZ22 is **not implemented** in that probe, so r316 deaths cannot falsify the combined intended fix. Its reported engine1.2.9 check is mechanical evidence, not a paired overall-win result. Do not credit multiple changes to one switch. No completed new tester outcome was available this unit.

## Collection, pending work and boundaries

Sole hub collector35400 healthy, latest inspected passes23/27 downloads,0errors; checkpoint DB read-only/query_only at03:46Z says14585active/14265idle. Immutable read excludes WAL; new replay arrivals independently confirm team7 live collection. No API call, collector setting, simulator, bot, deployment or main-source change this unit. One query worker at a time, all complete. Own qcols store remains31games/62sides with1110 pending in the unit19 snapshot; old754-game store preserved. Neither store is a current census.

Next: read the completed Rome zero when available; obtain the401 ID manifest; let Nara deliver per-hash queen gaps; hand Shenzhen/Kanazawa the corrected hazard design before its event study. Resume the existing store queue when needed for fresh mechanism coverage, rather than repeating completed audits. Recent matched unranked coverage remains missing; no spoofing inference from the mode gap. Board H21-01..07 and coordination notes record these handoffs.
