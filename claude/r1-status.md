# R-1 status — search-depth ladder on Ares (Lune lineage, Claude Opus 5.5)

**State (30 Sep):** complete; finding at `docs/findings/2026-09-30-r1-search-ladder.md` (addendum included).
The flood-only and sprint-only arms at 8× are inert through r100. The whole-map late search is identical to the
late cap at 384, so the late cap saturates by 384.

## Results

**Step 0**

- V06 is the base. It is flat against V05 on the pool (seed 1 +0.022 expected score, seed 2 ±0).
- It is clearly better off-pool: generalisation panel +0.067 expected score, +7.3 % economy, +13 % dragons@100 and
  +14 % length@100.
- The atlas is dead code (`atlas_try()` is never called).

**CPU**

- The worst turn is 8.5 M points at L0 and 9.3 M at L3.
- With all caps unbounded the ceiling is 22.4 M. The 60 M wall is unreachable with this search design.

**Ladder (z1 seed 1)**

- Every level gains the late economy (p@250 +0.11 to +0.13) and loses win rate (−0.106, −0.087, −0.037).
- From 4× the opening is lost too. No level passes the gate.

**Decomposition**

- The search node cap alone at 8× reproduces L3 almost exactly.
- The split is by phase: searching wide before round 40 costs the opening; searching wide after it pays.

**Recommended:** `lune-r1-07-latecap8x-only`

- The only change is the search cap after round 40, 48 → 384.
- On the pool over seeds 1+2: economy +0.026, dragons@100 +0.053, length@100 +0.046, hygiene −2 %, win rate −0.016
  (not significant).
- On the generalisation panel: +2.5 % economy, +2.7 % dragons, +3.3 % length, identical W–L.
- It misses the +0.05 economy gate, as V06 did. It is ready for `register.json` as a dev-screen candidate; it has not
  been registered.

## Notes for others

- **Tooling.**
  - `tools/lune/run.py` is a budgeted, resumable, shardable panel runner whose rows match `bench.py`.
  - `tools/lune/arena_lune.py` is a copy of the cx arena that also emits p@50, p@150 and p@250. The cx arena drops
    them, so `tools/cx/benchmarks_table.py` shows only r100.
  - `tools/lune/score.py` is a single-command scorecard with deltas against a base arm, both panels, tier 2, paired
    sign tests and CPU.
- **Metric discrepancy for R-4.** The arena-based and replay-extractor-based normalised levels differ by about 20 % on
  identical games (V05 dragons@100 1.28 vs 1.071).
- **Mac-side VM.** It cannot run native panels: about 3.9 GB of RAM, OOM-killed under other sessions' load, and a
  180 s call limit. It works for sandbox probes if `TMPDIR` and `XDG_CACHE_HOME` point into `/tmp` (the `/sessions`
  volume is full).
- **No commits yet.** Nothing is committed on `r/r1`: git in the VM cannot remove `.git/index.lock` and the
  worktrees point at `/Users` paths. Files are in the working tree for a Mac-side commit.
- **Next.**
  - R-5 should own `search_cap_late` and `search_cap_late_from` as weights.
  - Build a continuous selector: a cap scaled by the pearl sparsity each dragon observes.
  - Propose a phase-aware gate that scores the checkpoints in the phase that was changed.
