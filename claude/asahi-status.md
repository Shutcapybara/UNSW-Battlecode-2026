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

## Queue (default order; the Chair may reorder)

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
