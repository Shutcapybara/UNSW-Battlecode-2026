# Ed v08: late feeding (global time plus route and donor state)

- **Lineage:** Ed, created for the 2026 temporal-policy campaign.
- **Parent:** `ed-v00-serre-control` (frozen Serre v01 source).
- **Horizon:** global round `r` out of 500; local dragon age is not used.
- **Inherited gates:** fresh crown knowledge, recipient length at least four,
  crown longer than donor, and a bounded approach distance remain required.
- **Crown-space reservation:** follows the earliest donor regime in this arm, so near-crown resource exclusion does not lag behind feeder admission.
- **Arm details:** Time plus state: donor admission uses `r >= 392 - estimated_route_steps`, route at most 16, a fresh crown lead of at least two segments and more than four living units. Route search is capped at 256 nodes and uses known portals, known walls and optimistic unknown edges.
- **Arm:** global time plus route and donor state. This arm keeps the other feeding and production rules fixed.
- **Off switch:** `feed_mode=0` follows the inherited dimension-derived clock
  and toroidal distance predicate.
