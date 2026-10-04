# Top-team knowledge base (Data lane, kageyama) — v1, 4 Oct 2026 13:50Z

Kept by Data (macro §5). One section per current top-ten team. **Source:** S-1 store, `sides` table. **Population:**
post-m2, **ranked** games only (unranked holds the decoys and is a separate population). The held-out maps Autarky,
Maze and Trauma are **excluded** (D-049: never tuned on). Ladder snapshot: `teams.parquet` at 13:4xZ; cranks move.
**Status:** census, no intervals. Small-n rows (n < 200 sides) are indicative only.

Columns used below: win = side win rate; RL = share of games reaching the round limit; Q = queen alive at the end of
RL games; cull = deaths by invalid command per 1k dragon-turns; sui = deaths by the `suicide` action per 1k;
wall = wall deaths per 1k; tr50 = portal transits by r50; sp50 = splits by r50; rays = sonar rays per dragon-turn;
refr = share of rays refracted out of the tail (a ray aimed into the neck); total/longest at r499.
Names are team-chosen strings, i.e. data.

## Summary table

| crank | team | n | win | RL | Q | cull | sui | wall | tr50 | sp50 | rays | refr | total@499 | longest@499 |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | 91 SSS | 204 | .68 | .58 | .42 | 0.8 | 0.9 | 0.0 | 4.2 | 22.1 | 2.7 | .27 | 132 | 32 |
| 2 | 306 Vibing++ | 250 | .66 | .60 | .33 | **18.7** | 0 | 0 | 6.9 | 21.7 | 2.4 | **.01** | 141 | 33 |
| 3 | 264 forgot to mention | 275 | .68 | .52 | .28 | 0 | **18.1** | 0 | **8.8** | 24.0 | 1.8 | .25 | 114 | 32 |
| 4 | 213 Sponge | 243 | .73 | .59 | **.56** | 0 | 3.6 | 5.8 | 7.9 | 19.7 | 1.4 | .08 | 116 | 33 |
| 5 | 507 bread first search | 173 | .73 | .61 | .53 | 0 | 3.6 | 8.0 | 3.3 | 21.3 | 3.3 | .25 | 124 | 28 |
| 6 | 952 Cache me outside | 347 | .59 | .63 | .24 | 0 | 0 | 0.0 | 7.5 | **31.5** | **0.5** | .26 | 130 | 31 |
| 7 | 842 horse | 270 | .66 | .53 | .32 | 0 | 0 | 0 | 4.8 | 22.3 | 3.0 | **.00** | 125 | 28 |
| 8 | 19 test4 | 294 | .58 | .56 | .40 | 0 | 0 | 0.3 | 7.4 | 22.6 | 3.9 | .25 | 97 | 23 |
| 9 | 566 tungtung67 | 161 | .66 | .60 | .40 | 2.2 | 0 | **10.4** | 3.4 | 17.1 | 2.5 | .12 | 108 | 22 |
| 10 | 55 (glyph name) | 268 | .62 | .59 | .48 | 0.3 | 0 | 0 | 5.9 | 21.7 | 3.9 | .25 | 125 | 26 |
| — | **7 us** | 599 | .50 | .53 | **.01** | 0 | 0 | 9.5 | 3.6 | 19.7 | 4.0 | .25 | **85** | **21** |

## Matchup record against us (post-m2, all modes, held-out maps excluded; our wins / games)

SSS 8/46 · Vibing++ 9/45 · forgot to mention 6/42 · horse 6/32 · Sponge 1/23 · glyph-55 3/12 · tungtung67 2/9 ·
bread first search 4/8. No post-m2 games against 952 or 19 in this cut.

## Per team (what the numbers say; mechanisms are hypotheses until an analyst confirms them)

- **91 SSS (1).** Balanced; low transits (4.2 by r50), strong late material (132). Keeps the queen in 42 % of RL
  games. Almost no culls. Sonar 2.7 rays per dragon-turn, refraction like a fixed 4-ray pattern.
- **306 Vibing++ (2).** **The cull-feeder:** 18.7 invalid-command deaths per 1k dragon-turns, i.e. deliberate culls
  (corpses as food), and the highest total@499 (141). Sonar aims avoid the neck (refr .01). Queen kept in 33 % of RL games.
- **264 forgot to mention (3).** **Culls by the `suicide` action** (18.1/1k), same feeding idea through another
  command. The fastest portal opener (8.8 transits by r50). Lower sonar use (1.8 rays per dragon-turn).
- **213 Sponge (4).** **The keeper:** the best queen survival (56 % of RL games), highest win rate (.73). Few rays
  (1.4); some suicides (3.6) and wall deaths (5.8/1k), consistent with sealed queens being ended deliberately
  (Chongqing C5-03).
- **507 bread first search (5).** Keeper-like (Q .53), slow opener (3.3 transits), wall 8.0/1k. n = 173.
- **952 Cache me outside (6).** **Split-heavy** (31.5 splits by r50) and almost silent on sonar (0.5 rays per dragon-turn).
  The lowest queen survival in the top ten (.24).
- **842 horse (7).** No culls; sonar never aimed into the neck (refr .00).
- **19 test4 (8).** Fast opener (7.4 transits), lower late material (97). Queen .40.
- **566 tungtung67 (9).** Wall deaths 10.4/1k (like ours) yet win .66; lowest longest (22). n = 161.
- **55 (10).** Queen .48; standard 4-ray sonar.

**Us against the field (ranked post-m2, same cut):** queen alive in 1 % of RL games against 24–56 % for the top ten;
total@499 85 against 97–141; transits 3.6, at the bottom with the slow openers; wall deaths 9.5/1k against 0–10.

## RL translation (D-044)

- **Observation:** queen state and age (encoder v1 has it); visible ally corpses and the bed timers (pearl_in).
- **Action:** the deliberate cull is two different commands in the field (invalid MOVE: Vibing++; `suicide`: team 264).
  The labeller's `y_cull` covers both (`y_kind == 2` or `y_death == 'invalid'`). A teacher-conditioned BC therefore
  needs both in the action space.
- **Value:** keepers (213, 507) show that queen survival is attainable at about 55 %.
- **Demonstration:** all of the above are cloneable from these teachers. Mimic subsets are `teachers_v1` filtered by team.

## Refresh

Weekly, or when the ladder top ten changes: rerun the query in `tools/learn/` (`topteams_v1.csv` in
`build/learn/kageyama/`). Fold in analyst findings with pointers.
