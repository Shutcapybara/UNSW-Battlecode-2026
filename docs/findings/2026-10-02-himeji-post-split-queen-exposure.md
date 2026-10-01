# Himeji unit 3 — post-split queen exposure, not just death counts

Published 2026-10-01 15:36 UTC. **Rome's seed-1 base shows a strong association between recent splits and queen death.**
This is replay analysis, not a bot experiment, a causal estimate, a live-field target or a gate change.

## Cohort and denominator

Frozen panel `z1-rome-01-nodevil-28132ee5`: all **160 seed-1 pool games**, ten maps × eight opponents × both seats,
engine **unswbc 1.2.3**. We analyse only Rome's original queen. Exclude the 48 Autarky, Prisoners Dilemma and Slithery
pocket-map games from the main comparison; retain them in the data. The analysis population is **112 games** on seven
maps. There are 99 observed queen deaths in these games; the 13 other queens survive their game, which may end early.

A risk round is an actual start-of-round snapshot with the queen alive, through the last played round. Death is
counted in that same round. The exposed window is rounds **s+1 through s+3** after the most recent queen split at s.
Rounds containing another split are a separate bin, excluded from the exposed/other ratio to avoid ambiguous event
ordering within a round. Multiple recent windows never double-count a round. End-of-game extra snapshots are excluded.
No terminal state is carried forward. This includes **all queen splits**, not specifically production splits: replay
events do not identify the bot's rescue-versus-production decision. Excluding pocket maps does not remove every rescue.

| Queen-alive round category | Deaths / risk rounds | Deaths per 1,000 rounds |
|---|---:|---:|
| 1–3 rounds after a split | **45 / 1,249** | **36.03** |
| Other rounds, excluding split rounds | **53 / 12,224** | **4.34** |
| Round containing a split (separate diagnostic) | 1 / 470 | 2.13 |

The recent-split window is 9.0% of all 13,943 at-risk rounds but contains 45.5% of the 99 deaths. The crude rate ratio is
**8.31 [5.80, 12.23]**. Intervals are **95% bootstrap intervals**, 1,000 resamples, seed 20261002. Resample the eight
opponent fixtures within each map with both seats kept together: 56 fixture resampling blocks, not 112 independent
games or 13,943 independent rounds. This describes uncertainty within this one seed's fixed map/opponent panel; it does
not measure variation across seeds, unseen maps or future field bots.

## Map and state comparisons

Each map below has 16 games. Counts are queen deaths / queen-alive risk rounds. Small map-specific death counts do not
support precise per-map effect sizes; the ratios are descriptive, not targets.

| Map | Recent split | Other | Crude rate ratio |
|---|---:|---:|---:|
| Default | 2/187 | 10/2340 | 2.50 |
| Devil | 7/122 | 5/975 | 11.19 |
| Portals | 10/254 | 6/1221 | 8.01 |
| Queen Of Spades | 6/132 | 6/2468 | 18.70 |
| Schooltime | 5/247 | 11/1493 | 2.75 |
| Trauma | 13/204 | 2/2569 | 81.86 |
| Trophy | 2/103 | 13/1158 | 1.73 |

Mantel–Haenszel incidence-rate ratios retain only strata with both exposure types:

| Grouping variables | Rate ratio [95% fixture bootstrap] | Recent / other risk rounds retained |
|---|---:|---:|
| Map + phase | 6.96 [4.87, 9.43] | 1,249 / 12,179 |
| Map + phase + queen length | **7.24 [5.03, 10.08]** | 1,249 / 11,832 |
| Above + nearby ally body + nearby enemy head | 7.09 [4.46, 10.66] | 1,245 / 11,536 |

Phase bins are r0–49, r50–149 and r150+; length bins are 2–3, 4–7 and 8+. Nearby means toroidal Chebyshev distance:
any other ally body within two cells; any enemy head within three. This is geometric proximity, not path reachability
through walls/portals or proof of collision risk. Current length and local density can themselves be consequences of a
split. Conditioning on them is a descriptive robustness check, **not confounding control sufficient for causality**.
Rescue selection, imminent entrapment and policy decisions remain unmeasured. Trauma dominates some raw contrasts;
Trophy's association is only 1.73, so do not turn the pooled number into a uniform map law.

Recent-split deaths: wall 19, ally body 10, ally head-on 6, enemy head-on 5, self 5. Other-round deaths: enemy head-on
33, wall 8, ally body 4, ally head-on 4, self 4. Thus **35/45** recent-split deaths are wall/ally collisions. This is
cause composition conditional on death, not a cause-specific treatment effect. One ally head-on occurs on a split round.

## Mechanism reading and next test

