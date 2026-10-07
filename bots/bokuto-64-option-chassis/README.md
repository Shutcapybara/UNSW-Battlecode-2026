# bokuto-18-queenfeed

bokuto-17-atlas with the atlas off (`atlas::n_maps = 0`; Asahi's twin showed the 17-map atlas cost 4.4 points on the
pool) plus:

- the queen is fed from round 290 (`QueenParams::feed_from`; was carthage's feed_from, r400–430): feeders die next
  to her from r290, she stops shedding at r290, other dragons leave pearls within 5 of her beacon alone;
- queen terrain safety from round 0: no blind portal dive when another step survives, no escape-split reliance,
  K=4 survival while the team is small; the dodge (enemy reach, head adjacency) runs for the queen from round 0 and
  judges a sprint by its final landing; enemy reach counts up to two paid segments (a 3-long kamikaze sprints 2);
- the careful queen never splits after r290 when a step survives (the policy's threat terms score every path of a
  long queen below −900 and ask for an escape split);
- Kenma's global reserve: non-queens plan with one unit slot free (asahi-27: +11 total length at r300 on the pool).

Ladder diagnosis behind it: claude/bokuto-status.md (5 Oct, 17530's ranked games and the queen census).
