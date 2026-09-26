# godel-x02-pacifist: bounds arm. All strikes priced out. Diagnostic only,
# never a promotion candidate (tools/godel/selection_rule.json).
PARAMS = {
    "ladder_attack_units": 99,      # the compact-map ladder never strikes
    "gather.trade_margin": 99,      # evaluator: every trade below threshold
    "hunt.trade_margin": 99,
    "scout.trade_margin": 99,
    "crown.trade_margin": 99,
    "gather.strike_bonus": -50.0,   # ... and heavily penalised on top
    "hunt.strike_bonus": -50.0,
    "scout.strike_bonus": -50.0,
    "crown.strike_bonus": -50.0,
    "crown_kill_round": 999,        # no endgame crown-kill aggression
}
