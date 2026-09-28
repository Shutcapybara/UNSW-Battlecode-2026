# ein-dog-x06-eatvac: eating dragons do not vacate on schedule

Parent: ein-dog-v01-control. One state-model correction, default off:

- `eat_vac` (set 2): any dragon (ally or enemy) whose head is on or next to
  a pearl, or a bed spawning this round or next, gets +2 turns of vacancy on
  every body segment. Route search, flood room and trap pricing then see a
  standing, growing obstacle instead of a moving one.

Diagnosis: the tight-space death loop (trauma r106-112 trace) is a child
re-entering a pocket behind a feeding parent -- the i+2 vacancy schedule
assumes forward motion every round, but an eating dragon pauses and its tail
persists, so the corridor never clears and the parent wall-dies after
shedding children into the jam. x01's entry gate treated the symptom and
cost the farm economy (corpse recycling feeds the crown); this arm keeps the
economy and removes the jam.

Off-state (`eat_vac` 0) is behaviorally identical to the control.
