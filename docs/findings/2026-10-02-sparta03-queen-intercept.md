# Sparta 03 — local queen intercept

Sparta 02's fixed-seed screen failed to improve on Sparta 01. Against Sparta
01, 14 of Sparta 02's 24 queens died in head-on collisions; against Carthage
05, 16 died to walls. The queen's own movement veto is not enough when an
enemy moves into her or when the queen has no safe route. Sparta 03 tests a
nearby ally response to a visible attacker.

## Mechanism

When the acting dragon can see our original queen and at least one enemy head
within three cells of her, it determines whether it is one of the two nearest
visible non-queen allies. Those two defenders override local forage, feeder,
and crown targets with the nearest enemy head threatening the queen. A
head-on trade with that specific attacker receives a dominant score, even if
the defender is shorter or the team is below the normal attack threshold.
Other dragons keep hunting the opponent's queen. The queen itself remains
excluded from interception.

This uses only local observations and the existing movement/radio system. It
does not claim that a nearby head will attack next turn; distance three is a
predeclared reach proxy. Multiple dragons may nominate different defenders
if their visible ally sets differ. A defender can be lost without killing the
threat, and body placement may create crowding.

## Evaluation

The fixed-seed paired screen ran 48 matches on Devil, Queen of Spades,
Schooltime, and Trauma, both seats, seeds 1–3, against Sparta 01 and Carthage
05. It scored 12–12 against Sparta 01 and 9–15 against Carthage 05, with no
runner errors. Sparta 03's original queen died in all 48 games: 19 head-on, 25
wall, and 4 body deaths. It was alive at round 490 in 0 of 22 games that
reached that point. The enemy queen died to Sparta 03 in 28 games. The
interceptor did not improve wins or queen survival and remains a diagnostic
variant.

Reproduce with:

```sh
python3 tools/sparta/paired_screen.py --candidate sparta-03-queen-intercept \
  --opponents sparta-01-queen-priority carthage-05-free-sprint \
  --maps devil queen_of_spades schooltime trauma --seeds 1,2,3 \
  --output build/sparta03-paired-screen-20261002
```

Results and replays are under `build/sparta03-paired-screen-20261002/`. Source
and map fingerprints are recorded in `manifest.json`.
