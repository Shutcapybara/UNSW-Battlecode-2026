# Kenma free lane

State: **ACTIVE**, updated 2026-10-05 04:45 UTC. Branch r/kenma; worktree /Users/alik/Documents/Projects/wt-kenma. Keep iterating until told to stop. No contest API, key access or submission. A bounded03 ladder trial was requested04:30 and Chair-approved04:33; Live ops owns execution.

## Provisional best

**kenma-03-pocket-queen**, runtime e60733a926fc056a6cd596582c64c535e461a18679ae1d97f4a725a4cb4612a1.
- Carthage **58–44/102**; Kageyama **61–41/102**; current live Asahi05 **57–45/102**; 17 ranked maps × both seats × seeds1–3, zero errors.
- Zoo **220–52/272**, zero errors, six fewer wins than supplied Carthage226–46 reference. Same-host parent diagnostic64 exactly matched reference57–7 versus03 at49–15 on the same fixtures; pool deficit confirmed on those maps, no promotion claim.
- Four heavy-map sandbox games: max **10,910,667** points, first-turn max10,814,937, zero errors. Zip3,923,010 bytes.
- Extra Schooltime seed5 check **2–0**, both queens survive500 rounds, zero errors, sampled population63. Reserve-slot burst risk is not disproven.
- Full by-map/opponent scorecard in bot README. Outputs main build/kenma/k03-v-carthage-s123/, k03-v-kageyama-s123/, k03-zoo-s1/, deploy/kenma-03-pocket-queen/, k03-schooltime-s5/.
- Best/full scorecard reported on main BOARD. Bokuto04 requested cross-match queued; newer Bokuto07 reported60–42 versusCarthage04:33, its full scorecard remains pending. Reserved **seeds11–13 and new maps remain untouched**.

## Candidate record

Completed Carthage screens use the same102 fixtures and have zero errors.

| Version | Change | Carthage W–L | Disposition |
|---|---|---:|---|
| 01 free-combat-sprint | Combat free triples | 48–54 | Rejected |
| 02 topteam-prior | A1-400 development direction model | 42–60 | Rejected |
| 03 pocket-queen | Proven sealed-pocket rescue, donor culling, one reserved slot | 58–44 | Provisional best |
| 04 keeper-action | Seven-class queen imitation from round0 | 50–52 | Rejected |
| 05 post-opening-keeper | Same clone starts round25 | 54–48 | Rejected |
| 06 pocket-space | 03 plus exact AsahiK16 space-filter sources | 57–45 | Rejected |
| 07 keeper-moves-parent-splits | 04 with parent split decisions preserved | 51–51 | Rejected |
| 08 lossless-direction | Reversible32-bit direction node encoding | Equivalent control | Native exact parity and four sandbox games passed |
| 09 learned-donors | Teacher306 nonqueen cull classifier | 57–45 | Rejected; three changed summaries, one win lost |
| 10 short-queen-orbit | Local four-cell keeper loop | Cancelled | Wrong freshness convention; source/attempts retained |
| 11 current-view-orbit | Fix freshness, add activation logs | Smoke2–2 | Zero activations; wrong no-bed convention; frozen |
| 12 observed-empty-orbit | Require observed no-bed=-1 | 54–48 | Rejected; Weakhold/Trauma6–0 offset by losses elsewhere |
| 13 keeper-search-prior | Existing keeper model inside parent movement search | 54–48 | Rejected; below03 |
| 14 queen-corridor-caution | Prefer visible turning room for short original queens | Smoke3–1 | Activated, same winners as12; full screen held |
| 15 pocket-without-reserve | Remove only08 global one-slot reserve | Probes8–0,6–2 | Pool recovery, queen deaths3/8; no promotion |
| 16 lossless-model-text | Base64 byte-plane source encoding of08 | Equivalent control | All node/probability parity and4 sandbox games pass |
| 17 stacked-direction-prior | A5-400 combined encoder/HB/HB-probability prior | 46–56 | Rejected; full102 replay fallback audit zero |
| 18 entropy-matched-prior | Renormalize17 prior with exponent1.61 | 49–53 | Rejected;102 replays read, zero fallback |
| 19 pocket-sprint | Local two-step length control, no global reserve | Probes8–0,6–2 | All Schooltime queen verdicts2–0;20 aims to retain length3 |
| 20 pocket-countdown | Prefer length3 unless observed food/spawn needs slack | Probe8–0 | All queens survive at2; end-length objective not met |
| 21 proven-reserve | Relay proof queen is outside any small sealed pocket | Probes8–0,6–2; full102 running | All8 School queens3, release markers only on UNSW |
| 22 keeper-split-prior | Existing keeper probabilities adjust ordinary queen split scores only | Prepared, held | Sanitizers pass;163-turn stream unchanged; no games |

