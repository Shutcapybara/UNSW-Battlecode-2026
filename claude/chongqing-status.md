# chongqing — P2-A Claude analyst (Opus 5.5), replay lead, wave 2 (from 4 Oct 2026)

Worktree `../wt-chongqing` (Mac, via the Cowork VM; `build/` and `public_replays/` symlinked to the main checkout), branch
`r/chongqing`, tools `tools/chongqing/`, findings `docs/findings/<date>-chongqing-*.md`. Cadence: one unit of work, one
hour off, repeat (user's instruction, to conserve credits). No API calls; GPT's analyst pulls replays this wave, so this
lineage only decodes what the hub collector has already written.

## Top — read this first (2026-10-04 04:30 UTC)

- **Unit 4:** D-043 read (`maps/live/`, `LIVE_MAPS_M2`, parent carthage-05; byte identity done by Nara/Shenzhen/Himeji; Nara takes the
  per-hash queen gap, Himeji the loss-share intervals). `q_len@k` semantics fixed (NULL past game end, `q_censored`; Himeji H19-05).
  **The VM is saturated (3.9 s/game; shared with the other analyst sessions): the s1 post-m2 decode has stalled at ≈ 1,320 games.**
  `git merge origin/main` cannot complete in a VM call (273 files); r/chongqing stays on 0298966ec, integrated by the coherence task.

- **Unit 3: our bot culls its own queen.** On the new corridor/portal maps our queen dies by wall (Trauma 0.61, Portals 0.88,
  Maze 0.67, weakhold 1.00 at r29/r44), 74 % within 5 rounds of its own production split; our culls are north-into-kelp walks
  (≥ 90 % of our wall deaths; chronic since 13010). H-C5: exempt ids 0/1 from the cull — prerequisite for every L39/L49 arm.
  Per-new-map queen table in TARGETS § chongqing (unit 3): nine of 17 maps are queen maps; Devil/Trophy/Stripes are not.

- **Map swap 2 Oct 03:49Z** (six maps new, seven back at 04:31Z): store `games.map_era` ∈ {pre, post, post-m2}; per-map
  references must state it. Live is carthage-05 (14585) since 2 Oct 04:22Z. H-C1 = the new Schooltime cage (0/51 old map,
  22/22 new), still our bug (we neck-step where keepers split-and-patrol); local fixtures run old maps. H-C3 withdrawn.
- **Post-m2 ranked field keeps queens: top ten 0.444 alive at RL end, r11–50 0.27–0.29, us 0.000; half of RL games
  queen-decided.** H-Q4 trigger fired. carthage-05 live: win 0.313, 20 % of games lost on the queen, Schooltime 0.87.
- Division with Shenzhen (other Claude analyst): chongqing owns `build/s1/`, CORPUS.md, field references/TARGETS table;
  Shenzhen works hypotheses from `build/shenzhen/`.
- **Ladder reset 1 Oct 06:21Z–17:09Z**: everyone to 1500; ranks are post-rules-only; store cohorts are post-reset (top
  ten: 306 Vibing++ (ex-Cutlery), 264, 91, 213, 87, 842, 82, 952, 566, 552). Stockfish/PPP gone, cheji bt idle.
- **hb1-14 live kills its queen at r0 on Schooltime in 31 % of games** (edge 2×2 spawn's r0 split; replays 996205,
  887973). 10.8 % of our live games are queen-decided and we lost 71/73. Schooltime 38 % / Trauma 40 % queen-decided.
- **Top four keep queens against us** (SSS 0.53, Sponge 0.70, Vibing++ 4/4 on 2 Oct unranked; Vibing++ 0.23 ranked 1 Oct).
- Store: 45,165 games; post-m2 ≈ 1,250 of 11,852 in scope; VM decode 50–120 games per call (two 60 s batches per call).
- Findings: `docs/findings/2026-10-04-chongqing-era-ladder-queen.md` (unit 1), `…-chongqing-unit2-map-era-and-field-queens.md`.
  Targets: `docs/hub/TARGETS.md` § chongqing (unit 2 supersedes unit 1 § 5).

## Environment

- VM: aarch64 Linux, 4 vCPU, 3.9 GB; python3.10 with `build/s1-pylib` (duckdb 1.5.6, pandas, pyarrow). `tools/s1/q.py`
  takes minutes to bind over the mount (series views + describe); use `tools/chongqing/qq.py` (post parts only, ~6 s).
- Decode: `nice -n 5 python3 tools/chongqing/decode.py --jobs 4 --time 60 --flush 20` per call (≤ 180 s). Never run a decode
  and a query in the same call window. Throughput 0.6–4 s/game depending on the other sessions sharing the VM; skip when > 3.
- Git in the VM cannot unlink: every write op leaves `*.lock` / `MERGE_HEAD` behind in `.git/worktrees/wt-chongqing/` — `mv` them
  into `_stale/` before the next git command. Merges of main do not fit in a call; do not attempt.
- Git: the VM has no GitHub credentials; the worktree was created by hand (git 2.34 refuses `worktree add` because the
  other worktrees' Mac paths are invalid in the VM); `.git/worktrees/wt-chongqing/gitdir` holds the Mac path, the
  worktree's `.git` file a relative path, so both sides read it. Pushes go through the keeper (`hub-state/control/git.json`
  `push_branches`). `build`, `public_replays` symlinks are in `.git/info/exclude`.
- The main checkout's `.git/worktrees/wt-chongqing/_stale/` holds one stale `index.lock` (cannot delete from the VM).

## Live hypotheses

| id | claim | status | falsifier | size | suits |
|---|---|---|---|---|---|
| H-C1 | r0 queen death on Schooltime | **corrected unit 2**: the new map's cage; folded into Himeji's H-H3 (legal r0 split → child sacrifice → patrol) | — | needs live maps (unswbc ≥ 1.2.6) | Rome/any tester |
| H-C2 | the queen tiebreak is our largest loss mechanism on Schooltime/Trauma; a merely surviving queen flips most | posted, 0.7 | queen alive ≥ 0.5 on those maps without ranked win +10 pp | 2 maps, s1–3, both panels (~300 pairs) | Claude tester (carthage-10 built) |
| H-C3 | Default early queen deaths | **withdrawn unit 2** (old map; new Default 0/17) | — | — | — |
| H-C4 | queen hunting pays now | **trigger fired unit 2** (top ten 0.444 alive); lane is Shenzhen's H-SZ5/H-SZ14 | — | — | — |
| H-C5 | exempt the queen (ids 0/1) from the cull — our queen is culled north-into-kelp within 5 rounds of its first split | posted unit 3, 0.85 | alive@RL-end < 0.15 on Trauma/Portals/Maze/weakhold after the exemption, or econ lb < −0.03 | 4 maps × s1–3 both seats, live maps | Claude tester / Carthage lineage |
| H-C6 | the north-into-kelp cull wastes corpses (recovered 0.68 vs top ten 0.78); cull in place beside an ally | posted unit 3, 0.6 | corpse_recovered_share not ≥ +0.05 | pool + gen s1–3 | any tester |

## Queue (next units, in order)

1. Decode post-m2 (top-ten sides first) every unit; republish CORPUS.md; refresh the post-m2 ranked table.
2. New-map norms: per (map, map_era) field medians/SDs for the series/sides views once ≥ 300 games per new map; then the
   opening components (S-1 Q3) top-10 − us on post-m2, per map and Esquie cluster (clusters need re-checking on the new maps).
3. Per-map post-m2 queen hazard (death round/cause by map_hash and seat) — the geometry half for the testers.
4. Queen backfill of old-map games only if someone needs q_len on old maps (deprioritised).
5. Readings of tester results as they land; answer board questions addressed to me.

## Log

- 2026-10-03 22:30 UTC — launched; protocol, summaries, board, TARGETS, ledger read; worktree built by hand.
- 2026-10-03 23:00 UTC — ladder reset found; `build.py games` patched; decode wrapper; first batches (team 7).
- 2026-10-03 23:20 UTC — queen columns added to `sides`; `qq.py` connector.
- 2026-10-04 00:20 UTC — unit 1 published: finding, TARGETS § chongqing, CORPUS.md, board C1-01…07. Sleeping one hour.
- 2026-10-04 04:30 UTC — unit 4: D-043 read; q_len semantics fix; board C4-01…04; decode stalled (VM 3.9 s/game); merge of
  origin/main abandoned (mount too slow); no new tester results to read. Sleeping one hour.
- 2026-10-04 03:25 UTC — unit 3: per-new-map queen hazard table; the cull mechanism (C3-01), H-C5/H-C6; readings Rome 03/04;
  +65 games (VM slow). Sleeping one hour.
- 2026-10-04 02:00 UTC — unit 2: map swap verified, `map_era` in the store, +837 games (post-m2 first), post-m2 ranked
  queen table, H-C1/H-C3 corrected on the board (C2-01…07), finding 2, TARGETS unit-2 section. Sleeping one hour.
