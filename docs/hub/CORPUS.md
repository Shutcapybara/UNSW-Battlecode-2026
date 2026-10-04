# Corpus and store — what is in them (replay lead: chongqing, wave 2; antioch before)

As of **2026-10-04 09:25Z** (index ~121,000 games, collector running on the Mac). Store built **on the Mac** (Cowork VM,
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
- **Eras:** `games.era` (rules): `post` ⇔ `started_at ≥ 2026-10-01T06:00Z` (D-042). **`games.map_era` (maps, new 4 Oct):** `pre` |
  `post` (new rules, old maps) | `post-m2` ⇔ `started_at ≥ 2026-10-02T03:49Z` (the server replaced Autarky, Default, PD, Schooltime,
  Slithery Fight and Trophy — new `map_hash`, two seat-hashes each — and restored the seven non-ladder maps at 04:31Z). Old and new
  versions are different maps: per-map references and norms must state `map_era`; the cached `post` norms are old-map norms.
  The repo's `maps/*.map` are the old versions (unswbc ≥ 1.2.6 ships the new ones — Shenzhen).
- **Ladder reset (new):** between 06:21Z and 17:09Z on 1 Oct every team went to 1500 / `rank: null`; ranks return as teams
  play. `teams.parquet` (`cohort`, `crank`) is the **post-reset** ladder from the latest snapshot. Stockfish (206) and PPP
  (27) are no longer on the ladder; cheji bt (70) has not played since; Cutlery (306) is now named Vibing++ (rank 1).
  Game-time `elo_a/elo_b` are stale/1500 around the reset — use `crank` or the 06:21Z snapshot for cohorts.
- **Queen columns (new, parts from 3 Oct 23:16Z):** `q_id, q_alive_end, q_death_round, q_death_cls, q_death_killer,
  q_moves, q_maxlen, q_end, q_header, q_len@{25,50,100,150,250,400,490}` on `sides`. Older parts read NULL; backfill queued.
  Queen survival/death for any part: `deaths where id in (0,1)` per side (the two queens are ids 0 and 1, side varies by map).

| era | games in index | in scope (top-50 post-reset, or us) | decoded in store | first start | last start |
|---|---|---|---|---|---|
| pre | 78,907 | 48,445 | 40,793 | 25 Sep 07:12Z | 01 Oct 05:57Z |
| post (old maps) | 21,215 | 13,332 | 2,965 | 01 Oct 09:23Z | 02 Oct 03:48Z |
| post-m2 (new maps) | 18,600 | 13,439 | **~7,200** (native Mac decode ~05:00–05:18Z, idle since; VM batches; queue ~6,300) | 02 Oct 03:49Z | 04 Oct 05:17Z |

**Post-change in-scope games by map (index):** Schooltime 2,195, Slithery Fight 2,170, Portals 2,104, Trophy 1,986,
Trauma 1,959, Default 1,926, Autarky 1,886, Queen Of Spades 1,819, Devil 1,756, Prisoners Dilemma 1,696; **the seven
non-ladder maps are back since 2 Oct:** Australia 572, Islands 563, Around UNSW 562, Maze 525, weakhold 454, Stripes 445,
Tower Defense 417.

**Decoded post-change side-games by cohort (ladder 00:53Z):** old maps — top10 993, r11–30 1,980, r31–50 767, other 2,441, us 486
(14265); new maps — top10 1,067 (489 ranked, 1 % vs us), r11–30 277, r31–50 221, us 271 (15 × 14265 + 256 × 14585 = carthage-05,
live since 2 Oct 04:22Z). Decode order: post-m2 first, top-ten sides balanced over team × map, then the rest.

## Gaps (requests to the director)

- Someone ran a native decode on the Mac at ~05:00–05:18Z (150 parts, pid 1558) — that is the right way to finish the backlog:
  `nice -n 15 python3 tools/chongqing/decode.py --jobs 6 --time 3000` from the repo root (post-m2 first). VM batches are
  stopped while it runs; `canon` dedups any overlap.
- Collector: Himeji reports 264/91 checks ~32 h stale and own-team games arriving only via opponents (H11-05/H12-05) — the
  director's call; nothing here pulls.
- Queen backfill of the 2,862 old-map games is deprioritised behind post-m2 decoding (old maps are no longer played).
