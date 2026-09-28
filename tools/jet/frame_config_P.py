# Jet c23 principled table: seat B plays in seat A's frame (the map's own symmetry), seat A unchanged.
# Live pool: 180-degree maps -> "r"; x-mirror maps (SYMMETRY y) -> "fx". 32x16 is shared by portals, dilemma (r) and
# devil (fx); it gets "r" (2 of 3). Unknown sizes: no change.
FRAMES = {
    (32, 32, "B"): "r",   # default
    (32, 16, "B"): "r",   # portals, dilemma (devil is x-mirror; shares the size)
    (25, 35, "B"): "r",   # queen_of_spades
    (54, 18, "B"): "r",   # autarky
    (48, 24, "B"): "r",   # trauma
    (63, 27, "B"): "r",   # slithery_fight
    (25, 25, "B"): "fx",  # trophy
    (60, 40, "B"): "fx",  # schooltime
}
DEFAULT = {"A": "id", "B": "id"}
