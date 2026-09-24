# Four-lineage review — 24 September 2026

Ouroboros is the strongest tested line. Its advantage is consistent across the common native opponent pools; the completed sandbox results are recorded below. Hydra has the strongest cheap swarm implementation, Kraken has rich memory but costly reproduction mistakes, and Leviathan has a compact evaluator whose team strategy is underdeveloped. These are claims about frozen versions and the maps below, not a universal ranking of authors or approaches.

No bot or other lineage's tooling was edited. The new review scripts live in `tools/leviathan`; all builds used copies. Snapshot hashes, raw logs, replays, per-game analysis and the aggregate summary are retained in [the review output](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/summary.json).

**Comparison design and results**

The latest-version round robin uses Leviathan v07-local-cache, Ouroboros v05-spread, Kraken v04-eval and Hydra v10-farmclean. Hydra's own strategy backlog retained v06-echo as its flagship, so an additional 30 games compare v06 with the other three. Combining those with the 30 games among the other lines gives a second complete, fair round robin. Do not add both Hydra versions to the standings and then compare unequal opponent pools.

Five maps: `arena`, `default_small`, `default`, `queen_of_spades`, `big_empty`. Every pair plays both team assignments on every map: 60 matches per round robin, 30 per bot. Both tables share 30 matches; there are 90 unique native matches, not 120. Runner: `unswbc 1.0.0`. No match errors, replay-analysis errors, invalid-action deaths or reported timeouts occurred in the native runs.

| Line and version | Native with Hydra v06 | Native with Hydra v10 |
|---|---:|---:|
| Ouroboros v05 | **26–4** | **24–6** |
| Hydra v06 / v10 | 14–16 | 17–13 |
| Leviathan v07 | 10–20 | 9–21 |
| Kraken v04 | 10–20 | 10–20 |

Entries are wins–losses; there were no draws. In the v06 field, Ouroboros goes 9–1 against Leviathan, 9–1 against Hydra and 8–2 against Kraken. Leviathan beats Kraken 6–4, but loses 3–7 to Hydra. Hydra v10 improves to 8–2 against Leviathan and 3–7 against Ouroboros while staying 6–4 against Kraken. Across its 30 matched cases, v10 gains five wins and loses two previously won cases: it regresses against Kraken as B on `big_empty` and as A on `queen_of_spades`. The net improvement is not uniform.

| Map | Ouroboros v05 wins / 6 | Hydra v06 | Leviathan v07 | Kraken v04 |
|---|---:|---:|---:|---:|
| arena | 5 | 4 | 0 | 3 |
| default_small | 6 | 4 | 2 | 0 |
| default | 4 | 1 | 4 | 3 |
| queen_of_spades | 5 | 2 | 2 | 3 |
| big_empty | 6 | 3 | 2 | 1 |

The judge sandbox screen uses the same frozen v06-field sources on `arena`, `queen_of_spades` and `big_empty`, both sides: **36 matches, 18 per bot**. All 36 winners match their corresponding native cases. Across all **126 new matches**, there were no match errors, replay-analysis errors, invalid-action deaths or reported timeouts. The death counts also match the runner logs.

| Line | Sandbox wins–losses | Highest observed turn cost / 100M budget |
|---|---:|---:|
| Ouroboros v05 | **16–2** | 80.6M |
| Hydra v06 | 9–9 | 24.6M |
| Kraken v04 | 7–11 | 68.2M |
| Leviathan v07 | 4–14 | 90.8M |

Costs are estimates from the runner's summaries, rounded to 0.1M; this runner leaves instruction fields absent in the saved replays. Missing replay values are not zero CPU usage. These observed maxima do not prove budget safety on every reachable state. Leviathan has the least measured headroom; Hydra has substantial room for more careful tactical evaluation. Hydra v10 was tested natively only in this review.


These are deterministic map/side cases, not independent random samples. No statistical significance or population win probability is claimed. The five-map set is a diagnostic screen, not an untouched holdout, and omits known difficult maps such as `trauma`. Native and sandbox modes must be assessed separately; matching sources do not establish matching trajectories.