**H-H1 (proposed L24/L39, weight remains 0.5)** gets a more specific diagnostic: death risk concentrates immediately
after splits even within coarse map/phase/length strata. It still does not establish that retaining a larger queen head
piece prevents those deaths, nor that extra retained length is worth lost offspring material. The queen may split because
it is already trapped. Carthage 02's large production penalty still rules out treating blanket no-split as a cheap fix.

Next measurement is a **frozen replication on Rome seeds 2–3**, same definitions and exclusions, with seed/map/opponent
fixture blocks. Do not choose windows or bins after seeing those data. Ask testers to distinguish production and rescue
splits in their own traces when feasible; otherwise keep the all-split label. A failure to replicate the positive
association across seeds weakens this diagnostic; it does not by itself falsify the retained-head intervention.

Decisive policy test remains a production-preserving retained-head split versus the same base, suited to Rome after its
baseline or Carthage's next split-specific arm. Keep both panels, seeds 1–3 and paired fixtures; report queen survival,
production and **overall win**, not only round-limit wins. Existing H-H1 falsifier: upper 95% bound of survival gain <=0
or upper bound of overall-win gain <0; show a production advantage over blanket no-split. For a 10pp binary effect,
unit-1 planning counts were about 149/306/463 independent pairs at discordance .2/.4/.6, before clustering. The 56 fixture
blocks here cannot be relabelled as that powered intervention test. This unit proposes no new bot and no ledger edit.

## Reading Carthage 07

Source `origin/r/carthage` **da39a6922**, report `2026-10-01-carthage-base-and-queen.md`. Agree with rejection: queen
survival is 0% in both panels; ally kills 62→65 do not support the intended mechanism. Pool economy improves
**+0.029 [+0.011,+0.052]**, but gen economy **−0.041 [−0.064,−0.021]** and gen win **−0.040 [−0.061,−0.013]** are adverse.
These quoted intervals are Carthage's 5th–95th percentiles (90% central intervals). The opening-spacing interpretation
is plausible, not isolated by the treatment: this arm changes both queen and non-queen movement.

The correction from base enemy/ally kills **112/62** to 06's **45/97** matters: the dominant remaining cause depends on
the prior intervention. **07 has parent 00, not 06**, so it does not directly test whether yield repairs 06's new failure
mode. A later 06+yield versus 06 would isolate that interaction more clearly; this is guidance, not a request to interrupt
the already queued arms. Carthage 08 (avoidance+guard) and Kyoto's revised stack also differ because Kyoto includes
no-production-split/tail-shedding changes; do not label them exact replications. No new Rome/Kyoto panel outcome or
Nara/Antioch reply was available at this unit's source cutoff.

## Reproduction and provenance

Run `tools/himeji/split_exposure.py --repo <wt-himeji> --panel <Rome fingerprint directory> --out <private-output>
--jobs 2`, then `tools/himeji/summarize_exposure.py <private-output>` (join the first command onto one line).
The query reads existing cache files only if their path/size/mtime/frame-version key matches; it never calls a cache
helper that writes shared data. All 160 matched existing F1 v5 caches. A fresh decode of the first selected replay was
identical for rounds, events, last round and geometry. Official results are read independently from the replay header;
old cached winner inference is not used. All 160 runner index records say 1.2.3, successful execution, seed 1. All ten
maps have exactly 16 games, every recorded queen death is allocated exactly once. No replays, shared caches, bots or
store data were changed. Two read-only workers were used; both have finished.

Compact outputs, per-replay SHA256 values and the panel-index hash are under `tools/himeji/split_audit/`.
Panel-index SHA256: `7e2f52b379ab23d6d4c81acd50291c60c843a8929d1b848f2a490278815a0896`. Per-replay hashes make changed replay inputs detectable;
outputs checkpoint per game. Resume only the same immutable panel; choose a fresh output directory for different inputs.

Source cursor: main cb2e920c7; Antioch ed714f51e; Nara 762ae51df; Kyoto 5d7f3863b; Carthage da39a6922; Rome local status
pool 480 complete, gen 800/1392. Protocol, all five statuses and changed board/targets were read. Corpus freshness:
**78,650 unique games**, latest start **2026-10-01T15:28:47.994Z**, index SHA256
`0fe80789725020f90ee9c945078d75bd78b952d594c7f0ae1e0dd161906c568e`; **0 post-era team-7 games**; ladder remains `20261001T062107Z.json`.
Mac store last verified unit 2: 58,040 games through Sep30 10:26:08Z, no era column. The requested post-store sync,
ladder refresh and Nara's five claimed Cutlery IDs remain outstanding. Himeji's live-field targets stay frozen and
provisional; local panel rates above are not substituted for live-us percentiles.
