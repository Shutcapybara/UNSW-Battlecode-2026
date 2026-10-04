# Himeji unit19 — sprint hypothesis audit and D-043 transition

4 October 2026, 03:10 UTC. Analysis only; no bot or simulator run.

**Decision:** retain early queen feeding as a hypothesis, correct its speed threshold, and reject a universal zero-paid-sprint target. D-043 was explicitly authorized during this unit: Himeji fast-forwarded to main `69f4561d4`, leaving the main checkout untouched. Read the director's 03:10 board line and D-043 decision. The named `claude/brief-2026-10-04-live-maps.md` was absent in that commit; the full user brief supplies the direction.

## 1. H-SZ21 and H-SZ23: useful observations, different intervention

Read Shenzhen unit6 and its qpay source. Its 416-game sample contains **159 ranked / 257 unranked** games, not a ranked-only reference. Frozen side rows joined to metadata reproduce 243 longest, 167 queen and 6 total verdict games; thus this particular sample's R>=499 selection contains no elimination, but the shortcut is not generally an official-verdict test. Window 2 Oct04:12–3 Oct23:46Z, entirely post-m2. The following re-cut uses the 4 Oct02:52Z ladder (82 in, 952 out), so cohort counts differ from Shenzhen's 366 sides. Both versions remain valid descriptions of their stated cohorts.

| Top-ten population | Sides / series | Recorded queen segments paid per side-game [95% series CI] | Ever paid |
|---|---:|---:|---:|
| Ranked, all selected sides | 104 / 84 | 0.192 [0.082,0.333] | 12/104, 11.5% [5.6,18.0] |
| Ranked, terminal queen alive | 50 / 41 | 0.060 [0,0.133] | 3/50, 6.0% [0,13.3] |
| Unranked, all selected sides | 245 / 117 | 0.229 [0.100,0.391] | 26/245, 10.6% [6.2,15.3] |
| Unranked, terminal queen alive | 102 / 70 | 0.137 [0.052,0.233] | 10/102, 9.8% [4.3,15.4] |

These are pooled-map descriptive diagnostics, **not map-specific targets or stable field percentiles**. Full rows preserve map/hash/mode/series. Sample selection, current-rank conditioning and survivor conditioning preclude causal interpretation. The recorded `paid` field measures realized body loss, not intended path cost: a fatal attempted sprint need not incur its planned tax. No matched-us gap is filled. Bootstrap: 1,000 whole-series resamples, seed1919, fixed selected cohort; no claim that intervals cover collection bias.

**Threshold correction:** ceil(L/4) is 1 at L=2–4, 2 at L=5–8, 3 at L=9–12. Length8 has no speed increment over5; a 3–7 versus8+ hazard cut mixes free-step regimes. Length can still help the tiebreak, but that is a separate mechanism.

**Disagreement retained with H-SZ21/H-SZ20:** “never pay” and “exactly3 in every cage” are too strong as policies. H17's four selected late failures in three games had food-free two-step prevention opportunities before the meal filled the cage; at length3 that costs one segment. The first-step-food case instead fills length4 and self-collides before a useful tax. This is an observable geometry/food/cap exception, not license for arbitrary queen shedding; length2 can lose the queen tiebreak. Shenzhen's 10/12 local probe wins do not compare zero-tax against that exception on matched cap exposures. Its 1.2.9 live-template, carthage-05 probe is distinct from Rome's historical hb1 parent and old maps.

## 2. Test cards for analysts and testers