**Concurrent source change:** while these tests ran, the live Ouroboros v05 file changed `w_tunnel_unknown` from 1 to 0 and `w_doomed` from 8 to 0, and gained a README. Every match in this review uses the earlier frozen file (SHA-256 `6aeacc3d176da4a79577e64f79203fab6b57bed0e6088ba5bb33297e0c8cdab5`). The results do not measure those later changes. Source links below point to tested copies; the other tested source folders still matched their snapshots at the final audit.

**What the code actually implements**

| Line | Core loop and useful strengths | Main code criticism | Main strategic criticism |
|---|---|---|---|
| Leviathan | About 330 lines of Python plus weights; bounded move/sprint/split/trade evaluation; current observations protect sprint affordability; local cache invalidation | Teammate reports are parsed and stored but never consumed by decisions. Enemy reach ignores enemy length; congestion assumes stationary bodies. | Roles mostly change weights. There is no pearl allocation or protected champion, and local trade/material scores do not price future team production well. |
| Ouroboros | About 1,695 lines of Python; common action values, role weights, pearl ownership, tunnel/doom checks, newborn exit checks, sonar handoff, crown growth | Large global-state program with hand-tuned probabilities and some coefficients outside the parameter table. Stale pearls are treated as certain during simulation; crown promotion has no demotion. | Most complete team strategy, but partial sonar views can permanently promote multiple short crowns. It can still be overwhelmed during the opening. |
| Kraken | About 1,283 lines of Python; persistent terrain, pearl-bed predictions, ally/enemy memory, cached graph search, configurable weights | Split risk argument is unused. Sonar reconstruction starts at the pre-move head. v04's executable policy is identical to v03: the override is empty. | Split → strike → move priority prevents a common economic comparison. Reproduction ignores newborn escape and fixed birth roles do not adapt well to later length/state. |
| Hydra | About 811 lines of C++; quick reproduction, pearl separation, enemy gossip and late growth; low sandbox cost | Six-bit dragon IDs alias after sufficient lifetime births. Many branch-specific constants and a fixed action hierarchy make interactions hard to tune. | Strong attrition engine; attacks and reproduction can divert food from winning length. A long attack path may be truncated to a costly sprint that does not reach its target. |

Line counts describe the main source file only, not complexity-adjusted productivity. A unified evaluator does not by itself make good strategy: Leviathan and Ouroboros both have one and perform very differently. Conversely, Hydra's priority policy remains competitive.

**Reproduced findings, with limits on the claims**

The [probe results](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/probes/findings.json) contain assertions run against imported modules or a copied C++ encoder. They establish behavior, not the tournament benefit of fixing it.

- **Leviathan L1/L2:** injecting 20 fresh ally reports leaves the selected action unchanged. A safe length-four lone gatherer still selects `SPLIT 2` at round 450. The endgame penalty is soft; this is a design weakness to test rather than an illegal action. Relevant code: [report storage](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/sources/bots/leviathan-v07-local-cache/main.py:155), [split evaluation](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/sources/bots/leviathan-v07-local-cache/main.py:272).
- **Kraken K1/K4:** `want_split(0)` and `want_split(2)` both return 2 in the same eligible state. The caller commits that split before considering escape. After moving east from cell 60 to 61, the saved sonar origin remains 60. The supplied rules explicitly cast sonar after the action; body refraction also means a single outgoing direction does not uniquely describe the final ray. Relevant code: [split policy](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/sources/bots/kraken-v04-eval/main.py:1007), [sonar reconstruction](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/sources/bots/kraken-v04-eval/main.py:1043).
- **Hydra H1 / Kraken K3:** actual self-report encoders give identical identity fields to IDs 1/65 and 1/257 respectively. A cap of 64 simultaneous dragons does not cap lifetime IDs. Replays contain simultaneously live same-team aliases: up to 26 excess IDs under Hydra's six-bit encoding, and six under Kraken's eight-bit encoding. This establishes real exposure, not proof that both conflicting reports reached one receiver. [Hydra encoder](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/sources/bots/hydra-v06-echo/hunter.cpp:93).
- **Ouroboros O1:** a two-step simulation starting at length three counts an old pearl as present and predicts length three; if that pearl is gone the result is length two. The candidate generator separately caps sprint length, so this probe does **not** establish an unaffordable sprint. It establishes optimistic material/body prediction.
- **Ouroboros O3:** a length-four dragon promotes itself at round 200 when no crown is heard, then remains crown after hearing about a length-40 crown. Crown roles refuse normal splitting. Over-promotion is a plausible growth/production coordination problem, not a measured explanation for its four native losses. [Promotion logic](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/sources/bots/ouroboros-v05-spread/main.py:1550).
- **Portal edge case K2/O2:** both Python lines truncate gossiped portal IDs to eight bits. Synthetic IDs 1 and 257 corrupt the learned pairing/identity; Ouroboros also ignores a later direct correction because the edge is already marked portal. No bundled root map currently uses IDs above 255. This is a latent defect, **not an explanation of losses in this comparison**. [Ouroboros direct learning](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/sources/bots/ouroboros-v05-spread/main.py:604).

