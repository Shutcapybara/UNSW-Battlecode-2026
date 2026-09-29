# Ares family

Ares is a C++ research family built from the Anna protocol-3 chassis. It copies anna-a02-chassis into its own versioned directory and does not modify the Anna control.

## V01 — safe launch routing

The ares-v01-safe-launch-routing snapshot keeps Anna's time-aware movement model and adds four switchable behaviors:

1. Routine splits wait for a known nearby resource and a clear child site.
2. A trapped escape split chooses the largest viable rear child rather than always shedding two segments.
3. A small identity bonus breaks opening target ties; one in three dragons mildly prefers a known paired-portal route.
4. A recent same-pair return is softly discouraged near the remembered exit.

The target and crowding conditions follow the newborn-death and small-dragon crowding measurements in the efficiency ledger. The emergency split responds to the wall-step replay and the repeated dead-end split observations. The target tie-break borrows Tyr V12's positive-only lane idea, but leaves the route objective primary: Bifröst's broader opening-sector and route-ownership changes often regressed outside their target maps. The portal cost borrows Bifröst's exit-memory direction and Tyr's room-return work while avoiding a hard portal ban; the field measurement found portal safety, rather than transit volume, is the issue.

Tyr V12 is a useful matchup reference, not the all-map Ares parent: its 50–42 all-map result versus Yuna V05 had a strong seat split and remaining sandbox faults. Fenrir V20 remains the top measured all-map frontier candidate in FRONTIER.md. Heimdall V10's broad panel success also supports the value of spatially informed routing, but its echo-role design is not copied into this single-process C++ policy.

## V01 benchmark result

The completed seed-1 panel used unswbc 1.2.1: 8 opponents × 10 live maps × 2 seats (160 Ares games and 160 Anna control games), plus 20 direct Ares–Anna games. All 340 replays extracted successfully. The scorecard applies the saved per-map field medians and field distributions in docs/analysis/benchmarks; the raw field corpus was not present to regenerate them. Table values are medians across 160 side-games.

| Metric | Ares V01 | Anna A02 | Change |
| --- | ---: | ---: | ---: |
| Mean of four field-normalised pearl checkpoints | 0.4705 | 0.4402 | +0.0303 |
| Pearls at r50, field-normalised | 0.5000 | 0.4674 | +0.0326 |
| Pearls at r100, field-normalised | 0.5078 | 0.4772 | +0.0306 |
| Pearls at r150, field-normalised | 0.4751 | 0.4280 | +0.0471 |
| Pearls at r250, field-normalised | 0.3991 | 0.3883 | +0.0107 |
| Dragons at r100, field-normalised | 0.7500 | 0.7295 | +0.0205 |
| Total length at r100, field-normalised | 0.7746 | 0.7040 | +0.0706 |
| Births by r100, field-normalised | 0.5316 | 0.5266 | +0.0050 |

The economy mean is below BENCHMARKS.md's +0.05 acceptance gate. Dragons and total length at r100 did not fall. Both bots scored 21 wins, 138 losses, and 1 draw against the fixed roster (21.5/160 expected-score points).

| Tier 2 hygiene rate (per 1,000 dragon-turns) | Ares V01 | Anna A02 | Change |
| --- | ---: | ---: | ---: |
| Wall deaths | 3.9976 | 3.6447 | +9.7% |
| Own-body deaths | 0.0000 | 0.0000 | unchanged |
| Ally-body deaths | 1.3008 | 0.9016 | +44.3% |
| Ally head-on deaths | 1.1640 | 1.4344 | −18.9% |
| No-valid-action deaths | 0.0000 | 0.0000 | unchanged |

Ally-body deaths exceed the 10% guardrail. Newborn deaths within ten rounds fell from 29.41 to 22.22 per 100 births. Tier 3 proxies were mixed: pearl share at r150 and territory at r100 improved, while bed capture and length share at r250 fell. The direct Ares–Anna screen was 14–6 for Ares, with 9–1 as Team A and 5–5 as Team B; this small seat-skewed matchup does not override the equal fixed-panel score.

