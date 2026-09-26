# Godel x26-style: GM-3 mechanism master (default-off)

Parent: `bots/godel-x01-frozen` (= ouroboros-v13-ladder). Differences from the
parent are exactly: `safety.py` (`combat_pricing` + per-dragon pressure EMA,
consumed by `head_risk`) and `defaults.py` (eight `style_*` keys, all
defaulting to x01 behaviour). With `style_pressure=0` the pricing path is
expression-for-expression x01; a screen run of this directory MUST reproduce
the x01 cycle-1 screen record (13-11, identical per-fixture outcomes and
round counts) — that reproduction is the structural parity check.

## GM-3 opponent-pressure-conditioned threat pricing

Cycle-1 evidence: a GLOBAL cautious constant (trade_bias 2.5, p_strike2 0.5)
won vs contact-seeking opponents and lost vs banking opponents, netting zero
on the gauntlet while winning the fresh combat reserve 12-4. GM-3 turns that
constant into a per-dragon conditioned one: an EMA of visible enemy heads
within `style_radius` of our head estimates opponent contact pressure; at or
above `style_hi` the dragon feels the cautious (style_*_hi) prices, otherwise
the P defaults (or `style_lo_*` overrides). Covers both combat paths:
`head_risk` feeds the evaluator (open maps) and the ladder safety veto
(compact maps). Spec: `tools/godel/cycle2_plan.json`.
