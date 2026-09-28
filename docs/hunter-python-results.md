# Python Hunter experiments — 2026-09-24

The current submission-safe Python candidate remains
**hunter-v11-route-distance-exploration**. Python V13 scored 25W/19L in its
latest normal-runner pool, but failed `big_empty` sandbox validation late in
the game. The separate Python V14 experiment scored 20W/24L and its source was
removed. C++ V14 is a new behavior-matched port of V13; it nearly tied V13 in
the paired pool but lost all four `big_empty` matches. Its sandbox run and
large-map tactical diagnosis remain open. The user reports intermittent V09
large-map timeouts; fresh V09 `big_empty` runs passed, but medium/full and
repeated sandbox tests remain.

## Method

Each experiment uses the same three-version pool in two focused runs: newest
and second-newest, on all 11 maps, with both team assignments. Each focus plays
44 games. The two runs repeat their mutual head-to-head fixtures; those must
agree. Their union is a complete 66-game round robin and can also assess the
incumbent when an experimental version branches from it.

Wins earn 3 points and draws 1. `tools/hunter/summarize.py` verifies identical
source and map fingerprints, complete schedules, and matching repeated games.
It also scans logs for bot failures. A map with any such failure is excluded
from both sides of the tactical comparison so the weights remain equal.

C++ v03/v04 reject the bundled 16x8 `small` map at startup. Python accepts it.
Raw scores include those compatibility wins; tactical comparisons involving
these C++ versions exclude `small` entirely.

Initial overlapping eight-worker runs exceeded host process resources and the
180-second timeout. They were interrupted and resumed sequentially with four
workers and a 600-second timeout. Failed/incomplete fixtures were rerun; their
failed attempts are not counted as strategy losses. The final error counts
below refer to completed runs. Source files were frozen throughout each run.

## V05: current-observation, reachable attacks

V05 ports v04 to Python and restricts attacks to targets reachable within the
current movement budget. It blocks unsuitable heads as route intermediates and
uses only currently visible body counts to authorize a larger-target attack.
It preserves the minimum-three-survivor guard, growth policy, portal planning,
and directional sonar priority.

| Focus | Raw W/D/L | Raw points | Tactical W/D/L | Tactical points | Match errors |
| --- | --- | --- | --- | --- | --- |
| v05 | 28 / 0 / 16 | 84 | 24 / 0 / 16 | 72 | 0 |
| v04 | 19 / 2 / 23 | 59 | 19 / 0 / 21 | 57 | 0 |

**Historical decision:** accept v05 as the first Python version. It led by 15
tactical points in the v03/v04/v05 pool, and all 22 repeated head-to-head
fixtures agreed. V06 later replaced it. V05 still scores only 1W/3L on
`schooltime`; the gain is not uniform across maps.

Per-map results against v04 (each run contributes two games on each map):

| Map | v05 W–L | v04 W–L |
| --- | ---: | ---: |
| Colloseum | 3–1 | 3–1 |
| arena | 4–0 | 1–3 |
| big_empty | 2–2 | 3–1 |
| default | 2–2 | 1–3 |
| default_small | 2–2 | 2–2 |
| help | 4–0 | 1–3 |
| queen_of_spades | 2–2 | 2–2 |
| queen_of_spades_but_she_ages | 2–2 | 2–2 |
| schooltime | 1–3 | 2–2 |
| trophy | 2–2 | 2–2 |

Artifacts:

- [V05 focused results](../build/hunter-v05-small/results.json)
- [V04 focused results](../build/hunter-v04-v05-small/results.json)
- [Paired comparison](../build/hunter-v05-comparison.json)

## V06: pearl routing

V06 branches from v05. It compares visible route distance for pearl ownership
instead of Manhattan distance, and values shorter pearl routes ahead of strong
friendly separation. Exploration retains the original separation score.

| Shared pool (10 comparable maps) | W–D–L | Points | Matches |
| --- | ---: | ---: | ---: |
| v06 pearl routing | 22–0–18 | 66 | 40 |
| v05 safe attack routes | 20–0–20 | 60 | 40 |
| v04 team state sonar | 18–0–22 | 54 | 40 |

