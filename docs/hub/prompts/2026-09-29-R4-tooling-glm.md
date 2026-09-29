# R-4 — Tooling: reconcile `tools/cx`, a single-bot scorecard, C++ parity in the harness (GLM 5.3)

Branch `r/r4`, worktree `../wt-r4`. No bots. Read first: `docs/hub/prompts/2026-09-29-R-index.md` (rules),
`tools/cx/README.md`, `docs/analysis/BENCHMARKS.md` §"How to use it" (last paragraph: "A single-bot scorecard …
does not exist yet"), `docs/findings/2026-09-29-ares-v06-expanded-search-support.md` §"Seed-1 fixed panel" (the
table the scorecard must reproduce).

Dependency-free; every other R task consumes what this produces, so ship each part as its own commit as soon
as it works rather than all at the end. Every part has a test in `tools/cx/tests/` or
`tools/analysis/features/test_features.py`.

## Part 1 — reconcile `tools/cx` (first)

`cx/f` was merged into main with `-X ours`, so main carries C1-B's (`cx/b`) versions of `tools/cx/{arena,bench,ablate}.py`
and **your** `cx/f` changes to those three files are not on main. `git diff main cx/f -- tools/cx/` shows them.
Bring every feature from both sides into one version of each file: C1-B's additions (whatever the router work
added: read `docs/findings/2026-09-30-cx-b01-router.md` §tools) and C1-F's (the switch-set ablation support,
`cx_f_summary.py`'s expectations). Re-run both findings' summary commands on their archived runs in
`game_stats/runs/` and show the numbers are unchanged. Delete nothing; if two features conflict, keep both behind
flags and say so in the README.

## Part 2 — C++ candidates in the harness

Ares bots are directories with `bot.toml language = "c++"`. Confirm and fix where needed that `arena.py`,
`bench.py`, `ablate.py`, `golden.py`, `meter.py` and `run_panel.py` handle a C++ bot exactly like a Python one:
build once per fixture set, purge the sandbox wasm cache when headers change (README notes the cache hashes only
`.c/.cpp`), report sandbox points with the boot turn separated, and fail loudly on a compile error rather than
scoring a stale build. `meter.py`'s parse/sense/policy/BFS breakdown needs a C++ equivalent if it has none: a
`-DCX_METER` build that prints the same phase timings to stderr, dropped from the replay. Golden `replay` must
run a C++ bot against a Python-recorded transcript (Ares V04's behaviour-parity finding did this by hand; make it
a command).

## Part 3 — the single-bot scorecard

One command: `python -m tools.analysis.features.scorecard bots/<candidate> [--parent bots/<parent>] [--panel z1|gen|both] [--seed 1,2] [--jobs N] [--atlas off]`
that runs the panel (or reuses `build/zoo/...` replays already present, keyed by the runtime-source fingerprint
the Ares findings use), extracts, scores against the fixed references, and prints **exactly the two tables in the
Ares V06 finding** (tier-1 with parent deltas; tier-2 with % change) plus the panel W–L–D, the generalisation-panel
block, the CPU probe block if `--sandbox` fixtures were run, and one line: `GATE: pass|hold|fail — <reason>`
applying BENCHMARKS §"How to use it" step 4 literally (hold = hygiene up with economy flat; fail = economy down or
hygiene rate up >10 % or panel win rate down). Writes `game_stats/runs/<candidate>-<panel>-s<seed>.json` and a
markdown block ready to paste into a finding. Reproduce the Ares V06 finding's numbers from its archived replays
(`build/zoo/ares-v06-expanded-search-support-20260929/`, if present; else from a fresh run and say so) as the
acceptance test.

## Part 4 — generalisation panel definition

`run_panel.py` knows `LIVE_MAPS`; add a `GEN_MAPS` set (`maps/new/*.map` all 20, `maps/var/*_tr.map`) and a
`--panel gen` mode with the same ZOO and both seats, and make `benchmarks.py` degrade gracefully on maps with no
field reference (BENCHMARKS §guardrails: report tier-1 raw against the parent on the same map, mark the `|map`
columns as unavailable rather than dividing by a missing median). This is what R-1/R-2/R-3/R-5 report as "the
panel"; until this lands they build it by hand, so land it first if Part 1 is slow.

## Deliverables

Commits on `r/r4` per part; `docs/findings/2026-09-3x-r4-tooling.md` (what changed, the reconciliation diff
summary, the reproduced V06 numbers, the scorecard usage); `tools/cx/README.md` and
`tools/analysis/features/README.md` updated; `claude/r4-status.md`. Tell the director when each part is on the
branch so it can be merged ahead of the rest.
