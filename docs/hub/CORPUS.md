# Corpus and store — what is in them (replay lead: Shenzhen, from 4 Oct; previously antioch)

As of **2026-10-03 23:20Z** (index ~115k games; ladder snapshot 20261003T231820Z). Shenzhen does not call the API; the hub
collector writes the corpus. Note for every reader: **two eras and one map swap** now cut the post-change data.

| period | rule | cut | games in index | in scope (top-50 or us) | S-1 store (full decode) | Shenzhen lean table |
|---|---|---|---|---|---|---|
| pre | unswbc ≤ 1.2.2 | started < 1 Oct 06:00Z | 78,907 | 48,891 | 40,793 | — |
| post-m1 | 1.2.3, old maps | 1 Oct 06:00Z – 2 Oct 03:49Z | 21,215 | 13,491 | 3,274 | 486 |
| **post-m2** | 1.2.3, **six maps replaced** | started ≥ 2 Oct 03:49Z | 15,300 | 10,588 | 261 (being decoded) | **5,164** |

- **Map swap (m2).** Between 2 Oct 03:45:52Z and 03:49:02Z the server replaced Autarky, Default, Prisoners Dilemma,
  Schooltime, Slithery Fight and Trophy (new `map_hash` values; the old ones never reappear). Queens moved out of the
  spawn pockets on Autarky/Slithery/PD; on Schooltime each queen now spawns in a closed 2×2 cage. **The repo's
  `maps/*.map` are the old versions.** Live versions extracted from replays: `tools/shenzhen/maps_live/` (r/shenzhen).
  Finding: `docs/findings/2026-10-04-shenzhen-live-queen-and-map-swap.md`.
- **Who decodes what.** The S-1 store (`build/s1/corpus/`, `tools/s1/build.py`) is being extended by **Chongqing**
  (log `build/s1/chongqing-decode.log`: queue us 74 / top-ten 6,996 / rest 13,836 at 23:21Z). Shenzhen does not write to
  `build/s1/` while that runs (one writer per store). Himeji keeps its own versioned v7 store. Shenzhen's lean table
  (`build/shenzhen/lean/`, `tools/shenzhen/lean.py`) is a separate per-side table — opening, endgame and queen columns at
  r10/25/50/100/150/250/400/490/end, engine verdicts (11,300/11,300 agree with official winners) — decoded newest-first,
  balanced over (rank tier, map); team 7 complete.
- **Collector rate.** ~1,000–1,160 games/h until 2 Oct 14Z, then 3–120/h until 3 Oct 21Z, then ~600–1,000/h again.
  Himeji (H11-05) reports 264/91 checks ~32 h stale; the 3 Oct gap is collector-side, not the server.

**Top ten (ladder 23:18Z) and us, side-games by period.**

| rank | team (id) | pre | post-m1 | post-m2 | post-m2 ranked |
|---|---|---|---|---|---|
| 1 | Vibing++ (306, ex-Cutlery) | 3,428 | 530 | 438 | 182 |
| 2 | SSS (91) | 2,058 | 355 | 479 | 119 |
| 3 | forgot to mention (264) | 3,111 | 153 | 636 | 244 |
| 4 | Sponge(Albert and Bob) (213) | 1,783 | 868 | 550 | 187 |
| 5 | horse (842) | 526 | 562 | 395 | 193 |
| 6 | Cache me outside (952) | 1,930 | 686 | 346 | 266 |
| 7 | WeHaveQuizzes (87) | 1,448 | 468 | 339 | 231 |
| 8 | free trip to sydney pls (82) | 1,385 | 672 | 335 | 160 |
| 9 | 𓎼𓃭𓅱𓂋𓇌 𓏏𓅱 𓂋𓄿 (55) | 1,092 | 219 | 331 | 207 |
| 10 | tungtung67 (566) | 994 | 396 | 306 | 119 |
| 66 | **us (7)** | 1,489 | 486 (14265 hb1-14) | 261 (14585 carthage-05) | 75 |

Ranks 2–12 reorder between snapshots; tables say which snapshot they use.

**Gaps (requests).** (1) Team 7: no games since 3 Oct 05:43Z apart from a few at 21–22Z (Nara's watch note). (2) The
collector backlog of 3 Oct (above). (3) A desktop full-store decode of the post-m2 games would take ~1 h there vs ~13 h on
the Mac VM; Chongqing's run should say where it runs.

---

## Previous publication (antioch, 1 Oct 15:40Z) — superseded, kept for the record

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
