# antioch — P2-A Claude analyst, replay lead (from 1 Oct 2026)

Worktree `../wt-antioch` (desktop), branch `r/antioch`, tools `tools/antioch/`, findings `docs/findings/<date>-antioch-*.md`.
Data: the corpus and the S-1 store are rsynced from the Mac into this worktree (`public_replays/corpus/`, `build/s1/`);
from now on the desktop copy of the store is the one I build. Never call the API; the hub collector stays on the Mac.

## Top — read this first (updated 2026-10-01 22:20 ACST)

- **Era switch:** the live server adopted 1.2.3 between **05:57:53Z** (last old-rule game) and **09:26:58Z** (first
  new-rule game) on 1 Oct; there are no games in between. Era rule: `post` ⇔ `started_at ≥ 2026-10-01T06:00Z`. Evidence:
  sprint pricing on 1,804 games (0 mixed; every priced sprint before is k−1, every one after is max(0, k−⌈L/4⌉)), and the
  queen field is non-zero only after. Tagged in the store: `games.era`; `S1_ERA=pre|post` scopes the views and norms.
- **The queen** is the team's *original* lowest-id dragon. The engine's 4th `TeamStanding` int32 equals its length and
  reads 0 once it has died; there is no succession. On a split the parent keeps the id **and the head end**
  (12,039/12,039 splits), so the queen survives splitting but keeps only the head piece.
- **Gate win share is computed with the old tiebreak.** `frame.decode` infers the winner as longest → total
  (`frame.py:224-233`); the scorecard's win share (`scorecard.py:141` via `extract.py:411`) inherits it. The fix (read the
  engine's own verdict and the queen field) is in `tools/antioch/patches/frame-engine-verdict.patch`, for the director to
  apply. FRAME_VERSION goes 5 → 6. Validated: the patched decoder matches the server's recorded winner on 300/300
  sampled corpus games (135 pre, 165 post, incl. 2 queen-decided).

- **Queen value:** where exactly one queen survives a round-limit game it won 36/36, 26 of those from behind on total.
  RL queen survival: field 2.2 %, top ten 0.7 %. Pocket maps (Slithery, Autarky, PD) kill every queen on r4–5.
- **Corpus gaps:** five of the top ten have no post-change games; no ladder snapshot since 06:21Z (requests on the board).
- **Next unit:** post-change opening references (Q3's four components) once `build.py corpus --era post` finishes
  (log `build/antioch/build-corpus.log`); `S1_ERA=post` norms; a stability check (bootstrap of the top-ten − field gap per
  checkpoint vs n); per-map queen table on the ten ladder maps; the gate-bug size on the testers' local panels
  (`tools/antioch/queen.py --glob 'build/zoo/**/*.replay'`).

## Live hypotheses

| id | claim | status | falsifier | size | suits |
|---|---|---|---|---|---|
| H-Q1 | queen preservation from r0 raises RL win ≥ 10 pp at ≤ 0.02 economy | posted 1 Oct, proposed ledger 0.7 | queen alive r490 on pool < 0.5, or RL win Δ LB ≤ 0 | pool + gen, seeds 1–3 | Claude tester |
| H-Q2 | feed the queen late (TT's cull-into-the-long-one, keyed on the queen) | posted, after H-Q1 | both-alive RL win ≤ 0.5 vs queen-keepers | ~200 games mirror | after H-Q1 |
| H-Q3 | pocket escape by splitting | **falsified** 1 Oct (engine probe) | — | — | — |
| H-Q4 | hunt the enemy queen once the field keeps queens | watch, 0.3 | field RL queen survival < 10 % for a week | corpus watch | — |

## Store maintenance (replay lead)

- `tools/s1/build.py`: `ERA_SWITCH`, `games.era`, `corpus --era pre|post`.
- `tools/s1/q.py`: `S1_ERA` scopes `c_sides` (and everything built on it) and the norms. Norms are cached as
  `norm_series_<era>.parquet`. Unset keeps the old pooled behaviour; it was tested unset and returns the same games.
- Sync from the Mac: `rsync -a alik@192.168.0.86:/Users/alik/Documents/Projects/UNSW-Battlecode-2026/public_replays/corpus/{index.jsonl,ladder,teams.json} public_replays/corpus/`,
  then `replays/`. Build with `nice -n 15 … build.py games && build.py corpus --era post --jobs 6`. The desktop is
  shared with the testers: stay at ≤ 6 jobs, niced.

## Log

- 2026-10-01 22:20 — launched. Era established, store tagged, queen semantics, decoder bug found.
- 2026-10-01 22:45 — unit 1 posted: finding, TARGETS endgame columns, 7 board lines, CORPUS.md, frame patch. H-Q3
  closed. Opening references pending the build.
