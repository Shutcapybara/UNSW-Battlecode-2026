# Ed v06: late feeding (fixed time only)

- **Lineage:** Ed, created for the 2026 temporal-policy campaign.
- **Parent:** `ed-v00-serre-control` (frozen Serre v01 source).
- **Horizon:** global round `r` out of 500; local dragon age is not used.
- **Inherited gates:** fresh crown knowledge, recipient length at least four,
  crown longer than donor, and a bounded approach distance remain required.
- **Crown-space reservation:** follows the earliest donor regime in this arm, so near-crown resource exclusion does not lag behind feeder admission.
- **Arm details:** Fixed gate: when `r >= 380`, eligible dragons with a fresh crown of length at least four and greater than theirs may become feeders if toroidal distance is at most 16. The earliest eligible donor round matches the opening of the inherited round-380 conversion stage.
- **Arm:** fixed time only. This arm keeps the other feeding and production rules fixed.
- **Off switch:** `feed_mode=0` follows the inherited dimension-derived clock
  and toroidal distance predicate.
