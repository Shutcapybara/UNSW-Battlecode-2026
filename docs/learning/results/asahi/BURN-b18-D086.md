# D-086 §D burn test — bokuto-18-queenfeed, local sandbox (unswbc 1.2.3), 5 Oct 18:05Z

Tool `tools/asahi/burn.py` (job 2077b; raw rows build/asahi/burn/bokuto-18-queenfeed.json). One seat-A game per level on
live/default vs yuna-v05-core, seed 1, sandbox=True. Each copy of bokuto-18 spins on its queen's (id 0) 10th turn
(round 9) until the sandbox's virtual monotonic clock — which is denominated in CPU points (sandbox.py
`clock_time_get` → `now() = spent + slept`) — has advanced BURN points. Local limit: `MAX_TURN_POINTS = 100_000_000`.

| burn | metered points that turn | worker restarts | error | queen | game |
|---|---|---|---|---|---|
| 0 | 7.45 M | 0 | none | alive | A wins r500 (control) |
| 50 M | 57.45 M | 0 | none | alive | identical to control |
| 90 M | 97.45 M | 0 | none | alive | identical to control |
| 95 M | (≥ 100 M: cut) → retried, 7.42 M | 1 | none reported | alive (dies r163 h2h) | diverges: B wins r398 |
| 105 M | same as 95 M | 1 | none reported | alive (dies r163 h2h) | identical to 95 M |

Reading:
1. Up to ~97.5 M metered in one turn the dragon acts normally: the local limit is 100 M a dragon-turn, not 30 M.
2. Over 100 M the dragon does **not** die locally. `TurnBot.ask` (turn.py) sees the worker exit with no output, starts a
   fresh worker and re-asks the same turn (with the init block); that reply is used and no error is recorded. The cost
   is the process's memory (World state, statics): the game diverges from the control from that turn on.
   Whether the judge also retries is not shown by this test; Hinata 16:53Z: server tle turns record exactly 100,000,000
   and the same dragon acts again later.
3. Output writes: one buffered write a turn (helper.hpp setvbuf + flush at ENDTURN), charged 2.5 M + 4,000/byte
   (sandbox.py WRITE_SYSCALL_COST / WRITE_BYTE_COST). bokuto-18's reply is 132 bytes at p50 (149 max; the four SONAR
   lines are ~110 of them) → **3.03 M a turn = 41 % of the p50 turn (7.41 M), 29 % of the max turn (10.61 M)**.
   Cutting the sonar lines would save ~0.45 M a turn; the 2.5 M syscall is fixed.
