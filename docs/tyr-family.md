# Tyr family — Fenrir and Yuna synthesis

Tyr is a new Norse-named research family based on the strongest measured Fenrir snapshot, `fenrir-v20-crowded-resource-revalue`, with Yuna V03's direction-momentum mechanism transferred into the action scorer. The source fingerprints for runtime files and frozen tournament manifests are recorded below.

## Current candidates

Tyr V01 uses Fenrir V20's production, portal memory, threat model, and newborn separation. It adds Yuna's momentum EWMA with weight `0.6` and decay `0.6`.

On 2026-09-28, Tyr V01 played both seats against Yuna V03 on the frozen 35-map panel and won **38–32**, with zero draws or runner errors. It won both Queen of Spades fixtures in that run.

Tyr V08 adds a short-window return guard to V01: remember the dragon's portal landing cells for two rounds, then subtract 8 points from a movement that re-enters within two tiles after moving at least two tiles away. V08 won **37–33** against Yuna V03 over the same 35 maps and both seats, with zero errors. V08 lost both Queen of Spades games in that full panel; an earlier six-game Queen screen split 1–1 with Yuna and went 2–0 against Tyr V01. These are native, unseeded direct screens, not paired-seed estimates.

V01 and V08 are both viable all-map candidates based on one duel each. The unseeded scores do not establish a reliable ranking between them. Tyr remains experimental and should not be added to the pilot ELO table or treated as promoted.

- V01 results: `build/tyr-v01-vs-yuna-35map-20260928/` (ignored local output)
- V01 frozen input hash: `0939b8bfd52f83bb02efecd411d2c506abb2e772bb781d4a601be3f56cff6b74`
- V01 runtime-source fingerprint (Python and bot.toml files): `810e8a6e30a40e08861e974e7156fe8c68202c93f1968da988f41b23aae2391b`
- V08 results: `build/tyr-v08-vs-yuna-35map-20260928/` (ignored local output)
- V08 frozen input hash: `0b442d8bba0fa8e8a6826240d04b7cccd1f884cd1646b4ff78e30cd2859b1f7d`
- V08 runtime-source fingerprint (Python and bot.toml files): `facd1c5192b0f847f80042dde840754253a640117bf567431b434bacc7503d53`

## Portal-room experiments

Several measured variants tried to stop dragons from leaving a portal room and quickly returning. V02–V07 did not reliably preserve Tyr V01's all-map result. V08 also beat Yuna on the full panel, but its Queen result varied and was 0–2 in that run:

| Snapshot | Change | Result |
|---|---|---|
| V02 | First portal-return patch | Invalid comparison: undefined helper caused emergency fallback; zero pearls and portal traversals. |
| V03 | Penalize the last paired portal for two rounds | 3–3 across both seats against Tyr V01, Fenrir V20, and Yuna V03 on Queen of Spades. |
| V04 | Remember recent landing areas and penalize a return after moving away | 34–36 vs Yuna V03 over the frozen 35-map, both-seat panel (70 games, zero errors). |
| V05 | Apply V04 only when an ally is near the landing | 2–6 across both seats against Tyr V01, V04, Fenrir V20, and Yuna V03 on Queen of Spades. |
| V06 | One-round memory, two nearby allies, smaller penalty | 3–5 against the same four controls on Queen of Spades. |
| V07 | Yuna's crowded-target discount and narrow-corridor penalty | 2–6 against Tyr V01, Yuna V02/V03, and Fenrir V20 on Queen of Spades. |
| V08 | Two-round, two-tile recent-landing guard with an 8-point penalty | 37–33 vs Yuna V03 over the 35-map panel; Queen of Spades 0–2 in that run. An earlier Queen screen was 1–1 vs Yuna and 2–0 vs Tyr V01. |

The Queen of Spades screens were unseeded and showed substantial run-to-run variation. The V08 return penalty is a targeted heuristic, not a hard prohibition; its full-panel Queen result did not improve over Yuna. The explicit return guards are retained as research arms, not merged into V01. In the two V01-versus-Yuna Queen replays reviewed, an approximate five-round/four-tile detector found no rapid room return by either bot. Those replays do not validate the user-observed sequence; no matching replay was supplied.

## Lineage and version notes

- **V01 — Fenrir + Yuna momentum:** baseline all-map candidate; 38–32 in its completed 35-map duel against Yuna V03.
- **V02 — broken portal patch:** preserved as a rejected implementation record; do not use as a strategy control.
- **V03 — paired-portal cooldown:** broad cooldown proved too costly on Queen of Spades.
- **V04 — room re-entry memory:** best Queen screen in one multi-bot run, but lost the full 35-map duel.
- **V05–V06 — crowding-gated return:** narrower attempts did not beat the controls on Queen of Spades.
- **V07 — Yuna congestion transfer:** target discount and corridor guard underperformed on Queen of Spades.
- **V08 — immediate return guard:** 37–33 vs Yuna over 35 maps; its Queen score varied from 1–1 in the short screen to 0–2 in the full panel.

The run manifests are preserved under ignored `build/` directories. The tournament README files were corrected after their runs; runtime strategy files were unchanged. Do not copy results from Fenrir or Yuna onto a Tyr row.
