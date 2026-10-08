# Akaashi 03 vs Heartbreaker: first iteration review

Measured 8 October 2026. Submission 20244 (v105); series 05360044-7f0a-42b1-b33e-66de0fdcfa18; 5 wins, 6 losses. One game per map, no strength confidence claim.

| Lost map | Total length A/B at r50; r100 | Queen death | Largest material death | Primary weakness to investigate |
|---|---|---|---|---|
| Around UNSW (1410660) | 123/56; 188/94 | r388, length 28, h2h | length 60, r492, h2h | Late material preservation: healthy early economy, then queen and long-body deaths; disconnected own-body simulation proven faulty. |
| Autarky (1410662) | 25/49; 2/69 | r86, length 3, h2h | length 3, r4, wall | Early corridor harvesting loses short parent pieces; food collection and population collapse before queen death. |
| Default (1410663) | 17/25; 13/37 | r146, length 2, h2h | length 3, r75, h2h | Early food/population deficit followed by head-on attrition; no large-dragon crash. |
| Prisoners Dilemma (1410667) | 7/19 | r34, length 3, h2h | length 3, r3, wall | Early splits leave length-two heads unable to turn after one dead-end pearl; queen dies early. |
| Slithery Fight (1410668) | 109/87; 145/113 | r242, length 2, h2h | length 30, r456, h2h | Midgame material attrition overturns an early lead; queen death and repeated late long-head losses. |
| Stripes (1410669) | 4/16; 4/36 | r69, length 2, h2h | length 3, r74, self | Near-zero pearl collection; single-pearl dead ends strand length-three heads, followed by queen/worker collisions. |

Primary weaknesses above are diagnosis/inference, not proof that a specific replacement wins.

First implemented candidate: Akaashi 04, visible own-body collision safety. Replay 1410660 dragon 711 has length 36 but a four-cell represented chain before moving NEE at r408 and self-colliding at length 37. Current visible disconnected own parts are absent from collision simulation. 04 includes every own part in the current observation and does not treat a partial chain as a vacating real tail. No map names, coordinate rules or terrain atlas are used.

Artifact curves (CSV and PNG) and full event-linked summaries: `build/finals/heartbreaker-iteration/akaashi03/review/`. Longest-length drops retain their split and death events separately; an ordinary production split is not counted as a death. The baseline has zero replay TLE/invalid-action faults (audit in summary).

Next: engine branch for the self-collision, synthetic full/partial-body legality tests, local/metered checks, then user-authorized upload and six-loss-map retest. Early corridor viability and material/queen avoidance remain outstanding targets for subsequent versions.

Further observed queen failure: Around UNSW r388 queen sees enemy 685 at
(26,59) and moves north from (28,58) to (28,57), which the enemy can reach
with a sprint. At length 27 she has several free sprint steps, but guard
dodge alternatives are single-step only. Investigate a bounded general
multi-step queen escape (endpoint danger plus continuation validation)
after the 04 retest. This is a proposed next mechanism, not measured fix.

### Akaashi 04 deployment and live retest

20265 (v106), `LV-akaashi-04-visible-body-safety-78d38fff-ai`, compiled and
was verified sole active. Archive 15 files / 3,941,039 bytes, ZIP integrity
and source-byte checks passed. Archive SHA256
`78d38fff65215b9d1897e533e4d268c6caf2567480cd0c42467becfba584afa9`;
server sourceHash `e0606fff4a87c81a1f4fa103db3515b38026952c42c49da60724cbe09f852f16`.
User-authorized unranked retest accepted **1412255–1412260**, one each on
Around UNSW, Autarky, Default, Prisoners Dilemma, Slithery Fight, Stripes.
Receipts: `build/finals/20261008-akaashi04-submit/`. Results pending.
Next continuation must refresh this series, analyze new losses, and make
a further general change from evidence. Goal remains active.

## Akaashi 04 retest — completed

Submission 20265 vs Heartbreaker: **1–5**, six games, one per map, fresh server seeds. Around UNSW is a win; five losses remain. This is not a matched causal estimate of the effect of 04. All six replays have zero TLE/invalid-action faults.

| Loss | Total A/B r50; r100; r200 | Queen death | Largest dragon death | Current primary weakness |
|---|---|---|---|---|
| Autarky (1412256) | r50 13/49 | r44, length 2 | r4, length 3, wall | Early corridor/food deficit; repeated length-three dead-end deaths before queen loss. |
| Default (1412257) | r50 21/19; r100 62/27; r200 79/37 | r166, length 2 | r367, length 9, h2h | Economy leads at r100/r200, then material/contact attrition reverses it; queen killed at r166. |
| Prisoners Dilemma (1412258) | r50 2/40 | r52, length 2 | r2, length 6, h2h | Opening population collapses: spawned heads collide and short chains strand before resource growth. |
| Slithery Fight (1412259) | r50 98/95; r100 141/113; r200 152/184 | r116, length 3 | r494, length 72, h2h | Midgame economy lead reverses; early queen loss plus decisive length-72 head-on at r494. |
| Stripes (1412260) | r50 2/24 | r38, length 3 | r38, length 3, h2h | Very weak food collection; queen collision at r38; partial-body fix cannot solve narrow-route starvation. |

Artifacts: `build/finals/heartbreaker-iteration/akaashi04-series/review/` (all curves, event-linked drops, summaries and plots).

