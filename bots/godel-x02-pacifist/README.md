# Godel x02-pacifist (bounds arm, diagnostic only)

Byte-identical to `godel-x01-frozen` (= ouroboros-v13-ladder) except
`params.py`: every strike priced out (`ladder_attack_units=99`, all
`trade_margin=99`, all `strike_bonus=-50`, `crown_kill_round=999`).
Bounds the stance space from below: how much does conditioned aggression
contribute over no aggression? Never a promotion candidate
(`tools/godel/selection_rule.json`).
