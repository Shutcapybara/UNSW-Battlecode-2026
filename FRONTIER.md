# Current bot frontier

## Kuroo soft reserve — 8 October 2026

New family `kuroo-01-soft-reserve` (Akaashi02) and
`kuroo-02-escort-soft-reserve` (Akaashi12) gradually discourage routine
splitting near capacity and penalize loss of free sprint steps. Terminal
escapes may use the last reserved slot. Exact replay diagnosis and focused
regressions pass; native two-map screen4–4 (3–1 vs02,1–3 vs12), zero runner
errors. Expanded128-game parent panel:32–32 vs02 and34–30 vs12, with no decisive strength gain. Replay/F1 audits pass; death rates are higher against both parents. Kuroo02 was user-requested and submitted as **20472 (v111)**;
server compilation succeeded. After an initial restoration of 20432, the user
requested Kuroo02 remain active for live retesting. It is now verified sole
active; the14-game retest against team193 finished2–12 (Australia/Maze wins),
zero own replay runtime faults. Local `kuroo-03-queen-retention` addresses
1431111 queen obstruction through late crown feeding, fresh body-adjacency
sacrifice and bounded sprint escape checks. Final native screen2–2 vs02;
regressions pass. Expanded22-map/88-game screen finished31–57 vs02, zero
replay faults; queen end-game survival15/88 vs24/88.03 is rejected for
strength; no upload/promotion.02 remains active. See
[Kuroo notes](docs/kuroo-family.md).

## Isolated Kuroo04/05 — 8 October

Both fork02.04 adds visible local obstruction feeding;05 adds late bounded
free queen escape search without paid sprints.22-map development panels,
seed81034/both seats:04 **22–22**, no observable gameplay difference;05
**21–23**, two free escape overrides, stronger queen length on Stronghold
but an extra Islands loss.88 replay audits zero faults.05 Slithery sandbox
pair1–1, zero faults, candidate peak11.1M points. No strength gain, upload,
combination or promotion. Targeted queen distress radio remains proposed for
1431111's out-of-view donor. [Kuroo notes](docs/kuroo-family.md).

## Active Kuroo07 targeted distress — 8 October

Fresh06 adds queen-selected, expiring donor requests;07 fixes diagonal
visible-queen rejection.07 final development panel22–22 vs02 on22 maps,
seed81036/both seats, zero replay faults. One same-round Stronghold feed:
donor5 length49, queen eats16 donated pearls and finishes87 vs mirrored02
queen6; gameplay first diverges at423 after r422 request. Winner unchanged.
07 Stronghold sandbox pair1–1, zero candidate faults, peak10.34M points.
06 raw23–21 includes three pre400 invalid deaths and is not clean strength
evidence. 06 remains local. At explicit user request07 was submitted as**20627/v112**,
compiled and API-verified sole active; previous20472/02 is inactive. This is
requested deployment, not strength promotion. [Kuroo notes](docs/kuroo-family.md).

## Local composite Akaashi 12 — 8 October 2026

