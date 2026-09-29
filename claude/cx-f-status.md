# cx-f status — C1-F dependency-free leak fixes (working line "asa")

Worktree `../wt-cx-f`, branch `cx/f` (from main). Base: `bots/anna-a02-chassis` via
`bots/cx-f00-base` (chassis + `ATLAS_ENABLED` switch; golden-verified identical to the
chassis with the atlas on: 1541 turns, 0 divergent). Bots: `bots/cx-f00…f05*` + the
`-noatlas` twins for panel cells. Findings will live in
`docs/findings/2026-09-30-cx-f01-leaks.md`.

## Log

- **29 Sep (session start).** Tools: adopted the main tree's uncommitted panel bench
  (arena/bench/ablate) + added additive stats (pearls at r50/r150/r250, portal steps,
  portal deaths, sprint segments) and `bench.py --replay-dir`; new
  `tools/cx/benchmarks_table.py` (BENCHMARKS.md's three yardsticks vs
  field_references/field_distributions).
- **§1 baseline launched** (chassis atlas-on, atlas-off twin, yuna; live ×2 sides ×
  seeds 1-3 × the 4-opponent panel; same on the 31-map generalisation panel).
- **F-1 (escape)**: first two attempts had real bugs — (1) unconditional
  `split_has_room` at len 2 threw `length_error("vector")` every turn (the fallback
  walker drove; schooltime ate 0 pearls by r100), (2) a 10-cell room requirement on
  the trapped split stopped Slithery's trapped-split pump (u25 3 vs 25; the base does
  356 trapped vs 27 greedy splits in 100 rounds there). Final F-1: enclosure probe
  (reach < len+2, no tail-chase), exit-target override, trap-split gate = "child has
  ≥1 legal step". **Measured alone on the live pool: neutral** (len_r100 37/167/36,
  p=1.0). The f01b early-warning variant (k = room_need) also coincides with base.
  The chassis's trapped leak is not where the ledger said — that measured yuna/live.
- **F-2 (portals)**: pair exit memory (World), sonar probe before blind transits,
  id parity, id-order exit simulation, `exit_known(pair)` exposed. Full rule set
  **fell into the sakura trap** (interim n=156: portal steps −36%, deaths −33%,
  per-100-steps 25.7→27.0 flat, eaten −6%): the gates only restricted, and parity
  halves crossings the chassis already does too few of. Variant
  `cx-f02b-confident`: parity off + memory-fresh verified-clear exits **waive the
  blind-landing penalty** (known-safe transits get cheaper — willingness up, not
  just safety up). f02b live run launched.
- **F-3 (sprint)**: exact-sim sprints (ouroboros `tactics.sim` semantics) only when
  they win a contested arrival race (smallest sufficient k ≤ 3), rate-capped 4/24
  rounds. Smoke: 40 sprint segments on slithery with eat100 252 vs 249 base.
- **F-4 (kelp)**: kelp-edge score penalty on cramped steps only. Smoke on slithery
  seed 1 = bit-identical to base (the room tie-break already avoids those cells);
  awaiting the live pairs — likely folded into F-1 as the prompt allows.
- **f05 combined** assembled (all four; scripted merge, one compile error and one
  silently dropped hunk caught by smoke tests — sprints verified present).

## §1 first reads (live pool, 240 games/arm)

- Chassis atlas-on eats at 0.4–0.7× the field median on most maps (Schooltime 1.37
  best, Portals 0.04 worst), wall deaths 0–7.9/1k, portal-step deaths 14–36/100.
- Atlas effect on the chassis: eaten_r100 on/off 99/15/126 (p=0.08, atlas helps);
  portal_deaths_r100 72/143/25 (p=0.000, atlas-off transits less and dies less).
  The atlas buys economy with portal exposure — exactly the C1-B/F-2 interface.
- yuna-v03-core vs the same panel: eats 1.2–2.3× field median on Portals,
  Schooltime, Slithery; portal deaths 45/100 steps on Portals (the leak the ledger
  measured); 57% win rate.

## Verdicts (all 240-pair exact, live pool, atlas on, vs `build/cx/f00-on-live.jsonl`)

| fix | pairs (len_r100) | own statistic | verdict |
|---|---|---|---|
| F-1 escape | 37/167/36 (p=1.0) | trapped proxies flat | **neutral**; machinery ships |
| F-2 all rules | 34/169/37 | steps −31%, deaths −30%, rate 25.9→26.1 flat, pearls −4.4% | **sakura trap — rejected** |
| F-2b confident | ≡ f02 totals | ≡ f02 | rejected |
| F-2c swarmwise | ≡ f02 to the digit | ≡ f02 | rejected (ally id-sim never decides) |
| F-2d memory-only | ≡ f02 to the digit | ≡ f02 | rejected (the gate is a volume throttle) |
| F-2e confidence-only | 0/240/0 | bit-identical games | no-op |
| F-3 sprint | 50/84/106 (p=0.000) | sprint/pearl 0.456 | **rejected**; ships OFF |
| F-3b close-race | 34/54/68 (p=0.001, n=156) | sprint/pearl 0.358, pearls flat | rejected; governor delivered |
| F-4 kelp | 2/235/3 | never flips a decision | **folded into F-1** (the flood covers it) |

Sandbox probes (4 fixtures, seed 1, --sandbox): f00/f01/f02d/f03b/f04 all p50 3.9 M,
p99 ≤ 4.8 M, max 5.1 M, zero faults.

## What this means

**The ledger's leaks are in the yuna-lineage code, not the chassis.** The chassis's
own leak profile: wall deaths on Slithery (29.5/1k — a navigation problem for C1-B's
router cost map), portal deaths at 25.9/100 steps on 1/8th the field's transit volume
(the gates have nothing to bite on at this volume), and an economy at 0.4–0.7× the
field median (the cheap policy's known limit). No fix passes its acceptance bar on the
chassis; none is promoted; `cx-f05-combined` (F-1+F-4 on, F-2 gates off with the
memory/probe infrastructure live, F-3 off) is running its four-cell matrix
(live/panel × atlas on/off) as the shipped switch set for C1-B.

The atlas finding is the one positive discovery: on the chassis it buys +17% pearls
(p=0.08) and doubles portal deaths (p=0.000) — remembered landings make transits
tempting but not safe. Off-pool it matches nothing (683/744 identical to atlas-off).

## In flight

f05 4-cell matrix (~2000 games); F-2 replay cross-check (portal_deaths.py on saved
replays, base vs f02d); f05 sandbox probe; then findings finalize, summary JSON,
CANDIDATE decision (likely: none passes → no registration; report negatives), commit.
