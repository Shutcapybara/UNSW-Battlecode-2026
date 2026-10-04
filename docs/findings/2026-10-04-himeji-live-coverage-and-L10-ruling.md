# Himeji unit12 — live coverage correction and L10 ruling

**Our live games are continuing.** Ten ranked games absent from Nara's737-game artifact were collected: five started3Oct21:56Z and five22:57Z, all replay-identified as submission14585. The first five were already in the corpus by22:38Z, before the23:00 watch note. Three of these ten games end in queen-decided losses; on Schooltime995611 we lose with **total249–6**, because the opponent retains queen3 while ours died on its first move. Separately, **L10 remains HOLD/unstacked**: the pre-existing gate specifies checkpoint medians, and neither panel demonstrates a positive gain on that measure. This unit resolves the estimand question, not the wider prospective guard redesign.

## Live availability and submission provenance

Frozen23:23:29Z corpus115,442 games includes747 post-era team7 games:208 ranked/539 unranked. Nara's sample has737:198 ranked/539 unranked. The two added ranked series are:

| Start UTC3Oct | Opponent | Seat | Games | W–L | Reached actual r490 / queen alive | Official RL / terminal queen alive |
|---|---:|---|---:|---:|---:|---:|
|21:56:08|1097|A|5|2–3|3 /0|3 /0|
|22:57:18|776|B|5|1–4|4 /0|4 /0|

All ten replay hashes, header submission IDs and official winners were verified; all20 side terminal queen fields match reconstructed bodies. Opponent submission IDs remain unknown. The database read-only submission registry at23:18Z labels14585 `LV-carthage-05-free-sprint-ebeba55f-ai`, active, and14265 `LV-hb1-14-prior-r540-ed7e4515-ai`, idle. These are observed registry labels, not a fresh source-code equivalence audit. Do not recommend activating or repairing14265 based on an old sample's timestamp. No game or deployment settings were changed.

The hub SQLite `games` table has1,280 records, `series`1,131, `ranked_exposure`20, but **zero game rows for14265/14585**. Its game table is not the public corpus and cannot establish absence of play. Use the registry for the observed submission state and the collector's index/replays for this corpus coverage. The initial connection failed using the system Python; the existing analysis runtime succeeded read-only, with query_only enabled. This is not evidence that the collector lost its connection.

Collector `watch_list` deliberately removes our own team (`out.pop(me,None)`); our ten new games were obtained through opponents1097/776. Accordingly, sparse own-game coverage has an acquisition explanation before any bot-activity inference. H11-05's separate top-team refresh problem persists:264/91 direct checks are~32h old and below their historical targets. Request the keeper to review own-game ingestion/collection alongside the prepared refresh patch, through the sole existing paced collector. Do not start a parallel downloader, restart the executor, or treat a corpus gap as a server outage.

This is a census of the ten newly identified collected games, not a complete live history. Only two independent series are represented, so no reliable population win interval, trend or mode effect is claimed. Ranked/unranked and older own submissions remain separate. Nothing here establishes opponent switching or deceptive intent.

## What the new losses mean

| Ranked game | Map | Own–opponent queen at r490 | Total at r490 | Final total | Official result |
|---|---|---:|---:|---:|---|
|992701|Autarky|0–46|68–46|81–50|queen loss (final0–41)|
|995611|Schooltime|0–3|237–5|249–6|queen loss (final0–3)|
|995614|Australia|0–3|146–148|154–155|queen loss (final0–3)|

All seven round-limit games actually reach r490 (decoder terminal index499). The other three terminate early and have missing r490 values, not carried terminal values. Among the six RL losses, **2/6 have a total lead**; among the two RL games with total leads, **2/2 lose**. These counts hold separately at r490 and at the final checkpoint in this sample. Do not pool those two denominators or infer recoverable wins from a hypothetical queen intervention.

The Schooltime original queen is **ID0 on sideB**. It starts length4, head(3,2), body through(3,1),(2,1),(2,2), issues a one-step north move at round0 and dies by self-collision; no split, sprint length cost or TLE is recorded. Lowest ID must be determined within the team: ID parity is not a reliable queen selector. Our remaining swarm later dominates material but cannot win the queen comparison. The opponent's length3 queen survives and commands200 steps fromr300 onward; preserving a small moving queen suffices in this case.

