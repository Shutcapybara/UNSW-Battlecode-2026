# Ed v12: child-only split-site egress

- **Parent:** `ed-v01-local-release`, which branches from frozen `ed-v00-serre-control`.
- **Mechanism:** birth-site egress, corrected in two ways: activate it only for processes first born after round 0, and measure progress with known-terrain route distance. Initial dragons start at global round 0 and receive no opening movement bonus. A split-born child records its old-tail launch cell on its first observation and may receive the egress score during its first seven local turns.
- Reward progress by known-terrain shortest-path distance from the launch cell, using known walls and portals and optimistic unknown edges. The score applies only within radius 5, and only when the destination has at least two optimistic exits.
- **Off switch:** `birth_release=0`; the child-only gate remains explicit and does not alter parent behavior.
- **Runtime bound:** the nearby breadth-first search is capped at 128 visited cells and radius 6; it is cached for the decision and recomputed after each observation.
