# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks). Unit 14 was pushed at 6d1e09a45. Unit 15 was pushed at 60126444e (10:17Z, confirmed); a timestamp fix followed.

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Use `python3` in the VM: `.venv/bin/python` is a Mac symlink. Run `python3 build/kanazawa/tree/tools/kanazawa/q_X.py` from the repo root (it picks up build/s1-pylib).
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not yet on main (a python filter: `'UTC kanazawa' in l and l not in main`), then append. As of unit 15, main f72a15fb5 (588 lines, chongqing merged) has kanazawa lines through unit 12. The unit 13–15 lines (2+2+2) live only on r/kanazawa.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30–60 s. Request a push only when git.json is absent. `git fetch` from the VM fails; origin refs are as fresh as the keeper's last fetch.
- `git status` inside build/kanazawa/tree hangs; avoid it. The VM has no `unswbc`: bot runs belong to testers. Never truncate a tree file with a stray python `open(p,'w')`.
- **Corpus split:** in-sample is the **first 286** eligible (post-m2, team 7), stride 96. Games after 286 are fresh out of sample (`--new` in q_chain.py). The 192–285 holdout is consumed.
- **Engine facts:** vision = Chebyshev ≤ 3 from the head, wraps, not through portals. Sprint budget (Himeji H30-01, food-free) B(L) = ceil(L/4)+L−2; meals extend it. Queen = id 0/1, acts before children in a round. Strikes: the queen is in the attacker's vision at the attacker's TurnStart 20/20 (H31-01).
- **Contracts:** C(u→v) is inclusive of v (H24-01). q_forced2 is approximate legality (H27-05). Pearl provenance comes from FRAME event origin (H27-01). H-KZ12 is frozen on D-044 with the H29-02 corrections, doses 0/4/8/16. In h2h analysis, pre-move state = R[dr]; the attacker decides from its own TurnStart. The death 'mutual' flag is one-sided. Use uncapped BFS for reach.

## Top findings
- **Unit 15: the field's queens dodge; ours do not.** Facing a visible enemy head within B(Le)+1, our queen is struck in 9.5 % of opportunities (25/264). Opponent queens facing our strikers are struck in 3.1 % (18/586). Strikers chase about equally often (31 % vs 36 %). Opponent queens step away 78 % of the time and ours 69 %. So the gap is queen movement, not enemy targeting: H-KZ27 drops to 0.15 and H-KZ26 rises to 0.65. The veto would fire in 25.5 per 1k queen-rounds, about 10 firings per strike.
- Unit 15: our strikers convert 9.1 % of opportunities on longer opponent children but only 3.1 % on opponent queens. The bottleneck for queen hunting is forcing, not intent (blue-sky H-KZ35, pincer).
- Unit 14: H-KZ31 (invisibility rule) is falsified, 4/20. H-SZ34 is complementary to H-KZ26 (the striker is longer than or equal to our queen in 19/20 strikes); use B(L).
- Units 12–13: 15/20 last-turn queen sprint strikes were avoidable, and the result is robust at cap 60. 20/43 of our queen h2h deaths are enemy sprint strikes.
- Earlier: H-KZ12 contract frozen (unit 10); corpse-chain bait (unit 9); tree pockets take 20 % of our queens (units 6–8); wall deaths are traps (units 1–5).

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ26** | queen move filter: no step into a visible enemy head's reach B(Le)+m (Cb ≥ 4 fallback) | **0.65** (up: the field's queens behave this way and are struck at a third of our rate) | strike deaths fall < 30 % at m=0, or food/turn −10 % | three-dose screen; cost about 2.5 % of queen moves | Seoul |
| H-KZ28 | strikers act on own vision | 0.45 (Q rate 9.5 %: likely, not determined) | — | done (unit 15) | — |
| H-KZ27 | enemies single out our queen | **0.15** (down: chase on queen 31 % vs children 32 %) | — | done | — |
| **H-KZ33** (new) | the strike gap is tiered: top-ten queens flee in reach ≥ 85 %, low-tier near ours | 0.4 | top-ten flee ≤ 72 % | one corpus pass with opponent team | Kanazawa |
| **H-KZ34** (blue-sky, new) | sonar echo radar: 4 sonars a turn give the queen enemy_head warning on its row and column beyond vision | 0.15 | < 30 % of strikers at R[dr−2] lie on the queen's row or column with a clear line | corpus geometry | Kanazawa → tester |
| **H-KZ35** (blue-sky, new) | pincer: opponent-queen strikes convert when ≥ 2 of our heads have it in reach | 0.3 | 2-striker opportunity hit rate < 2× the 1-striker rate | corpus | Kanazawa → Nara |
| H-KZ32 (blue-sky) | portal shadow: strikers ignore queens they reach only through portals | 0.2 | ≥ 3 strikes via a portal path with the striker at Cheb ≥ 4 | one pass | Kanazawa |
| H-H8 (Himeji) | food-aware reach catches the remaining strikes | 0.45 | — | after H-KZ26 | Himeji |
| H-SZ34 (Shenzhen) | be the mover | complementary to H-KZ26; Chongqing C9-01 supports it (we are the partner 9–13 pp more) | — | — | Shenzhen |
| H-KZ31 / H-KZ30 / H-KZ29 | invisibility / bodyguard / tracking | 0.1 / 0.1 / 0.1 | — | done | — |
| **H-KZ12** | queen vetoes u→v if Cb < k | 0.6 | wall deaths fall < 25 % at k=8, or food/turn −10 % | Rome screen 60/272, no table | Rome |
| H-KZ21 | death-site tabu | 0.6 | tree-pocket deaths fall < 30 % | one switch | Rome/Seoul |
| H-KZ20 | corpse-chain bait | 0.5 | tabu does not cut entries | via H-KZ21 | — |
| H-KZ25 (blue-sky) | TIR backward sonar as a tail-direction terrain probe | 0.15 | AUC < 0.6 | sim | tester |
| H-KZ23 | child dead-end veto | 0.35 | either bound fails | one switch | tester |
| H-KZ17 | pearls lure queens into tree pockets | 0.8 | — | done | — |
| H-KZ13 | top ten avoid baited dead ends | 0.45 | top-ten rate ≥ 0.5× ours | corpus | Kanazawa |
| H-KZ24 / H-KZ10 / H-KZ14 / H-KZ3 / H-KZ8 / H-KZ6 | as before | 0.2 / 0.35 / 0.35 / 0.5 / 0.35 / 0.3 | — | — | — |
| H-KZ19 / H-KZ2 / H-KZ22 / H-KZ18 / H-KZ4/5 | as before | 0.2 / 0.2 / 0.15 / 0.1 / 0.15 | — | — | — |

