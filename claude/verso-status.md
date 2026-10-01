# X-1 `verso` status — Verso lineage (Claude Opus 5.5, desktop)

Three-tier learned loop on Ares (prompt: `docs/hub/prompts/2026-10-01-X1-three-tier-loop.md`). Branch `r/verso`,
worktree `../wt-verso`, bots `bots/verso-*`, tools `tools/verso/`. Decision memo: §0 of
`docs/findings/2026-10-01-verso-three-tier-loop.md`. Gate: D-032 (`tools/verso/lane.py score`, Maelle's code
unchanged). The host is shared with the top-teams mimic lane (`r/tt`), which has priority: Verso games run at
`nice 19`, 12 in parallel.

## Cycle table

| Cycle | Version / arm | What changed | Per-head held-out | Fidelity to previous | Pool (D-032, seeds 1–3) | Gen (D-032, seeds 1–3) | CPU max | Verdict |
|---|---|---|---|---|---|---|---|---|
| — | `verso-00-base` | platform: runtime for heads, dump, exploration; inert | — | golden vs maelle-01-nodevil: 61,667 turns, 0 divergent | = maelle-02-features (8 re-played fixtures identical) | = | (maelle-02: 8.7 M) | base |
| 0 | `verso-01-hb-dir-prior` (arm `c0-hb-small~l1`) | `dir` head on Heartbreaker's corpus moves (v5 features), prior `λ·log p`, λ = 1 | direction 0.829 (their moves) | 0.885 of the base's commands (57,213 turns, 4 games) | win +0.150 [+0.110, +0.188]; econ~ **+0.052 [+0.019, +0.081]**; units +0.193, length +0.151; all four death rates down | win +0.050 [+0.012, +0.089]; econ~ +0.013 [−0.017, +0.042]; units +0.305, length +0.327 | 11.53 M | **ACCEPT** |
| 1 | screening (platforms `verso-p2/p3-platform`) | tier 3 on own data: Monte-Carlo `q`; hindsight-search `q` (5 label versions); tempo-credit labels; opening donor ensembles | MC 0.015; hindsight 0.76–0.86 | — | best so far `c0x-both-sf`: tempo −2.6 [−4.5, −0.8] rounds, econ~ −0.026 (seed 1); every `q` head REJECT | — | — | no accept yet |
| 2 | `verso-02-hb540-prior` (arm `c3-big540`) | new base: the 540-round Heartbreaker prior (hb1-14's size) on the Verso base; platform p4 | direction 0.843 (their moves) | pending | vs cycle 0: win +0.000 [−0.032, +0.033]; econ~ −0.001 [−0.028, +0.026]; tempo −1.0 | vs cycle 0: win **+0.097 [+0.064, +0.130]**; econ~ **+0.107 [+0.081, +0.135]**; tempo −6.3 [−8.4, −4.2] | 11.73 M | REJECT by the letter (pool lower bounds); off-pool gain — lead's call |
| 3 | `verso-03-hb1000-prior` (native) | 1,000-round prior, compact streams decoded at boot | 0.847 | — | vs cycle 2: win +0.021, econ~ +0.008 [−0.020, +0.036] | vs cycle 2: win +0.034 [+0.007, +0.060], econ~ +0.044 [+0.021, +0.067] | **fails in the sandbox** (boot decode > 100 M points) | not deployable |
| 3′ | **`verso-05-hb800-prior`** | 800-round prior, evaluated in place (no boot decode), zip 3.38 MiB | — | 0 divergent vs its file-loaded arm | vs cycle 2: win **+0.033 [+0.003, +0.065]**, econ~ −0.017 [−0.038, +0.013] | vs cycle 2: win +0.024 [−0.003, +0.049], econ~ +0.017 [−0.006, +0.040], length@100 +0.085; vs cycle 0: win +0.121, econ~ +0.124 | **12.01 M** | **lane parent** (lead, 1 Oct: kept despite the D-032 letter — pool lower bounds — for later comparison) |

Three lines: **what changed** — the prior's size is the lever (300 → 540 → 1,000 → 2,251 rounds all measured); the
work since cycle 2 was fitting more of it into the 4 MiB upload and the judge's first-turn CPU budget. **What it
did** — a 1,000-round prior in a compressed format plays better natively but cannot boot in the sandbox (decoding
1.5 M nodes costs > 100 M points); an 800-round prior evaluated in place (`verso-05-hb800-prior`, 3.38 MiB, 12.0 M
max) is the best deployable bot: vs cycle 0 off-pool win +12.1 pp, economy +0.124; vs cycle 2 pool win +3.3 pp.
Opening-knob SPSA was stopped at 6 iterations as noise-limited (SE 0.07 per iteration against effects < 0.05).
**Next** — the lead's call on the D-032 letter (pool lower bounds) vs the off-pool gains; then a better donor model
(more Heartbreaker data, or distillation of the full model into fewer nodes).

## Platform (30 Sep)

- `bots/verso-00-base`: `maelle-02-features` at zero weights (lune-r1-07 late cap, D-033 terms off, SF-1
  `state.hpp`) + `verso.hpp`. Feature schema 447 columns: v5 270 (HB-1's actor-local row, map-identity columns
  dropped), Ares search outputs 58, tier-4 route features and state scalars 119. Golden replay of
  maelle-01-nodevil's five transcripts: 61,667 turns, **0 divergent**; with `VERSO_DUMP` and the view tensor on:
  0 divergent.
- Determinism: 8 pool fixtures (Portals, seed 1) re-played with `verso-00-base` give metrics identical to
  `maelle-02-features`' recorded runs, so the parent arm **imports Maelle's 1,224 finished parent games**
  (pool + gen, seeds 1–3) instead of re-playing them (`lane.py import`).
- Tools: `lane.py` (panels, train games, D-032 gate; fork of Maelle's), `train_heads.py` (corpus `dir` heads,
  own-data `q` heads), `export.py` (boosters → head blob / header, C++ parity), `dataset.py` (dump + replay
  outcomes → per-game arrays), `common.py`.
- Incident: `verso-00-base` was edited (view-tensor dump added, behaviour-neutral) while a screen was running;
  the rebuild killed 15 games in flight, which were re-played. The directory is frozen from that point; changes
  go to new directories.

## Cycle 0 — `dir` heads on corpus targets, v5 features only

Held-out = 20 % of each team's corpus games, by game, seed 62. XGBoost (GPU), 255 leaves, lr 0.1, early stop.
C++ evaluator parity vs XGBoost margins on 3,000 held-out rows per model: max |Δ| < 4e-5, 0 argmax differences.

| Head | Donor | Train rows | Rounds | Held-out direction accuracy | Blob |
|---|---|---:|---:|---:|---:|
| `c0-hb-small` | Heartbreaker (62), 1,200 rows/game, 63 leaves | 0.66 M | 300 (cap) | 0.829 | 0.9 MB |
| `c0-hb` | Heartbreaker (62), 3,000 rows/game | 1.45 M | 2,251 | 0.856 | 27.5 MB |
| `c0-cj` | cheji bt (70), 600 rows/game | 1.73 M | 2,217 | 0.774 | 27.1 MB |
| `c0-sf` | Stockfish (206), 1,200 rows/game | 1.55 M | 1,979 | 0.787 | 24.2 MB |
| `c0-top3` | all three pooled | — | — | 0.787 | 36.7 MB |

Screens (pool, seed 1, 160 paired fixtures vs `verso-00-base`; λ = 1, fixed before screening):

| Arm | W rate (parent 0.662) | d econ~ [90 %] | d p50 | d p100 | d p150 | d p250 | d units@100 | d length@100 | d win | Hygiene |
|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|
| `c0-hb-small~l1` | 0.863 | +0.105 [+0.058, +0.174] | +0.151 | +0.117 | +0.101 | +0.050 | +0.339 | +0.265 | +0.200 [+0.131, +0.269] | wall 8.57→7.13, self 5.69→4.76, ally body 2.80→2.02, ally head-on 2.60→1.88 |
| `c0-hb~l1` | 0.863 | +0.093 [+0.042, +0.170] | +0.146 | +0.105 | +0.087 | +0.034 | +0.242 | +0.247 | +0.200 [+0.125, +0.269] | wall 6.20, self 4.14, ally body 1.72, ally head-on 1.92 |
| `c0-cj~l1` | 0.831 | +0.073 [+0.024, +0.156] | +0.166 | +0.071 | +0.032 | +0.023 | +0.298 | +0.227 | +0.169 [+0.100, +0.237] | wall 7.73, self 5.59, ally body 2.79, ally head-on 2.08 |
| `c0-sf~l1` | 0.831 | +0.085 [−0.008, +0.149] | +0.288 | +0.007 | +0.010 | +0.034 | +0.191 | +0.187 | +0.169 [+0.106, +0.231] | wall 6.25, self 4.63, ally body 2.01, ally head-on 1.29 |
| `c0-top3~l1` | 0.825 | +0.045 [+0.000, +0.117] | +0.066 | +0.042 | +0.059 | +0.014 | +0.164 | +0.198 | +0.163 [+0.100, +0.231] | wall, ally body, ally head-on down |

Reading: every donor's direction model helps Ares as a prior (+16 to +20 pp win on seed 1); Heartbreaker's is the
best although it is the weakest team of the three — its policy is the most predictable from the local view
(0.83–0.86 against 0.77–0.79), so its prior is the sharpest. The small head (0.829, 0.9 MB) screens the same as
the 27 MB one (0.856): as a prior inside a search the last 3 pp of imitation accuracy buy nothing, so the
deployable head is small. Pooling donors is worse than any single donor. `c0-top3` held-out: 0.787.

### Cycle 0 gate — `c0-hb-small~l1` vs `verso-00-base`, D-032, seeds 1–3: ACCEPT

| Panel | n paired | win | d econ~ [90 %] | d econ mean | d p50 | d p100 | d p150 | d p250 | d units@100 | d length@100 | d win [90 %] |
|---|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| pool | 480 | 0.698 → 0.848 | +0.052 [+0.019, +0.081] | +0.069 | +0.111 | +0.092 | +0.030 | −0.024 | +0.193 | +0.151 | +0.150 [+0.110, +0.188] |
| gen | 744 | 0.568 → 0.618 | +0.013 [−0.017, +0.042] | +0.063 | +0.080 | +0.014 | −0.015 | −0.028 | +0.305 | +0.327 | +0.050 [+0.012, +0.089] |

Death rates per 1k dragon-turns, pool: wall 8.60 → 7.16, own body 5.99 → 4.88, ally body 2.99 → 2.02, ally
head-on 2.72 → 1.97; gen: 3.79 → 2.91, 3.24 → 2.16, 2.38 → 1.08, 1.36 → 1.00. Newborn deaths (first 10 rounds, per
100 births) 35.6 → 31.3 and 30.5 → 24.9.

- Economy vs material (seed 1, both panels): pearls@250 −1 % on the pool and −17 % off-pool while total length
  at r250 is +41 % and +27 % and deaths by r250 −16 % and −32 %. The corpse share of what is eaten falls (pool
  0.452 → 0.419, gen 0.438 → 0.381 at r250): the late "economy" the base had was partly its own dead (L29). Bed
  pearls@100 are up on both panels (+14 %, +6 %); bed pearls@250 are down off-pool (−9 %).
- The off-pool effect is strongly map-dependent (seed 1 win deltas): +0.50 to +0.75 on `devil_tr`, `trophy_tr`,
  `queen_of_spades_tr`, `trauma_tr`, `autarky_tr`, `archipelago`, `commons_shared`; −0.50 to −0.62 on `far_harbors`,
  `default_tr`, `crossroads_tr`, `pulse_farms`. The losers are large or sparse maps with remote income: a
  local-view prior out-votes Ares's long-range target when nothing is in view. A fixed λ is the wrong shape off
  the pool; the fix is a state-dependent term (cycle 1), not a smaller λ.
- Determinism and provenance: the arm was measured as `verso-00-base` + `VERSO_POLICY`; `verso-01-hb-dir-prior`
  embeds the same head and reproduces the arm's transcript exactly (12,217 turns, 0 divergent).
- Sandbox CPU, `verso-01-hb-dir-prior` (4 dense maps × both seats vs ares-v06): p50 4.4–8.6 M, p99 ≤ 9.95 M,
  **max 11.53 M** points/turn (big_empty A), 0 errors.
- Fidelity: `c0-hb-small~l1` issues the same command as the base on 88.5 % of the base's own turns (4 games,
  57,213 turns; open-loop replay).

