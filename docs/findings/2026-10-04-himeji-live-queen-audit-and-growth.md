# Himeji unit 11 — live queen audit and growth, 4 October 2026

The exact 737-game team-7 sample contains **72 queen-decided games: 70 losses and 2 wins**. Nara's probe excluded `queen` from its round-limit reason filter (line46 at4219c1b63), omitting precisely the outcomes it sought to measure. Official headers give **398 round-limit games, not326; terminal queen survival2/398, not0/326**. This corrects the claim that no games have yet been lost to the queen tiebreak. It does not measure wins recoverable by a queen intervention.

## Exact sample correction

All737 replay SHA256 values match the frozen corpus index; all official winners match the index. Counts below are a census of Nara's frozen sample, not independent trials or a representative field estimate. No confidence interval is needed for the accounting identity; future-population precision is not established. The sample runs1Oct16:59:38Z–3Oct05:43:11Z, entirely after the06:00Z1Oct era boundary. Preserve this population separately from the new recent-store sample.

| Own header submission | Mode | Games / series | Wins | RL games | Queen alive at RL end | Queen-decided losses |
|---|---|---:|---:|---:|---:|---:|
|14265|ranked|138 /29|78|74|1|5|
|14265|unranked|363 /44|88|175|1|22|
|14585|ranked|60 /14|34|40|0|9|
|14585|unranked|176 /25|39|109|0|34|

The two queen wins are832740 (ranked Trauma,20–0 queen) and845908 (unranked Schooltime,27–0). Nara's existing rows already record their r490 lengths20 and25, but its filter removes both. This audit uses **official terminal fields**, not clipped r490; no pooled r490 survival estimate is inferred. Submission IDs are observed headers; the build corresponding to14585 is not asserted from naming or timing. Pooled ranked112/198 and unranked127/539 reproduce, but each blends two own versions and different opposition. They cannot establish a mode effect, switching or current-build strength.

Material-lead conversion at the **final RL state**, with both denominators explicit:

| Submission / mode | Losses with final total lead / RL losses | Losses / final total leads |
|---|---:|---:|
|14265 ranked|14/39|14/39|
|14265 unranked|18/134|18/41|
|14585 ranked|6/19|6/16|
|14585 unranked|13/88|13/26|

A final total lead is total length greater than the opponent's, regardless of queen/longest. These are not r490 lead rates or a causal decomposition. All maps remain separate in the raw rows; map-matched live-us gaps remain missing. Nara's ranked-only ten-map claim is also false: its own198 ranked games contain **17 map names**, including Maze5, Around UNSW4, Islands4, Australia4, weakhold5, Tower Defense2 and Stripes4. Use actual map hash/initial geometry and era, not a historical map-name whitelist.

## Four selected ranked queen-growth traces

These are deliberately selected surviving long queens from unit10, **not a random sample or percentile target**. All four reach the actual r490 checkpoint, terminate at round limit, win officially by queen, and have matching header/body final queen lengths. Decoder last_round is499; do not call the terminal state r500 without declaring indexing.

| Game / team / map | Queen birth→r490→end | Queen splits | Move rounds / multistep | Queen food: bed / ally corpse / enemy corpse |
|---|---:|---:|---:|---:|
|929650 /306 /Slithery Fight|25→35→37|2|498 /173|7 /76 /0|
|990578 /91 /Slithery Fight|25→66→73|13|487 /125|15 /58 /1|
|990728 /91 /Maze|4→35→35|10|490 /51|17 /30 /4|
|993136 /306 /Maze|4→121→123|5|495 /170|84 /50 /0|

All recorded multistep queen moves incur zero decoded sprint length cost in these cases. Queens move almost every round; preservation need not mean parking. On Slithery Fight (hash c8e8fa61335b), there are14 initial robots and the original queens start length25. Team306 sheds22 at round0, keeps a small queen throughr300, then grows; team91 sheds length2 repeatedly throughround10, sits at length3 throughr200, and reaches66 byr490. On Maze (8202a09f96a4), team91 remains length3 at r400 before late growth; team306 grows much earlier (19 atr200,76 atr400). This supports multiple production/growth schedules, not a universal long queen from birth.

Food provenance shows substantial allied-corpse use. Team306's42 and36 contributing donors in these two games all die with `invalid` labels; **zero explicit suicide commands** are observed for those donors. Team91's32 and11 contributing donors include10 and2 explicit suicide commands, respectively. Neither a corpse meal nor an invalid death proves that the bot intended to feed its queen. Inspect action sequences, opportunity costs and matched controls before claiming deliberate provisioning. Game990728 is a concrete conversion example: team91 wins with queen35–0 while trailing final total72–208 and longest35–53.

These examples refute a blanket claim that current Slithery queens cannot survive. They do not retroactively invalidate a particular old spawn configuration or local panel. Keep historical observations and key exclusions to actual geometry.

## Readings and disagreements

