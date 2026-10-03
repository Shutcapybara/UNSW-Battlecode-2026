# chongqing — P2-A Claude analyst (Opus 5.5), replay lead, wave 2 (from 4 Oct 2026)

Worktree `../wt-chongqing` (Mac, via the Cowork VM; `build/` and `public_replays/` symlinked to the main checkout), branch
`r/chongqing`, tools `tools/chongqing/`, findings `docs/findings/<date>-chongqing-*.md`. Cadence: one unit of work, one
hour off, repeat (user's instruction, to conserve credits). No API calls; GPT's analyst pulls replays this wave, so this
lineage only decodes what the hub collector has already written.

## Top — read this first (2026-10-04 00:20 UTC)

- **Ladder reset 1 Oct 06:21Z–17:09Z**: everyone to 1500; ranks are post-rules-only; store cohorts are post-reset (top
  ten: 306 Vibing++ (ex-Cutlery), 264, 91, 213, 87, 842, 82, 952, 566, 552). Stockfish/PPP gone, cheji bt idle.
- **hb1-14 live kills its queen at r0 on Schooltime in 31 % of games** (edge 2×2 spawn's r0 split; replays 996205,
  887973). 10.8 % of our live games are queen-decided and we lost 71/73. Schooltime 38 % / Trauma 40 % queen-decided.
- **Top four keep queens against us** (SSS 0.53, Sponge 0.70, Vibing++ 4/4 on 2 Oct unranked; Vibing++ 0.23 ranked 1 Oct).
- Store: 3,535 / 23,035 post-change in-scope games; VM decode ~65 games per call; queen columns added to `sides`.
- Finding: `docs/findings/2026-10-04-chongqing-era-ladder-queen.md`. Targets: `docs/hub/TARGETS.md` § chongqing.

## Environment

- VM: aarch64 Linux, 4 vCPU, 3.9 GB; python3.10 with `build/s1-pylib` (duckdb 1.5.6, pandas, pyarrow). `tools/s1/q.py`
  takes minutes to bind over the mount (series views + describe); use `tools/chongqing/qq.py` (post parts only, ~6 s).
- Decode: `nice -n 5 python3 tools/chongqing/decode.py --jobs 4 --time 75` per call (≤ 180 s; flushes every 40 games).
  Never run a decode and a query in the same call window.
- Git: the VM has no GitHub credentials; the worktree was created by hand (git 2.34 refuses `worktree add` because the
  other worktrees' Mac paths are invalid in the VM); `.git/worktrees/wt-chongqing/gitdir` holds the Mac path, the
  worktree's `.git` file a relative path, so both sides read it. Pushes go through the keeper (`hub-state/control/git.json`
  `push_branches`). `build`, `public_replays` symlinks are in `.git/info/exclude`.
- The main checkout's `.git/worktrees/wt-chongqing/_stale/` holds one stale `index.lock` (cannot delete from the VM).

## Live hypotheses

| id | claim | status | falsifier | size | suits |
|---|---|---|---|---|---|
| H-C1 | hb1-14's r0 split of the edge 2×2 queen on Schooltime kills it (31 %) — bug | posted unit 1, 0.9 | child's Schooltime `q_death_round=0` rate not < 2 %, or queen-decided Schooltime losses not down from 36 % | Schooltime, 2 × 48 games | any tester, now |
| H-C2 | the queen tiebreak is our largest loss mechanism on Schooltime/Trauma; a merely surviving queen flips most | posted, 0.7 | queen alive ≥ 0.5 on those maps without ranked win +10 pp | 2 maps, s1–3, both panels (~300 pairs) | Claude tester (carthage-10 built) |
| H-C3 | Default's spawn is half a pocket: 22–36 % of queens die by r5; a reach-keyed first-five-moves rule fixes it | posted, 0.5 | no structural feature separates dead/alive r5 queens | engine probe + 100 Default games | me (probe), any tester |
| H-C4 | queen hunting pays now vs the top four | watch, 0.4 | ranked top-ten RL queen survival stays < 0.10 | corpus watch (2–3 Oct bulk) | — |

## Queue (next units, in order)

1. Decode batches every unit (top-ten sides first); republish CORPUS.md; re-run §3/§5 on the ranked 2–3 Oct bulk.
2. Queen backfill (decode-only) for Antioch's 2,862 games → `q_len` trajectories; who feeds the queen (q_len@400, q_moves).
3. Opening components on the post-reset top ten at r25/r50 (series view), per Esquie cluster, incl. the seven returned maps.
4. H-C3 engine probe on Default's spawn; Default/Trophy queen hazard by position.
5. Readings of tester results as they land; answer board questions addressed to me.

## Log

- 2026-10-03 22:30 UTC — launched; protocol, summaries, board, TARGETS, ledger read; worktree built by hand.
- 2026-10-03 23:00 UTC — ladder reset found; `build.py games` patched; decode wrapper; first batches (team 7).
- 2026-10-03 23:20 UTC — queen columns added to `sides`; `qq.py` connector.
- 2026-10-04 00:20 UTC — unit 1 published: finding, TARGETS § chongqing, CORPUS.md, board C1-01…07. Sleeping one hour.
