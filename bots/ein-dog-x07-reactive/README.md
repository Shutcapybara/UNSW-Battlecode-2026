# ein-dog-x07-reactive: convert when the enemy converts

Parent: ein-dog-x02-convert (carries the converge machinery; `feed_lead` kept
as the ordinary late-clock lead). One added trigger in `roles.update`:

- `race_margin` (set 6), `race_from` (340): from race_from, a dragon that
  knows a fresh crown and a live prey report converts early (feeder role,
  converge_range window) when the prey's length >= crown length - margin.
  The prey channel is the longest enemy seen by us or relayed by sonar --
  no opponent names, no omniscience.

Evidence: x02's fixed 40-round lead converted mechanically (devil/v13 crown
32->44; QoS/porthos 25->32) but lost the devil/leviathan race by ceding the
economy (their total 66 vs 41, final 36 vs 27); the same fixture under the
control lost the late race 20-29. Close length-race losses (trauma/lev 13-14,
trophy 30-34, schooltime 34-38) are exactly the games a reactive trigger
should flip, while grind games keep the full-clock economy.

Off-state (`race_margin` -1) reproduces ein-dog-x02-convert exactly.
