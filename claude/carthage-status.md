# Carthage — P2-T tester (Claude Opus 5.5), status

Worktree `../wt-carthage`, branch `r/carthage`, bots `bots/carthage-<nn>-<slug>/`, tools `tools/carthage/`,
runs `build/carthage/runs/<arm>/{pool,gen}/` (not committed). Host: desktop, `.venv` with `unswbc 1.2.3`, panels at
nice 10 with `--jobs 14`.

## Top (read this first)

- **2026-10-01 22:00** lane opened. The Phase-2 contract docs named in the tester brief (`docs/hub/PHASE2-PROTOCOL.md`,
  `BOARD.md`, `TARGETS.md`, `docs/PHASE1-SUMMARY.md`, `docs/TAXONOMY.md`) are on no branch yet (checked origin/*
  at 22:00); working from the brief, D-032 as coded in `tools/verso/lane.py`, and the ledger. Board lines were held in
  §Board drafts until `BOARD.md` appeared (Antioch, `r/antioch`, 22:36); now posted on this branch's copy.
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
| 00-base | hb1-14, D-033 terms off | hb1-14 | — | abs: pool econ~ 1.139, win 0.826; gen econ~ 1.111, win 0.689 | — | — | wall 6.89 self 4.62 /1k (pool) | pool 0.9 %, gen 0.6 % | base (the 1.2.3 zero) |
| 01-queen-guard | queen prices its own death +24 material (`queen_guard`) | 00 | queen alive@490 ↑, win ↑ (r500 games), econ ≈ 0/− | +0.008 [−0.008, +0.027] | −0.046 | −0.020 [−0.046] | ±3 % | pool 3.6 %, gen 8.6 % (excl. pocket) | reject |
| 02-queen-nosplit | queen never takes a production split (`queen_nosplit`) | 00 | queen length ↑, queen alive ↑, econ − (fewer births) | −0.036 [−0.056, −0.008] | −0.352 | −0.016 [−0.047]; gen −0.221 | ±4 % | pool 13.3 %, gen 8.7 % (excl. pocket); queen W/L 23/6 | reject |
| 03-queen-guard-nosplit | 01 + 02 stacked (re-run in full on request) | 00 | both | −0.044 [−0.062, −0.016] | −0.343 | pool −0.022 [−0.052]; gen −0.210 [−0.240] | ±3 % | **pool 22.6 %**, gen 11.9 % (excl. pocket); pool queen W/L 37/7 | reject |
| 06-queen-avoid | queen: −40 for a cell an enemy head can reach next turn, −3/cell inside radius 6 of each enemy head, never strikes (`queen_avoid`) | 00 | queen h2h deaths ↓↓, queen alive@490 ↑, econ − small | −0.017 [−0.033, +0.003] | −0.054 | −0.002 [−0.032]; gen +0.013 [−0.012] | ±3 % | pool 2.9 %, gen 23.6 % (excl. pocket); gen queen W/L 33/0 | reject |
| 07-queen-yield | swarm yields to the queen: −20 ending adjacent to the queen's head (−6 at 2) for non-queens; the queen pays the same next to any ally head (`queen_yield`) | 00 | ally-caused queen deaths ↓ (97 of 271 on 06 pool), queen alive ↑, econ ≈ | **+0.029 [+0.011, +0.052]** | −0.064 | +0.003 [−0.025]; gen −0.040 [−0.061] | ±2 % | 0 % both panels (ally kills 62 → 65) | reject (queen unchanged; pool opening gain from spawn spacing, reverses on gen) |
| 08-queen-avoid-guard | 06 + 01 stacked (joint H-Q1 re-test; Kyoto's combined form) | 00 | queen alive ↑ on pool (trap premium covers 06's trapped deaths) | −0.004 [−0.021, +0.020] | −0.050 | pool −0.009 [−0.037]; gen +0.022 [−0.003] | ±5 % | pool 4.7 %, gen 33.3 % (excl. pocket); gen queen W/L 46/0 | reject |
| 09-queen-avoid-yield | 06 + 07 stacked (yield as the repair for 06's ally/trapped deaths; Himeji H3-03) | 00 | queen alive ↑ on pool vs 06 | queued after 03 | | | | | |
| 04-sprint123 | sprint price = max(0, steps − ⌈L/4⌉) in simulator and score (`sprint_rules_123`) | 00 | small: sprints only near threats | −0.001 [−0.003, +0.002] | −0.001 | **+0.040 [+0.016, +0.065]**; gen +0.003 [−0.011] | ±1 % | — | reject (econ lb ≤ 0 only; neutral rules fix; pool win gain does not transfer to twins) |
| 05-free-sprint | on-route 2/3-step moves while foraging when free (`free_sprint`) | 04 | econ ↑ (travel 2×), deaths ≈ | vs 00: +0.001 [−0.003, +0.004]; vs 04: +0.002 [−0.002] | −0.005 | **vs 00 pool +0.045 [+0.019], gen +0.017 [+0.003]**; vs 04 pool +0.005, gen +0.014 [+0.000] | ally body/h2h +5–6 % | — | reject by letter (econ lb only); win-positive on both panels — candidate if the gate is win-led |

## Base re-measured under unswbc 1.2.3 (the new zero; 1,224 games, seeds 1–3, both seats; absolute numbers — no
post-change references published yet)

| Panel | n | win | econ~ | p50 / p100 / p150 / p250 (median, normalised) | units@100 | total@100 | wall / self / ally body / ally h2h per 1k |
|---|---|---|---|---|---|---|---|
| pool | 480 | 0.826 | 1.139 | 1.09 / 1.14 / 1.16 / 1.17 | 1.32 | 1.20 | 6.89 / 4.62 / 1.83 / 1.86 |
| gen | 744 | 0.689 | 1.111 | 1.16 / 1.11 / 1.11 / 1.07 | 1.40 | 1.42 | 2.92 / 2.04 / 0.95 / 0.96 |

Queen (`tools/carthage/queen.py carthage-00-base --maps`): pool — 219 of 480 games reach r490; queen alive at r490
in 2 (0.9 %), queen length at r490 mean 0.1 (15 when alive), queen is the longest own dragon in 0.9 %; the zoo's
queen alive in 3.2 %. Verdicts: elimination 262, longest 199, total 10, **queen 8 (we won 1, lost 7)**. Median queen
death r65; causes wall 170, h2h 146, self 88, body 28. Gen — 157 of 744 reach r490; queen alive 0.6 %; median death
r66, h2h 464 of 633 (gen opponents are hunters). Per map: Portals, Schooltime, Slithery, Trauma (and their gen twins)
are the maps that reach r490 (46–48 of 48); Devil, Dilemma, Trophy never do.

CPU probe (`lane.py cpu`): 00 max 10.83 M points/turn; 05-free-sprint max 11.30 M (limit 30 M), 0 errors.

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
