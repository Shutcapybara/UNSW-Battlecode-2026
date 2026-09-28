# Gavroche V54 sparse late room

Parent: V53. Preserve the round-40 search cap of 48, with 64 nodes only in
sparse late play. When the team has at most 20 units after round 150, allow
length-4 through length-7 three-step paths and raise the long-body flood cap
from 24 to 32 cells.

Hypothesis: recover late escape and growth options for the priority matchups
that V53 still lost, while limiting extra path/flood work to very sparse play.

## Selection results

V54 completed the 108-game seeded family panel at 69–39 with zero errors or
runtime faults. It scored 32–16 against Sinbad, tf05, grad1, and x04. Four
judge-sandbox games on Big Empty and Trauma (both sides against V31) had p99
CPU of 43.0–44.1M points and maxima of 52.8–63.7M, with no timeouts. This
passed the project CPU screen (p99 <60M, max <80M).

V60 tied V54 at 56 wins on their 88 common fixtures, but V54 won 28/40 common
priority-family games to V60's 27/40 and had more CPU headroom. V66 passed CPU
but did not beat V36's priority-family score after 88/108 seeded games. V54
remains the strongest fully measured CPU-safe Gavroche candidate in this
campaign, though it does not beat V36's 73–35 overall and 37–11 priority-family
record. The former `gavroche-final` directory was a duplicate copy of this
snapshot; use this versioned path in configurations.

Evidence runs: `experiment_data/gavroche-v54-sparse-room_20260927055615026685`
(108-game panel) and
`experiment_data/gavroche-v54-sandbox-cpu_20260927054500000000` (four sandbox
games).
