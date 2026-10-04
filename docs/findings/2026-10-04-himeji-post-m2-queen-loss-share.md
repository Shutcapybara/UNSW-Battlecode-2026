# Himeji unit20 — post-m2 queen losses and per-map reference

4 October2026, 03:40UTC. D-043 measurement unit; no bot/simulator/API calls.

**Ranked carthage-05: 18/45 losses were queen-decided, 40.0% [95% series-bootstrap 21.4,60.8].** This is 18/90 games, 20.0% [9.8,32.3], and 18/18 queen verdicts were losses. These are three different denominators. The older “70 of72 queen-decided games lost” was a historical conditional-verdict result; it does not answer the share-of-all-losses question and is not substituted here.

## Population, coverage and precision

Confirmed live submission14585 only, post-m2 >=2Oct03:49Z. Frozen local corpus118964, 4Oct03:23:20Z; team7 collection verified active in unit19's15winner/queen checks and current collector/DBcheckpoint. No new own arrivals in this190-game increment. Start times: ranked2Oct04:23–4Oct02:14; unranked2Oct04:22–3Oct05:43. The unranked window ends almost a day earlier: **do not interpret the mode gap as a policy switch or causal mode effect**.

Existing Shenzhen lean parts supplied5813post-m2 games;11626 side-winner checks agree with the frozen index and lean's engine winner. Timestamp strings were normalized as instants before era selection (space/+00:00 versus T/Z). Excluded15team7 sides with header-metadata14265. The lean cache lacked15recent14585ranked games: decoded those from existing replays in Himeji scratch, verifying15replay hashes/official winners/14585headers and30terminal queen lengths. No shared lean/store write. Final **90/90ranked and176/176unranked confirmed14585 games available in this corpus freeze** are included; this is not a census of every server game. Ranked observed series sizes are16×5,3×3 and1×1 games: four series are partial in the corpus, and resampling does not recover those missing games. Other teams' blank submission identity remains unknown.

Current top ten from ladder031300Z:264,306,213,566,91,842,87,507,55,952. Selected field reference1097ranked sides/978games/274series;1342unranked sides/1123games/264series. Exact hashes retained; Prisoners Dilemma10 remains a separate initial-dragon variant. No old/new map pooling. All intervals are2000whole-series bootstrap resamples, seed2020; zero-denominator draws omitted. They are conditional on collection/decoding coverage and cohort, not guarantees against opponent/time selection bias. Later independent-window replication is absent. **Provisional descriptive references; no stable field-percentile target or matched top10−us estimate.**

| Confirmed14585 population | Games / series | Queen losses / all losses | Queen losses / all games | Actual490 alive / reached; early censored |
|---|---:|---|---|---|
| Ranked |90 /20|18/45 =40.0% [21.4,60.8]|18/90 =20.0% [9.8,32.3]|0/60;30early|
| Unranked |176 /25|34/137 =24.8% [16.1,34.8]|34/176 =19.3% [12.4,27.5]|0/109;67early|

The zero-survival bootstrap degenerates, so no [0,0]game-rate interval is reported. With an independent-series model, observing no survival in20ranked eligible series bounds the chance a series has ANY such survival below13.9% (one-sided95%); for25unranked series,11.3%. These are **series-event bounds**, not per-game survival bounds. Joint actual490 survival is0/90 and0/176 respectively. Terminal RL survival is0/60 and0/109, separately defined from reached490.

## Ranked map reference and the observed queen gap

Top-ten actual490 survival251/629=39.9% [35.5,44.3],468early side-ends; own0/60. The **unadjusted observed gap is39.9pp**; no matched-gap confidence interval follows from the boundary own sample. Terminal RL top-ten survival249/623=40.0% (not identical to reached490). Unranked field381/852=44.7% [40.9,48.7],490early ends, a separate population. A pooled cohort mean is not a per-team median or field percentile; retain Chongqing's0.444 as its historical cohort/coverage estimate, not evidence of temporal decay.

| Post-m2 map/variant | Top-ten alive / reached490; % [95% series CI] | Own alive / reached490 | Own queen losses / losses |
|---|---|---:|---:|
| Around UNSW | 12/60; 20.0% [10.7,30.5] | 0/6 | 1/1 |
| Australia | 14/53; 26.4% [15.7,38.6] | 0/6 | 1/4 |
| Autarky | 4/24; 16.7% [3.8,34.6] | 0/2 | 1/2 |
| Default | 4/31; 12.9% [3.0,26.7] | 0/3 | 0/2 |
| Devil | 2/10; 20.0% [0.0,43.8] | 0/0 | 0/2 |
| Islands | 10/50; 20.0% [9.8,31.1] | 0/5 | 0/1 |
| Maze | 27/69; 39.1% [27.8,50.8] | 0/7 | 1/2 |
| Portals | 20/50; 40.0% [26.9,54.0] | 0/5 | 1/3 |
| Prisoners Dilemma | 3/11; 27.3% [0.0,62.5] | 0/0 | 0/0 |
| Prisoners Dilemma 10 | 7/11; 63.6% [30.8,90.0] | 0/1 | 1/1 |
| Queen Of Spades | 5/13; 38.5% [11.8,71.4] | 0/2 | 0/2 |
| Schooltime | 48/53; 90.6% [82.1,98.1] | 0/7 | 6/6 |
| Slithery Fight | 22/64; 34.4% [23.9,45.2] | 0/6 | 2/3 |
| Stripes | 0/1; boundary CI omitted | 0/0 | 0/2 |
| Tower Defense | 4/17; 23.5% [5.6,50.0] | 0/1 | 0/1 |
| Trauma | 50/64; 78.1% [68.2,87.7] | 0/5 | 3/5 |
| Trophy | 0/1; boundary CI omitted | 0/0 | 0/2 |
| weakhold | 19/47; 40.4% [27.1,55.3] | 0/4 | 1/6 |


