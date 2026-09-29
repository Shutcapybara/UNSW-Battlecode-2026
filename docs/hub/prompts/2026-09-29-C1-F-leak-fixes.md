# C1-F — the dependency-free leak fixes on the chassis  (model: **GLM 5.3**; issued 29 Sep 01:20 UTC)

Read first: `docs/hub/prompts/2026-09-29-C1-index.md` (shared rules, incl. the measurement gate added 29 Sep),
`…C1-out-of-sample-rule.md` (binding), `docs/findings/2026-09-30-cx-c01-eff.md` (the ledger and its fix list),
`docs/findings/2026-09-30-cx-d01-portals.md` (the portal measurement and rules), `docs/findings/2026-09-29-cx-a01-
chassis.md` (the chassis API), `docs/analysis/BENCHMARKS.md` (what may be optimised and how it is reported). Lineage
`cx`; bots `cx-f01-…`, one directory per fix, built on **`bots/anna-a02-chassis`** (copy, never edit). C1-B (the
router) is ~12 h away; nothing here waits on it, and everything here lands on it afterwards as `params.hpp` switches.

## 0. The job

Close the leaks that do not need the router, one at a time, each measured alone. The ledger's ranking, restated:
trapped/mill deaths (Portals 126 vs band 63 length lost per 1k dragon-turns; Slithery 111 vs 88; Schooltime 25 vs 4),
portal exits (28 deaths per 100 steps vs Cutlery's 12.5; 623 wall/self deaths within two rounds of a transit in 35
games vs 2; 548 same-pair friendly collisions), the sprint tax (0.023 length per pearl vs 0). Newborn siting needs
the router's arrival map and is **not** in this task. BENCHMARKS.md says self-inflicted deaths are hygiene — stable,
bot-owned, top ten at zero, but not rating-predictive — so the rule is: push them down **only while the
map-normalised economy curve does not drop**. That is the gate below.

## 1. Baseline first (half a day; also the answer to "where does the chassis sit today")

Run `bots/anna-a02-chassis` and `bots/yuna-v03-core` on the ten live maps × both sides × seeds 1–3 against the
panel (`bots/yuna-v03-core`, `bots/fenrir-v18-arrival-ready-beds`, `bots/kazuha-s01-swarm-dissolve`,
`bots/ouroboros-s02-portal`) **and** on the generalisation panel (`maps/var/*_tr.map`, `maps/pub/*_rec.map`, the
20 maps in `maps/new/` with `training_map_weights.csv`), the chassis with `ATLAS_ENABLED` on and off. Extract with
the F1 extractor and report with `tools/analysis/features/benchmarks.py`'s references
(`docs/analysis/benchmarks/field_references.json`, `map_reference_medians.json`): for each bot, each panel, the
three benchmark groups — map-normalised economy curve (pearls at r50/r100/r150/r250 over the field's per-map
median), dragons and length at r100 on the same scale, the hygiene group (wall, self, ally-body, portal-step deaths
per 1k) — each as **absolute, gap to the top ten, and field percentile**. `maps/new` has no field median; report
absolute there and the zoo-relative version. This table is the baseline every fix below is measured against and
the first number the director needs when the router lands.

## 2. The fixes (each its own `params.hpp` switch, its own bot directory, measured alone; then all together)

**F-1 Trapped/mill escape.** Per candidate step, a bounded reach flood (the chassis' `flood_room` / `room_need`;
reach-5 is nearly free in C++). When the reachable region behind a step is smaller than the room need, the step is
out; when the dragon is already enclosed (reach ≤ k), move toward the largest reachable open space even at pearl
cost. Never enter a 1-wide dead end whose only exit is a split. Note a02's own lesson: splitting when trapped made
wall deaths worse (4.65 → 11.7 per 1k) because the children died in the trap — a split is an escape only if both
halves have room. Statistic: trapped length lost per 1k (the ledger's class) on Portals, Slithery, Schooltime.
Accept: −30 % on those maps' pairs, economy curve not down.

**F-2 Portal exit discipline** (C1-D §2, on the chassis). Exit memory per pair (last exit cell, whether it was
occupied or lethal, round); a sonar probe along the entry direction the turn before a transit (echo counts by
kind: kelp / ally / enemy beyond the portal); transit only on a clean echo or a known-clear exit; exit-cell
one-step simulation in id order (lower ids move first); the id-parity convention against same-pair double transit
(one direction on rounds where `(round + id) % 2 == 0`, the other on odd), ablated against a sonar-payload
reservation. Expose `exit_known(pair)` for C1-B. Statistic: portal-step deaths per 100 steps and per game, same-pair
double deaths (re-run `tools/replay_stats/portal_deaths.py` on the fixtures). Accept: −25 % pooled, transits per
game not down more than 10 %, economy curve not down. The trap to avoid is halving deaths by halving transits
(sakura's −16 net on portal-heavy maps).

**F-3 Sprint discipline.** A k-step sprint costs k − 1 segments; sprint only when the target pearl's arrival margin
over any enemy beats that cost within a short horizon; cap sprints per dragon per k rounds. Statistic: sprint length
per pearl (the ledger's `sprint/pearl`, which our newer submissions grew to 0.029–0.044). Accept: halves, pearls by
r100 flat, economy curve flat.

**F-4 Kelp cost on tight ground.** Kelp-adjacent cells carry a routing cost only when the room behind them is small.
Statistic: wall deaths per 1k on Slithery (ours 26 vs band 9). Accept: −50 % on Slithery, pearls flat. This one is
small and may be folded into F-1 if the flood already covers it; say so if it does.

Then **all four together** on the same fixtures, both panels, atlas on and off, and against the baseline of §1.

## 3. Rules that bind here

- Out-of-sample: nothing keys on map identity; the atlas is a switch; every number is reported with it off on the
  generalisation panel beside the live pool. A fix whose gain exists only with the atlas on, or only on the pool, is
  rejected (`…C1-out-of-sample-rule.md`).
- Sandbox: p50/p99/max points on the four probe fixtures for every bot; purge the wasm cache before sandbox games
  (`tools/cx/arena.py` does it; the 1.2.2 cache ignores header edits).
- Exact pairs (map, side, seed, opponent), better/same/worse and the sign-test p; never pooled win rates alone.
- No live actions, no uploads; `CANDIDATE.toml` for the combined bot when it passes; the director registers it.

## 4. Report

`docs/findings/2026-09-30-cx-f01-leaks.md` with the baseline table (§1) first, then one block per fix (statistic
before/after, pairs, sandbox, the economy-curve check), then the combined result; `claude/cx-f-status.md` at every
stop. Falsifiers: a fix moving its own statistic without the economy curve holding (a leak moved, not closed);
F-2 cutting deaths only by cutting transits; any p99 > 60 M.
