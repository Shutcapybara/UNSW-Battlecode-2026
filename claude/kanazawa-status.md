# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- Repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the parent folder `Projects` is the connected folder; the worktrees `wt-*` sit beside it). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as main's BOARD plus every kanazawa line not yet on main, then append. Unit 2 re-inserted the three 03:00 lines because r/kanazawa wasn't merged into main yet.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- The VM has no `unswbc` on PATH: bot runs belong to testers. Corpus reads: `tools/analysis/features/frame.decode`; 60 games in 67 s with 4 jobs.
- `rounds[r]` = state at the start of round r, `{id: (team, body head-first)}`; `nbr[cell]` = (N,E,S,W), None = kelp.

## Top findings
- **Unit 2: our wall deaths are trapped dragons, not culls (contradicts Chongqing C3-01/H-C5).** 87 % of 3,620 post-m2 team-7 wall deaths had no free neighbour; 97 % of trapped deaths go north because of the DEAD tie-break (`{0}` first); the queen was trapped in 17/17. carthage-05 has no fatal move before the feeder branch (r ≈ 412). H-C5 as worded would be a no-op. The cause is queen splits with no parent-exit check → H-KZ6.
- **Unit 2:** Nara's weakhold "exception" compared the wrong file (stronghold.map). maps/live has 2 issues, not 3.
- Unit 1: sonar is near-universal (96 % of sides); 60 % of enemy-head echoes come from beyond vision. Echoes could be a long-range sensor that nobody uses.
- Unit 1: H-SZ23 evidence is cross-sectional. Shenzhen adopted my event-study falsifier (03:40).

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| H-KZ1 | sonar volume does not mark skill | — | closed as a fact | done | — |
| H-KZ2 (blue-sky) | rotating one-ray echoes find the enemy queen before vision does | 0.2 | bearing before first sight < 20 % | 12 sim games | Claude tester |
| H-KZ3 | H-SZ23's length→hazard drop is mostly selection | 0.5 | event study hazard ratio < 0.7 | corpus pass | Shenzhen (adopted) |
| H-KZ4 (blue-sky) | a foreign packet means an enemy ray ended on us (danger cue) | 0.15 | P(death ≤ 10 r \| foreign) ≤ 1.5× base | payload decode | Kanazawa |
| H-KZ5 (blue-sky) | some opponents trust unauthenticated payloads (injection) | 0.1 | all formats authenticated | payload decode | Kanazawa |
| **H-KZ6** | a queen split needs a parent exit (≥ 1 free cell + flood) → queen alive@RL-end up on Trauma/Portals/Maze/weakhold | 0.6 | alive < 0.15 or units guard fails | one switch, LIVE_MAPS_M2 + gen s1–3 | Rome/Seoul |
| H-KZ7 | part of the 13 % free-cell wall deaths are bot-model errors | 0.3 | id-ordered in-round re-sim leaves every cell occupied | corpus pass | Kanazawa |
| H-KZ8 (blue-sky) | aiming trapped deaths (toward ally heads) raises corpse recovery | 0.3 | Δcorpse share < +0.03 | one switch | tester |

## What changed in unit 2 (4 Oct 04:00–04:15Z)
- Push of b196f9d29 confirmed (origin/r/kanazawa). D-043 acknowledged.
- `tools/kanazawa/q_trap.py`, finding `docs/findings/2026-10-04-kanazawa-unit2-trapped-not-culled.md`, five BOARD lines (D-043 ack, C3-01 contradiction, H-KZ6 request, weakhold reconciliation).

## Next steps
1. Watch for Chongqing's reply and for the first tester taking H-KZ6. If H-C5 gets run literally anyway, read it as a no-op check.
2. H-KZ7: id-ordered in-round occupancy re-sim on the 466 free-cell deaths.
3. Sonar payload decode (H-KZ4/H-KZ5).
4. Contradiction ledger: Shenzhen live transit gap vs Himeji H18-03; Himeji H20-02's denominators (40 % vs 20 %) vs the brief's "70 of 72".
5. Blue-sky: portal and wraparound escape routes for a boxed queen.
