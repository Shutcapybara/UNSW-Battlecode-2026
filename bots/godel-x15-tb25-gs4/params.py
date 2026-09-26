# godel-x15-tb25-gs4: round-2 coordinate-descent arm (params-only vs godel-x01-frozen).
# Incumbent: trade_bias=2.5. Hypothesis: hold adopted trade_bias, tighten gather/scout trade margins 3 -> 4 (non-hunters trade less)
PARAMS = {
    'trade_bias': 2.5,
    'gather.trade_margin': 4,
    'scout.trade_margin': 4,
}
