OVERRIDE = {
    "v_dive": 3.0,
    "sprint3_saturated_limit": 4,
    "sprint3_late_from": 150,
    "sprint3_late_limit": 5,
    "big_cap_late_from": 40,
    "big_cap_late": 48,
    "big_cap_sparse_from": 150,
    "big_cap_sparse_units": 20,
    "big_cap_sparse": 64,
    "sprint3_sparse_limit": 8,
    "flood_cap_late_from": 150,
    "flood_cap_long_late": 24,
    "flood_cap_long_sparse": 32,
}

OVERRIDE.update({'portal_mode': 1, 'cong_mode': 1, 'nb_mode': 1, 'mom_w': 0.6})  # yuna-v02-core
OVERRIDE.update({'w_support': 0.0})  # spike-x12-yuna-support0: support dose (yuna-v02-core uses 0.5)
