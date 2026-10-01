# Ares V35 — crown clipped-dash threat

V35 branches from V33 after match 669722. At round 477, the 24-length king moved to a cell one tile from a visible 4-length enemy. The enemy's tail continued beyond the king's vision, so V33 estimated only two dash steps. The enemy ended adjacent to the king after two steps and both heads died.

V35 retains V33's split-time portal handoff and ordinary movement scoring. A crowned dragon assumes a clipped enemy tail may support the full legal dash. Its threat penalty also covers adjacent head-contact cells around every predicted enemy endpoint. Other dragons retain V33's existing threat model.

This remains an experimental research snapshot and has not been admitted to
`FRONTIER.md`. It was uploaded as `ares-v35-crown-clipped-dash-threat-ai`,
submission v90 (ID 12675); the API reports it active as of 2026-09-30 06:23
UTC. Its API source hash is
`870f4bbb1b20371e472728363fe05479ecf92c0a9d260ce70c4c21106eb04c1d`. See the
V35 finding for replay and benchmark evidence.

## Verification

Replay-driving the round-477 observation with the V35 rule enabled at that turn
changes the crown move from `S` to `WN`. From `(20,10)`, that route ends at
`(19,9)`, two Chebyshev cells from the enemy's recorded contact at `(21,11)`.
Four seed-1 head-to-head screens used the same ten live maps, both seats,
sandbox execution, and had no runner errors:

| Opponent | V35 wins–losses |
|---|---:|
| V33 | 10–10 |
| V32 | 6–14 |
| V28 | 9–11 |
| V19 | 13–7 |

V35's combined record was **38–42** across 80 games. In the five-bot
round-robin standings, V32 scored 46–34, V33 43–37, V28 41–39, V35 38–42,
and V19 32–48. This is one seed and does not establish a strength gain. V35
remains experimental and is outside `FRONTIER.md`. The 60 new V35-vs-V19/V28/V32
games are in `build/ares-v35-vs-v19-v28-v32-live10-seed1-20260930/`; V33 games
are in `build/ares-v35-vs-v33-live10-seed1-20260930/`. See the
[V35 finding](../../docs/findings/2026-09-30-ares-v35-crown-clipped-dash-threat.md).
