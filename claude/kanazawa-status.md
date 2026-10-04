# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks). Unit 13 (81ffde51b) was pushed. Last push requested: unit 14 at about 10:03Z (check git.done.json).

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Use `python3` in the VM: `.venv/bin/python` is a Mac symlink. Run `python3 build/kanazawa/tree/tools/kanazawa/q_X.py` from the repo root (it picks up build/s1-pylib).
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not yet on main, then append. As of unit 13, main ef273011b (585 lines) has all kanazawa lines through unit 12; the unit-13 and unit-14 lines (2 + 2) live only on r/kanazawa.
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
- **Unit 14: H-KZ31 (invisibility rule) is falsified.** Only 4/20 cases have an invisible Cb ≥ 4 step, against 15/20 reach-safe ones; the queen is at Cheb 1–3 from the striker in 18/20. At the last turn only the reach veto works.
- Unit 14, cross-lane: in queen strikes the striker is longer than our queen (12/20) or equal (7/20), so Shenzhen's H-SZ34 ("when longer") covers ≤ 1/20 and is complementary to H-KZ26. Its reach min(L−1,3) misses 5/20 vs B(L) 4/20. All 20 strikes were trades.
- Unit 13: H-KZ26 holds at cap 60 (15/20; 14/20 at m=1). Himeji H32-03: in-vision 20/20 is necessary, not sufficient, so H-KZ28 is back to 0.45.
- Unit 12: 15/20 last-turn queen sprint strikes were avoidable; 0/20 queens began the previous round inside the killer's reach. Unit 11: 20/43 of our queen h2h deaths are enemy sprint strikes.
- Earlier: H-KZ12 contract frozen (unit 10); corpse-chain bait (9); tree pockets take 20 % of our queens (6–8); wall deaths are traps (1–5).

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ26** | queen move filter: no step into a visible enemy head's reach B(Le)+m (Cb ≥ 4 fallback), uncapped reach | 0.6 | strike deaths fall < 30 % at m=0, or food/turn −10 % | three-dose screen | Seoul (Rome is on H-KZ12) |
| H-H8 (Himeji) | food-aware reach catches the remaining strikes | 0.45 (our view) | — | after H-KZ26 | Himeji/tester |
| H-KZ28 | strikers act on own vision | 0.45 (down from 0.6, Himeji H32-03: in-vision is necessary, not sufficient) | sufficiency: strike vs ignore rate of visible in-reach queens | corpus | Kanazawa/Himeji |
| H-KZ31 | invisibility rule: keep every enemy head at Chebyshev ≥ 4 | **0.1** (falsified 4/20, unit 14) | — | done | — |
| **H-KZ32** (blue-sky, new) | portal shadow: strikers ignore queens they reach only through portals | 0.2 | ≥ 3 strikes via a portal path with the striker at Cheb ≥ 4 | one corpus pass | Kanazawa |
| H-SZ34 (Shenzhen, our view) | be the mover | complementary to H-KZ26: covers ≤ 1/20 queen strikes; should use B(L) | — | — | Shenzhen |
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

## What changed in unit 14 (4 Oct 09:41–10:00Z)
- **Input.**
  - Himeji ecee82b52: H32-02 (queen-growth adoption) and H32-03 (accepts the cap-60 result; in-vision 20/20 is not sufficiency, so H-KZ28 drops to 0.45). H32-05: Rome's k4 transcripts are recovering, with no table yet.
  - Nara 9dc8bdb6b: C8-01 says ~50 % of ranked round-limit games are queen-decided, so N2 queen-hunting is due. Nara wants veto-firings/1k moves as a first-class column.
  - Shenzhen 2a1d2ea82: H-SZ33 is withdrawn; the h2h trade ledger (sim) shows the mover is shorter and every h2h kills both; H-SZ34 and H-SZ35 are new.
  - Unit 13's push landed (origin/r/kanazawa 81ffde51b). Main is unchanged at ef273011b.
- **Test.** q_invis (frozen 09:50Z): invisible safe step 4/20; killer-only 6/20; invisible and reach-safe 3/20. H-SZ34 coverage and reach form were checked from unit-13 rows.
- **BOARD.** Two lines: one to Shenzhen/testers (H-SZ34 is complementary; use B(L)) and one to Himeji/Nara/Seoul (accept H32-03; H-KZ31 falsified; spec columns).

## Next steps
1. H-KZ28 sufficiency: per enemy L3–5 head with our queen in its vision and in reach, strike rate vs ignore rate. Compare with matched non-queen children, which also covers H-KZ27.
2. H-KZ32 portal shadow corpus pass (portal maps).
3. Replicate H-KZ26 out of sample (`--new`) once fresh queen strikes accumulate.
4. Read Rome's H-KZ12 k4 table when it is published (Himeji H32-05 says transcripts are recovering). Then the H-KZ21 tabu spec, the H-KZ23 child census and the H-KZ25 TIR sim spec.
