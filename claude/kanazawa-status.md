# Kanazawa — Claude (Opus 5.5) analyst: cross-lane synthesis and blue-sky mechanisms (branch r/kanazawa)

Mirror of repo `claude/kanazawa-status.md` (r/kanazawa, pushed via the keeper). Half-hourly units (:10/:40 UTC tasks).

## Operating notes (for the next unit)
- The repo is mounted at `$HOME/mnt/Projects/UNSW-Battlecode-2026` (the connected folder is the parent, `Projects`). If `connectedFolders` is empty, exit silently: the user was told once, on 4 Oct at 03:10Z.
- Private tree `build/kanazawa/tree`; commit with `bash build/kanazawa/tree/tools/kanazawa/commit.sh "msg"` from the repo root.
- **BOARD:** tree files replace the branch's files. Rebuild the tree's BOARD.md as origin/main's BOARD plus every kanazawa line not yet on main (`l not in main`), then append. As of unit 8, main (1edac66c2) still lacks the kanazawa lines from units 5–8.
- **Lock:** the VM cannot delete files. Release `build/kanazawa/unit.lock` by writing `released <time>` and `touch -d 2000-01-01`. The lock is free if its content starts with `released` or it is more than 40 min old.
- **Keeper:** about 30 s. Request a push only when git.json is absent. The unit-7 push landed (origin = 57bfbb463). Unit 8: check git.done.json for the push of the unit-8 commit.
- `git status` inside build/kanazawa/tree hangs (it is not a repo); avoid it. The VM has no `unswbc`: bot runs belong to testers.
- Corpus split: post-m2 team-7 index, 286 eligible. In-sample = stride 96 of positions 0–191. The holdout (192–285) is consumed (Himeji H25-04). **Himeji H26-01: our own games are missing from the corpus since 03:25Z** (own-watch removed from the collector; patch H26-02 awaits the director). Fresh out-of-sample data needs the collector repair or opponent-vs-opponent games.
- Feature contract: C(u→v) inclusive of v (Himeji H24-01). Legality contract (unit 8): own tail fatal; id < q at R[t+1], id > q at R[t] with tails.

## Top findings
- **Unit 8: exact legality trims avoidability a little.** Our first tree entries are avoidable at the entry step 14/19 in-sample and 12/19 on the holdout (pooled 0.68, down from 0.74 approx). About a third are decided upstream.
- **Unit 8: weakhold is two scripted queen deaths.** 16/16 post-m2 games, win 1/16. The r40 branch (7 games) has a legal open exit at the entry step, so a one-step veto fixes it. The r24 branch (8 games) is sealed upstream (Himeji H22-01). This replicates Chongqing C3-01.
- Unit 7: tree-pocket entries are pearl-baited (17/19, 18/19; associational). Next to a free pocket the entry rate with a pearl inside is 20–25 % vs 1–2 % without.
- Unit 6: tree pockets are terminal (19/19). They take 20 % of our queens and 13 % of opponent queens. Orbit-capable pockets are safe.
- Units 2–5: our wall deaths are traps, not culls; 75 % of trapped long deaths happen at the 64 cap.
- Unit 1: sonar is near-universal; 60 % of enemy-head echoes come from beyond vision.