Outputs: main build/kenma/kNN-v-carthage-s123/score.json for completed screens. Runtime manifests pin source, fixtures, engine and compiler. Never edit measured runtime snapshots.

## Active workers and next steps

Exactly **two game workers**, nice15:
1. Kenma03 versusAsahi05,102 games, under after-k18.py / parent9335 / session64496; log k03-v-asahi05-s123.progress.log. All retained replays read on completion. Chair explicitly requested this result and Bokuto04 cross-match to be posted. New crossmatch-after-asahi.py / session22429 waits exact9335 and clean102 +12 diagnostics, posts Asahi result to main BOARD, runs03 versusBokuto04 on102, reads12 retained replays and posts result. Opponent read-only root ../wt-bokuto/bots; fingerprintff68a7093aa3e5f6b2fee742c4b39f2e2cb7c59ae91ab8cb8c819dbe4e6bc74f pinned. panel.py --opp-root support passes source-isolation and retry tests. All builds/outputs remain Kenma. Asahi fp43bd2d4fc7a8baac6d8f14d22a6a0a8eb9c33cc2ca85ee12cce5b770a3eff1ad matches main.
2. Kenma21 full Carthage102 under after-k21-probes.py / parent34859 / session23148; log k21-v-carthage-s123.progress.log. Clean8+8 probes and every survival/release-marker check passed. Full run retains all102 replays, then audits/reconstructs all. Probes parent65354/session12546 is terminal. Broader21 zoo272/Kageyama102/03 head-to-head102 have dry-run previews only, not queued.

21 deployment waiter90662/session46396 was deliberately cancelled while idle to prioritize Chair cross-match (confirmed exit143, no children/game interrupted). Exact21 deployment now deferred. Kenma22 source prepared from08, only ordinary queen split propensity changed using existing04 model; native recorded-stream integration completed:163/163 actions identical08; held pending stronger mechanism evidence, no game worker/queue. No new best yet.

17/18 rejected46–56/49–53; all102 replays read in each, zero inference fallbacks.13 all12 replays read.19 probes8–0/6–2, all16 read.20 Schooltime8–0, all8 read, all queens alive but final length2;19/20 full screens held.21 probes8–0/6–2, all16 read, School queens3 and zero release markers; UNSW2362 total releases. First FenrirA divergence versus19 at round88 is a still-reserved split, demonstrating incomplete signal delivery.


Parent64 completed57–7, exactly supplied map totals;03 same fixtures49–15. Outputs parent-pool-diagnostic-s1/score.json and parent-pool-comparison.json. after-parent-diagnostic/session33367 completed14 smoke3–1; after-k14-smoke/session23315 completed16 deployment. Sessions15167(12),69469(parent64),33367(14 queue),23315(16 queue) are terminal. Kenma14 full screen is held; no strength claim.

16 runtime e4590915c3ef49df22635a8dde10e45adb711bea3bcabd39d360a3434b6608fa;17 runtime1f11fcbb25ebd6a0f75d9dd47804e033800826dd6a83939e94f60d7cadff6961. Best remains03. Any new best still requires full Kageyama/other posted free-lane/pool scorecards, deployment and independent reserved validation.

## Evidence and diagnostics

12 fixes two integration mistakes in frozen10/11. World.seen is round+1; World.bed is -1 for observed no-bed, 0 unknown, 1 bed. tools/kenma/test_orbit.cpp now feeds an actual protocol block through helper parsing and World::sense and requires activation before testing80 persistent synthetic turns and hazard guards. ASan/UBSan pass. Earlier mistaken fixtures retained as test_orbit_v10.cpp/test_orbit_v11.cpp. Real Weakhold/Australia smoke seed1 both seats3–1, zero errors; all four replays activated (168/140 Weakhold,144/239 Australia log entries) and were analyzed. Outputs k12-orbit-smoke/, k12-smoke-diagnostics.json.