- **H-SZ23 refinement, proposed L49/L50, weight0.45 retained:** on open geometry, feeding past an actual free-step threshold increases safe displacement and then survival. Shenzhen can test lagged at-risk queen-turn lengths at 4→5 and8→9, with within-band placebo comparisons; match/stratify team, exact map hash/seat, phase, opponent, prior threat and mode. Include every at-risk queen, not only queens surviving to the end. Falsifier: no movement increase at true thresholds, or the apparent hazard improvement vanishes with time/geometry/threat controls. Team adjustment alone does not isolate speed from length, feeding policy or selective survival. Approximate 80%-power two-sided HR0.7 planning needs **247 queen enemy-death events** under balanced independent exposure (Schoenfeld approximation); clustering/imbalance increase this. Do not call a non-significant smaller sample falsification. This remains observational; a one-switch feeding-time arm would be a tester's later causal check after the new zero.
- **H-H3 / H-SZ21 exception, proposed L24/L49, weight0.5 retained:** compare zero-tax with a predeclared food-free escape exception at cap, on carthage-05 and live-map fixtures. Falsifier: no prevention of eligible cage deaths, or queen-length/win/production guards worsen. First obtain **60 independent eligible paired cases** plus food-first, blocked-route, below-cap and open-map negative controls; zero failures would bound the independent failure probability below4.87% one-sided95%, not prove win gain. A10pp paired-win effect needs approximately149/306/463 pairs for discordance0.2/0.4/0.6 before series/seed clustering. Suitable tester Rome or an assigned live-map tester after its D-043 zero. No arm launched here; do not bundle feeding, hunting and emergency escape.

## 3. Checkpoint and tester readings

The new `build.py::queen_cols` uses `lens[min(k,last)]`. A two-snapshot unit example ending at r1 returns q_len@490=3. This is terminal carry, not reached-r490 survival. Preserve the column's historical values, but query `R>=490` and publish early-end counts; prefer an explicit reach flag / nullable observed length. New own store19games/38sides all reach490, so **0 affected early sides in this small batch**; the source diagnostic is not a claim that current published Chongqing tables are wrong.

Rome `3fff00df0`: **05 is incomplete/historical**, old `maps/*.map`, parent Rome03 derived from Rome01/hb1-14, engine1.2.3. Pool480 completed but unscored against parents; official gen227/1392, incompatible custom744 stopped. Agree with no verdict/no stack. H-H5 remains untested; resume new carthage-05/live-map zero, not an extra old-map panel. Completed Rome04 conclusions remain historical and do not transfer swapped-map gen geometry. Direct D-043 coordination sent to active Rome; no other analyst chat available for Shenzhen/Chongqing, so board requests used.

## 4. Freshness, live-us and next action

Raw freeze118774 at02:56:32Z, +277 including **five new ranked team7 games**, series02:14Z vs529, all replay headers14585. Independently verified all5 official winners and10 terminal queen lengths. Result2–3;4RL longest games, own queen alive490=0/4; one early elimination win censored. Australia188–171 and QoS34–29 material leads at490 became losses and terminal deficits145–186/15–31. Therefore r490 lead-loss/RL-loss=2/3 and lost/RL-lead=2/3, versus terminal0/3 and0/1. **Zero queen-decided losses in this one series**, not a field conclusion or usable series-level interval. Live collection has resumed and remains active; other teams' blank submission names remain unknown, not switching evidence.

Collector35400 healthy, recent passes0errors. SQLite mode=ro opening failed; read-only immutable checkpoint succeeded (explicitly excludes WAL), active14585/idle14265 lastseen02:52:03Z, corroborated by current replay arrivals and collector log. No database, collector, credentials or deployment settings changed.

Builder hash changed with new queen columns. Preserve old754game/1508side store and its308pending unit17 queue. Separate `work/himeji-live-store-qcols-v1` has19games/38sides (all ranked/post-m2),0errors,38official-index winner agreements, latest02:23:59Z,2map labels;1122 queued on the frozen unit19 snapshot. One decoder worker,171s; no workers remain. The metadata wrapper now emits map_era on future builds. This new store is not merged with old-schema parts.

Next bounded unit: actual-map byte/structural identity audit (public fertility serialization is already known to differ), or post-m2 queen-gap / queen-decided-loss share with series uncertainty, using the new live-map definitions and complete denominators. Resume the1122 queue only on the same frozen snapshot/decoder version. Unit18 references already lie entirely after the map switch and used exact hashes; explicitly relabeled post-m2, values unchanged. Older exemptions are historical and void for new-map policy.

Reproduce from committed rows: `python tools/himeji/sprint_reference_audit.py --repo <main> --snapshot <new-output> --frozen-rows tools/himeji/unit19_audit/sprint-rows.jsonl`. Source check: `checkpoint_semantics.py --repo <main> --out <json>`. Live audit: `new_own_queen_audit.py` with committed new-own-rows. All manifests, hashes, estimates and coverage: `tools/himeji/unit19_audit/`.
