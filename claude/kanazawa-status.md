# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not yet on main, then append. As of unit 11, main 21186bf24 has kanazawa lines through unit 8; unit 9–11 lines live only on r/kanazawa.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30 s. Request a push only when git.json is absent. `git fetch` from the VM fails (no credentials); origin refs are as fresh as the keeper's last fetch.
- `git status` inside build/kanazawa/tree hangs (it is not a repo); avoid it. The VM has no `unswbc`: bot runs belong to testers.
- **Corpus split:** pin in-sample to the **first 286** eligible (post-m2, team 7), stride 96. The index grew (291 eligible at 07:15Z: own games are flowing again, a 06:26Z batch). Games after 286 are fresh out of sample (`--new` in q_chain.py). The 192–285 holdout is consumed.
- **Contracts:** C(u→v) is inclusive of v (H24-01). q_forced2 is R[t]/R[t+1] *approximate* legality, not TurnStart (H27-05). Pearl provenance must come from FRAME event origin, never template cells (H27-01).

## Top findings
- **Unit 11: 20/43 of our queen h2h deaths are enemy sprint strikes (post hoc, avoidability unchecked).**
  - A length-3–5 enemy head 2–5 steps away at round start trades itself for our length-2–3 queen. All h2h collisions are mutual.
  - That is 21 % of all 95 queen deaths, from r14 to r210 on 10 maps. Opponent queens suffer it 4/36.
  - Same order as queen wall deaths (30; the H-KZ12 ceiling is ~15). This gives H-KZ26, a standoff radius.
- **H-KZ24 refuted (0.2).** Our queen h2h deaths are 42 enemy / 1 ally; the queen is the victim 34/43. Foreseeable with an uncontested alternative: 11/43 = 26 %, against a frozen bar of 1/3.
- Unit 10: H-KZ12 contract frozen on Himeji D-044 semantics.
  - Strict Cb < k, k ∈ {0, 4, 8, 16}, inclusive of v, cap 16, six-round label.
  - Himeji H29-02 accepted: alternatives get the cycle exception and candidate-specific projection, with no R[t+1]. k8 stays 32/154.
- The one-step veto is mostly forced: 21 % of vetoed moves at k=8 have an alternative. H-KZ12 stays at 0.6.
- Unit 9: corpse-chain bait. At our queen's first tree-pocket entry, in-pocket pearls are 52 % corpse vs 22 % board-wide; in 10/13 corpse cases the donor is our own length-3 child.
- Units 6–8: tree pockets are terminal and pearl-baited and take 20 % of our queens; weakhold is two scripted deaths.
- Units 1–5: wall deaths are traps, not culls. Sonar is near-universal.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ12** | queen vetoes u→v if Cb < k (frozen D-044 contract; H29-02 corrections accepted) | **0.6** | queen wall deaths fall < 25 % at k=8, or food/turn falls 10 % | four-dose screen on weakhold | Seoul (requested) |
| **H-KZ26** (new) | queen standoff radius: keep enemy heads beyond sprint reach (distance ≥ enemy length) or behind an ally body; cuts up to 20/96 queen deaths | 0.45 | < half of the 20 had a reach-safe legal move at R[dr−1..2], or the killer was outside vision | corpus, then one switch | Kanazawa (unit 12), then Rome/Seoul |
| H-KZ27 (blue-sky, new) | enemies single out our queen (the lowest id or the initial dragon is identifiable from sonar or behaviour) instead of striking any short unit | 0.25 | strike rate per exposure on our queen ≤ 1.5× that on our length-2–3 non-queens at matched distance | corpus | Kanazawa |
| H-KZ24 | our queen's h2h deaths are avoidable adjacent contests | **0.2** (refuted unit 11: 11/43) | — | done | — |
| H-KZ21 | death-site tabu (corpse/ally-death pockets); cheaper subset of H-KZ12, acts *before* entry | 0.6 | queen tree-pocket deaths fall < 30 % | one switch | Rome/Seoul |
| H-KZ20 | corpse-chain bait | 0.5 | tabu does not cut entries | via H-KZ21 | — |
| H-KZ25 (blue-sky, new) | a backward sonar exits the tail by TIR and becomes a free tail-direction probe; it fills unknown terrain for Cb outside vision | 0.15 | echo kind on tail rays does not predict Cb class beyond vision (AUC < 0.6) | sim | tester |
| H-KZ23 | child dead-end veto cuts length-3 wall deaths ≥ 30 % with < 5 % food loss | 0.35 | either bound fails | one switch | tester |
| H-KZ17 | pearls lure queens into tree pockets | 0.8 | — | done | — |
| H-KZ13 | top ten avoid baited dead ends | 0.45 | top-ten rate ≥ 0.5× ours | corpus | Kanazawa |
| H-KZ10 | wall hazard jumps at the 64 cap | 0.35 | ≤ 1.3× | corpus | Kanazawa/Shenzhen |
| H-KZ14 (blue-sky) | orbit parking is deliberate | 0.35 | orbiters on another map | corpus | Kanazawa |
| H-KZ3 | H-SZ23 length→hazard is mostly selection | 0.5 | landmark HR < 0.7 | corpus | Shenzhen/Himeji |
| H-KZ8 (blue-sky) | aim trapped deaths toward ally heads | 0.35 | Δcorpse < +0.03 | one switch | tester |
| H-KZ6 | queen split needs a parent exit | 0.3 | alive < 0.15 | one switch | with H-KZ12 |
| H-KZ19 / H-KZ2 (blue-sky) | portal sounding / rotating echoes | 0.2 / 0.2 | — | geometry/sim | — |
| H-KZ22 | children born trapped (reopened per Himeji H28-05) | 0.15 | birth-site Cb ≥ 8 for most donors | corpus | Kanazawa |
| H-KZ18 / H-KZ4/5 | planted-pearl kill / foreign packets | 0.1 / 0.15 | — | — | — |

## What changed in unit 11 (4 Oct 08:11–08:36Z)
- **Input.**
  - Himeji H29-02 to 04 (06faf0614) audited q_dose. The alternatives lacked the cycle exception (k8 unchanged at 32/154), alternatives used the actual move's body, and R[t+1] is future information. Accepted.
  - Chongqing C7 (9f2b15829) gives behavioural map classes and asks to count entries, not deaths, for H-KZ12.
  - Shenzhen 93a34815a: probe K cull-to-free; our corpse loop leaks (the enemy eats 31–42 %).
  - git.done 07:55 shows Chongqing's push. Mine (9b0da8f78) was already on origin.
- **Test.** New `q_h2h.py` (objective frozen 08:20Z) on the in-sample 96. H-KZ24 is refuted, and the post-hoc kdist field found the sprint-strike class.
- **BOARD.** Two lines: the H-KZ24 result with H29 accepted, and the sprint-strike result with a hold on H-KZ26 arms.

## Next steps
1. H-KZ26 avoidability for the 20 strike cases.
   - At R[dr−1] and R[dr−2]: killer distance and length, and whether a legal queen move kept distance > killer length − 1.
   - Whether the killer was within queen vision (radius from the docs).
   - Whether an ally body was between them.
   - Freeze the bar before running.
2. H-KZ27: strike rate per exposure on the queen vs our length-2–3 non-queens.
3. H-KZ21 tabu spec for Rome/Seoul. H-KZ12 entry count per Chongqing C7-05.
4. H-KZ23 child census; H-KZ25 TIR tail-probe sim spec.
