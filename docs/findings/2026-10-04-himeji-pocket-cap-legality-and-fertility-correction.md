# Himeji unit16 — correct the bed inference; prevent pocket saturation before the cap

4 October 2026, 01:40 UTC. H-H3 proposed L24/L49 remains weight **0.5**. This unit supplies a measurement correction and eight small deterministic engine checks, not a bot experiment or a performance verdict.

## Correction to H13/H14: public fertility is unavailable

I withdraw the “no-bed component” description in H13-02 and the “non-static-bed” inference in the unit14 finding/status. Ten inspected public replay headers have **zero fertility pairs on every tile**. Four saved local Rome headers (Portals, Schooltime, Trauma, Autarky) retain 104/326/142/188 positive max-gap tiles and their map-header hashes match the authored maps. Public zeros therefore cannot establish absence of a bed. The original reports remain frozen; this is the correction.

Replay997644 also contains **zero countdown events throughout**, so absence of a countdown at r267 is not discriminating. All **1,758 FRAME7 non-corpse/bed-labeled spawn events** lie on authored Schooltime bed coordinates. The two relevant pocket cells, (3,1) and (56,1), have authored gap20–200. This supports an ordinary bed-spawn explanation. It does not establish a new spawn mechanism or a FRAME7 attribution bug. FRAME7's fallback attribution remains a general limitation, but this case is not evidence of an error.

The replay's full terrain adjacency differs from the authored Schooltime map. Do not insert authored fertility or exact timers into transformed live games. The reason public fields are zero is not established, and implies no deceptive intent. The real 3→4 growth followed by a next-turn wall death remains observed; H-H3 must use topology, occupancy and legal continuation, without a “no beds” premise.

## The unit cap is already binding at the queen's action

Applying all earlier split/death events before each queen TurnStart gives:

| Game | Team / queen ID | Fatal turn | Own units at TurnStart |
|---|---|---:|---:|
|996984|280 / 0|325|64|
|997644|187 / 0|268|64|
|997644|280 / 1|268|64|
|998186|791 / 0|320|62|

Four queens across three games; the two rows in997644 are correlated. Three have no spare slot under a64-unit limit. The fourth failure is not explained by the cap. These selected late failures are not a field prevalence estimate; ranked/unranked selection and earlier holdout denominators remain in unit14.

## Eight isolated1.2.3 legality checks

Using fixed scripted actions on a generated four-cell pocket, seed116, no repository bot loaded or built:

| Own units / queen length | Action | Observed outcome |
|---|---|---|
|63 / 4|SPLIT2|Legal, original queen ID retained; child dies, queen2 then3 and alive through fixture end r4|
|64 / 4|SPLIT2|Invalid death on initial turn|
|64 / 4|MOVE N/E/S/W (four cases)|Self/wall/wall/self on initial turn|
|64 / 4|MOVE WN|First step self-collides; sprint cannot repair an already blocked first step|
|64 / 3|MOVE WN on empty route|Legal two-step sprint spends one segment; queen length2 next turn|

The last fixture deliberately terminates the queen with invalid SPLIT0 at r1; that later death is not a sprint failure or a survival estimate. Other fixture actors deliberately terminate. These eight cases establish mechanics only; they are not eight independent field trials or a comparison of strategies. Engine WASM SHA256 `26e68680e45eb0f221db702aead9eefde776c2ad2ba066f4ddf8c12500c6a546`, installed unswbc1.2.3. Compact results contain map/replay hashes; generated replay binaries stay untracked.

## Refined H-H3 test card — prevention before growth