`akaashi-12-queen-strike-escort` forks the strongest measured 01–06 baseline,
`akaashi-02-queen-strike`, and ports Akaashi08's nearest-ally queen escort.
Focused six-map screen vs01–11: **71–61**, zero runner errors; 51–45 against
01–08. It loses to01,04,05,11 and ties03. A separate 40-game weak-map
follow-up went **16–24**, so it is not a confirmed family-wide winner.
Local/experimental; no upload or active-bot change. Full matchup and map
tables: [Akaashi notes](docs/akaashi-family.md#akaashi-0912-composite-candidates--8-october-2026).

## Local Akaashi 08 escort counterfactual — 8 October 2026

For Australia1418905, `akaashi-08-queen-intercept` adds a nearest ally escort potential when an equal-or-stronger visible pursuer nears the queen. Original replay oracle reproduces with zero mismatches; scripted branch has A21 set up north at protocol r47 and mutually trade with B10 at r48. Queen survives, branch ends A win at r181. Recorded opponents do not adapt and produce invalid commands after board changes; terminal outcome is not strength evidence. Allocation and six safety regressions pass. Local only; 20333 remains active; no upload requested. See [Akaashi notes](docs/akaashi-family.md).

## Akaashi 07 local validation — 8 October 2026

`akaashi-07-hotspot-capacity` forks06 for the latest Team A congestion request. Reserves nearest collectors/defenders around visible resource targets and suppresses surplus routine production. Synthetic allocation plus six inherited safety regressions pass. Native Trophy/Default, seed81014, both seats vs06: **2–2**, zero replay faults. Uploaded as 20333 for the user-requested Heartbreaker retest; experimental, with no strength promotion. Metered Trophy1–1, zero faults, peak9.9M / p99<=8.0M. See [Akaashi notes](docs/akaashi-family.md).

## Current Akaashi 07 test — 8 October 2026

20333 (v109), `akaashi-07-hotspot-capacity`, compiled and verified sole active after user requested seven-map Heartbreaker retest. Seven-map test1418905–1418911 completed **2–5**: won Devil/Trophy; lost Australia, Autarky, Maze, Prisoners Dilemma and Stripes. Zero TLE/invalid faults; loss curves and death/split diagnostics collected under `build/finals/heartbreaker-iteration/akaashi07-series/review/`. Experimental; local comparison was2–2 and server retest does not support promotion. No next iteration until requested.

## Previous Akaashi 06 test — 8 October 2026

20296 (v108), `akaashi-06-late-material-safety`, compiled and was verified sole active. Native screen2–2 vs05; metered Slithery0–2, zero faults, peak13.6M points. Live Heartbreaker test1415322–1415326 completed **1–4** (Default won), zero own runtime faults. Remaining losses: Autarky, Prisoners Dilemma, Slithery Fight, Stripes. Whole-game Slithery oracle did not reproduce, so no counterfactual strength claim. User asks to finish this iteration/test before any further version.

## Latest iteration checkpoint — 8 October 2026

Akaashi 04's six-map Heartbreaker retest completed **1–5**, zero replay
faults. Around UNSW won; five maps remain. `akaashi-05-sprint-queen-escape`
adds bounded, legal multi-step queen dodges with endpoint risk and six-step
continuation checks. Engine branches avoid the observed Around UNSW r388
and Stripes r38 deaths but queens die later; no general strength claim.
Synthetic/prior regressions pass; two-map native screen vs04 is 2–2, focused
metered screen 1–1 with zero faults. Uploaded as **20276 (v107)**, compiled and verified sole active. Queued
**1413068–1413072** on five remaining losses; that test is superseded by the latest seven-map run. See [campaign review](docs/finals-campaign/HEARTBREAKER_ITERATION.md).

## Heartbreaker iteration evidence — 8 October 2026

Akaashi 03's 11-map Heartbreaker retest completed **5–6**, with zero replay
faults. Remaining losses: Around UNSW, Autarky, Default, Prisoners Dilemma,
Slithery Fight and Stripes. All have total/queen/longest length curves and
linked death/split diagnostics in the [iteration review](docs/finals-campaign/HEARTBREAKER_ITERATION.md).

`akaashi-04-visible-body-safety` fixes ignored visible disconnected own-body
segments and false partial-tail vacancy. It avoids the observed Around UNSW
r408 length-37 self-collision; the scripted dragon later dies against a wall
at r411. Synthetic and prior regressions pass; two-map native screen vs03
is 2–2, focused metered checks have zero faults. Upload **20265 (v106)** compiled and is verified sole active. Queued
1412255–1412260 against Heartbreaker on the six losses; outcomes pending.
This is user-authorized iteration, not confirmed statistical promotion.

## Earlier deployment and validation — 8 October 2026

At the user's explicit request, **Akaashi 03, 20244 (v105)**,
`LV-akaashi-03-threatened-queen-split-4f229cf2-ai`, compiled successfully and
was verified sole active. Server sourceHash:
`23e621f6c2f14deb4f4f3fdc5113751c41e351ccb6b5ef62d7cc18045ca6c92c`.
Queued and API-verified 11 unranked games against Heartbreaker (team 62),
one on every map lost in the series containing 1407768: games 1410660–1410670,
series `05360044-7f0a-42b1-b33e-66de0fdcfa18`. Results pending at readback.
Deployment is user-selected, not statistical promotion; Bokuto 18 remains
the supported fallback. See [family notes](docs/akaashi-family.md).

## Earlier deployment — 8 October 2026

At the user's explicit request, Akaashi 01 was uploaded as **20222 (v104)**,
`LV-akaashi-01-queen-escape-4cf62807-ai`, and verified sole active after server
compilation. Server sourceHash:
`188b90bbba4dcc0cd28d69dce51e9e1e4d60415d66a398039c1da1ed18ef0f8f`.
This deployment does not establish statistical promotion; Bokuto 18 (17791)
remains the best-supported fallback. See [the family notes](docs/akaashi-family.md).

## Historical finals checkpoint — 6 October 2026

Retained atlas-free qualifier fallback: **`bokuto-18-queenfeed`, submission 17791**.
After the independent confirmation gate failed for candidate 63, fallback **17791** was activated
on 6 October at 21:22 Adelaide and immediately verified as the sole active submission. No candidate
is promoted by this decision.
The initial four-fresh-map development baseline for 18 against Kenma 03 scored
5W–3L, both seats, seed 61006, with zero runner errors. This small screen does
not establish improvement over the fallback. Provenance and next tasks are in
[the finals working memory](FINALS_WORKING_MEMORY.md); artifacts are under
`build/finals/20261006-baseline/`.

Current finals experiments (all atlas-disabled, no promotion): `bokuto-62-escape-priority`
screened 4–4 versus 18 and 4–4 versus Kenma. `bokuto-63-resource-crowding` had an initial
four-map 5–3 screen, then scored 86–88 in its independent 174-game confirmation against 18;
the direct advantage was +0.0057 with a 90% map-cluster interval [−0.0517, +0.0632], so it
failed the frozen promotion gate despite zero replay faults. Keep 18 as the supported fallback.
`bokuto-64-option-chassis`
passed 26,159 complete baseline-reply parity checks; `bokuto-65-policy-collector`
collects lawful action/sonar candidate data. These are integration artifacts, not
new strength rankings or active submissions.

The common-seed four-arm development screen tied action-only, sonar-only, and combined
u10 policies with 18 at 4–4 and with Kenma at 4–4; matched keeper deltas were zero.
Optional-packet suppression led that four-map screen but lost 83–91 to 18 on a separate
29-map, 174-game confirmation (direct advantage −0.023; 90% map-cluster interval
[−0.086, +0.040]; zero faults). No learned or suppression artifact is supported for
promotion. A fresh server check before fallback activation showed 18078 active and 17791 idle;
the subsequent guarded activation and readback confirmed 17791 as sole active. See the
[working memory](FINALS_WORKING_MEMORY.md) for hashes, replay diagnostics, and the sonar resource check.

## Akaashi safety family — 8 October 2026

`akaashi-01-queen-escape` forks atlas-disabled Bokuto 18. It strengthens
queen continuation/head clearance from round zero, validates dodge overrides
against the full horizon, and enables early teammate yielding. It fixes the
Trophy 1404793 team-B round-66 alcove trap in an oracle-verified scripted
branch (queen survives; B wins). A serial three-map, both-seat development
screen against 18 scored 4–2 with zero runner errors; this is not promotion
evidence. See [the Akaashi family notes](docs/akaashi-family.md).
Bokuto 18 remains the supported qualifier fallback.

`akaashi-02-queen-strike` extends 01 with visible, affordable one-to-three-step
non-queen attacks on enemy queens, including pearl-funded paid steps. An
oracle-verified branch of Trophy 1407768 confirms dragon 4 kills enemy queen
at protocol r46 (visualiser r47). One-map development screen: 1–1 vs 01 and
1–1 vs Bokuto 18, zero replay faults. Experimental local candidate; deployed
submission 20222 remains Akaashi 01. See [family notes](docs/akaashi-family.md).

`akaashi-03-threatened-queen-split` extends 02: queen splits on enemy-reachable
cells evaluate a surviving dodge at every round, with conservative incomplete
body reach and separate per-enemy BFS visitation. In Trophy 1407768, it turns
north at r109, avoids the recorded queen-killing sprint and wins the scripted
branch with the queen alive. Trophy/Schooltime screen 2–2 vs 02; focused
metered/replay audits have zero faults. Local experimental candidate; 20222 stays
deployed 01. See [family notes](docs/akaashi-family.md).

## Historical panel — 2 October 2026

The rankings and upload discussion below are historical evidence; they do not
describe current Queen-rule standings or the current active server submission.

**Updated 2026-10-02.** Rows are ordered by displayed ELO. Numbers in the first
column are 35-map panel ranks; `Screen` entries have provisional 10-map ratings.

| Rank / status | Bot snapshot | ELO (evidence) | Source fingerprint |
|---:|---|---:|---|
| Screen | `tyr-v12-devil-scout-tiebreak` | 1,786 (10-map) | `d2f691c4fc0c` |
| 1 | `fenrir-v20-crowded-resource-revalue` | 1,654.3 (35-map) | `dc7717689882` |
| 2 | `bifrost-v01-portal-memory` | 1,620.9 (35-map) | `037872088e6f` |
| 3 | `gavroche-v33-half-support` | 1,618.0 (35-map) | `57d123043c7f` |
| 4 | `gavroche-v66-supported-safe` | 1,617.2 (35-map) | `a5c8dc0f8db5` |
| 5 | `von_neumann-x04-support` | 1,586.8 (35-map) | `3772d5a35503` |
| 6 | `skadi-v13-clear-exit-only` | 1,586.1 (35-map) | `34d716a3492d` |
| Screen | `eunchae-s02-pearl-band` | 1,576 (10-map) | `46ffdb69ce64` |
| 7 | `sinbad-v07-divecap` | 1,572.6 (35-map) | `c759a5c8a8ba` |
| 8 | `serre-v01-foundation` | 1,566.2 (35-map) | `ae4bcc23254c` |
| 9 | `monte_christo-x12-remote-density` | 1,534.8 (35-map) | `5589c30d0525` |
| 10 | `tew-v12-mid-support` | 1,485.1 (35-map) | `8bff0f54828f` |
| 11 | `hunter-v20-portal-scouts` | 1,438.6 (35-map) | `f844fa3ae595` |
| 12 | `hunter-v23-supported-arrival-feed` | 1,416.7 (35-map) | `b10300e824d4` |
| 13 | `ouroboros-v10-beacon` | 1,407.8 (35-map) | `a9eafbaffc51` |
| 14 | `hunter-v14-cpp-hybrid-route-spacing` | 1,405.5 (35-map) | `6ba4e603ad19` |
| 15 | `fry-v14-stateful-size-aware-3` | 1,356.8 (35-map) | `962541eb674d` |
| 16 | `kraken-v04-eval` | 1,132.6 (35-map) | `7d23d380f291` |

These provisional screen ELOs are anchored to the 16-bot panel. Map-bootstrap
95% intervals from 2,000 resamples (seed 20260929): Tyr 1,682–1,924; Eunchae
1,436–1,716. The fit uses 160 recent screen games across five screen bots,
holding panel ratings and the +19.1 ELO A-seat term fixed. Intervals do not
capture all run-to-run behavior randomness.

## Panel and admission

The official ratings cover 35 maps (15 established, 20 custom), both starting
sides, and 15 opponents per bot: 8,400 unique games total. Preliminary
Bradley–Terry ELOs are centered at 1,500 across these source fingerprints;
they are not contest ratings. A paired lineage bootstrap found no supported
map-wise dominator, so all 16 remain on the statistical frontier.

A map qualifies for dominance analysis when both bots have both sides against
at least three opponents there. A bot dominates another only when the paired
95% interval is nonnegative on every qualified map and positive on at least
one. New candidates need 200 distinct directional fixtures, 15 exact-source
opponents, 6 lineages, 10 maps, and at least 3 paired opponents on 10 maps
before admission. Screen rows above do not meet that threshold.

Full ratings and intervals are in the [35-map panel report](docs/frontier-panel-20260929.md).
The 7,616-game campaign contribution is
[`game_stats/runs/187e0e722be944ec90f626a129b4b544.parquet`](game_stats/runs/187e0e722be944ec90f626a129b4b544.parquet).
Recreate the analysis with
`.venv/bin/python tools/frontier_panel.py experiment_data/benchmark_20260928083347416650`.

## Gaia experimental lineage

`gaia-v47-medium-map-threat-pearl` is the current retained Gaia snapshot,
forked from Fenrir V20 through the V08 parent-aware line and V44's compact-map
dispersion policy. It adds a bounded enemy-threat pearl-exit check on ordinary
compact maps while retaining V44's tiny-arena and Big Empty behavior. The
repeated four-map 48-game panel scored 13W-11L for V47 versus 12W-12L for V44
and 8W-16L for V08, with zero runner errors or TLEs. Against Fenrir, V47
matched V44 at 3W-5L and won the direct V47-vs-V44 comparison 5W-3L. These are
family-development results, not frontier-qualified evidence. V09–V63 remain
immutable lane, pearl, breeding, pathfinding, split, portal, and density
controls; V51–V63 did not produce a significant repeatable gain. V56 improved
portal traversal on the portal-heavy screen but lost to Fenrir, while V57/V58
traded early population for lower newborn risk. Post-V63 Arena diagnostics
tested immediate-threat veto, Arena child siting, and stronger opposing lanes;
each lost both Fenrir orientations and was rejected. No Gaia version has
triggered the C++ fallback threshold: all tested panels completed with zero
runner errors and zero TLEs. Additional contact-penalty relaxations also
scored 0-8 on the four-map screen, so V47 remains the retained Gaia
candidate.

The serial harness is now the promotion gate (`--jobs 1`): concurrent
low-level runs were not reproducible and an apparent pearl-value 8-0 was
reversed by replay-producing and serial runs at 0-8. Serial V54 four-way
lanes and the subsequent contact/pearl controls also failed their focused
screens, so no Gaia V64 has been promoted.

## Recent screens

- **Tyr V12:** 14–6 against Fenrir on 10 maps; it won at least one game on
  nine maps and swept both seats on five. The other candidates in that screen
  were Chaewon Y04 (10–10), Heimdall V10 (8–12), and Tyr V01 (8–12). Outcomes:
  [`db75c3f2.parquet`](game_stats/runs/db75c3f2093b4e71b67afebb3e91736c.parquet),
  [`27f41a20.parquet`](game_stats/runs/27f41a20010e40019846871a99347b23.parquet).
- **Eunchae S02:** 10–10 against parent Chaewon Y04, 9–11 against Fenrir,
  6–14 against Bifröst, and 5–15 against Tyr V12. It went 7–1 on Crossroads
  and 6–2 on Scattered Fleets, but 1–7 each on Portal Quartet, Queen of Spades,
  and Stronghold. No draws or runner errors. Results:
  [`ed4cbcaa.parquet`](game_stats/runs/ed4cbcaa5ccc48de92f1dd1c9a2cb3bc.parquet);
  logs: `build/frontier-eunchae-s02-screen-20260929/`.
- **Fenrir V20 vs Hunter V20:** 50–20 over 70 games on all 35 maps, with no
  draws or runner errors. Results:
  [`549ce497.parquet`](game_stats/runs/549ce497d5e14041bf5321a96787d7a0.parquet).
- **Tyr V16:** `tyr-v16-live-loss-response` scored 7–11 against Tyr V12 in an
  18-game screen on the nine review maps, both sides, zero runner errors. V16
  split 1–1 on seven maps and lost both Devil and Trauma games. This unseeded
  focused screen gives V16 no all-map ELO; keep V01 as the baseline and V12 as
  the Devil specialist. See the [Tyr family notes](docs/tyr-family.md); results
  are in `build/tyr-v16-vs-v12-loss-review-20260929/`.
- **Tyr V33:** `tyr-v33-targeted-resource-defense` scored 55–53 against V12
  over six fixed seeds, both sides on the same nine maps (108 games, no draws
  or errors). Fresh seeds 7–18 reversed that edge: 91–125 over 216 games.
  Across seeds 1–18, V33 scored 146–178; it went 32–4 on Trauma, 2–34 on
  Autarky, and 6–30 on Dilemma. Keep it experimental, not a general V12
  improvement; see the [Tyr family notes](docs/tyr-family.md), the
  [V33 result](bots/tyr-v33-targeted-resource-defense/README.md), and
  `build/tyr-v33-fresh-v12-seeds7-18-absolute-20260929/`.
- **Tyr V34:** lowering V25's pearl-funded sprint threat floor to 0.2 scored
  37–71 against V12 on fresh seeds 19–24 (108 games, zero errors); V12 swept
  26 paired map/seed sets to V34's 9, with 19 split. Rejected. V01 remains the
  all-map baseline and V12 the Devil-specialist reference; see the [Tyr family
  notes](docs/tyr-family.md) and [V34 result](bots/tyr-v34-calibrated-pearl-sprint/README.md).

The V12, Eunchae, and Fenrir screens above used native `unswbc 1.2.1` with both
starting sides. Tyr V16 used native `unswbc 1.2.2` on its focused nine-map
screen. The [Tyr family notes](docs/tyr-family.md) contain its earlier Devil
and Yuna experiments. The earlier three-map pilot is preserved in
[`bc86c2ad.parquet`](game_stats/runs/bc86c2adc518428f8d77039e11111a97.parquet);
its dominance findings are limited to those three maps.

## Experimental C++ family: Ares

Ares V01 copies Anna A02's C++ scaffold and adds safe split launches, escape-sized
emergency splits, weak opening tie-breaks, and a soft recent-portal-return cost.
On the seed-1 BENCHMARKS.md panel it scored **21 wins, 1 draw, 138 losses** in
160 games, matching Anna A02 on the same fixtures. Its mean map-normalised
pearl curve improved by 0.030 field medians, short of the +0.05 gate, while
ally-body deaths rose 44.3%, over the 10% hygiene guardrail. Keep V01
experimental and outside the all-map ratings. In a separate native seed-1
screen, Tyr V12 swept Ares **20–0** across the same ten live maps, winning both
seats on every map (unswbc 1.2.2). The source fingerprint, full scorecard, and
matchup details are in [the Ares family notes](docs/ares-family.md) and
[the V01 finding](docs/findings/2026-09-29-ares-v01-safe-launch-routing.md).

Ares V02 is a separate experimental C++ translation of Tyr V12's policy on
the Anna A02 scaffold, including sonar reports and newborn separation. Anna's
hard safety tiers and room-valid split checks adapt Tyr's action ordering. It
passes a C++20 executable compile-check. In a separate native seed-1 direct
screen, Tyr V12 won Ares **20–0** across ten live maps and both seats (unswbc
1.2.2); this one-opponent screen does not meet the fixed-panel acceptance
benchmark. V02 is not ranked or admitted to the frontier. See the
[V02 port notes](docs/ares-family.md#v02--tyr-v12-c-policy-port),
[source snapshot](bots/ares-v02-tyr12-cpp-port/), and
[matchup report](docs/findings/2026-09-29-ares-v02-vs-tyr-v12.md).

Ares V03 is a separate pure C++ port of Tyr V12's strategy on the Anna runtime
scaffold. Anna's action tiers, nearby-enemy split veto, hard parent-room split
gate, and atlas lookup are removed from the active policy. Tyr beat V03 **12–8**
on the same ten live maps and both seats; the extractor processed all 20
replays. This is still a one-seed direct screen, not the fixed-panel gate. V03
remains experimental and is not admitted to the frontier. See the
[V03 port notes](docs/ares-family.md#v03--pure-tyr-v12-c-policy-port),
[source snapshot](bots/ares-v03-tyr12-pure-cpp-port/), and
[matchup report](docs/findings/2026-09-29-ares-v03-vs-tyr-v12.md).

Ares V04 is the behavioral-parity C++ port of Tyr V12 on the Anna runtime
scaffold. On identical ordered inputs from ten live maps and both seats, it
matched all move, split, and sonar outputs across 168,123 turns from 5,089
dragons, with zero divergences. Its seed-1 panel against the current eight-bot
roster scored **117–43 with no draws** over 160 games. The absolute economy and
hygiene scorecard does not establish the BENCHMARKS.md parent-relative gate;
V04 remains experimental and is not admitted to the all-map frontier. See the
[V04 notes](docs/ares-family.md#v04--tyr-v12-behavioral-parity-port),
[source snapshot](bots/ares-v04-tyr12-behavior-parity/), and
[parity and benchmark finding](docs/findings/2026-09-29-ares-v04-behavior-parity.md).

Ares V05 fixes the inherited Tyr V12 zero-bed-wait division and newborn pearl-pause
counter exceptions. Its seed-1 panel improved expected score slightly, but the
normalized economy gain was +0.007 (below +0.05) and normalized r100 dragons
fell. It remains experimental and is not submitted. See the [V05 notes](docs/ares-family.md#v05--separation-exception-fixes),
[source snapshot](bots/ares-v05-tyr12-separation-bugfix/), and
[bugfix finding](docs/findings/2026-09-29-ares-v05-separation-bugfix.md).

Ares V06 restores larger bounded target/room/triple search and adds visible,
size-matched allied support to threat scoring, drawing on Tyr, Bifröst, Skadi,
and Fafnir experiments. Its seed-1 panel scored **122–38–0**, improving the
V05 parent by 3.5 expected-score points. The normalized pearl mean rose only
+0.0133, below the +0.05 gate, while r100 dragons and length improved; all
Tier-2 rates stayed within the 10% guardrail. Four sandbox Schooltime/Portals
games had zero runner errors (p99 max-of-games 7.4M points, maximum 8.6M).
V06 remains experimental and is not submitted or admitted to the frontier. See
the [Ares V06 notes](docs/ares-family.md#v06--expanded-search-and-supported-threat-evaluation),
[source snapshot](bots/ares-v06-expanded-search-support/), and
[benchmark finding](docs/findings/2026-09-29-ares-v06-expanded-search-support.md).

The later Ares line includes experimental V41 portal-bed dispersion and V42's
memory-aware exploration and teammate approach penalties. V42 scored 8–12
against V41 on one ten-map, both-seat screen. V43 scopes the teammate approach
cost to exploration and scored 12–8 against V41 on a separate screen with
different generated seeds. Both remain experimental and outside the all-map
frontier. See the [Ares family notes](docs/ares-family.md), [V42 finding](docs/findings/2026-09-30-ares-v42-memory-team-dispersion.md),
and [V43 finding](docs/findings/2026-09-30-ares-v43-exploration-only-dispersion.md).
The server accepted V43 as submission v95 and reported it as processing.

V44 adds confidence-weighted sonar reports of explored sectors and short-lived
claims on exploration targets after Ares V43 replay 710870 showed repeated
low-value scouting. Its three-seed, ten-map, both-side screen against V43
scored 32–28 over 60 games, with no runner errors; this small margin is
inconclusive. V44 remains experimental. See the [Ares V44 finding](docs/findings/2026-09-30-ares-v44-shared-sector-exploration.md)
and [source snapshot](bots/ares-v44-shared-sector-exploration/).

## Experimental C++ family: Sparta

Sparta 01 forks Carthage 05 and adds a survival veto for our original queen,
team-wide pursuit of a sighted enemy queen, and unconditional non-queen
head-on trades against that target. A large route bonus prioritizes the
queen's last known position. It preserves Carthage's sprint/search base.
Sparta 01 scored 17–23 in its first 40-game serial screen, with 16 wall-caused
queen deaths. Sparta 02 adds a queen-only unknown-edge veto. Its fixed-seed
paired screen found no improvement: 12–12 against Sparta 01,
9–15 against Carthage 05, and no queen alive@490 among reached games. Sparta 03
adds two local interceptors when an enemy head threatens a visible queen. It
tied Sparta 01 (12–12), lost to Carthage 05 (9–15), and the queen died in all
48 games. Sparta 04 scored 13–11 against Sparta 01 and 7–17 against Carthage
05; its queen was alive@490 in 3/32 reached games, compared with Sparta 03's
0/22. It killed the enemy queen in 13 games, down from Sparta 03's 28. Sparta
05 allowed splits after retaining length seven. It recorded 27 queen splits
and 14 enemy-queen kills, but kept the queen alive@490 in the same 3/32 games
and matched Sparta 04's scores. Sparta 06 scored 13–11 against Sparta 01 and
6–18 against Carthage 05,
with 2/32 queens alive@490 and 15 enemy-queen kills. Sparta 07 scored 9–15
against Sparta 01 and 8–16 against Carthage 05; it reduced head-on deaths but
raised wall deaths and had no queens alive@490. Sparta 08 added an unknown-edge
veto but matched Sparta 07's screen and queen-safety totals. None is admitted
to the all-map frontier. See the
[Sparta family notes](docs/sparta-family.md), [queen-priority finding](docs/findings/2026-10-02-sparta-queen-priority.md),
[Sparta 01](bots/sparta-01-queen-priority/), [Sparta 04](bots/sparta-04-queen-reserve/),
and [Sparta 08](bots/sparta-08-edge-safe-queen-flee/).

## Defaults and upkeep

The contest API lists **Ares V40 — `Ares V40 length-priced sprints`, submission
v93 (ID 13010)** as active. Its API source hash is
`1a4ee3dc7148ef7b8c2488879d09c75d8b9cfbc32364d8c03e96e35013597737`. Server
deployment does not promote V40 locally: it remains experimental after an
11–9 one-seed screen against V37. The previous active upload was Ares V37,
submission v92 (ID 12851), whose API source hash was
`d0b6e74c95f9d98e1cbceb58c8d82179d21ad676b699aa2ab3e11d2248ca683f`. See the
[V28 finding](docs/findings/2026-09-30-ares-v28-minimum-sacrifice-enclosure-split.md),
[V32 finding](docs/findings/2026-09-30-ares-v32-dead-end-split-orientation.md),
[V33 finding](docs/findings/2026-09-30-ares-v33-split-portal-route-handoff.md),
[V35 finding](docs/findings/2026-09-30-ares-v35-crown-clipped-dash-threat.md),
and [V36 finding](docs/findings/2026-09-30-ares-v36-no-pearl-portal-scout.md).
[`comparison.toml`](comparison.toml) keeps Ouroboros V10, Hunter V14, Hunter
V20, Fry V14, and Kraken V04 as controls. See [`docs/benchmarking.md`](docs/benchmarking.md)
for the workflow, [`game_stats/README.md`](game_stats/README.md) for the ledger,
and [`maps/new/EXPLAINER.md`](maps/new/EXPLAINER.md) for custom maps. Update this table with exact source
fingerprints and linked results when a candidate is screened or admitted.
