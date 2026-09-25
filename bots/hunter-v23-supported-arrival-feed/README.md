# hunter-v23-supported-arrival-feed

Experimental V23 fork of `hunter-v22-frontier-exploration`. It keeps V22's
portal planner, emergency escapes, frontier exploration, sonar, and compact-map
policy, then combines selected ideas from the requested ladder, Tew, Leviathan,
and Avery experiments.

## Strategy changes

- **Ouroboros v13 / Tew v18 ladder:** retain V22's attack, split, forage, and
  explore priority, including its three-unit attack gate. Tew v18's compact
  open-trade threshold is therefore already represented.
- **Tew v10 / v12 supported hunts:** a trade-up attack now requires at least as
  many currently visible friendly heads as enemy heads within torus distance
  four. The dragon itself is excluded from the friendly count.
- **Leviathan v09 arrival value:** a currently observed empty bed is a forage
  target when its pearl countdown expires before the dragon arrives, using the
  same first-step timing as V22's growth planner.
- **Leviathan x03 Estuary:** exploration gets a small regional reward based on
  observed pearl-bed density, with penalties for visible teammate crowding and
  enemies. It uses V22's existing 4x4 coverage sectors and adds no radio format.
- **Avery v06 late feed:** after round 410, short non-crown dragons can home to
  a larger reported crown and intentionally omit their action within two
  tiles, depositing corpse pearls. Feeding requires a fresh crown report,
  direct crown visibility at the death point, no recent enemy within eight
  tiles, and more than four surviving units. A relayed beacon may guide the
  approach, but cannot authorize a death by itself.

The full Estuary role allocator and continuation planner were not copied: its
selected profile was an alternative rather than a promotion over Leviathan v09,
and its large-map CPU maximum was close to the budget. V23 takes the bounded
regional signal and the stricter feeding checks instead.

## Native tournament

The 208-game focus tournament on all 13 bundled maps, both sides, against V22
and all seven references finished with no runner errors. V23 scored **71–137**
overall; it beat V22 **15–11**, but lost to most of the reference strategies.

| Opponent | V23 W–L |
| --- | ---: |
| hunter-v22-frontier-exploration | 15–11 |
| leviathan-x03-estuary-roles | 12–14 |
| avery-v06-late-feed | 9–17 |
| leviathan-v09-arrival | 8–18 |
| tew-v10-supported-hunts | 8–18 |
| ouroboros-v13-ladder | 7–19 |
| tew-v18-open-trade-gate | 7–19 |
| tew-v12-mid-support | 5–21 |

V23 did best on Dilemma (16–0 across opponents), Arena (12–4), and Autarky
(10–6). It lost heavily on Big Empty (2–14), Default (1–15), Queen of Spades
(2–14), Schooltime (1–15), and Trauma (1–15). Of its 137 losses, 82 reached
round 500. This native run is a screening result; judge sandbox CPU validation
has not been run, and V23 is not promoted.

Full [standings](../../build/hunter-v23-reference-tournament/standings.csv) and
[per-game records](../../build/hunter-v23-reference-tournament/results.json) are
in `build/hunter-v23-reference-tournament`.

Run from the repository root:

```sh
.venv/bin/unswbc run maps/trauma.map bots/hunter-v23-supported-arrival-feed bots/hunter-v22-frontier-exploration
```