0/0 means no eligible observation, not zero survival. Full all-game/eligible/series/hash counts, intervals, reached490 queen-length quartiles and both modes are in queen-reference.json/hash-counts.json. Map-level observed differences are unmatched across opponent, seat and time; exact matched-us gaps remain NA. A single reached Trophy side already warns against treating an empirical “pure elimination” label as a rule exemption.

## Material leads and mechanism guidance

Ranked14585 RL losses: **14/35** had a total lead at490 (40.0% [26.8,53.1]), but **12/35** had a terminal total lead (34.3% [20.0,48.0]). Conversely, losses among RL games with a lead are14/28at490 (50.0% [27.6,71.9]) and12/25atend (48.0% [23.5,72.0]). Unranked lead-loss/RL-loss14/88at490 versus13/88atend. These measure different failure modes; neither is the queen-loss denominator above.

**H-H3 and H-H4 remain separate (proposed L24/L49 and L39/L49, weights0.5):** all6ranked Schooltime queen losses faced an opponent queen oflength3. Outside Schooltime,9/12queen losses faced lengths>3 (two<3, one=3). Unranked:13Schooltime cases all=3;19/21elsewhere>3. This is retrospective loss-conditioned evidence, not a forecast or causal win gain. Holding other state fixed, an ownqueen3 would only tie the queen term against3 and still lose that term against>3; no replay rewrite estimates wins.

- H-H3 falsifier/test: live-map carthage05 cage intervention fails to prevent eligible queen deaths, or worsens win/economy guards. Retain60independent paired exposed cases + food-first/blocked/below-cap/open negative controls; zero failures would yield4.87%one-sided bound under independence. Keep H19's food-free emergency exception versus universalzero-tax disagreement; do not infer universalgrowthtarget3.
- H-H4 mechanism/test: after survival is established in open geometry, one queen-directed feeding switch should increase queen-length advantage and official queen/RL conversion without production or overall-win loss. Measure actual originalqueen alive-at-trigger and length/eating exposures; dead-trigger cases cannot falsify feeding. Falsifier: adequate exposed sample with no length/conversion gain or a breached guard. Pilot>=60exposed pairs for mechanism/safety, then roughly149/306/463pairs for10pp paired-win effect at discordance0.2/0.4/0.6, before seed/series clustering. Suitable testerRome after its new carthage05/LIVE_MAPS_M2 zero; no extra arm requested now. H-SZ8 is aligned, not an independent causal confirmation.

## Readings, provenance and next action

Rome700971108 new carthage05/LIVE_MAPS_M2 pool is running (100/816 at03:30 snapshot), no complete result/gate reading yet. Historical Rome05/Rome03-hb1/oldmaps partial stays no-verdict. Sent the live denominator/length findings directly to active Rome. New brief resolved at **docs/briefs/2026-10-04-live-maps.md** and read; D-043 acknowledged. Shenzhen owns requested map-byte identity; avoid duplicate work. Main2e4c74832 differs from the already merged69f4561d4 only in docs; current decoder dependencies unchanged. Peer/status/source hashes recorded.

Collector35400healthy,0errors; DB read-only immutable checkpoint03:12:58Z says14585active/14265idle (WALexcluded). Raw indexSHA4d53f15681ea7687dc0617835b5f2d50a0ff3b432ffee9438d753e6a294e508c. New qcols store resumed same frozenunit19 metadata118774:12new,0errors/199s,now31games/62sides allrankedpost-m2,62winneragreements,latest02:23:59Z;1110pending. One decoder worker; checkpointed and stopped. Old754store untouched. Field reference uses independently frozen lean rows plus15supplements, **not this31game store**.

Next: read Rome's new zero when complete and Shenzhen's identity result; resume1110queue only if the measurement needs it. Need fresh matched opponent/seat/time live samples before using a mode difference or testing switching intent; request already-played recent unranked14585data through collector coordination if available, without initiating matches. H-H2 unresolved.

Reproduce: `python tools/himeji/queen_loss_reference.py --repo <main> --snapshot <new-output> --frozen-rows tools/himeji/unit20_audit/queen-rows.jsonl`. Original freeze reads main lean parts and frozen index/ladder; `complete_own_rows.py` fills only confirmed missing own replays. Both computations use official winners and explicit checkpoint/lead denominators.76summary rows reproduced exactly from committed inputs. Evidence/query/source/coverage hashes: tools/himeji/unit20_audit/.
