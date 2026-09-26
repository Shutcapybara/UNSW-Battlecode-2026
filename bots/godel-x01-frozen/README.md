# Godel x01: frozen baseline (Ouroboros v13 / ladder doctrine)

Every `.py` file and `bot.toml` is a byte-identical copy of
`bots/ouroboros-v13-ladder` (verified by SHA-256 in `tools/godel/frozen.json`,
2026-09-26; 10 files, zero mismatches). Godel is the combat/aggression
lineage: non-combat machinery (world model, comms, targeting, roles,
production, economy, crown/feeding endgame, safety geometry) is frozen at
this baseline; iteration happens on the combat procedures of the policy
(strike admission, threat calibration, trade margins, aggression gating,
hunt allocation) with the policy refit as evidence accumulates.

Provenance of the baseline (see `bots/ouroboros-v13-ladder/README.md`):

- Ouroboros v10/v12 core (modular evaluator) + hunter-v20's production ladder
  ported to `ladder.py`, active on compact maps (<= 625 tiles) via the
  doctrine dict; open maps play the v10 evaluator exactly.
- Measured at promotion: G+V 240 games **214-1-25** vs its own v10 control's
  180-1-59; compact-map gain driven by the ladder. Panel rating 73.7%
  (established, 1345 fixtures, 119 opponents) — the strongest well-measured
  Python chassis outside the French line at freeze time.

Combat surface (the only unfrozen part):

- `ladder.py` strike admission (compact maps): trade-up rule,
  `ladder_attack_units`, `ladder_safety`, `ladder_risk_max`.
- `safety.py` threat calibration: `p_strike1/2/3`, `p_split_child`,
  `trade_bias`, `threat_reach`.
- `evaluate.py` trade scoring: per-role `trade_margin`, `strike_bonus`,
  `risk`, `w_enemy`; `crown_kill_round` endgame aggression.
- Role mixes `mix_*` (hunt allocation = how much of the swarm fights).

Role in this lineage: the control every combat variant is compared against on
identical fixtures (deterministic engine, exact pairing). Do not edit; edit a
copy with a new version number. Pure-parameter variants differ from x01 only
by a `params.py` file; mechanism variants additionally touch exactly one of
the combat files above.
