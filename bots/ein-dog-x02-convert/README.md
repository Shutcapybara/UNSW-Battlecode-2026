# ein-dog-x02-convert: staged conversion (converge before the feed window)

Parent: ein-dog-v01-control. One gated edit in `roles.update`, default off:

- `feed_lead` (set 40): for `feed_lead` rounds before `feed_from()`, any
  non-crown dragon shorter than a fresh crown and within `converge_range`
  (default 48) of it takes the feeder role early — it walks to the crown and
  suicides on arrival (within `feed_dist` 4) as usual. Diagnosis: round-limit
  losses show opponents converting +21 longest r400->500 vs our +14 even when
  we hold a material lead (Schooltime loss: total 162-111, longest 34-38);
  the crown is pearl-rate limited (1/round), so conversion volume = rounds of
  feeding; today only dragons already within feed_range 16 when the window
  opens ever convert.

Off-state (`feed_lead` 0) is behaviorally identical to the control. Screen
gate: serre screen 32 paired per fixture vs control's 25-7.
