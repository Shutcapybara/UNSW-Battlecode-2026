# Himeji unit 8 — ranked post-store references and the gate ruling

Published 2026-10-01 18:15 UTC. **The Mac post store is usable: 2,072 ranked games, 482 series, nine current top-ten teams.**
Ranked opening references are now separated from unranked testing and carry series-bootstrap uncertainty. They
remain provisional. Carthage09 fails its direct repair test; Himeji answers the delegated gate question below.

## 1. Himeji's ruling on the delegated analyst gate question

Carthage3ff5dd9aa explicitly re-addresses this to the analysts at the lead's instruction. Himeji's answer is **yes:
use a win-led local evaluation for predeclared 1.2.3 rule adaptations**, with these conditions:

| Quantity, paired candidate minus declared parent | Required lower bound / guard |
|---|---|
| Overall pool expected-score share (win1, draw0.5, loss0) | >0 |
| Overall generated-panel expected-score share | >−0.02 |
| Frozen normalized economy mean, both panels | >−0.03 |
| Pool units@100 and total@100 | retain existing lower bounds ≥−0.02 |
| Tier-2, early-checkpoint guards for late arms, CPU/errors | retain existing D-032 checks and thresholds |

Use official outcomes on common fixtures, complete seeds1–3 and both seats/panels, and retain the per-map and
per-checkpoint readout. Here “lower bound” means the existing bootstrap fifth percentile: a one-sided95% bound,
also the lower endpoint of the published central90% interval. Do not relabel it as a two-sided95% interval.
Existing fixture bootstrap is the screening convention; freeze a common blocked/clustered confirmation analysis
before claiming population-level deployment strength, and do not select a favorable interval after viewing outcomes.

This is **Himeji's analyst ruling**, not a claim of unanimous ratification or an edit to the shared decision ledger.
It changes economy from a required gain into a guard for this predeclared class; it does not abolish production,
safety or opening checks. The margins0.02/0.03 are decision tolerances, not measured field percentiles. Preserve
historical D-032 verdicts and show the second reading alongside them. New ranked live testing remains deployment
evidence; unranked and local panels stay separate. No bot is promoted, registered or activated by this finding.

**Queen arms use the same overall-win criterion.** H-Q1's survival≥0.5 is a mechanism hypothesis/falsifier, not a
substitute acceptance metric. Report actual reach, conditional survival and the joint alive-and-reached count;
keep pocket maps in overall results. Baseline-defined RL subgroups are diagnostic, not a replacement for overall
wins. Large queen-verdict counts do not compensate for lost elimination games.

**04 is an appropriate corrected measurement baseline** once the tester freezes its exact fingerprint and existing
full official-result baseline. This does not imply a proven gen gain. Keep00 as the historical control; subsequent
incremental tests must declare04 as parent if that is the baseline they build on. Do not silently change comparison
parents. Φ remains diagnostic until the outstanding active-only/provenance/calibration audit is resolved; an
unvalidated or unmeasured Φ guard cannot be used to declare that an arm passes.

### What this ruling says about the existing arms

| Contrast | Pool win lower bound | Gen win lower bound | Other relevant evidence | Win-led reading |
|---|---:|---:|---|---|
| 04−00 | +0.016 | −0.011 | economy lower bounds−0.003/−0.001; reported guards pass | passes retrospective local screen; corrected baseline |
| 05−00, whole adaptation bundle | +0.019 | +0.003 | economy lower bounds−0.003/−0.005; reported guards pass | passes retrospective **bundle** screen |
| 05−04, free-sprint increment | **−0.020** | rounded+0.000 | point pool gain+0.005 | **does not pass** required pool gain |
| 08−00 | **−0.037** | −0.003 | gen economy LB−0.050; material guards fail | reject |
| 09−00 | **−0.031** | **−0.072** | gen economy LB−0.105 | reject |

Antioch/Nara support the sprint bundle; Himeji agrees with its observed gain against00, while disagreeing with
calling05 an accepted **increment over04** under the proposed pool-positive rule. Preserve both readings. If the
tester wishes to evaluate the bundle as a whole against the historical baseline, label that contrast explicitly;
if testing the increment, its current evidence is inconclusive on pool. Fresh confirmation after choosing the
rule/contrast avoids treating a post-result rule change as a preregistered success. This analysis performs no stack
change and leaves candidate manifests alone.

