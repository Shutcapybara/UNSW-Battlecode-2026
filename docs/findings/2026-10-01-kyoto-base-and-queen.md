# Kyoto unit 1 — base under 1.2.3, queen measurements, cap-lift arm (GLM tester, 1 Oct 2026)

Lane: `r/kyoto` (worktree `../wt-kyoto`). Engine `unswbc 1.2.3`, hub venv, Mac host (see status
file for the host deviation). Tooling: `tools/kyoto/lane.py` (copy of `tools/rc/lane.py`, scoring and
gate code identical, paths only), `tools/kyoto/queen.py` (row logic from `tools/antioch/queen.py`,
engine verdicts via `tools.antioch.era.header`).

## 1. Base and parity

- `kyoto-00-base` = byte-copy of `hb1-14-prior-r540`. Golden parity via `tools/cx/golden.py`
  (devil, side A, seed 1): 657 turns / 13 dragons, **0 divergent**.
- `kyoto-01-nodevil` = kyoto-00 with `Params::shape_terms = false` (the renoir-23 form of D-033:
  `devil_center_bonus` / `devil_lane_bonus` / `ally_body_buffer` return 0.0). Verified surgical:
  default (32×32) golden replay 14,477 turns / 178 dragons, **0 divergent**; devil (32×16) diverges
  from turn 6. The three 32×16 pool maps are portals, dilemma, devil.
- Panels: pool = 8 ZOO opponents × 10 live maps × both seats × seeds 1–3 (480 games); gen = 4
  GEN_OPPS × 31 maps (new/var/pub) × seats × seeds 1–3 (744 games).

## 2. Engine verification in our own replays

- **Sprint pricing** (`tools.antioch.era.signals` over 120 pool replays): 55 games with
  discriminating sprints price **new** (⌈L/4⌉ free), 0 price old, 65 ambiguous; max sprint 3 steps.
  Every prior sprint-cost result is stale on this engine (as the board said).
- **Queen tiebreak**: round-limit verdicts decide by queen → longest → total; on our pool games the
  deciding level is longest 83 %, total 5 %, **queen 4 %**, tie 1 %; the new rule flips the
  old-rule winner on ~4 % of RL games (the frame-inferred win column in lane scoring is old-rule
  until antioch's `frame-engine-verdict.patch` lands — paired deltas largely cancel it).
- **Queen identity**: engine ids interleave by team parity from r0 (A even from 0, B odd from 1);
  the queen is id 0 / id 1 in 556/556 side-rows; frame-tracked alive ≡ engine queen field 100 %.

## 3. Queen measurements on the base (kyoto-01-nodevil, full panels, engine verdicts)

| metric | pool ours (n=480) | pool opps (n=480) | gen ours (n=744) | gen opps (n=744) |
|---|---|---|---|---|
| queen alive @490 (any game) | 0.100 | 0.019 | 0.152 | 0.031 |
| queen alive at end among **round-limit** games | **0.005** (1/217) | 0.008 | **0.020** (3/152) | 0.01 |
| queen length @490 (alive only), median | 3 | 3 | 3 | 3 |
| queen is longest @490 | 0.025 | 0.008 | 0.034 | 0.004 |
| queen death round: median / p10 / p90 | 65 / 3 / 169 | 52 / 3 / 172 | 66 / 5 / 157 | 55 / 7 / 144 |
| queen death causes (wall/h2h/self/body) | 169/147/88/28 | 175/159/88/34 | 92/**466**/52/21 | 92/367/56/31 |
| queen killed by enemy | 0.26 | 0.35 | **0.71** | 0.61 |
| RL win given queen alive | 1.00 (n=1) | 1.00 | 1.00 (n=3) | 1.00 |

Notes: (i) the RL cut is the decision-relevant one — the tiebreak applies only at the round limit;
our base keeps its queen to the limit in 4 of 369 RL side-games. carthage's 0.9 % pool number is
the same cut on the same bot (their n smaller). (ii) "any-game" survival is inflated by elimination
blowouts (gen 80 % elimination games): the queen is alive when the game simply ends. (iii) Cause
profiles differ by panel: pool kills are wall-first (169) with only 26 % enemy-caused; on gen the
stronger opposition murders the queen (h2h 466, 71 % enemy-caused) — a preservation mechanism that
only ducks self-inflicted deaths will move the pool number, not the gen number. (iv) win|alive is
1.00 on every surviving queen in our 2,448 side-rows (antioch's 36/36 replicated). (v) p10 death
round = 3–5: the pocket maps and the earliest wall hits are a separate, unfixable slice (H-Q3).

## 4. Zero under 1.2.3 (numbers to be posted on completion)

### Zero (kyoto-01-nodevil, seeds 1–3, unswbc 1.2.3; normalised by pre-era field medians)

| panel | n | win | econ~ | p50 | p100 | p150 | p250 | u100 | t100 | wall | self | h2h_ally | nb10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| pool | 480 | 0.836 | 1.140 | 1.091 | 1.365 | 1.389 | 1.354 | 1.545 | 1.459 | 6.89 | 4.61 | 1.87 | 29.5 |
| gen | 744 | 0.693 | 1.113 | 1.429 | 1.336 | 1.329 | 1.329 | 1.833 | 1.955 | 2.91 | 2.04 | 0.97 | 23.7 |

(gen normalised by renoir-00's frozen per-map medians — 1.0 = that base, not the field.) Win shares
use frame.py's inferred (old-rule) winner until the director applies antioch's patch; the new rule
flips 3.2 % of pool RL winners, so absolute win carries ±0.4 pp of inference bias.

Cross-host check vs carthage-00-base (same bot, desktop, their finding): pool 0.826/1.139 and gen
0.689/1.111 against ours 0.836/1.140 / 0.693/1.113 — the two lanes' instruments agree to <0.01 win.

### D-033 cost on this base (kyoto-00 vs kyoto-01, seed 1, pool, n=160)

The terms are worth econ~ +0.026 [−0.009, +0.060] and win +0.034 [+0.009, +0.062] **on the pool**,
front-loaded exactly as Renoir found on V06: p@50 +0.072 [−0.001, +0.181], p@100 +0.029 [+0.000,
+0.062], p@150/p@250 ~0. The cost of D-033 honesty is an opening-edge cost, concentrated on the
32×16 maps; off-pool the terms were never legitimate.

## 5. Cap-lift arm (kyoto-03-latecap) — H-1 ranked #4 flavour

hb1-14 carries the un-lifted V06 search caps (late 48 / sparse 64); verso-05 carries lune-r1-07's
lifted profile (effective late 160 / sparse 512). kyoto-03 = late 48→160, sparse 64→512, opening
(r<40) untouched. CPU probe (sandbox, dense maps): max 10.25 M points/turn vs the 30 M budget.
Expected sign: p@150/p@250 up, p@50/p@100 flat (R-1 measured econ +0.026 on V06), units/length
flat. Scored with the lane gate and `--phase late`.

PLACEHOLDER gate result.

## Rows touched (proposal to the director)

- L01/L25 text (the 160-clamp story): unchanged by this run; the *hb1-14-side* measurement is new —
  the cap lift has never been scored on the prior base.
- H-Q1 (proposed ledger row, antioch): baseline numbers above; the falsifier cut (RL alive) is 0.8 %
  on our base — carthage's arms own the mechanism test.