## Cycle 1 — tier 3 on our own data (in progress)

Platform `verso-p2-platform` (schema 450: + `h_dir_{F,R,L}`; split exploration; optional split output on `q`).
Collector arm `c1a` = cycle-0 policy + ε = 0.1 on the first step + ε_split = 0.1 + view tensors. Data games:
`train` panel, seed 101 — 5 off-panel maps + the 10 live maps × (8 zoo opponents both seats + 1 mirror) = 255
games, 12 minutes; 2,506,344 actor-turn rows (2,454,036 moves, 52,308 splits; 213,725 exploratory steps), 1.6 GB.

### Operator A — Monte-Carlo Q (`c1-qA`): rejected at this budget

Target: 20-round lineage return (Δ length + 3·Δ units of the dragon and its descendants). V(s) cross-fitted
(held-out R² 0.142), then one residual regressor per first step (mirror-augmented).

| Head | Rounds (early stop) | Held-out R² of the residual | corr |
|---|---:|---:|---:|
| F / R / L | 75 / 21 / 14 | 0.017 / 0.015 / 0.012 | 0.13 / 0.13 / 0.13 |

Held-out exploratory steps: realised residual +0.04 when the step is the head's argmax (32 % of them), −0.18
otherwise — the head recognises bad alternatives and finds no good ones (+0.04 ± 0.03). Screens vs the cycle-0 arm
(pool, seed 1, 160 paired):

