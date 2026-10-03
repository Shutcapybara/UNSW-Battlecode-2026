# Sparta 01 — first focused screen

Sparta 01 was run serially against Carthage 05 and four frontier controls on
Devil, Queen of Spades, Schooltime, and Trauma. The 40 games covered both
seats, with no explicit seed passed to the tournament runner. Results are a
single exploratory screen, not a ranked or promotion panel.

| Map | Sparta wins | Losses |
|---|---:|---:|
| Devil | 6 | 4 |
| Queen of Spades | 6 | 4 |
| Schooltime | 3 | 7 |
| Trauma | 2 | 8 |
| **Total** | **17** | **23** |

Sparta went **4–4 against Carthage 05** over the four maps. Overall results
against the other selected bots were 13–19. Runner errors: 0. The weakness is
concentrated on Schooltime and Trauma, where the queen's survival and the
economy of its pursuit policy both need scrutiny.

The queen reached round 490 in 20 of the 40 games and survived in 2 of those
20. Cause-coded own-queen deaths were 16 wall, 15 head-on, and 3 body; six
other games had no queen-death event before the game ended. These are small
unpaired counts and should not be interpreted as a causal effect versus
Carthage 05. The 16 wall deaths motivate Sparta 02: the inherited simulator
plans through unknown edges as if they were open, and the queen guard did not
mark those candidate routes as uncertain.

The serial output and replays are under the ignored local path
`build/tournament-sparta01-queen-priority-20261002/`. Reproduce with:

```sh
PATH="$PWD/.venv/bin:$PATH" python3 tools/benchmarking/tournament.py \
  --bots sparta-01-queen-priority carthage-05-free-sprint \
    tyr-v12-devil-scout-tiebreak fenrir-v20-crowded-resource-revalue \
    bifrost-v01-portal-memory gavroche-v33-half-support \
  --focus-bot sparta-01-queen-priority \
  --maps schooltime queen_of_spades devil trauma \
  --jobs 1 --timeout 900 \
  --output build/tournament-sparta01-queen-priority-20261002
```

The dry-run scheduled 40 matches before the same command was run without
`--dry-run`. All games completed without runner errors. No claim is made about
unscreened maps or opponent cohorts.
