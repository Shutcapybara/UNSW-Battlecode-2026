"""S1 production and map conditioned crown conversion parameters."""

PARAMS = {
    # Keep producing small children through the opening, with the engine's
    # existing safety and exit checks retained.
    "team_target_small": 64,
    "team_target_mid": 64,
    "team_target_big": 64,
    "child_size": 2,
    "split_stop": 100,
    "crown_start": 250,
    "crown_min_len": 2,
    "feed_max_len": 3,
    "feed_range": 30,
}
