# Corpus and store — what is in them (replay lead: antioch)

As of **2026-10-01 15:40Z** (index 78,733 games). **Synced to the Mac's `build/s1/corpus` at 2026-10-01 20:50 UTC** (219 parts, `games.era`, post-change norms). Republished after every build.

- **Corpus:** `public_replays/corpus/`. The hub collector on the Mac writes it under the shared API rate limit; the
  targets are in `tools/hub/config.py`. A copy is rsynced to the desktop (`wt-antioch`).
- **Store:** `build/s1/corpus/`, built on the desktop from the rsynced corpus with `tools/s1/build.py`.
- **Queries:** `tools/s1/q.py`. Set `S1_ERA=post` (or `pre`) to scope the views and the field norms to one rules era.
- **Era:** `games.era`. `post` ⇔ `started_at ≥ 2026-10-01T06:00Z`. The live server switched to unswbc 1.2.3 between
  05:57:53Z and 09:26:58Z (`docs/findings/2026-10-01-antioch-era-and-queen.md`).

| era | games in index | in scope (top-50 or us) | decoded in store | first start | last start |
|---|---|---|---|---|---|
| pre | 74,761 | 55,728 | 40,793 | 25 Sep 07:12Z | 01 Oct 05:57Z |
| post | 3,943 | 2,862 | 2,862 (desktop and Mac) | 01 Oct 09:23Z | 01 Oct 15:39Z |

**Post-change games by map:** Slithery Fight 176, Autarky 170, Schooltime 170, Portals 168, Devil 165, Trophy 164,
Trauma 153, Queen Of Spades 151, Default 147, Prisoners Dilemma 139. Only the ten ladder maps appear after the switch.
Seven maps seen on 30 Sep (Around UNSW, Australia, Islands, Maze, Stripes, Tower Defense, weakhold) have not appeared
since.

**Top ten and us, side-games by era.** Ranks are from the last ladder snapshot, 2026-10-01 06:21Z.

| rank | team | pre | post |
|---|---|---|---|
| 1 | Cutlery | 3,365 | 42 |
| 2 | forgot to mention | 3,041 | **0** |
| 3 | 3.14159265 | 2,216 | 83 |
| 4 | SSS | 2,029 | **0** |
| 5 | cheji bt | 4,446 | **0** |
| 6 | Stockfish | 2,188 | 42 |
| 7 | PPP | 1,198 | **0** |
| 8 | calc | 2,549 | 58 |
| 9 | Sponge(Albert and Bob) | 1,754 | 83 |
| 10 | Cache me outside | 1,851 | **0** |
| — | us (team 7) | 1,442 | **0** |

## Gaps (requests to the director)

- **No ladder snapshot since 06:21Z.** Cohorts and Elo at game time are stale for every post-change game.
- **Five of the top ten have no post-change games.** Please raise the collector targets for forgot to mention, SSS,
  cheji bt, PPP and Cache me outside. They are needed for the post-change top-ten references.
- **Team 7 has played no post-change games.** That is expected while the submission is paused.

## Side tables (antioch, not in the s1 store yet)

- `tools/antioch/era.py`: per-game era signals (sprint pricing, queen field, engine verdict).
- `tools/antioch/queen.py`: per-side queen and endgame rows. Output: `build/antioch/queen.parquet`.
