# godel-x12-tb25-margin1: round-2 coordinate-descent arm (params-only vs godel-x01-frozen).
# Incumbent: trade_bias=2.5. Hypothesis: hold adopted trade_bias, tighten hunter trade margin (was null from x01; retest from new incumbent)
PARAMS = {
    'trade_bias': 2.5,
    'hunt.trade_margin': 1,
}
