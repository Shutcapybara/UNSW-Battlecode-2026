# Ares V13 — enclosure reach priority

Ares V13 branches from Ares V09 and aligns one movement decision to the benchmark's enclosure measure. For each legal post-move candidate it counts cells reachable within five steps with the simulated body and other visible bodies blocking. More than 15 reachable cells is open. If any candidate is open, V13 scores only open candidates, even when a tighter move reaches a pearl. If the current position is enclosed and no one-turn candidate escapes the 15-cell threshold, V13 chooses the legal candidate that opens the most reachable cells, using the existing score to break ties.

This replaces the previous room-length proxy, which did not reduce `death_rate_enclosed_per1k` in short screens. Target selection, farm scoring, splits, portal behavior, and threat valuation stay at the V09 settings. The probe uses measured terrain and treats unknown edges optimistically; it does not branch on map identity.

Development gate: compare against V09 on all 10 active maps, both seats, seed 1. Track exact `death_rate_enclosed_per1k`, W/L, pearls, units and length at r100, and sandbox points.