## 2. Carthage09 and the next queen comparison

**Agree: the tested yield repair fails.** Direct09−06 gen win is−0.057 [central90% −0.083,−0.031], economy
−0.044 [−0.065,−0.021]. Pool economy improves+0.046 [+0.027,+0.068] but queen survival barely moves2.9→3.0%;
gen survival falls23.6→20.4%. This is the requested repair contrast, not merely another comparison against00.
Close this yield implementation as a repair; it does not falsify all coordination or H-H1's different head-retention
mechanism. H-H1 stays proposed0.5.

Queued10 starts suppressing queen production splits at r120 on08. Read it as **10−08** for the phase intervention,
and also10−00 for the whole stack; report queen-alive@120/reach counts and verify that pre120 behavior matches08
on paired fixtures. It is not a replication of blanket no-split02 or a retained-head split policy. No result assumed.

## 3. Ranked-only opening references from the synchronized store

Direct read-only DuckDB extraction, **no q.connect / no shared norms writes**. Earliest part filename per game,
both sides retained, `games.era='post'`, ranked/unranked separated. Store metadata covers3,943 post games but only
**2,862 decoded** games: **2,072 ranked / 790 unranked**. The reference field is the decoded ranked in-scope sample,
not an unbiased census of every live game. Ranked has4,144 sides/482 series; unranked1,580 sides/201 series.

Use **17:51:07Z ladder membership**, applied retrospectively to decoded post games from **09:26:46Z–15:39:31Z**.
Top-ten ranked sides total**878**, from **9 teams**: 112,20,206,213,249,314,375,801,87. New leader952 is missing.
There are no team7 rows in this older store; the five ranked live games from unit7 are external observations at a
later time, from one series/opponent/seat. This temporal/cohort selection prevents a stable current-strength claim.

The table gives **the current-cohort median's percentile in the ranked field**, r50, using midranks for ties.
It is a provisional reference, not an instruction to maximize every count. Full raw medians, bed-capture and units,
r25 references, sample counts and **95% series-bootstrap intervals** are in `annotated-references.csv`.

| Map (frozen signature cluster) | Field games / top10 sides | Bed pearls pct | Splits pct | Transits pct | Territory pct | Total pct |
|---|---:|---:|---:|---:|---:|---:|
| Autarky (c1) | 214 / 90 | 65.2 | 54.7 | 67.1 | 65.3 | 74.4 |
| Default (c5) | 189 / 79 | 53.6 | 52.4 | 45.8 | 58.9 | 62.0 |
| Devil (c0) | 208 / 84 | 66.8 | 67.7 | 50.0 | 70.6 | 67.1 |
| Portals (c2) | 206 / 81 | 43.1 | 44.3 | 33.3 | 50.0 | 46.6 |
| Prisoners Dilemma (c1) | 99 / 51 | 49.5 | 51.0 | 47.5 | 60.6 | 50.5 |
| Prisoners Dilemma 10 (unassigned replay-label variant) | 95 / 40 | 50.0 | 43.4 | 47.1 | 53.7 | 40.5 |
| Queen Of Spades (c4) | 208 / 84 | 58.7 | 53.0 | 60.9 | 69.1 | 54.6 |
| Schooltime (c3) | 201 / 87 | 61.8 | 60.3 | 46.4 | 67.2 | 61.3 |
| Slithery Fight (c0) | 220 / 91 | 60.0 | 58.6 | 52.3 | 55.0 | 57.3 |
| Trauma (c0) | 210 / 82 | 62.9 | 67.1 | 74.2 | 55.2 | 67.0 |
| Trophy (c6) | 222 / 109 | 61.6 | 56.8 | 46.2 | 58.2 | 57.3 |

For example, top-cohort transits sit at **33.3rd percentile on Portals versus74.2nd on Trauma**. A universal
“more transits” target is not supported by these references. This does not establish that restricting portals causes
better play: map, opponent and policy composition remain observational.

**Uncertainty:**1,000 resamples, seed8123, whole series within each map, preserving both sides and the field/top-ten
overlap within the same draw. The r50 median **full**95% interval widths across maps are17.4pp bed pearls,
17.0pp splits,17.7pp transits,15.6pp territory and16.1pp total. Maximum transit width is49.5pp. These are not
simultaneous confidence bands. Current top-team coverage, sampling and time stability remain unresolved; **all154
map/checkpoint/metric rows remain provisional**, even where an individual interval is narrow.

