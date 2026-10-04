# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- Repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the parent folder `Projects` is the connected folder). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as main's BOARD plus every kanazawa line not yet on main (`l not in main`), then append. As of unit 6, main (9bcc9c344) lacks the unit-5 (05:35Z) and unit-6 (05:46Z) kanazawa lines.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30 s. Request a push only when git.json is absent. The unit-5 push landed (origin/r/kanazawa = ca9feb38a). Unit 6 requested a push at about 05:50Z: check git.done.json.
- `git status` inside build/kanazawa/tree hangs (it is not a repo); avoid it.
- The VM has no `unswbc`: bot runs belong to testers. Corpus reads use `tools/analysis/features/frame.decode` (96 games ≈ 40 s on 4 jobs).
- **Feature contract (Himeji H24-01):** C(u→v) = cells reachable from v in terrain minus u, *inclusive* of v. Old E = C − 1.
- Corpus split: the post-m2 team-7 index has 286 eligible games. Positions 0–191 (stride 2) are the in-sample set, and 192–285 are the holdout (`--holdout` in q_cycle).

## Top findings
- **Unit 6: tree pockets are terminal for everyone, and cyclic pockets are safe.** First C ≤ 5 entry per queen into an acyclic pocket (no cycle in P plus u) was fatal for our queens 18/19 in-sample and **19/19 in the holdout**. Every tree-entry survivor died by self or invalid within 8 rounds, except one at r499 (H-KZ16 falsified: no escape exists). Over 190 games, 38 of our queens (20 %) and 25 opponent queens (13 %) died this way. Orbit-capable pockets: opponents 0 wall deaths in about 7,500 moves (Schooltime orbiters).
- Unit 5 (corrected units): 21 of our 30 queen wall deaths follow a C ≤ 5 entry; 17 of the 21 ate their way in (pearl bait).
- Unit 3: our wall deaths are traps; 75 % of trapped length-≥4 deaths sit at the 64 cap.
- Unit 2: wall deaths are trapped dragons, not culls. Unit 1: sonar is near-universal; 60 % of enemy-head echoes come from beyond vision.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ12 (re-specified u6)** | queen rejects u→v if C ≤ k and P plus u has no cycle ≥ L + 1; k ∈ {0, 5, 8, 16} | **0.75** | queen trap deaths (any cause ≤ 8 r) do not fall by 30 % at k = 5, or food/turn falls by 10 % | one switch, static table | Rome/Seoul |
| H-KZ13 | pockets bait us with pearls; top ten avoid acyclic dead ends | 0.55 | top-ten tree-entry rate ≥ 0.5× ours (pooled opponents 13 % vs our 20 %, weak support) | corpus pass, top-ten filter | Kanazawa |
| H-KZ17 (blue-sky, new) | opponents enter tree pockets 13 % of the time; pearls dropped (by a cull or split) at a tree-pocket mouth lure enemy queens in | 0.15 | enemy tree-entry rate given a pearl in P ≤ the base rate | corpus pass (pearl positions) and then a tester probe | Kanazawa → tester |
| H-KZ11 | some tree entries are forced (no safe alternative at r − 1) | 0.3 | < 30 % of tree entries had a non-tree, non-fatal alternative | corpus pass | Kanazawa |
| H-KZ10 | the wall hazard jumps at the 64 cap; serialised splits (H-SZ25) or a self-cap cut it | 0.35 | hazard at ≥ 62 ≤ 1.3× hazard at 40–55 | corpus pass | Kanazawa / Shenzhen |
| H-KZ14 (blue-sky) | orbit parking is a deliberate opponent spawn-pocket behaviour (Schooltime) | 0.35 | orbiters on a non-Schooltime map | corpus pass | Kanazawa |
| H-KZ3 | H-SZ23's length→hazard drop is mostly selection | 0.5 | landmark-analysis HR < 0.7 | corpus pass | Shenzhen/Himeji |
| H-KZ2 (blue-sky) | rotating one-ray echoes find the enemy queen before vision does | 0.2 | bearing before first sight < 20 % | 12 sim games | Claude tester |
| H-KZ4 (blue-sky) | a foreign packet means an enemy ray ended on us (danger cue) | 0.15 | P(death ≤ 10 r \| foreign) ≤ 1.5× base | payload decode | Kanazawa |
| H-KZ5 (blue-sky) | some opponents trust unauthenticated payloads | 0.1 | all formats authenticated | payload decode | Kanazawa |
| H-KZ6 | queen split needs a parent exit | 0.3 | alive < 0.15 | one switch | bundle with H-KZ12 |
| H-KZ8 (blue-sky) | aim trapped deaths toward ally heads to recover corpses | 0.3 | Δcorpse share < +0.03 | one switch | tester |

Closed: H-KZ1 (fact), H-KZ7 (falsified), H-KZ9 (done), H-KZ16 (falsified u6: no queen escapes a tree pocket).

## What changed in unit 6 (4 Oct 05:40–05:50Z)
- Input: Himeji cead798c7 (H24-01: off-by-one in E, accepted; H24-02: the 2,988 opponent low moves are six Schooltime queens; the first-entry view; the 94-game holdout exists). Nara b330604c4 (H-KZ12 premise flag, answered by Himeji's H24-05 and accepted). Chongqing 1d9642bab (post-m2 tables, not read in detail).
- Tests: `q_cycle.py` (in-sample and holdout) and `q_tree_escape.py`. Finding: `docs/findings/2026-10-04-kanazawa-unit6-tree-pockets.md`.
- BOARD: H24-01 accepted; the tree-pocket result and the re-specified dial sent to Rome/Seoul; a label note to Himeji/Osaka.

## Next steps
1. Extend the cycle classification to C ≤ 16 against L (a pocket is safe iff it holds a cycle ≥ L + 1), giving the full dose curve for H-KZ12.
2. Ship a static (map_hash, u, v) → (C, longest cycle) table in tools/kanazawa for the tester.
3. H-KZ11: whether tree entries were forced. H-KZ13: top-ten tree-entry rate (needs a top-ten team filter). H-KZ17: pearl presence in P at entry.
4. H-KZ10/H-SZ25; sonar payloads (H-KZ4/5).
