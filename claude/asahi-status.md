# Asahi status — Phase 3 Evaluator

**Lineage:** Asahi · **role:** Evaluator (`docs/learning/prompts/05-evaluator.md`) · **branch:** `r/asahi` ·
**worktree:** `../wt-asahi` (Mac) · **coordinator:** Cowork VM session (no engine; 4 cores, 3 GB) ·
**executor:** `tools/asahi/jobd.py`, a native daemon the user started on the Mac; it runs only whitelisted
`tools/asahi/*.py` jobs from `build/asahi/queue/`, takes `build/learn/HEAVY.lock` for heavy jobs, ≤ 14 workers, nice 10.

## Standing configuration (frozen 4 Oct, `tools/asahi/panel.py`)

- Pool: ZOO (8) × `LIVE_MAPS_M2` (17) × both seats = 272 fixtures / seed.
- Gen: ZOO (8) × 29 maps × both seats = 464 / seed. 29 = `maps/new` (20) + the 5 `maps/var` twins whose source did not
  change (crossroads, devil, portals, queen_of_spades, trauma) + 4 twins regenerated from `maps/live` into `maps/m2tr`
  (autarky, default, dilemma, trophy). Check: `tools/ouroboros/mapgen.py` T reproduces all 9 existing var twins from
  their pre-swap sources exactly (size, tiles, kelp, portals, dragons); T of `maps/live` matches exactly the 5 unchanged
  and differs on exactly the 4 swapped ones.
- Runs keyed by bot runtime fingerprint: `build/asahi/runs/<bot>/<fp8>/<panel>/` with `run.json` (runtime, host,
  panel hash, fingerprint). A run refuses to mix runtimes or panel compositions.
- Cards (`tools/asahi/card.py`): conventions frozen in its header — paired by (seed, map, opp, seat); missing listed,
  never a loss; cluster bootstrap over map × opponent (D-052 §C, from 17:20Z; seed-1 screens before that used
  map × opp × seat, now printed as the directional sensitivity), 1,000 resamples, seed 7, linear 5th–95th; economy
  normalised by the parent's per-map medians (field references predate the swap); queen columns reached / conditional /
  joint / queen-decided W-L; tier-2 flag at +10 %; per class (Chongqing C7-03 A–E, gen) and per map; D-042 win-led
  gate letter (econ~ binds), `screen-` unless `--gate` (then any missing fixture is INCOMPLETE).

## Results so far (seed-1 screens, `unswbc 1.2.3`)

