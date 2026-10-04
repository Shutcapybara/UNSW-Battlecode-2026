# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not yet on main, then append. As of unit 10, main 21186bf24 has kanazawa lines through unit 8; unit 9–10 lines live only on r/kanazawa.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30 s. Request a push only when git.json is absent. `git fetch` from the VM fails (no credentials); origin refs are as fresh as the keeper's last fetch.
- `git status` inside build/kanazawa/tree hangs (it is not a repo); avoid it. The VM has no `unswbc`: bot runs belong to testers.
- **Corpus split:** pin in-sample to the **first 286** eligible (post-m2, team 7), stride 96. The index grew (291 eligible at 07:15Z: own games are flowing again, a 06:26Z batch). Games after 286 are fresh out of sample (`--new` in q_chain.py). The 192–285 holdout is consumed.
- **Contracts:** C(u→v) is inclusive of v (H24-01). q_forced2 is R[t]/R[t+1] *approximate* legality, not TurnStart (H27-05). Pearl provenance must come from FRAME event origin, never template cells (H27-01).

## Top findings
- **Unit 10: H-KZ12 contract frozen on Himeji D-044 semantics** (body-aware Cb, strict Cb < k, k 0/4/8/16, six-round label by cause), answering Seoul. A one-step veto is mostly forced: 21 % of vetoed moves have an alternative at k=8, so H-KZ12 → 0.6. Ceiling ≈ 15/30 of queen wall deaths. **h2h is our largest queen death cause (43/95).**
- Unit 9: corpse-chain bait (H-KZ20 supported, us-specific). At our queen's first tree-pocket entry, in-pocket pearls are 52 % corpse vs 22 % board-wide. In 10/13 corpse cases the donor is our own length-3 child that died by wall in that pocket.
- Unit 8: weakhold is two scripted queen deaths (16/16). About two-thirds of entries have a terrain-only open alternative; this halves with body awareness (unit 10).
- Units 6–7: tree pockets are terminal (19/19) and pearl-baited (17/19), and take 20 % of our queens.
- Units 2–5: our wall deaths are traps, not culls. Unit 1: sonar is near-universal; 60 % of enemy-head echoes come from beyond vision.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ12** | queen vetoes u→v if Cb < k (frozen D-044 contract) | **0.6** (↓, mostly forced) | queen wall deaths fall < 25 % at k=8, or food/turn falls 10 % | four-dose screen on weakhold | Seoul (requested) |
| **H-KZ24** (new) | our queen's h2h deaths (43/95) are a larger, untouched lever: avoidable contests vs shorter/equal heads | 0.4 | < 1/3 of h2h deaths had a non-contested legal move | corpus pass | Kanazawa (unit 11) |
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

## What changed in unit 10 (4 Oct 07:40–07:50Z)
- **Input.** git.done 07:18 answered the unit-9 push (r/kanazawa 4aca2103c).
  - Seoul ff8fac943 asked Kanazawa and Himeji to reconcile the H-KZ12 contract.
  - Rome b926cdf64: SZ1 cage dose screen HOLD (invalid deaths +8/1k).
  - Himeji f37abdf63 H28: H28-05 weakhold donor born outside the pocket; age > 3 does not falsify 'born trapped'.
- **Test.** q_dose.py is the frozen-contract exposure. Bar (b) failed → H-KZ12 0.6. Ceiling ≈ 50 % of queen wall deaths; h2h is the largest cause.
- **BOARD.** Contract frozen for Seoul; H28-05 accepted; h2h flagged.

## Unit 9 (archived) (4 Oct 07:11–07:20Z; the BOARD lines are stamped 07:35, which is a clock slip)
- **Input.** Main 21186bf24 merged himeji, kanazawa, nara and shenzhen (git.done 06:49 answered my unit-8 push). Himeji d30f065ed (H27):
  - H27-01: the template-cell corpse proxy is invalid (93.8 % proxy vs 52.8 % event-based). Shenzhen retracted its 85–99 % corpse claim at 07:35 (a1d088d33): late income is about half beds, and our corpse loop leaks (31–42 % eaten by the enemy on Around UNSW and Islands). The contradiction is resolved.
  - H27-02: the field's newborns capture more environmental food.
  - H27-05: q_forced2 is not exact (accepted).
  - H27-07: the collector still drops own games per Himeji, but the index now has new team-7 games from 06:26Z.
- Chongqing b50bbe886 withdrew H-C5/H-C6 (sealed, not culled). This agrees with my units 2–5.
- **Test.** q_chain.py, H-KZ20 with event provenance → supported for us. H-KZ22 falsified.
- **BOARD.** Result to Himeji/Rome/Seoul/Osaka; H27-05 acknowledgement to Himeji. Pushed as 4aca2103c (keeper, about 07:18Z). This edit is uncommitted; commit it in unit 10.

## Next steps
1. H-KZ24: size our queen h2h deaths (opponent head length, contest legality, alternative moves) in-sample.
2. H-KZ21 tabu spec: a static (map_hash, u, v) → pocket table plus death-site memory (Himeji's TTL 0/10/30 matches this) for Rome/Seoul.
3. Event-stream TurnStart re-check of the 19+19 entries (H27-05).
4. H-KZ23 child census versus Himeji H-H7; H-KZ25 TIR tail-probe sim spec.
