# Gavroche v22: retain v21 CPU cap, add bounded late crown feeding.
OVERRIDE = {
    "sprint3_limit": 4,
    "feed_base": 14,       # start at round 410 on 64x64 maps
    "feed_dist": 2,        # commit only when adjacent to the visible crown
    "feed_max_len": 10,    # donate only short non-crowns
}