| Arm | d econ~ [90 %] | d units@100 | d length@100 | d win [90 %] | Verdict |
|---|---|---:|---:|---|---|
| `c1-qA~b1` (β = 1) | −0.050 [−0.101, −0.009] | −0.104 | −0.065 | −0.062 [−0.119, −0.006] | REJECT |
| `c1-qA~b3` (β = 3) | −0.107 [−0.173, −0.044] | −0.175 | −0.134 | −0.056 [−0.113, +0.000] | REJECT |

Reading: with 214 k exploratory rows the advantage estimate is noise (R² 0.015); adding it to the path score is
adding noise, and it costs in proportion to β. Monte-Carlo credit needs an order of magnitude more exploratory
data to be usable here; not pursued while operator B works.

### Operator B — hindsight search (`tools/verso/relabel.py`, `cpp/hindsight.cpp`)

For each logged move, the best value of each first step over the *recorded* next 20 rounds (true terrain, every
other dragon moving as it did, pearls as they appeared; head-to-head = both die, scored as a material trade);
255 games relabelled in 2 m 16 s. Audit against the record (2.43 M one-step moves):

- a recorded step that survived 20 rounds is called fatal in 0.39 % of cases (model error);
- 1.3 % of all decisions (32,472) were fatal with a surviving alternative;
- when did the death become unavoidable (share of rows with some surviving first step, by rounds before the
  dragon's own death): wall deaths 0.1 % at the fatal move, 28 % one round before, 35 % two, 42 % three, 56 % four
  (the taken step survives in 3 %, 20 %, 33 %, 46 %) — trap deaths are decided 2–5 rounds before they happen;
  head-to-heads we initiate have a surviving alternative 75 % of the time; being rammed is avoidable on the last
  move in 86 % of cases with hindsight (not all of that is learnable).

Head `c1-hA`: three regressors of the clipped hindsight advantage on all 450 features, every move row
(mirror-augmented); held-out R² **0.76 / 0.78 / 0.78**. Offline, on held-out games, the bot's one-step choice
rebuilt from its own dumped scores (agrees with the recorded greedy choice on 98.7 % of rows):

| Policy (rebuilt) | Hindsight regret | Fatal-choice rate |
|---|---:|---:|
| Ares hand score alone | 0.373 | 2.81 % |
| + Heartbreaker prior (cycle 0) | 0.251 | 1.51 % |
| + hindsight head, β = 1 / 4 / 8 | 0.238 / 0.229 / 0.227 | 1.26 % / 1.09 % / 1.05 % |
| hand + hindsight head, **no donor prior**, β = 4 | 0.232 | 1.13 % |
| hindsight head alone | 0.217 | 1.02 % |

The escape-split-free labels above over-punished dead ends. Later label versions (all hindsight, 20 rounds, all
screened at β = 1 against the cycle-0 arm, pool seed 1, 160 paired):

| Head | Label change | R² (F/R/L) | d econ~ [90 %] | bed pearls r100 / r250 | d win | Tempo (rounds) | Wall deaths /1k (parent 7.13) |
|---|---|---|---|---|---:|---|---:|
| `c1-hA` | material loss (length + 3), ram pinned on the cell we took | 0.76–0.78 | −0.361 [−0.415, −0.297] | −18 % / −18 % | −0.031 | — | 2.0 at β = 4 |
| `c1-hC` | ram modelled as a zone around the attacker (reactive), enemy head arrivals at p = 0.5 | 0.83–0.84 | −0.386 [−0.448, −0.289] | −19 % / −20 % | −0.044 | — | 3.86 |
| `c1-hD` | + pearls discounted 0.8 (earliness) | 0.82–0.84 | −0.274 [−0.317, −0.199] | −11 % / −11 % | −0.072 | — | 4.73 |
| `c1-hE` | + escape split: a dragon ≥ 4 that runs out of moves loses only the stub | 0.85–0.86 | −0.112 [−0.169, −0.057] | −5 % / −4 % | −0.019 | +2.7 [+1.1, +4.3] REJECT | 5.96 |
| `c1-hT` | tempo credit: loss = 0.6 × length (we eat back 45 % of our dead, measured), enemy kill +0.45 × length, no unit term, pearls 0.9 | 0.79–0.81 | −0.006 [−0.061, +0.042] | 0 % / −1 % | −0.025 | +2.5 [+1.0, +3.9] REJECT | 6.78 |
| `c1-hT` β = 2 | same | | −0.038 [−0.087, +0.024] | −1 % / 0 % | −0.025 | +1.7 [+0.1, +3.3] REJECT | 6.52 |

Hindsight β sweep of `c1-hA`: β 0.5 / 1 / 2 / 4 / 8 → d econ~ −0.19 / −0.36 / −0.57 / −0.60 / −0.61, d win −0.04 / −0.03 /
−0.14 / −0.15 / −0.24: monotone harm.

Reading: every modelling fix moved the head toward neutral, none past it. The first versions were a lesson in
credit: charging a death at full material when the side eats back 45 % of its dead (S-1's tempo accounting) makes
the learned term too cautious, and a cautious dragon leaves contested beds (bed pearls −18 %) while its wall deaths
fall 70 %. With tempo credit the head stops hurting and stops helping: in the offline rebuild it changes 1.6 % of
choices and lowers the hindsight fatal-choice rate 1.2 % → 1.1 %; in games that is inside the noise. On this
policy the first-step choice is no longer where the tempo is lost — L36's components (bed conversion, production,
early transit, territory) are macro decisions the steering term does not reach.

### Opening controller (lead's direction, 1 Oct): tempo as the opening objective

S-1's tempo gate on the cycle-0 arms (vs `verso-00-base`): pool −7.6 rounds [−8.9, −6.4] ACCEPT (seeds 1–3); gen
−7.7 [−9.5, −5.9], INCONCLUSIVE only through the per-map guard (`crossroads_tr`, `portal_quartet`, `pulse_farms`,
`seam_market` slower). Donor priors, seed 1: Heartbreaker 27 MB −9.8, cheji bt −9.1, Stockfish −7.5, pooled −6.6.

Platform `verso-p3-platform`: 27 Ares knobs made runtime values and blended by an opening belief
`b = sigmoid(8 (0.6 − units/limit − 1.5 round/500 − 0·contact))` (measured state, clock as a soft prior; ~0.5 by
round 100): `value = base + b (opening − base)`; a second direction head (`dir2`) with its own phase weight.
Golden parity at the defaults and with the cycle-0 head (0 divergent). Screens against the cycle-0 arm (pool,
seed 1):

| Arm | Opening (b high) | Later | d econ~ [90 %] | d p50 | d win | Tempo (rounds) [95 %] |
|---|---|---|---|---:|---:|---|
| `c0x-open-sf` | Stockfish small prior only | Heartbreaker | −0.059 [−0.107, −0.011] | −0.034 | −0.069 | +1.4 [−0.6, +3.4] NO GAIN |
| `c0x-open-cj` | cheji bt small prior only | Heartbreaker | −0.230 [−0.305, −0.134] | −0.266 | −0.056 | +5.7 [+3.5, +7.9] REJECT |
| `c0x-spec-sf` | Stockfish prior fitted on rounds ≤ 120 only | Heartbreaker | −0.049 [−0.125, −0.002] | +0.041 | −0.044 | +2.3 [+0.2, +4.4] REJECT |
| **`c0x-both-sf`** | Heartbreaker **+** Stockfish (both λ = 1) | Heartbreaker | −0.026 [−0.081, +0.015] | +0.109 | −0.009 | **−2.6 [−4.5, −0.8]** INCONCLUSIVE |

Reading: Heartbreaker's prior is the better opening controller on its own; a second donor added to it (not
replacing it) is the first move that makes the opening faster than cycle 0. Seeds 2–3 queued, plus the same with
cheji bt and with an opening-specialist Heartbreaker head.

