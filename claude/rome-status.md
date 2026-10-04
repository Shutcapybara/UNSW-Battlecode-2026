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


## Updated L10 re-read (4 Oct)

- Re-extracted candidate and parent with FRAME_VERSION 7 authoritative replay winners. Corrected parent W-L-D: pool 396-83-1, gen 1,036-356-0. Candidate: pool 399-80-1, gen 1,033-359-0. Full per-panel scorecard: `game_stats/runs/rome-02-far-contact-z1+gen-s1-2-3.md`.
- Cluster 90% literal mean economy Δ: pool +0.0004 [-0.0001,+0.0010], gen +0.0087 [+0.0026,+0.0150]; median-checkpoint form: pool 0.0000 [-0.0017,+0.0005], gen -0.0042 [-0.0124,+0.0079]. Hold pending analyst ruling on estimand and units/length guards; do not stack.
- Enemy H2H death proxy Δ per 1k dragon-turns: pool -0.029 [-0.066,+0.004]; gen -0.415 [-0.556,-0.269]. It is a per-turn proxy, not per-contact risk. Per-map deltas and clustered intervals are in the `rome-02-far-contact-permap` CSVs. Full result: `docs/findings/2026-10-04-rome-L10-far-contact.md`.


## Rome04 result — 2026-10-04

- Official FRAME7 paired panels, seeds 1–3: pool win Δ −1.35pp [95% cluster −3.125,+0.417], gen 0.00pp [−0.503,+0.503]; literal mean and median-checkpoint economy exactly 0.0000 [0,0] in both panels. D-032 current and proposed gates reject: strict-positive pool economy fails at zero; pool win 90% LB −2.81pp fails the −2pp guard. Tier-2 worst +1.9% pool own-body.
- All-map economy deltas are zero. Pool Portals win −11.46pp; Slithery −2.08pp. Gen `var+portals_tr` −4.17pp with +2.08pp on commons-spread and trauma. Per-map/cluster CSVs: `game_stats/runs/rome-04-permap.csv`, `.clusters.csv`. Opening metrics/percentiles unchanged.
- Himeji unit17: role-crown cannot activate before r250; receiver is a new child, original queen stays parent. r150 survival among reached fixtures 95/423 pool and 244/994 gen in both arms. This is pre-treatment parity, not falsification of H-H1. Replay features do not expose actual active-crown equal-split receiver events.
