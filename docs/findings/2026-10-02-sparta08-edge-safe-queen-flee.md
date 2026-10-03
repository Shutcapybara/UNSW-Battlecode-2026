# Sparta 08 — edge-safe queen flee

Sparta 07 reduced head-on queen deaths from 23 in Sparta 05 to 16, but
increased wall deaths from 19 to 29, scored 9–15 against Sparta 01 and 8–16
against Carthage 05, and left no queen alive@490 among 27 games that reached
round 490. Its retreat score may have pulled the queen toward unexplored
terrain, which the simulator treats as open.

Sparta 08 added Sparta 02's queen-only unknown-edge veto on top of Sparta 07's
retreat score and seven-segment reserve. It tested whether this combination
could retain the lower head-on death count without routing the queen into
unknown walls. Other dragons kept the queen hunt.

## Evaluation

The fixed-seed panel ran 48 matches on Devil, Queen of Spades, Schooltime,
and Trauma, both seats, seeds 1–3, against Sparta 01 and Carthage 05. Sparta 08
scored 9–15 against Sparta 01 and 8–16 against Carthage 05, with zero runner
errors. Its queen died in all 48 games: 16 head-on, 29 wall, and 3 body deaths.
She was alive at round 490 in 0 of 27 games that reached it. Sparta 08 killed
the enemy queen in 10 games.

The unknown-edge veto did not change those results or queen-safety totals from
Sparta 07. The combination did not rescue the retreat strategy; keep Sparta 08
as a diagnostic variant, not a candidate for promotion.

```sh
python3 tools/sparta/paired_screen.py --candidate sparta-08-edge-safe-queen-flee \
  --opponents sparta-01-queen-priority carthage-05-free-sprint \
  --maps devil queen_of_spades schooltime trauma --seeds 1,2,3 \
  --output build/sparta08-paired-screen-20261002
```

Results and replays are under `build/sparta08-paired-screen-20261002/`. Source
and map fingerprints are recorded in `manifest.json`.
