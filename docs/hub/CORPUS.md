# Corpus and store — what is in them (replay lead: antioch)

As of **2026-10-01 12:40Z** (index), store build in progress. Republished after every build.

- **Corpus:** `public_replays/corpus/`. The hub collector on the Mac writes it under the shared API rate limit; the
  targets are in `tools/hub/config.py`. A copy is rsynced to the desktop (`wt-antioch`).
- **Store:** `build/s1/corpus/`, built on the desktop from the rsynced corpus with `tools/s1/build.py`.
- **Queries:** `tools/s1/q.py`. Set `S1_ERA=post` (or `pre`) to scope the views and the field norms to one rules era.
- **Era:** `games.era`. `post` ⇔ `started_at ≥ 2026-10-01T06:00Z`. The live server switched to unswbc 1.2.3 between
  05:57:53Z and 09:26:58Z (`docs/findings/2026-10-01-antioch-era-and-queen.md`).

| era | games in index | in scope (top-50 or us) | decoded in store | first start | last start |
|---|---|---|---|---|---|
| pre | 74,761 | 55,728 | 40,793 | 25 Sep 07:12Z | 01 Oct 05:57Z |
| post | 1,603 | 1,143 | building (`build.py corpus --era post`) | 01 Oct 09:23Z | 01 Oct 12:29Z |

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
