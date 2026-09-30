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
| 1 | screening (platform `verso-p2-platform`) | tier 3 on own data: (A) Monte-Carlo `q` head, (B) hindsight-search `q` head | A: advantage R² 0.012–0.017; B: 0.76–0.78 | — | A: REJECT at β = 1, 3 (seed 1); B: running | — | — | in progress |

Three lines: **what changed** — cycle 0 is accepted; cycle 1's data (255 exploratory games, 2.5 M rows) and both
improvement operators exist. **What it did** — the prior is the first D-032 accept (+15 pp win on the pool, +5 pp
off-pool, material +15–33 %); the Monte-Carlo Q head is noise at this budget and loses; the hindsight search
labels are learnable (R² 0.77) and cut the offline fatal-choice rate from 1.5 % to 1.05 %. **Next** — the
hindsight head's screens and gate; then distil it into our own `dir` head (no donor), synthetic training maps,
the tier-4 and tier-1 ablations.

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
| `c0-top3` | all three pooled | — | — | running | — |

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
