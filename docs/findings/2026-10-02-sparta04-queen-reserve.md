# Sparta 04 — queen reserve

Sparta 03 added local interceptors but did not improve the paired screen: it
tied Sparta 01 12–12, lost to Carthage 05 9–15, and its queen died in all 48
games. Across those games the original queen performed 156 split actions, and
19 queen deaths were head-on collisions. Sparta 04 forks Sparta 01 and
disables ordinary and opening splits for the original queen. It preserves the
emergency escape split as a fallback when no movement is viable.

## Hypothesis

Keeping length on the original queen should improve her ability to survive
head-on contact and should retain queen value at the round limit. The tradeoff
is reduced unit production: the team may have fewer hunters and farmers.

## Evaluation

The fixed-seed paired screen ran 48 matches on Devil, Queen of Spades,
Schooltime, and Trauma, both seats, seeds 1–3, against Sparta 01 and Carthage
05. Sparta 04 scored 13–11 against Sparta 01 and 7–17 against Carthage 05,
with zero runner errors. Its queen made 15 emergency split actions, compared
with 156 original-queen splits by Sparta 03. The queen died in 45 games: 22
head-on, 19 wall, and 4 body deaths. She was alive at round 490 in 3 of 32
games that reached that point. Sparta 04 killed the enemy queen in 13 games.

This is a small directional survival gain over Sparta 03, alongside fewer
enemy queen kills and a 7–17 loss to Carthage 05. The all-splits guard has a
substantial production cost. Sparta 04 remains experimental; Sparta 05 tests a
length reserve so the queen can split after retaining a large body.

```sh
python3 tools/sparta/paired_screen.py --candidate sparta-04-queen-reserve \
  --opponents sparta-01-queen-priority carthage-05-free-sprint \
  --maps devil queen_of_spades schooltime trauma --seeds 1,2,3 \
  --output build/sparta04-paired-screen-20261002
```

Results and replays are under `build/sparta04-paired-screen-20261002/`. Source
and map fingerprints are recorded in `manifest.json`.
