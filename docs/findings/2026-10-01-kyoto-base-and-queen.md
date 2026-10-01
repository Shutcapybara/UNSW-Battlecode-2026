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

## 3. Queen measurements on the base (kyoto-01-nodevil, pool)

| metric | ours (n=278 side-games) | zoo opponents (n=278) |
|---|---|---|
| queen alive @490 (any game) | 0.083 | 0.022 |
| queen alive at end among **round-limit** games | **0.008** (1/124) | 0.03 |
| queen alive at end among elimination games | 0.143 | — |
| queen length @490 (alive only), median | 3 | 3 |
| queen is longest @490 | 0.025 | 0.007 |
| queen death round: median / p10 / p90 | 65 / 3 / 169 | 52 / 3 / 164 |
| queen death causes (wall/h2h/self/body/invalid) | 101/89/48/17/0 | 90/104/46/16/16 |
| queen killed by enemy | 0.27 | 0.32 |
| RL win given queen alive | 1.00 (n=1) | 1.00 (n=4) |

Notes: (i) the RL cut (0.8 %) is the decision-relevant number — the tiebreak only applies at the
round limit; carthage's 0.9 % pool number is the same cut, and the two bases are the same bot.
(ii) Our base already keeps its queen more than the zoo does in elimination games (14 %) and overall
(8.3 % vs 2.2 %), but essentially never to the round limit. (iii) 73 % of our queen deaths are
wall/h2h/self — self-inflicted, exactly H-Q1's target. (iv) The win|alive row replicates antioch's
36/36 field finding in our zoo (all 5 surviving queens on either side won their RL game).

## 4. Zero under 1.2.3 (numbers to be posted on completion)

PLACEHOLDER pool/gen absolute + summary (win, econ~, per-checkpoint) for kyoto-01 seeds 1–3;
D-033 cost = kyoto-01 vs kyoto-00 at seed 1 (expect the cost concentrated on devil/portals/dilemma).

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