**Decision: promote v06 over v05 for now.** Both focused runs completed all 44
fixtures with zero match errors. Their repeated head-to-head results agreed.
The C++ v04 startup failures excluded `small` from both candidates' comparison.
The v06 gain is modest; medium/full tournaments remain necessary before release.

Artifacts:

- [V06 focused results](../build/hunter-v06-small/results.json)
- [V05 focused results on the same pool](../build/hunter-v05-v06-small/results.json)
- [Paired comparison](../build/hunter-v06-comparison.json)

## V07: full lifetime IDs over sonar

V07 independently branches from v05, leaving v06's pearl hypothesis out. It
uses tag `0xA8`, 20 ID bits, 12 length bits, two 6-bit coordinates, and a 10-bit
round field in a 64-bit message. Incoming state must be at most 20 rounds old,
within map bounds, and at least length two. Older messages cannot overwrite a
newer state. `MOVE_ASIDE` still overrides only the forward sonar channel.

The completed v07/v06 comparison covered all 11 Python-compatible maps with
zero match errors and no repeated-game disagreements. In their shared pool,
v07 tied v05 at 20–24; v06 led at 26–18. **Do not promote v07.** The sonar
protocol bug is fixed in code, but that change alone regressed in this pool.

Artifacts:

- [V07 focused results](../build/hunter-v07-small/results.json)
- [V06 focused results on the same pool](../build/hunter-v06-v07-small/results.json)
- [Paired comparison](../build/hunter-v07-comparison.json)

## V08: pearl routing plus wide sonar

V08 combines the v06 pearl changes with the v07 sonar format. Both focused runs
completed 44 games with zero errors and no repeated-game disagreements.

| Shared pool (11 maps) | W–D–L | Points | Matches |
| --- | ---: | ---: | ---: |
| v06 pearl routing | 24–0–20 | 72 | 44 |
| v08 pearl routing + wide sonar | 24–0–20 | 72 | 44 |
| v07 wide sonar | 18–0–26 | 54 | 44 |

V08 and v06 split their direct head-to-head games 11–11. V08 ties v06 overall
and beats v07, while sending distinct IDs correctly after v04/v05's six-bit ID
field aliases in high-ID matches. **Use v08 as the current candidate for its
corrected teammate state; retain v06 as the tactical-score leader.** The test
does not show a tactical gain over v06; medium/full tournaments remain needed.

Artifacts:

- [V08 focused results](../build/hunter-v08-small/results.json)
- [V07 focused results on the same pool](../build/hunter-v07-v08-small/results.json)
- [Paired comparison](../build/hunter-v08-comparison.json)

## V09: confidence-aware teammate lengths

V09 separates recent exact sonar length reports from visible body-count lower
bounds. Visible sightings cannot refresh old sonar timestamps. Reports expire
after 20 rounds; current partial body observations can still establish a fresh
lower bound for largest-friendly selection.

The behavior tests cover expiration after repeated partial sightings, use of a
fresh lower bound, expiration when unseen, and replacement by newer shorter
reports. Both focused runs completed all 44 fixtures with zero match errors,
and all 22 repeated head-to-head fixtures agreed.

| Shared pool (11 maps) | W–D–L | Points | Matches |
| --- | ---: | ---: | ---: |
| v09 confidence-aware teammate lengths | 26–0–18 | 78 | 44 |
| v06 pearl routing | 20–0–24 | 60 | 44 |
| v08 pearl routing + wide sonar | 20–0–24 | 60 | 44 |

V09 won its focused run 26–18 and, in the v08-focused run, scored 13 wins to
v08's 9 in their 22 head-to-head games. It beat both references by 18 points
overall. The largest weakness is `schooltime`, where v09 lost all four games;
the backlog's segmented-map item remains open. **Promote v09 as the current
normal-runner candidate, pending sandbox validation.**

The 26–18 scores above used pre-optimization v09 source and are historical.
Post-fix measurements against v08 and v10 are below.

Artifacts:

