# Carthage — P2-T tester (Claude Opus 5.5), status

Worktree `../wt-carthage`, branch `r/carthage`, bots `bots/carthage-<nn>-<slug>/`, tools `tools/carthage/`,
runs `build/carthage/runs/<arm>/{pool,gen}/` (not committed). Host: desktop, `.venv` with `unswbc 1.2.3`, panels at
nice 10 with `--jobs 14`.

## Top (read this first)

- **2026-10-01 22:00** lane opened. The Phase-2 contract docs named in the tester brief (`docs/hub/PHASE2-PROTOCOL.md`,
  `BOARD.md`, `TARGETS.md`, `docs/PHASE1-SUMMARY.md`, `docs/TAXONOMY.md`) are on no branch yet (checked origin/*
  at 22:00); working from the brief, D-032 as coded in `tools/verso/lane.py`, and the ledger. Board lines are held in
  §Board drafts below until `BOARD.md` exists.
- The shared `.venv` was on `unswbc 1.2.2`; upgraded to 1.2.3 (no other lane was running games at the time).
- **Rules change in 1.2.3** (diffed the wheel; confirmed on game.battlecode.au/docs): (1) a game that reaches r500 is
  ranked by **queen length**, then longest dragon, then total length; the queen is the team's starting dragon with
  id 0 or 1, the parent keeps its id on every split, and a dead queen counts 0; (2) a sprint costs
  `max(0, steps − ceil(L/4))` segments (was steps − 1), so a dragon of length ≥ 5 moves 2 tiles a turn for free.
- **Shared-tool bug, fixed on this branch:** `tools/analysis/features/frame.py` decided r500 games by (longest, total);
  every lane's win rate under 1.2.3 is wrong where the queen term decides. Now (queen, longest, total), queen derived
  from the final snapshot (the replay does not store it), `FRAME_RULES=pre123` restores the old ranking for old
  corpora; `FRAME_VERSION` 5 → 6. Validated against the CLI verdict on 11 games including a "longer queen, 38 to 0".
- Base `carthage-00-base` = `hb1-14-prior-r540` + `shape_terms` switch (D-033 terms off). Golden parity: switch-on
  copy identical to hb1-14 on Devil (657 turns) and Trauma (9,454 turns); switch-off diverges only on Devil.

## Running table

| Version | Mechanism (switch) | Parent | Expected sign | Pool Δecon~ [lo, hi] | Gen Δecon~ lo | Win Δ [lo] | Tier-2 worst | Queen alive@490 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 00-base | hb1-14, D-033 terms off | hb1-14 | — | (re-measure, running) | | | | | base |
| 01-queen-guard | queen prices its own death +24 material (`queen_guard`) | 00 | queen alive@490 ↑, win ↑ (r500 games), econ ≈ 0/− | queued | | | | | |
| 02-queen-nosplit | queen never takes a production split (`queen_nosplit`) | 00 | queen length ↑, queen alive ↑, econ − (fewer births) | queued | | | | | |
| 03-queen-guard-nosplit | 01 + 02 stacked | 00 | both | queued | | | | | |

## Queen on the base (first look, 83 pool games, seed 1, partial)

- Queen alive at r490: 0 of 41 games that reached r490; the zoo's queens: 1 of 41. Median queen death round 77.
- Causes (cause, length): wall/3 22, self/3 14, h2h/3 13, wall/2 7, h2h/4 7, h2h/2 7, self/2 7. The queen splits a
  median 4 times and peaks at length 4: it plays as a small forager.
- Slithery Fight: the queen dies at **r3 in every game, both teams** — the spawn faces a dead end and the opening rescue
  split gives the tail 6 segments, leaving the head (the queen) at length 2. Queen-neutral map.
- The trapped escape split (`tyr_escape_split`) keeps the head at length 2 inside the trap: for the queen it is death.

## Board drafts (post when BOARD.md exists)

- `[2026-10-01 carthage → all]` unswbc 1.2.3 changes the r500 ranking to queen length first (queen = starting dragon
  id 0/1, dead = 0) and makes the first ceil(L/4) sprint steps free. `tools/analysis/features/frame.py` still ranks by
  (longest, total): every lane's win rate is wrong where the queen decides. Fix on `r/carthage` (frame v6). On the base,
  our queen is dead by r490 in 41/41 pool games (median death r77); so are the zoo's (40/41): a bot that keeps its
  queen alive wins every timed-out game against them. Taking it as my own hypothesis (C-Q1), carthage-01..03.
