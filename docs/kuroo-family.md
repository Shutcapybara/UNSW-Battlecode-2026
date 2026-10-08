# Kuroo family — capacity and escape safety

Created 8 October 2026 at the user's request, based primarily on Akaashi02
and Akaashi12. Existing measured snapshots remain unchanged.

- `kuroo-01-soft-reserve` forks `akaashi-02-queen-strike`.
- `kuroo-02-escort-soft-reserve` forks `akaashi-12-queen-strike-escort`.

## Measured replay diagnosis

[Match 1427506](https://game.battlecode.au/visualiser?match=1427506), Around
UNSW, Team A submission20432/Akaashi12: A405 died against a wall at protocol
round199 (the user's visualiser turn19755). Length7, head(2,52), unit count63,
limit64. Original decision `MOVE N`; no TLE. The policy temporarily reduced
the limit to63 to reserve the queen's slot, suppressing escape splitting.
The guard also excluded worker splits at63. With the real limit restored,
`tyr_escape_split` identifies legal size5 with a free exit for the child.
The diagnostic trace reports move score−1001 and no guard override.

Official-engine replay oracle with seed `63fdd981139ad925` reproduces all
54,133 turns: zero mismatches, zero extra turns, winnerB at round499.
Artifacts: `build/finals/20261008-wall-1427506/`, including metadata, original
replay, oracle blocks, diagnostic trace, and exact-history candidate output.
Kuroo02 outputs `SPLIT 5` on the original A405 input history. This establishes
an action correction, not an adaptive opponent outcome or strength gain.
A scripted SPLIT5 engine branch confirms a valid split at r199 (parent2,
child5). Subsequent recorded commands are invalid for the changed state and
new ID allocation, so r200 deaths in that branch are not survival evidence.

## Proposed general strategy and implemented initial settings

Replace the policy's hard worker limit reduction with a soft routine-production
penalty. For a normal64-unit limit, pressure starts inside the final eight
slots, with four free slots as the initial economic target. This is a soft
incentive, not a guarantee that four slots stay vacant. For small limits the
band scales to `min(8,max(1,limit/8))`.

Penalty = `(band - free_slots) / band * (16 + 4 * lost_free_steps)`, bounded
below by zero. Routine split reward is8, so at four free slots the base
penalty cancels it. The extra term preserves the parent's `ceil(length/4)`
free movement allowance: splitting a length5 or6 parent into a two-cell child
loses a free step; length7 or8 retains two. Apply this to full-body production
and partial-body opening production. Opening rescue and terminal escape
splits are exempt. Existing queen shedding receives the production penalty;
its stronger reward can still justify splitting.

After the guard, a worker can spend the final actual slot if every immediate
single-step simulation is fatal, its full body is known, and the tail escape
has a visible free exit. Preserve intentional feeds, head-on trades, existing
splits, and queen decisions. The inherited guard still reserves one slot for
ordinary workers; this terminal exception prevents the observed wall death.

Validation so far: capacity/threshold/emergency-exclusion regression passes
for both snapshots. Inherited queen escape and pearl-funded queen strike CPP
fixtures pass for both. Native eight-fixture development comparison of
Kuroo02 against Akaashi02/12 on Around UNSW and Trophy, both seats, seed81020
finished **4–4**, with zero runner errors: **3–1** versus Akaashi02 and
**1–3** versus Akaashi12. Recorded under `build/finals/20261008-kuroo02-screen/`. This small two-map screen does not establish an improvement; all eight replay winner checks pass, with zero TLEs or invalid deaths.
Native execution is not sandbox runtime validation. Analysis: `analysis/`
inside the screen directory.
At the user's request, Kuroo02 was uploaded as **20472 (v111)** and compiled.
It auto-activated after compilation; 20432/Akaashi12 was restored and verified
as the sole active submission. The user then directed that Kuroo02 remain
active and be tested against the same opponent from match1427506 on every map
lost there. Kuroo02 was activated and verified sole active; 14 unranked games
against ComTamSuonNuong (team193) were accepted and verified pending, one each
on Around UNSW, Australia, Devil, Islands, Maze, Portals, Prisoners Dilemma,
Schooltime, Slithery Fight, Stripes, Tower Defense, Trauma, Trophy, and
weakhold. This is a requested submission/test, not a strength promotion. No
sandbox runtime validation has been completed.

## Kuroo03 — queen retention and obstructing crown feed (8 October)

User observation: [Slithery Fight1431111](https://game.battlecode.au/visualiser?match=1431111),
visualiser round439. Protocol round438 queen A1 splits31 into parent7/child24;
A1 dies at protocol460, length7, head-on against B1926. No own TLE or invalid
fault. Reconstructed original queen history reproduces all461 commands exactly.
The guard selects cage escape `C`, `SPLIT24`: the unsplit queen's single-step
horizons are1/0/0/0, while removing A573's visible body opens six-turn north
and west routes. Replacing those cells with pearls also leaves those routes
open in the same-state guard check. A573 is length37 and forages instead of
feeding. Late queen feeding previously excluded every `role_crown` snake.

New immutable candidate `bots/kuroo-03-queen-retention` forks02:

- From round400 a crown within queen feeding range16 may feed a fresh,
  unconfined queen. Other existing feeder timing stays unchanged.
- A feeder of length>=8 with known body cells adjacent to a queen beacon
  aged<=2 may intentionally die before its head reaches distance4. This
  clears known obstruction and creates nearby food; stale/distant-only
  evidence does not trigger this sacrifice.
- In the feeding phase, queen target scoring softly favors visible support
  within distance4, retaining crowd and enemy-risk penalties.
- Port bounded three-step queen dodges and independent enemy threat BFS
  from Akaashi05. Check legal sprint alternatives before a late emergency
  split; preserve genuinely necessary cage splits.

Measured local checks: new feed/endpoint/cage regression passes; inherited
queen escape, queen strike and soft-capacity C++ fixtures pass. Diagnostic
candidate history selects intentional feed for A573 at r436. The candidate
changes earlier commands, so its later reconstructed queen body is not the
original full-body state; its r438 `MOVE N` is **not** evidence that the
original queen can move north with A573 alive. Worker history is approximate:
original573 has82 command mismatches over362 reconstructed turns. Full server
oracle fails (51,992/52,007 mismatches, early divergence); no engine branch,
adaptive survival outcome, or counterfactual win is claimed.

Final source fingerprint:
`5ae4fb0d34f6929e1b22f28040b9c86cde7243bc180a5421a0b6d5799481a0d6`.
Final native screen against02, Slithery Fight/Trophy, both seats, seed81031:
**2–2**, one win/loss on each map; zero runner errors, replay TLEs or invalid
deaths. Artifacts `build/finals/20261008-kuroo03-final-screen/`; diagnosis
`build/finals/20261008-queen-1431111/`. Preliminary pre-threat-BFS version,
seed81030, also2–2; it is a different frozen source and is not pooled with03.
No sandbox/runtime-budget validation, upload or strength promotion.

The02 server retest1431103–1431116 has completed **2–12**: Australia and Maze
won. All14 replays, economy/queen/longest curves and linked split/death reviews
are under `build/finals/heartbreaker-iteration/kuroo02-series/review/`; zero
own TLEs/invalid deaths. Queen dies in13/14 games (including both wins), so
broader queen survival remains unresolved. Kuroo03 needs broader paired
strength and runtime checks before a server iteration; Kuroo02 stays active.

## Expanded paired comparison — 8 October 2026

Kuroo02 played Akaashi02 and Akaashi12 on 16 maps, two fresh seeds per map,
and both seats: 64 games per opponent (128 total). Maps: Australia, Autarky,
Default, Devil, Prisoners Dilemma, Islands, Maze, Portals, Queen of Spades,
Schooltime, Slithery Fight, Stripes, Tower Defense, Trophy, Around UNSW, and
Weakhold. Seeds81021–81024 were split across two independent runs. Native
unswbc1.2.9; sandbox disabled. All128 runner results had no errors. Replay
winner checks found zero faults; the registered feature extraction decoded
128/128 games and all1,152 V0 bookkeeping residuals were zero. Native runs do
not measure sandbox CPU use.

| Opponent | Kuroo record | Win rate | Hierarchical 90% interval |
|---|---:|---:|---:|
| Akaashi02 | 32–32 | 50.0% | 37.5–62.5% |
| Akaashi12 | 34–30 | 53.1% | 42.2–64.1% |

Intervals resample maps, then games within each sampled map (50,000 draws).
They include seat and seed variation and remain wide. Kuroo02 has no decisive
measured advantage over either parent. Its small edge over12 is four games in
64 and does not establish a strength improvement.

Map records (wins–losses in four games per map and opponent):

| Map | vs02 | vs12 |
|---|---:|---:|
| Australia | 2–2 | 3–1 |
| Autarky | 2–2 | 2–2 |
| Default | 2–2 | 2–2 |
| Devil | 1–3 | 2–2 |
| Prisoners Dilemma | 2–2 | 2–2 |
| Islands | 2–2 | 2–2 |
| Maze | 1–3 | 2–2 |
| Portals | 1–3 | 2–2 |
| Queen of Spades | 3–1 | 2–2 |
| Schooltime | 1–3 | 2–2 |
| Slithery Fight | 3–1 | 2–2 |
| Stripes | 2–2 | 2–2 |
| Tower Defense | 2–2 | 2–2 |
| Trophy | 2–2 | 2–2 |
| Around UNSW | 4–0 | 3–1 |
| Weakhold | 2–2 | 2–2 |

Registered F1 paired side-feature differences (Kuroo minus that match's
parent; intervals resample maps, not isolated rounds):

| Feature | vs02 difference (90% map interval) | vs12 difference (90% map interval) |
|---|---:|---:|
| Total length at round100 | −1.6 [−5.8, +2.2] | +0.8 [0.0, +2.0] |
| Longest dragon at round100 | +0.17 [−0.08, +0.52] | +0.23 [0.0, +0.55] |
| Pearls by round100 | −5.3 [−13.7, +2.1] | −0.8 [−1.7, 0.0] |
| Split count, rounds100–249 | −1.2 [−6.0, +3.7] | +1.2 [−0.8, +4.6] |
| Deaths per1,000 dragon-turns | +1.12 [+0.30, +1.95] | +0.43 [+0.21, +0.67] |
| Wall deaths per1,000 dragon-turns | +0.11 [−0.33, +0.53] | +0.08 [+0.001, +0.16] |
| Sprint segments spent per pearl | +0.002 [−0.004, +0.008] | −0.001 [−0.0015, +0.0001] |

The near-even match scores coexist with slightly higher measured death rates
for Kuroo in both comparisons. Early total material and free-step sprint
usage do not show a clear broad advantage from the soft reserve. Those are
paired play features, not causal estimates of the reserve alone: both bots
adapt to each other's behavior, and several intervals cross zero. This panel
compares Kuroo02 with its parents; it is not a test against an independent
opponent pool or an untouched confirmation set.

Artifacts: `build/finals/20261008-kuroo02-expanded/` and
`build/finals/20261008-kuroo02-expanded-b/`; combined feature rows, map
bootstrap analysis, and checks are in
`build/finals/20261008-kuroo02-expanded-combined/summary.json` and its JSONL
feature tables. The first multiprocessing extraction was blocked by the
sandbox's process permission; the successful registered extraction ran in one
process and reported zero errors.

## Kuroo03 expanded map test — 8 October

User requested more maps. Final03 was frozen unchanged (hash
`5ae4fb0d34f6929e1b22f28040b9c86cde7243bc180a5421a0b6d5799481a0d6`).
Tested vs `kuroo-02-escort-soft-reserve` on all22 `maps/live/*.map`, seeds81032
and81033, both starting sides:88 native games. Four independent serial shards;
each dry-run checked first. Frozen sources/maps, seed manifests and replay
paths are saved. This is a development comparison against02, not independent
opponent confirmation or sandbox budget validation.

**Measured:31 wins,57 losses,0 draws.** Win score35.2%;90% map-cluster bootstrap
interval[26.1%,43.2%]; advantage over50%−14.8 percentage points, interval
[−23.9,−6.8]. All88 replay winners agree with runner results; zero runner
errors, replay TLEs or invalid deaths for either bot. **Reject03 as a strength
improvement; do not upload/promote it. Kuroo02 remains active.**

| Map | Kuroo03 vs02 |
|---|---|
| Colosseum | 1–3 |
| arena | 0–4 |
| australia | 0–4 |
| autarky | 3–1 |
| big_empty | 2–2 |
| default | 2–2 |
| default_small | 2–2 |
| devil | 2–2 |
| dilemma | 0–4 |
| islands | 1–3 |
| maze | 3–1 |
| portals | 0–4 |
| queen_of_spades | 1–3 |
| schooltime | 0–4 |
| slithery_fight | 2–2 |
| stripes | 1–3 |
| stronghold | 2–2 |
| tower_defense | 1–3 |
| trauma | 2–2 |
| trophy | 2–2 |
| unsw | 2–2 |
| weakhold | 2–2 |

The targeted safety/economy metrics also fail to show the desired benefit:

| Metric | Kuroo03 | Kuroo02 | Paired difference,90% map interval |
|---|---:|---:|---|
| Queen alive at game end |15/88|24/88|−10.2 percentage points[−17.0,−3.4]|
| Queen alive at r300,59 games reaching r300 |19/59|23/59|Descriptive,conditional on reaching300|
| Queen survival round,game-end-censored mean |201.3|218.3|−17.1[−39.3,+3.5]|
| Queen length at game end,dead=0 |3.625|4.568|−0.943[−3.045,+0.977]|
| Queen segments shed after r290,per game |1.398|1.420|−0.023[−1.193,+1.398]|
| Self-deaths length>=8 after r400,per game |3.432|2.795|+0.636[+0.250,+1.068]|

Self-deaths include intentional feeds and accidental self collisions; the
replay cause alone does not identify motive. Queen survival times are
right-censored at game end and are not uncensored death-time estimates.
The whole03 bundle changes feeding, queen targeting, dodge paths and threat
marking; these results do not identify which rule caused the regression.
The original same-state obstruction mechanism remains supported, but it
does not imply an overall strategy improvement. Proposed next experiment:
isolate fresh local obstruction feeding from the other03 changes in fresh
snapshots, then repeat paired tests; no new behavior change started here.

Reproduction: `.venv/bin/python build/finals/20261008-kuroo03-expanded/run.py`
(fresh output only); analysis:
`python3 build/finals/20261008-kuroo03-expanded/analyze.py`.
Artifacts and complete per-game metrics:
`build/finals/20261008-kuroo03-expanded/analysis/summary.json` and
`analysis/diagnostics.json`; source/map/seed manifests in each `part0`–`part3`.

### Kuroo03 regression diagnosis — 8 October

Follow-up asked what went wrong/how to fix it. Additional replay analysis
`build/finals/20261008-kuroo03-expanded/diagnose.py`, output
`analysis/diagnosis.json`: queen deaths before r29003=66 vs02=56; r290–399
6 vs5; r>=4001 vs3; queens alive15 vs24.29 matches end before290,03 wins9
and loses20. Only guard/dodge/threat changes differ before290; support-target
change starts290 and new crown/body-feeding starts400. Thus the early behavior
regression cannot be attributed to those late additions. This timing does not
isolate individual guard changes or estimate their standalone win effect.

Queen paid movement segments03=154 vs02=22 across88 games. Queen wall deaths
6 vs0; h2h61 vs58. Large self-death length after400 totals4652 vs3959; causes
include intentional feeds and accidental self-collision. These describe the
bundle's play, not independent causal attribution.

Code review: new queen dodge permits paid sprint paths from round zero and
ranks endpoint risk without an explicit retained-length cost. New late escape
fallback picks the first path passing the terrain/body horizon, with no
explicit enemy-reach landing filter. Existing after_path tests obstacles and
future head adjacency but does not itself reject enemy-reachable current-turn
landings. Body feed trigger proves adjacency to a<=2-round beacon, not that
this body is the critical blocking route or that the queen can harvest the
corpse safely. Blanket late crown role conversion starts within range16,
before a verified local need. Queen support bonus attracts any visible ally
head, without testing whether it can actually escort/protect her.

Proposed fix: fork02 and isolate local obstruction-feeding from global guard
changes; require current visible queen or an explicit distress request,
verified obstruction/route benefit and safe food access, elect one donor,
preserve cover under an active attack. Test queen movement independently:
prefer safe free sprints, penalize paid length loss unless needed for survival,
apply landing threat checks to every fallback, and use bounded search capable
of the long queen's actual free-step allowance rather than an arbitrary
three-step ceiling. Future horizon currently models single-step turns and
can be pessimistic for long queens; change that only as a separately tested
snapshot. Run component ablations and broader paired/runtime checks before
combining. No bot source edits or promotion performed in this diagnosis turn.

## Kuroo04/05 — isolated corrections from02 (8 October)

User approved separate corrections and tests after03 regression diagnosis.
Both new snapshots fork immutable02; none of03's blanket crown conversion,
all-game sprint dodge/threat changes or queen support attraction are retained.

- `kuroo-04-local-obstruction-feed`: after400, a visible queen must have no
  clear known adjacent exit. Donor body removal must open an adjacent food
  cell with another known step; elect lowest ID among visible local blockers;
  do not sacrifice with a visible enemy head within6 of the queen. Return an
  intentional self-feed only into known own body. Existing feeder/crown
  behavior otherwise stays inherited. This checks a local two-step opening,
  not a full future queen survival certificate. Invisible queens cannot
  request rescue in04; no new distress radio protocol has been implemented.
- `kuroo-05-free-queen-escape`: after290 and length>=8/full known body, try
  a bounded beam of legal **free** paths before a split or short-horizon
  action. Search up to `min(16,ceil(length/4))` steps, beam8 endpoints and
  at most16 horizon questions. Require known terrain and landing outside
  marked enemy reach/head adjacency; retain inherited six-turn body check.
  No extra paid movement, no early guard change, no new feed rule. This
  still inherits the guard's single-step future-turn model and optimistic
  node-cap behavior; it does not fix every long-queen pathfinding limitation.

Regression `python3 tests/test_kuroo_isolated_safety.py` passes: donor
eligibility, clear exit/unknown terrain/attacker/early/invisible exclusions,
single-donor election; five-step free queen escape beyond the old three-step
cap with preserved length, unsafe/early/partial-body rejection. Inherited
queen escape(modeE), queen strike and soft reserve CPP fixtures pass for both.

Frozen fingerprints:
04 `e9961318b84164f3297dc0c49b8aa8f22576646ea5de0c9a85c439c7141dd1e4`;
05 `bf5e7308ae8bdcbd31538f399171cb3b01da36a6b6b11b133d757f68185f4041`.

Native development panel: each against02 on all22 live maps, seed81034,
both seats,44 games each/88 total. Four independent serial shards, dry-run
first. Both source fingerprints unchanged after testing. All88 replay
winner checks pass, zero runner errors/TLE/invalid deaths for either side.

| Result | Kuroo04 | Kuroo05 |
|---|---:|---:|
| Win/loss vs02 |22–22|21–23|
| Map-cluster90% score interval |[50%,50%]|[43.2%,50.0%]|
| Queen alive at game end,candidate vs02 |12/44 vs12/44|12/44 vs12/44|
| Final queen length mean,dead=0,candidate vs02 |3.841 vs3.841|4.614 vs3.841|
| Late queen segments shed/game,candidate vs02 |1.614 vs1.614|0.886 vs1.614|

Every04 map is1–1. All22 swapped-seat replay pairs have identical gameplay
snapshots/events/results: no observable effect on this panel. The degenerate
bootstrap interval reflects one seed and exact paired symmetry; it is not
proof of equivalence on unseen seeds/maps or that the new predicate never
runs (an inherited feed could choose the same action).

05 is1–1 on21 maps and0–2 on Islands. Logged `BK:L` new free escapes occur
**twice**, on Stronghold/Islands;20/22 map-pair replays remain identical.
Stronghold A queen finishes49 versus15 for the02 A queen in the swapped
control-like seat pair; she sheds32 rather than64, but A still loses to a
length74 B queen. Islands A queen survives358 vs339 in the swapped02 A
history; both queens ultimately die, and candidate A loses rather than
winning. Thus the measured length benefit is concentrated in one map and
has no demonstrated win gain. These reactive paired games are not fixed
opponent engine counterfactuals. Do not combine/promote these candidates.

Focused05 sandbox check: Slithery Fight, seed81034, both sides,1–1, same
winner per seat as native. No candidate TLE/invalid deaths across53,510
metered turns. Candidate peak11,060,270 points(A)/10,904,744(B);
p99 8,235,691(A)/8,073,997(B). This is a two-fixture runtime screen, not
coverage of every map or worst-case search state.04 has no sandbox check.
Artifacts `build/finals/20261008-kuroo05-runtime/runtime-audit.json`.

Reproduction/analysis:
`.venv/bin/python build/finals/20261008-kuroo04-05-isolated/run.py` (fresh
output), `python3 .../analyze-kuroo04.py`, `python3 .../analyze-kuroo05.py`,
`python3 .../effects.py`. Full manifests/maps/replays and per-game summaries
are in that directory, with combined `kuroo04/analysis/` and
`kuroo05/analysis/`. No upload/activation; Kuroo02 stays active.

Proposed next: a separate queen-issued targeted distress packet is needed
for the original1431111 case, where the donor's head is outside queen vision.
The queen should identify the obstructing donor and requested opening; the
donor should validate a fresh request and local body match, and only one
should yield. This requires its own radio/turn-order regression and paired
comparison. The stronger04 visibility condition alone cannot fix that
specific original state. No distress candidate built in this turn.

## Kuroo06/07 — targeted queen distress (8 October)

User explicitly requested implementation and continued interrupted test runs.
06 forks02;07 forks06 solely to fix the visible-queen distance rejection.
Measured snapshots remain immutable. Active server remains02; no upload or
activation was performed.

Protocol type8 uses the existing team marker/checksum envelope. Payload:
donor ID12 bits, opening x/y7 bits each, round9 bits, queen ID1 bit,
pre-action queen length8 bits. Requests expire after two rounds, never rewind
a newer request, reject wrong recipients/team markers/corrupt checksums and
invalid coordinates/times. The queen, from r400/length>=8/full known body,
selects one nearby body owner whose removal increases known reachable space
by>=4 cells to>=8 total (BFS cap min32,length+4). Preserve a visible escort
head if a visible attacker is present. This is a bounded static topology
check, not a guarantee of future safe pathfinding or food harvest.

Donor eligibility requires length>=8, the named opening still matching
known own body, a fresh request, no visible enemy head within6 of the opening,
and a visible queen still near it. Exception: a same-round queen sighting may
certify an off-screen unknown tail of a partially reconstructed body, within
plausible body distance; never contradict visible cells, and never apply
this certificate after the next round. The donor selects a known own-body
collision, marked as intentional feed so the inherited guard preserves it.
Verified queen strikes still take priority. Queen movement/split guard is
unchanged: this protocol does not ban emergency splits or prove that the
original1431111 queen retains31 cells.

Requests override gossip on all four sonar directions. Sonar can hit the
selected body while its head is outside queen vision, but intervening own
and foreign bodies can block/refract rays. Sending a request is not receipt.
Diagnostics `QD:R <donor> <cell>` and `QD:F` distinguish sends and feeds.

### Regression and replay evidence

`python3 tests/test_kuroo_targeted_distress.py` verifies target/topology,
expiry, exact-recipient, checksum/team, attacker, future/stale, monotonic
message order, known-body and current unknown-tail-certificate conditions.
`python3 tests/test_kuroo_distress_visibility.py` verifies the06 rejection
and07 acceptance of a queen two diagonal cells from an opening (Manhattan4,
Chebyshev2), with expiry/distant-queen rejection retained.
`.venv/bin/python tests/test_kuroo_distress_delivery.py`, also run with
`KUROO_DISTRESS_BOT=kuroo-07-distress-visibility`, runs an official-engine
fixture with the native donor process: protocol3 is negotiated before the
message, the distant donor receives it in the same round and self-feeds,
and the scripted queen grows8→9 on the donated food. The fixture deliberately
ends other actors with empty commands; it is a mechanism regression, not
an adaptive win/survival trial. Inherited escape(modeE), strike and capacity
CPP fixtures passed against both06 and07.

Original1431111 reconstructed queen history emits a request to573 at
protocol438, while retaining `SPLIT24`. Injecting that packet into worker573's
reconstructed history yields intentional `MOVE E`/`QD:F` at438. Original
worker reconstruction has82/362 command mismatches; original full engine
oracle fails. These are decision diagnostics, not an exact engine
counterfactual or a saved-game claim. Artifact directory
`build/finals/20261008-kuroo06-distress/`. An initial captured-body fixture
sent a64-bit packet before first-turn protocol negotiation; it failed and
was replaced by the portable protocol3-negotiated regression above.

### Native and sandbox results

Each candidate was compared against02 on all22 live maps, seed81036,
both starting sides (44 games each). Dry-runs first; source/map hashes pinned.
06 raw result23–21, but three invalid deaths occurred before the new protocol
starts: opponent149 r204 on Stronghold, candidate750 r250 on Slithery,
opponent110 r378 on Weakhold. Zero TLEs.41 clean games score21–20,90%
map-cluster interval[47.6%,55.0%]. Do not credit those early faults or cross-run
behavior differences to late distress rules.06 had19 request turns in one
Stronghold game, only one named-donor ray hit, and zero actual feeds.

06/07 replay states in that Stronghold seed already differ at r205, following
the06 opponent invalid death. Therefore06→07 whole-game outcomes are not a
clean late-rule causal comparison, despite matching map/seed/source manifests.

07 final result **22–22**, all44 replay winner/fault checks pass: zero runner
errors, TLEs or invalid deaths. Every map is1–1 on this seed. End-game queens
alive7/44 on both sides; queen final length mean2.795 vs0.955 (dead=0).
The degenerate50% map-bootstrap interval follows exact paired score symmetry
with one seed; it is not proof of equivalence/generalization.

**Observed successful feed:** Stronghold, candidate B, queen1 requests donor5
at r422; donor5 self-feeds that round at length49. Queen eats16 corpse pearls
from that donor, survives to500 and finishes length87, versus6 for the
corresponding02 B queen in the opposite-seat run. Mirrored gameplay states
are identical through start-of-round422 and first diverge at423 after this
request/feed.07 has one request and one successful feed across the44 games.
The stronger final queen does not change the match winner or aggregate
win rate; the measured benefit is concentrated in this one case.

07 Stronghold sandbox, same seed/both sides:1–1, zero candidate TLE/invalid
deaths across25,888 metered turns. Candidate peak10,256,438(A)/10,336,059(B)
points; p99 8,057,655(A)/8,515,144(B).06 Slithery sandbox pair also finishes
1–1, zero candidate faults across52,274 metered turns; peak10,992,064(A)/
10,954,174(B), p99 8,557,994(A)/8,402,543(B). These are focused runtime
screens, not all-map/worst-state budget guarantees.

Interrupted07 native fixtures and06 sandbox attempts were resumed using
unchanged sources, retaining completed results. Harness180/360-second
wall-clock timeouts are recorded; a600-second retry completes the06 A
sandbox game in127.9s after recovery. Two07 native timeout entries were
rerun to completion. Do not classify harness timeouts as judge TLE events.

Frozen hashes:
06 `4f3480f7cedafa8f8e457fe722abe9fea1ca342b97823a1096f7b87ec58ff002`;
07 `d01d1fa570f56a4048afa684b2c3d8b0088f741db668c6f3652f80de84942ace`.

Artifacts: `build/finals/20261008-kuroo06-screen/analysis/`,
`build/finals/20261008-kuroo07-screen/analysis/` (summary, activity and
feed-case.json), and `20261008-kuroo06-runtime/`/`20261008-kuroo07-runtime/`
(runtime-audit.json, logs and replays). Each screen has run.py/analyze.py and
four frozen part manifests;07's recovery runner resumes existing results
with600-second limits. Protocol mechanism implemented and tested; **07 stays
local/unpromoted**,02 remains active. Proposed next: independent fresh seeds
and opponents, with receipt-aware routing if requests remain rarely delivered.

### 8 October — user-requested Kuroo07 submission and activation

User explicitly instructed “submit and keep it active”, superseding the
previous request to retain02 and the local-only status of07. Exact tested
snapshot `d01d1fa570f56a4048afa684b2c3d8b0088f741db668c6f3652f80de84942ace` packaged as15 root C++ source/header
files, zip3760694 bytes, SHA256 `25dd4d8af6488e3363d2f338aaf6a260e7087bd6f4ac96cc0014afa4f66468dc`. Fresh authenticated
preflight verified team7 and incumbent20472. Uploaded once as**20627/v112**,
`LV-kuroo-07-distress-visibility-25dd4d8a-ai`. Server compilation completed successfully; authenticated
readback verifies20627 is the**sole active** submission. Server sourceHash
`7e9f3afe2cad37d6d3b2076cc33d5dc6d8be2f5c727c8bdb0e4938bab635d07d`. No incumbent restoration or new match queue.

This is an explicit user-requested deployment, not statistically confirmed
strength promotion; the measured22–22 development panel remains unchanged.
Receipt/archive/preflight/readback: `build/finals/20261008-kuroo07-submit/`.
