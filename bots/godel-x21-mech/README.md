# Godel x21-mech: combat mechanism master source (default-off)

Parent: `bots/godel-x01-frozen` (= ouroboros-v13-ladder). Differences from the
parent are exactly: `ladder.py` (strike admission conditioning) and
`defaults.py` (three new combat keys, all defaulting to x01 behaviour).
With `strike_support_radius=0` the admission path is expression-for-expression
the x01 rule; a screen run of this directory MUST reproduce the x01 record
(13-11, identical per-fixture outcomes and round counts) — that reproduction
is the structural parity check for the switches.

## GM-1 support-gated strike (`strike_gate_supported`, default 0)

When `strike_support_radius` > 0 and the gate is on, the ladder strikes only
when visible allied heads within the radius of our head are at least as many
as visible enemy heads. Evidence basis: tew's supported-hunt lineage
(`ladder_support_radius=4` in tew-v12) is the family's proven conditioning;
the replay studies associate initiating contact while pressured with losing
(`initiated_h2h_fraction` -0.172).

## GM-2 support-relaxed admission (`strike_relax_supported`, default 0)

When so supported, the ladder also admits even trades (enemy_len >= LEN), not
only strict trade-ups. Tests the opposite direction under the same
conditioning: taking even trades from a position of local superiority.
