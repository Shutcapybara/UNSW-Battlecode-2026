# godel-x03-berserk: bounds arm. Every trade admissible, hunt rewarded for
# striking. Diagnostic only, never a promotion candidate
# (tools/godel/selection_rule.json).
PARAMS = {
    "ladder_attack_units": 2,       # ladder strikes with any support at all
    "gather.trade_margin": -99,     # evaluator: no trade is below threshold
    "hunt.trade_margin": -99,
    "scout.trade_margin": -99,
    "crown.trade_margin": -99,
    "hunt.strike_bonus": 10.0,      # hunters actively paid to trade
    "crown_kill_round": 200,        # endgame crown-kill aggression from r200
}
