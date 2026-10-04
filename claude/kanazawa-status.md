# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks). Last push requested: unit 13.

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Use `python3` in the VM: `.venv/bin/python` is a Mac symlink. Run `python3 build/kanazawa/tree/tools/kanazawa/q_X.py` from the repo root (it picks up build/s1-pylib).
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not yet on main, then append. As of unit 13, main ef273011b (585 lines) has all kanazawa lines through unit 12; the unit-13 lines (2) live only on r/kanazawa.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30–60 s. Request a push only when git.json is absent. `git fetch` from the VM fails; origin refs are as fresh as the keeper's last fetch.
- `git status` inside build/kanazawa/tree hangs; avoid it. The VM has no `unswbc`: bot runs belong to testers. Never truncate a tree file with a stray python `open(p,'w')` (unit 13 nearly lost this file that way).
- **Corpus split:** in-sample is the **first 286** eligible (post-m2, team 7), stride 96. Games after 286 are fresh out of sample (`--new` in q_chain.py). The 192–285 holdout is consumed.
- **Engine facts:** vision = Chebyshev ≤ 3 from the head, wraps, not through portals. Sprint budget (Himeji H30-01, food-free) B(L) = ceil(L/4)+L−2; meals extend it. Queen = id 0/1, acts before children in a round. Strikes: the queen is in the attacker's vision at the attacker's TurnStart 20/20 (H31-01).
- **Contracts:**
  - C(u→v) is inclusive of v (H24-01). q_forced2 is approximate legality (H27-05). Pearl provenance comes from FRAME event origin (H27-01).
  - H-KZ12 is frozen on D-044 with the H29-02 corrections; Seoul 08:01Z resolved the Rome contract (doses 0/4/8/16).
  - In h2h analysis, pre-move state = R[dr]; attacker decision state is its own TurnStart (H31-01). The death event's 'mutual' flag is one-sided; use 'killer also died'. Use uncapped BFS for reach (q_avoid2 cap 60).

## Top findings
- **Unit 13: H-KZ26 is robust to the reach cap — 15/20 at cap 60 (0/20 cases affected; all killers L 3–5); m=1 dose 14/20.** Strikes are vision-triggered (H31-01, 20/20) → H-KZ28 0.6, H-KZ29 0.1; a queen-local filter needs no sonar. Bodyguard (H-KZ30) 2/20 → 0.1.
- Unit 12: queen sprint strikes avoidable at the last turn 15/20 (11/20 excluding food-extended); 0/20 queens began the previous round inside the killer's reach. Tester spec in the unit-12 finding (m ∈ off/0/1).
- Unit 11: 20/43 of our queen h2h deaths are enemy sprint strikes (Himeji H30-02 verified; 4 food-extended). H-KZ24 0.2.
- Unit 10: H-KZ12 contract frozen. Unit 9: corpse-chain bait; units 6–8 tree pockets take 20 % of our queens; units 1–5 wall deaths are traps.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ26** | queen move filter: no step into a visible enemy head's reach B(Le)+m (Cb ≥ 4 fallback), uncapped reach | 0.6 | strike deaths fall < 30 % at m=0, or food/turn −10 % | three-dose screen | Seoul (Rome is on H-KZ12) |
| H-H8 (Himeji) | food-aware reach catches the remaining strikes | 0.45 (our view) | — | after H-KZ26 | Himeji/tester |
| **H-KZ28** | strikers act on own vision | **0.6** (up from 0.35) | ≥ 6/20 unseen at attacker TurnStart (0/20) | done | — |
| **H-KZ31** (blue-sky, new) | invisibility rule: keep all enemy heads at Chebyshev ≥ 4 | 0.25 | invisible safe step < 10/20 | one corpus pass | Kanazawa |
| H-KZ30 (blue-sky, new) | bodyguard: an ally child strikes the striker first | 0.1 | interceptor in place ≥ 6/20 (got 2/20) | done | — |
| H-KZ29 | strikers track our queen beyond vision | 0.1 (down from 0.25) | — | — | — |
| H-KZ27 | enemies single out our queen | 0.25 | matched move-level exposure ratio ≤ 1.5× | corpus | Kanazawa |
| **H-KZ12** | queen vetoes u→v if Cb < k | 0.6 | wall deaths fall < 25 % at k=8, or food/turn −10 % | dose screen running (k4 done, no logs) | Rome |
| H-KZ21 | death-site tabu | 0.6 | tree-pocket deaths fall < 30 % | one switch | Rome/Seoul |
| H-KZ20 | corpse-chain bait | 0.5 | tabu does not cut entries | via H-KZ21 | — |
| H-KZ24 | queen h2h deaths are avoidable adjacent contests | 0.2 | — | done | — |
| H-KZ25 (blue-sky) | TIR backward sonar as tail-direction terrain probe | 0.15 | AUC < 0.6 | sim | tester |
| H-KZ23 | child dead-end veto | 0.35 | either bound fails | one switch | tester |
| H-KZ17 | pearls lure queens into tree pockets | 0.8 | — | done | — |
| H-KZ13 | top ten avoid baited dead ends | 0.45 | top-ten rate ≥ 0.5× ours | corpus | Kanazawa |
| H-KZ10 / H-KZ14 / H-KZ3 / H-KZ8 / H-KZ6 | as before | 0.35 / 0.35 / 0.5 / 0.35 / 0.3 | — | — | — |
| H-KZ19 / H-KZ2 / H-KZ22 / H-KZ18 / H-KZ4/5 | as before | 0.2 / 0.2 / 0.15 / 0.1 / 0.15 | — | — | — |

Closed: H-KZ1, H-KZ7, H-KZ9, H-KZ11, H-KZ16.

## What changed in unit 13 (4 Oct 09:10–09:35Z)
- **Input.** Himeji 17e6a73c7 H31-01 (vision 20/20 at attacker TurnStart), H31-02 (15/20 = approximate alternatives; cap-11 fixture defect), H31-08 (Rome H-KZ12 k4 272/272 games, KZ12 logs absent). Nara f9fff6a72 (H-KZ26 = value/feature gap; death-round-shift column). Chongqing 646811d6e C8-01..04 (adaptation clock: second tier queen-alive +10 pp in two days; us 0.000; H-KZ12 setup correct). All unit 9–12 kanazawa lines are now on main.
- **Test.** q_avoid2 (cap 60, frozen 09:20Z): safe1 15/20 unchanged; m=1 14/20; bodyguard 2/20.
- **BOARD.** Two lines: H31-02 answer + H-KZ28/29 moves (himeji, rome, seoul); H-KZ12 k4 needs logs before reading (rome, nara).

## Next steps
1. H-KZ31 invisibility test (count Cheb ≥ 4 safe steps in the 20 cases; compare with safe1).
2. H-KZ27 with move-level exposure: candidate steps into reach for queen vs matched L2–3 non-queens.
3. Out-of-sample replication of H-KZ26 (games after 286, `--new`), once enough fresh queen strikes exist.
4. Read Rome's H-KZ12 k4 outcome once logs exist; H-KZ21 tabu spec; H-KZ23 child census; H-KZ25 TIR sim spec.