On Autarky our original queen is ID1 on sideA. It survives untilr319, then dies in an allied head-on collision with ID240 at length3; nearby actions are ordinary one-step moves, with no nearby split. The enemy queen survives to41 and eats39 allied-corpse pearls fromr300 onward. These are distinct failure times and mechanisms. They do not support treating every queen loss as an illegal split or every corpse meal as intentional feeding.

The raw Q3 four-component r50 rows are frozen for both sides of each game. For example, Schooltime own/opponent bed pearls4/7, splits3/5, commanded portal transits6/0, territory0.779/0.221. Dominant early territory and late material do not ensure conversion. These are opponent comparisons on individual maps, **not** field percentiles or current-top10 targets. Neither opponent is in the frozen top ten; matched top10-minus-us remainsNA.

Guidance to Rome's L39/L49 experiment: report queen alive at the first conversion trigger, games with no trigger, trigger timing, and final queen growth conditional on exposure alongside all-game wins and economy guards. A late intervention cannot preserve a queen already lost at r0; distinguish non-exposure from failure after exposure. The existing H-H1 production-preserving split hypothesis/falsifier and size rationale stay unchanged, weight0.5. This audit requests diagnostics, not a new bot implementation, gate exemption or promotion.

## L10: resolve the estimand before considering new guards

Rome6f1ec3527 completes480 pool and1,392 gen paired fixtures. Himeji independently reads the four saved feature files, checks complete unique seed/map/opponent/seat pairing, reproduces all W–L–D totals and point estimates, and resamples the pairs with2,000 fixed-seed draws. No simulator or re-extraction ran here; authoritative-result provenance is Rome's FRAME_VERSION7 extraction, with feature hashes frozen by Himeji. The parent official counts were already independently header-audited in earlier units.

The lane contract at **ad611b51c**, before this final re-read, explicitly defines `econ~` as the mean over four checkpoint medians of normalized side-game pearls. Its bootstrap and gate use `econ~`; arithmetic `econ_mean` is reported separately. Clair's revision changes which panel can demonstrate benefit and makes cluster uncertainty authoritative; it does not replace the estimator. D-042's win-led exception covers predeclared1.2.3 adaptations and does not automatically reclassify L10.

Himeji's ruling: **use the preregistered median-checkpoint economy estimator for L10.** Preserve the arithmetic-mean result as a useful diagnostic; do not choose it because it passes. A prospective estimator change requires a separate rule and historical rescore, not retrospective selection for this arm.

| Panel | Parent → candidate W–L–D | Median economy delta | 90% interval: map×opponent×seat | 90% interval: seed×map |
|---|---|---:|---:|---:|
|Pool480|396–83–1 →399–80–1|0.0000|[−0.00180,+0.00054]|[−0.00210,+0.00119]|
|Gen1392|1036–356–0 →1033–359–0|−0.00418|[−0.01265,+0.00795]|[−0.01396,+0.01079]|

The first clustering groups all three seeds for each map/opponent/seat (160/464 clusters), matching Rome's reported form. The second groups all opponent/seat fixtures sharing a seed/map (30/87 clusters), addressing BENCHMARKS' shared-layout rationale. These are alternative sensitivity analyses, not interchangeable independent observations. Both fail the positive-economy requirement. Pool win delta+0.625pp has intervals[−0.219,+1.667]pp and[−0.625,+1.875]pp; neither meets the borderline exception's **lower bound>+2pp**. Gen win delta−0.216pp has intervals[−0.934,+0.503]pp and[−1.006,+0.575]pp.

Arithmetic-mean gen economy is+0.008666 with map/opponent/seat90%[+0.002564,+0.014919] and seed/map[+0.001337,+0.015664]. The difference from the median estimand is real and reproduced, but not an acceptance choice. Gen units/total@100 median-change lower bounds are−0.02202/−0.03314 under the first clustering and−0.02500/−0.03673 under the second; these cross the existing−0.02 safeguards. The units-guard redesign remains a prospective question, but **cannot rescue L10's absent median-economy gain**.

