# Himeji unit18 — ranked opening references by observed geometry

4 October 2026,02:38UTC. The new references cover S-1 Q3's bed conversion, production, portal use and territory at25/50. They are **provisional percentiles within a selected decoded ranked sample**, not replacement population norms or a causal top-ten-versus-us estimate. Rome04's corrected rejection is accepted; Rome05 is testing the distinct H-H5 fallback guard.

## Frozen cohort and reproducible estimand

Freeze the first708decoded games /1416sides of Himeji's versioned FRAME7 store, then take **504ranked games /1008sides**. There are489current-top10 sides and20own ranked sides per checkpoint. Window2Oct23:13:00Z–4Oct01:45:11Z, all post123 (cutoff1Oct06:00Z). Data came from the frozenunit17 coverage queue, not a random field census. Cohort is ladder021804Z:264/306/213/91/952/842/87/55/507/566. Membership is retrospective, not rank at game time.

For each metric, compute each side's empirical midrank percentile **within its exact map-header hash**, then take the currenttop10 median within a geometry stratum. This avoids pooling raw counts from differently sized maps. Bootstrap whole series500times (seed1818) within stratum/checkpoint, retaining both sides and recomputing those map-conditioned percentiles on every draw. Table values are percentile points with95% intervals. Both field and top10 selection are held to the decoded coverage sample. Confidence intervals do not remove sampling bias or rank-selection bias.

Structural descriptors are calculated from38actual live headers, never map names or authored fertility: portal-edge fraction>=.025 selects portal-dense; otherwise degree<=2 cell share>=.25 selects corridor; otherwise open. Cross with whether **both original queens initially fill a four-cell connected component**. This is an explicit coarse stratification inspired by Esquie's geometry features, **not** a reproduction of his21-feature/k8 clustering. The actual geometry and thresholds are recorded in geometry.json. Thus current Slithery can be classed open here without contradicting a historical authored-map cluster.

- Corridor: Devil, Islands, Maze, Tower Defense, Trauma, weakhold (12hashes).
- Open / four-cell queen: Schooltime (4hashes).
- Open / other queen spawn: Around UNSW, Australia, Autarky, Default, Prisoners Dilemma, Prisoners Dilemma10, Queen Of Spades, Slithery Fight, Trophy (18hashes).
- Portal-dense: Portals and Stripes (4hashes).

| Geometry stratum | Ranked field sides / games / series | Top10 sides / series | Own sides | Exact matching strata |
|---|---:|---:|---:|---:|
|Corridor|358 / 179 / 108|169 / 92|8|0|
|Open / four-cell queen|52 / 26 / 26|23 / 21|3|0|
|Open / other queen spawn|498 / 249 / 134|253 / 118|6|0|
|Portal-dense|100 / 50 / 48|44 / 37|3|0|

The current references, all provisional:

| Geometry | Round | Bed capture | Splits | Transit attempts | Territory |
|---|---:|---:|---:|---:|---:|
|Corridor|25|60.9 [56.7,65.9]|48.3 [44.3,58.0]|50.0 [50.0,50.0]|60.9 [55.6,67.1]|
|Corridor|50|64.1 [57.9,68.3]|60.9 [56.2,67.3]|50.0 [50.0,50.0]|64.5 [58.8,70.0]|
|Open / four-cell queen|25|50.0 [34.7,62.1]|52.8 [50.0,58.3]|65.6 [39.3,75.0]|65.6 [45.0,75.0]|
|Open / four-cell queen|50|63.9 [50.0,82.1]|75.0 [46.0,83.9]|60.0 [50.0,71.9]|68.8 [44.1,77.6]|
|Open / other queen spawn|25|58.8 [54.6,63.7]|55.8 [52.1,63.5]|50.0 [44.3,59.1]|58.3 [54.1,61.7]|
|Open / other queen spawn|50|60.3 [56.2,64.5]|58.8 [52.8,64.2]|57.7 [52.5,63.9]|58.0 [54.2,62.0]|
|Portal-dense|25|64.4 [54.5,71.1]|56.9 [50.0,72.5]|60.8 [48.5,68.8]|50.0 [50.0,50.0]|
|Portal-dense|50|65.7 [54.5,72.8]|59.6 [48.5,69.5]|55.7 [45.7,68.0]|50.0 [50.0,50.0]|

