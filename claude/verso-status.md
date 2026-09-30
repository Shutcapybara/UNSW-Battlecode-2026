# X-1 `verso` status — Verso lineage (Claude Opus 5.5, desktop)

Three-tier learned loop on Ares (prompt: `docs/hub/prompts/2026-10-01-X1-three-tier-loop.md`). Branch `r/verso`,
worktree `../wt-verso`, bots `bots/verso-*`, tools `tools/verso/`. Decision memo: §0 of
`docs/findings/2026-10-01-verso-three-tier-loop.md`. Gate: D-032 (`tools/verso/lane.py score`, Maelle's code
unchanged). The host is shared with the top-teams mimic lane (`r/tt`), which has priority: Verso games run at
`nice 19`, 12 in parallel.

## Cycle table

| Cycle | Version / arm | What changed | Per-head held-out | Fidelity to previous | Pool (D-032) | Gen (D-032) | CPU max | Verdict |
|---|---|---|---|---|---|---|---|---|
| — | `verso-00-base` | platform: runtime for heads, dump, exploration; inert | — | golden vs maelle-01-nodevil: 61,667 turns, 0 divergent | = maelle-02-features (8 re-played fixtures identical) | = | not probed yet | base |
| 0 | screening | `dir` head from corpus targets (v5 features), λ = 1 | see below | — | seed 1 only, below | — | — | in progress |

Three lines: **what changed** — the platform and the cycle-0 donor heads exist; **what it did** — the first screen
(Heartbreaker's small head as a prior) is +20 pp win and +0.105 econ~ on pool seed 1; **what is next** — donor
screens (Heartbreaker / cheji bt / Stockfish / pooled), the D-032 gate on both panels for the best, then cycle 1
data collection with ε-exploration.

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