Rome's enemy-head-on diagnostic improves on gen (reported−0.415/1k dragon-turns,90%[−0.556,−0.269]); this supports a behavioral effect, not a per-contact hazard reduction or overall win benefit. Its displayed scorecard uses median hygiene rates while its lane gate uses mean per-game rates; retain and label both rather than selecting one mid-test. The new guard proposal must specify weighting as well as its functional form.

Verdict: agree HOLD/unstacked; no acceptance and no repeat experiment is needed merely to settle the estimator. Keep Rome's published numbers/historical verdict intact and append this ruling. Its next queen-conversion arm stays on the measured parent, as Rome already planned.

Implementation note for reproduction: current zoo filenames encode gen map keys with an underscore (`new_mc26_...`), whereas the frozen reference uses a plus (`new+mc26_...`). The audit explicitly maps the first separator and asserts every reference exists. Missing references must not silently become a unit denominator. No shared normalizer or feature file is changed.

## Freshness and next action

Snapshot23:23:29Z index SHA43d6b876a97b36ed4b2f38f81e7a644915300e38057f73df9104bae90f18bdc7, latest start23:22:18Z; ladder231820Z SHAacb0c399837d3243494bf0b4dba7058abffdbe44d2cf8188962a455a07f599a6. Currenttop10 IDs306/91/264/213/842/952/87/82/55/566;55 replaces552, so preserve old cohort labels.

Read-only DB connection verified; sole collector PID35400, recent passes19–40 downloads,0 errors; executor remains shadow. Two store workers added92 games in171seconds,0 errors, then checkpointed. Separate v7 store now**423 games/846 sides**, all846 winner labels match the index;472 current-top10 sides/12own. Window2Oct23:13Z–3Oct23:11:43Z. Of202 selected new games,110 remain; resume the same immutable unit12 snapshot before replacing its work queue. No worker remains active. Legacy store/norms and main source unchanged.

Main0298966ec/D-042; Antioch2c7113f66; Carthage5b69fa9d0; Kyoto fccea71c0 unchanged. New Rome6f1ec3527 L10/result and next queue read; Nara7105552fe23:00 watch note read. Himeji boardH12-01..07. No direct Nara/Antioch chat appears in the app inventory; addressed branch-board replies remain the analyst communication route. Rome's existing chat is active; no paused lane is restarted or new chat created.

Next: read replies/results and inspect collection; finish the110-game saved decode queue if no higher-priority correctness issue arises, then current ranked map-structure/Q3 references with whole-series uncertainty and actual checkpoint reach. Frozen references stay provisional. No new field percentile target, causal weight update or spoofing verdict is justified by this unit.

## Queries and evidence

All compact results and source hashes are under `tools/himeji/unit12_audit/`. The full immutable index remains local; replay hashes and precise selection permit reconstruction. Use the existing analysis Python. MAIN and ROME are read-only source checkouts; SNAP is the unit12 scratch directory; HIMEJI is this worktree.

```sh
python tools/himeji/recent_live_check.py --repo "$MAIN" --himeji "$HIMEJI" --snapshot "$SNAP" --prior tools/himeji/unit11_audit/audit/live-header-rows.jsonl
python tools/himeji/own_queen_events.py --repo "$MAIN" --snapshot "$SNAP" --games 995611,992701
python tools/himeji/rome_estimand_check.py --rome "$ROME" --out NEW_AUDIT --draws 2000
python tools/himeji/resume_store.py --repo "$MAIN" --snapshot "$SNAP" --store LIVE_STORE --jobs 2 --seconds 160
python tools/himeji/summarize_store.py --store LIVE_STORE --snapshot "$SNAP"
```

Every case here is post06:00Z1Oct; local L10 is explicitly1.2.3 and separate from ranked live. Per-game raw rows contain maps and checkpoint fields; early ends stay censored for r490. Counts in the two live series are descriptive, and no inferential current-field gap is filled with them.
