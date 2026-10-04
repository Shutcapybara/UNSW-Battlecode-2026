# Rome status — P2 tester

**Lineage:** Rome · **branch:** `r/rome` · **worktree:** `../wt-rome` · **host:** MacBook Pro (18 cores).
Bot snapshots live under `bots/rome-<nn>-<slug>/`; tools under `tools/rome/`.

## Setup

- `rome-00-hb1-base` is an exact copy of `bots/hb1-14-prior-r540`.
- `rome-01-nodevil` is the measurement base: same prior with D-033's three `W==32 && H==16` terms gated off through `Params::shape_terms=false`.
- `tools/rome/lane.py` copies the Verso D-032 runner; only the output paths and descriptive name point to Rome. `queen_metrics.py` measures queen survival, mean/median length and longest-dragon share from panel replays, and audits sprint charges and tiebreak messages.
- Golden check of the exact copy: recorded from `hb1-14-prior-r540` and replayed to `rome-00-hb1-base` on Schooltime, seed 1 vs Yuna: **0 divergent / 21,479 turns**. Runtime available here was `unswbc 1.2.2`.
- D-033 ablation parity on the same Schooltime transcript: `rome-01-nodevil` **0 divergent / 21,479 turns** (terms are inactive on this map).

## Measurements

- The repository venv was upgraded from `unswbc 1.2.2` to **1.2.3** at the user's direction (via `uv pip`, because the venv had no pip module). The isolated `/tmp/rome-venv` attempt had failed; it is not used.
- Required base scorecard completed from `rome-01-nodevil` with `--panel both --seed 1,2,3 --jobs 16`. Pool and gen fixtures are complete (**480/480**, **1,392/1,392**); scorecard and queen reports are written. The Mac host rejected `nice -n 10` (`setpriority: Operation not permitted`); panels used 16 workers on 18 cores, leaving two cores unused.
- Baseline absolute scorecard (new 1.2.3 zero; no parent comparison): pool W-L-D **401-78-1**, expected-score share **83.65%**, normalized pearl checkpoints mean **1.1398** (r50/r100/r150/r250: **1.091/1.136/1.157/1.175**), dragons@100 **1.316**, length@100 **1.200**, births@100 **1.119**. Tier-2 deaths per 1k dragon-turns: wall **5.663**, own body **3.765**, ally body **1.551**, ally head-on **0.628**, invalid **0**. Gen W-L-D **1,041-351-0**, expected-score share **74.78%**; normalized field references unavailable, raw per-map medians: pearls r50/r100/r150/r250 **35/114/176/235**, dragons@100 **27**, length@100 **65**, births@100 **46**. Gen tier-2 rates per 1k: wall **0.047**, own body **0.423**, ally body **0.459**, ally head-on **0**, invalid **0**. Post-rule field targets/references are not yet published; these are absolute base values, not a gate verdict.
- Queen audit: pool (480 games) survival at r490 **0.42% (2/480)**; mean length dead-as-zero **0.063**, median **0**; longest at r490 **0.42% overall (2/480), 100% when alive (2/2)**; longest over recorded r0–490 rounds **11.17% (18,728 / 167,682 team-round checks)**. Gen (1,392 games) survival **0.43% (6/1,392)**; mean length dead-as-zero **0.096**, median **0**; longest at r490 **0.43% overall (6/1,392), 100% when alive (6/6)**; longest over recorded r0–490 rounds **17.14%**. D-040 checks across both panels: all **72,334/72,334** measurable successful sprint charges matched `max(0, steps - ceil(start_length/4))`; 422/422 longest-dragon tiebreaks had tied queen lengths; all 38 queen-tiebreak winners matched queen lengths.
- D-040 replay preflight from finished r500 Trauma fixtures: the engine reported `longest dragon, 19 to 11`; both lowest-id queens were dead (length 0), so the queens tied before the longest-dragon tiebreak. One replay had a queen tiebreak with queen lengths 11–0 at r490; another used the longest-dragon tiebreak with queen lengths 0–0 at r490. In the second replay, 36 sprint actions included 33 measurable successes, all of which matched `max(0, steps - ceil(start_length / 4))`; 3 fatal actions were excluded because they do not expose the charge in resulting length.
- Do not use old-rule results as the new zero. The 1.2.3 base and queen panel aggregates above are complete.

## Queue

1. Complete: measured both 1.2.3 panels and recorded `rome-01-nodevil` as the post-rule zero.
2. Complete: queen, sprint-cost, and tiebreak audits cover pool and gen replays.
3. Complete: L10 `rome-02-far-contact` was re-scored from FRAME_VERSION 7 features. Verdict: hold; keep it unstacked. Full finding and corrected results are below.