## Hypotheses
| id | claim | weight | falsifier | cost | suits |
|---|---|---|---|---|---|
| **H-KZ12** | queen vetoes u→v if C ≤ k and P+u has no cycle ≥ L+1; k ∈ {0, 5, 8, 16} | **0.8** | queen trap deaths do not fall 30 % at k = 5, or food/turn falls 10 %; on weakhold the r40 branch must vanish | one switch; weakhold alone is a clean check | Rome/Seoul |
| **H-KZ17** | pearls lure queens into tree pockets (both sides) | 0.8 | ratio ≤ 1 | done (associational) | — |
| H-KZ20 (new) | corpse-chain bait: pearls in fatal pockets are often corpse pearls from an earlier death there, so one pocket death baits the next | 0.3 | corpse-origin share of in-pocket pearls at entry ≤ board base rate | corpus pass with pearl provenance | Kanazawa |
| H-KZ19 (blue-sky, new) | portal sounding: a ray sent through a portal before transit reveals camped/blocked exits (echo enemy/enemy_head) | 0.2 | among portal-transit deaths ≤ 3 r, < 30 % had an enemy body within k tiles on the ray line past the exit at transit time | corpus geometry pass | Kanazawa, then Carthage |
| H-KZ18 (blue-sky) | pearls planted by a cull or split in a tree pocket next to the enemy queen kill it | 0.15 | enemy queen deaths ≤ 10 r after plant ≤ base | planted-bait sim | Rome/Seoul/Claude tester |
| H-KZ13 | top ten avoid baited dead ends | 0.45 | top-ten pocket entry rate ≥ 0.5× ours | corpus pass, top-ten filter | Kanazawa |
| H-KZ10 | wall hazard jumps at the 64 cap | 0.35 | hazard ≥ 62 ≤ 1.3× hazard at 40–55 | corpus pass | Kanazawa/Shenzhen |
| H-KZ14 (blue-sky) | orbit parking is deliberate (Schooltime) | 0.35 | orbiters on another map | corpus pass | Kanazawa |
| H-KZ3 | H-SZ23 length→hazard is mostly selection | 0.5 | landmark HR < 0.7 | corpus pass | Shenzhen/Himeji |
| H-KZ11 | tree entries are forced | 0.3 (u8: exact 26/38 avoidable) | — | done | — |
| H-KZ2 (blue-sky) | rotating one-ray echoes find the enemy queen before vision | 0.2 | bearing before sight < 20 % | 12 sim games | Claude tester |
| H-KZ4 (blue-sky) | a foreign packet means an enemy ray ended on us | 0.15 | P(death ≤ 10 r \| foreign) ≤ 1.5× base | payload decode | Kanazawa |
| H-KZ5 (blue-sky) | some opponents trust unauthenticated payloads | 0.1 | all authenticated | payload decode | Kanazawa |
| H-KZ6 | queen split needs a parent exit | 0.3 | alive < 0.15 | one switch | with H-KZ12 |
| H-KZ8 (blue-sky) | aim trapped deaths toward ally heads (now linked to Shenzhen's corpse economy, H-SZ28/29) | 0.35 | Δcorpse share < +0.03 | one switch | tester |

Closed: H-KZ1, H-KZ7 (falsified), H-KZ9, H-KZ16 (falsified).

## What changed in unit 8 (4 Oct 06:41–07:00Z)
- **Input.** Himeji 06:40: H26-01 own games missing from the corpus since 03:25Z (explains "no new team-7 games"); H26-02 collector patch awaits the director; H26-05 asked for exact legality before my H-KZ11 drop. Shenzhen 06:50: H-SZ26 refuted in sim (throttling cap splits loses food); late-game length on cap maps is 85–99 % corpse pearls; top ten eat 46–60 % more corpses after r150 (H-SZ28/29). Rome: test-arm metadata cleanup only. Main: Carthage H-S1 portal memory rejected (per-transit deaths −2.7 %), D-045 learned gate. No contradiction between lanes this unit; Himeji H26-06 vs Nara 06:02 on the cull fallback is a live disagreement but between those two lanes, each with a stated test.
- **Test.** `q_forced2.py` (exact legality) and `q_weakhold.py`. Finding: `docs/findings/2026-10-04-kanazawa-unit8-exact-legality.md`.
- **BOARD.** H26-05 result to Himeji/Osaka; weakhold branch split to Chongqing/Himeji/Rome/Seoul.

## Next steps
1. H-KZ20 corpse-chain bait (pearl provenance: pearls appearing at a death's alternating segments). Links my pocket findings to Shenzhen's corpse economy.
2. H-KZ19 portal sounding geometry pass (Carthage's portal memory failed, so the portal exit state is the open question).
3. Strata (Himeji H25-04, ranked/series) on the tree-entry rate; H-KZ13 top-ten filter on opponent-vs-opponent games (fresh out-of-sample).
4. Static (map_hash, u, v) → (C, longest cycle) table for the H-KZ12 tester; push Rome/Seoul to run weakhold first.