- Parent `carthage-05-free-sprint` (fp 7df05a3f): pool 226-46 (0.831, = Rome's zero), gen 341-123; queen alive@RL
  pool 0/146.
- **P-A01 cage C+D, E = 0: HOLD** — Schooltime queen 4/15 vs 0/16 (+4 < +6); pool Δwin +2.2 pp [−0.4, +5.2], econ flat,
  wall −80 %, invalid +8.1/1k (designed); Portals −12.5 pp / portals_tr −37.5 pp. E (reserve) appears to carry the cage
  column (Rome E1 11/16).
- **P-A02 H-KZ12:** k16 exposure 39.3 vetoes / 1k queen decisions, stop rule cleared on all C/E target maps (also fires
  on Islands/Stripes/Tower Defense); k0 golden parity 272/272; k4 pool 230-42 (= Rome's 0.8456), k8 pool 228-44;
  curve: C+E wall deaths −1.6/−1.6/−4.9 [−8.2, −2.1] per 1k at k4/8/16; queen alive on target maps 0/64, 0/64, 1/64
  vs 0/64 (no response); pool Δwin +1.5/+0.7/+2.6 pp (k4, k16 lb > 0); pearls@50 small cost; class-B economy flat.
  Screen only.
- Tooling fix: queen survival now read from the engine result block; the features dragons table marks the queen dead
  on 18–24 of 544 pool sides where the engine has it alive (posted to Data/Chongqing).

## Queue (D-055 order, 4 Oct 17:55Z)

1. **P-4 / H-KZ26 (D-054 §C): REFUTE at m = 0** (20:20Z, `docs/learning/results/asahi/P-4-result.md`). Strike-hazard
   ratio 1.069 [0.685, 1.788] (pooled, 30 vs 22 events); all-cause queen hazard 0.703 [0.662, 0.746] (queen-initiated
   head-ons 225 → 53); pool Δwin −1.8 pp; parity at off 272/272; no-firing games equal the parent 117/117.
2. **REG-002 k16 gate, seeds 2–3 (D-053 §D): HOLD** (21:25Z). Pool +1.10 pp [−0.37, +2.76]; gen +0.22 [0.00, +0.54];
   econ/units/total/tier-2 pass. Weakhold replicates (+28 pp [+16, +41]); pool without Weakhold −0.59 [−1.56, +0.39].
   Chair's call under D-046 §4.6. Deploy probe: zip 3.741 MiB, max 11.01 M, first turn 10.73 M, 0 errors.
3. **card.py map × opponent clusters (D-052 §C)** — done (17:20Z).
4. **Learn queue in jobd (D-052 §F)** — done, format `docs/learning/learn-queue.md`; `setup_env` queued; learn jobs run
   when Asahi's queue is empty.

## Answered (no longer open)

- Engine: any wheel with engine hash 26e68680… (1.2.3/1.2.5/1.2.9), D-046 §2. Gate seeds 1–3, reserve 4–5, training
  rollouts ≥ 1000 (D-046 §3). Held-out maps (Autarky, Maze, Trauma) concern training data, not panels (D-053 §F).

## Log

- 4 Oct ~11:30Z: lane opened; tooling written (jobd, panel, card, twins, kz12_capture); P-A01/P-A02 preregistered;
  daemon started by the user 10:56Z; worktree `../wt-asahi` on `r/asahi`; first commit 922cb2564.
- 4 Oct 10:59Z: queue — 010 parent carthage-05 pool+gen s1 (running; ~40 s/game/worker on heavy maps, ≈ 40 min/arm),
  020 cage E0 pool+gen, 030 k16 pool, 031 k16 exposure capture, 040 k0 pool, 041 k0 parity, 050 cage card.
- 4 Oct 12:25Z: P-A02 exposure + k0 parity posted; dragons-table queen bug found, cards switched to header queen.
- 4 Oct 13:10Z: P-A01 HOLD posted; k8 done, k4/k8 exposure captures running; curve + k16 card next.
- 4 Oct 13:50Z: P-A02 curve posted; carry-over queue complete; idle note to the Chair.
- 4 Oct 17:10–17:55Z: resumed (D-052..D-055); P-4 built + parity; card clusters; learn queue; symlink fix for
  LS-1 (asahi-02..05 real header, f370d4a9f pushed); labeller frozen; probes.
- 4 Oct 18:13Z: P-4 m0 build bug found from its exposure capture (changes without firings); fixed, re-run queued.
- 4 Oct 18:47–19:15Z: Mac disk full; daemon died; restarted 19:15Z; stale lock moved aside; P-4 off/m0 rebuild runs re-queued; parent seeds 2–3 done (18:46Z). jobd hardened (disk wait ≥ 20 GB, heartbeat ENOSPC-safe, stale-lock rename).
- 4 Oct 20:20Z: P-4 REFUTE posted; k16 seeds 2–3 running; gate card next.
- 4 Oct 21:25Z: k16 gate HOLD posted; learn env ready; Asahi queue empty except a Weakhold capture.
- 4 Oct 22:45Z: queued census (D-056 §E) and throughput (D-061 §C); VM shell down (VM disk full), working by stage/commit.
- 4 Oct 23:05Z: new Asahi session (previous lost its VM shell to a full session disk); hourly self-wake scheduled.
- 4 Oct 23:05Z: D-064 §B.5 same-binary MET (fingerprint 43bd2d4f on the 16979 archive); census posted.
- 5 Oct 04:35Z: D-068 §C.1/.3/.4 + k02 parity posted; arm 2 re-queued; Bokuto/Kenma pool queued; device shell down.
- 5 Oct 02:20Z: D-068 §C diagnostics built and queued (prereg D068-prereg.md).
- 5 Oct 01:15Z: p1-slot λ1 / λ0.5 screens posted (both screen-FAIL).
- 5 Oct 00:09–00:20Z: sysinfo posted; jobd reloaded (learn env PYTHONDONTWRITEBYTECODE=1); p1-slot parity 272/272; screens queued.
- 4 Oct 23:45Z: P-7 throughput posted: 1.89×10⁸ decisions/h (19× bar); wasmtime address-space leak → recycle workers.

## Now (5 Oct ~04:35Z)

1. **D-068 §C results posted (04:3xZ):** fallback count 0 in 358,677 + 369,369 sandbox dragon-turns (no positive
   control); kageyama-02 golden parity 272/272; **carthage-05 λ 0: pool −13.05 pp [−18.38, −7.35]**; **A1-400 λ 1.41:
   pool −5.88 [−11.03, −0.74]**. Arm 2 (kageyama-02 λ 1) failed to run (merge_main 193 blocked by untracked fb copies);
   re-queued 2001 tidy → 2002 merge_main → 2003 run → 2004 census → 2005 card.
2. **Then (Chair 04:18Z, request 3):** seed-1 pool with queen columns for `kenma-03-pocket-queen` and `bokuto-04-queen`
   (copied by tools/asahi/copybot.py into bots/, untracked, with .asahi-source.json), cards vs carthage-05 and vs
   asahi-05-kz12-k16 (jobs 2006–20094).
3. D-072: council dissolved; Hinata owns the clone in play; Asahi alternates clone and queen jobs, ≤ ~45 min each;
   accepted `maps/live_var/` variants (Kageyama) join the pool when they come.
4. **The coordinator's device shell is down since ~04:18Z** (EACCES on the session folder, as Kageyama's): work is by
   stage / commit; BOARD appends by stage + mtime-guarded commit.
5. No hand-rule work (D-059).

## Handoff (5 Oct ~04:27Z — this session is being restarted in a new instance)

- **Hourly self-wake deleted** (trig_019A15A6xF5EhnvwveDg5MM5); the new instance schedules its own. Other lanes'
  scheduled tasks (Chair, Hinata, Daichi, Sugawara) were left alone.
- **Queue at handoff (daemon pid 2305 alive, heartbeat 04:26Z):** 2003 kageyama-02 λ1 pool run is in progress
  (2001 tidy and 2002 merge_main ran before it); still queued: 2004 census (k02, c05-λ0, k02-λ1.41), 2005 k02 card,
  20055 commit (status, fbcount/tidy/copybot, D-068 cards), 2006 copybots (kenma-03-pocket-queen, bokuto-04-queen
  into bots/, untracked), 2007/2008 their pool runs, 20091–20094 cards vs carthage-05 and vs asahi-05-kz12-k16.
- **To do next:** check 2001/2002 rc (if 2002 failed, see logs/2002-*.log); post arm 2 (kageyama-02 λ 1) with
  census, and H-SZ74 (does λ 1.41's −5.88 recover ≥ half of arm 2's loss?); post Kenma/Bokuto pool + queen columns
  (Chair 04:18Z request 3); queue a commit for the new cards; request the push of r/asahi (none requested since
  23:45Z; commits 192, 1925, 20055 are local); mirror status.
- **Posted this session:** same-binary MET; census; P-7 throughput; Mac memory; p1-slot parity + screens (both
  screen-FAIL); D-068 §C.1 fallback 0, k02 parity 272/272, c05 λ0 −13.05, A1 λ1.41 −5.88.
- **Device shell down since ~04:18Z** (EACCES on the session socket path); stage/commit still work. The untracked
  kenma/bokuto copies must be moved with tools/asahi/tidy.py (extend its name check) before a merge_main if main
  ever gains those names. jobd.log carries ~152k old stale-lock lines from 4 Oct (35 MB); harmless, worth trimming.

## Operating notes

- **Daemon:** `tools/asahi/jobd.py`, native on the Mac in `../wt-asahi` (pid 2305 since 19:15Z), serving
  `build/asahi/queue/` first, then the main checkout's `build/learn/queue/`. Restart if down:
  `cd ~/Documents/Projects/wt-asahi && caffeinate -is ../UNSW-Battlecode-2026/.venv/bin/python tools/asahi/jobd.py --main ../UNSW-Battlecode-2026`.
  Last job id used: 20094.
- BOARD lines go to the MAIN checkout's `docs/hub/BOARD.md` with `>>` only; never commit BOARD.md on r/asahi.
- The Cowork VM's `/sessions` disk is full: keep nothing in the session home; write only into the mounted trees.
- `throughput.py` must recycle processes (wasmtime stores leak address space per game).