### Tier questions (offline, tempo-credit hindsight targets, equal data, no mirror augmentation)

| Features | Advantage R² F / R / L | Head-alone hindsight regret |
|---|---|---:|
| v5 (+ prior output) | 0.776 / 0.795 / 0.797 | 0.142 |
| + Ares search outputs | 0.781 / 0.799 / 0.800 | 0.133 |
| + tier-4 map memory (no Ares) | 0.782 / 0.801 / 0.802 | 0.132 |
| v5 + Ares + tier 4 | 0.784 / 0.804 / 0.803 | **0.129** |
| v5 + Ares + tier 4 + tier-1 state | 0.783 / 0.802 / 0.803 | 0.130 |
| v5 + tier-1 state | 0.776 / 0.793 / 0.794 | 0.141 |

- **Tier 4** (route features over the map memory) earns a small, consistent place: +0.6 pp R², −7 % regret over v5.
- **Tier 1** (CNN over an 11×11 ego window of the map memory, 18 channels + GRU-96; 8 epochs, held-out policy
  accuracy 0.82) adds nothing at equal data (≤ ±0.2 pp) — **dropped** under the pre-registered rule. Linear probes
  on its state: reach within 8 steps R² 0.75, food density 0.48, corridor length 0.46, beds known 0.49, Ares's
  target type 50 % (majority 29 %): it learned a compressor of the hand state, not new state.