- [V09 focused results](../build/hunter-v09-small/results.json)
- [V08 focused results on the same pool](../build/hunter-v08-v09-small/results.json)
- [Paired comparison](../build/hunter-v09-comparison.json)

## V10: confidence-aware enemy sizes

V10 branches from v09 and records visible enemy body counts as timestamped
lower bounds. The estimate decays and expires after 20 unseen rounds, so stale
sightings cannot keep affecting the late-game growth threshold. Attack
authorization still uses only enemy body counts visible on the current turn.
Both focused runs completed all 44 matches with zero runner errors; all 22
repeated fixtures agreed.

| Shared pool (11 maps) | W–D–L | Points | Matches |
| --- | ---: | ---: | ---: |
| v09 confidence-aware teammate lengths | 24–0–20 | 72 | 44 |
| v10 confidence-aware enemy sizes | 23–0–21 | 69 | 44 |
| v08 pearl routing + wide sonar | 19–0–25 | 57 | 44 |

V10 split its direct fixtures 11–11 with v08 and beat v09 12–10. V09 made up
that two-game deficit by beating v08 14–8, so it led the full pool by one win
and three points. The enemy-confidence change is **not a demonstrated overall
improvement**. V10 did improve on `schooltime` (2–2 versus v09's 0–4), but lost
three of four `big_empty` games.

Artifacts:

- [V10 focused results](../build/hunter-v10-post-cpu-small/results.json)
- [V09 focused results on the same pool](../build/hunter-v09-post-cpu-small/results.json)
- [Paired comparison](../build/hunter-v10-post-cpu-comparison.json)

## V09: large-map CPU fix

After submission, a sandbox run on `big_empty` reproduced round-0 CPU-limit
failures for all v09 dragons; the engine reported “died: no valid action.” The
earlier small tournaments used the normal runner and did not exercise judge
limits, so their match-error-free status did not detect this failure.

V09 now stores only observed edges and visit counts, computes neighbors on
demand, and adds portal endpoints as edges are observed. This removes dense
whole-map setup and repeated full-map scans. A 500-round v09-versus-v09 sandbox
run on `big_empty` kept all 64 dragons active per team and completed nearly
30,000 dragon-turns per side without CPU-limit or “no valid action” failures.
The submission ZIP contains the fixed `bot.toml` and `main.py` at its root.
All-map sandbox checks remain.

The same sparse-map optimization is present in v10's working copy. A separate
500-round v10-versus-v10 sandbox run on `big_empty` also kept 64 dragons active
per team and completed almost 30,000 dragon-turns per side without CPU-limit
or invalid-action failures. Both current candidates pass this large-map stress
case; all-map sandbox checks remain before submission.

## V11: route-aware exploration spacing

V11 branches from v09 and uses actual visible route distance to measure
teammate spacing during exploration when a known path reaches the candidate
tile. It retains wrapped Manhattan distance when the current local map does
not reveal a route. A regression test verifies a known wall detour changes
the spacing estimate from 1 to 3. Both focused runs completed all 44 games
with zero runner errors and no repeated-fixture disagreements.

| Shared pool (11 maps) | W–D–L | Points | Matches |
| --- | ---: | ---: | ---: |
| v11 route-aware exploration | 26–0–18 | 78 | 44 |
| v09 confidence-aware teammate lengths | 21–0–23 | 63 | 44 |
| v10 confidence-aware enemy sizes | 19–0–25 | 57 | 44 |

V11 beat v09 12–10 and v10 14–8 head-to-head. It went 4–0 on `arena` and
`help`, but 0–4 on `small`; on `schooltime`, it scored 2–2, between v09's 1–3
and v10's 3–1. **Promote v11 as the current small-sample candidate**, while
keeping the small-map regression open.

Artifacts:

- [V11 focused results](../build/hunter-v11-small/results.json)
- [V10 focused results on the same pool](../build/hunter-v10-v11-small/results.json)
- [Paired comparison](../build/hunter-v11-comparison.json)

V11 also completed a 500-round mirror match on `big_empty` under the judge
sandbox without CPU-limit or invalid-action failures; each side completed
nearly 30,000 dragon-turns. All-map sandbox validation remains.

## V12: static-map exploration spacing

V12 branches from v11 and ignores transient dragon bodies when measuring
exploration spacing, while retaining the body-aware route check for pearl
ownership. The two focused runs completed 88 games with zero runner errors,
zero repeated-fixture disagreements, and a valid shared-pool summary.

| Shared pool (11 maps) | W–D–L | Points | Matches |
| --- | ---: | ---: | ---: |
| v11 route-aware exploration | 24–0–20 | 72 | 44 |
| v12 static-map spacing | 24–0–20 | 72 | 44 |
| v10 confidence-aware enemy sizes | 18–0–26 | 54 | 44 |

V12 tied V11's direct matchup 11–11 and did not demonstrate an aggregate
improvement. It improved `default_small` to 3–1 from V11's 1–3, but both scored
1–3 on `small`; V12 also fell behind V11 on `arena` (1–3 versus 4–0), `help`
(1–3 versus 3–1), and `schooltime` (1–3 versus 3–1). Keep V11 as the measured
candidate. [V12 focused results](../build/hunter-v12-small/results.json),
[paired V11 focus](../build/hunter-v11-v12-small/results.json), and
[validated comparison](../build/hunter-v12-comparison.json).

## V13: hybrid route spacing

V13 uses body-aware teammate routes when they are currently available, falls
back to static terrain routes when temporary bodies block those paths, and uses
wrapped Manhattan distance when local map knowledge cannot connect the pair.
Regression tests cover live-route preference and static-route fallback. In the
paired 11-map pool against V11 and V12, V13 scored 24W/20L, V12 22W/22L, and
V11 20W/24L. A later pool replacing V11 with V14 scored V13 25W/19L, V12
21W/23L, and V14 20W/24L. Both comparisons had zero runner errors and no
repeated-fixture disagreements.
V13 won `arena` 3–1 and `default` 4–0, but went 1–3 on `default_small`; it split
`small` and `schooltime` 2–2. The summary labels this an improvement on the
small sample. Keep the `default_small` regression open. V13 is not submission
safe: its 500-round `big_empty` judge-sandbox mirror test recorded 77 CPU-limit
events and 77 no-valid-action deaths beginning at round 414. Its peak per-turn
cost reached the 100M judge limit.

Artifacts: [V13 focused results](../build/hunter-v13-small/results.json),
[V12 focused results](../build/hunter-v12-v13-small/results.json), and
[validated comparison](../build/hunter-v13-comparison.json).

## Rejected V14 experiment (source removed)

This section describes the rejected **Python** V14 experiment. A distinct C++
V14 port was later created; see the following section.

V14 preserves V13's live-route, static-route, Manhattan fallback order, but
computes nearest teammate distances with two multi-source BFS traversals
rather than two traversals per teammate. It completed a 500-round `big_empty`
judge-sandbox mirror with 64 dragons alive per team, about 29,700 turns per
side, and no CPU-limit or invalid-action failures. Peak turn cost was 75.6M.

The paired 11-map normal-runner pool completed 88 games with zero runner errors
and no repeated-fixture disagreements:

| Shared pool (11 maps) | W–D–L | Points | Matches |
| --- | ---: | ---: | ---: |
| v13 hybrid route spacing | 25–0–19 | 75 | 44 |
| v12 static-map spacing | 21–0–23 | 63 | 44 |
| v14 multi-source hybrid spacing | 20–0–24 | 60 | 44 |

V14 fixed V13's sandbox CPU problem but scored worse than V13 in their paired
pool. Its source directory and behavior test were removed; tournament and
sandbox artifacts remain only as historical evidence. It went 1–3 on
`default_small`, `help`, and `small`. Retain V11 as the submission-safe
baseline. Artifacts: [V14 focused results](../build/hunter-v14-small/results.json),
[V13 focused results](../build/hunter-v13-v14-small/results.json), and
[historical comparison](../build/hunter-v14-comparison.json).

## C++ V14: behavior-matched V13 port

`hunter-v14-cpp-hybrid-route-spacing` ports V13's Python strategy to C++. The
implementation keeps the same reachable-attack checks, timestamped teammate
size evidence, pearl ownership, and live/static/Manhattan route-spacing
fallbacks. Six action-level parity tests match both action and SONAR output
against Python V13 over fixed fixtures and a deterministic sequence of
observations. The C++ source also passes the inherited size-aware behavior
tests.

Two focused runs used the same 11 maps and the same three-bot pool (V11, V13,
and C++ V14), reversing the focus between runs. All 88 games completed with no
runner errors, and the repeated fixtures agreed. The combined standings were:

| Shared pool (11 maps) | W–D–L | Points | Matches |
| --- | ---: | ---: | ---: |
| V13 Python hybrid route spacing | 23–0–21 | 69 | 44 |
| V14 C++ hybrid route spacing | 22–0–22 | 66 | 44 |
| V11 Python route-distance exploration | 21–0–23 | 63 | 44 |

V14 C++ lost all four `big_empty` games while V13 won three of four. C++ V14
went 3–1 on `default` and `help`, split four games on each other map, and had
no invalid actions. A 500-round `big_empty` judge-sandbox mirror then completed
with 64 dragons alive per team, about 29,800 turns per side, no invalid actions
or CPU-limit failures, and a 10.4M peak CPU cost. The aggregate result does not
demonstrate a tactical improvement; the large-map loss remains a specific
weakness to diagnose. This is a C++ implementation and does not change the
Python submission-safe status.

Artifacts: [C++ V14 focused results](../build/hunter-v14-cpp-small/results.json),
[V13 focused results](../build/hunter-v13-cpp-small/results.json),
[validated comparison](../build/hunter-v14-cpp-comparison.json).

## Large-map runtime and C++ comparison

The user reports intermittent V09 timeouts on large maps. Two fresh 500-round
judge-sandbox runs on the largest bundled map (`big_empty`, 64×64) passed
without CPU-limit or invalid-action failures. V09-vs-V09 completed about 29,800
turns per team, peaking at 65.3M CPU points in 5m56s. V09-vs-C++ completed about
29,800 Python turns and 29,600 C++ turns; the Python peak was 64.1M and the C++
peak 17.2M, with a 2m16s total match. These runs do not reproduce or rule out an
intermittent timeout on other submitted maps.

The existing C++ `fry-v14-stateful-size-aware-3` mirror completed 500 rounds in
1m14s, with about 29,500 turns per team and a 17.1M peak. The C++ code plays a
different strategy, so this is not a tactical comparison. The repeated runtime
gap does make a C++ port of the current safe Hunter worthwhile to evaluate for
submission headroom. Preserve behavior with action-level parity tests and a
paired tournament before switching; the old C++ bot is not a drop-in replacement.

## Validation and limits

- 34 Python behavior tests cover protocol streaming, attack safety, pearls,
  portal collection and return, sonar priority, ID aliasing, freshness, and
  out-of-order messages.
- Four summary tests cover bot-failure exclusion, errors, incomplete schedules,
  changed sources, and contradictory repeated fixtures.
- The existing 10 tournament-runner tests pass.
- A temporary differential check restored v04's attack policy in the Python
  port and compared 120 deterministic three-turn scenarios: all 360 turns
  matched the C++ reference output. Portal behavior is also tested separately.
- CMake/CTest were unavailable on PATH; Python tests ran directly. They are
  registered in CMake for environments with those tools.
- The recorded strategy tournaments used the normal local runner, not judge
  sandbox measurements. Medium/full tournaments and full all-map sandbox
  validation remain before submission. Small samples do not establish broad
  superiority.

The [strategy backlog](strategy-backlog.md) records remaining problems, including
uncertain global enemy counts, heavy body-collision losses,
portal-versus-pearl reward selection, and segregated maps.

- The v07 sonar-only strategy regressed against v06. Combining its message fix
  with v06 in v08 recovered the tactical score, tying v06 while retaining the
  wider teammate IDs.