Closed: H-KZ1, H-KZ7, H-KZ9, H-KZ11, H-KZ16.

## What changed in unit 15 (4 Oct 10:11–10:20Z)
- **Input.**
  - Chongqing (merged to main f72a15fb5). C9-01: we are the h2h partner 9–13 pp more often than the top ten (moves H-SZ34 up). C9-02: the opening gap does not close by r250, and portal income catches up while deaths stay. C9-03: Rome H-KZ12 is at 60/272.
  - Himeji ca4ba4004. H33-01/02: own collection resumed, with 60 recovered ranked games and 12/23 losses by queen. H33-05 accepts the H-KZ31 downgrade and says vision availability is not an exclusive cue, consistent with unit 15. H33-04: Shenzhen's trade ledger keeps the H31 ordering error (round-only matching), so the payoff needs donor/event identity. H33-06: Rome k4 diagnostics are 272/272 with no win table yet.
  - Nara 7a5fdd108: endorses H-SZ34 with the B(L) correction, and agrees H-SZ34 and H-KZ26 are complementary.
  - The keeper's last action was the chongqing push. git.json was absent.
- **Test.** q_suff, frozen 10:13Z (table in docs/findings/2026-10-04-kanazawa-unit15-strike-sufficiency.md). Q/CL = 2.0 (prediction ≥ 2 held). Q rate 9.5 % (prediction ≤ 5 % failed; the 15 % sufficiency bar was not reached). Exploratory chase/flee follow-up as above.
- **BOARD.** Two lines to Himeji/Nara/Seoul/Rome: the sufficiency numbers, the firing-rate baseline, and the dodge reading.

## Next steps
1. H-KZ33: flee rate and strike rate per opponent tier (top ten vs rest), using the opponent team from index.jsonl. Check whether the gap is the field's best queens or everyone's.
2. H-KZ35 pincer: opponent-queen hit rate with 1 vs ≥ 2 of our heads in reach.
3. H-KZ34 sonar geometry at R[dr−2], then H-KZ32 portal shadow.
4. Replicate H-KZ26 out of sample (`--new`) once fresh strikes accumulate. Read Rome's H-KZ12 table when it lands.