- Monte-Carlo Q (operator A) is also out at this budget (above).

## Cycle 2 — the base question (lead, 1 Oct: try hb1-14 or tt-05 as base, or an hb → tt interpolation)

hb1-14 = hb1-12 with its prior cut to 540 rounds (uploadable); tt-05 = hb1-14 feeding the crown from ~r300
(`feed_base` 140); tt-06 = the hb1-14 → tt-05 hand-over of the feeding onset between r300 and r400. Copied into the
Verso tree unmodified for measurement (not committed here). All three are V06 underneath (late cap 48, the
`W == 32 && H == 16` terms on). Against cycle 0 (arm `c0-hb-small~l1`), seed 1:

| Bot | Pool win | Pool econ~ | Gen win | Gen econ~ [90 %] | Tempo pool / gen (rounds) |
|---|---|---|---|---|---|
| hb1-14 | 0.863 → 0.881 | −0.040 | 0.641 → 0.724 (+0.083 [+0.022, +0.141]) | +0.098 [+0.057, +0.146] | −7.2 / −0.8 |
| tt-05 | 0.881 | −0.040 | 0.702 | +0.098 | −7.2 / −0.8 |
| tt-06 | 0.863 | −0.040 | 0.714 | +0.098 | −7.2 / −0.8 |

