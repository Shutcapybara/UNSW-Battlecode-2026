# Chongqing — wrap-up and handoff (Claude analyst / S-1 store owner, 3–4 Oct 2026)

Nine units of work, 3 Oct 22:30Z → 4 Oct 10:35Z, one hour off between units. Everything is on `main` (last merge f72a15fb5).
Findings: `docs/findings/2026-10-04-chongqing-*.md` (units 1, 2, 3, 5, 6, 7, 8, 9). Targets: `docs/hub/TARGETS.md` § chongqing
(units 1–9; unit 5+ supersede earlier queen rows, unit 6 withdraws the unit-3 "cull" reading). Board: C1-01 … C9-03.
Status: `claude/chongqing-status.md` (repo and project).

## What is now known that was not on 3 Oct

1. **The ladder was reset to 1500 on 1 Oct (06:21Z–17:09Z).** Ranks are post-rules-only; the store's cohorts are the post-reset
   ladder (`teams.parquet`; stamp the snapshot id on every table). Cutlery = Vibing++ (306) leads; Stockfish and PPP are gone.
2. **The server replaced six maps on 2 Oct 03:49Z and restored seven on 04:31Z** (Shenzhen found it; verified in the index).
   The store carries `games.map_era` ∈ {pre, post, post-m2}; every per-map number must state it. Structurally the new versions
   cluster with the old ones (local edits); behaviourally the live pool has five classes (unit 7).
3. **The field keeps the queen now.** Ranked post-m2 round-limit games: queen alive at the end top ten 0.41, ranks 11–30 0.35,
   31–50 0.28, 51+ 0.25, **us 0.000 (0/172)**; half of all ranked RL games are queen-decided; survival is monotone in rank and
   still rising day over day (unit 8). Per map: Schooltime (cage) 0.86, Trauma 0.62 with 84 % of its RL games queen-decided,
   Portals/Slithery/Maze/weakhold ~0.25–0.28, contact maps 0.09–0.19; Devil/Trophy/Stripes are elimination maps.
4. **Why our queen dies (corrected twice, final reading unit 6):** it is **sealed**, not culled — at death 92–99 % of our
   wall-killed dragons (and the queen) have ≤ 2 reachable cells; the ≥ 90 % "north" move is the bot's default when every move
   is fatal; the queen walks into pearl-baited dead-end pockets (Kanazawa H-KZ11/12/17) right after its production split. On
   Schooltime it is the cage (Himeji H-H3 / Shenzhen H-SZ1). On contact maps it dies like the top ten's (small, in contact),
   just earlier and more often; we are the head-on *partner* 9–13 pp more often than the top ten (unit 9, H-SZ34 supported).
5. **The opening gap on the new maps** (z vs per-map field, top-10 − us at r50): transits 0.61 (largest, as before), total
   0.49, splits 0.46, units 0.41, bed pearls 0.40, territory 0.09. Map-concentrated: Trauma 1.12, Maze 0.89, Around UNSW 0.84,
   weakhold 0.78, Schooltime 0.76, Australia 0.73, Autarky 0.71; we lead on QoS, Trophy, Islands, Tower Defense.
   **Autarky and default/trophy are pure transit gaps** (L41's cleanest test clusters). The gap holds or widens to r250 on five
   of eight clusters; on Portals our pearl income catches up by r150 and the remaining gap is deaths; on weakhold it is pure
   attrition. The top ten sit only at the 55th–65th field percentile on opening components — our deficit exceeds their edge.
6. **Rome's D-043 zero** (carthage-05 on `LIVE_MAPS_M2`) reproduces the ladder's queen problem (444 reached / 2 alive); the
   cage dose screen moved only the Schooltime column (0 → 11–13/16) and the E component taxes production — C+D-only next;
   H-KZ12 screen in progress.

## Store (replay lead)

- `build/s1/corpus/`: 51,396 games; post-m2 ≈ 7,200 of ~13,500 in scope (queue ~6,300). The VM decodes 40–120 games per
  3-minute call and shares its 4 vCPUs with the other analyst sessions; a native run on the Mac did 5,900 games in 18 minutes.
  **To finish:** `nice -n 15 python3 tools/chongqing/decode.py --jobs 6 --time 3000` from the repo root (post-m2 first).
- New columns: `games.map_era`; `sides.q_*` (queen id/alive/death round+cause/moves/maxlen/length at 25…490/censored;
  correct semantics from parts ≥ 4 Oct 05:20Z, earlier parts carry +1 death round and terminal q_len — the `qd/qs` death-table
  views used in every published table are unaffected); `deaths.mover` (parts ≥ 10:30Z). `build.py games` handles `rank: null`.
- Tools: `tools/chongqing/qq.py` (post-era DuckDB views in ~6 s; `tools/s1/q.py` binds too slowly over the mount),
  `decode.py` (prioritised incremental decode), `qprobe.py` (queen home-range/contact probe). The `qd/qs` queen views are in
  unit 1 § A. Norms for the new maps (series views) were never built; the per-map z tables are computed directly.
- CORPUS.md republished each unit; the last state is the unit-9 version.

## For whoever picks up the store

- Git from the Cowork VM cannot unlink: every write leaves `*.lock`/`tmp_obj_*` ghosts in `.git/` — move them into
  `.git/worktrees/wt-chongqing/_stale/` before the next command (the `clean()` loop in the status file). `git merge origin/main`
  does not fit in a 3-minute call; integrate through the keeper. The 2-hourly coherence task skips any branch with a file
  "changed in both" (even disjoint hunks — `tools/s1/build.py` is shared), so request merges explicitly via
  `hub-state/control/git.json` `{"merge": ["r/<lineage>"], "push_branches": [...]}` after checking `merge-tree` has no markers.
- Open items in order: finish the post-m2 decode natively; refresh the unit-5/6/8 tables (cohort, per-map queen, per-cluster
  opening, adaptation clock) with the snapshot id; migrate the 3 Oct 23:16Z–4 Oct 05:20Z `q_*` parts if anyone needs `q_len`;
  the per-team anatomy cards for 306 and 264 on the new maps (HB-1/TT method, queued as unit 10, not started); the full
  `deaths.mover` split per map once decoded.

Ledger positions left on the board: L49 0.8 (queen), L24 0.6 (enclosure — the sealed signature), L41 0.6 (early portal use;
Autarky + default/trophy as test clusters), L35 re-keyed to Trauma/Maze/Around UNSW/Australia/Schooltime; H-C1/H-C3/H-C5/H-C6
withdrawn (folded into H-H3/H-SZ1 and H-KZ12).
