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

## In flight

baseline off-panel + yuna-panel; f02/f03/f04 live (queued); f02b live; then f05
4-cell matrix (live/panel × atlas on/off), F-2 portal replay stat (base vs f02 on
portal-heavy maps with replays saved), sandbox probes for the shipped bots.
