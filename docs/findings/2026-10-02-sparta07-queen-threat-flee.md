# Sparta 07 — queen threat flee

Sparta 03's two local interceptors did not improve its paired screen or queen
survival. Sparta 04–06 instead varied how much length the original queen
retained through splits: the seven-segment reserve produced 3/32 queens
alive@490, while the five-segment reserve produced 2/32 and more enemy queen
kills. The queen still died early in most matches, often in a head-on
collision.

Sparta 07 forks Sparta 05 (the seven-segment reserve). When a visible enemy
head is within eight cells, the original queen receives a move score bonus
proportional to the increase in distance from the nearest visible enemy. The
change only affects the queen; other dragons retain the aggressive
team-wide enemy-queen hunt and trade acceptance.

## Evaluation

The fixed-seed panel ran 48 matches on Devil, Queen of Spades, Schooltime,
and Trauma, both seats, seeds 1–3, against Sparta 01 and Carthage 05. Sparta 07
scored 9–15 against Sparta 01 and 8–16 against Carthage 05, with zero runner
errors. The queen died in all 48 games: 16 head-on, 29 wall, and 3 body deaths.
She was alive at round 490 in 0 of 27 games that reached that point. Sparta 07
killed the enemy queen in 10 games, down from Sparta 05's 14.

The retreat bonus reduced head-on queen deaths from Sparta 05's 23 to 16, but
increased wall deaths from 19 to 29, lowered round-490 survival from 3/32 to
0/27, and reduced wins. The added distance score can direct the queen toward
unexplored edges, where the movement simulator assumes unknown edges are
traversable. Keep Sparta 07 as a diagnostic control; Sparta 08 adds a queen-only
unknown-edge veto to test that interaction.

```sh
python3 tools/sparta/paired_screen.py --candidate sparta-07-queen-threat-flee \
  --opponents sparta-01-queen-priority carthage-05-free-sprint \
  --maps devil queen_of_spades schooltime trauma --seeds 1,2,3 \
  --output build/sparta07-paired-screen-20261002
```

Results and replays are under `build/sparta07-paired-screen-20261002/`. Source
and map fingerprints are recorded in `manifest.json`.
