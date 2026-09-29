OVERRIDE = {
    "v_dive": 3.0,
    "bed_wait": 0.0,
    # Fenrir v20's 0.10 discount regressed against v18 on its own panel.
    # Restore the v18 crowding value while retaining Gaia's safety layer.
    "density_ally": 0.25,
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
