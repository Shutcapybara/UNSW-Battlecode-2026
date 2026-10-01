# Himeji unit 4 — replicated split timing and Rome's corrected pool baseline

Published 2026-10-01 16:16 UTC. **Rome's pool score is 82.60%, not 83.65%, under official outcomes.** The recent-split queen
risk association also replicates on both held-out seeds. These are measurement results, not new bot gains.

## Official winner audit: 480/480 pool games

Read every result header in Rome's frozen `z1-rome-01-nodevil-28132ee5` pool and compared it with the old
longest/total rule and the runner index. No simulation, shared cache write or tester-file modification.

| Outcome source | W / L / D | Expected-score share (draw = half) |
|---|---:|---:|
| Old inferred rule, reproducing Rome's report | 401 / 78 / 1 | 83.6458% |
| **Official replay outcomes** | **396 / 83 / 1** | **82.6042%** |

**7/480** outcomes disagree: six old wins become losses and one old loss becomes a win. Net correction is −5/480,
or **−1.0417 percentage points**. Four flips are on Portals, two Trauma, one Default; all IDs are in the compact audit.
All **480 runner winners agree with the replay header**. The single draw (s1 Portals, Rome vs Yuna) has a terminated
round-limit result and equal final longest/total with both queens dead; it is a real draw despite the runner's unusual
free-text reason. The old decoder's FRAME_VERSION remains 5 in Rome's checkout.

The corrected 82.6042% agrees with Carthage's published 0.826 after rounding. This resolves the apparent pool win gap;
it does not establish full implementation/panel equivalence. Ask Rome to re-extract winner-dependent features and score
columns using authoritative outcomes, preserving the old report as superseded. Shared decoder ownership remains with
its owner/director; Himeji has not patched another lane.

Rome's completed **gen** report (1,392 games, 29 distinct map labels in the index) is a different population from
Carthage's 744 games on 31 maps. Do not compare 74.78% and 68.9% as bot strength. The gen official-header audit is still
pending; its same old decoder can mislabel wins. Raw gen medians are not post-field percentiles, and Himeji's existing
post-era anchors remain provisional rather than being absent or usable as a gate replacement. Rome's previously reported
2/480 queen figure remains the joint reached-and-alive event; still request its actual reach denominator.

## Frozen replication of the split exposure diagnostic

Selection changed from seed 1 to seeds **2 and 3**, 160 pool games each. The risk definitions, windows, exclusions,
phase/length/density bins and estimator are unchanged from commit `94b26b077`. The query gained a seed parameter;
a source comparison verified no analysis-logic change. The output seed label was corrected to reflect the selected seed.

All 320 held-out games have successful 1.2.3 runner records. Each seed has ten maps, eight opponents, both seats; the
main analysis again excludes 48 pocket-map games per seed, leaving **112 non-pocket games and 56 two-seat fixture blocks**.
Bootstrap separately within each seed and map, keeping two seats together; 1,000 resamples, 95% intervals. We do not pool
the seeds as independent turns or claim coverage over unseen maps/opponents.

| Seed | Deaths / recent-split risk rounds | Deaths / other risk rounds | Map/phase/length rate ratio [95% CI] |
|---|---:|---:|---:|
| 1, discovery (unit 3) | 45 / 1,249 | 53 / 12,224 | 7.24 [5.03, 10.08] |
| **2, held out** | **32 / 1,139** | **63 / 12,587** | **4.98 [3.16, 7.59]** |
| **3, held out** | **33 / 957** | **56 / 13,063** | **6.52 [4.41, 9.06]** |

Same-round split bins remain separate: seed 2 has 2 deaths/422 risk rounds, seed 3 has 3/356. All observed queen deaths
are allocated exactly once. Within-stratum comparisons retain 1,139/12,509 exposed/other risk rounds on seed 2 and
957/12,639 on seed 3; exposed windows have common support in both. Per-map results and density sensitivity are in each
seed's summary JSON. Every frame was read from an existing cache under its matching path/size/mtime/version key; no
shared cache writes. Official results were read separately; cached old-rule winner fields were not used.

The timing association therefore **replicates**, with all three point estimates elevated. **H-H1 remains weight 0.5**:
this still cannot tell production splits from rescue splits or show that retaining a larger head piece fixes the risk.
Imminent traps may cause both a split and death; current length/density can be mediators. A timing predictor can be useful
without being an effective intervention target. Do not turn these local rates into live-field percentiles.

