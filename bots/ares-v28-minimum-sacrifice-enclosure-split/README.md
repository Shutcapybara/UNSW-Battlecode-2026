# Ares V28 — minimum sacrifice enclosure split

V28 starts from Ares V19 and changes only the tail size used by V19's critical-enclosure fallback. When the five-step reach probe says the current and best-move states remain critically enclosed, V28 detaches the minimum two-segment tail child. This leaves the long head dragon with most of its length to move through the freed corridor, following the segment-economy observation in the live loss review.

The ordinary V19 split score, opening production, movement policy, and critical reach gate are unchanged.

Development screen: four-map diagnostic versus V19 was 6-2. The full all-10-map, both-seat, seed-1 screen was 12-8 with zero runner errors and all 20 replays decoded. Maximum recorded sandbox usage was 9.14M points. Replay split sizes were 5,016 of 5,026 at two segments; V19 produced 4,590 of 4,897 two-segment splits and 22 splits of size 10 or more. The direct screen is a single-seed development result, so V28 remains experimental.

Contest submission: uploaded as **v87 (ID 12440)**, named
`ares-v28-minimum-sacrifice-enclosure-split-ai`, at 2026-09-30 03:01:47 UTC. The
contest API reports it active; the upload auto-activated after processing.
Its API source hash is
`782fec21f7d2cb4f924e0a68e886f8e8a1c2c2b8a5d33095ca6b367817059e0c`.
