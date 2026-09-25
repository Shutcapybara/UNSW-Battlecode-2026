# avery-v02-id-order-corridors

**Lineage:** avery · **Parent:** avery-v01-safe-swarm (full architecture
inherited; see that README for layers and borrowed-component notes).

## Hypothesis

Most of v01's friendly-fire and corridor deaths come from entering 1-wide
tunnels behind dragons that act **after** us: dragons act in ascending id
order each round, so the cell ahead of a follower is occupied on its turn,
every turn, unless the leader has a lower id (then it vacates before we
act). ID-order-aware corridor discipline should cut `team_kills` and
`self_collisions` without giving up corridor access.

## Changes vs v01

- `tunnel_ahead` classifies the first tunnel occupant by act order:
  - any enemy head → never followable (heavy penalty `w_tunnel_head=10`)
  - occupant id > ours → unfollowable (heavy)
  - occupant id < ours → followable (mild `w_tunnel_follow=2.0`)
- Ending adjacent to an ally head costs full `w_ally_head_adj` when that
  ally acts after us (it may step into our head, killing both), half when
  it acts before us.
- Split placement: single-exit child penalty raised 1.0 → 2.0;
  `split_crowd_max` tightened 10 → 8.

## Results

Gauntlet run: `experiment_data/avery-v02-id-order-corridors_*/`
(filled in after completion; comparison vs v01 baseline 66–40–1).
