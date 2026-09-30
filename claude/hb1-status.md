# HB-1 status — Heartbreaker (team 62) anatomy

Prompt: `docs/hub/prompts/2026-09-30-HB1-heartbreaker-anatomy.md`. Branch `r/hb1`, worktree `../wt-hb1`
(desktop, `~/Documents/Projects/2026/`; the original `~/Projects` checkout was wiped at ~07:25 ACST 30 Sep and the
uncommitted Q0 scaffolding was rebuilt from the session transcript, then pushed step by step).

## Q0 — data + extractor (done, 30 Sep)

- `tools/hb1/sync_from_mac.sh` — the prompt's data recipe plus `public_replays/team-62/` (era-labelled replays).
  Re-run to pick up new games.
- `tools/team_recon_claude/features_v5.py` — v4 actor-local row, versioned; one parquet (+ `.traj.json`) per game.
- `tools/hb1/build_dataset.py --jobs 14` — `build/hb1/games.parquet` + `build/hb1/v5/{corpus,era}/`; incremental.

| set | games | span (UTC) | win rate | ranked | maps | opps |
|---|---|---|---|---|---|---|
| corpus | 817 | 27 Sep 20:18 – 29 Sep 21:48 | 0.590 | 384 | 10 | 46 |
| era (27 Sep packets, sub ids) | 180 | 21 Sep – 27 Sep 14:11 | 0.617 | 97 | 14 | 50 |

Extraction: 997/997 games, 0 errors, 7m46s on 14 jobs; ~10k actor-turn rows/game, 294 columns. Corpus and era
sets do not overlap. The corpus covers only 10 maps (era set 14), so map-cliff comparisons must use the era set.

## Q1 — five decisions (done; `tools/hb1/q1_decisions.py`, raw `game_stats/runs/hb1-q1-gaps.json`)

Holdout = 163 of 817 corpus games (by game, seed 62); map-identifying columns (W, H, x, y, facing_abs, map) excluded.
GBT = XGBoost on the GPU (63 leaves, lr 0.1, early stop) — CPU boosting starved under the R-lane panel load;
on gate/alloc it matches sklearn HistGBT to 0.05 pp. MLP = 256-128 ReLU, 12 epochs.

| decision | n test | majority | tree depth 4 | GBT | MLP | gap tree→MLP | largest drop-family Δacc |
|---|---:|---:|---:|---:|---:|---:|---|
| gate (split-eligible turns) | 128,379 | 0.903 | 0.952 | 0.975 | 0.970 | +0.018 | candidates −1.27 pp |
| direction (F/R/L) | 179,436 | 0.534 | 0.685 | 0.829 | 0.814 | **+0.129** | candidates −14.0 pp |
| sonar mask | 94,761 | 0.699 | 0.937 | 0.981 | 0.966 | +0.029 | action taken −9.6 pp |
| alloc (child size) | 34,445 | 0.753 | 0.918 | 0.957 | 0.943 | +0.025 | scalars (length) −0.99 pp |
| late gate (r≥350, len≥8) | 48,345 | 0.960 | 0.9993 | 0.9994 | 0.9988 | −0.001 | candidates −0.93 pp |

Reading: **direction is the learned part; the other four are rules.**
- Late gate = "split iff no exit of any kind (portals included)" (tree 99.93 %; "no ordinary exit" alone 99.54 %).
  Late splitting is only an escape reflex — no productive late splits, consistent with the concentration weakness.
- Gate depth-4 tree: no exit → split; in the open → split iff it just ate and length ≤ 4 (the 2+2 production
  split), plus an opening split at r0–1. The tree→GBT 2.3 pp is the fuzzy edge of that production rule.
- Alloc: `length−2` baseline 77.9 %, child-2 75.3 %; only length/units matter (other families < 0.5 pp).
- Sonar: keyed to the action just taken and own-body layout (grid −1.4 pp); received messages −0.05 pp
  (no receiver response, as on 27 Sep).
- Direction ablations: candidates −14.0, grid −2.0, local −1.2, memory −0.96, scalars −0.89, messages −0.86 pp.
  Messages matter 9× more for direction than for the gate: the echo counts inform steering.

