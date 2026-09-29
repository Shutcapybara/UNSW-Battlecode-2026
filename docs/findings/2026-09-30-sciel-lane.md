---
id: sciel-lane-r2
author: glm/sciel
kind: lane-log
title: Sciel lane (R-2) — versions 00–03, two ledger leaks tried, the first economy-clearing mechanism found
task: R-2 (sciel lane)
evidence: build/sciel/runs/ (ignored panels), game_stats/runs/sciel/*.json (scored), tools/sciel/ (lane
tooling), golden transcripts from wt-ra's build/cx/golden (Ares V06 recordings)
---

# Sciel lane, versions 00–03 (30 Sep 2026)

**Summary.** The Sciel line was founded from `ares-v06-expanded-search-support` (atlas off; no
`claude/r1-status.md` exists in any worktree, so the brief's default V06 base applies). Four versions
screened at seed 1 on the fixed pool (`run_panel.ZOO` × ten live maps × both seats, 160 side-games)
with the BENCHMARKS gate. Two rejected-and-dead (siting, post-transit steering), one rejected-but-
directional (EW food-density memory cleared the economy bar and died on convergence crowding), and
its guard variant is the live candidate. The lane's headline for the director: **stateful food
valuation is the first mechanism in either R-2 lane to clear the +0.05 economy gate — the direction
that pays is memory, not weight tuning.**

## Base and parity

`sciel-00-base` = byte-identical Ares V06 policy + documenting `atlas_enabled=false`. Golden parity
against the ra lane's Ares V06 transcripts: 52,728 turns / 1,842 dragons over schooltime-A,
portals-B, slithery_fight-A, trauma-B (seed 1), **0 divergent**. Fingerprint
`779808b9c98f99b4d8f432398f78f290dade2f2061e8d54736a2b6d2ecfff205`. Pool base rates (seed 1):
econ~ 1.111, win 0.762, units@100|n~ 1.20, total@100|n~ 1.04, wall 8.74/1k, self 5.74/1k,
h2h_ally 2.41/1k, newborn-deaths-10 34.6/100. Leak ledger (r3 instrument, reproduced exactly):
trapped 36.1, newborn 19.3, portal 6.3, crowd23 11.4 len/1k.

## What was tried

| version | mechanism | verdict | the number that decided |
|---|---|---|---|
| sciel-01a-siting | newborn siting: split score gains a food-earliness × crowd term for the child's spawn cell | REJECT (inert) | econ~ −0.003; nb10 34.6→34.6 — the statistic never moved |
| sciel-02a-ptnav | post-transit steering: clear the exit mouth + re-transit brake for 4 decayed rounds | REJECT (leak moved, not closed) | portal 6.3→5.0 len/1k (−21%) BUT econ~ −0.004, units −0.057, portals-map econ −0.045 |
| sciel-03a-ewfood | EW food-density memory: eaten-pearl field (×0.98/round) scales unseen and bed values | **REJECT on guards, economy cleared** | econ~ **+0.067** (> +0.05 bar), pearls@100 pairs 103/9/48 p≈0 — killed by h2h_ally +34% (up in 100/130 pairs), units/total medians down |
| sciel-03b-ewguard | same + visible ally-saturation guard | REJECT (h2h_ally +31%) | econ~ +0.071; gen econ +9.5%, pearls pairs p=1e-4 — the mechanism generalises |
| sciel-03c-ewradio | same + radio-informed guard (density reports, stronger) | **REJECT (h2h_ally +38%, win −0.028) — family closed** | econ~ +0.105 pool, +16.3% gen; gen dragons 1.589 / length 1.675 of base; pearls pairs p≈0 on both panels |
| sciel-04a-row | right-of-way on 03c (landing adjacent to lower-id ally head costs 2.5) | REJECT (h2h_ally +29%, win −0.044) | gen win 0.597 best yet, ally_body below base — hygiene real, head-ons hold |
| sciel-04b-rowpath | right-of-way v2 on bare 03a (guards off), every newly occupied path cell | REJECT (median econ +0.039 with **mean +0.103**, h2h_ally +24%, win −0.050) | h2h 34→29→24 across row variants; each deconfliction layer trades pool win (vs 03a p=0.023) |


## What the accepted/in-flight stack is

Nothing accepted yet. The live mechanism is the EW harvest memory with the saturation guard
(03b): beds respawn on fixed cycles, so each dragon's own decayed history of eaten-pearl cells is a
predictive food field; valuing unseen cells and beds by it moved pearls@100 by +0.146 of field
median at seed 1 — the largest economy movement any single switch has produced on this chassis in
either lane (ra's eight scored rejections span −0.065..+0.033 econ~).

## Which kinds of mechanism paid

- **Stateful valuation over static re-pricing.** Every static-weight retune ra scored was rejected
  (best +0.033). The EW field — the first stateful term tried on Ares — immediately cleared the
  economy bar, and its gain grew with each variant (+0.067 → +0.071 → +0.105 pool; +9.5% → +16.3%
  gen) while its crowding cost stayed fixed. The information is in *where food has been*, which no
  fixed weight encodes.
- **The death-ledger fixes buy hygiene at the economy's expense on this chassis too.** Both
  ledger-named leaks (newborn siting, post-transit nav) were tried as specified and both failed the
  same way r3's did: the statistic moves, the pearls don't follow. Newborn siting was inert rather
  than harmful — a len-4 parent's tail is near food by construction, so "site the child" has almost
  no lever arm through split timing; the birth-packet variant (hand the child a target) remains
  untested and needs protocol surgery.
- **Convergence is the failure mode of any pull toward richness, and valuation-time guards cannot
  fix it.** Three guard variants (none, visible-heads, radio-density) left ally head-on deaths at
  +34/+31/+38% of a 2.41/1k base. The collisions are arrival-time: targets were chosen when the
  field was uncontested, and the mechanism's larger sustained population (gen dragons +21%)
  structurally raises contact rates. The gate's 10% hygiene guardrail is exactly right here — this
  economy is real but not yet monetisable. **The named unlock for the next iteration is
  arrival-level deconfliction: target claims (a dragon broadcasts the bed it is walking to; others
  re-target at choice time because the claim captures intent before departure, not presence at
  arrival)** — sciel-05, needing one new sonar packet type. Movement-level right-of-way (04a/b,
  id-ordered yield, path-wide) bought the rest of the hygiene book (wall/self/ally_body down; gen
  ally_body below base) and moved head-ons +34→+24%, but could not reach the +10% guardrail and
  cost pool win rate at every step (0.787→0.756→0.734→0.719→0.713 across 03a→04b). Second
  observation for the director: **the gate's median-per-side-game convention bites when gains are
  map-concentrated** — 04b's economy is +0.103 on the mean and +0.039 on the median, because
  schooltime (+0.5) and a tail of maps carry it while the median map gains modestly.

## Reproduce

    ~/.venvs/bc122/bin/python tools/sciel/lane.py run <bot> --panel both --seeds 1 --jobs 7
    ~/.venvs/bc122/bin/python tools/sciel/extract_serial.py <bot> --panel both   # spawn pools OOM on this host
    ~/.venvs/bc122/bin/python tools/sciel/lane.py score <bot> --parent sciel-00-base --seeds 1 --json game_stats/runs/sciel/<bot>.json

Lane tooling copied from `tools/ra/` (ra's lane.py / variant.py / gen_reference.json; paths moved to
`tools/sciel/`); `extract_serial.py` and the r3 ledger copy (`tools/sciel/r3_ledger.py` from wt-r3)
are sciel-local additions.
