# Kenma21 — release only a proven unnecessary reserve

Parent:08 (strategy equivalent to03). Preserve the original queen keeper and donor behavior. A process releases its one-slot population reserve only after proving that its original queen belongs to an open-connected component of at least9 cells, or one containing a portal. Static terrain means such a queen can never enter a distinct closed <=8-cell, portal-free component where this keeper requires a reserve. Unknown edges are ignored, not treated as open. A nonqueen can seed the proof only from an observed allied original queen, never from its own large component.

Share the permanent fact using the unused high type bit of existing policy sonar packets. Recompute the checksum; receivers remove the envelope flag before parent decoding. All44 payload bits (including the high density id bit), packet order, ray count, split handoff and HB message-count features are preserved. No new rays, map identity or full-map inference. As with parent radio, team tag/checksum is not cryptographic authentication.

Motivation:15 removed four UNSW pool losses caused by the global reserve, but killed3/8 Schooltime queens;19/20 survived all8 but ended at length2.21 keeps03's length3 pocket keeper while removing reserve cost only where the terrain proof makes that reserve unnecessary.

Status: ASan/UBSan passes closed/unknown/portal/open terrain, queen-only proof seeding,7000 complete44-bit payload roundtrips, relay and corrupted/opposing-tag guards. Eight Schooltime and eight UNSW games are running; retain and read all16 replays and audit release markers. Runtime62671c2e5c55a03947b28f5aeb09b98453f47716a77845d1e370ec5bd1a368da. No reserved seeds11–13/new maps used. Source and results remain in the Kenma lane.

Validation command: compile tools/kenma/test_conditional_reserve.cpp with clang++ -O1 -g -std=c++20 -fsanitize=address,undefined and this bot as include directory, then execute the resulting binary. Probe runner tools/kenma/panel.py uses Schooltime seeds1/2/3/5 both seats againstCarthage, and UNSW seed1 both seats againstFenrir/Yuna/Chaewon/Gavroche. All fixture/source manifests and outputs are main build/kenma/k21-schooltime-s1235/ and k21-unsw-pool-s1/. Full102 k21-v-carthage-s123 is queued only after the survival and release-marker checks pass. Exact-source sandbox deployment remains outstanding.

Completed probes: Schooltime **8–0**, all8 original queens survive at length3 and zero release markers; UNSW **6–2**, release markers in every replay (2362 total), zero faults. All16 replays read. UNSW wins differ from the reserve-free control: loses FenrirA/GavrocheA, gains YunaA/ChaewonA. Trace against19 shows first action divergence in FenrirA at index5463/round88: uncertified dragon66 holds its reserve and declines a split at population63. There are571 high-population turns with no outgoing proof flag in that replay; propagation is incomplete, not immediate global consensus. Full102 native Carthage screen now running. Evidence reserve-first-audit.json, k21-probe-diagnostics.json and per-run replay-log-audit.json.

## Full Carthage comparison

60–42/102, zero draws/errors; all17 ranked maps,both seats,seeds1–3. Two additional wins versus03, on Australia andIslands; every other map total unchanged. All102 replays read;17,598 reserve-release markers audited. All6 Schooltime queens survive at length3. No best/promotion claim: matched four-map64 zoo diagnostic running, exact deployment queued after it, broader scorecard outstanding.

| Map | W | L |
|---|---:|---:|
| schooltime | 6 | 0 |
| portals | 3 | 3 |
| slithery_fight | 4 | 2 |
| queen_of_spades | 3 | 3 |
| default | 3 | 3 |
| trophy | 3 | 3 |
| dilemma | 3 | 3 |
| autarky | 3 | 3 |
| devil | 3 | 3 |
| trauma | 3 | 3 |
| australia | 5 | 1 |
| islands | 3 | 3 |
| unsw | 5 | 1 |
| maze | 4 | 2 |
| weakhold | 3 | 3 |
| stripes | 3 | 3 |
| tower_defense | 3 | 3 |

Output main build/kenma/k21-v-carthage-s123/{score,manifest,replay-log-audit}.json and k21-final-diagnostics.json.

Matched four-map pool64 complete57–7, zero errors (Schooltime15–1,UNSW13–3,Australia14–2,Maze15–1), versus03 at49–15 and parent57–7 on identical fixtures. Gains over03: UNSW+4,Australia+3,Maze+1; Schooltime unchanged. Full replay review is still running. Exact deployment is queued after review and safe worker capacity; full272 pool (reuse64 successful fixtures) and Kageyama102 are queued only after deploymentPASS. No full-pool or promotion claim.
