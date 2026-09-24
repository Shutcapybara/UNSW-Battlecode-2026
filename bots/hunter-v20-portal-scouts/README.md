# hunter-v20-portal-scouts

C++ fork of `hunter-v19-safe-growth-lookahead`. V20 removes the global hotspot
veto that prevented portal exploration on low-spawn maps such as Trauma.
Hotspots now represent present pearls or pearls due within eight rounds, are
shared with their original observation time, and expire after eight rounds.

When there is no reachable pearl that will be available within five moves, one
eligible length-3-to-6 dragon claims the portal-scout role over sonar once at
least four team dragons are alive. Local food only delays scouting when multiple
reachable pearls can feed the team. Scouts limit their approach to an
unmatched portal to eight moves, and known-portal trips must have a safe return
route. Compact boards (area at most 625 tiles) skip portal scouting because
replays showed the exits were too contested for the trips to pay off.

In the final 11-map, both-side tournament against V19, V20 went 13W/9L with no
errors. It went 11W/3L on portal maps and 8W/2L on default, Queen of Spades,
Schooltime, Stronghold, and Trauma. The full results are in
[`results.json`](../../build/hunter-v19-v20-hunter20-verified-all-maps/results.json)
and [`standings.csv`](../../build/hunter-v19-v20-hunter20-verified-all-maps/standings.csv).
V20 remains experimental pending validation against the wider field.

Build and run from the repository root:

```sh
.venv/bin/unswbc run maps/trauma.map bots/hunter-v20-portal-scouts bots/hunter-v16-boost-traps
```
