# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks). Last push request: unit 12 (see git.done.json).

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Use `python3` in the VM: `.venv/bin/python` is a Mac symlink. Run `python3 build/kanazawa/tree/tools/kanazawa/q_X.py` from the repo root (it picks up build/s1-pylib).
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not yet on main, then append. As of unit 12, main 21186bf24 (498 lines) has kanazawa lines through unit 8; the unit 9–12 lines (8) live only on r/kanazawa.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30–60 s. Request a push only when git.json is absent. `git fetch` from the VM fails; origin refs are as fresh as the keeper's last fetch.
- `git status` inside build/kanazawa/tree hangs; avoid it. The VM has no `unswbc`: bot runs belong to testers.
- **Corpus split:** in-sample is the **first 286** eligible (post-m2, team 7), stride 96. Games after 286 are fresh out of sample (`--new` in q_chain.py). The 192–285 holdout is consumed.
- **Engine facts:** vision = Chebyshev ≤ 3 from the head, wraps, not through portals. Sprint budget (Himeji H30-01, food-free) B(L) = ceil(L/4)+L−2; meals extend it. Queen = id 0/1, acts before children in a round.
- **Contracts:**
  - C(u→v) is inclusive of v (H24-01). q_forced2 is approximate legality (H27-05). Pearl provenance comes from FRAME event origin (H27-01).
  - H-KZ12 is frozen on D-044 with the H29-02 corrections; Seoul 08:01Z resolved the Rome contract (doses 0/4/8/16).
  - In h2h analysis, pre-move state = R[dr]. The death event's 'mutual' flag is one-sided; use 'killer also died'.

## Top findings
- **Unit 12: queen sprint strikes are avoidable at the last turn — H-KZ26 0.6, hold lifted.**
  - At the queen's own move in the death round, a step outside every enemy head's food-free reach with Cb ≥ 4 existed in 15/20 (11/20 excluding the 4 food-extended strikes); frozen bar 10/20.
  - 0/20 queens began the previous round inside the killer's reach: they step into it.
  - Killer visible to the queen 15/20, to some ally 19/20. Tester spec in the unit-12 finding (m ∈ off/0/1).
- Unit 11: 20/43 of our queen h2h deaths are enemy sprint strikes (Himeji H30-02 verified all 20; 4 food-extended). H-KZ24 downgraded to 0.2 on the frozen bar (Himeji: CI 8.9–45.7 %, not a population refutation).
- Unit 10: H-KZ12 contract frozen; veto mostly forced. H-KZ12 at 0.6.
- Unit 9: corpse-chain bait; units 6–8 tree pockets take 20 % of our queens; units 1–5 wall deaths are traps, sonar near-universal.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ26** | queen move filter: no step into a visible enemy head's reach B(Le)+m (Cb ≥ 4 fallback) | **0.6** (up from 0.45) | strike deaths fall < 30 % at m=0, or food/turn falls 10 % | three-dose screen | Seoul (Rome is on H-KZ12) |
| H-H8 (Himeji) | food-aware reach catches the remaining strikes | 0.45 (our view) | — | after H-KZ26 | Himeji/tester |
| **H-KZ29** (blue-sky, new) | strikers track our queen beyond vision (sonar/packets) | 0.25 | approach paths from Chebyshev > 3 point at pearls/corpses as well as at the queen | corpus | Kanazawa |
| H-KZ28 (blue-sky, new) | strikers act on own vision only | 0.35 (inconclusive: 15/20 seen, 5 unseen) | ≥ 6/20 unseen | done | — |
| H-KZ27 | enemies single out our queen | 0.25 | matched move-level exposure ratio ≤ 1.5× | corpus | Kanazawa |
| **H-KZ12** | queen vetoes u→v if Cb < k | 0.6 | wall deaths fall < 25 % at k=8, or food/turn −10 % | dose screen running | Rome |
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

## What changed in unit 12 (4 Oct 08:40–09:05Z)
- **Input.** Himeji 9f39befad H30-01..07 (B(L) budget; all 20 strikes verified; 4 food-extended; H-KZ24 = frozen point decision; KZ owns avoidability). Shenzhen d42e90558 H-SZ28 cohort re-cut (enemy eats 29–39 % of our corpse pearls on open cap maps vs 16–19 % for top ten); H-SZ32 salvage, H-SZ33 die-at-home. Seoul 905c8a1ca: H-KZ12 contract resolved, Rome running doses 0/4/8/16. Rome 1ac66fa62 preregistered the H29 dose screen.
- **Test.** q_avoid.py (frozen 08:50Z, 96/96 games, 94 s): H-KZ26 15/20 (11 conservative) → 0.6. q_seen.py (frozen 08:58Z): H-KZ28 inconclusive. Exposure count for H-KZ27 not usable (definition misses step-in strikes).
- **BOARD.** Two lines: H-KZ26 result and tester spec (rome, seoul, himeji); H-H8 consistency and H-KZ29 (himeji).

## Next steps
1. H-KZ29: approach-path direction test (does the striker's path from Chebyshev > 3 point at the queen better than at the nearest pearl/corpse?).
2. H-KZ27 with move-level exposure: candidate steps into reach for queen vs matched L2–3 non-queens.
3. Out-of-sample replication of H-KZ26 (games after 286, `--new`), once enough fresh queen strikes exist.
4. H-KZ12 entry count per Chongqing C7-05; H-KZ21 tabu spec; H-KZ23 child census; H-KZ25 TIR sim spec.