4. Complete: `rome-03-queen-state-convert` tested the preregistered own-unit-count proxy for L39/L49 on clean parent `rome-01-nodevil`. Reject; queen survival/length did not improve, pool win fell significantly, gen RL conversion fell, and gen wall rate rose 15.9%. This does not directly falsify the unobservable opponent-count trigger. Full finding: `docs/findings/2026-10-04-rome-L39-queen-state-convert.md`.
5. Complete: Rome04, `rome-04-queen-head-tie`, changes strict-majority crown inheritance to majority-or-tie on length-4 equal splits. D-032 reject; no stack. Himeji source audit shows treatment starts only at r250 and crowns a new child, so preregistered r150 survival is pre-treatment and the arm does not test original-queen head retention. Active-crown exposure could not be measured from saved frames. Finding: `docs/findings/2026-10-04-rome-H-H1-late-crown-tie.md`.

## Cycle table

| Version / arm | Mechanism | Pool | Gen | CPU | Verdict |
|---|---|---|---|---|---|
| rome-01-nodevil | Post-rule base baseline | 480 games; W-L-D 401-78-1; exp-score 83.65%; norm pearls 1.1398 | 1,392 games; W-L-D 1,041-351-0; exp-score 74.78% | 16/18 workers; host denied nice 10 | measured; new zero |
| rome-02-far-contact | L10: skip head-on paths >6 Manhattan cells from known beds | 480; FRAME7 W-L-D 399-80-1, win 83.23%, Δwin +0.63pp; literal econ Δ +0.0004 [cluster -0.0001,+0.0010] | 1,392; FRAME7 W-L-D 1,033-359-0, win 74.21%, Δwin -0.22pp; literal econ Δ +0.0087 [+0.0026,+0.0150] | 10.82M max / 0 errors | hold; economy estimand and units guard unresolved; see 2026-10-04 finding |
| rome-03-queen-state-convert | L39/L49: late own-count<=5 proxy pins crown/feeder to original queen | 480; exp-share 80.21% (−2.40pp), econ Δ 0.000 [0,0]; queen alive among reached RL target maps 2/168 (1.2%, unchanged) | 1,392; exp-share 73.64% (−0.79pp), econ Δ 0.000 [0,0]; queen alive among reached RL maps 5/124 (4.0%, parent 5/119); conversion −8.45pp | 10.83M max / 0 errors | reject; gen wall +15.9%; see 2026-10-04 L39 finding |
| rome-06-cage-e1 | H-SZ1 package C+D+E, reserve dose 1 | seed1 M2 229-43-0, score .842 (+1.1pp); r490 queen alive 11/147 reached | seed1 gen current 292-108-0, score .730 (+1.0pp); all-gen 353-111-0 | 10.14M max / 0 errors | hold at D-044 screen; invalid deaths +8.07/1k pool |
| rome-07-cage-e3 | H-SZ1 package C+D+E, reserve dose 3 | seed1 M2 224-48-0, score .824 (−0.7pp); r490 queen alive 14/150 reached | seed1 gen current 294-106-0, score .735 (+1.5pp); all-gen 355-109-0 | 10.37M max / 0 errors | hold at D-044 screen; invalid deaths +8.11/1k pool |


## Updated L10 re-read (4 Oct)

- Re-extracted candidate and parent with FRAME_VERSION 7 authoritative replay winners. Corrected parent W-L-D: pool 396-83-1, gen 1,036-356-0. Candidate: pool 399-80-1, gen 1,033-359-0. Full per-panel scorecard: `game_stats/runs/rome-02-far-contact-z1+gen-s1-2-3.md`.
- Cluster 90% literal mean economy Δ: pool +0.0004 [-0.0001,+0.0010], gen +0.0087 [+0.0026,+0.0150]; median-checkpoint form: pool 0.0000 [-0.0017,+0.0005], gen -0.0042 [-0.0124,+0.0079]. Hold pending analyst ruling on estimand and units/length guards; do not stack.
- Enemy H2H death proxy Δ per 1k dragon-turns: pool -0.029 [-0.066,+0.004]; gen -0.415 [-0.556,-0.269]. It is a per-turn proxy, not per-contact risk. Per-map deltas and clustered intervals are in the `rome-02-far-contact-permap` CSVs. Full result: `docs/findings/2026-10-04-rome-L10-far-contact.md`.


## Rome04 result — 2026-10-04

- Official FRAME7 paired panels, seeds 1–3: pool win Δ −1.35pp [95% cluster −3.125,+0.417], gen 0.00pp [−0.503,+0.503]; literal mean and median-checkpoint economy exactly 0.0000 [0,0] in both panels. D-032 current and proposed gates reject: strict-positive pool economy fails at zero; pool win 90% LB −2.81pp fails the −2pp guard. Tier-2 worst +1.9% pool own-body.
- All-map economy deltas are zero. Pool Portals win −11.46pp; Slithery −2.08pp. Gen `var+portals_tr` −4.17pp with +2.08pp on commons-spread and trauma. Per-map/cluster CSVs: `game_stats/runs/rome-04-permap.csv`, `.clusters.csv`. Opening metrics/percentiles unchanged.
- Himeji unit17: role-crown cannot activate before r250; receiver is a new child, original queen stays parent. r150 survival among reached fixtures 95/423 pool and 244/994 gen in both arms. This is pre-treatment parity, not falsification of H-H1. Replay features do not expose actual active-crown equal-split receiver events.


