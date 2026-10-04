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
  never a loss; cluster bootstrap over map × opp × seat, 1,000 resamples, seed 7, 5th–95th percentile; economy
  normalised by the parent's per-map medians (field references predate the swap); queen columns reached / conditional /
  joint / queen-decided W-L; tier-2 flag at +10 %; per class (Chongqing C7-03 A–E, gen) and per map; D-042 win-led
  gate letter, prefixed `screen-` below three seeds.

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

## Queue (default order; the Chair may reorder)

**Carry-overs complete; idle, ready for ladder gates (4 Oct 13:50Z).**


1. P-A01 cage C+D, E = 0 vs carthage-05 — preregistered (`docs/learning/proposals/P-A01-cage-cd-e0.md`).
2. P-A02 H-KZ12 dial k = 0/4/8/16 — exposure diagnostic on k16 first, golden parity k0, then the curve.
3. Ladder gates as the Learner hands candidates over (none yet).

## Open issues for the Chair

- **D-045 number collision.** `D-045` in the director log is already "Prospective 1.2.5 learned-arm local gate"
  (seeds 1–5, `--gate learned125`, pinned to `unswbc 1.2.5`). The Phase 3 prompts expect D-045 to be the Chair's
  first record (deadline, frozen splits, promotion/rollback). The venv runs `unswbc 1.2.3`; maps are the 1.2.9
  templates. The Chair needs to say which engine version gates use, and renumber.
- No frozen held-out fixtures exist yet (D-045 Phase 3 sense). Until they do, Asahi runs only the carry-over screens
  on seeds 1 (never seeds reserved later as held-out: the Chair should reserve seeds ≥ 6 or a map subset).

## Log

- 4 Oct ~11:30Z: lane opened; tooling written (jobd, panel, card, twins, kz12_capture); P-A01/P-A02 preregistered;
  daemon started by the user 10:56Z; worktree `../wt-asahi` on `r/asahi`; first commit 922cb2564.
- 4 Oct 10:59Z: queue — 010 parent carthage-05 pool+gen s1 (running; ~40 s/game/worker on heavy maps, ≈ 40 min/arm),
  020 cage E0 pool+gen, 030 k16 pool, 031 k16 exposure capture, 040 k0 pool, 041 k0 parity, 050 cage card.
- 4 Oct 12:25Z: P-A02 exposure + k0 parity posted; dragons-table queen bug found, cards switched to header queen.
- 4 Oct 13:10Z: P-A01 HOLD posted; k8 done, k4/k8 exposure captures running; curve + k16 card next.
- 4 Oct 13:50Z: P-A02 curve posted; carry-over queue complete; idle note to the Chair.
