# R-2 `sciel` status — Sciel lineage (GLM 5.3)

Base: `ares-v06-expanded-search-support`, atlas off (no `claude/r1-status.md` exists in any worktree
as of lane start, so the brief's default V06 base applies; Ares V06's atlas helper has no call site
either way). Worktree `../wt-sciel`, branch `r/sciel`. Run env `~/.venvs/bc122` (unswbc 1.2.2).

`sciel-00-base` = byte-identical Ares V06 policy + documenting `Params::atlas_enabled=false`.
Golden parity vs the ra lane's Ares V06 transcripts: **52,728 turns / 1,842 dragons across
schooltime-A, portals-B, slithery_fight-A, trauma-B (seed 1), 0 divergent**.
Fingerprint `779808b9c98f99b4d8f432398f78f290dade2f2061e8d54736a2b6d2ecfff205`.
Lane tooling copied from `tools/ra/` (ra's lane.py/variant.py/gen_reference.json, paths moved to
`tools/sciel/`, `build/sciel/runs`) — thanks ra; scoring logic unchanged.

Mechanism picks read (before choosing): ra has rejected, all vs its base — bed anticipation
(01a-c), child-room gate 4→8 (02a), pearl-TTL 40→20 (08a), threat ×0.25 (17c), revisit 0.05 (18a),
enemy-density devaluation off (19a), hunters from r40 (20b), strike margin 0 (21a); r3 rejected
pair-memory, exit-known, kelp-cost, escape-early held (+5pp win, own-body +11% guardrail).
**Untried per the R-3 director-read and the C1-C ledger: newborn siting and post-transit
navigation** — this lane starts with the first and holds the second.

| Version | Mechanism | Pool delta | Generalisation panel delta | CPU max | Verdict | Why |
|---|---|---|---|---:|---|---|
| sciel-01a-siting | Newborn siting: split score gains siting term for child spawn cell (food arrival-earliness within 4 via parent knowledge − reference 5.0, ×0.8; ally-crowd at spawn, cap 2.0) | econ~ −0.003 (mean −0.004); win 0.725 vs 0.762 (pairs 2/150/8, p=0.11); nb10 34.6→34.6 (statistic unmoved) | ≡ base (pearls 1/244/3; win 0.540 vs 0.520; var+devil_tr +0.100 the only mover) | 8.60M | **REJECT** | Mechanism barely fires (golden: 1 divergence in 13,649 schooltime turns): a len-4 parent just ate, so its tail is near food by construction; where it did fire (portals −0.018, devil −0.015) econ fell — the delay costs more than the sit buys. Kill number: pool econ~ −0.003 vs +0.05 gate. Switch stays (sit_enabled, default off in future parents). Untested variant for later: hand the child its first target in the birth packet (needs a new payload field), rather than shaping timing. |
| sciel-02a-ptnav | Post-transit navigation: 4 rounds of decayed steering after our own transit — clear the exit mouth (1.2/step from landing), mouth-zone malus, 3.0 re-transit brake; suppressed during newborn escape | econ~ −0.004 (mean −0.005); units@100\|n~ −0.057; win 0.725 vs 0.762 (13/128/19); portals-map econ −0.045 | win 0.512 vs 0.520; portal-heavy gen maps down (quartet −0.037, portals_rec −0.025); var+queen_of_spades_tr +0.205 outlier | 8.53M | **REJECT** | The statistic MOVED (ledger: portal 6.3→5.0 len/1k −21%, trapped 36.1→34.8, newborn 19.3→18.6; h2h_ally −12%) but pearls/units fell with it — H2's "leak moved, not closed" fired: steering off mouths and braking re-transits gives hygiene at an economy cost on the maps where transits are productive. Same shape as r3-04 (kelp cost). Kill number: pool econ~ −0.004 with units −0.057 vs gate. Switch stays (pt_enabled). No sweep point: the failure is multi-axis, and pooled portal leak is only 6.3 len/1k to harvest. |
| sciel-03a-ewfood | EW food-density memory: food_ew[c] += 1 per pearl eaten, ×0.98/round; valuation scaled by clamp(1+0.6·(density−0.5), 0.4, 2.5) on unseen cells AND bed values | **econ~ +0.067 (1.178 vs 1.111 — above the +0.05 bar)**; pearls@100 +0.146 (pairs 103/9/48, p≈0.0); schooltime +0.600, default +0.184, trauma +0.100; win 0.787 vs 0.762; births +0.113 | not run (pool verdict first) | 8.68M | **REJECT on guards** | First mechanism in the lane to clear the economy bar — the stateful-valuation direction pays. Killed by convergence crowding, as pre-declared: h2h_ally +34% (3.24 vs 2.41/1k), units@100\|n~ −0.075 (births UP but nb10 37.5 vs 34.6 — children die in the crush), total@100 −0.018. Fix is inside the mechanism: discount the EW factor by ally saturation of the target field (03b). |

Base reference numbers (seed 1, 160 side-games): econ~ 1.111, win 0.762, u100|n~ 1.20, t100|n~ 1.04,
wall 8.74, self 5.74, nb10 34.6. Gen (248): econ 1.098 abs, win 0.520.