(identical through r250 — the three differ only after ~r300). Taken apart on the Verso base (p4 platform), seed 1,
against cycle 0:

| Arm | Change | Pool win / econ~ | Gen win [90 %] | Gen econ~ [90 %] | Tempo pool / gen |
|---|---|---|---|---|---|
| `c2-feed140` | tt-05's feeding from ~r300, whole game | −0.013 / 0 | −0.004 | 0 (identical to r250) | 0 / 0 |
| `c2-ramp140` | hb → tt feeding onset ramped over r300–400 | −0.031 / 0 | +0.028 [+0.004, +0.052] | 0 | 0 / 0 |
| `c3-cap48` | V06's late search cap | −0.056 / −0.037 | +0.012 | −0.023 | +0.5 / −0.9 |
| `c3-big540` | **540-round prior** | −0.025 / −0.028 | **+0.057 [+0.004, +0.109]** | **+0.115 [+0.065, +0.166]** | −6.1 / −1.1 |
| `c3-big540-cap48` | both | +0.019 / −0.084 | +0.052 | +0.053 | −0.7 / −3.8 |
| `c3-big540-ramp140` (vs c3-big540) | + the hb → tt ramp | +0.006 / 0 | +0.016 | 0 | — |

Late feeding raises own-body deaths 13–23 % and changes nothing the panels can see (no zoo opponent converts; the
mimic lane's reading) — it stays a ladder question. **Decision: the base becomes `c3-big540`** and its D-032 run
against cycle 0 (seeds 1–3) reads:

| Panel | n paired | win | d econ~ [90 %] | d p50 / p100 / p150 / p250 | d units@100 | d length@100 | tempo (rounds) |
|---|---:|---|---|---|---:|---:|---|
| pool | 480 | 0.848 → 0.848 | −0.001 [−0.028, +0.026] | +0.021 / −0.029 / −0.022 / +0.025 | +0.079 | +0.040 | −1.0 [−2.1, +0.1] NO GAIN |
| gen | 744 | 0.618 → 0.716 (+0.097 [+0.064, +0.130]) | **+0.107 [+0.081, +0.135]** | +0.092 / +0.130 / +0.114 / +0.093 | +0.179 | +0.130 | −6.3 [−8.4, −4.2] INCONCLUSIVE (map guard: spring_wells) |

D-032 by the letter: REJECT (pool econ~ lower bound −0.028 ≤ 0, pool win lower bound −0.032). Both pool point
estimates are 0; the off-pool gain is the largest measured in this lane. Kept as the lane's parent (the lead may
read the letter differently for promotion); `bots/verso-02-hb540-prior` embeds the head (reproduces the arm, 0
divergent; upload zip 3.68 MiB).

