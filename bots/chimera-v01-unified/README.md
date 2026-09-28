# chimera-v01-unified

**Lineage:** Chimera. **Parent:** `examples/bahamut-scaffold/`.

v01 combines the strongest measured components that fit a single policy:
Ouroboros v13's compact-map production ladder and open-map evaluator, with
Ouroboros's crown communication and role system. It adds Hunter v21's
emergency portal escape and Avery v06's guarded late feeding rule.

## Strategy

- **Compact maps (625 cells or fewer):** use the Hunter-derived ladder retained
  by Ouroboros v13: attack a reachable, visibly longer enemy, split at length
  four, take an unclaimed visible pearl, then spread and explore. Exact move
  simulation and the ladder's safety vetoes remain active. Splits also require
  an unblocked, non-doomed first exit for the newborn.
- **Open maps:** use the Ouroboros evaluator with role-weighted targeting,
  probabilistic strike risk, exact movement simulation, flood/doom and tunnel
  penalties, predicted pearl beds, ally spacing, and portal-aware routing.
- **Team coordination:** carry self, enemy, bed, portal, crown, doom, handoff,
  and pearl-hotspot reports over validated sonar packets. HUNT roles consume
  relayed enemy sightings; scouts favor stale regions and portal discoveries.
- **Endgame:** elect and beacon a crown, hand the role to a surviving split
  child when needed, and allow short dragons to feed only when a larger crown
  is directly visible, at least five friendly units remain, and no enemy was
  seen within eight tiles during the last eight rounds. A beacon can guide a
  feeder but cannot authorize its death.
- **Emergency escape:** if every ordinary first step is fatal, take an adjacent
  portal before choosing an emergency split or a fatal fallback.

The executable follows the scaffold stages in `main.py`: decode, update state,
build features and intentions, choose, execute, construct sonar, encode, and
commit script memory. The strategy modules use the same persistent per-dragon
world model as the Ouroboros source; `protocol.py` remains the scaffold adapter,
with its reply writer extended to represent the engine's intentional no-action
feeding death.

## Borrowed components and evidence

- `ouroboros-v13-ladder`: compact-map ladder, role-aware communication,
  evaluator, pearl-bed model, exact simulation, and crown system. Its native
  source run was **214–1–25** across 240 G+V games, including **99–1–20** on
  compact G+V; open-map actions matched v10 in its reported parity run.
- `hunter-v20-portal-scouts` / `hunter-v21-emergency-portals`: ladder,
  portal scouting concepts, and the trapped-dragon portal escape rule.
- `avery-v06-late-feed`: late crown feeding; this version adds stricter direct
  visibility and nearby-enemy checks. Avery's native six-opponent gauntlet was
  **79–30–1**.
- Hydra's pack-hunt idea is represented by short-lived enemy reports consumed
  by HUNT-role targeting. Leviathan's arrival-aware pearl value is represented
  by remembered bed countdowns in the evaluator.

## Cross-family tournament

Native focus tournament on all 13 bundled maps, both sides, against eight
current family references:
**144W–0D–64L (69.2%)**, with no runner errors.
This is native evidence, not judge-sandbox CPU validation.

| Opponent | W–L |
|---|---:|
| Avery v06 | 16–10 |
| Ouroboros v13 | 10–16 |
| Hunter v14 | 21–5 |
| Hunter v20 | 17–9 |
| Fry v14 | 20–6 |
| Kraken v04 | 19–7 |
| Leviathan v09 | 16–10 |
| Hydra v10 | 25–1 |

The clearest map weaknesses were Dilemma (4–12) and Autarky (6–10). Results
were strongest on Trauma (15–1), Default Small (14–2), and Colosseum, Arena,
Big Empty, and Default (13–3 each). The Ouroboros v13 deficit is the main
lineage-level matchup to investigate before tuning the blend.

Full per-game records and standings are in
[`build/chimera-v01-cross-family-20260926-r2`](../../build/chimera-v01-cross-family-20260926-r2/).

## Run

From the repository root:

```sh
unswbc run maps/arena.map bots/chimera-v01-unified bots/ouroboros-v13-ladder
```

## Submission bundle

The root-level archive `chimera-v01-unified.zip` (`../../chimera-v01-unified.zip`)
contains this bot's files with `bot.toml` at the ZIP root.
