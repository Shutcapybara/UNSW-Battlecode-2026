# pace-v01

Parent `chaewon-y04-probe` (yuna-v05-core + atlas + newborn-neck fix + portal probe; copied with
attribution, host untouched). The **P1 pace probe**: the only new policy is a controller that keeps
the team's material on the field's production curve; everything else is the host's.

## What the controller does

Targets are public-corpus **winner medians** per map class (compact = W*H <= 625; 280 games,
2026-09-29): compact u25 7 / u50 12 / u100 23, t25 17 / t50 30 / t100 58 / t250 86; open u25 6 /
u50 11 / u100 20, t25 15 / t50 27 / t100 50 / t250 116. The curve is linearly interpolated and
self-anchored at the observed round-0 material (a team is never "behind" at the start by
construction). Units are exact from the header; team total is a clamped EWMA of sampled visible
lengths (self + visible allies + a fresh crown beacon) times UNIT_COUNT, floored at 2*units.

Per turn, gaps ug/tg (fraction behind) select a mode:

- **push** (ug > 0.12, r < 380): `split_val` +7*deficit (max), opening production window +<=30 rounds.
- **hold** (ug < -0.12 and tg > 0.05): `split_val` -3 (max) — grow existing dragons instead of splitting.
- **grow** (tg > 0.05): pearl/bed/memory values x (1 + gain*deficit), confirmed-pearl 2-step sprints
  for dragons of length <= 8. The gain is **class-conditioned**: 1.2 on open maps, 0.3 on compact —
  a full boost on compact collapses the churn economy (trophy seed-1 isolation: units r100 33 -> 11,
  win -> loss; 2026-09-29).
- on pace: the host's default knobs.

Survival constraints are never relaxed by the controller: exact 1-3 step simulation, split
child-exit and child-area gates, child = 2, split_min = 4. The **pace-nolimit** arm
(`pace_nolimit = 1` via override.py in a generated copy, never committed) zeroes the
trap/threat/blind-portal penalties and skips the split exit gates to measure what they cost.

Activation: `LOG ACT:pace+` rides the same stdout write as the action (protocol.py `pending`) when
a push/grow knob shift is active (heartbeat <= 1/8 rounds) and on splits/pearl-sprints under it;
`LOG ACT:pace-` while an eligible split is suppressed under hold.

## Measurement report (filled from the panel)

- **Strategy**: pace targets above; attainment per class in the findings file.
- **Execution**: pace controller on; ablation = the host arm itself (controller inert ≡ host knobs).
- **Implementation**: metered probes below.
- **State**: host's; the controller adds only the EWMA total estimate (consumer: the mode logic).
- **Messaging**: host's (crown beacons feed the total estimator); no new packets.
- **Momentum**: host's (unchanged).

## Metered probes (unswbc 1.2.2 sandbox, vs sinbad-v07-divecap)

| fixture | turns | p50 | p99 | max | faults | pace+ r0-100 |
|---|---|---|---|---|---|---|
| (filled after the final probe pass) | | | | | | |

## Panel (filled after the run)

Arms `host` (chaewon-y04-probe), `pace` (this bot), `nolimit` (constraints off), ten live maps,
both sides, seeds 1-3, six opponents, unswbc 1.2.2 `--seed`, paired by (map, side, seed, opponent).
