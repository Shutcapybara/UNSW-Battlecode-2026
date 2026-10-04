# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not yet on main, then append. As of unit 9, main 21186bf24 has all kanazawa lines through unit 8.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30 s. Request a push only when git.json is absent. `git fetch` from the VM fails (no credentials); origin refs are as fresh as the keeper's last fetch.
- `git status` inside build/kanazawa/tree hangs (it is not a repo); avoid it. The VM has no `unswbc`: bot runs belong to testers.
- **Corpus split:** pin in-sample to the **first 286** eligible (post-m2, team 7), stride 96. The index grew (≥ 296 eligible at 07:30Z: own games are flowing again, a 06:26Z batch). Games after 286 are fresh out of sample (`--new` in q_chain.py). The 192–285 holdout is consumed.
- **Contracts:** C(u→v) is inclusive of v (H24-01). q_forced2 is R[t]/R[t+1] *approximate* legality, not TurnStart (H27-05). Pearl provenance must come from FRAME event origin, never template cells (H27-01).

## Top findings
- **Unit 9: corpse-chain bait (H-KZ20 supported, us-specific).** At our queen's first tree-pocket entry, in-pocket pearls are 52 % corpse vs 22 % board-wide. In 13/19 entries there is a corpse pair, and in 10 of those the donor is our own length-3 child that died by wall in that pocket (median age 9, median 20 rounds earlier). Opponents are near base (35 % vs 24 %). Fresh games: 3/3. Weakhold r40 is this chain (sibling dies at r20).
- Unit 8: weakhold is two scripted queen deaths (16/16, won 1/16): r40 is a corpse-chain plus open exit, r24 is sealed upstream. About two-thirds of our tree entries have a legal open alternative (approximate legality).
- Unit 7: tree-pocket entries are pearl-baited (17/19).
- Unit 6: tree pockets are terminal (19/19) and take 20 % of our queens.
- Units 2–5: our wall deaths are traps, not culls; 75 % of trapped long deaths occur at the 64 cap.
- Unit 1: sonar is near-universal; 60 % of enemy-head echoes come from beyond vision.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ12** | queen vetoes u→v if C ≤ k and P+u has no cycle ≥ L+1 | **0.8** | queen trap deaths do not fall 30 %, or food/turn falls 10 % | one switch; weakhold first | Rome/Seoul |
| **H-KZ21** (new) | death-site tabu: the queen avoids acyclic pockets holding a corpse pearl or where an ally died. Cheaper subset of H-KZ12 | **0.6** | queen tree-pocket deaths fall < 30 % on live M2 | one switch | Rome/Seoul |
| **H-KZ20** | corpse-chain bait: our dead children's pearls lure our queen into fatal pockets | **0.5** (u9 supported, associational) | causal arm: tabu does not cut entries | via H-KZ21 | — |
| H-KZ23 (new) | child dead-end veto (L ≤ 4, acyclic C ≤ L+1) cuts length-3 wall deaths ≥ 30 % without reducing environmental food > 5 % (interacts with Himeji H-H7) | 0.35 | either bound fails | one switch | tester |
| H-KZ17 | pearls lure queens into tree pockets | 0.8 | ratio ≤ 1 | done | — |
| H-KZ19 (blue-sky) | portal sounding reveals camped exits | 0.2 | < 30 % of portal-transit deaths had an enemy on the exit ray line | geometry pass | Kanazawa |
| H-KZ18 (blue-sky) | planted pearls in a tree pocket next to the enemy queen kill it (inverse of H-KZ20; opponents look less susceptible) | 0.1 (↓) | enemy queen deaths ≤ base | sim | tester |
| H-KZ13 | top ten avoid baited dead ends | 0.45 | top-ten entry rate ≥ 0.5× ours | corpus pass | Kanazawa |
| H-KZ10 | wall hazard jumps at the 64 cap | 0.35 | ≤ 1.3× | corpus | Kanazawa/Shenzhen |
| H-KZ14 (blue-sky) | orbit parking is deliberate | 0.35 | orbiters on another map | corpus | Kanazawa |
| H-KZ3 | H-SZ23 length→hazard is mostly selection | 0.5 | landmark HR < 0.7 | corpus | Shenzhen/Himeji |
| H-KZ2 (blue-sky) | rotating one-ray echoes find the enemy queen early | 0.2 | < 20 % | sim | tester |
| H-KZ4/5 (blue-sky) | foreign packets / unauthenticated payloads | 0.15/0.1 | — | decode | Kanazawa |
| H-KZ6 | queen split needs a parent exit | 0.3 | alive < 0.15 | one switch | with H-KZ12 |
| H-KZ8 (blue-sky) | aim trapped deaths toward ally heads | 0.35 | Δcorpse < +0.03 | one switch | tester |

Closed: H-KZ1, H-KZ7, H-KZ9, H-KZ11 (approx. legality, ~2/3 avoidable), H-KZ16, **H-KZ22** (blue-sky 'born trapped': 0/13 donors aged ≤ 3; falsified in unit 9).

## What changed in unit 9 (4 Oct 07:11–07:40Z)
- **Input.** Main 21186bf24 merged himeji, kanazawa, nara and shenzhen (git.done 06:49 answered my unit-8 push). Himeji d30f065ed (H27):
  - H27-01: the template-cell corpse proxy is invalid (93.8 % proxy vs 52.8 % event-based). This weakens Shenzhen's 85–99 % corpse claim; Shenzhen needs to rerun it, and it is an **open lane contradiction (Himeji vs Shenzhen), not yet confirmed by Shenzhen**.
  - H27-02: the field's newborns capture more environmental food.
  - H27-05: q_forced2 is not exact (accepted).
  - H27-07: the collector still drops own games per Himeji, but the index now has new team-7 games from 06:26Z.
- Chongqing b50bbe886 withdrew H-C5/H-C6 (sealed, not culled). This agrees with my units 2–5.
- **Test.** q_chain.py, H-KZ20 with event provenance → supported for us. H-KZ22 falsified.
- **BOARD.** Result to Himeji/Rome/Seoul/Osaka; H27-05 acknowledgement to Himeji.

## Next steps
1. Event-stream TurnStart re-check of the 19+19 tree entries (H27-05; reuse Himeji queen_wall_attribution.py read-only).
2. Static (map_hash, u, v) → pocket table plus a death-site tabu spec for H-KZ21 (Rome/Seoul). Weakhold first.
3. Child wall-death census: where do length-3 children die, and which share is in acyclic pockets? This sizes H-KZ23 against H-H7.
4. H-KZ19 portal-sounding geometry; H-KZ13 on opponent-vs-opponent games.
