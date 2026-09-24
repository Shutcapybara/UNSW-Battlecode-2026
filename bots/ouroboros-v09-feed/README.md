# ouroboros-v09-feed  (champion)

v08-contest plus **endgame feeding**: from round 440 (`feed_start`), a
non-crown dragon of length <= 10 (`feed_max_len`) that knows a crown within
16 tiles (`feed_range`, from the crown's self-reports: role + position)
heads for it, and once within 2 tiles (`feed_dist`) takes no action: the
engine's default is death, and its corpse (ceil(len/2) pearls) lies right
next to the crown, which eats it. Only the longest dragon counts at round
500; v08's round-limit losses were mostly 0-7 segments short with 20-30
units still alive.

## Results

widefast (33 maps: originals + transposed + flipped) x cross-series pool
(hydra-v10-farmclean, hydra-v09-lanchester, kraken-v04-eval,
leviathan-v07-local-cache), both sides, 261 common matchups:

| opponent | v05 | v08 | v09 |
| --- | --- | --- | --- |
| hydra-v09-lanchester | 48-18 | 50-16 | 55-11 |
| hydra-v10-farmclean | 51-15 | 55-11 | 59-7 |
| kraken-v04-eval | 58-5 | 53-10 | 56-7 |
| leviathan-v07-local-cache | 62-4 | 61-5 | 64-2 |
| **total** | 219-42 | 219-42 | **234-27** |

Stronghold/trauma/trophy variants (the length races) improved most.
Feed parameters were screened on stronghold/stronghold_T vs hydra-v10:
start 460 range 12 split 2-2, start 430-440 range 16-20 4-0, start 400 3-1.
