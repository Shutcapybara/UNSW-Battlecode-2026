# Von Neumann x02: combat mechanism master source (P1+CM, default-off)

Parent: `bots/von_neumann-x01-frozen` (porthos-x04-policy). Differences from
the parent are exactly: `decision.py` (POLICY_VERSION 3), `params.py` (four
new combat keys, all defaulting to P1 behaviour), this README. With both
mechanism weights at 0 the scoring path is expression-for-expression P1, so a
screen run of this directory MUST reproduce the x01 record (19–5, identical
per-fixture outcomes and round counts) — that reproduction is the structural
parity check for the switches.

## CM-1 length-balance margin (`w_margin_balance`, default 0)

The h2h strike margin shifts with the enemy-minus-ally LENGTH balance at our
head, taken from the swarm field via `gf["lengths"]` (CM consumes an existing
feature; the policy computes no state). Evidence-gated: no confidence → no
shift. Enemy-heavy (positive balance) tightens the margin — trading while
locally outmatched is the failure mode the replay statistics associate with
losing (`initiated_h2h_fraction` −0.17, `team_kills_per_round` −0.19 at the
round-100 checkpoint); allied-heavy relaxes it toward P1's saturation-gated
relaxation.

## CM-2 support-weighted trade gain (`w_support`, default 0)

`strike_value` adds `w_support` per visible allied head within `support_r`
torus steps of our head, capped at `support_cap`. A mutual-death trade beside
allies drops pearls an ally can recover and leaves the enemy punished; the
same material trade isolated is worth less. Visible allied heads only.

## Cells

Mechanism cells are copies of this directory plus an `override.py` enabling
one switch (`tools/von_neumann/sweep.py` automates override-only variants for
the parameter sweeps; mechanism cells are recorded as bot dirs because the
switch changes code):

| Cell | Override | Measures |
|---|---|---|
| x02-mech (this) | — | structural parity with x01 |
| x03-balance | `w_margin_balance>0` | CM-1 alone vs x01 |
| x04-support | `w_support>0` | CM-2 alone vs x01 |

Everything else (state, radio, candidates, executors, non-combat parameters)
stays frozen from x01.