Opening references retain S-1's terminal carry convention and expose it:52/4,144 ranked sides have already ended
by r25,116/4,144 by r50. At r50 the PD10 stratum has36/190 ended sides. These are not active-game-only references.
Independent extraction parity on **596 overlapping side-games / 8,340 numeric comparisons** found0 mismatches
for all seven metrics at r25/50, using Himeji's earlier frozen replay extraction.

### Map labels and structural clusters

The store contains **Prisoners Dilemma** (129 decoded post games,99 ranked) and **Prisoners Dilemma10**
(123 decoded,95 ranked). Both map to the corpus metadata label “Prisoners Dilemma”; each has2 stored map hashes.
Their equivalence is not established here, so they remain separate. Antioch's hard-coded LADDER filter drops the
second label. Ask the replay lead to document/normalize aliases only after checking geometry; do not silently drop
those95 ranked games from references.

This report uses Himeji unit1's **computed frozen signature mapping**, which was already available in
`reference_data/cluster_map.csv`: c0Devil/Slithery/Trauma, c1Autarky/PD, c2Portals, c3Schooltime, c4QoS,
c5Default, c6Trophy. It is more precise than unit7's grouping from the prose excerpt; unit7 remains a historical
diagnostic. PD10 stays unassigned until its signature is verified. No map labels are offered as bot policy inputs.

### Live-us diagnostic, and the gaps that remain missing

The cached five ranked live games can be located in the earlier field distribution, without re-decoding them:
r50 total-length percentiles are **Autarky88.0, Devil92.4, PD93.4, Slithery61.8, Trophy63.4**. Raw top-cohort
median minus observed live-us totals are **−5, −16.5, −15, −2, −3** respectively. Each is **one later game against
team841**, not a matched-opposition or causal comparison. Do not read this as beating the top ten generally.

`annotated-references.csv` labels these as **descriptive unmatched differences**, with no contrast CI. The
opposition-matched inferential top-ten-minus-us column remainsNA. Unobserved live maps and PD10 retain missing
us values. Unranked unit7 games are not inserted into the ranked field or used to fill ranked gaps. This separates
having a measured live observation from having adequate evidence for a target or strength claim.

## 4. Freshness, cursors and reproduction

Source commits: main1d838553a/D-041, Antioch**cdac8bd96** (store sync), Carthage**3ff5dd9aa** (gate delegation,
09 result/10 queue), Nara21a182700, Kyoto7c835936c. Rome local L10 pool480 complete, gen395/1392; no paired verdict.
No new team7 games at this wake: the same fifteen from unit7, not re-decoded. Corpus cursor80,614 games, latest
17:58:49.453Z, SHA3bafc4dcd941b69829e36080b707c9b8aeb2bde7756e4b3beb468e662c3403bc.

Store sync request is now **resolved**. Games metadata hash`bfe4516582393c959f1cbfcf8279946d7c6a01466a5a75f65cd4e7da618e18c2`;15 post-series parts are frozen
by filename/size/mtime and checked unchanged through extraction. Metadata and row hashes are in the manifest.
The SQL display uses explicit +09:30 timestamps from DuckDB; this report converts them to UTC. No environment
packages were installed (the metadata inspection avoided a missing timezone dependency by casting timestamps).

```
python tools/himeji/ranked_store_refs.py --store /path/to/build/s1/corpus --ladder /path/to/20261001T175107Z.json --out /scratch/refs --boot 1000
python tools/himeji/annotate_ranked_refs.py /scratch/refs tools/himeji/unit7_audit/sides.jsonl tools/himeji/reference_data/cluster_map.csv
```

To reproduce the exact bootstrap without rereading a changing store, copy `opening-rows.csv` and `manifest.json`
from `tools/himeji/unit8_audit/` into the output directory first. All compact outputs remain below4MiB.
One DuckDB/query worker, now complete. No shared corpus/store/norms changes, bots, simulations or deployment actions.
Next: later ranked reference window/current missing team952 and additional live series; investigate PD10 geometry;
read10/L10/cap-lift when complete. Φ active-only/provenance requests remain open. No existing freeze is rewritten.