Bed pearls eaten also has a separate row for every stratum/checkpoint in ranked-references.json; raw-map-descriptives.json gives same-hash raw medians for interpretation, not additional stable targets. Each reference row records finite counts, teams, series, hashes, terminal carries and valid bootstrap draws.

**Measurement limits:** bed capture is FRAME7 non-corpse/fallback bed-labeled eats divided by bed-labeled spawns; it does not require fertile TILE values. Public header fertility is unavailable, so no bed-density/bed-absence claim is made. S1 transit counts follow proposed movement paths using the round-start body: they are attempted route transits, not guaranteed realized safe crossings. A50th-percentile transit row can simply mean everyone has zero transits; it is not a transit target of50. Territory ties likewise explain the portal-stratum50[50,50]. S1 cumulative events include the checkpoint round and its terminal carry convention;4open-stratum sides ended before50,0other strata; earlier terminal counts are in the artifact. These are opening metrics, not queen-survival estimands.

## Top-ten minus us remains missing; stability is not earned yet

We have20own ranked sides, but **zero overlapping strata** when matching exact map hash, seat, opponent ID and UTC6-hour bin against top10 sides. The corpus index has no game-time opponent Elo with which to reproduce S-1's1750–1900 matching. Current ladder Elo is not a substitute. All cluster×phase×component matched gaps therefore remain NA; this is missing support, not a zero gap. Local panel scores remain a separate population.

The references have no independent later-window replication. Even though corridor/open intervals are relatively narrow, none is stable enough to replace frozen BENCHMARKS. A future stability check requires a nonoverlapping window, at least20independenttop10 series per stratum, percentile half-width<=10points and agreement across the windows; these are screening conditions, not proof of unbiased population estimation. The four-cell queen stratum is especially imprecise (23top10 sides/21series). The708-game reference freeze stays fixed while incremental decoding continues.

## Hypothesis guidance: preserve the L41 volume-versus-yield distinction

Portal-dense r50 bed capture has top10 median percentile65.7 [54.5,72.8], transit attempts55.7 [45.7,68.0]. The paired-component contrast is **+10.0percentile points [−1.6,+17.5]**; its interval includes zero. This neither proves collection is the bottleneck nor falsifies L41's early portal-volume mechanism. It does rule out presenting transit volume alone as an established success target from this sample.

**Ledger/test card:** retain L41 at its existing0.5 weight; no new weight or invented causal finding. Mechanism to test remains that early portal entry opens access to food and subsequent production, rather than merely adding traffic. Use one entry-policy switch on a clean parent and predeclare accessible-food/traffic exposure from observations, keeping the outcome-defined high-performing teams out of trigger design. **Falsifier:** entry attempts rise but bed capture/production and paired wins fail to improve, or transit death/hygiene/economy guards fail. Record realized versus attempted crossings and per-transit outcomes so a throttle cannot appear to improve efficiency by suppressing access. At least60independent exposed pairs first for feasibility/discordance estimation;10pp paired binary-win planning requires149/306/463pairs at discordance.2/.4/.6 before map/series inflation. This sample does not justify a new performance arm by itself. Suitable tester is Rome after current05, or a director-assigned free tester; no new arm or paused lane started. L06's rejected portal throttles remain counterevidence and the safety/volume distinction is preserved.

H-H5 remains separately testable now: restore normal crown behavior when fresh queen evidence is absent. Rome05's fresh/expired/nonqueen/absent record counts and clean01 comparison matter more than a recovery against03 alone; a fresh beacon is not exact liveness. H-H1/H-H3/H-H4/H-H5 weights remain0.5; switching H-H2 remains unresolved without new matched identity/behavior evidence.

