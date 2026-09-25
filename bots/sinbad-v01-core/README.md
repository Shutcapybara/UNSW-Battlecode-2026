# sinbad-v01-core

- **Lineage:** Sinbad (Claude, Bahamut brief). **Parent:** `examples/bahamut-scaffold`
  (protocol.py unchanged, main.py loop kept, hooks filled in).
- **Borrowed:** geometry conventions (edge keys, portal exit formula) as in
  `tools/public_replay_review.py` / ouroboros `world.py`; the production default
  (split at length 4 into 2+2) from the hunter ladder. All code is new.
- **Hypothesis:** one scalar evaluation over exactly simulated 1–3 step paths
  (material, route progress to a value×γ^distance target, flood-fill trap
  shortfall, threat, crowding) plus always-split production is competitive
  with the pool's best without roles or sonar.

## Layers

| Layer | Implementation |
|---|---|
| State | `world.py`: edge memory, portal pairing, bed countdown → spawn round, pearls, own trail/body |
| Features | `tactics.py`: exact path simulation, time-aware flood, enemy reach map, route BFS |
| Decision | `policy.py`: target choice + candidate evaluation; `params.py` holds every weight |
| Encoding | none (no sonar in v01) |

## Measured (native, both sides, deterministic fixtures)

`tools/sinbad/arena.py`, cache `build/sinbad/cache.jsonl`.

| Set | Opponents | W–L–D |
|---|---|---|
| compact (arena, Colosseum, default_small, devil, trophy) | ouroboros-v13-ladder, leviathan-v09-arrival | **13–7–0** |
| open (default, queen_of_spades, stronghold, trauma, schooltime, big_empty) | same | 8–16–0 |

Per map (compact): arena 1–3, Colosseum 3–1, default_small 3–1, devil 2–2, trophy 4–0.
Per map (open): default 4–0, queen 2–2, schooltime 2–2, stronghold 0–4, trauma 0–4, big_empty 0–4.

Note: on open maps leviathan-v09 plays identically to ouroboros-v13 (both use
the v10 evaluator there), so the open column is effectively one opponent twice.

## Diagnosis (replays)

- Arena losses: early trades — shorter enemy heads sprint into our longer
  heads (the pool trades into longer targets); threat cost was too small.
- Trauma/stronghold: never leaves the walled base (unpaired portals were
  treated as walls), dies in 1-wide dead ends (optimistic unknown edges in
  the flood fill).
- All round-500 losses: no crown, so our longest dragon is ~15 vs 20–50.

These led to v02 (threat model, portal dives, pessimistic flood, crown/feeding).
No sandbox CPU check was run for v01.