No atlas-off generalisation panel was run, so the results cover the known live maps only. V01 stays experimental and does not pass the documented acceptance gate. Its runtime-source fingerprint (C++/headers and bot.toml) is 6af8a6f47bd05da28b9d5b7ce2ca28a8d0acbcb10850c9138110a4ac27d24a62. The full result and run details are in [the V01 finding](findings/2026-09-29-ares-v01-safe-launch-routing.md). This closes the V01 report; no follow-up seed or tuning pass was run.

## V02 — Tyr V12 C++ policy port

Ares V02 is a separate copy of the Anna A02 protocol-3 scaffold with a native
C++ translation of Tyr V12's local target and movement policy. It carries the
resource-value target field, hysteresis, direction momentum, length/endgame
valuation, split decisions, enemy head-trade scoring, bounded sprint search,
and the Devil center/lane/friendly-trail bonuses. Its source implementation is
[here](../bots/ares-v02-tyr12-cpp-port/), and the strategy reference is
[tyr-v12-devil-scout-tiebreak](../bots/tyr-v12-devil-scout-tiebreak/).

The port also implements Tyr's sonar food gossip, remote density reports, crown
and prey beacons, paired-portal sharing, crown inheritance on large-child
splits, constrained-spawn separation, and retried split handoffs. It retains
Anna's hard safety tiers and room-valid split checks, so action ordering is an
adaptation rather than an exact Tyr V12 replay. It passed a C++20 executable
compile-check. A separate direct matchup screen against Tyr V12 is recorded
below. V02 remains experimental and separate from V01's measured scorecard;
the direct screen is not the fixed-panel acceptance benchmark.

## V03 — pure Tyr V12 C++ policy port

Ares V03 ports Tyr V12's scalar target and move policy, split scoring, threat valuation, sprint candidates, communication roles, and newborn separation to C++ on the Anna A02 protocol-3 runtime scaffold. The active policy does not use Anna's action tiers, enemy-near split veto, hard parent-room split gate, or map atlas. Anna's C++ controller adapter and persistent world model remain; body reconstruction can therefore differ from Tyr's Python observation state. See the [V03 source](../bots/ares-v03-tyr12-pure-cpp-port/) and [direct matchup finding](findings/2026-09-29-ares-v03-vs-tyr-v12.md).

The native seed-1 direct matchup covered the same ten live maps and both seats. Tyr V12 won **12–8**. Replay extraction succeeded on all 20 fixtures. On the benchmark-aligned round-100 diagnostics, Ares had 1.168 field-median births but 0.820 field-median units and 0.818 field-median total length; newborn deaths within ten rounds were 38.0 per 100 births, against Tyr's 29.0. This points to weaker retention after splitting. The direct screen is not the documented 140-side-game fixed-panel acceptance run. V03 remains experimental; no policy tuning followed this screen.

## V04 — Tyr V12 behavioral parity port

Ares V04 is a C++ translation of Tyr V12's active decision policy on Anna's
protocol-3 runtime scaffold. The port aligns Tyr's action scoring and the
state semantics that feed it, including partial-body observations, bounded
topology searches, radio freshness and crown memory, newborn separation, and
fallback behavior. Anna supplies the protocol adapter; its action rules do not
participate in decisions. See the [V04 source](../bots/ares-v04-tyr12-behavior-parity/)
and [behavioral parity finding](findings/2026-09-29-ares-v04-behavior-parity.md).

The ordered golden transcript suite covered ten live maps in both seats: 168,123
turns across 5,089 dragons, with zero move, split, or sonar
output differences against Tyr V12. This establishes parity only for those
recorded inputs. The seed-1 fixed-panel benchmark used all eight opponents in
the current `run_panel.ZOO`, ten live maps, and both seats (160 games); Ares
scored **117–43 with no draws**. The field-normalized pearl checkpoint mean
was 1.090, while r100 dragons and length were 1.118 and 1.000. Its hygiene
rates and full field-reference scorecard are in the finding. This absolute run
does not establish the parent-relative acceptance gate. V04 remains
experimental and is not admitted to the local frontier. The contest API lists
the requested upload as active submission v83 (ID 11244); the upload auto-
activated after processing. See the finding for its timestamp and scorecard.

## V05 — separation exception fixes

