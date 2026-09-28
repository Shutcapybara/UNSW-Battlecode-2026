# Gavroche final

Selected source: V54 (`gavroche-v54-sparse-room`), copied after comparing the
completed seeded panel and CPU-safe candidates. Runtime source files match V54.
Policy: a 48-node target-search cap from round 40; after round 150 with at
most 20 units, V54 allows 64 search nodes, longer length-4–7 triple paths,
and a 32-cell long-body flood cap.

V54 completed the 108-game seeded family panel at 69–39 with zero errors or
runtime faults. It scored 32–16 against Sinbad, tf05, grad1, and x04. Its four
judge-sandbox samples had p99 CPU of 43.0–44.1M points and maxima of
52.8–63.7M, with zero timeouts. The fixtures were Big Empty and Trauma, both
sides against V31. This passes the project CPU screen
(p99 <60M, max <80M).

V60 tied V54 at 56 wins on their 88 common fixtures, but V54 won 28/40 common
priority-family games to V60's 27/40 and had more CPU headroom. V66 passed CPU
but could no longer beat V36's priority-family score after 88/108 seeded games.

V54 does not beat V36's 73–35 overall and 37–11 priority-family record. This is
the strongest fully measured CPU-safe Gavroche version in this campaign. It is
staged here as the final candidate; it has not been submitted.

Evidence runs: `experiment_data/gavroche-v54-sparse-room_20260927055615026685` (108-game panel) and `experiment_data/gavroche-v54-sandbox-cpu_20260927054500000000` (four judge-sandbox games).
