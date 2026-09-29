# R-4 status — tooling (GLM 5.3, worktree ../wt-r4, branch r/r4)

Task: `docs/hub/prompts/2026-09-29-R4-tooling-glm.md`. No bots; four parts, each its own commit.

## Log

- **2026-09-29 Part 1 (a78be3d96) — tools/cx reconciled.** The `-X ours` merge had dropped cx/f's
  edits to `arena.py` (multi-direction portal walk — `portal_steps` was a dead counter on main — plus
  the `eaten_r{50,100,150,250}` / `sprint_segs` / `portal_deaths` summary fields) and `bench.py`
  (`--replay-dir`). Both restored; `ablate.py` needed nothing (main already carries cx/b's
  `--exclude`). No feature conflicts — the union is clean, nothing behind a flag. Verified by
  re-running both findings' summary commands on their archived runs: C1-B's
  `ablate.py a b c --filter live|panel --exclude pub/` reproduces every quoted pair count
  (176/3/61, 194/1/45, 118/11/111 p=0.69, panel 126/12/94 p=0.036 …) and C1-F's `cx_f_summary.py`
  reproduces all 9 arms byte-identically (the committed JSON's extra blocks — `f05_panel_cells`,
  `f02_replay_crosscheck`, `sandbox_probes` — were hand-added, not script output). New tests:
  `tools/cx/tests/test_reconcile.py`.
- **2026-09-29 Part 2 (65c04a795) — C++ parity.** Confirmed arena/bench/ablate/golden already launch
  `bot.toml language="c++"` bots through the same `_resolve`/`Project` path as `unswbc run`
  (stamped rebuild incl. headers; wasm cache purged per sandbox game; boot turn separated). Fixed:
  bench aborts (exit 2) on pre-build failure instead of failing every fixture in flight;
  run_panel prebuilds all bots serially (the V04 parallel-startup race) and exits 2 on a compile
  error. meter.py gained `--mode cxx`: builds with `#define CX_METER 1`, collects
  `CX_METER parse=<us> sense=<us> policy=<us> bfs=<us>` stderr lines through arena's new
  `meter_prefix=` (stderr never reaches engine or replay) — the anna ANNA_MEASURE path is untouched
  (`auto` picks cxx only when the sources mention CX_METER). golden.py gained `suite`: one bot
  against every transcript under a directory — Ares V06 vs the Python reference recordings runs,
  diverges loudly, exit 1; yuna self-replay 5,771 turns 0 divergent. Tests:
  `tools/cx/tests/test_cxx_parity.py` (+ fixture bot `tools/cx/tests/fixtures/cxmeter-bot`).
- **2026-09-29 Part 4 (b4b1c3b7c) — generalisation panel.** `run_panel.GEN_MAPS` = maps/new all 20 +
  maps/var *_tr (29), `--panel gen` (same ZOO, both seats, seed 1 round robin; 1,624 games) and
  `--bot bots/<x>` candidate grids (8 ZOO opponents × maps × both seats; 160 on z1, 464 on gen)
  under `build/zoo/<panel>-<bot>-<fp8>/` keyed by the runtime-source fingerprint (SHA-256 over
  sorted source names+contents, NUL-separated). z1 game ids unchanged → old replays still reuse.
  benchmarks.py `derive`/`apply_field_rel` degrade gracefully: a map with no field reference gets
  NaN `|map|top|pct` (never a division by a missing median) and a metric with no reference is
  skipped, not a KeyError. Tests in `test_features.py`.
- **2026-09-29 Part 3 — scorecard.** `python -m tools.analysis.features.scorecard bots/<cand>
  [--parent …] [--panel z1|gen|both] [--seed 1,2] [--jobs N] [--atlas off] [--sandbox]` — runs or
  reuses the fingerprint-keyed panel, extracts, scores against the fixed references, prints the two
  V06 tables (tier-1 with parent deltas; tier-2 with % change), W–L–D, the gen block (raw vs
  parent, `|map` marked unavailable), the CPU probe block with `--sandbox`, and
  `GATE: pass|hold|fail — <reason>` applying BENCHMARKS step 4 literally (hold includes the V06
  case: economy up but < +0.05, hygiene within guardrails). Writes
  `game_stats/runs/<cand>-<panel>-s<seed>.json` + `.md`. `--atlas off` plays a
  `build/cx/atlas-off/` copy with `ATLAS_ENABLED=false` (snapshots untouched).
- **Acceptance:** `build/zoo/ares-v06-expanded-search-support-20260929/` (the archived V06 panel) is
  not on this machine, so the V05/V06 seed-1 panels were re-run fresh (160 games each) and the
  scorecard's tables compared to the finding — see `docs/findings/2026-09-29-r4-01-tooling.md`.

## Where things are

Branch `r/r4` in `../wt-r4`: a78be3d96 (P1), 65c04a795 (P2), b4b1c3b7c (P4), + P3/docs commits.
Findings: `docs/findings/2026-09-29-r4-01-tooling.md`. READMEs updated (`tools/cx`, features).
Run env: `~/.venvs/bc122/bin/python` (pytest installed into it via uv for the features tests).
