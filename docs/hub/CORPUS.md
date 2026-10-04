# Corpus and store — what is in them (replay lead: chongqing, wave 2; antioch before)
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

As of **2026-10-04 02:00Z** (index 117,097 games, collector running on the Mac). Store built **on the Mac** (Cowork VM,
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
| post (old maps) | 21,215 | 13,626 | ~3,100 (antioch 2,862 + team 7) | 01 Oct 09:23Z | 02 Oct 03:48Z |
| post-m2 (new maps) | 16,975 | 11,852 | **~1,250** (team 7 271 complete; top-ten ranked 410 games) | 02 Oct 03:49Z | 04 Oct 00:53Z |

**Post-change in-scope games by map (index):** Schooltime 2,195, Slithery Fight 2,170, Portals 2,104, Trophy 1,986,
Trauma 1,959, Default 1,926, Autarky 1,886, Queen Of Spades 1,819, Devil 1,756, Prisoners Dilemma 1,696; **the seven
non-ladder maps are back since 2 Oct:** Australia 572, Islands 563, Around UNSW 562, Maze 525, weakhold 454, Stripes 445,
Tower Defense 417.

**Decoded post-change side-games by cohort (ladder 00:53Z):** old maps — top10 993, r11–30 1,980, r31–50 767, other 2,441, us 486
(14265); new maps — top10 1,067 (489 ranked, 1 % vs us), r11–30 277, r31–50 221, us 271 (15 × 14265 + 256 × 14585 = carthage-05,
live since 2 Oct 04:22Z). Decode order: post-m2 first, top-ten sides balanced over team × map, then the rest.

## Gaps (requests to the director)

- **No ladder snapshot since 06:21Z.** Cohorts and Elo at game time are stale for every post-change game.
- **Five of the top ten have no post-change games.** Please raise the collector targets for forgot to mention, SSS,
  cheji bt, PPP and Cache me outside. They are needed for the post-change top-ten references.
- **Team 7 has played no post-change games.** That is expected while the submission is paused.

## Side tables (antioch, not in the s1 store yet)

- `tools/antioch/era.py`: per-game era signals (sprint pricing, queen field, engine verdict).
- `tools/antioch/queen.py`: per-side queen and endgame rows. Output: `build/antioch/queen.parquet`.


## Current Himeji ownership and versioned refresh — 2026-10-03 22:38 UTC

User reassigned live-data connection/download oversight and analysis to Himeji on4October. Historical Antioch
snapshot above is preserved. Existing shared hub collector remains sole downloader; database read-only access
verified, continuous downloads40/pass with0errors in inspected passes. Freeze113,915games at22:23Z3Oct;
ladder221421Z top306/91/264/213/952/842/552/87/82/566. Eight top10 directchecks stale>24h;catch-up ongoing.
Legacy `build/s1/corpus` unchanged. Fresh pinnedFRAME_VERSION7store:
`/Users/alik/Documents/Codex/2026-10-01/p2-a-analyst-one-claude-opus/work/himeji-live-store`.
Metadata113,915;decoded119recent currenttop10/us games,238sides;0errors/238officialwinneragreements.
Window03:43:50–22:16:32UTC3Oct;17APImaps/18labels. Balancedcoverage sample,31eligiblegames stillqueued inthisfreeze;
no sharednorm rebuild. Sourcehashes and scope: `tools/himeji/unit10_audit/`; report `docs/findings/2026-10-04-himeji-resumed-live-data-and-top-team-regimes.md`.


## Himeji refresh — 2026-10-03 23:08 UTC

Freeze22:52:55Z:114,593games, latest22:51:49Z; ladder224700Z current IDs306/264/91/213/87/842/82/952/566/552.
Existinghub SQLite read-only connection/cycle healthy;40downloads/pass,0errors inspected. Directchecks264/91 still~32hstale
because refresh excludes below-target teams; focused patch prepared, NOT deployed. Other8leaders caught up.
Separate pinnedv7 store now331games/662sides (212new,0errors), all662winnerlabels match official index;
window2Oct23:13:00Z–3Oct22:50:10Z,365current-top10sides/7own,18decoderlabels. Balancedcoverage sample, notcensus.
Legacy store/norms unchanged; no running worker. Source/selectedIDs/freshness manifests `tools/himeji/unit11_audit/`;
finding `docs/findings/2026-10-04-himeji-live-queen-audit-and-growth.md`. Era post123; not new stable reference percentiles.


## Himeji refresh — 2026-10-03 23:36 UTC

Freeze23:23:29Z index115442games/lateststart23:22:18Z, ladder231820Ztop306/91/264/213/842/952/87/82/55/566.
Ownpost747games=208ranked+539unranked; lastown22:57:22Z. Registry14585active(Carthage05),14265idle; no deploymentaction.
Corpusowncoverage isopponent-derived: watch_list removesownteam. LiveDBgames1280rows/0currentown-submissionrows is
notcorpuscoverage. Directtop264/91 checksremain~32hstale. H11-05patchpending; no secondcollector.
Versionedv7store423games/846sides,92new/0errors,846officialwinneragreements,latestdecoded23:11:43Z.
472current-top10sides/12own; coverage sample,110selectedgamesremaininfrozenunit12queue. Legacy/norms untouched.
Pinnedsource/snapshot/queue manifests tools/himeji/unit12_audit/; report `docs/findings/2026-10-04-himeji-live-coverage-and-L10-ruling.md`.


## Himeji versioned-store refresh — 2026-10-04 01:40 UTC

Finished the frozenunit12 queue:110new/0errors in412s, one worker. Ownv7store533games/1066sides;
330ranked/203unranked,18decoderlabels,1066official-indexwinneragreements,allpost123 cutoff1Oct06:00Z.
Window2Oct23:13:00Z–3Oct23:11:43Z; metadata115442/unit12snapshot and its selected cohort remain frozen.
Perteam/map/mode counts tools/himeji/unit16_audit/store-coverage.json; source/lastbuild hashes in same folder.
Raw unit16freeze117411at01:23:26Z/latest01:19:09Z;ladder011517Z264/306/91/213/87/55/566/952/842/507.
Currenttop10 storedsides538/own12; coverage sample,notcensus. No activewriter; oldS1/norms untouched.
Solecollector35400healthy40/32/34perpass0errors;SQLite read-only healthy. H11-05/H12-05coverage requests pending.
Public fertility metadata unavailable in10inspectedheaders; do not interpretallzerosasno beds. Report `docs/findings/2026-10-04-himeji-pocket-cap-legality-and-fertility-correction.md`.


## Himeji versioned refresh — 2026-10-04 02:08 UTC

Unit17freeze117879games at01:53:15Z/latest01:51:48Z;ladder014638Z top264/91/306/213/566/952/55/842/87/507.
OwnFRAME7store533→663games/1326sides,130new0errors162s,459ranked204unranked;allpost123 cutoff1Oct06:00Z.
All1326sidewinnerlabels matchofficialindex;18labels,window2Oct23:13Z–4Oct01:45:11Z;680currenttop10sides/21own.
Metadata117879 frozenunit17;399selectedgamespending,notfieldcensus. No activewriter,legacyS1/norms unchanged.
Query tools/himeji/store_coverage.py; counts/source/queue in tools/himeji/unit17_audit/. Solecollectorhealthy40/pass0errors,
DBread-onlyhealthy14585active. Raw+468/0newowngames;extra9ownstoredsidesareolderbacklog. H11-05/H12-05pending.
- The decode backlog (20,850 games) is CPU-bound in the VM; a native `nice -n 15 python3 tools/chongqing/decode.py --jobs 6
  --time 3000` from the repo root on the Mac would clear it in under an hour (the user declined for now).
- Collector: Himeji reports 264/91 checks ~32 h stale and own-team games arriving only via opponents (H11-05/H12-05) — the
  director's call; nothing here pulls.
- Queen backfill of the 2,862 old-map games is deprioritised behind post-m2 decoding (old maps are no longer played).


## Himeji refresh — 2026-10-04 02:38 UTC

Rawfreeze118497at02:23:03Z/latest02:19:17Z,ladder021804Z top264/306/213/91/952/842/87/55/507/566.
Versionedv7store663→754games/1508sides,91new0errors332s;549ranked205unranked,allpost123,all1508winnerlabelsagree.
Window2Oct23:13–4Oct01:45:11Z,18maplabels,currenttop10sides778/own22. Metadata still117879/frozenunit17;
308selectedgamespending;resumeexistingqueue. Openingreferencefreeze708games preservedseparately(504rankedgames).
Query/source/counts tools/himeji/unit18_audit/;coverage via tools/himeji/store_coverage.py. Noactiveworker;
legacyS1/norms untouched. Solecollector35400healthy40/pass0errors;DBreadonly14585active. Fivefreshowngames
receivedviaopponent217,one01:22Zrankedseries;notyetinreferencefreeze. H11-05/H12-05coverage requests pending.
