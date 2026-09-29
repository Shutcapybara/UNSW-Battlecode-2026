# R-3 — Re-target the C1-F leak switches at Ares, at real transit volume (GLM 5.3)

Branch `r/r3`, worktree `../wt-r3`. Bots under `bots/r3-<nn>-<slug>/`. Read first: `docs/hub/prompts/2026-09-29-R-index.md`
(rules), your own `docs/findings/2026-09-30-cx-f01-leaks.md`, `docs/findings/2026-09-30-cx-c01-eff.md`,
`docs/findings/2026-09-30-cx-d01-portals.md`, `docs/findings/2026-09-29-ares-v05-separation-bugfix.md`,
`docs/analysis/BENCHMARKS.md` §"How to use it".

## Why again

C1-F found no leak fix passes on the `anna-a02` chassis, and correctly said why: the chassis carries about 2 % of
the ranked bot's transit deaths, so F-1 (pair memory) and F-2 (exit-known) had nothing to fix and F-2 could only
act as a volume throttle (−4.4 % pearls). The ranked leaks in the C1-C ledger — trapped, newborn, portal-exit,
crowd — are **Tyr-lineage** leaks. Ares is the Tyr V12 lineage in C++. The switches were built for the wrong
host; this task puts them on the right one.

## Step 1 — measure the leaks on Ares (one day)

Before porting anything: run Ares V06 (atlas off; or V05 if `claude/r1-status.md` says V06 does not generalise)
on the z1 panel seed 1, both seats, and extract the C1-C ledger for it: deaths by cause and context
(trapped, newborn ≤10 turns, within k tiles of a portal exit, crowd ≥3 own units in the 5×5), per 1k
dragon-turns and per 100 portal steps. Put it beside the Tyr V12 ledger from C1-C and the field/top-ten
references. **If Ares does not show the leaks either, stop and report** — the lineage claim is then wrong and the
director needs to know before anyone ports anything.

## Step 2 — port as switches, one per version

In `policy.hpp`/`params.hpp` of your copy, each default off, each with a one-line `CANDIDATE.toml` mechanism and
the expected sign on the *specific* ledger row it targets:

- F-1 pair memory: remembered portal pair → exit tile and the last-seen danger at the exit; cost term on entering.
- F-2 exit-known: enter a portal only when the exit is known or a probe has been sent — **as measured on Ares**,
  where transit volume is real; C1-F's throttle result does not transfer and must not be assumed either way.
- The enclosure probe from F-4 if C1-F's fold left it as a distinct switch.
- The trapped-split rule from C1-F's negative result, restated: never gate the trapped split by room size (that was
  the finding; here the test is whether Ares V06's trapped escape already does this and what it costs).

Each version: golden-harness parity of the copy against its base (`tools/cx/golden.py`), CPU probe
(`arena.py --sandbox`, four dense fixtures), z1 seed 1 both seats, generalisation panel seed 1, scored with the
fixed references. Report the targeted ledger row first (did the leak move), then the BENCHMARKS three-number form
for everything else, then the panel win rate. Hygiene counts only while the economy holds; a fix that moves its
row and costs pearls is a **hold** with the trade stated in numbers (deaths saved per 1k vs pearls lost per
100 dragon-turns), not a reject — the director reads holds.

## Step 3 — stack

Stack the switches that were accepts or holds in step 2, in order of ledger size, one addition per version.
Report the stack against the base on both panels. Stop when a stack step fails the gate.

## Deliverables

`docs/findings/2026-09-3x-r3-ares-leaks.md` (step 1 ledger; per-switch tables; the stack; which leaks are
closed, which are open and why), `claude/r3-status.md`, `game_stats/runs/r3-*.json`, bots `r3-01…`. Any accepted
version gets a `CANDIDATE.toml` (`language = "c++"`, lineage `ares`, `lineage_parent` = base) and a "ready for
`register.json`" line. Do not register. Do not touch `bots/ares-*`, `bots/cx-*`, or R-1/R-2/R-5 trees.

Budget: step 1 ~160 games; step 2 ~4 × 400; step 3 as needed. Interrupted runs are reported as interrupted.