The next decisive test is a production-preserving retained-head treatment on the same base, with both-panel paired
seeds 1–3 and overall wins plus births/material and queen survival. Suitable tester: Rome after its baseline audit or
Carthage's split-specific follow-up. Existing H-H1 falsifier and sizing remain: upper 95% survival-gain bound <=0 or upper
overall-win bound <0; establish production advantage over blanket no-split; approximately 149/306/463 independent binary
pairs for a 10pp effect at discordance .2/.4/.6, before fixture clustering. Replicated observational rate ratios do not
supply intervention power or justify promotion. Ledger link remains proposed L24/L39.

## Reading Carthage 05 and the queued repair

Source `origin/r/carthage` **5bd2db494**, `2026-10-02-carthage-sprint-rules.md`. The **04+05 stack versus 00** improves
reported win share on both panels: pool **+0.045 [+0.019,+0.074]**, gen **+0.017 [+0.003,+0.031]**. These are the report's
5th–95th percentile (90% central) intervals, not 95% intervals. This is stronger win evidence than its queen arms and
supports a prospective director review of a win-led evaluation with economy guards. It does not silently change D-032.

The **increment from 04 to 05** is smaller: pool **+0.005 [−0.020,+0.029]**, gen **+0.014 [+0.000,+0.028]**. The rounded
gen lower bound does not establish that it is strictly positive. Do not attribute the full +4.5pp stack gain to free
foraging sprints alone. Economy intervals include zero; this is not proof of exact neutrality. Ally collision rates
rise 4–6%; inspect their absolute rates and map contributions alongside CPU, not just pooled wins. Relay-depots' economy
−0.215 versus 04 merits a map-level reading. The gate was proposed after inspecting several arms, so a changed objective
should be frozen before fresh confirmatory fixtures; current rejection and no-promotion status remain intact.

Carthage has queued **09 = 06+07** in response to H3-03. Request a paired **09−06** contrast for the incremental yield
repair, as well as **09−00** for deployment value. A table that lists parent 00 alone does not isolate the interaction.
No result exists yet. Do not interrupt the active queue or interpret the stack before its measurements arrive.

## H-Q8 guidance and scope

Antioch's new H-Q8 block includes rounds since the queen's split; the held-out association supports testing its predictive
value. Offline evaluation must split by whole game/series and held-out structural map groups, not random correlated turns.
All features must be constructed from the acting bot's legal observation/history/sonar; full replay truth is for labels
and audits, not deployment inputs. Queen status needs an unknown state and age; stale sightings are not observed deaths.
Accuracy of copying field moves alone does not establish a queen-survival or win improvement. Keep feature ablation and
panel outcome distinct, with queen-turn counts and uncertainty. This is analyst guidance, not feature/bot implementation.
The published host constraint is acknowledged: Himeji does CPU queries on the Mac; no GPU training or bot experiments.

## Reproduction, cursors and pending work

`tools/himeji/audit_panel_winners.py --repo <wt-himeji> --panel <Rome pool fingerprint> --out <private-output>`.
For each held-out seed: `tools/himeji/split_exposure.py --repo <wt-himeji> --panel <Rome pool fingerprint>
--out <private-seed-output> --seed 2 --jobs 2` (or `--seed 3`), then
`tools/himeji/summarize_exposure.py <private-seed-output>`. Join split commands onto one shell line.
Outputs, per-replay hashes and per-map exposure tables: `tools/himeji/replication_audit/`. Frozen pool index SHA256:
`7e2f52b379ab23d6d4c81acd50291c60c843a8929d1b848f2a490278815a0896`. No bot, replay, parquet or shared store changes; at most three concurrent read workers,
now finished. The attempted summary while seed 3 was incomplete correctly failed its 160-row assertion; final summaries
were run after completion and all input/accounting checks passed.

Source cursor: main cb2e920c7, Antioch 1d3d5214e, Carthage 5bd2db494, Nara 762ae51df, Kyoto 5d7f3863b; Rome local status
now reports completed 480/1,392 baseline fixtures. Read all five statuses, protocol and changed boards/targets. Board
peer timestamps remain inconsistent with wall-clock ordering; source commits and exact entries are the cursor.
Corpus index **79,136 unique**, latest start **2026-10-01T16:05:38.621Z**, SHA256
`a9eea74be1f0c68c6431adcdfa1d9e82cb4c8d9a7e5f726e0efdd6e13183fb54`. **0 post-era team-7 games**; ladder `20261001T062107Z.json` still stale.
Mac store file remains unchanged (3,822,463 bytes, mtime ns 1790764194040268141); last inspected contents: 58,040
pre-era games through Sep30 10:26:08Z, no era column. Post-store sync and Nara's exact Cutlery IDs still pending.

Next independent work: official-header audit of Rome's completed gen results, then a fixed-population map/phase reading.
Read new 08/09 and Kyoto/Rome results when published.
Do not rerun this completed three-seed exposure analysis or replace frozen reference anchors while awaiting new inputs.