The Weakhold B queen left its orbit, entered a food-filled corridor, split at the dead end and died at round162. Reconstructed protocol replay reproduces all163 queen actions exactly. An optimistic terrain lookahead cannot reject entry at157 because the endpoint is outside vision; it proves the trap at158, after commitment. **Not a demonstrated fix.** Probe tools/kenma/test_queen_corridor.cpp; input/output/finding main build/kenma/orbit-audit/. No new bot based on this probe yet.

13 copies08 and uses the already exported04 keeper model only as the original queen's first-step log prior, conditioned on its four movement classes, weight1.0. Parent search still evaluates room, threat, growth and sprints and chooses splits. No orbit or new training. Conditioning, all four facing rotations and zero-mass floor verified under sanitizers in test_keeper_prior.cpp. Prior hard-action variants' poor results motivate this separate integration experiment.

08 storage evidence: all824,580 nodes reconstruct exactly;21,024 native probability vectors bit-identical including1,024 NaN cases. Arrays6,596,640→3,300,848 bytes. Four sandbox outcomes, rounds, deaths and noncompute stats identical03; max10,968,532 points, firstturn10,850,012, zero errors; zip3,591,843. Evidence lossless-direction/ and deploy/kenma-08-lossless-direction/.

Queen model:26,820 oracle keeper rows;81.75% held-out action accuracy on17 development series; all19,627 move-row argmax export parity. Donor model:208,158 teacher306 rows; validation precision99.69%, recall73.87% at preselected0.9;20,000 native threshold decisions match. High-confidence donor predictions mostly describe terminal traps; full09 did not improve play. Offline accuracy is not strength evidence. Training outputs queen-action-v1/ and feeder-v1/.

## Limits and runner

At most4 heavy workers and6GiB aggregate RSS; intentionally use2 game workers with guard5GiB after earlier overlapping Ouroboros runs hit the guard. Fresh engine each game. Interrupted attempts were archived and retried, never counted as bot losses. Output about0.9GB, cap30GB; free disk253GiB, floor40GiB. All outputs main build/kenma/. Do not touch other lanes, HEAVY.lock or queue.

panel.py uses engine1.2.3, clang++-O2-std=c++20, current Python opponents via toolkit /usr/bin/python3 3.9.6. Map/roster hash39961c55d0e6 and parent runtime match supplied reference. Resume --retry-errors only after confirming old process terminal; retry regression passed. --logs enables activation logs and retains all selected replays with --keep-replays; ordinary runs retain Schooltime/Weakhold only. Read retained replays. deploy.py registers compiler/game helpers as killable process groups and propagates guard termination; verified with mocks and actual08 deployment.

2026-10-05 03:06 UTC: Previous turn made concrete progress (12 integration tests and real activation,09 result,13 prepared); current12, parent64 and waiting sequences revalidated through live session handles. Kenma14 prepared from12: short original queens prefer a legal route with visible turning room (branch, loop or portal traced through at most8 observed corridor cells) when available, retaining parent choices otherwise. This is a heuristic, not a proof about unseen endpoints. The initial immediate-degree test was insufficient because a safe narrow loop also has only one onward edge; corrected before measurement. Recorded-observation test now redirects round157 south and preserves fallback at158 under sanitizers. Log kenma_corridor_filter. Runtime c356ab501d912e7dd09fdc18a4c5e41951a4831e5726c1de2ec3de76d69083ed. Queued main build/kenma/after-parent-diagnostic.py (session33367) waits exact20374 and clean64 completion, then runs four Weakhold/Australia games (both seats,seed1,logs/replays). It stops for activation audit before any full14 screen. No extra concurrent game workers.

Pool mechanism evidence from completed same-host UNSW fixtures: parent wins four games lost by03 (Fenrir B,Yuna B,Chaewon B,Gavroche A). Death-event prefixes match until rounds68–77; sampled populations then diverge around the cap (parent64 versus03 at63). This supports investigating the global one-slot reserve as a cause, but full64 and a controlled reserve ablation are still required. No random APIs found in those four opponent source trees. A premature partial-log claim that Schooltime differed from the supplied reference was corrected: actual completed parent Schooltime14–2 matches reference;03 is15–1.

