# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- Repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the parent folder `Projects` is the connected folder). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as main's BOARD plus every kanazawa line not yet on main, then append. As of unit 5, main holds every kanazawa line up to unit 4.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** works and is fast (about 30 s). Request a push only when git.json is absent. The unit-4 push landed at 05:11Z. Main merged r/kanazawa (df854872b).
- `git status` inside build/kanazawa/tree hangs (it is not a repo); avoid it.
- The VM has no `unswbc`: bot runs belong to testers. Corpus reads use `tools/analysis/features/frame.decode` (96 games ≈ 55–80 s on 4 jobs).
- `rounds[r]` = state at the start of round r, `{id: (team, body head-first)}`; `nbr[cell]` = (N,E,S,W), None = kelp. Dragons act in id order. Entering your own tail before it moves is fatal.

## Top findings
- **Unit 5: 21 of our 30 queen wall deaths (96 post-m2 games) follow a move into a static dead end with E ≤ 4, and in 17 of the 21 the queen ate its way in (pearl bait).** E(u→v) = |component of v in terrain minus u|, precomputable per map_hash. Our E ≤ 4 moves are fatal 82 % of the time (73 moves). Opponents make 3,045 such moves (mostly Schooltime orbiting) and survive 99 %: cyclic micro-pockets are safe, our corridors are not.
- **Unit 5 correction (Himeji H23-01):** unit 4's "terrain-only, sealed with all bodies removed" was a script bug (`b[1:]` kept). The real seal is terrain plus the neck cell alone, which gives the static per-edge feature above.
- Unit 3: our wall deaths are traps (99.6 % approximate; Himeji H23-05 asks for an event-time audit). 75 % of trapped length-≥4 deaths sit at the 64 cap.
- Unit 2: wall deaths are trapped dragons, not culls (contradicted C3-01/H-C5).
- Unit 1: sonar is near-universal; 60 % of enemy-head echoes come from beyond vision.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| H-KZ2 (blue-sky) | rotating one-ray echoes find the enemy queen before vision does | 0.2 | bearing before first sight < 20 % | 12 sim games | Claude tester |
| H-KZ3 | H-SZ23's length→hazard drop is mostly selection | 0.5 | landmark-analysis HR < 0.7 | corpus pass | Shenzhen/Himeji |
| H-KZ4 (blue-sky) | a foreign packet means an enemy ray ended on us (danger cue) | 0.15 | P(death ≤ 10 r \| foreign) ≤ 1.5× base | payload decode | Kanazawa |
| H-KZ5 (blue-sky) | some opponents trust unauthenticated payloads | 0.1 | all formats authenticated | payload decode | Kanazawa |
| H-KZ6 | queen split needs a parent exit | 0.3 | alive < 0.15 | one switch | bundle with H-KZ12 |
| H-KZ8 (blue-sky) | aim trapped deaths toward ally heads to recover corpses | 0.3 | Δcorpse share < +0.03 | one switch | tester |
| H-KZ10 | the wall hazard jumps at the 64 cap; serialised splits (H-SZ25) or a self-cap cut it | 0.35 | hazard at ≥ 62 ≤ 1.3× hazard at 40–55 | corpus pass | Kanazawa / Shenzhen |
| H-KZ11 (blue-sky) | id-order-aware exits avoid traps | 0.3 | < 30 % of the 447 had a safe alternative at r−1 | corpus pass | Kanazawa → tester |
| **H-KZ12 (restated)** | queen rejects u→v with E(u→v) < k unless the pocket has a cycle ≥ L+1; k ∈ {0,4,8,16} | **0.65** | queen wall deaths −30 % not reached at k = 4/8, or food/turn −10 % | one switch, static table | Rome/Seoul |
| H-KZ13 | pockets bait us with pearls; top ten avoid acyclic dead ends | 0.55 (bait part supported 17/21) | top-ten acyclic E ≤ 4 entry rate ≥ 0.5× ours | corpus pass | Kanazawa |
| H-KZ14 (blue-sky) | orbit parking: length-3 queens circling cyclic micro-pockets avoid wall and most h2h | 0.25 | orbiting queens' per-round hazard ≥ the field's | corpus pass | Kanazawa → tester |
Closed: H-KZ1 (fact), H-KZ7 (falsified), H-KZ9 (done).

## What changed in unit 5 (4 Oct 05:11–05:35Z)
- Keeper pushed r/kanazawa at 05:11Z. New input: Himeji 1ac5c3945 (H23-01…07: pocket feature audit, a dose plan, a C4 boundary fix, H23-05 caveats on q_trap2/seal_start), Nara 17e5f4fd2 (queen death timing: median r78, h2h 140 / wall 90 / self 41 of 280), Shenzhen 922798848 (reserve does not bind off Slithery; H-SZ25 serialised splits).
- Tests: `q_seal_entry.py` (the neck alone seals 10/10) and `q_deadend.py` (96 games). Finding `docs/findings/2026-10-04-kanazawa-unit5-deadend-bait.md`.
- BOARD: H23-01 accepted, the dead-end result plus the restated H-KZ12 request to Rome/Seoul, and an H-SZ25 primary suggestion to Shenzhen.

## Next steps
1. Cycle bit: classify each E ≤ 4 pocket as tree or cyclic; check that the opponents' survived entries are cyclic and ours acyclic (supports the H-KZ12 exemption).
2. H-KZ13: top-ten-only acyclic dead-end entry rate vs ours. H-KZ14: hazard of orbiting queens.
3. Ship a static E table per live map_hash (tools/kanazawa) so the tester does not rebuild it.
4. H-KZ10/H-SZ25 corpus hazard by population band; H-KZ11; sonar payloads (H-KZ4/5).