HB + Stockfish opening ensemble (`c0x-both-sf`), seeds 1–3 vs cycle 0: tempo −0.5 [−1.7, +0.7] NO GAIN, econ~ −0.062
[−0.103, −0.027] — the seed-1 −2.6 was noise. Also NO GAIN: + cheji bt in the opening (+0.8), + an opening-only
Heartbreaker head (+1.5, econ~ −0.101).

## Cycle 3 — how much prior fits (1 Oct)

Against the 540-round base (`c3-big540`), seed 1 unless stated:

| Arm | Prior | Pool win / econ~ | Gen win [90 %] | Gen econ~ [90 %] |
|---|---|---|---|---|
| `c3-full` (seeds 1–3) | all 2,251 rounds (27 MB, local only) | +0.017 / **+0.044 [+0.015, +0.080]** | +0.011 [−0.016, +0.036] | **+0.037 [+0.009, +0.068]** |
| `c3-hb1000` | 1,000 rounds | +0.025 / +0.038 | +0.040 [−0.012, +0.089] | +0.043 [−0.002, +0.092] |
| `c3-big540~l0.7` | λ 0.7 | +0.006 / −0.000 | +0.044 | −0.015 |
| `c3-big540~l1.5` | λ 1.5 | +0.031 / −0.025 | −0.028 | −0.059 |
| `c3-mirror540` | 540 rounds, mirror-augmented fit (held-out 0.847) | +0.009 / −0.052 | +0.012 | +0.018 |
| `verso-03-hb1000-prior` (seeds 1–3, native) | 1,000 rounds, compact | +0.021 / +0.008 | +0.034 [+0.007, +0.060] | +0.044 [+0.021, +0.067] |
| `verso-05-hb800-prior` (seeds 1–3) | 800 rounds, direct | **+0.033 [+0.003, +0.065]** / −0.017 | +0.024 [−0.003, +0.049] | +0.017 [−0.006, +0.040] |

Formats (zip of the bot's sources; limit 4 MiB): 8-byte hex words 540 rounds = 3.68 MiB (`verso-02`); compact
streams (shape bits, feature ids, threshold index into per-feature tables, default bits, float16 leaves) 1,000 rounds =
3.37 MiB but needs a boot decode the judge prices at ~185 points per node — 1,000 rounds (1.53 M nodes) fails turn 0
(`verso-03`, `verso-04` with a single-pass decoder, both "exceeded CPU limit" on every dragon; 300 rounds alone
costs 89 M); direct form (three uint16 arrays per node, same tables, float16 leaves; evaluated in place) 800 rounds
= 3.38 MiB, boot 7.8 M points. float16 leaves changed no decision in 10–12 k-turn transcripts.

SPSA on the opening knobs (`es2`, base `c3-big540`, net-income objective on data fixtures): stopped after 6
iterations; per-iteration J standard error 0.07–0.11, check vs base at iteration 6 −0.015 ± 0.067. Resumable from
`build/verso/es/es2/history.jsonl`.