## Tester and analyst readings

- **Rome04 /6857cc261:** agree REJECT/no-stack;−1.354pppool [95%−3.125,+.417],0gen[−.503,+.503]. Gate failure does not imply H-H1 falsification. Treatment after250, child recipient, r150 pre-treatment and unknown active-crown exposure are now correctly stated. No need to rerun the unchanged panels. Direct handoff delivered this reading and requested Rome05 exposure categories; no duplicate experiment.
- **Nara89c2d2cbe:** accept H17-05's lineage, censoring and series/mode correction plan; its L47 second slice owns that work. Keep the95dead-queen-trigger finding scoped to the selected Portals pairs. It does not establish that all03 triggers across all maps had dead queens, nor a universal requirement to stack multiple queen changes before testing fallback. H-H3 space and H-H5 fallback remain separate interventions.

## Five newly downloaded own games: a useful fallback counterpoint

One ranked14585-versus217 series started01:22:13Z: **2wins,3losses**. Maze1003123 and Default1003124 win by longest; Queen Of Spades1003122 loses by longest; Trophy1003120 and Devil1003121 end by elimination before490. Both queens are dead at490 in all3reached games; ownqueen alive0/3,2early games censored. Terminal longest values are69–63,49–12 and25–31 respectively. The sole RL loss has total30–61 (r49036–58), so material-lead-loss/RLloss=0/1. Both material leads in RL games won: lost/RLlead=0/2 at both490/end. This is one series, not a stable rate or evidence that queen preservation is unnecessary; it illustrates why useful longest-dragon fallback remains valuable when both queens die. Five official/indexwinner matches and10terminal queen-header/body checks pass. These games were not yet in the frozen reference cohort.

## Collection/store cursor and reproduction

Rawfreeze02:23:03Z:118497games (+618including5own),latest02:19:17Z,indexSHAae389c653305ff7e33247a6af3aae88d33ada5dbb57e76ff2d269675797d0c1f. Ladder021804Z SHA74d926f42598386978de4ec7289c0429b14189fd72c2c8d3d51f83296336f797. Solecollector35400healthy40/pass,0errors. DB read-only succeeds,14585active/14265idle lastseen02:18:03Z. No API call, collector/deployment/source change or competing downloader.

Store663→754games /1508sides:91new,0errors in332s across two one-worker passes (45+46).549ranked/205unranked,allpost123;1508official-indexwinner agreements,18decoderlabels,latest01:45:11Z. Currenttop10sides778/own22;metadata is still unit17's117879-game freeze. **308selectedgames remain**; resume that same immutable snapshot next wake. Reference calculations used the earlier708-game freeze and are not silently updated to754. OldS1/norms untouched; no Himeji query remains active.

```text
ANALYSIS_PY tools/himeji/opening_geometry_refs.py --repo MAIN --store OWN_STORE --snapshot UNIT18 --out UNIT18/references --boot 500
ANALYSIS_PY tools/himeji/new_own_queen_audit.py --repo MAIN --rows UNIT18/new-own-rows.json --out UNIT18/new-own-queens.json
ANALYSIS_PY tools/himeji/store_coverage.py --store OWN_STORE --out UNIT18/store-coverage.json
```

MAIN=/Users/alik/Documents/Projects/UNSW-Battlecode-2026; ANALYSIS_PY=MAIN/.venv/bin/python;
UNIT18=/Users/alik/Documents/Codex/2026-10-01/p2-a-analyst-one-claude-opus/work/himeji-unit18;
OWN_STORE is siblingwork/himeji-live-store. Reproducing this exact reference uses committed opening-rows.jsonl and reference-manifest.json in an output directory; absent those files the script explicitly freezes the current store. Compact output/source hashes in tools/himeji/unit18_audit/; no replays/parquet committed.
