# Gavroche v20: conservative late crown feeding adapted from Avery v06.
OVERRIDE = {
    "feed_base": 14,       # start at round 410 on 64x64 maps
    "feed_dist": 2,        # commit only when adjacent to the visible crown
    "feed_max_len": 10,    # donate only short non-crowns
}
