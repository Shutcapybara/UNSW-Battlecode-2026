# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- Repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the parent folder `Projects` is the connected folder). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as main's BOARD plus every kanazawa line not yet on main, then append (unit 3 did this in a python snippet).
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** the unit-2 push request (9aea2e7e1) was still pending in git.json at 04:25Z. The keeper's last run hit a `git fetch` timeout (03:53Z). A pending request pushes the branch ref, so later commits ride along. Do not overwrite a pending git.json.
- The VM has no `unswbc`: bot runs belong to testers. Corpus reads use `tools/analysis/features/frame.decode` (60 games ≈ 55–65 s on 4 jobs).
- `rounds[r]` = state at the start of round r, `{id: (team, body head-first)}`; `nbr[cell]` = (N,E,S,W), None = kelp. Dragons act in id order. Entering your own tail before it moves is fatal.

## Top findings
- **Unit 3: our wall deaths are 99.6 % traps (H-KZ7 falsified in substance).** Of 3,620 wall deaths, only 13 had a legal free cell at move time. 447 cells were filled earlier in the round by lower-id movers, and in 85 cases the "free" cell was the dragon's own tail. 75 % of the length-≥4 trapped deaths happen at the 64-dragon cap, so a split was not available. The lever is upstream: H-KZ6 and H-KZ11.
- **Unit 2: wall deaths are trapped dragons, not culls (contradicts Chongqing C3-01/H-C5).** The queen was trapped in 17/17 cases, and the DEAD tie-break sends dragons north. The cause is queen splits with no parent-exit check → H-KZ6.
- Unit 2: Nara's weakhold "exception" compared the wrong file. Himeji H21-01 independently agrees (04:06Z).
- Unit 1: sonar is near-universal, and 60 % of enemy-head echoes come from beyond vision (an unused long-range sensor).
- Unit 1→3: H-SZ23 evidence is cross-sectional. Himeji H21-03 correctly notes that my event-study falsifier has immortal-time bias. Use landmark analysis instead.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| H-KZ1 | sonar volume does not mark skill | — | closed as a fact | done | — |
| H-KZ2 (blue-sky) | rotating one-ray echoes find the enemy queen before vision does | 0.2 | bearing before first sight < 20 % | 12 sim games | Claude tester |
| H-KZ3 | H-SZ23's length→hazard drop is mostly selection | 0.5 | landmark-analysis HR < 0.7 (Himeji H21-03 design) | corpus pass | Shenzhen/Himeji |
| H-KZ4 (blue-sky) | a foreign packet means an enemy ray ended on us (danger cue) | 0.15 | P(death ≤ 10 r \| foreign) ≤ 1.5× base | payload decode | Kanazawa |
| H-KZ5 (blue-sky) | some opponents trust unauthenticated payloads | 0.1 | all formats authenticated | payload decode | Kanazawa |
| **H-KZ6** | a queen split needs a parent exit → queen alive@RL-end up | 0.65 | alive < 0.15 or units guard fails | one switch | Rome/Seoul |
| H-KZ7 | free-cell wall deaths are bot-model errors | 0.02 (falsified: 13/3,620) | — | done | — |
| H-KZ8 (blue-sky) | aim trapped deaths toward ally heads to recover corpses | 0.3 | Δcorpse share < +0.03 | one switch | tester |
| H-KZ9 | split instead of dying when trapped | 0.1 (small: ≤ 1–2/game, cap blocks 75 %) | — | done | — |
| H-KZ10 | the wall hazard per dragon-round jumps at the 64 cap (crowding); a self-cap near 48 cuts deaths | 0.3 | hazard at ≥ 62 ≤ 1.3× hazard at 40–55, same maps | corpus pass | Kanazawa |
| H-KZ11 (blue-sky) | id-order-aware exits (net of cells lower ids can reach first) avoid traps | 0.3 | < 30 % of the 447 had a safe alternative at r−1 | corpus pass | Kanazawa → Claude tester |

## What changed in unit 3 (4 Oct 04:10–04:30Z)
- `tools/kanazawa/q_trap2.py` (id-ordered re-sim) and finding `docs/findings/2026-10-04-kanazawa-unit3-id-ordered-resim.md`.
- Two BOARD lines: H21-03 accepted (to Himeji/Shenzhen), and the H-KZ7 result (to Chongqing/Rome/Seoul/director).
- New input: Himeji c0c05c743 (H21-01…07). No other lane moved since unit 2. No reply yet from Chongqing.

## Next steps
1. Watch git.done.json for the r/kanazawa push. The keeper's fetch timed out at 03:53Z; if it is still stuck at about 05:10Z, notify.
2. H-KZ10: wall hazard per dragon-round by team population band.
3. H-KZ11: at r−1 for the 447 lower-mover traps, was there a move with ≥ 2 exits that no lower id could reach?
4. Sonar payload decode (H-KZ4/H-KZ5). Contradiction ledger: Shenzhen live transit gap vs Himeji H18-03.
5. Blue-sky: portal and wraparound escape routes for a boxed queen.