Direction calibration (`tools/hb1/q1_calibration.py`, `game_stats/runs/hb1-q1-calibration.json`): the v5 GBT is
calibrated and slightly under-confident (ECE 0.022; acc 0.829 at mean max-p 0.808). 28 % of held-out moves have
max-p ≥ 0.95 at 99.2 % accuracy (rule-like); 12.8 % are near-ties (top-2 gap < 0.2) at 52 % accuracy and hold 36 % of
all direction errors. A copy that samples from these probabilities would agree 73 % move-for-move (argmax 83 %).
The residual is what a sampled policy or unseen state produces; the replays cannot tell which.

Memory beyond the current view (`tools/hb1/q1_history.py`, `game_stats/runs/hb1-q1-history.json`; user's suggestion):
action history (last 6 actions, turn / left-right EWMAs, since-turn, eats in 10) and a decayed spatial "trail"
(enemy/ally segment and head mass + centroid in the egocentric frame at decay 0.7/0.9, own-position trail, EWMAs of
the five echo counts, Δdensity×step gradient). Same rows as Q1 (verified), same held-out games, GPU GBT:

| decision | v5 | + history | + trail | + both | MLP + both |
|---|---:|---:|---:|---:|---:|
| direction | 0.8287 | 0.8302 | 0.8296 | 0.8306 | 0.8167 |
| gate | 0.9747 | 0.9746 | 0.9746 | 0.9745 | 0.9702 |

+0.19 pp at most. The top 24 features by GBT gain are all current-view candidate features (forward run, blocked
neighbours, reachable area, pearl distance, ally heads within 2); the first memory feature is the turn EWMA at #25.
Steering is a function of the current local view — consistent with a memoryless (feed-forward) policy, though these
summaries only show that no predictable memory signal of this form exists. The engine's echo is five aggregate counts
(no direction), so an echo EWMA is the most any bot could keep from sonar. Conventions verified on data before use.

## Q2 — wrapper vs policy (done; `tools/hb1/wrapper.py`, `q2_enumerate.py`, `q2_command.py`)

Enumeration over all 7.3 M corpus actor-turns (`game_stats/runs/hb1-q2-enumerate-corpus.json`):

| state | observed |
|---|---|
| ordinary exit free | never wall / own body; ally cell 12 times in 7.08 M; enemy-head attacks 9,575 (policy) |
| no ordinary exit, no portal, split-eligible | split 89,986 / 90,072 (99.9 %) |
| no ordinary exit, portal, not eligible | portal 20,387 / 20,413 |
| no ordinary exit, portal, eligible | portal 7,204 vs split 5,387 — the one mixed blocked state (policy) |
| no exit at all, not eligible | ally **head** if adjacent (F>R>L), else forward — deterministic in a 1/3 sample; every such move dies |
| split sizes / capacity | 0 invalid of 186,440 |

Command-level accuracy (10 classes: F/R/L, SPLIT 2..8; raw `game_stats/runs/hb1-q2-command.json`). Trained on the
654 corpus training games; tested on the 163 held-out corpus games and on the 180-game era set (≤27 Sep, older
submissions — the era the 27 Sep packet's 66.45 % was measured on).

| policy | corpus raw | corpus wrapped | era raw | era wrapped | raw invalid picks (corpus / era) |
|---|---:|---:|---:|---:|---|
| class prior | 0.522 | 0.641 | 0.497 | 0.612 | 18.1 % / 17.7 % |
| tree depth 4 | 0.670 | 0.675 | 0.650 | 0.654 | 1.8 % / 1.3 % |
| GBT | 0.826 | 0.826 | 0.799 | 0.799 | 0.9 % / 0.8 % |
| MLP | 0.806 | 0.807 | **0.655** | **0.703** | 1.0 % / 7.8 % |

Reading: the 66 % ceiling is broken by capacity and the v5 candidate features (GBT 82.6 % / 79.9 %), not by the
wrapper — in distribution both learners have absorbed the wrapper. The prompt's test holds where it matters: the
same MLP out of time (era) is at 65.5 % raw with 7.8 % invalid picks and 70.3 % wrapped. The wrapper is the part to
copy verbatim (it is exact and costs nothing); it protects a learned component when that component is off
distribution. Observed commands outside the wrapper: 0.0014 % (corpus), 0.0032 % (era). The wrapper forces 0.9 % of
rows at 98.9 % agreement.


## Q3 — is a training loop running? (done; `tools/hb1/q3_windows.py`, `game_stats/runs/hb1-q3-windows.json`)

Corpus split into 6-hour windows from 27 Sep 20:00 UTC (9 windows; windows 0–2 hold only 5–25 games). GPU GBT,
accuracy on each window: 'within' = by-game half split inside the window; 'from_era' = fitted on the ≤27 Sep era set;
forward = fitted on the previous window; backward = fitted on the next window.

| decision | windows 3–7 (105k–193k rows each): within | from era | forward | backward |
|---|---|---|---|---|
| direction | 0.807–0.812 | 0.805–0.813 | 0.812–0.820 | 0.803–0.820 |
| gate | 0.967–0.974 | 0.965–0.969 | 0.967–0.972 | 0.965–0.973 |
| alloc | 0.941–0.955 | 0.937–0.949 | 0.946–0.948 | 0.941–0.953 |

- No continued superset drift: backward is not systematically above forward (it is higher in 3 of 5 large windows for
  direction, by ≤ 0.7 pp, and lower in the other 2).
- The era model (older submissions, ≤27 Sep) predicts 28–29 Sep as well as a model fitted inside the window: the
  policy has not changed since at least 27 Sep 14:00 UTC.
- Hourly change-points (open-position split rate, forward-when-free rate; penalised mean-shift DP over 36 hours):
  **none**. Hourly open-split rate 0.036–0.093, forward-when-free 0.605–0.682, all within sampling noise.
- Ladder (194 snapshots, 28 Sep 14:57 – 29 Sep 22:02 UTC): Elo 1788–1874, rank 30–52, no trend (1813 → 1840).

Reading: no training loop is visible in this span — the policy is static, and its rating wanders with the schedule.
Every observable here would look the same for a frozen RL policy and a static hand-written bot, so the replays still
cannot say whether it is RL; per the prompt, no further spend on the question.

## Q4 — structured mimic `bots/hb1-01-structured` (in progress)

- Ares V06 copied verbatim; `Params::hb1_mode = true` switches `main.cpp` to the mimic, Ares untouched otherwise.
- `hb1_features.hpp`: C++ port of the v5 row. Parity vs the Python rows on 3 held-out games: 19,553 rows × 276
  columns, **0 mismatches** (`tools/hb1/cpp/{dump_blocks.py,feat_parity.cpp,check_parity.py}`).
- Direction scorer choice (`tools/hb1/q4_scorer_offline.py`): per-candidate linear 0.733, per-candidate MLP 0.776,
  GBT 100 rounds 0.813, full GBT **0.829** — cross-candidate interactions matter, so the GBT is exported.
- `hb1_models.hpp` (5.2 MB; `tools/hb1/q4_fit_export.py`): gate 120 rounds (held-out 0.974), alloc 40 (0.953),
  direction 300 (0.829), sonar 40 (0.980), fitted on the 654 training games without `mem_initial`. C++ evaluator
  (`hb1_gbt.hpp`) matches XGBoost margins on 2,000 held-out rows per model, 0 mismatches.
- `hb1_policy.hpp`: wrapper W0–W4 as rules; gate / child size / direction from the models; sonar = rays N,E,S,W,
  payload 0 (observed on all 475k sonar turns), the model's dropped slot redrawn from the other three (approximation
  of the observed neck-ray substitution).
- Smoke: native, Autarky, seed 1 — beats Ares V06 by elimination at r477 (40 vs 2 dragons at r451). One game.
- Sandbox (judge wasm, CPU priced): Portals, seed 2, vs Ares V06 — mimic p50 6.1M / p99 6.6M / max 6.9M points per
  turn (Ares V06 same game: p50 4.5M, max 8.4M; screen wall 60M), 4.6 MB memory per dragon process, 0 fallbacks in
  9,447 turns; splits 183 escape (W1) / 177 gate-admitted. Result: loses on length at r500 — Heartbreaker's own
  Portals / round-limit profile. Two smoke games only; fidelity and panels are the measurement.
- **Deployable and testable** as of 30 Sep ~11:00 ACST. Next: held-out decision agreement and closed-loop divergence
  (`tools/team_recon_claude/closed_loop.py`), then the z1 / generalisation panels and head-to-heads.

### Q4 fidelity — deployed binary, open-loop conditional replay (`tools/hb1/replay_drive_cpp.py`)

40 of the 163 held-out corpus games (never used for fitting), 356,944 Heartbreaker actor-turns; one fresh native
process per dragon fed the exact round blocks they received (`game_stats/runs/hb1-q4-fidelity-open.json`):

| component | agreement | offline model on the same held-out set |
|---|---:|---:|
| family (move vs split) | 0.993 | — |
| direction, both moved | 0.824 | 0.829 |
| child size, both split | 0.944 | 0.953 |
| whole command | **0.821** (per game 0.742–0.893, median 0.817) | 0.826 |
| sonar direction multiset | 0.681 | mask 0.980 (the dropped slot is redrawn at random) |
| no reply / crash | 0 | |

The live bot keeps ~99 % of the offline agreement; the residual is the open-loop memory drift (each process
remembers its own choices while the boards follow the replay).

### Q4 strength — head-to-head vs our deployed Ares V04 (`tools/hb1/h2h.py`, `game_stats/runs/hb1-h2h-mimic-vs-ares-v04.json`)

Heartbreaker played our live Ares V04 (submission v83, active from 29 Sep 06:47 UTC) 40 times in the corpus, 4 per
live map, and won 28 (0.70). The mimic vs `bots/ares-v04-tyr12-behavior-parity`, same ten maps, both seats × 2
seeds, native, fixed seeds:

| map | mimic | real Heartbreaker |
|---|---:|---:|
| Prisoners Dilemma | 4/4 | 4/4 |
| Autarky | 3/4 | 4/4 |
| Devil | 2/4 | 3/4 |
| Trauma | 2/4 | 4/4 |
| Default | 1/4 | 3/4 |
| Queen of Spades | 1/4 | 4/4 |
| Trophy | 1/4 | 4/4 |
| Portals | 0/4 (all on length, r500) | 1/4 |
| Schooltime | 0/4 | 1/4 |
| Slithery Fight | 0/4 (all on length, r500) | 0/4 |
| **total** | **14/40 (0.35)** | **28/40 (0.70)** |

Reading: the mimic reproduces Heartbreaker's map *shape* — the same weak maps, lost the same way (round-limit length),
and the Prisoners Dilemma sweep by early elimination — at half its strength. 82 % per-turn command agreement does not
carry 70 % of the win rate: the gap sits on the maps Heartbreaker sweeps (Queen of Spades, Trophy, Trauma, Default).
Caveat: the real games are live-server scrims (unranked, server seeds); the local V04 copy is the submitted source.
Next: find where the strength goes (trajectory comparison against their real games on the same maps).

### hb1-02-sampled — direction sampled instead of argmax (`game_stats/runs/hb1-h2h-sampled-vs-ares-v04.json`)

Same 40 fixtures vs Ares V04: **3/40 (0.075)** vs hb1-01's 14/40 (25 losses by elimination, 15 on length).
Rejected, and informative: (1) Heartbreaker's residual is not useful randomness — the direction model's uncertainty
is mostly model error, so copying it as noise hurts; (2) strength is steep in direction accuracy: ~0.83 agreement
(argmax) → 0.35 win rate, ~0.73 expected agreement (sampled) → 0.075. The lever is a more accurate direction model;
the v5 direction GBT was trained on a 1,200-row/game sample (~0.7 M of ~6 M move turns) and hit its 300-round cap.

### Direction-model scaling (`tools/hb1/q4_direction_scale.py`, `game_stats/runs/hb1-q4-direction-scale.json`)

Same held-out rows as hb1-01's 0.829 (179,436 move turns, 163 games); GPU XGBoost, early stop 30, ≤ 3,000 rounds:

| rows per training game | leaves | rounds | held-out direction accuracy |
|---:|---:|---:|---:|
| 1,200 (hb1-01 data) | 63 | 2,995 (cap) | 0.8432 |
| 1,200 | 255 | 1,069 | 0.8449 |
| 3,000 | 63 | 3,000 (cap) | 0.8495 |
| 3,000 | 255 | 2,345 | **0.8543** |
| 6,000 | — | — | not completed (process ended without output at the 3.2 M-row load; likely memory on the shared host) |

hb1-01's direction model (1,200 rows, 63 leaves, 300-round cap) was under-fitted: +2.5 pp is available from data and
capacity alone. The 0.854 model is 7,035 trees / 3.58 M nodes (86 MB) — far over the header budget — so
**hb1-03-direction-scaled** is a local-only experiment: the model is memory-mapped from
`build/hb1/export/direction_v03.bin` (blob parity vs XGBoost margins: 2,000 rows, 0 mismatches). It answers whether
direction accuracy buys the missing strength; a deployable version would need distillation.

### hb1-03-direction-scaled vs Ares V04 (`game_stats/runs/hb1-h2h-scaled-vs-ares-v04.json`)

Same 40 fixtures: **22/40 (0.55)** vs hb1-01 14/40 and real Heartbreaker 28/40. Paired on identical fixtures:
9 flipped L→W, 1 W→L, 13 W/W, 17 L/L — one-sided sign test p = 0.011.

| map | hb1-01 | hb1-03 | real Heartbreaker |
|---|---:|---:|---:|
| Autarky | 3/4 | 3/4 | 4/4 |
| Default | 1/4 | 2/4 | 3/4 |
| Devil | 2/4 | 4/4 | 3/4 |
| Prisoners Dilemma | 4/4 | 4/4 | 4/4 |
| Portals | 0/4 | 0/4 | 1/4 |
| Queen of Spades | 1/4 | 2/4 | 4/4 |
| Schooltime | 0/4 | 1/4 | 1/4 |
| Slithery Fight | 0/4 | 0/4 | 0/4 |
| Trauma | 2/4 | 3/4 | 4/4 |
| Trophy | 1/4 | 3/4 | 4/4 |

Dose–response between held-out direction agreement and win rate vs Ares V04: ~0.73 (sampled, hb1-02) → 0.075;
0.829 (hb1-01) → 0.35; 0.854 (hb1-03) → 0.55; real Heartbreaker → 0.70. Roughly +8 pp of win rate per point of
direction accuracy in this range, and every map that moved, moved toward Heartbreaker's own record. The mimic's
strength is limited by the direction model, and the direction model is still data/capacity-limited.

### hb1-04-deployable — hb1-03's behaviour inside the judge's limits

The judge runs each dragon as a wasm instance capped at 768 pages = **48 MiB** (`unswbc/sandbox.py`
`MAX_MEMORY_PAGES`), built by clang 20 in wasm (2 GiB build memory). hb1-03's model at 24 B/node is 86 MB, so it
cannot ship as-is. Truncation costs accuracy (30k held-out rows: 100 rounds 0.827, 400 0.842, 1,000 0.847,
1,900 0.849, all 2,345 0.850 — `build/hb1/export/direction_v03_curve.csv`), so instead the full model is re-encoded
as 8-byte preorder nodes (`tools/hb1/q4_compact_direction.py`): 3.58 M nodes = 28.6 MB of data, a 56 MB header.
Parity vs the blob on 30,000 held-out rows: **0 argmax differences, max |Δp| = 0** (bit-identical) — hb1-04 makes
hb1-03's decisions, so hb1-03's 22/40 carries over. Native g++ compile: 1 m 55 s, 1.3 GB peak.
Note: the 56 MB generated header is above GitHub's 50 MB recommendation (hard limit 100 MB) and is the kind of
large generated artifact `docs/artifact-policy.md` discourages; it is committed because a registered bot must be
self-contained. Alternative for the lead: generate it at build time from the exporter.
**Decision (user, 30 Sep):** keep it committed — regenerating needs `build/hb1/export/direction_v03.bin`
(gitignored, 86 MB), i.e. a retrain of the GPU GBT, which is not guaranteed to reproduce identical trees.
- **Sandbox (judge wasm, CPU priced), Portals seed 2 vs Ares V06:** builds under the judge's clang 20; **30.6 MB per
  dragon process** (cap 48 MiB); **p50 7.6M / p99 8.0M / max 8.4M points per turn** (Ares V06 same game p50 4.5M,
  max 8.4M; screen wall 60M); 0 fallbacks in 10,560 turns; loses on length at r500 (Heartbreaker's Portals profile).
  hb1-04 is deployable. Wall time 8 m 50 s including the build.

## Q5 — what transfers (in progress)

Three one-mechanism ports onto verbatim Ares V06 copies (each fed by a per-process v5 row where needed):
- `hb1-10-escape-split` — wrapper W1: no free ordinary F/R/L step and no portal, split legal → split length−2
  (Ares escape-splits only when every scored path is already dead and the child has an exit).
- `hb1-11-split-gate` — Heartbreaker's gate GBT (0.974) replaces Ares's production-split admission
  (`tyr_split_option` / opening production); child size, escape split and moves unchanged.
- `hb1-12-direction-prior` — λ·log p_HB(first step) added to Ares's OK/DIVE path scores, λ = 1.0 fixed before
  screening (Ares move terms are O(1): goal 1.2, momentum 0.6, crowd 0.6; trap 30).
Smoke (Trophy vs V06, native): all three play full games, 0 `ares_fallback`.

Measurement: the R-4 scorecard (`tools.analysis.features.scorecard`, copied from origin/main), **z1 panel, seed 1,
parent Ares V06**, for hb1-04 and the three ports, as one detached chain (`tools/hb1/q4q5_chain.sh`; log
`build/hb1/games/q4q5_chain.log`). Scope cut from z1+gen to z1 only: at the shared host's measured ~2 games/min
(load ~100), z1+gen for five bots is ~26 h; z1 (the gate panel) is ~7 h. The gen panel follows if wanted.

### Q5 result 1 — hb1-10-escape-split vs Ares V06, z1 panel seed 1 (`game_stats/runs/hb1-10-escape-split-z1-s1.{json,md}`)

**GATE: fail** (verdict recorded as-is). W–L 132–28 vs parent 122–38 (+6.25 pp expected-score share); economy mean
+0.040 (r50 +0.044, r100 +0.031, r150 +0.017, r250 +0.068); length r100 +0.059; births r100 +0.043; dragons r100
−0.005. Tier-2: own-body deaths 3.66 → 4.05 /1k (**+10.5 %**, over the 10 % limit), wall +1.5 %, ally body −4.4 %,
ally head-on −0.8 %. The port helps on every economy checkpoint and on wins; it fails on one hygiene rate by 0.5 pp,
plausibly parent and child tangling after a split in a cramped space. One seed; a paired seed 2 (D-032) is the next
measurement for this row. Ledger: L24 (escape split at low reach) — supportive.

### Q5 result 2 — hb1-11-split-gate vs Ares V06, z1 panel seed 1 (`game_stats/runs/hb1-11-split-gate-z1-s1.{json,md}`)

**GATE: fail**, clearly: economy mean −0.135, dragons r100 −0.233, win share −11.56 pp, own-body deaths +18 %,
length r100 +0.018. Heartbreaker's production admission (split right after eating at length ≤ 4, very selective in
the open) starves Ares of dragons. The gate is tuned to Heartbreaker's own eating rhythm, i.e. to its direction
policy; transplanted alone onto Ares's steering it does not transfer. Ledger L27: a learned decision function does
not transfer when its inputs' distribution depends on the donor's other decisions.

### Q5 result 3 — hb1-12-direction-prior vs Ares V06, z1 panel seed 1 (`game_stats/runs/hb1-12-direction-prior-z1-s1.{json,md}`)

**GATE: hold** — the strongest Q5 result. W–L 139–21 vs parent 122–38 (+10.62 pp share, +17.0 expected-score points);
pearls r50 +0.160, r100 +0.079, r150 +0.007, **r250 −0.089** (economy mean +0.0393, short of +0.05); dragons r100
+0.194; length r100 +0.229; births r100 +0.068. Tier-2 all down: wall −36.5 %, own body −8.1 %, ally body −39.1 %,
ally head-on −34.0 %. Heartbreaker's learned direction choice, used only as a prior (λ = 1.0, fixed before
screening) inside Ares's search, makes Ares much better early and much cleaner; the one negative is late economy
(r250). That is the H10/L03 phase-bifurcation pattern — the ledger's prescription is phase-conditional logic
(the prior strong early, faded late), which is the next single-mechanism version, plus a paired seed 2.

### hb1-04-deployable (the mimic) vs Ares V06, z1 panel seed 1 (`game_stats/runs/hb1-04-deployable-z1-s1.{json,md}`)

**GATE: fail** (as expected of a mimic, not a candidate). W–L 94–66 vs parent 122–38 (−17.50 pp); economy mean
**+0.212** (r50 +0.429, r100 +0.363, r150 +0.111, r250 −0.055); dragons r100 +0.100; length r100 +0.485; births
+0.232. Tier-2: own body 3.66 → **0.00** (the wrapper never steps onto its own body), wall −19.1 %, ally body −54.3 %,
**ally head-on +147 %** (0.97 → 2.41/1k — the W2 exit-less fallback into an ally head). Heartbreaker's signature on
the field-relative yardstick: by far the most productive bot on the panel early, and it still loses more games —
material without conversion, as in the corpus. Note: 2 of 160 fixtures (Slithery Fight vs the Python Vibing++ mimic)
ran past run_panel's 1800 s and were refilled with a 7200 s timeout (`tools/hb1/run_panel_long.py`); one duplicate
index row from overlapping runners was removed (backup `index.jsonl.bak-dups`).
