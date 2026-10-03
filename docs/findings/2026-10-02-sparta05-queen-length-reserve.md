# Sparta 05 — queen length reserve

Sparta 04 disabled ordinary/opening splits for the original queen. It raised
queen alive@490 from Sparta 03's 0/22 reached games to 3/32, but scored 7–17
against Carthage 05 and killed the enemy queen in only 13 games, compared with
Sparta 03's 28. The results suggest preserving some queen length helps
survival but suppressing queen production costs offense.

Sparta 05 forks Sparta 04 and allows the original queen to split only when the
resulting parent will retain at least seven segments. Emergency escape splits
remain unchanged. The other units and the aggressive team-wide queen hunt are
unchanged.

## Evaluation

The fixed-seed panel ran 48 matches on Devil, Queen of Spades, Schooltime,
and Trauma, both seats, seeds 1–3, against Sparta 01 and Carthage 05. Sparta 05
scored 13–11 against Sparta 01 and 7–17 against Carthage 05, with zero runner
errors. It recorded 27 queen split actions, 12 more than Sparta 04. The queen
died in 45 games: 23 head-on, 19 wall, and 3 body deaths. She was alive at
round 490 in 3 of 32 games that reached that point. Sparta 05 killed the enemy
queen in 14 games, one more than Sparta 04.

The seven-segment reserve increased split frequency and enemy queen kills
slightly without changing wins or queen survival. The threshold is too
conservative to recover production in this panel. Sparta 06 tests a five
segment reserve.

```sh
python3 tools/sparta/paired_screen.py --candidate sparta-05-queen-length-reserve \
  --opponents sparta-01-queen-priority carthage-05-free-sprint \
  --maps devil queen_of_spades schooltime trauma --seeds 1,2,3 \
  --output build/sparta05-paired-screen-20261002
```

Results and replays are under `build/sparta05-paired-screen-20261002/`. Source
and map fingerprints are recorded in `manifest.json`.
