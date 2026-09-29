OVERRIDE = {
    # The corpus found a measurable sprint tax in our live line. Make an
    # extra segment materially more expensive so a sprint must buy enough
    # progress or immediate food to justify itself.
    "w_sprint": 1.5,
    # Runtime arm: keep the v02 policy but bound the cold-start and dense-turn
    # searches that exceeded the pinned sandbox max on Schooltime.
    "born_cap": 40,
    "big_cap": 128,
    "sprint3_limit": 8,
    "escape_target_nodes": 96,
    "escape_origin_nodes": 144,
    "flood_cap": 20,
    "flood_cap_long": 32,
    "v_dive": 3.0,
    "bed_wait": 0.0,
    "density_ally": 0.10,
    "r_unseen": 0.15,
    "frontier_search_depth": 4,
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