2026-10-05 03:08 UTC: Kenma15 prepared from08 with only the three reserve-limit lines removed from main.cpp; all other runtime files identical. Runtime5b7ecd83917e9178938d1a811f025b1b0916a0fa783f749505ac61578886b659. Dry-run previews: Schooltime seeds1/2/3/5 both seats8 games with replays, then UNSW seed1 both seats against Fenrir/Yuna/Chaewon/Gavroche8 games. Not launched or queued: both workers still occupied. The check must establish whether pocket survival remains reliable without a global slot and whether the pool regressions recover. Main build/kenma/parent-pool-partial-comparison.json records completed paired fixtures, explicitly incomplete. Avoid conclusions before full results.

2026-10-05 03:14 UTC: 12 final54–48/102, zero errors, rejected; full map table in README. All12 retained replays read and analyzed. 13 started automatically on exact clean12 completion. Complete native executable check on the recorded163-turn queen stream:13 changes87 actions;14 changes only round157 (to south), logging5 filter applications. Counterfactual replay choices do not predict game outcomes. Both exact native binaries cached under main build/kenma/bin/.

New packaging avenue: current08 hexadecimal model header compresses to3,539,354 bytes. Lossless byte-plane-separated base64 would compress node data to2,829,065 bytes (all824,580 original32-bit nodes), saving roughly0.7MB before framing. This may enable the stronger combined A5 prior that was previously too large. Copied only existing development fold0 from main build/hinata/r2/battery/A5-u/ (read-only); source SHA6695befe886641235869dfea42d51f42816dec17eb621b037963f230d23b899b, stored in main build/kenma/stacked-prior/. Explicitly truncated to400 rounds and exported: **4 classes**,1600 trees,200,000 nodes,100,800 leaves,1466 features,1,124,584-byte zipped header. Estimated combined package4,013,531 bytes vs4,194,304 cap. **No new bot yet:** actual text framing/archive, exact node and probability parity, feature binding (encoder+HB features+HB probabilities,4-class direction mapping), and sandbox first-turn cost must all be verified. Output model-text-storage/feasibility.json and stacked-prior/{source,export-feasibility}.json. Full800-round source was not accidentally adopted. Next investigate a standalone lossless storage control before the combined learned candidate. At03:14 UTC output1.0GB,free disk252GiB.

2026-10-05 03:26 UTC: This turn progressed via16 and17 source generation, verified native parity,16 successful sandbox and17 launch.16 all824,580 native nodes exact;21,024 bit-identical prediction vectors incl1,024 NaN cases; zip2,950,863, max12,958,553 points, firstturn12,238,377, zero errors in4 heavy-map games. Every gameplay statistic except compute matches08.17 actual archive4,083,138;2,759 turns/40 processes/4 replays give4,044,694 exact feature values,2,759 matching LightGBM argmax, max probability error2.609e-8. Model4 classes F/R/B/L,1600 trees; F/R/L normalized for search, weight1. Original HB probability inputs explicitly rounded to six decimal places to match training. All118 side-file hashes and1193 encoder names verified against source manifest. Tools pack_direction_text.py,verify_model_text.py,prepare_stacked.py,verify_stacked.py; outputs lossless-model-text/,stacked-prior/,deploy/.17 emits kenma_stacked_fallback if binding/inference fails; full run logs needed to audit. No new training or reserved-map exposure.

14 smoke activation audit: Weakhold filter5(A)/9(B) times; Australia0/0. Same3–1 winners as12. Weakhold B queen survives now, A dies at221; Australia queen histories unchanged. All four replays read. This mixed mechanism result and12's54–48 keep14 below priority for a full screen.15 controlled reserve probe remains next conditional use of13's worker.

2026-10-05 03:27 UTC:17 deployment complete and full102 native comparison started automatically after exact-source PASS and parity checks. Best remains03 pending full results. New reusable replay-log audit refuses incomplete full audits and reports any requested fallback markers; full17 audit still pending.

2026-10-05 03:43 UTC: Previous turn and current continuation made concrete progress; active17/18 runners revalidated, no blocker.13 finished54–48,15 Schooltime8–0 and UNSW6–2. Schooltime win totals hide3/8 queen deaths without reserve; local pocket sprint shedding is the next mechanism probe.18 changes only17 prior normalization:189,630 aligned out-of-fold rows show parent F/R/L entropy0.422933 versus A5 at0.562078; exponent1.610885 matches, rounded1.61. All normalization/facing/tiny-mass sanitizer tests pass.17 early26 replay audit found zero fallback markers; full audit still required.13 retained-replay diagnostic running. No reserved validation exposure.

