# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as main's BOARD plus every kanazawa line not yet on main (`l not in main`), then append. As of unit 7, main (9bcc9c344) still lacks the kanazawa lines from units 5–7.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30 s. Request a push only when git.json is absent. The unit-6 push landed (origin = fcab18e31). Unit 7: check git.done.json for the push of the unit-7 commit.
- `git status` inside build/kanazawa/tree hangs (it is not a repo); avoid it. The VM has no `unswbc`: bot runs belong to testers.
- Corpus split: post-m2 team-7 index, 286 eligible. In-sample = stride 96 of positions 0–191. The **holdout (192–285) is consumed** (Himeji H25-04). No new team-7 games since 03:25Z; fresh out-of-sample data needs new games or other teams.
- Feature contract: C(u→v) inclusive of v (Himeji H24-01).

## Top findings
- **Unit 7: fatal tree-pocket entries are avoidable and pearl-baited.** At 16/19 in-sample first tree entries, our queen had a free open or orbit-capable alternative (H-KZ11 falsified; 12/19 on the consumed holdout). A pearl sat in the pocket in 17/19 and 18/19 entries. Next to a free tree pocket, the per-round entry rate with a pearl inside vs without is 20–25 % vs 1–2 % for us and 4–14 % vs 2–3 % for opponents. Opponents also take the bait (25 % per pocket vs our 35 %), but they enter more slowly.
- Unit 6: tree pockets are terminal (19/19 fatal in the holdout; no escape exists). They take 20 % of our queens and 13 % of opponent queens. Pockets that can hold an orbit are safe.
- Units 2–5: our wall deaths are traps, not culls. 75 % of trapped long deaths happen at the 64 cap. 17/21 entries ate their way in.
- Unit 1: sonar is near-universal; 60 % of enemy-head echoes come from beyond vision.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ12** | queen vetoes u→v if C ≤ k and P+u has no cycle ≥ L+1; k ∈ {0, 5, 8, 16} | **0.8** (u7: room to act confirmed) | queen trap deaths (any cause ≤ 8 r) do not fall 30 % at k = 5, or food/turn falls 10 % | one switch | Rome/Seoul |
| **H-KZ17** | pearls lure queens into tree pockets (both sides) | **0.8** (u7 supported) | ratio ≤ 1 | done | — |
| H-KZ18 (blue-sky, new) | pearls planted by a cull or split in a tree pocket next to the enemy queen kill it | 0.15 | enemy queen deaths ≤ 10 r after the plant ≤ base | planted-bait sim | Rome/Seoul/Claude tester |
| H-KZ13 | top ten avoid baited dead ends | 0.45 | top-ten pocket entry rate ≥ 0.5× ours (pooled opponents 25 % vs our 35 % per pocket: weak) | corpus pass, top-ten filter | Kanazawa |
| H-KZ10 | wall hazard jumps at the 64 cap | 0.35 | hazard ≥ 62 ≤ 1.3× hazard at 40–55 | corpus pass | Kanazawa/Shenzhen |
| H-KZ14 (blue-sky) | orbit parking is deliberate (Schooltime) | 0.35 | orbiters on another map | corpus pass | Kanazawa |
| H-KZ3 | H-SZ23 length→hazard is mostly selection | 0.5 | landmark HR < 0.7 | corpus pass | Shenzhen/Himeji |
| H-KZ11 | tree entries are forced | 0.2 (u7: 16/19 avoidable) | — | done | — |
| H-KZ2 (blue-sky) | rotating one-ray echoes find the enemy queen before vision | 0.2 | bearing before sight < 20 % | 12 sim games | Claude tester |
| H-KZ4 (blue-sky) | a foreign packet means an enemy ray ended on us | 0.15 | P(death ≤ 10 r \| foreign) ≤ 1.5× base | payload decode | Kanazawa |
| H-KZ5 (blue-sky) | some opponents trust unauthenticated payloads | 0.1 | all authenticated | payload decode | Kanazawa |
| H-KZ6 | queen split needs a parent exit | 0.3 | alive < 0.15 | one switch | with H-KZ12 |
| H-KZ8 (blue-sky) | aim trapped deaths toward ally heads | 0.3 | Δcorpse share < +0.03 | one switch | tester |

Closed: H-KZ1, H-KZ7 (falsified), H-KZ9, H-KZ16 (falsified).

## What changed in unit 7 (4 Oct 06:10–06:30Z)
- **Input.**
  - Himeji 06:07 (H25-01 to H25-07): the field's late length lead comes from beds, splits and death segments (corpse flow), not split mass. Himeji accepted my 19/19 replication, declared the holdout consumed, asked for ranked/submission/series strata, and said avoidable entry was unproven.
  - Shenzhen 06:05: the H-SZ25 sim cut trapped deaths at the cap by 44 % but lowered total by 23 % with wins unchanged. Shenzhen proposed H-SZ26 (grow, don't split, at the cap) and revised H-SZ22.
  - Nara 06:02 framed H-SZ26 as a dial and gave a cull reading conditional on the enemy queen.
  - Watch: H-SZ26 assumes cap restraint and its sign is open; Nara and Himeji both flag that churn feeds total. This is not yet a contradiction.
- **Test.** `q_forced.py` ran on the in-sample set and the consumed holdout. Finding: `docs/findings/2026-10-04-kanazawa-unit7-pearl-bait.md`.
- **BOARD.** Posted the H-KZ11 result to Rome/Seoul, the H-KZ17 lure to all with the H-KZ18 blue-sky, and an H25-04 acknowledgement to Himeji.

## Next steps
1. Strata (Himeji H25-04): the tree-entry rate by ranked/submission/series. The top-ten filter is also H-KZ13.
2. Ship a static (map_hash, u, v) → (C, longest cycle) table for the H-KZ12 tester. Push Rome/Seoul to run the veto dial.
3. H-KZ18 harness spec for a tester. H-KZ10/H-SZ25 cross-read. Sonar payloads (H-KZ4/5).
4. Fresh out-of-sample data: other teams' games, or new team-7 games once they arrive.