- **Ledger:** proposed refinement of L24/L49, H-H3, weight0.5 unchanged; separate from H-H4 feeding and H-H5 dead-queen fallback.
- **Mechanism:** a full four-cell queen at the unit cap has no split slot and no legal first movement. Before growth fills the pocket, a legal food-free two-step sprint at length3 can spend one segment and preserve space. Test this one intervention only, with observable occupancy, safe path, cap and food timing conditions. Do not infer live bed absence from replay metadata.
- **Falsifier:** no observable precursor or safe route, prevention does not improve exposed queen survival, or paired wins/economy/hygiene fail the preregistered guards. A length2 queen can lose the tiebreak to length3, so survival alone is insufficient and this is not a universal length2 target.
- **Test:** first establish observable trigger and path legality, including food-on-first-step, blocked path and unknown-observation negatives. Then at least60 independent late-food-at-cap exposed fixture pairs, with below-cap and open-component controls. Zero legal-action failures in60 yields a one-sided95% upper failure bound of4.87%; the eight current mechanics checks do not satisfy that sample requirement. For a10pp paired binary win effect, planning n≈149/306/463 at discordance0.2/0.4/0.6, before series/map correlation inflation; report actual exposure and clustered uncertainty. See prior H13/H14 test cards for the paired design.
- **Tester:** Rome after its current04 run, or a director-assigned free tester. No new arm or paused lane started here. Use the existing parent comparison; do not bundle queen feeding, nonqueen fallback and this prevention action.

## Freshness and result reading

Rome03 REJECT and H15-01/02 stand; Rome04 was still running (gen330/1392) at this wake, with no new completed result. H-H5 direct handoff reply remains pending. Nara5e84e7d89, main0298966ec/D-042 and other peers unchanged at inspection. H-H2 switching remains unresolved: no new matched behavior/identity evidence, no spoofing claim.

Raw corpus freeze01:23:26Z: **117,411 games**, lateststart01:19:09Z, +413 sinceunit15 and0new own. Ladder011517Z currenttop10 is264/306/91/213/87/55/566/952/842/507;507 replaces82. Collector35400 healthy40/32/34 per inspected pass,0errors; SQLite read-only succeeds,14585active/14265idle lastseen01:15:16Z. H11-05/H12-05 ingestion requests remain pending; no source/config/deployment changes.

Completed the exact frozen unit12 queue: **110 new games,0errors,412s** over three bounded one-worker passes. Versioned store now **533games/1,066sides**,330ranked/203unranked,18decoder labels. All1,066 side results agree with the official index winner. Window2Oct23:13:00Z–3Oct23:11:43Z; metadata remains unit12's115,442-game snapshot and historical selection cohort, not this wake's entire corpus. All starts post123 cutoff1Oct06:00Z. At the current ladder cohort,538stored sides aretop10 and12own; this is a coverage sample, not stable field percentiles. Matched live-us gaps stay missing. Legacy S1 and norms are untouched. Team/map/mode coverage in the compact artifact; no active Himeji worker remains.

## Reproduction and evidence

From Himeji worktree; MAIN=/Users/alik/Documents/Projects/UNSW-Battlecode-2026, SCRATCH=/Users/alik/Documents/Codex/2026-10-01/p2-a-analyst-one-claude-opus/work/himeji-unit16. Use main analysis Python for the first three read-only queries, isolated work/himeji-venv/bin/python for the fourth:

```text
python tools/himeji/header_fertility_audit.py --repo MAIN --rome /Users/alik/Documents/Projects/wt-rome --out SCRATCH/header-fertility.json
python tools/himeji/pearl_mirror_audit.py --repo MAIN --out SCRATCH/pearl-mirror-audit.json
python tools/himeji/pocket_turn_counts.py --repo MAIN --prior tools/himeji/unit14_audit/pocket-failure-traces.json --out SCRATCH/pocket-turn-counts.json
isolated-python tools/himeji/pocket_legality_check.py --repo MAIN --out SCRATCH/legality
python tools/himeji/summarize_store.py --store OWN_VERSIONED_STORE --snapshot SCRATCH
```

The frozen raw snapshot and large data stay local. `tools/himeji/unit16_audit/` includes compact outputs, official-winner checks, per-team/map/mode store coverage, runtime/replay/source hashes and the last completed build cursor. No simulator from main was used. Next: read Rome04 if complete; otherwise make a new immutable recent ranked selection and inspect H-H3 precursor observability before asking for a performance test. Do not repeat this header audit unchanged.