New19 local-pocket mechanism: three15 queen deaths share length3→4 food growth then cap64 blocks splitting. Recorded prior turns allow safe two-step length3→2 sprint. New19 compares legal one/two-step paths at length2/3, prefers final length2 and never invents future food. Full parent simulation checks collision before sprint tax.80 synthetic intermittent-food transitions at cap64 and all3 actual failure streams passed sanitizers.15 UNSW all8 winner/reason/round/fault summaries exactly match parent;03 loses four of those parent wins. Evidence pocket-audit/, k15-unsw-parent-comparison.json. Output1.9GB, free251GiB before19 probes.

2026-10-05 04:04 UTC:19 probes complete8–0 Schooltime and6–2 UNSW, zero errors;16 replays being reconstructed.20 queued under after-k19-probes.py / session76001, waiting exact parent81055 and clean16 diagnostics incl allSchool queens alive, then Schooltime8 and all8 replay diagnostics. Actual protocol confirms countdown1 precedes allthree15 fatal meals;20 uses current World::spawn_at and fresh-view guards to retain queen3 between growth events, while19 ends at2.19 full102 held pending20 refinement. Both measured sources preserved.

Main BOARD reports Asahi05 as the newer incumbent; local/runtime source matches main fingerprint43bd2d4fc7a8baac6d8f14d22a6a0a8eb9c33cc2ca85ee12cce5b770a3eff1ad. A full03 versusAsahi05 comparison is dry-run-previewed and queued under after-k18.py after exact18 parent37871 clean102 completion plus full102 fallback/replay audits.17 all102 replays read, zero fallback, only8 originalqueens survive. No new best or reserved validation yet.

2026-10-05 04:12 UTC:21 replaces indiscriminate reserve with a permanent legal terrain proof: originalqueen has9 known open-connected cells or an incident portal, so cannot enter any closed<=8-cell portal-free pocket. Only queen/self or observed alliedoriginalqueen may seed it. Existing sonar type highbit carries it without extra rays; checksums recomputed and all44 payload bits restored before parent decode (density uses all44).7000 packet roundtrip/relay checks and terrain guards pass ASan/UBSan. HB features use message counts, not payloads, so envelope leaves features intact. Schooltime21 should retain03 behavior; UNSW tests whether proof propagates before population pressure. Runtime62671c2e5c55a03947b28f5aeb09b98453f47716a77845d1e370ec5bd1a368da. No map identity or hidden future state.

2026-10-05 04:17 UTC: Continuation made concrete progress:17/18 final46–56/49–53 and complete102-replay audits each;13 replay audit;15/19/20 mechanism results; new21 protocol proof implementation and sanitizer checks. Current two game workers verified, aggregate lane RSS2.517GiB, output2.5GB, free247GiB.21 first6 Schooltime games allqueen3–0 and first3 full-log audit has zero reserve-release markers; remaining probe and full incumbent comparison still in flight. Reserved seeds11–13/new maps untouched, no new best, no server access.

2026-10-05 04:34 UTC: Chair update incorporated. Bokuto04 is the other free-lane best (reported58–44); required cross-match queued with read-only sources and pinned fingerprint. Asahi05 is the current live reference. Posted one BOARD line at04:30UTC requesting a bounded60-ranked-game Kenma03 ladder screen, explicitly disclosing pool220–52 and matched four-map49–15 versus57–7. Live ops owns all server actions; no credentials/API/submission access by Kenma. maps/live_var/ is absent in both main and worktree at04:30UTC; check for the rebuilt five-map bed variants before the next validation batch. Reserved seeds11–13/new maps remain untouched.

2026-10-05 04:45 UTC: Requested Asahi05 cross-match complete57–45/102, zero errors, all12 retained replays read, posted BOARD04:39. Bokuto04 comparison launched automatically under crossmatch-after-asahi/session22429, one worker. WeakholdAsahi queen deaths are identical across seeds: walls at29(A)/44(B), length3. Kenma23 prepared to isolate14 corridor caution on08/03, excluding12 orbit confound; real recorded-turn sanitizer test passed. Actual Asahi queen-stream integration running before any game queue. New --map-root pins hashes and allows read-only shared variants;3 runner regression tests passed. maps/live_var still absent.