Ares V05 branches from V04 and fixes two confirmed separation failures: the
zero-`bed_wait` bed-value division and the constrained-newborn pearl pause's
missing global counter. A zero wait now values a bed only when it spawns in the
current round; the newborn can use its existing six-pearl pause budget while
keeping the normal route and first-step mask. These remove two exception
fallback paths from Tyr V12's Python behavior; they intentionally change
behavior on those cases. See the [V05 source](../bots/ares-v05-tyr12-separation-bugfix/)
and [bugfix finding](findings/2026-09-29-ares-v05-separation-bugfix.md).

On the seed-1 fixed panel (eight current opponents, ten maps, both seats), V05
scored **118–41–1** over 160 games, with no runner or extraction errors. Against
V04's matched-panel run, its normalized pearl-checkpoint mean rose only 0.007
(1.0905 to 1.0974), below the +0.05 gate; r100 dragons fell 0.047 while r100
length rose 0.009. None of the tier-2 death rates rose more than 10%, and panel
expected score rose 0.94 percentage points. The documented acceptance gate is
not met, so V05 remains experimental, is not admitted to the frontier, and was
not submitted. No seed-2 confirmation or further tuning pass was run; V04 and
active contest submission v83 remain untouched.

## V06 — expanded search and supported threat evaluation

Ares V06 branches from V05 and restores bounded high-effort search settings
measured in historical Bifröst and Skadi candidates: 160 target nodes normally,
64 at saturation, 60 in the first two turns, larger room-flood limits, and
Tyr's 12-length three-step candidate horizon. It also ports Skadi V02's
experimental Fafnir rule that discounts a predicted threat when a visible ally
at least as long as the attacker is within three tiles. Existing saturation,
late-game, and sparse-board guards remain. See the
[V06 source](../bots/ares-v06-expanded-search-support/) and
[experiment finding](findings/2026-09-29-ares-v06-expanded-search-support.md).

On the seed-1 panel (eight opponents, ten maps, both seats), V06 scored
**122–38–0**, compared with V05's 118–41–1. The normalized pearl mean rose
+0.0133, below the +0.05 gate; normalized r100 dragons improved from 1.071 to
1.200 and length from 1.009 to 1.035. No tier-2 death rate rose more than
10%. Dense Schooltime/Portals sandbox probes had zero timeout/crash errors,
with p99 max-of-games 7.4M points and an 8.6M maximum. It remains experimental,
not admitted to the frontier, and not submitted; no seed-2 confirmation or
further Ares iteration was run.

## Direct matchup screens: Tyr V12

### Ares V01

A native screen played Ares V01 against tyr-v12-devil-scout-tiebreak on the
same ten live maps, one game from each seat per map. With unswbc 1.2.2 and
simulation seed 1, Tyr won **20–0**, taking both seats on every map. Each game
returned rc=0; there were no draws. The 20 replay files and index are in the
ignored build/ares-v01-vs-tyr-v12-20260929/ directory. Full details are in
[the V01 finding](findings/2026-09-29-ares-v01-safe-launch-routing.md).

### Ares V03

A native seed-1 screen used the same ten live maps and both seats. Tyr V12 won **12–8**: Tyr swept Autarky, Dilemma, Portals, Queen of Spades, and Schooltime; Ares swept Default, Slithery Fight, and Trauma; Devil and Trophy split 1–1. All games returned rc=0. All 20 replays were extracted successfully. Logs, results, standings, manifest, features, and replays are in the ignored build/ares-v03-vs-tyr-v12-20260929/ directory. Benchmark-aligned measurements and limits are in [the V03 finding](findings/2026-09-29-ares-v03-vs-tyr-v12.md).

### Ares V02

A separate native screen used the same ten maps, both seats, unswbc 1.2.2,
and simulation seed 1. Tyr V12 won **20–0**, taking both seats on every map.
All 20 games returned rc=0, with no draws or runner errors. Logs, results,
manifest, standings, and 20 replays are in the ignored
build/ares-v02-vs-tyr-v12-20260929/ directory. The map-by-map results and game
rounds are in [the V02 matchup finding](findings/2026-09-29-ares-v02-vs-tyr-v12.md).

Each screen is one game per seat and map. These direct comparisons are separate
from the fixed zoo panel and its unswbc 1.2.1 Anna control. They measure only
these bot pairs and do not replace the fixed-panel gate or establish an all-map
ranking.
