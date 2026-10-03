# Sparta 06 — five segment queen reserve

Sparta 05's seven-segment queen reserve recorded 27 queen split actions and
14 enemy-queen kills, but it matched Sparta 04's results: 13–11 against Sparta
01, 7–17 against Carthage 05, and queen alive@490 in 3/32 reached games. The
threshold changed the amount of production only slightly.

Sparta 06 forks Sparta 05 and permits ordinary/opening splits once the
remaining parent length is at least five. This tests whether a lower
threshold restores hunters without dropping the queen back to the two-segment
parent created by the default split. Emergency escape splits remain unchanged.

## Evaluation

The fixed-seed panel ran 48 matches on Devil, Queen of Spades, Schooltime,
and Trauma, both seats, seeds 1–3, against Sparta 01 and Carthage 05. Sparta 06
scored 13–11 against Sparta 01 and 6–18 against Carthage 05, with zero runner
errors. It recorded 31 queen split actions and 15 enemy-queen kills, up from
27 and 14 in Sparta 05. The queen died in 46 games: 20 head-on, 21 wall, and 5
body deaths. She was alive at round 490 in 2 of 32 games that reached it,
down from 3/32 in Sparta 05.

The five-segment threshold allowed four more split actions and one more enemy
queen kill, but reduced queen survival and lost one game to Carthage 05. It
does not improve on the seven-segment reserve in this screen. A separate
queen-flee movement change is the next test.

```sh
python3 tools/sparta/paired_screen.py --candidate sparta-06-queen-reserve-five \
  --opponents sparta-01-queen-priority carthage-05-free-sprint \
  --maps devil queen_of_spades schooltime trauma --seeds 1,2,3 \
  --output build/sparta06-paired-screen-20261002
```

Results and replays are under `build/sparta06-paired-screen-20261002/`. Source
and map fingerprints are recorded in `manifest.json`.