## Rome05 preregistration — H-H5, 2026-10-04

- Taking H-H5 (Himeji H15-02; L39/L49, weight 0.5) after Rome04: add a single fresh-queen-evidence condition to Rome03's `queen_conversion` predicate at all three consumers (crown election, split inheritance, feeder reach). Require crown ID 0/1 and existing TTL freshness; otherwise preserve normal crown fallback. This does not prove queen liveness, so report possible stale beacons and actual exposures without replay-omniscience.
- Expected: on the preselected Rome03-triggered Portals subset, recover some terminal longest/crown consolidation vs Rome03; all-game paired win nonnegative vs Rome03; opening economy/material unchanged; compare the full arm with clean Rome01. Reuse paired 480 pool / 1,392 gen fixtures, seeds 1–3, both seats; per-map deltas and 90% cluster intervals. CPU probe required.


## D-043/D-044 live-map reset — 2026-10-04

- Rome01–05 use the repository’s old maps and are **pre-swap historical**. Rome04 is a completed pre-swap arm; do not treat gen twins of Autarky, Default, Prisoners Dilemma, Schooltime, Slithery Fight, or Trophy as current transfer evidence until regenerated.
- Rome05 H-H5 draft: CPU 10.83M / 0 errors; pre-swap pool simulator 480/480 but not scored against parents; official gen 227/1,392 when D-043 arrived. The incompatible 744-fixture custom gen set was stopped. No score/gate/verdict; no replays committed. Finding `docs/findings/2026-10-04-rome-H-H5-pre-swap-partial.md`.
- Required post-M2 zero complete on parent `carthage-05-free-sprint`, `unswbc 1.2.3`: pool `LIVE_MAPS_M2` 816/816, gen 1,392/1,392. All outcomes are official and queen columns are in the finding. Four stale gen twins (192 games) are excluded from transfer evidence; Schooltime open4 and PD 10-dragon are also absent from the 17-template pool. No post-M2 reference values are published, so the zero is absolute only. Finding `docs/findings/2026-10-04-rome-carthage05-post-m2-zero.md`.
- Pool: 656–160–0, expected score 0.804; pearls medians r50/r100/r150/r250 28/92.5/164/286.5, units/total/births@100 23/56/38. Queen reached r490 444/816, reached+alive 2/816, mean r490 length 0.043, longest 0/816. Queen-decided losses 19/160 (11.9%), map-cluster bootstrap 95% CI 3.3–25.5%.
- Gen all: 1,038–353–1, expected score 0.746; excluding stale twins 861–338–1 / 1,200, expected score 0.718. Queen reached 217/1,392, reached+alive 4/1,392, mean length 0.040, longest 3/1,392. Queen-decided losses 4/353 (1.13%), map-cluster 95% CI 0.0–3.3%.
- D-044 governs all new hand-rule arms: ≥3 declared doses including zero, response curve and side effects, with RL translation. Kanazawa's H-KZ12 screen is on the board; reconcile it with the director's cage-fix-first arm order before selecting the next mechanism.

## H-SZ1 / D-044 screen — 2026-10-04

- Preregistered dose screen on clean parent `carthage-05-free-sprint`, `unswbc 1.2.3`, seed 1, both seats: dose 0 parent, dose 1 C+D+E1, dose 3 C+D+E3. The response curve estimates package effects vs parent; it does not isolate reserve E from C+D. M2 pool 272 fixtures per dose; gen 464, split into 400 current/unflagged and 64 stale pre-swap twin fixtures. All completed with official outcomes; no rc errors.
- Pool W-L-D: dose 0 226-46-0; dose 1 229-43-0 (+1.1pp expected score); dose 3 224-48-0 (-0.7pp). Current gen: 288-112-0 (0.720), 292-108-0 (0.730), 294-106-0 (0.735). Stale gen twins stayed 61-3 at every dose.
- Pool queen alive@490 among reached: 0/149 parent, 11/147 (7.5%) E1, 14/150 (9.3%) E3; Schooltime specifically: parent 0/16, E1 11/12 reached and 16/16 wins, E3 13/13 reached and 15/16 wins. Target-file all-map target ≥0.42 reached: doses remain below; seed-1 screen only.
- Invalid deaths per 1k dragon-turns rose 0→8.07 / 8.11 in pool and 0→2.44 / 2.44 gen. Wall rate fell, but this is a tier-2 concern and the D-042 gate was not applied to this dose screen. CPU maxima 10.14M E1 Schooltime, 10.28M E3 Schooltime, 10.37M E3 Slithery; below 30M.
- Finding `docs/findings/2026-10-04-rome-SZ1-cage-dose-screen.md`; paired per-map/hash and regime files under `game_stats/runs/`. HOLD at screen stage; do not stack. Any E-specific follow-up needs C+D/E0 and a cage/cap-conditional reserve before full seeds 1–3.