Akaashi 05 adds general bounded sprint escape for queens: shortest-first legal prefixes of up to three steps, known visible terrain, exact body/pearl/paid-step simulation, lower endpoint risk, six continuation steps. Safe incumbent moves remain. It fixes a restricted single-step dodge search, without map identifiers or coordinate conditions.

Two measured counterfactuals: Around UNSW 1410660 oracle 36,347 turns/zero mismatches; original prefix through r387 then 05 only for queen 0. NN avoids r388 collision but queen dies at r397. Stripes 1412260 oracle 505 turns/zero mismatches; prefix through r36 then 05 only for queen 0. SE avoids original r38 collision, queen dies at r44; branch draws at r61 rather than original B win at r60. Other actors use recorded commands/sonar; exhausted lists use empty MOVE. These demonstrate avoidance of specific deaths, not wins against adaptive opponents.

05 synthetic endpoint escape test and all four earlier regression suites pass. Native Trophy/Autarky screen vs04, seed 81012, both seats: 2–2, zero faults. Metered Trophy same seed/both seats: 1–1, zero faults; candidate peak 8.8M points, p99 <=8.5M. Artifacts: `build/finals/20261008-akaashi05-screen/`, `...-runtime/`.

05 source fingerprint: `4a8d86ca8dc1cca4270d7623723bd42ddd28c8703204881df83aad7ecd19d7d0`.

Outstanding economy targets remain, especially opening corridor viability on Autarky/Prisoners Dilemma/Stripes. Next inspect 05 failures, and prioritize food/production changes or valuable late-dragon survival from the new evidence.

### Akaashi 05 deployment and five-map retest

20276 (v107), `LV-akaashi-05-sprint-queen-escape-55ad3fc2-ai`, compiled
and was verified sole active. Archive: 15 files, 3,941,224 bytes, ZIP integrity
and local-source byte checks passed. Archive SHA256
`55ad3fc299b062320aa2cc66fd5c77c860fb3175fbae6e157f4b3487b26976a0`;
server sourceHash `2ce46a1e8404ea60bb59150309cbd1167393f11a702a387b47d10d7feefd03d6`.
Accepted and verified five unranked Heartbreaker games **1413068–1413072**:
Autarky, Default, Prisoners Dilemma, Slithery Fight, Stripes; series
`66b05548-b3dd-4129-8db4-085a3c7fa0d1`. All pending at readback. Receipts:
`build/finals/20261008-akaashi05-submit/`. Goal remains active.

Next continuation: refresh 1413068, collect finished replays and generate
all loss curves. In addition to opening food/production viability, prioritize
Slithery Fight 1412259 dragon 1590's length-72 H2H at r494: authoritative
final standings show both queens dead and longest 12 vs55. This is a
plausibly outcome-changing late material loss; verify a legal escape from
its current observations before changing late long-dragon behavior.

## Akaashi 06 validation checkpoint

Latest user steering: finish current iteration and test. 05 live retest completed 0–5; all loss curves are in `build/finals/heartbreaker-iteration/akaashi05-series/review/`. 06 applies bounded dodge checks to late non-feeder heads of length >=12 before the partial-body shortcut. Partial known cells with >=6 unseen tail cells remain occupied for the six-step horizon. Reconstructed 1412259 dragon 1590 changes W to S at r494. Full oracle failed (39,133 mismatches / 39,147 turns); attempted branch rejected. No counterfactual win/survival claim. Synthetic asset/exclusion tests and prior safety cases compiled against06 pass. Native Slithery/Dilemma seed81013 both seats: 2–2, zero replay faults. Initial metered run was interrupted with truncated artifacts; recovery run is `build/finals/20261008-akaashi06-runtime-recovery/`.

06 focused runtime recovery completed: 0–2 vs05 on Slithery Fight, zero runner/replay faults, candidate peak13.6M points, p99<=8.6M. Uploaded 20296 (v108), LV-akaashi-06-late-material-safety-406f4835-ai; server sourceHash 4d5d6364ca83997284e2779cd8ba9b510c9116383a025bca236219e2ff01b98b; archive SHA256 406f4835b0edbf17f4f7201197fa48ce5063baf5a5b6c5eafe47bc1e438a1ea8. Compilation/readback and five-map live test pending. No general improvement claim.

06 compilation/readback succeeded: 20296 sole active. Accepted and API-verified five-map Heartbreaker test1415322–1415326, seriesc7153758-39cf-42e0-bf8e-201ad801e97a. User steering: finish current iteration and test; no new version started. Receipts build/finals/20261008-akaashi06-submit/; monitor/collection build/finals/heartbreaker-iteration/akaashi06-series/.

## Akaashi 06 current iteration — finished

Heartbreaker test1415322–1415326 completed **1–4**: Default won; Autarky, Prisoners Dilemma, Slithery Fight and Stripes lost. All five replays collected; total/queen/longest curves and linked death/split diagnostics are under `build/finals/heartbreaker-iteration/akaashi06-series/review/`. Own bot TLE/invalid-action faults: 0. Authenticated post-test read verifies20296 (v108) sole active. No next version started.

Autarky/Prisoners Dilemma/Stripes retain early food/population deficits (r50 total A/B25/50,3/38,2/18 respectively). Slithery Fight leads at r100143/114 and r300160/130 but loses its queen at r198 and substantial late heads (largest25 at r459); late material/queen safety remains incomplete. Default won despite queen death at r66, with strong early economy (r10056/19). Results use fresh server seeds, so no causal strength improvement is established by the single win.
