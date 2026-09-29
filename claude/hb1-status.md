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

Next: Q1 — per-decision datasets (split gate, allocation, direction, sonar, late concentration) and the
shallow-tree / GBT / MLP gap table.
