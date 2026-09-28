# C1-E — the field's pace targets from the corpus  (model: **GLM 5.3**)

Shared rules: `docs/hub/prompts/2026-09-29-C1-index.md`. No dependency; start now; deliver within 24 hours — the
builders are working to placeholders until you do. This is the narrow, fast slice of the A2 corpus programme
(`docs/hub/prompts/2026-09-29-A2-corpus-statistics.md`), not a replacement for it.

## 0. The job

One table: what the field does in the first 100 rounds, so the C++ bots have numbers to hit rather than guesses.

## 1. Data

`REPO/public_replays/corpus/` — `index.jsonl` (one row per game: teams, ranked flag, autoscrim window, map, winner,
timestamps; **no submission ids** — the API stopped returning them on 28 Sep, D-023) and `replays/<gid>.replay`
(gzipped server replays, version 2, ~5,000 and growing at ~2,400/h). Ladder snapshots in `ladder/` give each
team's rating over time; use the latest for rank bands. Decode with the vendored reader the hub uses
(`tools/hub/vendor/`) or `tools/replay_stats/`; the hub's per-game stage extractor (`tools/hub/executor.py::harvest_one`
→ `analyse_replay`) already computes units/total/longest at r25, r50, r100, r200, r250, … per side — reuse it in a
batch script, do not rewrite the decoder. Process in the cloud workspace if the Mac is busy; the replays copy in
chunks.

## 2. The table (`docs/analysis/C1-pace-targets.md` + `game_stats/field_pace_targets.json`)

For each of the ten live maps and for the map classes (compact / open), by cohort — **top 10, ranks 11–30, band
55–85, team 7** — medians and quartiles of: units at r25/r50/r100/r200; total length at r50/r100/r250; first-pearl
round; pearls eaten by r100 (if the replay exposes it; else length gained by r100); **pearls per dragon-turn alive
and moves per pearl by r100 (the efficiency numbers — pace cannot be forced, so these are the targets that matter)**;
deaths by cause per 1k dragon-turns by r100; longest at r100; number of splits by r100. Ranked games only for the cohort profiles (unranked test batches contain other teams' candidates), the
autoscrim-window flag as a covariate; both sides pooled unless side matters (report if it does).

Add two comparisons the builders need: the **winner-minus-loser** gap at r50 and r100 within the top-30 games (how
early the field decides its own games), and **team 7 minus band** on the same statistics (how far behind we are and
on which maps).

## 3. Report

The markdown file with the table and ten lines of reading; the JSON with the medians the sweeps consume
(`{"map": {"cohort": {"units_r100": …}}}`). Status `claude/c1-e-status.md`. Caveats to state: no submission ids
(team-level pooling mixes versions), the corpus covers one day, ranked-only filtering. Then continue with A2 proper.
