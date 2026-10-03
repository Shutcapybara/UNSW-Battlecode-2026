# Corpus and store — what is in them (replay lead: chongqing, wave 2; antioch before)

As of **2026-10-04 00:20Z** (index 115,542 games, collector running on the Mac). Store built **on the Mac** (Cowork VM,
`wt-chongqing`, `build/` symlinked to the main checkout) — the desktop copy under `wt-antioch` is stale from 1 Oct 20:50Z.
Republished after every build. **No API calls from this lineage; GPT's analyst also pulls replays this wave — the hub
collector is the only writer of `public_replays/corpus/`.**

- **Corpus:** `public_replays/corpus/` (index.jsonl, ladder/ 519 snapshots to 3 Oct 23:29Z, replays/). Targets in
  `tools/hub/config.py`.
- **Store:** `build/s1/corpus/` (`tools/s1/build.py`; parts are append-only). Decoding of the post-change backlog runs in
  VM calls at ~65 games per call with `tools/chongqing/decode.py` (team 7 first, then current top-ten sides balanced over
  team × map, newest first, then the builder's round-robin). Expect the 2–3 Oct bulk over several units.
- **Queries:** `tools/s1/q.py` (reference; slow to bind over the mount) or `tools/chongqing/qq.py` (post-era parts only,
  binds in ~6 s; views games, teams, sides, deaths, splits, transits, series).
- **Era:** `games.era`; `post` ⇔ `started_at ≥ 2026-10-01T06:00Z` (D-042). Unchanged.
- **Ladder reset (new):** between 06:21Z and 17:09Z on 1 Oct every team went to 1500 / `rank: null`; ranks return as teams
  play. `teams.parquet` (`cohort`, `crank`) is the **post-reset** ladder from the latest snapshot. Stockfish (206) and PPP
  (27) are no longer on the ladder; cheji bt (70) has not played since; Cutlery (306) is now named Vibing++ (rank 1).
  Game-time `elo_a/elo_b` are stale/1500 around the reset — use `crank` or the 06:21Z snapshot for cohorts.
- **Queen columns (new, parts from 3 Oct 23:16Z):** `q_id, q_alive_end, q_death_round, q_death_cls, q_death_killer,
  q_moves, q_maxlen, q_end, q_header, q_len@{25,50,100,150,250,400,490}` on `sides`. Older parts read NULL; backfill queued.
  Queen survival/death for any part: `deaths where id in (0,1)` per side (the two queens are ids 0 and 1, side varies by map).

| era | games in index | in scope (top-50 post-reset, or us) | decoded in store | first start | last start |
|---|---|---|---|---|---|
| pre | 78,907 | 47,634 | 40,793 | 25 Sep 07:12Z | 01 Oct 05:57Z |
| post | 36,635 | 23,035+ | **3,535** (2,862 antioch + 673 team 7) | 01 Oct 09:23Z | 03 Oct 23:29Z |

**Post-change in-scope games by map (index):** Schooltime 2,195, Slithery Fight 2,170, Portals 2,104, Trophy 1,986,
Trauma 1,959, Default 1,926, Autarky 1,886, Queen Of Spades 1,819, Devil 1,756, Prisoners Dilemma 1,696; **the seven
non-ladder maps are back since 2 Oct:** Australia 572, Islands 563, Around UNSW 562, Maze 525, weakhold 454, Stripes 445,
Tower Defense 417.

**Decoded post-change side-games by cohort (post-reset):** top10 1,122 (9 teams; the 2 Oct ones are unranked games vs us),
r11–30 1,627, r31–50 1,214, other 2,406, **us 673** (hb1-14 live since 1 Oct 17:00Z; 180 ranked, 493 unranked).

## Gaps (requests to the director)

- The decode backlog (20,850 games) is CPU-bound in the VM; a native `nice -n 15 python3 tools/chongqing/decode.py --jobs 6
  --time 3000` from the repo root on the Mac would clear it in under an hour (the user declined for now).
- Collector targets: the current top ten are all present post-change except that 2–3 Oct ranked games of SSS, forgot to
  mention, Cache me outside, free trip to sydney pls and fandagong are thin in the store until the bulk lands — not a
  collector gap, a decode gap.
