# Von Neumann x06: information-layer master source (P1+INFO, default-off)

Parent: `bots/von_neumann-x01-frozen` (porthos-x04-policy). Cycle 2 of the
lineage: with aggression's knobs at a flat local optimum, upgrade the
**information available to aggression** first, then re-test aggression.
Changed files vs the parent: `decision.py` (POLICY_VERSION 4), `features.py`,
`swarm.py`, `density.py`, `params.py`, this README. The execution layer
(`executors`, `intentions`, `targets`, `tactics`, `main`, `world`) is
byte-frozen. With every switch at its default the scoring path is
expression-for-expression P1; a screen run of this directory MUST reproduce
the x01 record (19–5, identical per-fixture outcomes).

## Idea map (cycle brief → mechanism)

| Brief | Mechanism |
|---|---|
| EWMA friendly counts over fuzzed own position | inherited (`density` counts, `swarm` lengths over `LOCAL` EWMA position); window validated vs replays |
| Enemy EWMA; sizes factored | inherited; consumed via the new dual-window fields |
| Factor own size | `self_balance`: balance damped by own length (`self_len_cap`) |
| Factor time | `self_balance` fades with `phase`; fields already age by round |
| Per-instance terrain + available space | `room` = bounded flood at the landing cell; `spatial_gain = swarm_gain * min(1, room/room_norm)` — the same enemy control in a tight corridor counts less as a push target |
| Messaging protocol / not decoding enemy messages | already authenticated at the port: team tag byte + 56-bit checksum (`comms.unpack` rejects foreign payloads, p ≈ 1−2⁻¹⁶); regression-tested, no wire change needed |
| Multiple EWMAs (long + short) | `swarm_h_short = 1.0` alongside the inherited `4.0`; both validated against replay ground truth (`tools/von_neumann/ewma_frozen.json`: h=4 is the stability knee, h=1 gives zero-lag contact with one round of exit memory; the position fuzz lags truth by ~3.2 tiles) |
| Friendly vs enemy gradients for direction | `gain` (inherited, long window) + `gain_short` (rising contact); consumption is context-dependent (target-relative), never compass |

## Switches (params; 0/off = x01 exactly)

- `field_dual` — build short-window length/count fields (build only).
- `field_room` — build room-normalised spatial gains (build only).
- `w_grad` — INFO-1: the early-saturation push follows `spatial_gain`
  instead of the raw `swarm_gain` (weight stays `aggro_push`).
- `w_mb2` — INFO-2: strike margin shifts by `w_mb2 * self_balance`
  (short-window, self-size-damped, phase-faded, evidence-gated).
- `w_tf` — INFO-3: `threat_cost × (1 + w_tf × contact)` where `contact` is
  the short-window enemy length at the head, normalised to [0, 1].

Everything is receiver-side: the radio stream is unchanged, so build-only
cells are parity-exact by construction and consumption cells change only
decisions, never messages.
