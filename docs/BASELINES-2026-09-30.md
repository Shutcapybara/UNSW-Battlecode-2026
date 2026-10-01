# Baselines for iteration — what to build on, what to avoid (director, 30 Sep 2026)

For teammates picking a starting point. Every number is from a 160-game z1 panel (8 zoo opponents × 10 live maps ×
both seats) unless stated; "off-pool" is the 29-map generalisation panel (`maps/new/*`, `maps/var/*_tr`). Details:
`docs/findings/2026-09-30-r1-search-ladder.md`, `docs/findings/2026-09-30-ra-lane.md`, `git show origin/r/sciel:claude/sciel-status.md`,
`docs/hub/HYPOTHESES.md` (the ledger), decisions D-029–D-034 in `docs/findings/2026-09-28-director-decisions.md`.

## Build on these

1. **`bots/lune-r1-07-latecap8x-only`** — Ares V06 with one change: the target-search node cap after round 40 raised
   48 → 384 (sparse 64 → 512). Opening unchanged; economy +0.026, dragons@100 +0.053, length@100 +0.046, all four
   death rates −2 %, win n.s. (239–81 vs 244–76 over two seeds); holds off-pool (+2.5 % economy, identical W–L).
   Registered for the dev screen (priority 510). **This is the recommended parent for any new Ares work.** Its
   `CANDIDATE.toml` and finding say why. Do not raise the cap in the first 40 rounds: that costs the opening (R-1).
2. **The same bot with the `W == 32 && H == 16` terms off** (`devil_center_bonus`, `devil_lane_bonus`,
   `ally_body_buffer` in `policy.hpp`). Those three terms are Devil's opening keyed on Devil's size: 16/16 on Devil,
   17 % on Devil transposed, and they *hurt* on Prisoners Dilemma. `bots/renoir-23-nodevil` is the ablation. For
   anything that will play unseen maps (Qualifier, Final) this is the honest base; the cost is Devil on the pool
   only. A structural replacement (a midline race keyed on observed spawn geometry) is open work and yours if you
   want it.
3. **`sciel-03a-ewfood`** (branch `r/sciel`, GLM lane) — a decayed per-dragon food-density grid (`food_ew[c] += 1`
   per pearl eaten, ×0.98/round) scaling target values. Economy +0.067, pearls@100 +0.146 (pairs 103/9/48): the only
   mechanism in the programme to clear the +0.05 bar. Rejected only on a guard (ally head-on +34 %, units@100
   −0.075: dragons converge on the same dense cells). The fix is inside the mechanism — discount the density factor
   by ally saturation of the target field — and is queued in lane `rc`; if you get there first, that is the single
   highest-value thing to try. This is also the strongest evidence that gains are in state/features, not rules.
4. **Your own `ares-v19-critical-enclosure-split`** — the escape split when reach ≤ 8 cells is the only form in the
   V10–V19 series that moved the enclosure hazard (680 → 615 deaths per 1k exposures) without a large cost (11–9,
   pearls −3 %). It was screened at 20 games vs one opponent; the missing step is the 160-game panel plus the
   generalisation panel, paired, seeds 1–3. Worth running before building V20.

## Measure like this

- Paired fixtures only. The same bot scores economy 1.111 at seed 1 and 1.182 at seed 2 with identical win rates:
  the seed moves the world by more than the old +0.05 bar. Compare candidate and parent on the same (map, seat,
  seed, opponent) and use the paired interval (D-032: seeds 1–3, pool + generalisation panel, bootstrap 90 % lower
  bound of Δeconomy > 0, with units/length, tier-2 (≤ +10 %) and win as guards, per-checkpoint reported).
- Run the generalisation panel every time. Pool win 0.762 vs off-pool 0.524 for V06 is the gap that decides the
  Qualifier.
- Watch churn: 38 % of what V06 eats is ally corpses (443 deaths a game). `pearls@k` can rise by feeding the
  swarm to itself; units@100 and length@100 must not fall.
- Atlas: dead code in Ares (`atlas_try()` is never called); every Ares number is already atlas-off.
- CPU is not a constraint on this design: 9 M points/turn at 8× search, 22 M fully unbounded, against a 100 M cap.

## Avoid (measured negative, or pool-fit)

- Lowering the exploration value of unseen cells (`unseen_value` 5 → 3–4): +0.11 on the pool, flat off-pool, ally
  head-on +51 % — it learned the ten maps (Renoir 07a/07c).
- The atlas-only build (Ares V08): +0.188 economy with ally head-on +205 %, own-body +25 %; and it is map memory
  (out-of-sample rule).
- Hard open-room filters (Ares V10, V13, V15): pearls halved. Soft reach scores (V16, V17): no hazard change.
- Flat "wait on a ripening bed" (Renoir 01a/01c, 11): −0.06 economy on dense maps.
- Any single Tyr parameter moved in the cautious direction (room, trap penalty, farming, child room): −0.01 to
  −0.18 economy, one for one with the deaths it saves. Leak fixes must change *which* pockets are entered, not how many.
- Wide search in the first 40 rounds (Lune L1–L3): −0.04 to −0.11 expected score.