**Replay evidence**

All 90 native replays were decoded, including births, movement updates, death causes, population and official final lengths. Events were reconciled with final population and runner outcome/round count. The following totals use only the fair 60-game field with Hydra v06; each bot participates in 30 games.

| Metric | Ouroboros | Hydra v06 | Leviathan | Kraken |
|---|---:|---:|---:|---:|
| Births before round 100 | 858 | 911 | 540 | 983 |
| Total births | 2,338 | 2,909 | 2,053 | 3,511 |
| Newborn deaths within 10 rounds | 353 (15.1%) | 431 (14.8%) | 381 (18.6%) | 982 (28.0%) |
| Births from round 380 onward | 0 | 472 | 377 | 57 |
| Wall + self + body deaths | 453 | 678 | 532 | 2,029 |
| Those deaths per 1,000 dragon turns | 2.02 | 2.65 | 2.52 | 7.71 |
| Friendly head collisions | 26 | 64 | 98 | 59 |
| Successful extra movement steps | 1,254 | 2,648 | 3,557 | 2,194 |

Births/deaths are aggregate workloads, not normalized experimental treatment effects. Long games offer more opportunities; newborn death rates include deaths to enemies and are right-censored by game end. Extra movement steps count successful movement beyond the first update in each action; they omit attempted fatal steps and are not a full material ledger. Friendly collision count counts the victim once, not both deaths. Late reproduction can be useful replenishment; these counts justify targeted ablations rather than proving every late birth is wrong.

Four particularly useful examinations:

1. **Leviathan's opening deficit:** [arena, Hydra v06 A versus Leviathan B](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/001-arena-hydra-v06-echo-vs-leviathan-v07-local-cache.analysis.json). Leviathan is eliminated after 46 rounds. Hydra collects 142 pearls and splits 52 times; Leviathan collects 57 and splits 14 times. Leviathan peaks at seven dragons against Hydra's 26. It initiates ten head collisions against Hydra's seven, yet cannot replace the losses. Local exchange value is inadequate when the opponent's production rate is much higher.
2. **Kraken wastes its reproduction:** [default_small, Kraken A versus Leviathan B](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/native/040-default_small-kraken-v04-eval-vs-leviathan-v07-local-cache.analysis.json). Kraken collects 400 pearls and splits 134 times, versus 251 pearls and 75 splits. Nevertheless it is eliminated after 468 rounds, with 83 body deaths and 27 wall deaths. Leviathan finishes with 14 dragons. This supports prioritizing survival and birth placement over raising Kraken's population target. Wall/body labels alone do not prove an edge-parser bug; trapped fallback moves can intentionally die.
3. **Hydra wins the wrong resource race:** [big_empty, Hydra v06 A versus Ouroboros B](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/008-big_empty-hydra-v06-echo-vs-ouroboros-v05-spread.analysis.json). At round 500 Hydra has 64 dragons, 457 total length and a longest dragon of 29. Ouroboros has only 18 dragons and 300 total length, but wins with length 42. Hydra collects more pearls (2,414 versus 1,951), splits more (351 versus 282), and makes more successful extra movement steps (483 versus 201). Population and total material are insufficient objectives when longest length is the first round-limit tiebreak.
4. **Ouroboros still has an opening failure:** [arena, Hydra v06 A versus Ouroboros B](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/flagship/002-arena-hydra-v06-echo-vs-ouroboros-v05-spread.analysis.json). Hydra eliminates it after 47 rounds: 50 splits and 138 pearls against 14 splits and 55 pearls. Ouroboros wins the reversed-side game and nine of ten overall against Hydra v06. The loss demonstrates sensitivity to the opening/map assignment; it does not negate the broader advantage.