- Accept Nara's withdrawal of the0/62→23/84 survival and deliberate-cull claims, plus its admission that the five original IDs cannot be recovered. The old request is closed as withdrawn, not independently reconstructed. Corrected0/31→9/31 and2/9 are the frozen historical observations.
- Disagree that team306's current #1 ranking proves the identity or causal merit of a two-day-old build. Opponent submission identity is still unknown. The four fresh traces strengthen the case for testing queen conversion, but ranking plus selected survivors is observational. Retain Nara's proposed N6 weight alongside this disagreement; Himeji does not adopt its causal claim or raise H-H1's0.5 weight.
- Nara's proposed paired log units/total guard needs an explicit statistic, zero/extinction policy, checkpoint reach handling, paired resampling unit and calibrated rejection controls. A normalized units LB−.146 cannot be compared directly with a log bound−.10; −.10 on log scale corresponds to about−9.52%. Mean paired log change and log median ratio also differ. Retain the D-042 gate/guards until the proposed form is defined and rescored on the rejected Carthage02/03 and a known correctness baseline. Ask a tester to run that decisive existing-data comparison; no new bot experiment is authorized here.
- Rome's existing chat has resumed L10; no new completed official gate result was available at this unit's check. No lane is restarted or messaged merely to obtain a reply. H10-06 reading stands.

No new field target or hypothesis weight is established by this audit. H-H1 retains its production-preserving queen-split mechanism/falsifier and tester pairing; its prior sample-size rationale remains149/306/463 independent paired fixtures for a10pp binary effect at discordance .2/.4/.6, before cluster inflation. H-H2 switching remains unresolved: match map hash, seat, opponent and time, retain unknown IDs, and seek repeatable switch/revert patterns. A ranked/unranked win gap alone cannot identify intent.

## Connection, collection and store freshness

The existing hub daemon remains sole collector. Read-only SQLite connectivity succeeded; inspected passes downloaded40 games with0 errors and the cycle/ladder were fresh at22:47Z. No credentials, deployment settings, submissions, service restarts or main source were changed. Frozen index at22:52:55Z has114,593 games, latest start22:51:49Z. Ladder224700Z top IDs306/264/91/213/87/842/82/952/566/552.

Eight of ten leaders have caught up on direct checks. Team264 has3,841/4,000 historical target games and was last checked2Oct15:22Z; team91 has2,876/3,000 and last checked15:09Z (~32h stale). These teams still appear in other teams' collected matches, so a stale direct check does not mean no recent games exist. The source's refresh filter excludes teams below their historical target; backfill prioritization can strand leaders just below that target. A focused **undeployed patch** includes below-target teams in refresh and prioritizes top10 checks older than15minutes, retaining the paced shared client and existing limits. Pure selection checks confirm a stale below-target leader goes first and a fresh leader does not displace unchecked nonleaders. Deployment requires the keeper's authorized service workflow; this unit only supplies the patch and evidence.

The separate FRAME_VERSION7 store grew119→**331 games /662 sides**,212 new decodes,0 errors. All662 results match official index winners. Decoded window2Oct23:13:00Z–3Oct22:50:10Z;365 current-top10 sides and7 own sides,18 decoder map labels. This is a balanced coverage sample, not a field census or a stable reference. Source hashes are unchanged and pinned; legacy S-1/norms remain intact. No query is running. Next unit: fresh matched ranked references/Q3 by actual structural signatures and explicit r490 reach; continue collection freshness checks. Do not rerun the737 audit or four traces unchanged.

## Reproduction and frozen evidence

Main source0298966ec; Nara4219c1b63; Antioch2c7113f66; Carthage5b69fa9d0; Kyoto fccea71c0; Romead611b51c plus resumed chat. Board source mainD-042 and Naraunit4; new HimejiH11-01..07. Snapshot index SHA8cd12a04ae180bcf6240de03c9200619216f69db87a79e1b54855977df767626; ladder SHAd863ead567e2f3db9c0947b98201ffdcd422288ea2639c3ac580c4ff0a28bbe0. `tools/himeji/unit11_audit/` contains the frozen737 rows, official-header audit, four event traces, source manifest, coverage summary and undeployed patch. Replays/index/parquet are local only; no blobs or credentials committed.

Queries (use the main analysis Python for decoder dependencies; MAIN is the read-only main source checkout and SNAP the frozen unit11 directory):

```sh
python tools/himeji/audit_live_labels.py --repo "$MAIN" --index "$SNAP/index.jsonl" --nara tools/himeji/unit11_audit/audit/nara-own-rows.jsonl --out NEW_AUDIT
python tools/himeji/summarize_live_audit.py NEW_AUDIT
python tools/himeji/queen_trace.py --repo "$MAIN" --index "$SNAP/index.jsonl" --out NEW_TRACES --games 929650,990578,990728,993136
python tools/himeji/summarize_store.py --store LIVE_STORE --snapshot "$SNAP"
python tools/himeji/collector_patch.py --repo "$MAIN" --out PATCH_REVIEW
```

The frozen subset can reproduce all737 results even if Nara's working file changes; its input hash will differ from the original full-file hash recorded in live-manifest. Use a new audit directory for that reproduction. The store builder's selected IDs and decoder hashes are frozen in last-build/decoder-source manifests; no shared norm helper is invoked.
