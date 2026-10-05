# Kenma 10 — short queen orbit

Parent: kenma-08-lossless-direction, equivalent strategy to Kenma 03. Adds a general geometric keeper for original queens of length two or three once at least three team dragons exist. Parent SPLIT decisions and the sealed-pocket rescue retain priority.

An eligible queen can enter a four-cell cycle whose edges are known ordinary moves and whose cells are freshly observed, have no bed or pearl, and contain no other body. Eight projected single-step turns prove entry and two full laps without touching the queen's current body. The selected cycle persists while valid. Nearby enemy heads, an adjacent allied head, new food, another body, growth, missing body information or lost terrain certainty abandon it. The parent supplies fallback movement. No map names or dimensions choose behavior.

Motivation: successful keeper-clone Weakhold replays repeatedly circle empty four-cell loops, while replacing the whole action policy hurt expansion. This variant preserves parent splitting and only begins after a small independent population exists. It does not claim safety against unseen opponents or future changes; the loop is checked again every turn.

Status: prepared, unmeasured. Focused C++ behavior checks passed under address and undefined-behavior sanitizers: 80 persistent single-step loop turns, including torus-boundary entry; body, food, bed, enemy, stale/unknown observation, team-population and parent-split checks passed. Full native comparison and exact-source deployment checks remain required. Test: tools/kenma/test_orbit.cpp, output binary main build/kenma/test-orbit. No reserved seeds 11–13 or new maps used.