A methodological correction: equal head-to-head death totals do not imply equal aggression. In [Kraken A versus Ouroboros B on big_empty](/Users/alik/Documents/Projects/UNSW-Battlecode-2026/build/lineage-review-20260924/native/017-big_empty-kraken-v04-eval-vs-ouroboros-v05-spread.analysis.json), both lose 143 dragons to heads, but Kraken initiates 106 collisions and Ouroboros 37. Death symmetry follows the collision mechanic; who initiated it is a separate observation.

**Earlier claims and test health**

- Kraken's saved 520-match sandbox pool does contain **325 wins, 3 draws, 192 losses**. That is useful evidence against the older Fry/Hunter/Kraken pool; it does not predict performance against current Ouroboros. v04 merely adds an empty parameter override to v03, so the version bump is not evidence of improvement.
- Hydra's earlier five-bot field contains **51–6–47** for v06 and **48–6–50** for v10 (wins–draws–losses), confirming why v06 was retained. The new cross-lineage field favors v10 by three wins. Pool dependence is real; neither experiment establishes a universal winner between them.
- Ouroboros v01's README claims **158–38** over 196 matches. I did not locate that result set in the local `build/ouro` directory; the retained `baseline-rr` metadata describes a different run without Ouroboros among its candidates. Treat the README figure as unverified here. The new v05 results stand independently.
- Leviathan's earlier 8–0 against Fry on its four-map native check is narrow evidence. The current 9–21/10–20 results show why promotion should use a common strong field.
- Existing Leviathan tests: **16 passed**. Shared tournament suite: **7 passed, 3 errored**, all because the test's mocked `result()` lacks the runner's `sandbox` keyword argument. These are test-harness compatibility errors, not observed match failures. Shared files were left unchanged. Logs and probe outputs are retained under `build/lineage-review-20260924/probes`.

**Next experiments, in priority order**

1. **Kraken:** make splitting compete with survival, reject births without an exit, and correct the sonar origin. Test each independently; measure newborn survival and noncombat deaths, not only total births.
2. **Leviathan:** use fresh teammate reports for soft pearl allocation; add a revisable champion election and value a dragon's lost future production in head trades. Test opening production and late growth separately. Maintain the small evaluator rather than adding another coarse mode.
3. **Hydra:** repair identity encoding; compare full attack cost against growth value before accepting a truncated pursuit. Test champion feeding on large maps while retaining the strong opening swarm.
4. **Ouroboros:** distinguish confirmed and remembered pearls; let crowns demote or renew a time-limited claim with a stable tie-break. Preserve newborn safety and pearl ownership. Fix wide portal IDs as a separate protocol regression test.
5. For every change: freeze sources, run focused reproducers, run paired map/side screens, inspect counterexamples, then validate finalists under the judge sandbox and on additional held-out maps. Keep rejected versions. Do not tune solely against the current leader or count repeated identical games as independent samples.

**Reproduction**

From the repository root, `tools/leviathan/lineage_review.py` creates a new output directory and snapshots sources before running. Example:

```sh
PYTHONPYCACHEPREFIX=/tmp/leviathan-review-pycache python3 tools/leviathan/lineage_review.py --output build/lineage-review-new --bots leviathan-v07-local-cache ouroboros-v05-spread kraken-v04-eval hydra-v06-echo --jobs 2
```

Add `--sandbox` for judge execution, `--maps arena,queen_of_spades,big_empty` for the sandbox screen, and `--sources /absolute/path/to/frozen/sources` to reuse an exact snapshot. Outputs must be new directories. `review_probes.py` reproduces the source findings; `review_metrics.py RUN_DIRECTORY` extracts event metrics; `summarize_review.py` rebuilds this review's summary and checks shared hashes. The latter two review scripts intentionally target this dated review's artifact layout.
